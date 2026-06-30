# Obstruction-map survey (outline / scaffold)

Status: **outline only.** A scaffold for a potential secondary publication that
operationalizes the program's central observation: all four architectures bottom
out at one object. It claims **no new theorem**; its content is the map of where
everything is provably stuck. Adapted from the zeta repo's obstruction-map survey
genre; see [`../../experiments/ZETA_INNOVATION_TRANSFER.md`](../../experiments/ZETA_INNOVATION_TRANSFER.md).

Source material: this atlas ([`README.md`](README.md)), the C1 forcing-sterility +
codegree note ([`../../paper/main.tex`](../../paper/main.tex)), and
[`../../experiments/LOAD_BEARING_FACTS.md`](../../experiments/LOAD_BEARING_FACTS.md).
Honesty contract: every claim tagged PROVEN or CONJECTURAL; no claim of progress on
the bound.

## Thesis (one paragraph)

The four standard architectures for $\chi(\mathbb{R}^2) \ge 6$ are not four
independent frontiers; they converge on a single missing object, a
unit-distance-realizable flexible color-clamp (equivalently a $\chi=6$ UDG embedding
in the plane). We map each architecture to the precise point where it stalls, and we
show the wanted gadget is pinched by a conjunction of four properties, each provably
necessary and each closing off a distinct manufacturing strategy.

## Section 1. The four architectures as frameworks

One subsection each (combinatorial, measurable, fractional, axiomatic). For each:
the strongest known result, the mechanism, and the exact stalling point. Lead with
the shared reduction to the clamp / its analogs.

## Section 2. The scorecard

A table grading each architecture against fixed columns. The columns ARE the
discipline (a method scores only if it clears all four):

| Architecture | produces a finite witness | respects $\mathbb{Q}^2$ ($\chi=2$) | respects $L^\infty$ ($\chi=4$) | reaches $\chi \ge 6$ |
|--------------|---------------------------|------------------------------------|--------------------------------|----------------------|
| 1 UDG        | yes (the goal)            | yes                                | yes                            | OPEN (W3)            |
| 2 measurable | no (bound on $\chi_m$)     | n/a (measure zero)                 | yes                            | order-2 CLOSED       |
| 3 fractional | no                        | yes                                | yes                            | plateau              |
| 4 Borel      | no                        | via rotation group                 | must not be norm-blind         | dark horse           |

(Fill cells from the atlas; cite each verdict.)

## Section 3. The four-property irreducibility bracket

The wanted host gadget must simultaneously be:

1. **K4-free** (the unit-distance graph has $\omega \le 3$),
2. **6-critical** (so a single contraction yields $\chi \ge 6$),
3. **UDG-realizable in the plane** (W3, Theorem R cocircularity),
4. **not $K_{2,3}$-excluded** (two unit circles meet in $\le 2$ points, L63 codegree wall).

Show each property is droppable by a distinct host-factory result: the abstract clamp
drops (3); the nauty-free host factory produces (1)+(2) abundantly (L63); the codegree
wall is exactly the obstruction to keeping (3)+(4) together (L63, L69). The bracket is
the survey's one genuinely new framing (a synthesis, not a theorem).

## Section 4. Why the controls are load-bearing

The $\mathbb{Q}^2$ / $L^\infty$ / $\mathbb{R}^1$ controls are not decoration: each
kills a natural-looking route (norm-blind Borel over-proves on $L^\infty$; naive
forcing over-proves on $\mathbb{Q}^2$; rotation-blind measure arguments over-prove on
$\mathbb{R}^1$). Present the control firewall (`experiments/lemma_db/`) as the
structural-honesty instrument and tabulate which routes each control eliminates.

## Section 5. What would move the map

The single most-leveraged open node (a new $\chi=5$ UDG outside the lineage with a
wide imprimitive interface), and the falsifiability triggers from
[`../../experiments/PHASE_STATE.md`](../../experiments/PHASE_STATE.md).

## Venue / scope notes

Geombinatorics or an arXiv math.CO survey, alongside C1. Lower priority than C1/C3.
If pursued, register it in [`../../experiments/PUBLICATIONS.md`](../../experiments/PUBLICATIONS.md)
with an honest V/N/S (expected N=2 framing, S=2 closes-no-route-but-maps-them, no new bound).
