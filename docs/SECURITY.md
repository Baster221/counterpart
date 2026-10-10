# Threat model

The batch creator, participants and clearing caller can all be adversarial. The creator's authority stops at choosing a label and bounded collection/confirmation windows. It cannot edit another participant's commitment, change the semantic rubric or override allocation.

| Threat | Control | Remaining boundary |
|---|---|---|
| Leader invents a favorable edge | Independent full-matrix derivation; exact comparison | Correlated model mistakes remain possible. |
| Keyword or negated capability passes | All requirements and restrictions are judged semantically | A model can still misread adversarial text; consensus is not a semantic theorem prover. |
| False exclusion by textual prefilter | Every pair evaluated; no similarity threshold | Conservative UNKNOWN can exclude ambiguous offers. |
| High/medium both accepted | Exact confidence for every cell | More disagreements can reduce liveness. |
| Greedy matcher wastes capacity | Bounded exhaustive maximum-cardinality allocation | Objective is number of matches, not welfare or fairness. |
| One supplier reused | Injective assignment with capacity one | Capacity is only per batch, not independently verified availability. |
| Participant's commitment changed after selection | Immutable input snapshot and confirmation digest | Public storage is not confidential. |
| Stranger confirms or declines a match | Address-bound participant checks | Address ownership does not prove distinct human/project identity. |
| Stalled confirmation | Permissionless expiry; unresolved reservation becomes EXPIRED | A cleanup transaction is required. |
| Silent rematching after refusal | Terminal decline; allocation never recomputed in cleared batch | Participants may create a new batch. |

No funds are held. No escrow delivery, refund path, payment settlement, private document storage, certification verification, human identity, anti-Sybil guarantee, or global capacity lock is claimed. A supplier's text is its **offer**, not evidence that the supplier can or will perform it. Bilateral confirmation makes the agreed pair explicit; actual fulfillment requires the integrating workflow.

External systems must wait for successful finalized execution before acting on AGREED state. GenLayer's ACCEPTED transaction status can still include a contract execution error, and acceptance may later be appealed. A cross-contract or external consumer must handle its own delivery/idempotency and finality boundary.

The digest covers protocol, chain, deployed contract, batch ID and every active commitment with participant and original entry ID. It is an integrity commitment, not encryption. The matrix stores compact indices plus explicit maps to original IDs; withdrawal cannot accidentally reassign consent to a different address.
