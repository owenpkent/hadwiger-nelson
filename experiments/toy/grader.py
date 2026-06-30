"""The grader: score a proposed chi-lower-bound TECHNIQUE against the toy battery.

A CANDIDATE is a function

    candidate(data: ToyData) -> int | None

that, from the abstract graph alone (n, edges), returns a claimed LOWER BOUND on
the chromatic number, or None when its technique is uninstantiable on this graph.
It never sees the answer key (known_chi).

The grader scores four things, mirroring the zeta toy's reproduce / reject /
clean / firewall:

  reproduces_target : bound >= 6 on every known chi>=6 instance (matches the SAT answer key).
  rejects_fakes     : bound < 6 on every known chi<6 instance (does not over-claim the target).
  control_immune    : bound <= known_chi on every CONTROL instance (the wrong-approach
                      firewall: a technique that paints Q^2 / L^infty / R^1 above its known
                      value is structurally wrong, the analog of D-H-immunity).
  k1_clean          : structural. The candidate only ever received ToyData (n, edges),
                      never known_chi, so it cannot have read the answer. Enforced by type.

The REFERENCE candidate (`sat_lower_bound`) returns the exact chi by SAT. It scores
all green: it is the known-correct technique in the toy, because chi is decidable on
finite graphs. The open problem is not computing chi, it is PRODUCING a planar
unit-distance graph with chi>=6 (W3), which the toy provably cannot contain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from experiments.toy.instances import ToyData, ToyInstance, FULL_BATTERY, chi_via_sat

Candidate = Callable[[ToyData], Optional[int]]


# ---------------------------------------------------------------------------
# The reference candidate: exact chi by SAT. The known-correct toy technique.
# ---------------------------------------------------------------------------
def sat_lower_bound(data: ToyData) -> Optional[int]:
    """The decidable gold standard: the exact chromatic number by SAT."""
    return chi_via_sat(data.n, data.edges)


@dataclass
class InstanceResult:
    name: str
    known_chi: int
    kind: str
    bound: Optional[int]
    correct: bool


@dataclass
class Scorecard:
    candidate_name: str
    results: list
    reproduces_target: bool
    rejects_fakes: bool
    control_immune: bool
    k1_clean: bool = True   # structural: candidates only ever receive (n, edges)

    @property
    def all_green(self) -> bool:
        return (self.reproduces_target and self.rejects_fakes
                and self.control_immune and self.k1_clean)

    def report(self) -> str:
        lines = [f"  candidate: {self.candidate_name}"]
        for r in self.results:
            b = "None" if r.bound is None else str(r.bound)
            mark = "OK " if r.correct else "BAD"
            tag = "target  " if r.known_chi >= 6 else ("control " if r.kind == "control" else "sub-6   ")
            lines.append(f"    [{mark}] {tag} {r.name:44} bound={b:>4}  (chi={r.known_chi})")
        lines.append(
            f"  => reproduces_target={self.reproduces_target}  rejects_fakes={self.rejects_fakes}  "
            f"control_immune={self.control_immune}  k1_clean={self.k1_clean}  "
            f"{'<<< ALL GREEN' if self.all_green else '<<< FAILS'}"
        )
        return "\n".join(lines)


def grade(candidate: Candidate, name: str = "candidate",
          battery: Optional[list] = None) -> Scorecard:
    """Run `candidate` over the battery and produce a Scorecard."""
    if battery is None:
        battery = FULL_BATTERY
    results = []
    reproduces_target = True
    rejects_fakes = True
    control_immune = True

    for inst in battery:
        try:
            bound = candidate(inst.to_data())
        except Exception:
            bound = None

        if inst.known_chi >= 6:
            correct = bound is not None and bound >= 6
            reproduces_target = reproduces_target and correct
        else:
            # known chi < 6: the technique must not claim the target here.
            claims_target = bound is not None and bound >= 6
            correct = not claims_target
            rejects_fakes = rejects_fakes and correct

        if inst.kind == "control":
            # The firewall: never exceed the control's known (true) chi.
            cimm = bound is None or bound <= inst.known_chi
            control_immune = control_immune and cimm
            correct = correct and cimm

        results.append(InstanceResult(inst.name, inst.known_chi, inst.kind, bound, correct))

    return Scorecard(name, results, reproduces_target, rejects_fakes, control_immune)


# ---------------------------------------------------------------------------
# Demonstration "bad" candidates: show the grader has teeth.
# ---------------------------------------------------------------------------
def clique_lower_bound(data: ToyData) -> Optional[int]:
    """Return the maximum clique size omega (a valid but weak lower bound, omega <= chi).
    On the unit-distance / triangle-free regime omega <= 3, so it can NEVER reach 6:
    FAILS reproduces_target on M^3(C5). This is exactly why the clamp route is hard,
    chi=6 with omega=3, and why a clique bound is useless for it."""
    try:
        import networkx as nx
    except Exception:
        return None
    g = nx.Graph()
    g.add_nodes_from(range(data.n))
    g.add_edges_from(data.edges)
    if data.n == 0:
        return 0
    return max((len(c) for c in nx.find_cliques(g)), default=1)


def max_degree_plus_one(data: ToyData) -> Optional[int]:
    """Return max-degree + 1 (a valid UPPER bound on chi, used illegitimately as a
    lower bound). It over-claims everywhere with a dense vertex: FAILS control_immune
    on the L^infty king-grid (interior degree 8 -> claims 9 where chi=4) and FAILS
    rejects_fakes on M^2(C5). The control-blind heuristic."""
    deg = [0] * data.n
    for u, v in data.edges:
        deg[u] += 1
        deg[v] += 1
    return (max(deg) + 1) if data.n else 0
