# Counterpart — Bilateral semantic matching with deterministic optimal allocation

**Category:** Intelligent Contracts

**Repository:** https://github.com/Baster221/counterpart

**Live contract (GenLayer StudioNet):** https://explorer-studio.genlayer.com/address/0xE3588c50857B2690577c0A3175884279C39D1288

## Purpose

Counterpart allocates bounded service commitments described in natural language. Participants opt into immutable task requirements or service offers with provider restrictions. After collection closes, GenLayer consensus derives the complete two-way compatibility matrix. Deterministic code computes a maximum-cardinality one-to-one matching and creates reservations. Each pair must bilaterally confirm the committed snapshot before becoming an agreement.

For example, one supplier offers translation plus copyediting, while another offers translation only. Greedily giving the first translation request to the flexible supplier leaves the copyediting request unmatched. Counterpart chooses translation→specialist and copyediting→flexible supplier, serving both. The model never controls optimization, capacity, tie-breaking or participant consent.

## GenLayer consensus

Validators independently evaluate every demand×supply pair, including negative and apparently unrelated pairs. Each cell separately binds fulfillment of all task requirements, admissibility under all supplier restrictions, and exact confidence. Negation and exceptions require substantive interpretation. No similarity prefilter can remove a plausible pair, and no extra leader edge can pass without independent agreement. Only YES/YES/high creates a usable edge; high and medium never compare as equivalent.

The entire normalized matrix must match exactly. The bounded optimizer exhausts all partial injective assignments, maximizes cardinality and applies a fixed lexicographic tie-break. Snapshot commitments bind chain, deployment, batch and active participants/specifications. Clearing and timeout cleanup are permissionless; consent is participant-only.

## Review evidence

- One standalone source file with a pinned GenVM runner.
- 20 passing direct tests with explicitly exercised validator disagreement cases.
- An independent exhaustive reference verifies all 512 possible 3×3 compatibility graphs, including maximum cardinality and tie-breaking.
- Live four-participant StudioNet flow and finalized receipts are recorded in `evidence/network.json`; matrix, optimal allocation and participant consent appear in `evidence/state.json`.
- Byte-for-byte deployment/source verification, public read-only verification script, CI, consensus and threat-model documentation, MIT license.

This contract matches publicly declared commitments. It does not claim verified skills, human identity, global availability, payment settlement or eventual fulfillment. Its distinctive primitive is consensus-derived graph construction plus deterministic allocation and bilateral consent, useful for service exchanges and review/task assignment.
