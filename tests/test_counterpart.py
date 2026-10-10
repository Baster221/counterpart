import itertools
import json
import sys
import pytest


def matrix(d=2, s=2, edges=None):
    if edges is None:
        edges = {(0, 0), (0, 1), (1, 0)}
    return {"pairs": [{"demand": i, "supply": j, "fulfills": "YES" if (i, j) in edges else "NO",
            "admissible": "YES", "confidence": "high"} for i in range(d) for j in range(s)]}


def mock(vm, obj):
    vm.clear_mocks()
    vm.mock_llm(r"COUNTERPART_V1", json.dumps(obj))


@pytest.fixture
def setup(direct_vm, direct_deploy, direct_accounts):
    direct_vm.warp("2026-10-10T00:00:00Z")
    direct_vm.sender = direct_accounts[0]
    c = direct_deploy("contracts/counterpart.py", sdk_version="v0.2.12")
    b = c.open_batch("Documentation exchange", 60, 300)
    for i, text in enumerate(["Translate English documentation into Indonesian.", "Copyedit English documentation."]):
        direct_vm.sender = direct_accounts[i + 1]
        c.join(b, "demand", text, "")
    for i, text in enumerate(["English copyediting and translation into Indonesian.", "Translation from English into Indonesian."]):
        direct_vm.sender = direct_accounts[i + 3]
        c.join(b, "supply", text, "Public technical documentation only.")
    direct_vm.warp("2026-10-10T00:01:00Z")
    mock(direct_vm, matrix())
    return c, b


def test_optimal_allocation_avoids_greedy_trap(setup, direct_vm):
    c, b = setup
    c.clear(b)
    batch = c.get_batch(b)
    assert [(m["demand_id"], m["supply_id"]) for m in batch["matches"]] == [(0, 1), (1, 0)]
    assert len(batch["matrix"]) == 4
    assert direct_vm.run_validator() is True
    with direct_vm.expect_revert("Batch not ready"):
        c.clear(b)


@pytest.mark.parametrize("field,value", [("fulfills", "NO"), ("admissible", "NO"), ("confidence", "medium"), ("confidence", "low")])
def test_every_effect_bearing_field_is_exact(setup, direct_vm, field, value):
    c, b = setup
    c.clear(b)
    obj = matrix()
    obj["pairs"][0][field] = value
    mock(direct_vm, obj)
    assert direct_vm.run_validator() is False


def test_false_edges_are_also_bound(setup, direct_vm):
    c, b = setup
    c.clear(b)
    obj = matrix()
    obj["pairs"][-1]["fulfills"] = "UNKNOWN"
    mock(direct_vm, obj)
    assert direct_vm.run_validator() is False


def test_matrix_order_normalizes(setup, direct_vm):
    c, b = setup
    c.clear(b)
    obj = matrix()
    obj["pairs"].reverse()
    mock(direct_vm, obj)
    assert direct_vm.run_validator() is True


def test_incomplete_or_duplicate_matrix_rejected_without_state_write(setup, direct_vm):
    c, b = setup
    obj = matrix()
    obj["pairs"].pop()
    mock(direct_vm, obj)
    with direct_vm.expect_revert("Incomplete all-pairs"):
        c.clear(b)
    assert c.get_batch(b)["status"] == "COLLECTING"
    obj = matrix()
    obj["pairs"][-1] = obj["pairs"][0]
    mock(direct_vm, obj)
    with direct_vm.expect_revert("Duplicate pair"):
        c.clear(b)


def test_malformed_leader_and_errors_disagree(setup, direct_vm):
    c, b = setup
    c.clear(b)
    assert direct_vm.run_validator(leader_result=[]) is False
    assert direct_vm.run_validator(leader_error=RuntimeError("timeout")) is False


def test_uncertain_or_one_sided_edges_never_match(setup, direct_vm):
    c, b = setup
    obj = matrix(edges={(0, 0)})
    obj["pairs"][0]["confidence"] = "medium"
    mock(direct_vm, obj)
    c.clear(b)
    assert c.get_batch(b)["matches"] == []


def test_bilateral_consent_and_snapshot_binding(setup, direct_vm, direct_accounts):
    c, b = setup
    c.clear(b)
    digest = c.get_batch(b)["input_digest"]
    direct_vm.sender = direct_accounts[0]
    with direct_vm.expect_revert("Only matched participant"):
        c.confirm(b, 0, digest)
    direct_vm.sender = direct_accounts[1]
    with direct_vm.expect_revert("Snapshot commitment mismatch"):
        c.confirm(b, 0, "0" * 64)
    c.confirm(b, 0, digest)
    assert c.get_batch(b)["matches"][0]["status"] == "RESERVED"
    with direct_vm.expect_revert("Already confirmed"):
        c.confirm(b, 0, digest)
    direct_vm.sender = direct_accounts[4]
    c.confirm(b, 0, digest)
    assert c.get_batch(b)["matches"][0]["status"] == "AGREED"
    with direct_vm.expect_revert("Match not reserved"):
        c.decline(b, 0)


def test_decline_is_terminal_and_no_silent_rematching(setup, direct_vm, direct_accounts):
    c, b = setup
    c.clear(b)
    direct_vm.sender = direct_accounts[1]
    c.decline(b, 0)
    assert c.get_batch(b)["matches"][0]["status"] == "DECLINED"
    assert len(c.get_batch(b)["matches"]) == 2


def test_permissionless_expiry_boundary(setup, direct_vm):
    c, b = setup
    c.clear(b)
    with direct_vm.expect_revert("Batch not ready to expire"):
        c.expire(b)
    direct_vm.warp("2026-10-10T00:06:00Z")
    with direct_vm.expect_revert("Confirmation closed"):
        c.confirm(b, 0, c.get_batch(b)["input_digest"])
    c.expire(b)
    assert c.get_batch(b)["status"] == "CLOSED"
    assert all(m["status"] == "EXPIRED" for m in c.get_batch(b)["matches"])


def test_withdrawn_entry_never_enters_matrix(setup, direct_vm, direct_accounts):
    c, b = setup
    direct_vm.warp("2026-10-10T00:00:30Z")
    direct_vm.sender = direct_accounts[1]
    c.withdraw(b)
    with direct_vm.expect_revert("Participant already joined"):
        c.join(b, "supply", "Different offer", "")
    direct_vm.warp("2026-10-10T00:01:00Z")
    mock(direct_vm, matrix(1, 2, {(0, 0)}))
    c.clear(b)
    assert c.get_batch(b)["matrix_demand_ids"] == [1]
    assert c.get_batch(b)["matches"][0]["demand_id"] == 1


def test_all_512_three_by_three_graphs_match_reference(setup):
    # Independent oracle: enumerate Cartesian assignments, filter collisions,
    # then compare maximum cardinality and the documented tie-break rule.
    c, _ = setup
    modules = [m for m in list(sys.modules.values()) if m is not None and hasattr(m, "_maximum_matching")]
    solve = modules[-1]._maximum_matching
    for bits in range(512):
        edges = {(i, j) for i in range(3) for j in range(3) if bits & (1 << (i * 3 + j))}
        valid = []
        for assignment in itertools.product(range(4), repeat=3):
            used = [s for s in assignment if s != 3]
            if len(used) == len(set(used)) and all(s == 3 or (d, s) in edges for d, s in enumerate(assignment)):
                valid.append(assignment)
        expected = min(valid, key=lambda a: (-sum(s != 3 for s in a), a))
        actual = solve(matrix(3, 3, edges)["pairs"], 3, 3)
        assert actual == [{"demand": d, "supply": s} for d, s in enumerate(expected) if s != 3]


def test_collection_deadline_and_empty_batch(direct_vm, direct_deploy):
    direct_vm.warp("2026-10-10T00:00:00Z")
    c = direct_deploy("contracts/counterpart.py", sdk_version="v0.2.12")
    b = c.open_batch("Empty", 60, 60)
    with direct_vm.expect_revert("Batch not ready"):
        c.clear(b)
    direct_vm.warp("2026-10-10T00:01:00Z")
    with direct_vm.expect_revert("Collection closed"):
        c.join(b, "demand", "Task", "")
    c.clear(b)
    assert c.get_batch(b)["matrix"] == []
    assert c.get_batch(b)["matches"] == []


def test_expiry_preserves_agreed_matches(setup, direct_vm, direct_accounts):
    c, b = setup
    c.clear(b)
    digest = c.get_batch(b)["input_digest"]
    direct_vm.sender = direct_accounts[1]
    c.confirm(b, 0, digest)
    direct_vm.sender = direct_accounts[4]
    c.confirm(b, 0, digest)
    direct_vm.warp("2026-10-10T00:06:00Z")
    with direct_vm.expect_revert("Confirmation closed"):
        c.decline(b, 1)
    c.expire(b)
    assert [m["status"] for m in c.get_batch(b)["matches"]] == ["AGREED", "EXPIRED"]


def test_four_slot_bound_and_no_self_matching(direct_vm, direct_deploy, direct_accounts):
    direct_vm.warp("2026-10-10T00:00:00Z")
    c = direct_deploy("contracts/counterpart.py", sdk_version="v0.2.12")
    b = c.open_batch("Bounded", 60, 60)
    for i in range(4):
        direct_vm.sender = direct_accounts[i]
        c.join(b, "supply", "Public technical copyediting", "")
    with direct_vm.expect_revert("Participant already joined"):
        c.join(b, "demand", "Copyedit docs", "")
    direct_vm.sender = direct_accounts[4]
    with direct_vm.expect_revert("Side is full"):
        c.join(b, "supply", "Public technical copyediting", "")


def test_unilateral_compatibility_cannot_allocate(setup, direct_vm):
    c, b = setup
    obj = matrix(edges={(0, 0)})
    obj["pairs"][0]["admissible"] = "NO"
    mock(direct_vm, obj)
    c.clear(b)
    assert c.get_batch(b)["matches"] == []


def test_boolean_pair_ids_rejected(setup, direct_vm):
    c, b = setup
    c.clear(b)
    obj = matrix()["pairs"]
    obj[0]["demand"] = False
    assert direct_vm.run_validator(leader_result=obj) is False
