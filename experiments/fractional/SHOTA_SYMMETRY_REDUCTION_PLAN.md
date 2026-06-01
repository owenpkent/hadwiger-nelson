# Shot A build spec: symmetry-reduced order-2 SDP for the measurable chi_m >= 6 attack

Status as of 2026-06-01 (L43): the multi-class measurable moment stack (e3k -> e3l ->
e3m order-1 -> e3n order-2) is correct and validated, but the order-2 SDP does not
scale (L41): the PSD block of size `|B| = 1 + nk + (C(n,2)k^2 - Ek)` is the cost, and
X_23 (n=23, k=5) gives `|B| ~ 4141`, out of naive cvxpy/CLARABEL reach. Degree-1
(order-1) was shown too weak on X_23 (L43: margin 0, IEC only to subset size 2). So
the measurable route is pinned to ONE engineering task: a symmetry-reduced order-2
SDP. This document is the build spec.

## The two symmetries

The order-2 moment relaxation is invariant under two groups acting independently:

1. **S_k, permuting color labels** (FREE, always present, no config structure needed).
2. **The O(2)-averaged congruence action on the configuration** (the IEC symmetry;
   config-dependent, the harder half).

This spec does the S_k reduction first (it block-diagonalizes the PSD cone with zero
config analysis and is enough to test whether it alone unlocks X_23), then the
congruence reduction.

## Part 1: S_k color-symmetrization (the easy, high-leverage half)

### Theorem (lossless). The optimum of the Phase-1 relaxation is attained on the
S_k-invariant subspace.

*Proof.* The objective (min sum of |slack| on the per-color Bochner couplings) and
every constraint (normalization, singleton<-pair marginalization, no-monochromatic-
edge, per-color Bochner positivity `nu_c >= 0` with `f_c(1)=0`, the order-t PSD
moment matrix, and the IEC Formulation-1/2 equalities) are invariant under relabeling
the k colors by any `pi in S_k`: relabeling permutes the variables among themselves
and maps the constraint set onto itself. The feasible set is convex and the objective
convex, so for any feasible point `z` the average `z_sym = (1/k!) sum_pi pi.z` is
feasible with objective `<= obj(z)`. `z_sym` is S_k-invariant. QED.

Validated computationally in `shotA_symmetry_validation.py` (e3m `symmetrize=True`):
on triangle/rhombus/Moser at k=4,5, LP and PSD, base and +IEC, the symmetrized
margin equals the plain margin (lossless) and never exceeds it (no fake certificate).

### The S_k orbit structure of the order-1 / order-2 variables

- Singletons `y_i(c)`: orbit `{y_i(c) : c}` -> one value per vertex `y_i` (and with
  normalization `sum_c y_i(c)=1`, `y_i(c) = 1/k`).
- Bochner masses `nu_c`: one shared measure `nu`.
- Pairwise `y_ij(c,c')`: two orbits, `c=c'` (diagonal) and `c != c'` (off-diagonal):
  `y_ij^= , y_ij^!=`, with `y_ij^= + (k-1) y_ij^!= = 1/k` and `y_ij^= = 0` on edges.
- Order-2 patterns `((i,c),(j,c'))` etc.: orbits indexed by the *pattern of color
  coincidences* (a set partition of the involved vertices), NOT the colors themselves.

### Block-diagonalization of the order-1 PSD matrix (the part that buys scale)

`M` is indexed by `{*} cup {(i,c) : i in [n], c in [k]}`, size `1 + nk`. The S_k action
fixes `*` and acts on `(i,c)` by `c -> pi(c)` (vertices fixed). The index space
decomposes as `triv` (the `*`) plus, per vertex, the permutation representation of
S_k on k colors `= triv_i (+) std_i` with `dim std = k-1`. Collecting isotypic
components:

- **Trivial block** (dim `1 + n`): basis `{*}` and the color-averages
  `u_i = (1/sqrt k) sum_c e_{(i,c)}`. Entries:
  `M_triv[*,*] = 1`, `M_triv[*, u_i] = (1/sqrt k) sum_c y_i(c) = sqrt(k) y_i^sym`,
  `M_triv[u_i, u_j] = (1/k) sum_{c,c'} y_ij(c,c') = (1/k)(k y_ij^= + k(k-1) y_ij^!=)`
  for i != j, and `(1/k) sum_c y_i(c) = ...` on the diagonal.
- **Standard block** (multiplicity `n`, each copy dim `k-1`): by Schur's lemma the
  restriction is `M_std (x) I_{k-1}` for an `n x n` matrix `M_std` with
  `M_std[i,j] = y_ij^= - y_ij^!=` (i != j) and `M_std[i,i] = y_i(c) - (off-diagonal
  within-vertex)`; the within-vertex singleton block `diag(y_i(.))` contributes
  `y_i^= - 0` on the standard component. (Exact entry: the standard-isotypic
  eigenvalue of the `k x k` color block.)

`M >= 0` iff `M_triv >= 0` AND `M_std >= 0`. So the order-1 PSD of size `1+nk`
reduces to one `(1+n) x (1+n)` block and one `n x n` block, **independent of k**.

For order-2 the same machinery applies with the index set replaced by the size-<=2
colored patterns; the isotypic blocks are larger but the `k`-dependence collapses
the same way (block sizes scale with the number of *vertex-pattern* orbits, times
small representation-theoretic multiplicities, not with `k^2`). For X_23, k=5 this is
the difference between `|B| ~ 4141` and a handful of blocks of size `~ O(n^2)`.

### Build steps (Part 1)
1. Implement the symmetry-adapted basis change for the order-1 matrix; cross-check
   `M_triv, M_std` PSD against the full `M >= 0` on small configs (must agree
   exactly: same margins as `shotA_symmetry_validation.py`).
2. Lift to order-2: enumerate size-<=2 colored-pattern orbits under S_k, build the
   reduced blocks, cross-check vs naive e3n on rhombus/Moser (margins must match).
3. Run order-2 reduced on X_23 k=4 (must reproduce >= 5 if order-2 IEC size-4 is
   strong enough; this is the test L43's degree-1 failed) and k=5 (open >= 6).

## Part 2: O(2)-congruence reduction (the harder half, only if Part 1 insufficient)

If the S_k reduction alone does not bring X_23 order-2 into solver range, block-
diagonalize further by the configuration's congruence automorphisms (the IEC
symmetry, de Laat-Vallentin / DeCorte-Oliveira-Vallentin 2022, note 08). This needs
the config's isometry/congruence group and a second symmetry-adapted basis on the
vertex indices. Strictly config-dependent and more delicate; defer until Part 1 is
measured.

## Correctness discipline (non-negotiable)

A measurable "certificate" here is a positive slack margin, so a WRONG reduction
silently FAKES a chi_m bound (cf. L40's SCS noise-floor incident). Therefore every
reduced solver must, before any bound is claimed:
- reproduce the naive e3n/e3m margins to `<= 1e-6` on ALL small configs (triangle,
  rhombus, Moser, k=4,5, base/+IEC);
- pass the `chi_m <= 7` gate (k=7 stays feasible);
- keep the cert path live (triangle k=2 / Moser k=3 infeasible);
- re-verify any positive X_23 margin at higher precision (ideally an exact rational
  dual) before it is recorded as a bound.

## What is done vs open
- DONE (2026-06-01, L44): lossless S_k symmetrization theorem + computational
  validation (`shotA_symmetry_validation.py`, e3m `symmetrize=True`).
- DONE (2026-06-01, L46): the order-1 block-diagonalized builder
  (`e3p_blockdiag_order1.py`). Reproduces e3m full-size margins exactly on all small
  configs (24/24, no fake certificate); reduces the PSD side from 1+nk to n
  (independent of k; X_23: 93 -> 23) and runs X_23 k=4 PSD+IEC in ~3 s vs e3m's
  ~290 s. The S_k symmetry-adapted basis is validated. IEC collapses to congruent-
  pair same-color-density equalities.
- DONE (2026-06-01, L47): the ORDER-2 block-diagonalized builder
  (`e3q_blockdiag_order2.py`). Reproduces naive e3n margins on triangle + rhombus
  (k=4,5, base/+IEC, 8/8, no fake certificate). Required the Murota multiplicity
  alignment (the naive eigenbasis provably fails at order 2: irreps with
  multiplicity > 1; alignment residual ~1e-13). PSD splits into ~4 blocks of size
  independent of k (rhombus 93->max 17 at k=4; 146->max 17 at k=5); 50-380x faster.
- DONE (2026-06-01, L48): pushed e3q to X_23. With the Z = V^T R2 V basis fix, the
  X_23 k=4 order-2 basis (|B|=3953) builds in 17.5 s into 4 blocks of size 253-735
  (~150x less PSD work than the naive 3953^2, which OOMs at 25 GB). BUT the full
  solve OOMs at 171 GiB: X_23 order-2 has 98627 MOMENT VARIABLES, which S_k does NOT
  reduce (it acts on the color axis, shrinking blocks; the variable count is a
  vertex-combinatorial quantity). 
- NEXT (Part 2, now REQUIRED not optional): the O(2)-congruence reduction. It acts on
  the VERTEX axis: congruent vertex-subsets share a moment, collapsing the 98627
  variables toward the few hundred distinct congruence types (X_23 has only 27
  distinct distances). This is the OTHER half of the reduction; without it the order-2
  moment-variable count alone blocks X_23 regardless of the PSD block sizes. Build it,
  cross-check vs e3q on small configs (margins must match), then run X_23 k=4
  (retest >=5) and k=5 (open >=6).
