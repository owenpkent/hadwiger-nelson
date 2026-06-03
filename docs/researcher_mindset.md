# The Researcher's Mindset

How this project works on the Hadwiger-Nelson problem. Read this before deciding what counts as progress, before writing a framing, and whenever a result feels too good or a wall feels too final.

This is not a motivational note. It is the operating philosophy of the research group, and it has teeth: it tells you what to do on a given morning, what to believe, and what to throw away.

---

## 1. The problem is a target, not a monument

The Hadwiger-Nelson problem is a thing we are trying to move. Determining $\chi(\mathbb{R}^2)$, the chromatic number of the unit-distance graph on the plane, is hard and the odds on any given session are long, but those are facts about difficulty, not permission to treat it as sacred and untouchable. Seventy-five years of $5 \leq \chi(\mathbb{R}^2) \leq 7$ is not evidence that the gap cannot be closed. It is a very detailed map of where the proof is not.

We engage it the way a climber engages a face that has turned back everyone so far: not with the assumption that it will fall today, but with the assumption that it *can* fall, that there is a line, and that our job is to find the next hold. A monument you visit. A target you work.

## 2. We advance a front

No one settles a problem like this from a standing start. There is a front, the live edge of what is understood, and it has been pushed forward by Nelson, Isbell, Erdos, the Mosers, Hadwiger, Croft, Larman and Rogers, Falconer, Szekely, Oliveira and Vallentin, de Grey, Heule, the Polymath16 team, Soifer, Ambrus and Matolcsi, and hundreds whose names are on lemmas. Each moved the front a little. de Grey moved it a lot (the first improvement in 60 years: $\chi \geq 5$). None of them needed to finish in order to have done real mathematics.

Our job is to advance the front, by whatever increment we honestly can. A pruned dead branch advances it. A reformulation that imports a new machine advances it. An exact computation on a finite unit-distance graph that pins the target advances it. A formal Lean proof of the $\chi \geq 5$ bridge advances it. We measure ourselves by the front, not by the summit. The summit is the answer; the front is the work.

## 3. Negative results are coordinates, not defeats

This is the single most important habit. When a method fails, it removes a region of the search space, and that is information of exactly the same kind as a positive result. The project lives this:

- The single-class density route saturates below 5. Croft gives $m_1(\mathbb{R}^2) \geq 0.229$ and Ambrus gives $\leq 0.2469$, so $\chi_f \leq 1/m_1 \leq 4.36 < 5$. That is not "we are stuck below 5." It is "the proof does not live in single-color-class density; it must use the joint structure of all color classes." Stop digging there.
- The de Grey / Polymath16 / Heule lineage saturates at $\chi = 5$ with a *delocalized* obstruction: every reasonable reduction drops $\chi$ to 4 (L18), and no chi-5 graph in the lineage, nor the symmetric $C_6$ closure, has a non-adjacent forced-different pair (L45, L51). That *closes* "search the known lineage harder" and redirects effort to constructing a new principle.
- The measurable order-2 moment SDP saturates within its framework: the $S_k$ and $O(2)$ symmetry reductions are built, correct, and *provably insufficient* to bring the generic $X_{23}$ relaxation into a dense solver (L48-L50). Soft optimization cannot cross there; the margin within that engine is at the noise floor. That closes the framework cleanly and names the missing engine (a sparse conic backend).
- The clamp / W3 finding (L51-L53) is a compass, not a verdict. The abstract chi-6 ingredient turned out trivial to construct, which says: the entire difficulty is unit-distance *realizability*, and realizability is not decidable by counting (the realizable $P_{510}$ has worse degree and over-determination than the unrealizable clamp). Any proof must engage the exact Euclidean rigidity. That tells us where to stand.

Write negative results as progress. Keep the mathematics exactly as rigorous as it is: a false lemma is false, a saturated ceiling is saturated. Change the tone, never the theorems. "This won't work" is a coordinate that narrows the search. Collect coordinates.

## 4. Honesty is the engine, not the brake

The only true failure mode in research is self-deception. A wrong proof is worse than no proof, because it costs the field years of cleanup and it costs you your credibility. The machine makes this danger sharper: an AI can generate plausible, well-typeset, confident nonsense faster than any human, so our discipline must be correspondingly harder.

Concretely, the immune system of this project:

- **The wrong-approach detector discipline.** Three control objects stand in for the things a real proof must distinguish. $\mathbb{Q}^2$ has $\chi = 2$ (Woodall): any *combinatorial* method that would also give $\chi(\mathbb{Q}^2) \geq 3$ is wrong. The $L^\infty$ plane has $\chi = 4$ (Chilakamarri): any *geometric* method that works without the Euclidean-specific rigidity (equilateral triangles, regular pentagons, cocircularity) is wrong. $\mathbb{R}^1$ has $\chi = 2$: any *measure-theoretic* argument blind to the $O(2)$ rotation group is wrong. Before believing any lower bound, ask: would it fire on $\mathbb{Q}^2$, the $L^\infty$ plane, or $\mathbb{R}^1$? If yes, discard it. This single reflex has killed more bad ideas here than any other.
- **The adversary always runs.** Every construction is stress-tested for the smallest case where it breaks. A result is not a result until it has survived an honest attempt to refute it. (The L53 reduction was recorded only after an independent adversary caught two outright errors in the draft and they were fixed.) We spawn the skeptic on purpose.
- **Formalize what can be formalized.** Lean does not care how elegant a proof feels. The machine-checked $\chi \geq 5$ bridge theorem is worth more than a paragraph of confidence. The discipline of "could this be checked by a kernel that has no taste and no hope" is the discipline of truth.
- **Name the irreducible step.** If a framework "works," locate exactly where the hard part went. If realizability is still the hardest step after all the machinery, the framework has not yet earned anything; it has relabeled the difficulty. Do not let the hard step hide inside the word "realizable."

Honesty is not what slows us down. It is the thing that makes the increments real, so they compound instead of evaporating.

## 5. Reformulation is progress only when it imports power

It is easy to move "$\chi(\mathbb{R}^2) \geq 6$" from one phrasing to another and feel that something happened. Usually nothing did. The test is sharp: **does the new form give new tools, or only new words?**

Moving "$\chi \geq 6$" to "is an abstract clamp unit-distance realizable?" is progress, because it connects the problem to a large, active machine (combinatorial rigidity: the rigidity matroid, Cayley-Menger determinants, global rigidity) and gives a non-circular geometric source for the obstruction (L53). Moving the measurable bound to the Delsarte / Bochner LP and the DeCorte-Oliveira-Vallentin / de Laat-Vallentin SDP is progress, because it imports real harmonic analysis on $\mathbb{R}^2$. By contrast, moving "$\chi \geq 6$" to "find a chi-5 graph with a non-adjacent forced-different pair" and stopping there was only words until L51-L53 made it a geometric, rigidity-theoretic question. "A detector fires" with no machine behind it is the old difficulty wearing a hat. Apply the test every time. A reformulation that connects is a bridge; one that relabels is a mirror.

## 6. Build the ladder; do not jump

We do not attempt the answer in one motion. We build a milestone ladder of reachable, verifiable rungs, and we climb it.

- Reproduce the known finite case exactly before reaching past it. (We did: SAT-verify de Grey's $\chi \geq 5$, and reproduce Ambrus's $\chi_m \geq 5$ with our own dual certificate, before any attempt at 6.)
- Construct the abstract object before claiming the realized one. (L51 built the abstract clamp and SAT-verified it before L52-L53 asked whether it embeds.)
- State the precise conjecture, with its kill conditions, before trying to prove it. (The sharpened target: does a $K_4$-free 6-critical graph have a degree-5 vertex whose deletion leaves a unit-distance-realizable graph flexing to put a 3-subset of the neighborhood at circumradius 1?)
- Check the three detectors ($\mathbb{Q}^2$, $L^\infty$, $\mathbb{R}^1$) on every candidate, the way one checks units.

Each rung is small enough to check and real enough to keep. The ladder is not a detour from the answer; over a hard problem, the ladder *is* the method. The summit is reached, if it is reached, by someone standing on a rung we built.

## 7. Taste: choosing where to dig

Effort is finite and not all directions are equal. We triage by structural promise (does it engage the exact Euclidean rigidity the W3 finding demands, or is it blind to the norm?), by connection to existing machinery (a direction wired into a live field, rigidity theory, harmonic analysis, SAT, has leverage), by falsifiability (can we kill it cheaply if it is wrong?), and by non-circularity (does the bound come from genuine geometry, or are we secretly assuming the thing we want to prove?).

And we are willing to abandon. A direction that has earned its rejection should be rejected, loudly, with the coordinate recorded. The creative-attack sweep killed a dozen directions on purpose, each with its failure mode named. Sunk cost is not a reason to keep digging a dry hole. The willingness to walk away from a beautiful idea that does not work is itself a research skill, and it is the orchestrator's job to enforce it.

## 8. The AI-augmented research group

This project is run as a group with roles, surveyor, builder, verifier, adversary, synthesizer, orchestrator, played by AI agents under human direction. That is a genuinely new way to do mathematics, and it has its own philosophy:

- **Parallelism with adversarial verification.** Many attempts in parallel, each checked by an independent skeptic and, where possible, by a formal proof assistant. Breadth is cheap; the discipline is in the verification. A builder's reduction is not banked until an adversary has tried to break it and a calibration has confirmed the negative is real, not solver fatigue.
- **The machine must be more honest than a human, not less.** Speed and fluency are exactly what make unchecked AI output dangerous. Every claim carries its kill conditions and its stress test. We would rather report a clean negative than a dirty positive.
- **The human holds taste, judgment, and the decision to push.** The agents generate, survey, verify, and synthesize; the human chooses the front and owns the irreversible acts. Mathematics is done by minds; the tools are tools.

## 9. The long game, and why it is worth it

We may not settle it. Most of the people who advanced this front did not, and they did real mathematics anyway. The partial results, a structural explanation of why the lineage caps at $\chi = 5$, a sharpened wall, a new reduction that relocates $\chi \geq 6$ onto a rigidity question, a Lean-verified $\chi \geq 5$, are contributions in their own right, and any one of them can outlive the project that produced it.

But we work as if it can be moved, because that is the only stance from which progress is possible, and because the gap is genuinely open: the answer is 5, 6, or 7, and nobody knows which. If $\chi(\mathbb{R}^2) \geq 6$, a finite unit-distance witness exists, and it has a specific shape: it engages the exact Euclidean rigidity (it passes $\mathbb{Q}^2$, $L^\infty$, and $\mathbb{R}^1$), it realizes a clamp the known lineage cannot, and it cannot be built in the rational plane or under the $L^\infty$ norm. We have located that shape with unusual precision. That is not nothing. That is a front, pushed forward.

The work is real whether or not it ends in the answer. Done with honesty, taste, and persistence, it is mathematics at the frontier, which is one of the better things a mind can do. That is reason enough to come back tomorrow and pull the next brick.

---

*Operating corollaries, for quick reference:*
- *Frame every negative result as a coordinate. Never as "stuck."*
- *Before believing a lower bound, ask whether it fires on $\mathbb{Q}^2$, the $L^\infty$ plane, or $\mathbb{R}^1$.*
- *Distinguish a reformulation that imports power from one that relabels difficulty.*
- *Name the irreducible hard step; do not let it hide inside machinery.*
- *Build verifiable rungs; do not jump to the summit.*
- *Abandon dry holes loudly, and record the coordinate.*
- *Be more honest than feels necessary. Especially when the result is exciting.*
