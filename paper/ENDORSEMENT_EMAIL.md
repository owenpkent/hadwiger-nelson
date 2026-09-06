# arXiv endorsement request: draft

**To:** Maciej Zworski (zworski@math.berkeley.edu)
**Re:** C1, `paper/forcing-sterility.tex` -- "Forcing-sterility of the realizable unit-distance
lineage and a codegree obstruction to $\chi \ge 6$"

## Mechanics, so the ask is concrete

Checked against arXiv's current policy (Sept 2026), which changed twice recently.

- **Math is still a single endorsement domain.** All math subject classes in the
  section share one domain, so an established math.AP / math.SP author is
  eligible to endorse for **math.CO**, C1's primary category (math.MG as
  cross-list). Only math-ph is carved out, following physics rules. The topical
  distance from microlocal analysis does not matter.
- **The endorser must have arXiv submissions in the domain from between three
  months and five years ago.** Zworski clears this by a wide margin. This rule
  is what disqualifies most otherwise-willing senior people, so check it before
  asking anyone.
- **An institutional email no longer earns automatic endorsement.** Since
  2026-01-21 arXiv requires an institutional address *and* prior authorship on
  an arXiv math paper. A first submission with neither needs a person.
- An endorser certifies two things only: that they know the submitter
  personally **or** have seen the intended submission, and that the paper is
  topically appropriate. They are explicitly **not** certifying correctness.
  Worth saying in the email, because senior people sometimes assume otherwise
  and decline out of caution.
- **Flow, checked against arXiv's help page.** arXiv does *not* contact the
  endorser. You register an account, start a submission and select math.CO,
  and arXiv emails **you** an endorsement request containing a link and a
  six-character code. You forward that to him yourself. He goes to
  arxiv.org/auth/endorse, enters the code, and says yes or no. You never enter
  his address anywhere in arXiv.
- arXiv explicitly invites you to include "a link to your ORCID profile, other
  scholarly profile, or a copy of your intended submission" when you contact an
  endorser. That is arXiv endorsing the offer-the-PDF approach below.

Since Owen knows him personally, the first ground is already satisfied.

## Draft

> Subject: arXiv endorsement for a combinatorics note (math.CO)
>
> Dear Maciej,
>
> You may not remember me, but I was an undergraduate in your seminar at
> Berkeley in 2012. I have kept up with mathematics since, and I am writing
> with a small administrative favor rather than a mathematical one.
>
> I have written a short note on the Hadwiger-Nelson problem (the chromatic
> number of the plane) and would like to post it to arXiv. I am working
> independently, without an institutional affiliation, so a first submission to
> math.CO needs a personal endorsement, and I am hoping you would be willing.
> Mathematics is a single endorsement domain on arXiv, so your math.AP and
> math.SP submissions qualify you to endorse for math.CO even though the subject
> is far from your own.
>
> To be clear about what that involves: an endorser is only confirming that they
> know the submitter or have seen the paper, and that it is topically
> appropriate for the category. It is explicitly not a statement that the
> results are correct, and it is not a referee report.
>
> The note is a negative, explanatory result and claims no new bound. Since 2018
> the lower bound $\chi(\mathbb{R}^2) \ge 5$ has rested on explicit finite
> unit-distance graphs, and a natural route to 6 would find, somewhere in that
> family, a non-adjacent pair forced to differ in every proper 5-colouring. The
> note shows that route is closed, and why: those graphs are produced by
> SAT-driven minimisation, which drives them to vertex-criticality, and a
> vertex-critical graph cannot host such a pair. An exhaustive computation over
> all 1,955,948 non-adjacent pairs in the nine published graphs of that lineage
> confirms it. The note
> then reframes where the missing object can live, via a codegree bound every
> planar unit-distance graph must satisfy, and shows by computer search that the
> resulting class contains no 6-chromatic member on at most 17 vertices.
>
> It is about 14 pages. I am happy to send the PDF first if you would rather see
> it before deciding, which is probably the more natural order.
>
> If you are willing, I will file the request and send you the link and
> six-character code arXiv gives me. You would enter the code at
> arxiv.org/auth/endorse, and the form takes a minute.
>
> Thank you either way, and no obligation at all.
>
> Best,
> Owen Kent

## Notes before sending

- **No blanks left.** Address confirmed, year filled (2012). If the seminar had
  a memorable topic, one clause naming it is worth more than any credential in
  the rest of the email.
- Offer the PDF *before* the code. Reads better, and "have seen the intended
  submission" is the other valid ground, so it strengthens the request.
- The paragraph describing the result is deliberately non-technical and states
  the negative honestly. Do not upgrade it: the note's value is that it closes a
  route cleanly, and overselling would invite exactly the correctness scrutiny
  that endorsement explicitly is not.
- C3 (the solver note) needs no second endorsement once math.CO is endorsed,
  unless it goes to cs.DM, which is a separate domain.

## On William Briggs (UC Denver) as an alternative

Willing is not the same as qualified, and here he is not. Briggs is Professor
Emeritus at CU Denver in applied math (multigrid, DFT, wavelets), best known for
the calculus textbooks. The endorser rule requires arXiv submissions in the math
domain from between three months and five years ago.

Checked the arXiv API for `au:"Briggs_W"` (2026-09-05): four hits, all
astro-ph, all John W. Briggs on SDSS papers, none later than 2012. No math
submissions by William L. Briggs at all. Author-name search is fuzzy, so this is
strong evidence rather than proof, but combined with emeritus status treat him
as **ineligible** unless he says otherwise.

So: a warm second contact, not an endorser. Better spent on a read or an
introduction than on the form.

Other matched fallbacks, all active in math.CO / math.MG and cited by C1: Parts,
Exoo, Ismailescu, Voronov, de Grey. Heule on the SAT side, though that is cs.DM.

## On owenkent@ocf.berkeley.edu

Legitimate to hold: OCF accounts are not deactivated at graduation, so an alum
keeping the address is using it as intended. But it does not do the job you are
hoping it does.

- **It will not get you auto-endorsed.** That door closed on 2026-01-21. arXiv
  now wants an institutional address *and* prior arXiv math authorship, and the
  second is the binding constraint. A student-organization subdomain is also
  unlikely to be on arXiv's institutional list in the first place.
- **Registering the arXiv account with it is harmless** and may marginally
  expedite handling, which is arXiv's own word for it. No reason not to.
- **Do not pair it with a Berkeley affiliation line.** An OCF address next to
  "University of California, Berkeley" reads as a claim of current affiliation.
  Both papers currently say "Independent researcher," which is accurate and is
  also exactly what the endorsement request says. Keep them consistent.

Recommendation: keep `\author{Owen P. Kent\thanks{Independent researcher.}}` in
both papers and pick the correspondence address on durability alone. Gmail is
already in both files and will outlive an OCF account; the OCF address looks
marginally more academic. Either is fine, but change both papers or neither.
