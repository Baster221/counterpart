# Live StudioNet validation

Contract: [0xE3588c50857B2690577c0A3175884279C39D1288](https://explorer-studio.genlayer.com/address/0xE3588c50857B2690577c0A3175884279C39D1288)

Network: GenLayer StudioNet, chain ID 61999. Deployment runs in hosted GenVM, rather than a native local simulator. The exact deployment and interaction receipts are stored in [network.json](../evidence/network.json); snapshot, matrix, allocation and consent state are stored in [state.json](../evidence/state.json).

The live flow uses a coordinator plus four separate demonstration participant addresses. The two demands are translation of a public English API tutorial into Indonesian and English grammar/clarity copyediting. Supplier 0 explicitly offers both; supplier 1 offers translation and explicitly excludes English copyediting. Both restrict their offers to public API tutorials.

The expected compatibility graph is:

```text
       supplier 0   supplier 1
demand 0    YES          YES
demand 1    YES          NO
```

Only YES/YES/high cells are usable. The deterministic optimum is demand 0→supplier 1 and demand 1→supplier 0. A greedy demand 0→supplier 0 choice would yield only one match. After clearing, each matched demand and supplier address confirms the same input digest; each match becomes AGREED only after both confirmations.

The evidence records actual status and execution results; FINALIZED is checked separately from SUCCESS. IDLE votes are validators canceled after quorum and are not described as unanimous agreement. The run uses normal consensus, not leader-only mode. Source SHA-256 is `8534138390712061115940085b019b1d5cc566f49e2c07f3cfd504a12d8b3e9e`, matching the fetched deployment source byte-for-byte.

The semantic clearing transaction recorded three AGREE, one DISAGREE and one IDLE vote and finalized with MAJORITY_AGREE. The disagreement is preserved in the evidence; this run is not presented as unanimity or proof of universal model accuracy. Both allocated pairs subsequently received confirmation from both participants and reached AGREED.

## Independent verification

```bash
npm ci --ignore-scripts
npm run verify
python scripts/check_manifest.py
```

Node.js 22+ is required for the read-only network verification script. No signing key or wallet is needed. It fetches source and every recorded transaction, rather than trusting the supplied hash or merely the Explorer label. The Python command is an offline consistency check only.

The live example demonstrates the complete semantic-allocation-consent lifecycle. The independent reference test checks the optimizer on all 512 3×3 graphs. Neither result constitutes a proof of LLM accuracy on all possible adversarial specifications; that limitation and the commitment/identity boundary are documented in SECURITY.md.
