"""The HN toy sandbox: a checkable training ground for chi-lower-bound techniques.

Finite graphs are the toy world where the chromatic number is a decidable theorem
(SAT). Because the answer is known, this sandbox grades a proposed lower-bound
TECHNIQUE right or wrong and catches a soft, circular, or control-blind argument on
contact, the HN analog of the zeta repo's function-field toy.

Modules:
  instances : the positive battery (chi>=6), the negative battery (chi<6 incl the
              chi=5 fakes), and the control battery (Q^2 / L^infty / R^1 as the
              firewall) + the candidate's (n, edges)-only data view + chi_via_sat.
  grader    : the four-part grader (reproduces-target / rejects-fakes /
              control-immune / k1-clean) + the reference candidate (exact chi by
              SAT) + demonstration bad candidates.
  play      : the top-level demo.

The honest caveat: the toy grades the TECHNIQUE, it cannot contain the OBSTRUCTION.
chi is decidable here because the graphs are finite; the real wall is W3, the
unit-distance realizability of a chi>=6 host in R^2. The delta between passing the
battery and producing a planar UDG is the compass, not the proof.
"""

from experiments.toy.instances import (
    ToyData,
    ToyInstance,
    POSITIVE_BATTERY,
    NEGATIVE_BATTERY,
    CONTROL_BATTERY,
    FULL_BATTERY,
    chi_via_sat,
)
from experiments.toy.grader import (
    grade,
    sat_lower_bound,
    clique_lower_bound,
    max_degree_plus_one,
    Scorecard,
)

__all__ = [
    "ToyData",
    "ToyInstance",
    "POSITIVE_BATTERY",
    "NEGATIVE_BATTERY",
    "CONTROL_BATTERY",
    "FULL_BATTERY",
    "chi_via_sat",
    "grade",
    "sat_lower_bound",
    "clique_lower_bound",
    "max_degree_plus_one",
    "Scorecard",
]
