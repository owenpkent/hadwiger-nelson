# A. Kechris, Classical Descriptive Set Theory (Springer GTM 156, 1995)

Survey notes for the Hadwiger-Nelson project, Architecture A4 (set-theoretic / axiomatic).
Source text: `sources/_extracted/Kechris-1995-Classical-Descriptive-Set-Theory.txt` (OCR of `sources/books/Kechris-1995-Classical-Descriptive-Set-Theory.pdf`).
Page references below are to the book's internal numbering as it appears in the extracted text.

---

## What this gives Architecture A4

1. This book is the FOUNDATION layer, not a result about $\chi(\mathbb{R}^2)$. It defines and develops the entire vocabulary in which "the Borel chromatic number of the plane" becomes a sentence with a definite truth value, independent of choice pathology.
2. It pins down the three carrier spaces A4 needs: Polish spaces (R^2 is Polish), standard Borel spaces (Section 12), and the Baire space / Cantor space as universal models (Section 7).
3. It builds the Borel hierarchy $\Sigma^0_\xi, \Pi^0_\xi$ (Section 11.B) and the projective hierarchy $\Sigma^1_n, \Pi^1_n$ (Section 37): the exact ladder on which "Borel coloring", "analytic coloring", "Baire-measurable coloring" sit.
4. It gives the regularity theorems that make definable objects tame: analytic sets have the Baire property, are universally measurable, and have the perfect set property (Sections 29.A, 29.B, 14.13). These are why a Borel or analytic coloring cannot exploit the AC-only tricks behind Shelah-Soifer.
5. It states the precise mechanism by which AC produces pathology: the Vitali equivalence relation $xEy \iff x-y \in \mathbb{Q}$ has no Lebesgue-measurable and no Baire-property transversal (Section 18.D, 18.19). This is exactly the engine of the Shelah-Soifer "axiom-dependent chromatic number" phenomenon, stated here in its cleanest descriptive-set-theoretic form.
6. It exhibits a non-measurable / non-BP set built directly from AC by transfinite recursion (the Bernstein set, 8.24), demonstrating that AC is doing the work, and that ZF + DC alone does not deliver it.
7. It supplies the Borel isomorphism theorem (15.6): every uncountable standard Borel space is Borel-isomorphic to $\mathbb{R}$, so results proved for the Cantor space or Baire space transfer to the plane.
8. It supplies the separation and definability machinery (Lusin separation 14.7, Souslin's theorem $B = \Delta^1_1$ at 14.11, the closure properties of the hierarchies) used to certify that a candidate coloring really is Borel / analytic.
9. It does NOT contain Borel chromatic numbers, graph colorings, the $G_0$ dichotomy, or any combinatorics of definable graphs. Confirmed by exhaustive search: zero hits on "chromatic" or "colo(u)ring". The only "graph" content is the graph-theoretic-tree definition (4.13) and function graphs.
10. Honest relevance caveat: A4 is largely orthogonal to the project's current bottleneck (a $\chi \geq 6$ unit-distance graph embeddable in the plane, an A1 object). This book sharpens the meaning of the axiom-dependence story and underpins the measurable-chromatic refinement, but it does not by itself move any lower bound on $\chi(\mathbb{R}^2)$.

---

## How $\chi_{\mathrm{Borel}}(\mathbb{R}^2)$ sits on these foundations

The unit-distance graph $G$ on the plane has vertex set $\mathbb{R}^2$ (a Polish space, Section 3.A, Example 1) and edge set
$E = \{(x,y) \in \mathbb{R}^2 \times \mathbb{R}^2 : \|x - y\| = 1\}$.
This $E$ is a closed subset of $(\mathbb{R}^2)^2$, hence $\Pi^0_1$, hence Borel (Section 11.B). So $G$ is a "Borel graph" in the sense the later literature makes precise: a graph whose edge relation is a Borel subset of $X \times X$ on a standard Borel space $X$ (Section 12.B).

A coloring $c : \mathbb{R}^2 \to k$ (where $k = \{0, \dots, k-1\}$ carries the discrete standard Borel structure) is:
- a Borel coloring if $c$ is a Borel function (Section 11.C / 12.A), equivalently each color class $c^{-1}(i)$ is a Borel set;
- a Baire-measurable coloring if each color class has the Baire property (Section 8.F);
- a Lebesgue-measurable coloring if each color class is Lebesgue measurable (Section 17, 29).

A coloring is proper when adjacent points get different colors. The Borel chromatic number $\chi_{\mathrm{Borel}}(\mathbb{R}^2)$ is the least $k$ for which a proper Borel $k$-coloring exists, and analogously for the measurable chromatic number $\chi_m$. These are well defined without invoking a well-ordering of the reals, so they sidestep the Shelah-Soifer phenomenon entirely: the AC-dependent value of the ordinary $\chi(\mathbb{R}^2)$ comes from colorings whose color classes are non-measurable / lack the BP, and the regularity theorems below forbid such classes from being definable.

Which Kechris machinery underlies the definition:
- "Vertex space is standard Borel, edge set is Borel": Sections 3.A, 11, 12.
- "A coloring is a definable function; color classes inherit a definability class": Borel functions 11.C, Baire-measurable functions 8.I, the BP sigma-algebra 8.F, universally measurable sets 29.
- "Definable colorings cannot cheat the way AC colorings do": analytic sets have BP (29.5) and are universally measurable (29.7); the Vitali relation has no measurable transversal (18.19). The contrast object is the Bernstein set / AC-recursion construction (8.24).
- "Lower bounds transfer between R^2, Cantor space, Baire space": Borel isomorphism theorem 15.6, the universal role of N and C (Sections 6, 7).

What Kechris-Solecki-Todorcevic (1999), "Borel chromatic numbers", adds (NOT in this book; we do not have it):
- The general theory of $\chi_{\mathrm{Borel}}(G)$ for Borel graphs $G$ on standard Borel spaces, including basic bounds (e.g. a Borel graph of bounded degree $d$ has $\chi_{\mathrm{Borel}} \leq d + 1$, and the gap between $\chi$ and $\chi_{\mathrm{Borel}}$ can be infinite).
- The $G_0$ dichotomy: there is a single Borel graph $G_0$ such that any analytic graph either has countable Borel chromatic number or Borel-contains $G_0$ (so its Borel chromatic number is uncountable, in fact $> \aleph_0$). This is the definable analog of "obstruction to low chromatic number". Kechris explicitly stops at the prerequisites: it would build on his analytic-set theory (Chapter III), the Baire-category and BP apparatus (Section 8), the separation/dichotomy style of argument foreshadowed by the Hurewicz-type separation theorems (28.E, 21.F), and the standard-Borel framework (Section 12).
- For the plane specifically, the KST line and its successors (Schmerl, and later the measurable-chromatic literature) ask whether $\chi_{\mathrm{Borel}}(\mathbb{R}^2)$ or $\chi_m(\mathbb{R}^2)$ exceeds the combinatorial bounds. Kechris-1995 supplies only the substrate; the chromatic statements live downstream.

Detector note (A4 relative to the project's wrong-approach controls): a Borel-chromatic argument operates on $\mathbb{R}^2$ as a Polish space and uses the closedness of the unit-distance relation plus measure / category. It legitimately fails on $\mathbb{Q}^2$ (countable, so every coloring is Borel and $\chi_{\mathrm{Borel}}(\mathbb{Q}^2) = \chi(\mathbb{Q}^2) = 2$) and is exempt from the $\mathbb{Q}^2$ control in the same way Architecture A2 is. It would also have to engage the rotation structure to avoid trivializing on $\mathbb{R}^1$. This is consistent with A4 being a refinement of A2 rather than a route to a pure combinatorial $\chi \geq 6$.

---

## Structured section notes

### Chapter I. Polish Spaces (Sections 1-9)

Sets `definable in Polish (separable completely metrizable) spaces` is the subject; the introduction (pp. xv-xvii) states both hierarchies cleanly and is the best one-page summary in the book.

- Section 1 (Topological and Metric Spaces). Standard setup: open/closed, $G_\delta$, $F_\sigma$, Urysohn's lemma. Relevance: baseline; $E = \{\|x-y\| = 1\}$ is closed hence $\Pi^0_1$.
- Section 2 (Trees). Trees on $\mathbb{N}$ and on products, well-founded trees and ranks, the Kleene-Brouwer ordering. Relevance: the encoding machine for analytic / coanalytic sets used throughout Chapters III-IV; not directly used by A4 at the definitional level.
- Section 3 (Polish Spaces). (3.1) Definition: a space is Polish iff separable and completely metrizable. (3.3) closed subspaces, countable products, countable sums of Polish are Polish. Examples (3.A): $\mathbb{R}, \mathbb{C}, \mathbb{R}^n, \mathbb{R}^{\mathbb{N}}$, the unit interval, circle, cubes, tori; the Cantor space $2^{\mathbb{N}}$ and the Baire space $\mathbb{N}^{\mathbb{N}}$; separable Banach spaces. (3.11) $Y \subseteq X$ ($X$ Polish) is Polish iff $Y$ is $G_\delta$. Relevance: $\mathbb{R}^2$ is Polish, so A4 lives here. The Cantor/Baire spaces are the universal carriers.
- Section 4 (Compact Metrizable Spaces). Hilbert cube universality (every separable metrizable space embeds in $[0,1]^{\mathbb{N}}$), continuous images of the Cantor space, the hyperspace $K(X)$ of compact sets. Relevance: support machinery.
- Section 5 (Locally Compact Spaces). Relevance: support.
- Section 6 (Perfect Polish Spaces). (6.A) every nonempty perfect Polish space contains a homeomorphic copy of the Cantor space, hence has cardinality $2^{\aleph_0}$. (6.B) Cantor-Bendixson theorem: every Polish space is the disjoint union of a perfect set (its kernel) and a countable open set. Relevance: source of the perfect-set property and the cardinality dichotomy that the regularity theory generalizes.
- Section 7 (Zero-dimensional Spaces). Topological characterizations of the Cantor space and the Baire space; every zero-dimensional Polish space embeds in $\mathbb{N}^{\mathbb{N}}$; every Polish space is a continuous image of $\mathbb{N}^{\mathbb{N}}$. Relevance: lets one reduce questions on $\mathbb{R}^2$ to the Baire space.
- Section 8 (Baire Category). The A4-critical section.
  - 8.A Meager sets: nowhere dense, meager (first category), comeager (residual). Meager sets form a sigma-ideal. $\mathbb{Q}$ is meager in $\mathbb{R}$.
  - 8.B (8.4) Baire Category Theorem: every completely metrizable space and every locally compact Hausdorff space is a Baire space (comeager sets are dense).
  - 8.C-8.E Choquet games characterize Polish spaces.
  - 8.F Baire property. (8.21) $A$ has the BP iff $A =^* U$ (equal modulo meager) for some open $U$. (8.22) the BP sets form a sigma-algebra, the smallest one containing all open and all meager sets. (8.23) $A$ has BP iff $A = G \cup M$ ($G$ a $G_\delta$, $M$ meager) iff $A = F \setminus M$ ($F$ an $F_\sigma$, $M$ meager). (8.24) THERE IS A SET WITHOUT THE BP: a Bernstein set, built by transfinite recursion over an enumeration of the $2^{\aleph_0}$ perfect sets, using the Axiom of Choice. Relevance for A4: this is the explicit demonstration that AC, not ZF+DC, manufactures the irregular sets that ordinary (non-definable) colorings rely on.
  - 8.H Banach-Mazur game characterizes meagerness via a determined-ish game.
  - 8.K Kuratowski-Ulam theorem (the category analog of Fubini). Relevance: the category-quantifier calculus used to push BP through projections.
- Section 9 (Polish Groups). Metrizable and Polish groups, Baire-group actions, universal Polish groups. Relevance: the isometry group of the plane and the action of $O(2)$ live here; relevant if one studies invariance of colorings under the Euclidean group.

### Chapter II. Borel Sets (Sections 10-24)

- Section 10 (Measurable Spaces and Functions). Sigma-algebras and generators, measurable functions. Relevance: definition of "coloring as a measurable map into a discrete space".
- Section 11 (Borel Sets and Functions). 11.A Borel sets = smallest sigma-algebra containing the open sets. 11.B THE BOREL HIERARCHY: by transfinite recursion for $1 \leq \xi < \omega_1$,
  $\Sigma^0_1 = $ open, $\Pi^0_\xi = $ complements of $\Sigma^0_\xi$, $\Sigma^0_\xi = \{\bigcup_n A_n : A_n \in \Pi^0_{\xi_n}, \xi_n < \xi\}$ for $\xi > 1$; ambiguous classes $\Delta^0_\xi = \Sigma^0_\xi \cap \Pi^0_\xi$. So $\Sigma^0_2 = F_\sigma$, $\Pi^0_2 = G_\delta$, etc., and $B = \bigcup_{\xi < \omega_1} \Sigma^0_\xi$. Each class is contained in every class to its right. 11.C Borel functions; (11.6) Lebesgue-Hausdorff: the Borel real functions are the smallest class containing the continuous functions and closed under pointwise limits (the Baire-class stratification). Relevance: this is the ladder on which "$\Sigma^0_\xi$-measurable coloring" is defined; a Borel coloring is exactly a Borel function into discrete $k$.
- Section 12 (Standard Borel Spaces). (12.5) Definition: a measurable space $(X, S)$ is standard Borel if isomorphic to $(Y, B(Y))$ for some Polish $Y$. Products and sums of standard Borel are standard; Borel subsets of standard Borel are standard (13.4). 12.C the Effros Borel space $F(X)$ of closed subsets is standard (12.6). 12.F standard Borel groups. Relevance: the abstract setting in which Borel-graph / Borel-chromatic-number questions are posed.
- Section 13 (Borel Sets as Clopen Sets). Any countable family of Borel sets can be made clopen by refining to a finer Polish topology with the same Borel sets. Relevance: a standard normalization trick.
- Section 14 (Analytic Sets and the Separation Theorem). (14.5) $A$ is analytic ($\Sigma^1_1$) if it is a Borel image / continuous image of a Borel set, equivalently a projection of a Borel set. (14.7) LUSIN SEPARATION: two disjoint analytic sets are separated by a Borel set. (14.10) coanalytic ($\Pi^1_1$) = complement of analytic; bi-analytic $\Delta^1_1 = \Sigma^1_1 \cap \Pi^1_1$. (14.11) SOUSLIN'S THEOREM: $B(X) = \Delta^1_1(X)$, i.e. Borel = analytic and coanalytic. (14.12) a function is Borel iff its graph is Borel iff its graph is analytic; a Borel bijection is a Borel isomorphism. (14.13) PERFECT SET THEOREM FOR ANALYTIC SETS (Souslin): an analytic set is countable or contains a Cantor set. (14.14) analytic-invariant analytic sets are separated by an invariant Borel set. Relevance: separation + Souslin are how one certifies a constructed coloring is genuinely Borel; the analytic perfect-set property is a regularity property a definable coloring inherits.
- Section 15 (Borel Injections and Isomorphisms). (15.6) ISOMORPHISM THEOREM: standard Borel $X, Y$ are Borel isomorphic iff $\mathrm{card}(X) = \mathrm{card}(Y)$; in particular all uncountable standard Borel spaces are Borel isomorphic (to $\mathbb{R}$, to the Cantor space). (15.7) Borel Schroder-Bernstein. Relevance: lets Borel-chromatic results proved on $2^{\mathbb{N}}$ transfer to $\mathbb{R}^2$ as spaces (note: this transfer is at the level of the standard Borel structure, not the unit-distance graph structure, so it transports definability but not the specific geometry).
- Section 16 (Borel Sets and Baire Category). Borel definability of category notions, Vaught transforms, connections to model theory and to Cohen forcing. Relevance: forcing connection is the technical neighbor of the independence phenomena A4 cares about.
- Section 17 (Borel Sets and Measures). General measures, Borel measures, regularity and tightness, Lusin's theorem on measurable functions, the Polish space $P(X)$ of probability Borel measures, the isomorphism theorem for measures. (17.47 area) Lebesgue measurability discussed. Relevance: the measure-theoretic substrate for the measurable chromatic number $\chi_m$ (Architecture A2's home, refined by A4).
- Section 18 (Uniformization Theorems). 18.A Jankov-von Neumann: every $\Sigma^1_1$ set has a $\sigma(\Sigma^1_1)$-measurable (hence universally measurable, hence Baire-measurable) uniformizing function. 18.D Selectors and transversals: a Borel equivalence relation need not have a BP or measurable transversal. KEY EXAMPLE (text near 18.19): the Vitali equivalence relation $xEy \iff x - y \in \mathbb{Q}$ on $[0,1]$ has NO transversal that is Lebesgue measurable or has the BP. Smooth equivalence relations (18.20) are those Borel-reducible to equality. Relevance for A4: the Vitali example is the prototype of the Shelah-Soifer mechanism; the AC-chosen transversal is exactly the kind of non-measurable choice that makes the ordinary chromatic number axiom-sensitive, and uniformization theory says definable selectors avoid it only at a measurability cost.
- Section 19 (Partition Theorems). Comeager/non-meager pieces, a Ramsey theorem for Polish spaces, Galvin-Prikry, the Ellentuck topology, a Banach-space application. Relevance: definable Ramsey theory, the combinatorial neighbor of definable colorings (and the toolkit KST-style dichotomies draw on).
- Section 20 (Borel Determinacy). 20.A infinite games $G(A, X)$ with payoff $X \subseteq A^{\mathbb{N}}$; determined = one player has a winning strategy. Using AC there are non-determined sets (text near 6223). 20.B closed games are determined (Gale-Stewart). (20.5) MARTIN'S THEOREM: Borel games are determined (proved in ZFC, via game coverings). Relevance: determinacy is the deep regularity engine; it is what lifts BP / measurability / perfect-set property up the hierarchy, and it is the lever by which large-cardinal / choice assumptions interact with definable combinatorics.
- Section 21 (Games People Play). The unfolding (*-games, **-games / Banach-Mazur), Wadge games, separation games and Hurewicz's theorem, Turing degrees. (21.2 ff.) reprove the perfect set property and BP for analytic sets via games. Relevance: the Hurewicz-type separation / dichotomy machinery (21.F) is the stylistic ancestor of the $G_0$ dichotomy that KST 1999 proves.
- Section 22 (The Borel Hierarchy). Universal sets, Borel vs Wadge hierarchy, structural properties, the difference hierarchy. Establishes the hierarchy is PROPER (strict inclusions at every level). Relevance: confirms "Borel coloring" is a genuinely finer notion than "arbitrary coloring".
- Section 23 (Some Examples). 23.A combinatorial examples, classes of compact sets, sequence spaces, classes of continuous functions, universal sets. Relevance: worked complexity computations; no graph coloring.
- Section 24 (The Baire Hierarchy). Baire classes of functions; functions of Baire class 1. Relevance: stratifies "almost continuous" colorings.

### Chapter III. Analytic Sets (Sections 25-31)

- Section 25 (Representations of Analytic Sets). Analytic sets as projections / Souslin-operation results / well-ordered unions of Borel sets / open sets in strong Choquet spaces. Relevance: alternative certificates that a set is $\Sigma^1_1$.
- Section 26 (Universal and Complete Sets). Universal analytic sets exist; 26.B ANALYTIC DETERMINACY (Martin, from a measurable cardinal): analytic games are determined. Complete analytic sets; Borel-isomorphism classification. Relevance: first place a large-cardinal hypothesis enters; this is the formal home of "determinacy strengthens regularity beyond Borel".
- Section 27 (Examples). Ill-founded trees, closed sets, model-theoretic structures, isomorphism, universal sets. Relevance: complexity benchmarks.
- Section 28 (Separation Theorems). Lusin revisited, Novikov separation, Borel sets with open/closed sections, special separation theorems, 28.E HUREWICZ-TYPE SEPARATION THEOREMS. Relevance: 28.E is the technical template (a set is in a low class, or it contains a canonical hard obstruction) that the $G_0$ dichotomy follows.
- Section 29 (Regularity Properties). THE A4-RELEVANT REGULARITY PACKAGE.
  - 29.A (29.1) Perfect Set Theorem for analytic sets (Souslin): analytic set is countable or contains a Cantor set. (29.3) analytic set is contained in a $K_\sigma$ or contains a closed copy of $\mathbb{N}^{\mathbb{N}}$.
  - 29.B (29.5) every analytic set has the BAIRE PROPERTY. (29.7) (Lusin) every analytic set is UNIVERSALLY MEASURABLE. (29.8) (Silver) analytic sets are completely Ramsey. (29.9) (Jankov-von Neumann) $\Sigma^1_1$ sets have universally-measurable, Baire-measurable uniformizations.
  - 29.C closure property of the Souslin operation; 29.D the C-sets. Relevance for A4: this is the decisive contrast with 8.24. Definable (analytic, hence Borel) sets are automatically measurable and have the BP, so a Borel / analytic coloring's color classes are tame. The axiom-dependence of $\chi(\mathbb{R}^2)$ therefore cannot survive the definability restriction: $\chi_{\mathrm{Borel}}$ and $\chi_m$ are choice-stable.
- Section 30 (Capacities). The Choquet capacitability theorem. Relevance: potential-theory neighbor; not central to A4.
- Section 31 (Analytic Well-founded Relations). Bounds on ranks; the Kunen-Martin theorem (an analytic well-founded relation has rank $< \omega_1$). Relevance: rank/boundedness method, used in coanalytic complexity proofs.

### Chapter IV. Co-Analytic Sets (Sections 32-36)

- Section 32 (Review). Basic facts, representations, regularity of coanalytic sets. Relevance: $\Pi^1_1$ context. Note: coanalytic sets do NOT in general have the perfect set property in ZFC (this is independent), the first genuinely choice/large-cardinal-sensitive level.
- Section 33 (Examples). Well-founded trees, well-orderings, differentiable functions, everywhere convergence, singular functions, separable Banach spaces, etc. Many natural "definably hard" sets are $\Pi^1_1$-complete. Relevance: complexity benchmarks.
- Section 34 (Co-Analytic Ranks). Ranks and prewellorderings, ranked classes, coanalytic ranks, derivatives. Relevance: the rank apparatus.
- Section 35 (Rank Theory). Reflection theorems, boundedness of ranks, the rank method, the strategic uniformization theorem, coanalytic families of closed sets and their sigma-ideals. Relevance: technical engine of Chapter IV.
- Section 36 (Scales and Uniformization). $\kappa$-Souslin sets, scales, scaled classes, the NOVIKOV-KONDO UNIFORMIZATION THEOREM ($\Pi^1_1$ sets have $\Pi^1_1$ uniformizations), regularity of uniformizing functions. Relevance: the strongest classical uniformization result; foundational for projective structure theory.

### Chapter V. Projective Sets (Sections 37-40)

- Section 37 (The Projective Hierarchy). 37.A definition: $\Sigma^1_{n+1} = $ projections of $\Pi^1_n$ sets, $\Pi^1_{n+1} = $ complements, $\Delta^1_n = \Sigma^1_n \cap \Pi^1_n$; classically $A, CA, PCA, CPCA, \dots$. $P = \bigcup_n \Sigma^1_n$. (37.1) closure properties: $\Sigma^1_n$ closed under continuous images / projection / countable unions and intersections; $\Pi^1_n$ under co-projection; $\Delta^1_n$ is a sigma-algebra. The hierarchy is proper. Relevance: the full ladder above analytic; where harder definable colorings would sit if ever needed.
- Section 38 (Projective Determinacy). The second level; PROJECTIVE DETERMINACY (PD) as a hypothesis; its consequences for regularity (under PD all projective sets have BP, are Lebesgue measurable, have the perfect set property). Relevance: PD is the axiom under which the entire projective hierarchy becomes as tame as the Borel level; it is the strong-axiom backdrop to A4's choice-sensitivity discussion.
- Section 39 (The Periodicity Theorems). First / second / third periodicity (Moschovakis): prewellordering, scale, and uniformization properties alternate up the hierarchy under determinacy. Relevance: structural, deep; not needed for the plane.
- Section 40 (Epilogue). 40.A extensions beyond projective (sets in $L(\mathbb{R})$, hyperprojective). 40.B effective descriptive set theory (lightface classes via computability; effective results imply classical ones). 40.C LARGE CARDINALS: a deep duality between definable determinacy and large cardinals / inner models. 40.D connections to measure theory, probability, functional analysis, harmonic analysis, operator algebras; the remark that projective sets have all the regularity properties (universal measurability, BP) plus strong closure, so they are a good framework for applications. Relevance for A4: 40.C names the precise reason the choice/determinacy spectrum matters, and 40.D is the explicit statement that definable = regular, which is the conceptual payoff A4 draws on.

### Appendices

- Appendix A (Ordinals and Cardinals): ordinals, cofinality, ordinal arithmetic, initial ordinals, $\aleph_n$, $2^{\aleph_0}$. AC stated as "every set has a cardinality" (a bijection to a unique initial ordinal). Relevance: the AC usage that A4 toggles.
- Appendix B (Well-founded Relations): well-foundedness, induction and recursion on well-founded relations, rank functions. Relevance: underlies tree ranks throughout.
- Appendix C (On Logical Notation): the $\Sigma / \Pi$ quantifier-counting notation. Relevance: reading aid.

---

## Cross-references followed up / to follow up

- Kechris, Solecki, Todorcevic, "Borel chromatic numbers", Adv. Math. 141 (1999). NOT IN REPO. This is the actual A4 result for definable graph coloring (the $G_0$ dichotomy). It builds on: Chapter I Section 8 (Baire category, BP), Chapter II Section 12 (standard Borel spaces) and Section 14 (analytic sets), Chapter III Section 28.E and Section 21.F (Hurewicz-type separation / dichotomy style). HIGH PRIORITY to obtain.
- Moschovakis, "Descriptive Set Theory" (1980, 2nd ed. 2009): the reference Kechris repeatedly defers to for effective DST, determinacy, and the projective structure theory (Sections 40.B-C). Useful if A4 needs effective bounds.
- Shelah-Soifer (the project's named A4 landmark): the mechanism is the AC transversal of the Vitali relation (Section 18.D here) plus Bernstein-style recursion (8.24). Cross-check the project's existing Shelah-Soifer write-up against these two Kechris locations.
- For $\chi_m(\mathbb{R}^2)$: the project's A2 thread (Falconer, Ambrus) is the measurable-chromatic neighbor; this book supplies the measure substrate (Section 17, 29).

## Discrepancy log

- No content discrepancies with the atlas were found, because this book asserts nothing about $\chi(\mathbb{R}^2)$ to disagree with. The one framing point worth flagging to the SYNTHESIZER: the project README places A4 as "Shelah-Soifer + Borel chromatic number". This book covers ONLY the foundational half. If any atlas text implies Kechris-1995 itself contains Borel chromatic numbers or the $G_0$ dichotomy, that should be corrected: it does not (verified by full-text search, zero hits on "chromatic" / "coloring").

## What this enables / what remains open

ENABLES:
- A precise, choice-stable definition of $\chi_{\mathrm{Borel}}(\mathbb{R}^2)$ and $\chi_m(\mathbb{R}^2)$ for BUILDER / SYNTHESIZER, with exact citations for every ingredient (Polish: 3.A; Borel graph edge set $\Pi^0_1$: 11.B; coloring as Borel function: 11.C, 12; color classes regular: 29.5, 29.7).
- A clean statement of the Shelah-Soifer mechanism for ADVERSARY to probe: non-measurable colorings exist via AC (8.24) and via the Vitali transversal (18.19), and these are exactly what the definability restriction kills (29.B).
- The transfer lemma (Borel isomorphism, 15.6) and the hierarchy/closure facts needed to certify any future definable coloring construction.

REMAINS OPEN / MISSING:
- The actual KST 1999 paper (Borel chromatic numbers, the $G_0$ dichotomy). Without it, A4 has the foundation but not the theorem that turns the foundation into a lower-bound tool for definable colorings of the plane.
- Whether any of this moves $\chi(\mathbb{R}^2)$ or even $\chi_{\mathrm{Borel}}(\mathbb{R}^2)$ above the known $\geq 5$. It does not, by itself. A4 stays orthogonal to the project's current bottleneck (a $\chi \geq 6$ unit-distance graph embeddable in the plane, an A1 object).
