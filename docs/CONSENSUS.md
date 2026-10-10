# Consensus and optimizer specification

After the transaction clock reaches the collection deadline, active demand and supply entries are immutable. Every node receives the same bounded snapshot. Names/addresses are omitted from the semantic prompt because they do not affect compatibility; addresses remain in the deterministic consent state and snapshot digest.

For every pair `(d,s)`, the node derives `(fulfills, admissible, confidence)`. Fulfillment asks whether all demand requirements are explicitly covered by the offer. Admissibility asks whether the task fits all supplier restrictions. A missing requirement is not inferred. Negation and exceptions must be interpreted substantively. Specifications are commitments, not independent evidence of real-world ability.

```text
equivalent(L,V) := canonical_complete_matrix(L) == canonical_complete_matrix(V)
edge(d,s) := fulfills == YES and admissible == YES and confidence == high
```

The validator independently re-runs the whole task, including cells whose leader label is NO or UNKNOWN. The leader cannot exclude an inconvenient pair or add an unverified extra edge. IDs must be exact integers; duplicate, missing, extra or malformed cells fail. Input row order is normalized. Confidence buckets are exact, not numerically close.

If `equivalent(L,V)`, both nodes derive the same edge set. Deterministic optimization on identical ordered inputs therefore produces the same allocation. It also produces the same stored matrix. No free-form explanations control matching, timing, quorum, capacity, or consent.

## Allocation objective

Each demand and supplier has capacity one in a batch. Enumerate every partial injective assignment from demand IDs to supplier IDs. Retain only compatible edges. Compare assignments by:

1. More assigned demands first.
2. Lexicographically smaller supplier vector first, with unmatched encoded as `supply_count`.

This is maximum-cardinality matching with a deterministic tie-break, not maximum welfare, strategy-proof allocation, stable marriage, or optimal monetary pricing. Append order decides ties, so earlier entries can have an advantage. With 4×4 slots, at most 209 partial matchings exist; no unbounded optimizer or model-generated code executes.

The reference test independently enumerates the Cartesian space for all 512 3×3 graphs, filters duplicate supplier use and invalid edges, and checks the optimum and exact tie-break.

## Failure and liveness

Malformed model output aborts the transaction before writes. Validators reject leader exceptions or their own failed model calls. Ambiguous inputs can fail exact consensus or produce a conservative unusable edge. There is no automatic fallback to an optimistic matrix.

An empty side clears deterministically without a model call. Real semantic clearing uses GenLayer's validator selection, appeals and transaction finality. The application adds bilateral confirmation of a domain-separated snapshot digest, not a parallel adjudication or challenge registry.
