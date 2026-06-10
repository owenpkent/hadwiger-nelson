# 2026-06-09 lens dossier (provenance for L58-L62)

Raw structured output of the `hn-first-principles-attack` workflow (10 first-principles
lenses, adversary per proposal). Committed as provenance: LEARNINGS L58-L62 summarize
this material; the full conjecture text, falsifiable predictions, and adversary verdicts
live here.

- `result_*.json` (26 files): one per agent. Odd/even mix of BUILDER generators (`lens`,
  `conjectures`, `experiment`, `detector_self_check`) and ADVERSARY verdicts (`verdict`,
  `kills`, `surviving_kernel`, `steelman`). Workflow run `wf_e43e9fa0-d1a`.
- `COMPACT_DOSSIER.txt`: human-readable digest of all results (the form synthesized into L58).

The statmech lens failed twice in a StructuredOutput retry loop and never delivered, so 9
of 10 lenses are represented. These are AI-generated proposals, not verified results; the
verified follow-ups are the committed scripts (e9-e12, critscan) and LEARNINGS L58-L62.
