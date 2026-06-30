# lemma_db

A queryable proof-dependency DAG for the Hadwiger-Nelson program, with a
control-object firewall. Adapted from the zeta repo's Davenport-Heilbronn
firewall; see [`../ZETA_INNOVATION_TRANSFER.md`](../ZETA_INNOVATION_TRANSFER.md).

It answers three questions that LEARNINGS.md and the Lean skeleton cannot answer
mechanically:

1. **What can I work on now?** The `frontier` view: open nodes whose every
   load-bearing prerequisite is already proven or external.
2. **Is the program still non-circular?** The `control_audit` firewall: it fails
   (non-zero exit) if any node whose argument is also valid on a control object
   ($\mathbb{Q}^2$ $\chi=2$, $L^\infty$ $\chi=4$, $\mathbb{R}^1$ $\chi=2$) sits
   on a load-bearing path to a strictly larger $\chi$ lower-bound claim. Such an
   argument would over-prove on the control, so it is structurally wrong.
3. **Where is the believed-but-unproven gap?** `--deps chi_r2_ge6` lists the
   load-bearing prerequisites of the goal, open ones first. Today that is exactly
   one node: `w3_realizable`.

## Files

- `schema.sql` - tables (`nodes`, `edges`, `controls`, `node_controls`) and views
  (`v_load_bearing`, `frontier`, `control_audit`). Pure SQLite, no extensions.
- `seed_lemmas.json` - the actual proof skeleton. **This is the source of truth.**
  Edit it, then rebuild. Keep it in sync with LEARNINGS.md and PUBLICATIONS.md.
- `build_db.py` - materializes `_cache/lemma_db.sqlite` and runs the audit.
- `_cache/lemma_db.sqlite` - the built DB (gitignored; rebuilt deterministically).

## Usage

```powershell
python -m experiments.lemma_db.build_db                # build + audit (CI gate)
python -m experiments.lemma_db.build_db --frontier     # open nodes ready to attack
python -m experiments.lemma_db.build_db --deps chi_r2_ge6   # prerequisites of the goal
python -m experiments.lemma_db.build_db --selftest     # prove the firewall fires
```

Exit code = number of firewall violations (0 = clean). Wire it into CI alongside
`experiments/_shared/smoke_test.py`.

## Data model

A node carries `kind` (target / result / theorem / lemma / conjecture / note /
kill), `arch` (arch1..arch4 / shared), `status` (proven / external / open /
conjectural / refuted), an optional `claims_bound` (N for a "$\chi(\mathbb{R}^2)
\ge N$" claim; NULL otherwise), and `control_buildable` (the controls on which
its argument is also valid; empty for a genuinely-Euclidean node).

Edges split into two classes:

- **Load-bearing** (`depends_on`, `specializes`): src's validity rests on dst.
  Only these propagate the firewall and feed `frontier` / `--deps`.
- **Annotation** (`motivates`, `constrains`, `refutes`, `would_prove`):
  commentary that does not transmit logical dependence.

The `kill_*` nodes double as a structured freeze-list: each dead approach is a
refuted node, and the control-blind ones (e.g. `kill_norm_blind_borel` on
$L^\infty$, `kill_q2_naive_lift` on $\mathbb{Q}^2$) carry their control flag, so
if anyone ever re-wires one as load-bearing the firewall catches it. See also the
human-readable [`../FREEZE_LIST.md`](../FREEZE_LIST.md).

`claims_bound` is intentionally NULL on every $\chi_m$ (measurable) node: a
measurable lower bound does NOT load-bear an ordinary-$\chi$ target (the K1
circularity guard, recorded as the `bridge_chim_chi` node and as gate 4b in
[`../PUBLICATIONS.md`](../PUBLICATIONS.md)).

## Maintenance

When a finding lands in LEARNINGS, add or update its node and edges in
`seed_lemmas.json` and rebuild. A new lower-bound argument that trips the firewall
is telling you something true: either the argument is wrong, or you mislabeled a
`control_buildable` flag. Do not silence it by deleting the flag without a reason.
