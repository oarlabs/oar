# KNOWN ISSUES — measured, not hidden

This register records what the kit's adoption tests found. **Every one of them
was performed by a large language model running a written persona, not by a
person.** No human has walked `QUICKSTART.md` end to end and reported findings.
Each persona was given a charter, no prior contact with the kit, and a scratch
repository, and it wrote down what happened. That is the kit's own escape-rate
loop turned on itself, and it has found something **in all fourteen walks** —
though the hands-on walks in 13 and 14 were clean; their findings were in the
documentation meta-layer, and the loop closed there by the owner's materiality
ruling (see walk 14).

The prompts behind the seven adoption walks and the three evaluation reads are
published under `docs/walks/`, with the commit each ran against, what is
retained and what is not, and one paragraph on what a reader can and cannot
verify from them. **Entries 1–7 predate that loop and have no prompt
published** — `docs/walks/README.md` states its own coverage in its first
table, and this sentence is scoped to it. *[Corrected in round 30 (R30-2): it
read "the prompts behind every walk", which was false of entries 1–7. Same
class as round 29's F2, and the fifth instance of the class. Nothing
mechanical found it: this register is exempt from both of `count_lint`'s
layers as a document class, and the exemption's residual is exactly this.]*

Entry 15 is not a walk. It is an adversarial review of the kit's own
streamlining report, and it found three measured hazards that every walk before
it had passed over.

**Rows are never deleted.** A fixed item is marked in place with what it used to
do, because that is the only honest way to calibrate how much to trust the
current claims.

**The escape table comes first, from round 30 on.** This document is large, and
three independent readers in a row reported grepping it rather than reading it
— each of them looking for the same table, which used to sit several hundred
lines down. It is now the first section. Everything after it is the record the
number is computed from.

---

## The kit's own numbers — computed, not narrated

The kit's headline claim is that the loop publishes its own escape rate and
that trust is therefore measured rather than asserted. Until 2026-08-21 that
claim had no instrument behind it: nothing in the kit computed the number, for
an adopter or for the kit itself, and `RATIO_CEILING` shipped as the literal
string `derive-from-your-own-data` in the kit's own config. Both are fixed
here, and the escape rate is now computed **by a tool that runs inside
certification**, not by a sentence in this document.

### The escape rate

**An escape is an item a human reported that an existing check should have
caught.** A defect on a surface no check covered is a coverage gap, not an
escape; the honest response to a coverage gap is a new check, not a worse
number.

That is the definition an adopter uses, and it says *human* because in an
adopting project the reporter is one. **In the kit's own table below the
reporter was almost never a human.** Rounds 8–14 were reported by LLM personas
walking the documents, round 17 by LLM personas reading them, and the rest by
the maintainer or by a review lane. The number the kit publishes for itself is
therefore a self-administered measurement, and it is labelled as one here rather
than in a footnote nobody reaches.

The table below is **machine-read** by `modules/04-ledgers/escape_rate.py`.
Its first three columns are fixed. `-` in both count cells declares a round
uncountable and excludes it from the denominator — and the tool prints how
many rounds that hid, on every run, so that dropping a round is a visible act
rather than a quiet one.

<!-- ESCAPE-RATE TABLE. Columns Round | Items | Escapes are read by
     modules/04-ledgers/escape_rate.py. Notes is for the reader. Append one
     row per entry in the timeline below, in the same commit as the entry. -->

| Round | Items | Escapes | Notes |
|---|---|---|---|
| 1–6 | - | - | **Uncountable, declared.** The timeline aggregates these six pre-ship walks into one cell ("the eight instances tabulated below, plus items 1–11 in Confirmed fixed"), and the two lists overlap — instances 1, 3 and 4 are also Confirmed-fixed items 1, 3 and 9. No per-round item count is recoverable from the record, so none is invented. **The exclusion is not direction-neutral, and the direction flatters the published number.** Five of the eight instances the timeline names for these walks are instances of the promoted silent-green class — a check that was green over the defect — which is an escape by the definition above. Whatever the true denominator was, the escape share of these rounds was almost certainly *higher* than 21.7%, so including them would raise the headline rather than lower it. Inventing a denominator would be worse than excluding one, so the exclusion stands; what it costs the reader is stated here rather than left to be discovered. |
| 7 | 7 | 3 | Release audit. Items = the timeline's authoritative "3 MAJOR + 4 NIT". Escapes: SB-A (`--armed` proved a settings file *named* the hook, not that the script existed — green over a harness that could not start), SB-B (`STATUSLINE_CMD`'s quotes broke the settings JSON, silently disarming every hook, while the smoke substituted without parsing), SB-C (the UNSET family did not cover placeholder-shaped values, so a rule that forbade nothing read as configured). **Disclosed ambiguity:** the walk-7 sections also present SB-A/B/C under their own headings; if those are three items *beyond* the seven, this round is 3/10 = 30.0% rather than 42.9%. The timeline row is authoritative and the worse of the two readings is published. |
| 8 | 13 | 2 | W8-1 (`{{PROSE_VOICE}}` shipped raw because smoke phase 10 silently skipped 10 of 23 slot-using files while reporting a green count) and W8-3, which this register itself names as an escape: "that is why W8-3 escaped" — the walk staged with `git add -A` and reached `VERIFY: PASS` where a literal reader did not. |
| 9 | 7 | 1 | K-1: Step 9's `--tracked-only` scan ran over a tree whose last commit was Step 4's, so the scan that certifies nothing personal is about to be published never saw the profile. Smoke phase 9 walked that step and passed. |
| 10 | 10 | 3 | Items = S3-F1…F9 plus the end-state item S3-E3; 2 of the 10 were rejected with reason and are still items. Escapes: S3-F1 (a regression introduced by walk 9's own fix, which phase 9 walked past), S3-F2 (Step 6's checkpoint measured the hook, so an entirely unrendered `CLAUDE.md` passed every check in the document), S3-F8 (a gate with no oracle certified green). |
| 11 | 18 | 2 | F-1 (a literal walk *ends* at `VERIFY: FAIL`, measured, while the smoke ended green — the third consecutive errata pass to break the same printed commit line) and F-2 (the document routed an absolute path into the committed config, manufacturing the second-tracked-file hit Step 9 exists to catch). The other 16 are documentation and unlabelled-provenance findings with no check behind them. |
| 12 | 6 | 1 | W12-2: Step 8 was the one template step whose committed artifact no checkpoint reached, while every sibling step had one — the same silently-narrowed-coverage shape as W8-2. **Disputable:** read as a coverage gap rather than an escape, this round is 0/6. |
| 13 | 6 | 0 | All six in the meta layer (register bookkeeping, cross-module attribution). No check existed for any of them. M08-1's first fix attempt tripped the smoke's manifest detector — a check working, which is not an escape. |
| 14 | 8 | 0 | All eight documentation and module-README cross-descriptions; two rejected below the materiality bar. No check covered module READMEs describing each other's contracts. |
| 15 | 4 | 2 | SR2-1 (a `JUDGE_PATHS` entry hidden by the adopting repo's `.gitignore` read permanently clean, giving a full `VERIFY: PASS` over a settings file anyone could edit to disarm every hook — the `judges` gate existed and was green) and SR2-2 (both printed `git add` lines used directory pathspecs, which the kit's own enforcement layer read as compliant). Two further defects were found *inside this round's own fix* — a Windows carriage-return corruption in the probe, and a CI false-positive on the runner's `\runneradmin` home path — and are not counted as separate items because the timeline records four. |
| 16 | 19 | 3 | Items = R16-1 plus the 18 spec-side review findings on `kit_render.py`. Escapes: R16-1 (Step 8's own assertion stayed green over a profile that had silently lost its provenance block) and the two review majors this register records as "both reporting `PASS` at the time" — an output path that could escape the target repository, and a reordered-matcher comparison that appended a duplicate hook block. |
| 17 | 21 | 9 | Items = 4 ratified + 2 riders + 14 from the review of the fix + the post-review CI case-folding red. Escapes: R17-1 (eight measured functional equivalents of the blanket-add ban passed silently), R17-2 (a `//` in a string literal blanked an `agent(` call — a false allow reported as 0 vs 0), R17-R1 (the hook's interpreter was outside the startability check, so a disarmed enforcement layer certified), R17-R2 (the protected-path tripwire's silent-allow directions), R17-5 (the widened pattern scanned across newlines and false-denied five ordinary blocks, plus ten further real bypasses found after three persona reads), R17-6 (two residuals disclosed as fail-safe were measured as silent false allows), R17-7 (`kit_doctor.py` wrote `__pycache__` into the tree it diagnosed while its docstring said it wrote only to stdout), one of the nine smaller items (a reviewer's mutation walked past the doctor's hand-enumerated selftest list), and the CI case-folding assertion that hard-coded the Windows answer and false-failed on Linux. **This is the kit's worst measured round and it is published as such.** |
| 18 | 1 | 0 | R18-1: no shipped statement of the loop's stopping rules. Doctrine, not defect; nothing checked it and nothing could have. n = 1, which is noise — the denominator is printed for exactly this reason. |
| 19 | 30 | 3 | Items = the three funded builds' dispositioned review findings (10 + 10 + 10). The 14 findings REJECTED below the materiality bar are not counted: counting them would enlarge the denominator and flatter the rate, so the worse reading is published. Escapes: the Level-1 build's shipped-values gap (all six documents titled with the shipped example value certified HEALTHY while a rule the kit already owned should have caught them), and the instrument build's two (the gate ceiling was duplicated in two unlinked places and drifted silently — found by the review of the instrument built to prevent exactly this class; and a stale module-inventory row an existing doc check should have covered). The relabel build's three MAJORs (attribution-from-memory, including one invented quotation) had no covering check and are an oracle candidate, not escapes. |
| 20 | 7 | 0 | Items = the positioning-and-instrumentation round's dispositioned review findings (5 MINOR + 2 NIT); 7 below-bar REJECTs not counted, same worse-reading rule as round 19. Escapes: none — the reviewer's classification, passed through unaltered: both live-proven gaps (the unbound ceiling claim; the crashing selftest line) were in checks BUILT THIS ROUND, so no pre-existing check should have caught them; they are the new checks' own review findings, not escapes past the standing net. A zero round is published with its reasoning shown, per the register's own suspicion of unexplained zeros. |
| 21 | 22 | 4 | Items = the 16 brownfield-walk findings plus dogfood F1–F6 (the round's 5 review punch items on its own new work are not counted — see the timeline row; excluding them is the worse reading). Escapes, the reviewer's classification passed through unaltered: P3W-3 (smoke phase 12 proved the force-track remedy but never compared it to the remedy the runner printed), P3W-12 (a smoke check ran the documented shell block without inspecting what it wrote), F3 (`doctor:l1-rendered`'s own selftest was green over a false-positive class it never probed), F4 (`doctor:l1-interview` accepted any parseable future date). All four are one shape — **a check that exercises an artifact without asserting the artifact's own claim about itself** — recorded as this round's oracle candidate. The other 18 findings had no covering check at all. 18.2% is a rise from round 20's zero; the honest reading is a new instrument (the first brownfield walk) reaching surfaces the standing net was never pointed at, not a decaying net. |
| 22 | 11 | 1 | Items = the review's nine findings plus the fix pass's F11 and the ruled-in pre-existing P1; F10's below-bar REJECT uncounted (worse reading). Escape, the reviewer's classification: F5 — the example-entries removal instruction was incomplete and cited the wrong section, while an existing selftest section (I) bites on exactly that edit; a check existed, covered the surface, and the document contradicted it. Everything else: oracle candidates (F1's wrong-section citation and F11's dressed paraphrase had no covering check — the new `citation_lint.py` now covers the document-level half and states the section-level residual; P1's count drift had no cross-check and is now derived, not asserted). |
| 23 | 11 | 0 | Items = the adversarial review's dispositioned findings; 6 below-bar rejects uncounted (worse reading). Escapes: none — the reviewer's classification, passed through with its own caveat published: a zero on a prose-only round is arithmetically expected, because DEFAULTS.md is among the kit's most normative documents and not one line of it is mechanically checked. The two candidate oracles that would change that (an ordering lint; a closed-set routing lint) are recorded in Round #23 as shapes, not builds — if either is built and this page's class then produces findings, those will count against the round that declined the check, which is this one. |
| 24 | 6 | 1 | Items = the acceptance run's findings F1–F6; the review's 20 punch items on the round's OWN fixes are not counted (round-20/21 precedent — including them would enlarge the denominator and flatter the rate; excluding them is the worse reading). Escape, owner-ruled: F3 — `doctor:l1-*` existed, its stated subject covers exactly the claim it printed, and it greened while asserting ownership of a file the adoption never wrote; the third appearance of the exercises-without-asserting-its-own-claim shape. F1 had no covering check (count-drift, second sighting) and its oracle is now BUILT rather than declined; F2/F4/F5/F6 oracle candidates, five of the round's six declination bets filed against their classes per rule 7. |
| 25 | 1 | 0 | One owner-funded doctrine item; nothing checked doctrine completeness and nothing could have (the round-18 reading applies). n = 1 is noise. The round's one live event — the digest lint firing on rule 8's own growth — is the standing net working, not an escape. |
| 26 | 12 | 1 | Items = R26-1…R26-12, the battery's ruled findings; the review's own punch items on this round's fixes are uncounted (the worse reading — including them would lower the rate). Escape: R26-4 — the binding-digest's selftest label claimed arithmetic it never compared to anything while the check it labels was green; the claims-more-than-it-verifies class round 20 published, on the check built to prevent drift. R26-5's six stale locators are NOT counted as escapes: their class was ORACLE-DECLINED in round 24 and module 04's convention makes a declined-class finding a coverage gap attributed to the bet, not an escape — the first live firing of rule 7's accountability arithmetic. The remaining ten had no covering check (oracle candidates; three new ORACLE-DECLINED rows filed this round). |
| 27 | 2 | 1 | Items = R27-1 and R27-2, on the R26-12 precedent (a self-catch on the round's own new work counts as an item, no escape attributed); the alternative one-item reading is 1/1 = 100.0% and is stated here rather than hidden — either reading moves the cumulative rate to the same 16.7%. Escape: R27-1 — `citation_lint` existed from round 22, its stated subject covers exactly this class (a quoted string that does not appear verbatim in the document it names), and it was green over the defect for four rounds because its extractor's reach was narrower than its claim; not the round-20 shape, since the defect sat in shipped prose, not in a check built this round. The review's 7 punch items on the round's own build are uncounted per the standing rule. **This row is the denominator floor's live case:** 1/2 = 50.0% cannot pass a 35.0% ceiling at n = 2, so the round publishes `state SMALL-N` under the owner-ruled derived floor (see the Round #27 section) — the per-round gate is not armed, the cumulative number in this section still binds, and the six R26-5 locators remain attributed to round 24's bet, not recounted here. |
| 28 | 3 | 0 | Items = R28-1, R28-2 and R28-3. The alternative reading is stated rather than hidden: R28-3 is a self-catch on the round's own new document, and excluding it as own-new-work gives 2 items — which is under the denominator floor and would publish `state SMALL-N`. Both readings give 0.0%, because there are no escapes under either. **Escapes: none, and a zero on a prose round is published with its reasoning shown** (the round-20 and round-23 precedent). R28-1 is a provenance label on a figure: `count_lint` checks whether a stated number matches a target it can enumerate and has no opinion about whether the number is an estimate, so no check covered it and none could have as built. R28-2 is a contradiction between two shipped documents' instructions, which needs a reader of meaning; the kit's only cover for that class is the module file contract and spec-side review, both human-shaped. R28-3's surface is `checks-registry.json`, which neither lint reads — `count_lint` enumerates markdown documents only, and its own docstring already discloses that a count with no locatable target is skipped. All three are coverage gaps, and all three have an ORACLE-DECLINED bet filed against their class in the Round #28 section, so a second sighting of any of them counts against this round. |
| 29 | 4 | 0 | Items = R29-1 through R29-4 (the Round #29 section carries the findings, the alternative two-item reading stated completely, and the counter-argument to the zero-escape classification with its answer). R29-4 is a self-catch on the round's own new work. Two round-28 bets fired in this round's review and are recorded in the section with resolution owed at the owner's gate. A second consecutive zero-escape prose round: the cumulative figure falls 16.7 → 16.4 → 16.2 across rounds 27–29 by denominator growth alone — two prose rounds added seven clean items and built no new check. That is arithmetic, not learning, and the register says so here where the number is published. |
| 30 | 6 | 0 | Items = R30-1 through R30-6 (the Round #30 section carries them, the alternative five-item reading stated completely, and the counter-argument to the zero). R30-6 is a self-catch on the round's own new work, the R26-12 / R27-2 / R29-4 precedent. **Escapes: none, and this zero costs more to state than the last two.** The round BUILT the check for the class it had paid for four times, and then found a fifth instance of that class (R30-2) sitting on a surface the new check exempts by design - a findings register, exempt as a document class since round 24 with the residual disclosed on every run. That is not an escape by this register's definition, because no check covered the surface, and it is the least flattering true sentence available about the round. R30-3 and R30-4 were found by the round-30 recon reads — LLM personas this program ran with zero context, not people outside it — rather than by any check. Round 29's skim-test bet FIRED here on both of its triggers and is a coverage gap attributed to round 29 rather than an escape of this round (the R26-5 precedent). Two round-28 bets were resolved at the owner's gate; the resolution rows are in the section. |

**The published number, as the tool computes it:**

```
ESCAPE RATE UNCOUNTED: 1 round(s) declared uncountable and excluded from the denominator — 1–6
ESCAPE RATE TREND: 42.9 -> 15.4 -> 14.3 -> 30.0 -> 11.1 -> 16.7 -> 0.0 -> 0.0 -> 50.0 -> 15.8 -> 42.9 -> 0.0 -> 10.0 -> 0.0 -> 18.2 -> 9.1 -> 0.0 -> 16.7 -> 0.0 -> 8.3 -> 50.0 -> 0.0 -> 0.0 -> 0.0 (percent, oldest first); direction FLAT
ESCAPE RATE: 37/235 items (15.7%) over 24 rounds; latest 0/6 (0.0%); ceiling 35.0%; state MEASURED
```

Round 27's run of the same command printed a third line, `ESCAPE RATE
SMALL-N`, because that round had 2 items and the gate's denominator floor is 3.
Rounds 28, 29 and 30 are at or above that floor and the gate is armed again, so
the line is absent rather than green — which is the floor working as ruled, not
a check that stopped running. The trend direction reads FLAT at this run
because three consecutive zero rounds flatten the tail; the cumulative fall
across rounds 27–30 (16.7 → 15.7) is denominator growth from clean items, not
learning, and rounds 28 and 29 built no check at all. **Round 30 is the first
of the three that did**, which changes the argument for the next round's
number rather than for this one: a check built after the finding cannot
retroactively catch it, so its effect, if any, is only visible from round 31
onward. Read the fall as arithmetic until then.

The direction word swings on small tail denominators (rounds 18–20 are n = 1,
30 and 7): a single round moves it. Read the cumulative number and the spikes,
not the word; it is printed anyway because the tool does not editorialize.

**What the number says, including the part that is not flattering.** Roughly
one finding in five was something the kit's own checks should already have
caught. The trend does **not** fall monotonically: it spikes at rounds 15
(50.0%) and 17 (42.9%), and both spikes land exactly where the kit had just
built new machinery — the runner's exclusion probe and the hook's staging
rule. The honest reading is that this loop learns on the surfaces it has
already been burned on and escapes freshly on the ones it has just built. The
doctrine says a rate that does not fall means the loop is witnessing rather
than learning; on this record the rate falls on mature surfaces and resets on
new ones, which is a weaker claim than the doctrine's and is the one the data
supports.

**The ceiling, derived from this table.** The `--ceiling` literal in
`verify.py`'s `escapes` gate entry is **35.0**, by the same four-step method
`TOKEN-LEDGER.md` gives for the cost ratio. (It is an inline literal beside the
gate's other thresholds, not a named constant and not a config key, so that
moving it is a reviewed commit inside the judge surface.
`modules/04-ledgers/escape_rate.py`'s `DEFAULT_CEILING` is the second copy of
the same number, and `escape_rate.py --selftest` section F requires the two to
agree — before that binding existed, a drifted copy published a different
ceiling from the standalone command while the gate stayed green.)

Step 1 says take the *successful* rounds: rounds 7, 15 and 17 are the three
this register itself records as rounds where the kit was green and the green
was wrong, so they are not in the cluster. The remaining counted rounds peak at
**30.0%** (round 10). Step 2: 30.0 × 1.15 = 34.5, rounded to **35.0**.

Step 3, the backwards sanity check: **one half of it is evidence and the other
half is arithmetic, and both are stated.** A 35.0% ceiling fires on rounds 7,
15 and 17 and on nothing else. The "on nothing else" half is true *by
construction* — step 1 removed those three rounds from the cluster and step 2
set the ceiling above the retained maximum, so no retained round could possibly
fire. It carries no information. The half that does carry information is that
all three excluded rounds land clearly above the line rather than in the
30.0–34.5 gap, which is a real fact about where the threshold sits and a
weaker one than "fires on exactly the right rounds" sounds. Step 4: n = 12
counted rounds, one project, one maintainer's classification. Low confidence,
and an adopter should re-derive it from their own first rounds rather than
inherit this one.

**How the classification was made, and how to dispute it.** Every escape is
named by its id in the Notes column, and each was classified from this
register's own text — in most cases from a sentence that already says a check
was green over the defect. It is a maintainer's classification of a
maintainer's record, with the disputable calls disclosed in place (round 7's
item count, round 12's single escape, whether round 15's two in-fix defects
are separate items). Where a reading was genuinely ambiguous the **worse**
number was published. Anyone who disagrees with a row can change two integers
and re-run the tool.

**Known limits of this instrument.** It reads a table; it cannot audit the
table. A round that is never appended is invisible to it, and nothing in it
reads a clock, so a project that has stopped recording rounds looks the same
as a project between rounds. The ledger is deliberately **not** in
`JUDGE_PATHS` — it is the subject the gate measures, not a rule that decides
what green means, and putting it there would make every ordinary ledger append
invalidate certification — so an uncommitted edit to the table can move the
published number within a single run. The number is printed on every
certification, which is the compensating control and is not the same thing as
a proof.

### The ratio ceiling

`RATIO_CEILING` in the kit's own `kit.config` is now **0.40**, derived rather
than adopted, by the method `modules/04-ledgers/TOKEN-LEDGER.md` prescribes:

1. **Cluster maximum.** The kit's published process/implementation ratios are
   the reference build's four certified rounds, `BLUEPRINT.md` §11: 0.21–0.36.
   Cluster maximum **0.36**.
2. **Ten to fifteen percent above it.** 0.36 × 1.10 = 0.396; 0.36 × 1.15 =
   0.414. Rounded to **0.40**.
3. **Sanity-check backwards.** Half of this check passes and half is unproven,
   and both halves are stated. It fires on no round anyone was happy with — no
   round in 0.21–0.36 reaches it. It has never fired on a round independently
   judged an overrun, because **no measured round has ever exceeded it**, so
   the half of the test that would confirm the threshold sits in the right
   place has not been run.
4. **n and confidence.** n = 4 rounds, one reference build, one owner. A
   **low-confidence tripwire**, not a budget, and stated as one.

`kit.config.example` still ships `RATIO_CEILING = derive-from-your-own-data`,
and that is deliberate rather than an oversight: it is the one shipped value
QUICKSTART Step 7 tells an adopter to keep, because adopting somebody else's
cost ceiling is exactly what the method above says not to do. The key is not
deleted. What changed is that the kit now fills its own copy of it, with the
arithmetic above, instead of shipping itself the instruction.

---

## The entry timeline — authoritative

Every "walk N" in this document means a row in this table. Where an older
sentence used a different number, it is corrected in place with a bracketed
note; the table is what the numbers mean.

| Entry | What it was | Found | State |
|---|---|---|---|
| 1–6 | Pre-ship adoption tests: modules walked alone and in combination, one fix pass per walk | The eight instances tabulated below, plus items 1–11 in "Confirmed fixed" | fixed |
| 7 | **Release audit** — a read of the whole kit before shipping, not an adoption | Verdict **SHIP**, zero ship-blockers; 3 MAJOR + 4 NIT of day-one errata, including instances 6–8 of the class | fixed, except two NITs left OPEN by decision |
| 8 | **LLM-persona adoption walk #1** — Windows/pwsh, literal obedience, no coach | 13 (2 major, 8 minor, 3 nit) | all 13 fixed |
| 9 | **LLM-persona adoption walk #2** — Linux/bash conventions on a Windows host | 7 (1 major, 3 minor, 3 nit): K-1…K-7 | all 7 fixed |
| 10 | **LLM-persona adoption walk #3** — the impatient skimmer: headings, code blocks and checkpoints only | 9 findings + 1 end-state item: S3-F1…F9, S3-E3 | 9 fixed, 2 rejected with reason |
| 11 | **LLM-persona adoption walk #4** — a team-lead evaluator who read doctrine first, then walked, then simulated a second machine | 18 (7 major, 7 minor, 4 nit): F-1…F-18 | all 18 dispositioned FIX; four are honest-labeling fixes with the design recorded open |
| 12 | **LLM-persona adoption walk #5** — the dry-test literalist: full re-walk after the walk 8–11 errata, end-state audit | 6 (1 major, 2 minor, 3 nit): W12-1…W12-6 | all 6 fixed |
| 13 | **LLM-persona adoption walk #6** — the thorough adopter: full walk + end-state audit + doctrine spot-checks. **The hands-on walk was clean** — every step, checkpoint and audit property passed | 6 (0 major, 3 minor, 3 nit): KI-1, KI-2, BP-1, CA-1, M08-1, QS-1 — all meta-layer (register bookkeeping, cross-module attribution, one prose-vs-checkpoint asymmetry) | all 6 fixed |
| 14 | **LLM-persona adoption walk #7** — the final cap walk: full walk + audit + doctrine and module-README spot-checks. **The hands-on walk was clean again** — the second consecutive clean walk | 8 (0 major, 4 minor, 4 nit): M03-1, M02-1, M01-1, M02-2, CA-2, KI-3, KI-4, QS7-1 | 6 fixed; KI-3 and KI-4 **rejected — below the owner's materiality bar** (register self-audit; ruling 2026-08-20) |
| 15 | **Streamlining review, pass 2** — not a walk: an adversarial read of the streamlining report the walk-14 close produced, and of the shipped files it described, against the owner's materiality bar | 3 measured hazards (SR2-1…SR2-3) — one silent-green defect in the runner, two documentation hazards that cost real work — plus the register entry this pass owed itself (SR2-4); the first version of the SR2-1 fix carried a Windows transport defect, caught by spec-side review before any commit (recorded in SR2-1's disposition); the first committed version of the phase-12 control then false-positived on hosted Windows CI (its raw backslash-r scan matched the runner's own `\runneradmin` home path), caught by CI on the first push and fixed the same day | all 4 fixed |

| 16 | **Second-authority round** — not a walk: `tools/kit_render.py`, the optional mechanical substitution path, was built, and a second rendering of the same templates was required to agree with the smoke's hand-built adopter model | 1 defect in a shipped check (R16-1), found by the new check on its first run. The tool itself was then reviewed spec-side before any commit: 5 major, 8 minor, 5 nit, every major live-proven — two of them defects inside the tool's own guards (an output path could escape the target repository; an equivalent-but-reordered matcher was duplicated and mislabelled), both reporting `PASS` at the time | R16-1 fixed; all 18 review items dispositioned and fixed or rejected with reason, none of them ever committed |
| 17 | **Adversarial persona round** — not a walk: three independent LLM-persona evaluation reads of the shipped kit (a controls graybeard, a team-lead evaluator, a skeptic), then a fourth read attacking those findings against the owner's materiality bar; then a spec-side review of the implementation before any of it was committed | 4 owner-ratified items (R17-1…R17-4) plus 2 riders (R17-R1, R17-R2), then **14 more from the review of the fix itself** (R17-5…R17-8 plus nine smaller): the hardening false-denied five ordinary two-line shell blocks, two disclosed residuals were labelled in the wrong direction, and the new doctor wrote `__pycache__` into the tree it diagnosed. Two of the four review blockers were the SAME silent-false-allow direction the fixes were meant to close | R17-1 **NARROWED, not closed** (durable index-based fix recorded, not built); R17-2, R17-4, R17-5's false-deny half, R17-6, R17-7, R17-8 fixed; R17-3 decided and labelled; both riders absorbed into `tools/kit_doctor.py`. Fixture count 17 → 40. After the fix passed all ten gates and both reviews, a doctor selftest assertion hard-coded the Windows case-folding answer for `path_inside` and false-failed on Linux CI — the fourth second-machine catch of the quest, and the first in the Windows-passes-Linux-fails direction; the assertion now derives the expected value from `os.path.normcase`, the same case-sensitivity class the doctor's own `protected-case` check probes | R17-3 decided and labelled; both riders absorbed; the CI case-folding assertion fixed on the first red. **Two attacks from this round were ruled separately and funded later, and both are now closed:** the skeptic's "no instrument for the headline metric" (see "The kit's own numbers" above, 2026-08-21) and the skeptic's first FATAL, that this register described its walks in language a reader takes to mean people while other documents recorded them as AI personas (see "The walk labels, corrected" below, 2026-08-21) |
| 18 | **Owner-question round** — not a walk: the owner asked whether a new adopter inherits the loop-termination discipline (what stops adversarial review iterating to stupidity or forever), and the answer was no — the ENGINE ships (dispositions, oracle manufacture, escape rate, demotion) but the STOPPING RULES were practice, not doctrine | 1 finding (R18-1): no shipped statement of the bounded loop shape, the verdict brake, diminishing-severity-or-redesign, the materiality bar as an adopter instruction, or discovery-loop caps | R18-1 fixed — "WHEN THE LOOP ENDS" in the module-01 standing rules, the verdict brake in the reviewer charter (FINDINGS = approved, only REJECT buys a round), REJECTED-below-the-bar as a first-class punch-list disposition |
| 19 | **Funded-builds round** — not a walk: the three builds funded out of rounds 15 and 17 (the Level-1 onboarding path; the escape-rate instrument whose table this register now carries; the walk-label relabel with `docs/walks/`), each run impl → spec-side review → single fix pass under the round-18 stopping rules | 30 dispositioned review findings across the three builds (10 + 10 + 10); a further 14 were REJECTED below the materiality bar with one-line reasons. Notable: the relabel build's three MAJORs shared one root cause — attribution written from memory rather than from the source, including one invented quotation — for which no covering check exists; recorded as an oracle candidate (verify a quoted string appears in its cited source), not an escape | All 30 fixed in single fix passes, none needing a second review round; the Level-1 shipped-values escape fixed by relocating the placeholder rule to a single authority and manufacturing its missing selftest oracle; the instrument's two escapes (a silently driftable ceiling; a stale module row) fixed with a bound cross-check and the row edit |
| 20 | **Positioning-and-instrumentation round** — not a walk: three small owner-funded items (the README "Beyond code" scope statement; the decision brief's tiering-economics paragraph; the optional module-05 escape-rate sparkline), one build, one spec-side review, one fix pass | 7 dispositioned review findings (5 MINOR, 2 NIT), zero MAJOR; a further 7 REJECTED below the bar with reasons. The two live-proven check gaps: a registry reason claiming a ceiling binding its check did not deliver (the reviewer's mutation passed 90/90), and a selftest line that crashed instead of failing — both the claims-more-than-it-verifies class | All 7 fixed in one pass; the ceiling binding was made real (the mutation now fails, naming its check) rather than re-worded; the statusline selftest grew 90 → 94; every prose citation in the new sections was cross-checked against this register and held |
| 21 | **Existing-project round** — the first measured brownfield adoption walk (closing the decision brief's never-measured caveat) plus its ruled fix round: an LLM-persona walker adopted the kit @ `990b950` into a prepared repository that really had a pytest suite, CI, populated docs, a `.claude/`-covering ignore file, a pre-existing `CLAUDE.md` and settings file, and uncommitted work; then a code lane and a doc lane fixed the ruled findings, one spec-side review ran with mutation tests on a tree copy, and one fix pass closed its punch list | 22 dispositioned items: the walk's 16 findings (6 MAJOR, 6 MINOR, 4 NIT — all six MAJORs one root cause, the empty-repository assumption) and the Level-1 dogfood's six (F1–F6). The review returned APPROVE-WITH-PUNCH-ITEMS: 1 MAJOR + 4 MINOR punch items on the round's own fixes (all five fixed in the fix pass; the MAJOR was the round's own "safer" commit line failing on the repository shape it was prescribed for), plus 3 findings REJECTED below the bar with reasons. The 5 punch items are review findings on work built this round and are not added to the item count — adding them would enlarge the denominator and lower the rate, so the worse reading is published | 20 FIXED (the existing-project branch through Steps 1/4/6/9; the render route made required over pre-existing files; the runner's printed remedy corrected; `gate_line.py` + captured pytest goldens; F1–F5 as mechanical checks; `EXISTING-PROJECT.md`; `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md`), 1 RECORD-OPEN (P3W-7, gate-schema exact-count expressiveness, fix shape stated), 1 scoped-honest (F6). Independent note: the walk report's claim that an ignored-path `git add` fails atomically was measured false by two later instruments; the shipping text states the true behaviour and discloses the correction |
| 22 | **Drop-and-go round (R6-A1)** — `ONBOARD.md`, the agent-facing entry document, built impl → spec-side review → single fix pass under the standing stopping rules | 11 dispositioned items: the review's F1–F9 (1 MAJOR-as-filed, 6 MINOR, 2 NIT), the fix pass's F11, and pre-existing P1 (kit_doctor count drift). One review finding (F10) REJECTED below the bar with its reason, uncounted per the worse-reading rule. **F1's MAJOR was an instrument false positive:** the "fabricated" quotation is real, split across a line wrap the review's line-oriented grep could not match; the surviving defect is a wrong-section citation, MINOR. The same blind-spot class (newlines inside quoted strings) appeared in the first build of this round's own new check and was forced red before handoff | All fixed except F10 (rejected, reason recorded); P1 fixed by derivation (`len()` of the check lists, so the counts cannot drift again); the round's manufactured oracle SHIPPED: `tools/citation_lint.py` (quoted-string-in-named-document, scope honestly bounded — document-level, not section-level, and it says so; 13 controls; seen red three times during its own build; caught F11, a paraphrase dressed as a quotation, on its first live run, plus its own author's two unregistered controls via the new `citation:` lint family) |
| 23 | **Calibration-defaults round (R6-A2)** — `modules/08-collaboration/DEFAULTS.md`: the de-identified default calibration (33 values, one measured program's shapes with the identity removed) plus the realignment ask (the seed interview as a walk down the defaults: KEEP / OVERRIDE / DELETE / NOT-REACHED), OPTIONAL beside the preserved blank-page doctrine route; built impl → adversarial review → single fix pass | 11 dispositioned review findings (2 MAJOR — both routing omissions: the solo-path anchoring gap and KEEP's missing landing site — 6 MINOR, 3 NIT); 6 REJECTED below the bar with reasons, uncounted per the worse-reading rule. **The review's lead attack, re-identification (shape fingerprints beyond the token scan's reach), returned NO LEAK** — every fingerprint cross-checked inside this repository's already-published surface. The round also landed two owner-funded statements: Prerequisites (git named at last — previously the deepest undisclosed dependency; no version floor invented, measured-on facts only) and "At scale, and where it breaks" (the per-seam scaling model with the three-point floor conceded, including that the graph-engine composition is architecturally clean and empirically untested) | All 11 fixed; M1 fixed structurally (the open-first ask precedes any sight of the defaults on every route into the page); 0.60 removed from the kit entirely rather than restated underived; the citation lint went red once mid-pass on its own author and was obeyed; two oracle candidates recorded as shapes, deliberately not built (ordering lint; closed-set routing lint) |
| 24 | **Acceptance-and-hardening round (R6-A3)** — the first drop-and-go executed through its own front door: an agent handed one sentence and `ONBOARD.md` adopted the healthcare example host at Level 1 in 11m 55s of tool-time (the run itself declined to state a speed claim), ended HEALTHY, protected the host's WIP byte-identical, and handed the owner a fourteen-item deferral punch list; then the ruled fix round, one spec-side review, and a second fix pass under the brake | The run's 6 findings F1–F6 (owner-gated dispositions: the count-drift class promoted to `tools/count_lint.py`; the Level-1 check's misattribution of a host's own CLAUDE.md — ruled ESCAPE; the classification binary's missing third case; a cross-document contradiction resolved by ONBOARD's own yield rule working on first contact; the fence/token-file empty intersection resolved as a documented default-closed capability grant). The review of the round's own fixes returned 10 MAJOR / 7 MINOR / 3 NIT (all fixed; 6 below-bar rejects) — **the MAJOR count spiked 2 → 10 and the scope reading is published rather than assumed: two builds plus doctrine plus six findings rode one lane; if a future round looks like this, that is the redesign signal, not a number to explain away** | All fixed; rule 7 (declined oracle = recorded bet) shipped in module 01 AND applied to this round's own twenty unbuilt candidates — six ORACLE-DECLINED rows filed, the first bets held under the rule by the round that authored it; the grant clause rebuilt on enumerated-purpose-per-path after the review showed the report path could be construed as a grant; the smoke caught the fix lane itself writing a literal slot mid-pass (recorded as the layer working) |
| 25 | **Self-coverage round** — owner-funded doctrine, one item, coordinator-direct (the round-18 shape): WHEN THE LOOP ENDS rule 8, distilled from round 24's nine self-catches — **ERRATA, round 26 (finding R26-2): that count is unsourced.** "nine self-catches" appears in this register only here, in this row asserting it; round 24's timeline row and its Round #24 section enumerate nothing of the kind, and a reader following the pointer found the claim restated rather than evidenced. Rule 8 now cites four self-catches that this register does carry, one per round across 22–25, each with its check named. The count above is left standing as what was written, marked; the row's original text continues — ("a new check's own claims are the first surface the next check must cover"; first red is a self-red; maximal irony is a detection signal; the cost is front-loaded and the payoff mechanical). Shipped lean at the owner's instruction — the rule carries its own compressed example and points at this register; no new sections anywhere | 1 item, owner-funded. The rule's own arrival tripped `doctor:binding-digest` — the self-coverage rule caught by the rulebook-size guard on the way in, exactly as its own text predicts — and the ceiling was re-derived 350 → 375 with the arithmetic shown (219 rendered + 90 = 309, x1.15 = 355.35, rounded up) | Shipped; the binding observed red before the constants moved; n = 1, which is noise — the denominator is printed for exactly this reason |
| 26 | **Battery round** — the program's first formal adversarial battery pointed three independent lanes at the kit and its own coordinator's claims (a prior-art hunt with live web citations; a hostile reader in three professional personas; a fresh evaluation read), then one implementation lane closed the ruled findings and one spec-side review confirmed under the brake | 12 findings R26-1…R26-12: the battery's ruled set (the fabricated-vs-real citation classes, the grant clause's second empty intersection generalized, rule 8's unverifiable citation made adopter-verifiable with the count corrected 9 → 4 and the old number errata'd rather than rewritten, six stale locators fixed, BLUEPRINT's zero-external-citations ancestry FAIL closed with §12 Lineage, the peer-naming and conduct-over-composition positioning, COMPARISON.md shipped with a where-competitors-are-better section). Review: APPROVE-WITH-PUNCH-ITEMS (1 MAJOR — the register's own draft double-counted a declined-class finding as an escape, forbidden by module 04's convention; 5 MINOR; 4 NIT; 4 below-bar rejects), all fixed coordinator-direct; review punch items on the round's own work are not counted as items per the standing worse-reading rule | All 12 dispositioned (11 FIXED; R26-5 additionally FIRES round 24's declined-oracle bet — six findings of the declined class; the build-or-re-decline decision is the owner's at the gate, with the review's measured counsel on record: bare-bounds v1 detects 0 of the 6 and would be a vacuous oracle; the line-window extension reaches 4 of 6). Severity fell across rounds (2 MAJOR → 1, unpublished-number class); no second round per the brake |
| 27 | **Fired-bet round** — rule 7's first resolution: round 24's declined stale-locator oracle, fired by round 26's six attributed findings, resolved at the owner's gate both ways — BUILT as `citation_lint`'s line-window check (tolerance 0, overlap; measured recall 3 of 6, counsel's predicted 4 corrected to the measured number) and RE-DECLINED in the bare-bounds form (0 of 6 on its own class, vacuous). B3-m4's recall control built FIRST (`RECALL_FLOOR`, red-provable), which is the only reason the third defect was reachable. One spec-side review (APPROVE-WITH-PUNCH-ITEMS, worst finding MINOR — down from round 26's MAJOR), one coordinator-direct fix pass. The round's escape row surfaced the per-round ceiling's missing minimum denominator; the owner ruled the derived floor + SMALL-N state (see the Round #27 section) | 2 counted items: R27-1 (**ESCAPE** — a miscased quotation `citation_lint` was green over for four rounds; the recall control caught it on arrival, correcting round 26's "no live defect" reading) and R27-2 (self-catch on the round's own new work, the R26-12 precedent). The review's 5 MINOR + 2 NIT punch items on the round's own build are uncounted per the standing worse-reading rule; 5 below-bar rejects with reasons | Both dispositioned: R27-1 FIXED at both layers (the quotation corrected to its source; the glue generalized with the lookahead, 40 → 44 attributions, none lost); R27-2 WAIVED with its reason rather than relabelled. Three new ORACLE-DECLINED bets filed under rule 7 |
| 28 | **Capsule-doctrine round** — not a walk: one build lane shipped `modules/08-collaboration/CAPSULE.md`, the sync-capsule doctrine, from three hostile lane reports run the day before (a prior-art battery, an ancestry hunt, and a corrected A/B protocol) plus a binding seven-item corrections file those lanes produced. The governance doctrine is published as IMPORTED, with an ancestry table and an ancestor named in the same paragraph as every doctrine claim; the honest-boundary section states the published null on the nearest artifact class as the prior. Prose-only: no new tooling, no new check, and no adoption step routes through the document | 3 counted items, all found by the build against the pre-existing tree or against its own addition: R28-1 (a shipped figure stated as measured when it is an internal estimate), R28-2 (a shipped instruction contradicting the doctrine this round shipped), R28-3 (a stated count inside `checks-registry.json` that the round's own new document made stale — self-catch, R27-2 precedent). **Zero escapes, with the reasoning published** per the register's own suspicion of unexplained zeros: no check in this kit reads any of the three surfaces | All 3 FIXED. Three new ORACLE-DECLINED bets filed under rule 7, one per item's class |
| 29 | **Front-door round** — driven by the program's first real-human evaluation read (a VM/SecOps engineer who read COMPARISON.md and asked for manual validation of its claims, and skimmed long-form prose to a headache): COMPARISON.md gains a one-screen "Verify these rows yourself" preamble that names the self-attestation problem and hands over the per-row manual check; README gains a practitioner routing block (three artifacts, one line each) and the plain AI-authorship statement. Prose-only; the skim-test instrument deliberately not built | 4 counted items (R29-1/2/3/4, per the Round #29 section; R29-4 is a self-catch on the round's own new work), 0 escapes — coverage gaps, reasoning published per the zero-suspicion convention | Dispositions per the Round #29 section; three new ORACLE-DECLINED bets incl. the skim-test instrument with its trigger; two round-28 bets FIRED in this round's review, recorded, resolution owed at the owner's gate |
| 30 | **Transplant round** — not a walk and not a read: three cold LLM-persona evaluation reads of the published kit, each required to end in ADOPT / PILOT / PASS rather than in an opinion, plus **one executed increment on a project this program does not maintain** — a two-year-old internal AI advisory project whose owner authorised a Level-1 adoption and one improvement under the kit's discipline. The round then built the quantifier check the round-29 review recommended, rebuilt the front door around the increment's own output, and published the increment as `docs/CASE-STUDY-INCREMENT.md`. | 6 counted items (R30-1 through R30-6, per the Round #30 section), 0 escapes — reasoning published per the zero-suspicion convention, and this round's zero is the most expensive of the three to state. Three verdicts: PILOT, PILOT, PILOT; none ADOPT, none PASS. | R30-1 through R30-5 FIXED; R30-6 fixed pre-commit as a self-catch. `count_lint` gains a quantifier layer with fifteen registered controls, a forced-red and a true-universal control in CI, and a state word with a coverage denominator that retires `clean` over 1.9%. Round 29's skim-test bet FIRED on both of its triggers and is recorded with its resolution owed at the owner's gate; round 28's two bets were resolved RE-DECLINED at that gate, both with rule-7 resolution rows. |

Walks 1–7 were run against the kit as a whole by personas with some exposure to
it. Walks 8–14 are **LLM-persona adoption walks**: a language model given a
persona and no prior contact adopts the kit into an empty repository by obeying
the documents, executing every command in a real shell. Entries 15, 16 and 18
are neither — see their rows. Entry 17 is neither, and it is a different
instrument again: its three runs are **LLM-persona evaluation reads**, the same
kind of persona reading the shipped repository only, with no scratch project
and no `QUICKSTART.md` execution. The two instruments find different things —
a read can find a claim the material contradicts, and cannot find a command
that does not run as printed — so this register does not merge their counts.
`docs/walks/` publishes the prompt behind every run of both kinds. Entry 29
is a third kind and the register's first: a **human read** — a practising
engineer outside the program, reading the published material self-directed.
It has no prompt to publish, which is what makes it independent and also
what makes it unreproducible; its findings are counted like any other
round's, and the round's section states the instrument's limits. Entry 30 is
a fourth kind: an **executed increment on a host outside this program**,
alongside three evaluation reads of the ordinary kind. An increment can find
what neither a walk nor a read can — whether the documents survive contact
with a repository they were not written for — and it cannot find what a walk
finds, because it followed one path on one host rather than every step on a
clean one. `docs/CASE-STUDY-INCREMENT.md` is its public account and states
those limits again where a reader meets them.

---

## The pattern — **PROMOTED: prose design-question → mechanical lint**

Walks 1–7 found **eight** instances of one class, and after the fourth it was
clear they were one defect wearing different hats:

| # | Instance | Walk |
|---|---|---|
| 1 | the `judges` gate read only git's stdout, so "no repository" read as clean | 1 |
| 2 | the runner resolved its root from its own file location, so it judged the wrong tree and pronounced it fine | 2 |
| 3 | `--selftest` named the example gates the documentation tells you to delete | 3 |
| 4 | `kit.config` was outside the judge surface, so the config parameterising the judges could change without invalidating them | 4 |
| 5 | fixture `j` built its payload from the very key it was guarding | 4 |
| 6 | the armed check trusted the settings file to prove the settings file | 5 → **7** |
| 7 | `NONE` read as a value, so a placeholder configured a rule that guarded nothing | 5 → **7** |
| 8 | `STATUSLINE_CMD` broke the JSON it was substituted into, silently disarming the hooks | 6 → **7** |

*[Corrected 2026-08-20: the last three rows carried **fix-pass** numbers (5, 5,
6) in a column headed "Walk". All three were found by **walk 7**, the release
audit — the section below says so and always did. Instances 1–5 are walk
numbers and are unchanged.]*

**THE CLASS:** *a check whose expectation comes from the same artifact it is
asserting about cannot see a change to that artifact.* Fixture and defect move
together; the check stays green and its greenness means nothing.

### Why it is now a lint and not a ninth paragraph

The kit's own operating architecture carries a standing rule: **when a prose
rule fails, promote it a layer or accept it with the residual named.** That
rule had fired eight times against one class while the class itself was
documented only as a "design question asked of every new check" — which is
exactly the prose-only enforcement the doctrine says to distrust. Fix pass 5
made the class *legible*. This pass makes it **mechanical**:

- **`checks-registry.json`** — every check declares its **subject** and the
  artifact its **expectation** is read from.
- **`tools/expectation_lint.py`** — fails when those are the same artifact and
  no waiver explains why, and fails a waiver that carries no reason, because a
  waiver without a reason is the silent case wearing a label.
- **Negative controls in its own selftest** — instances 5 and 6 reconstructed
  as registry entries and shown red un-waived. A lint that has never flagged
  the thing it exists for is not evidence.
- **Run in three places:** `--selftest` in Step 0, the real registry in
  adoption-smoke phases 11 and 11b, and both on Linux and Windows in CI.

**Six waivers survive**, printed on every run with their reasons: four
config-driven fixtures (structurally covered by `kit.config` being in
`JUDGE_PATHS`), the armed check (only half-closable — no second source exists
for a harness's intent, but *startability* is now read from the filesystem),
and the registry checking itself. That is the honest residue of the class: not
zero, but named, visible, and each with what covers the gap instead.

**Inline literal expectations are out of scope** and marked `inline`. A
hand-written literal is the specification; it does not move when the code does.

---

## Confirmed fixed — walks 1–4, verified by later walks

| # | What it used to do | What closed it |
|---|---|---|
| 1 | **Non-git silent false green** — `git status` outside a work tree exits 128 with empty stdout, and empty porcelain is how "clean" is spelled. | `git_answer()` turns any non-zero rc into a porcelain line; the startup assertion refuses to run a git-judged gate outside a work tree. |
| 2 | **Module 03 could not run standalone**; the in-file comment said "keep them". | Module README **Step 0**, the comment reversed, and why `--skip hooks` is worse. |
| 3 | **`--selftest` broke on the README's own adaptation step.** | Section F resolves a live gate name at runtime; the smoke deletes both example gates. |
| 4 | **Module 05's holes** — module-02-dependent wiring, no defaults, a silently vanishing banner. | Inlined JSON for both boards, defaults for all seven keys, a loud amber segment, the gitignore coupling documented both ways. |
| 5 | **QUICKSTART Steps 1 and 6 were mutually exclusive.** | The third state `n/a` (off on purpose ≠ a gap); the kit's own tripwire is off. |
| 6 | **The startup assertion rejected flag VALUES as paths** — `-ExecutionPolicy Bypass` aborted the runner. | `looks_like_a_path()`, with the Bypass invocation as a named selftest case. |
| 7 | **The smoke under-tested its own label**; `--plant-f1` printed FAIL and exited 0. | Both gates deleted plus a `--list` assertion; `INSTRUMENTED` and exit 2. |
| 8 | **The shell note was backwards.** | Rewritten, and now machine-checked — see SB-3 below. |
| 9 | **`kit.config` was not in the judge surface** — an uncommitted rule-weakening edit certified clean. | The config is in `JUDGE_PATHS` in all three shipped examples; smoke phase 8 asserts it live. |
| 10 | **Steps 4 and 5 could not complete in document order.** | Settings substitution moved into Step 4; smoke phase 9 walks the document. |
| 11 | **Step 1 put an absolute `PROJECT_ROOT` in the committed config.** | Out of the fill list; `PROTECTED_PATH` too; `PROTECTED_PATH_ENABLED` stays. |

---

## Fixed in fix pass 5 — walk 7 (release audit)

*[Corrected 2026-08-20: this heading read "the sixth walk (release audit)" while
the section below it, and the section after it, both number the release audit as
walk 7. Walk 7 is correct; the "sixth" was a fix-pass number. "This pass" meant
fix pass 5, which is now named.]*

The release auditor confirmed every prior fix held: module 03 standalone was a
clean PASS, the impostor matchers were dead in four directions, and the no-git
abort behaved. It then found three more instances of the class, numbered 6–8
above.

**SB-A — `--armed` proved a settings file *named* the hook, not that the named
file *exists*.** A settings entry pointing at a moved, renamed or never-copied
script reported `armed:` for every tool and exited 0, while the harness would
fail to start the hook on every single call. The script a matched command names
is now resolved against the **filesystem** — an artifact independent of the
settings file — and a missing one reports **`UNSTARTABLE:`**, which is also a
veto token in the verify runner's `hooks` gate. QUICKSTART's over-claim ("proves
the harness actually calls it") is now the true sentence: *wired at every
enforcement point to a script that exists*, with what it still cannot tell you
stated beside it.

**SB-B — `STATUSLINE_CMD` was an absolute-path key in the committed half, and
its value contained double quotes.** Substituted into `"command": "…"` that
yields a settings file that does not parse — and unparseable settings mean **no
hooks either**, so a cosmetic slip silently disarmed the whole enforcement
layer. The key moved to `kit.config.local` alongside `PROJECT_ROOT` and
`PROTECTED_PATH`; the quote rule is stated at all three sites; the adoption
smoke now **parses** the substituted settings and refuses a double quote in the
command; and Step 9's enumeration is a table that is true on every branch (four
hits on the recommended one), asserted by phase 9 on that branch.

**SB-C — the UNSET family did not cover placeholder-shaped values.** The kit
ships fourteen of them, and every one is an ordinary non-empty string:
`FORBIDDEN_SPAWN_TIER = your-top-tier-model` reads as a configured rule that
forbids a tier nobody will ever request. Enforcement-shaped, enforcing nothing.
One shared `is_placeholder()` now covers `your-*`, `/abs/path/*`, `<paste…>`,
`derive-from-*`, `example.invalid` and the NONE family, in **all three** config
readers. Consequences flow through machinery that already existed: unset tiers
render `<KEY unset in kit.config>`, an unset `FORBIDDEN_SPAWN_TIER` or
`MODEL_EXEMPT_TYPES` raises a `CONFIG WARNING` that `--strict` fails on, and
phase 9 asserts a rendered governance file carries no surviving example value.

**Mechanical items.** The `--runner` / `--plant-f1` coupling disclosure
corrected — both are coupled to the *example gates*, so they work on an
unadapted runner and abort loudly on an **adopted** one ("if adopted", not "if
refactored"); adopted-runner support is deliberately not built. Two stale
fixture-count citations refreshed. The last unlabelled cross-module line in
`CLAUDE.md.template` labelled, so the "labels every cross-module line" claim
is true. Module 03 gained the same working-order adoption recipe module 02 has,
including the `git init` line and why it is load-bearing. And the smaller ones:
an "above" that pointed below, the Step-0 command count, the abort message
naming `HOOK_*` constants only when the `hooks` gate is actually selected, and
the size figure here.

---

## Release walk (#7): **SHIP** — with day-one errata

> **Verdict: SHIP. Zero ship-blockers.** The seventh walk was a release audit
> rather than an adoption test, and it is the first walk that did not find a
> silent green.

It did find three MAJORs and four NITs, all of them day-one errata. Dispositions:

| # | Finding | Disposition |
|---|---|---|
| MAJOR-1 | QUICKSTART Step 1's fill list omitted `FORBIDDEN_SPAWN_TIER`, so obeying the document produced one `SKIP` and made Step 6's `0 skipped` checkpoint unreachable. | **ROOT-CAUSE FIXED.** The key is in the fill list, in both QUICKSTART and module 02's recipe, with the note that it looks like a duplicate of the orchestrator tier and is the one people skip. |
| MAJOR-2 | Module 02's recipe did not say to fill the tier keys, so its own proof command could not go green by obedience. | **ROOT-CAUSE FIXED** by the same edit. Proof re-run against a config filled per the new list: `HOOK FIXTURES: 15/15 passed, 0 skipped, 2 n/a`, exit 0. *[Corrected 2026-08-21: that count is the one measured on 2026-08-20. Twenty-one fixtures for the measured blanket-staging bypasses, the false-deny class the widening created, and the string-literal defects landed in round #17, and the same command now ends `38/38 passed, 0 skipped, 2 n/a`. The `0 skipped` and the exit code are what this row was proving; the same correction is on the identical line in `README.md`.]* |
| MAJOR-3 | Step 4's copy list omitted the status board while Step 4's `STATUSLINE_CMD` step pointed at it. | **COPY STEP FIXED** (`cp …/tools/statusline.py tools/` on the recommended branch). The underlying gap is **recorded, not fixed** — see the row below. |
| NIT-7 | An `armed:` line and an `UNSTARTABLE:` line can both appear for the same tool, which reads as a contradiction. | **OPEN.** Both are true — the matcher covers the tool, the script is missing — and the run is red either way. Merging them is a presentation change to a line that is currently correct. |
| NIT-8 | The non-git abort ends with the generic `Fix: set JUDGE_PATHS / CERT_PATHS…` line, which is not the fix for that particular problem. | **OPEN.** The specific remedy (`git init`, or `--skip judges`) is in the sentence directly above it; the generic tail is redundant rather than wrong. |
| NIT-9 | `kit-ci.yml` carried the expectation-lint step twice. | **FIXED** — it was a deletion. Eleven steps, no duplicate names. |
| NIT-10 | QUICKSTART's Step 0 command count. | **FIXED** — eight commands, counted. *[Corrected 2026-08-20: the count in this disposition went stale. Step 0 has since grown to **nine** commands, and its checkpoint says nine. The block and its checkpoint agree; only this row's number was wrong.]* |

### Recorded, not fixed: statusLine startability

**SB-A's startability check covers hook commands only.** For each PreToolUse
block naming the hook, the script is resolved against the filesystem and a
missing one reports `UNSTARTABLE:`. The **`statusLine`** command gets no such
check, so a mis-pathed board fails silently: no banner, no error, and a status
line that renders nothing looks exactly like a session with nothing to report.

Why it is recorded rather than closed: the failure is **observability, not
enforcement**. A dead hook means rules stop binding; a dead board means you
stop seeing. Both deserve to be loud, but only one of them can let something
through — and this pass was chartered as errata, not features.

**Fix shape, when someone wants it:** extend `check_armed`'s existing
`hook_script_from_command` + `resolve_hook_script` pair over
`settings["statusLine"]["command"]` and emit the same `UNSTARTABLE:` token.
Perhaps twenty lines, including the fixture. The verify runner's `hooks` gate
already vetoes on that token, so nothing downstream changes.

---

## Walk #8 — LLM-persona adoption walk, Windows/pwsh, literal obedience

The eighth walk was the first post-ship adoption test: a persona adopted the
kit into an empty repo by obeying the documents literally, in pwsh, with no
coach. The walk completed — all nine QUICKSTART steps, `VERIFY: PASS` at the
end. It found 13 defects. Every executable did what its documentation said; 12
findings are documentation defects and one is a check-coverage defect.

The check-coverage defect is this walk's instance of the class: **phase 10
reported "all 13 template SLOTS manifests match their bodies" while its
detector silently skipped 10 of the 23 slot-using files** — a green count with
no coverage claim behind it. One skipped file, the governance template, really
did carry a defect (`{{PROSE_VOICE}}` missing from its inventory), and the
skipped check is why it shipped.

All 13 were fixed in one errata pass, same day:

| # | Finding | Disposition |
|---|---|---|
| W8-1 | `CLAUDE.md.template`'s SLOTS inventory omitted `{{PROSE_VOICE}}`; obeying Step 6 shipped a raw slot. | **FIXED** — inventory now lists all 18 slots. |
| W8-2 | The smoke's manifest detector required "slots" and a token on one line; multi-line inventories went unchecked, silently. | **FIXED** — multi-line detection; the headline now states coverage (14 of 23 checked, 9 carry no manifest). |
| W8-3 | Step 4's printed commit line did not stage the gate payload, so the `VERIFY: PASS` checkpoint failed as printed. | **FIXED** — line stages `tests`; checkpoint conditioned. |
| W8-4 | The shell section over-claimed `mkdir -p` portability; in pwsh an existing directory is an error, not a no-op. | **FIXED** — claim corrected, `-Force` form given. |
| W8-5 | The "following week" `--runner` command ran from neither directory and aborts on an adopted runner. | **FIXED** — replaced with what an adopter should run; the limit stated where printed. |
| W8-6 | Step 8 named `PROFILE-TEMPLATE.md` with no copy command or destination. | **FIXED** — explicit command and destination rules. |
| W8-7 | `kit.config.example` promised templates "degrade to repo-only" at `KNOWLEDGE_DIR = NONE`; no template has a NONE branch. | **FIXED** — promise replaced with the substitution instruction, noted at both interpolation sites. |
| W8-8 | Step 9 predicted exactly four deident hits; the count is path-shape arithmetic (a real walk measured 8). | **FIXED** — count made illustrative; the second-tracked-file diagnostic promoted. |
| W8-9 | Ledger seed lesson 8 shipped the narrow blanket-add rule the governance template calls wrong. | **FIXED** — reworded to the blanket rule. |
| W8-10 | Step 7 never said to substitute the ledgers' slots or delete their SKELETON blocks. | **FIXED** — instruction and checkpoint added. |
| W8-11 | `CONTEXT-ARCHITECTURE.md` was in no reading order. | **FIXED** — evaluator route added to README. |
| W8-12 | `kit.config`'s `JUDGE_PATHS`/`CERT_PATHS` vs the `verify.py` constants: nothing reconciles them and module 03's README stated the reverse relationship. Measured: no tool reads the config's `JUDGE_PATHS`; the hook's cert-green tripwire reads its `CERT_PATHS`. | **FIXED** (docs) — the constants are authoritative; the docs now say so and tell the adopter to reconcile by hand. |
| W8-13 | No step told a bare-`git init` adopter to create a source or test tree. | **FIXED** — Step 3 note. |

### Closed on the tenth walk: the document-order walk staged with `git add -A`

`document_order()` in `tools/adoption_smoke.py` used to stage its scaffold with
`git add -A` instead of the QUICKSTART's printed targeted-add line. That is why
W8-3 escaped: the walk reached `VERIFY: PASS` while a literal reader did not,
because the walk staged everything and the reader staged what the document
printed. It was also the one place the kit's own tooling used the blanket add
its governance template forbids.

**Now fixed.** The walk stages the document's named paths, dropping only the one
path its scaffold genuinely does not have — which is the substitution the
document now tells the reader to make inside the code block, because `git add`
is atomic and one bad pathspec stages nothing at all. The walk also creates
Step 3's `docs/ORACLE-<gate>.md` and asserts the commit carries it, so a gate
adopted without an oracle no longer certifies green.

---

## Walk #9 — LLM-persona adoption walk, Linux/bash conventions

The ninth walk adopted the kit with bash habits on a Windows host. It completed
all nine steps and found 7 defects, all documentation. Its major is the walk's
instance of the class: **Step 9's scan ran `--tracked-only` over a tree whose
last commit was Step 4's**, so the scan that certifies nothing personal is about
to be published never saw the rules file, the ledgers, or
`docs/collaboration-profile.md` — the one file the walk fills with a person's
verbatim words. A green scan over a tree that does not contain the profile looks
exactly like a green scan over one that does.

All 7 were fixed in one errata pass:

| # | Finding | Disposition |
|---|---|---|
| K-1 | Step 9 scanned `--tracked-only` with Steps 6–8 uncommitted, so the profile and the ledgers were unscanned and the scan could not say so. | **FIXED** — Step 9 opens with the named-path commit; the step tells the reader to read the printed `scope:` line; smoke phase 9 now walks the commit, asserts the scope widens to the whole tracked tree, and asserts the remediation reaches zero. |
| K-2 | Step 1 said only `JUDGE_PATHS` and `CERT_PATHS` come back later. `KNOWLEDGE_DIR` and `RATIO_CEILING` come back too, at Steps 6 and 7, unannounced. | **FIXED** — Step 1 names all four keys and the step each returns at. |
| K-3 | Step 3's checkpoint asked for "one filled worksheet page" and no step said where it goes or what to call it; the only hint was a parenthetical two steps later. | **FIXED** — Step 3 names `docs/ORACLE-<gate-name>.md` explicitly and says Step 4's commit line stages `docs`. *(This fix introduced walk 10's S3-F1: Step 4's commit line then named a `docs` a skimmer did not have.)* |
| K-4 | `{{PROJECT_ROOT}}` is a mandatory slot in three hook commands while the config registry ships the key of the same name empty on purpose — the slot and the key look like one thing. | **FIXED** — Step 1 separates the runtime *key* from the substituted *slot*, states that nothing fills the slot from the key, and names the `UNSTARTABLE:` an empty slot produces. |
| K-5 | Step 7's checkpoint ("no `{{` surviving") is satisfied by substituting `RATIO_CEILING`'s shipped `derive-from-your-own-data`, which the kit's own readers treat as UNSET. | **FIXED** — Step 7 names that one placeholder as a deliberate, allowed survivor, with when to replace it, and separates config *values* from template *slots*. |
| K-6 | Step 4 told the adopter to delete an `examples/` directory its own copy list never brings into the repo. | **FIXED** — the instruction states that the directory stays behind in the kit and there is nothing to delete. |
| K-7 | The NIT-10 disposition above said "eight commands, counted"; Step 0 had grown to nine. | **FIXED** — corrected in place with a bracketed update on the row itself. |

---

## Walk #10 — LLM-persona adoption walk, the impatient skimmer

The tenth walk read headings, code blocks, tables and checkpoints, and paid for
prose only when something failed. It reached the kit's full done state —
`VERIFY: PASS`, clean tree, `DEIDENT SCAN: 0 hits` — and the end-state audit
then found three defects **no checkpoint had caught**: no oracle worksheet
existed at all (Step 3 has no command block, so this persona skips it with
certainty), `CLAUDE.md` would have shipped as an unrendered template carrying 45
raw slots (Step 6's checkpoint measured the *hook*, not the rules file), and
`kit.config` and `CLAUDE.md` disagreed about `KNOWLEDGE_DIR` from day one.

**The structural finding** is worth more than any single row: *load-bearing
instructions were living in prose while the adjacent checkpoint measured
something else.* The errata pass applied one pattern throughout — move the
instruction into the checkpoint, with a runnable line in both shells.

| # | Finding | Disposition |
|---|---|---|
| S3-F1 | Step 4's printed commit line named `docs`, which a skimmer who skipped Step 3 did not have; `git add` is atomic, so nothing staged and nothing committed. **A regression introduced by walk 9's K-3 fix.** | **FIXED** — an in-block comment tells the reader to drop paths they do not have and states that one bad pathspec stages nothing at all. Counted as rework. |
| S3-F2 | Step 6's checkpoint measured the hook only, so an entirely unrendered `CLAUDE.md` passed every check in the document. | **FIXED** — the checkpoint is two bullets, the second inspecting `CLAUDE.md` itself, with a runnable line in both shells and in the smoke. |
| S3-F3 | Step 7 claimed "Step 6's own check on the rendered rules fails on any of them" — no such check existed. | **FIXED** — the false sentence is deleted and replaced by "No shipped tool checks your tree for them", which names what phase 9 does and does not cover. |
| S3-F4 | The de-identification token file's format was never stated, and a wrong-shaped file still parses and reports `0 hits`. | **FIXED** — format given in the block; the failure mode stated in the paragraph beside it. |
| S3-F5 | Step 1 had no checkpoint, so its mandatory fills lived only in prose and `PROJECT_NAME` was caught nowhere in the document. | **FIXED** — Step 1 ends in two runnable lines per shell; the smoke asserts the same thing over the config it writes. |
| S3-F6 | A commit that did not run leaves the *identical* `VERIFY: FAIL … RED: judges` line as the pre-commit run, and nothing said so. | **FIXED** — the checkpoint bullet names the ambiguity and what to check. |
| S3-F7 | Step 4's runnable block depended on edits made in prose above it, unmarked. | **FIXED** (marker half) — an in-block comment names the prerequisite. Restructuring Step 4 was out of scope. |
| S3-F8 | Nothing between Step 4 and Step 9 mentioned the worksheet again, so a gate with no oracle certified green. | **FIXED** (artifact half) — Step 4's checkpoint names `docs/ORACLE-<gate-name>.md` and gives the command to read the commit. |
| S3-E3 | `kit.config` and `CLAUDE.md` could state different answers for `KNOWLEDGE_DIR` with no check reading either. | **FIXED** — Step 6 gained "Set the key as well as the slot"; the smoke asserts the two agree. *(Walk 11's F-2 later corrected which half the key goes in.)* |
| — | **REJECTED (2):** S3-F9, that the placeholder paths in examples should be real; and S3-F8's second half, that "an afternoon of thinking" for Step 3 should be compressible. | **REJECTED with reason** — placeholder-shaped values are read as UNSET by design, which is the safer failure; and the oracle step does not compress, which is the point of the step. |

---

## Walk #11 — LLM-persona adoption walk, the team-lead evaluator

The eleventh walk was the first to read **doctrine before commands**: README →
BLUEPRINT → CONTEXT-ARCHITECTURE → KNOWN-ISSUES, then QUICKSTART hands-on, then
a second-machine simulation. It found **18** defects — the largest round — and
the reason is the route: claim-checking BLUEPRINT and CONTEXT-ARCHITECTURE
against the shipped files, auditing this document for self-consistency, and
running the kit as a *team* would are four surfaces the first three of these
walks never touched. Every executable behaved as documented, including the ones
designed to fail; all 18 findings are documentation defects.

The walk's recommendation was **adopt, partially and in a different order than
the kit proposes**: modules 04 and 08 immediately, module 03 and then module 02
after — not a rejection, and not the full adoption the document assumes.

Four of the majors are **architecture-level**: the honest fix is a true label
plus a recorded design, not a feature. Those four appear in the open list below.

| # | Finding | Disposition |
|---|---|---|
| F-1 | Step 6 requires editing `KNOWLEDGE_DIR` in `kit.config`; Step 9's printed commit line staged only `CLAUDE.md tools/deident_scan.py docs`, so a literal walk *ends* at `VERIFY: FAIL — RED: judges`, `M kit.config`. Measured. **Rework — introduced by the walk 9/10 errata chain.** | **FIXED** — Step 9's commit line names `kit.config` and says why; Step 9 now ends in a certification run. The smoke's walk sets the key at Step 6 (leaving the config dirty, as a reader does), stages it at Step 9, and asserts `VERIFY: PASS` at the end. |
| F-2 | Step 6's *first* branch told you to write an absolute knowledge-base path into the **committed** `kit.config` — manufacturing the "second tracked file" escape Step 9 defines. Measured: `HIT kit.config`. | **FIXED** — the absolute branch routes the key into `kit.config.local`; the rule is stated plainly (an absolute path never enters the committed half); Step 9's key list and second-file note both name `KNOWLEDGE_DIR`; `kit.config.example` and `kit.config.local.example` say which half takes which value. |
| F-3 | The committed `.claude/settings.json` is simultaneously per-machine, shared, and inside `JUDGE_PATHS`; the kit's own `.gitignore` names `.claude/settings.local.json` and no document mentions it. Measured on a second machine: `UNSTARTABLE:` × 3 and `RED: judges, hooks`. | **LABELLED, recorded not fixed** — Step 4 gains "One machine per settings file" with the measured consequence and no false remedy. The split is real design work and is **open** below. |
| F-4 | `CONTEXT-ARCHITECTURE.md` §6 describes SessionStart, PreCompact and a handoff PreToolUse hook in shipping-grade detail; the kit ships none of the three and nothing said so. | **LABELLED** — §6 opens with a NOT SHIPPED banner in module 07's style; BLUEPRINT's diagram edges and its §7 closing paragraph carry the same flag; the two forward references in §2–3 say the hook does not exist. **Open** below. |
| F-5 | The rendered rules file's first binding line — "ON RESUME: read the newest checkpoint FIRST" — is unsatisfiable on day one: no checkpoint template ships, no step writes one, no check notices. | **LABELLED** — the template line now says you write the first one at your first stage close, and points at the four-clause shape contract in the paragraph below it; QUICKSTART Step 6 surfaces the same thing on the adopter's path. **Open** below. |
| F-6 | This document contradicted itself on its own walk count — "five walks", "six", "the sixth walk (release audit)", "Release walk (#7)", "eight walks in" — and walks 9 and 10 had no findings section. | **FIXED** — an authoritative walk timeline at the top; every contradicting number corrected in place with a bracketed note; findings sections added for walks 9, 10 and 11. |
| F-7 | README's "transfers to any stack, any model, any team": the team half had two adaptation notes behind it and single-seat assumptions throughout. | **FIXED (softened)** — the claim now reads "any stack and any model", with a paragraph naming what a team must decide and a pointer to the open row. |
| F-8 | QUICKSTART's "The order matters" asserted an order the nine steps do not have; two of its four clauses contradicted the steps they summarised. | **FIXED** — rewritten as "Why the nine steps are in this order" (an ordering by dependency), with the README's adoption levels named as the different thing they are (an ordering by commitment). |
| F-9 | Step 6 told you to amend a "mirror" sentence that does not exist in `CLAUDE.md.template`. | **FIXED** — the instruction now quotes the template's actual text, `(that copy is source of truth)`. |
| F-10 | Module 05 inlines `statusLine` JSON with escaped double quotes; the `STATUSLINE_CMD` substitution route bans them. Both correct, neither cross-referenced. | **FIXED** — a cross-reference at each site naming the other route, why the rule differs, and SB-B as the failure it prevents. |
| F-11 | BLUEPRINT said the seed interview takes "ten minutes" against "fifteen" at four other sites. | **FIXED** — fifteen. |
| F-12 | "Stage" is used in BLUEPRINT before its definition, and "phase" was never defined anywhere. | **FIXED** — module 04's vocabulary section now defines **phase** too, with the "read phase as round" fallback; BLUEPRINT and CONTEXT-ARCHITECTURE point at it at first load-bearing use. |
| F-13 | "cert-green pre-authorization" was used in README's module table with no definition on the evaluator's route. | **FIXED** — a defining clause at first use. |
| F-14 | `kit.config.local.example` said "`.gitignore` already excludes `kit.config.local`", which is false at Step 1 copy time — the rule lands at Step 4. | **FIXED** — the sentence is conditional and true, and tells a standalone adopter to add the rule first. |
| F-15 | Module 02's "the hook reads eight keys" against a nine-key table and nine keys in the source. | **FIXED** — nine, with the row arithmetic stated. |
| F-16 | The repository-size figure was stale (`~525KB, 50 files` against 585,001 bytes / 51 files measured at `641b392`). | **FIXED** — re-measured on this pass's tree, dated, with the prior figures kept and a note that the number moves with every errata pass. |
| F-17 | Step 9's "check `tokens : N` is the number you meant" fires falsely: the scanner de-duplicates case-insensitively, so a name and its capitalised variant are two lines that report `tokens : 1`. Measured. | **FIXED** (document, not scanner) — the dedup is documented where `N` is read. |
| F-18 | Step 4's "(20 min)" understated a JSON substitution, four constants, a gate table, a selftest case and two config keys by 2–3× for a first-timer. | **FIXED** — 45–60 minutes first time, and the hour budget in QUICKSTART, README and BLUEPRINT reconciled to the new sum (90 minutes to two hours). |

---

## Walk #12 — LLM-persona adoption walk, the dry-test literalist

The twelfth walk was the first dry-test: a careful literalist re-walked the
full document after the walk 8–11 errata, verifying every checkpoint and
auditing the end state against the kit's stated intent. It reached the
documented done state, confirmed the prior fixes it crossed, verified the live
hook with its own configured tier values, and found **6** new defects — one
major, two minor, three nits — all in the same class the register keeps
recording: a committed artifact or a load-bearing rule that no checkpoint
reaches. The loop was therefore **not dry** at walk 12.

| # | Finding | Disposition |
|---|---|---|
| W12-1 | Step 1 ("illustrative defaults you may never need") and Step 7 ("every other shipped placeholder is a fill-in you missed") gave opposite rules for the nine placeholder values that legitimately survive in the committed `kit.config` at done. | **FIXED** — Step 7's rule is scoped to the `docs/*.md` ledgers its own scan covers; Step 1 gains the deciding rule (unadopted-module keys, local-half keys, `RATIO_CEILING`); the steps cross-reference. |
| W12-2 | Step 8 was the one template step whose committed artifact no checkpoint reached: the collaboration profile could ship with a raw `{{KNOWLEDGE_DIR}}` and its template header, and nothing noticed — despite Step 6 promising "Step 8 spells out what it means for that one file". | **FIXED** — Step 8 instructs the substitution and the header deletion, carries its own runnable checkpoint in both shells, and the smoke now renders and asserts the profile. |
| W12-3 | `tools/deident_scan.py` makes Step 9's publish-safety judgment but the document never put it in `JUDGE_PATHS` — the kit's own "the config that parameterises the judges is itself a judge" reasoning, not applied. | **FIXED** — Step 6 adds the scanner to `JUDGE_PATHS` in both `verify.py` and `kit.config` (with the reason it cannot happen at Step 4); Step 9 stages `tools/verify.py`; the smoke walks the whole ripple. |
| W12-4 | Step 1 listed `GATE_COMMAND` as fill work; its shipped value is already correct and the checkpoint regex omitted it. | **FIXED** — five keys to fill plus "confirm `GATE_COMMAND`"; the smoke asserts it non-empty. |
| W12-5 | `REPORTS_DIR = docs/reports` renders into two binding rules and no step created the directory. | **FIXED** — Step 7's line is `mkdir -p docs/reports`, with the empty-directory caveat stated and the pwsh note corrected to measured behaviour. |
| W12-6 | Step 8 described `CLAUDE.md` as naming `{{KNOWLEDGE_DIR}}/collaboration-profile.md`, a file state Step 6's own checkpoint forbids. | **FIXED** — reworded to the post-substitution state, and the adjacent branch sentences aligned to Step 6's real branches. |

The walk-12 errata pass also ran a full Steps 4→9 re-walk after its own edits —
the structural answer to the rework class walks 10 and 11 recorded (three
findings across them were introduced by this loop's own errata passes). The
re-walk caught three downstream inconsistencies of the pass's own edits before
they shipped.

---

## Walk #13 — LLM-persona adoption walk, the thorough adopter

The thirteenth walk combined the full hands-on walk, the end-state audit, and
doctrine spot-checks against the shipped files. **The walk itself was clean:**
all nine steps ran as printed in pwsh, every checkpoint matched observed
output, and the 12-property end-state audit found nothing broken that no
checkpoint caught. Its six findings — 0 major, 3 minor, 3 nit — were all in
the meta layer, and two were this register's own bookkeeping falling out of
date again one walk after F-6 fixed the class.

| # | Finding | Disposition |
|---|---|---|
| KI-1 | The "authoritative" walk timeline had no row for walk 12 while a Walk #12 section existed — the table violated its own rule that it is what the numbers mean. Introduced by the walk-12 errata's own register edit. | **FIXED** — row added; and the walk-13 close adds its own row in the same commit as its section, which is the structural rule going forward. |
| KI-2 | Three sentences still said "eleven walks" against twelve documented — a recurrence of F-6, recorded FIXED one walk earlier. | **FIXED** — counts corrected; the recurrence is the finding: a hand-maintained count in prose goes stale every time a walk lands, so the count now lives primarily in the table. |
| BP-1 | BLUEPRINT's module table gave module 08's contract surface as "none — pure text" against the module's own three-item file contract. | **FIXED** — the cell states the real surface. |
| CA-1 | CONTEXT-ARCHITECTURE attributed the collaboration profile to module 01; it ships in module 08. | **FIXED** — attribution corrected. |
| M08-1 | Module 08's README claimed `kit.config` supplies a token no shipped file in the module uses. | **FIXED** — the contract names the one real token. The first fix attempt tripped the smoke's manifest detector (the word "slot" beside a token reads as an inventory) — the guard caught its own author; reworded. |
| QS-1 | Step 6 edits the runner and no later step re-ran `--selftest`, against the document's own after-every-runner-change rule. | **FIXED** — Step 6 now prints the selftest re-run where the edit happens. |

---

## Walk #14 — LLM-persona adoption walk, the final cap walk

The fourteenth walk closed the adoption-walk loop at its seven-walk cap. **The
hands-on walk was clean for the second consecutive time**: all nine
steps as printed, every checkpoint matched, and a 14-property end-state audit
found nothing uncaught. All three deliberate reds produced their documented
verdict words. Eight findings, none major, all documentation.

The loop therefore ended **not-dry by its own rule** (two consecutive
zero-finding walks never occurred), and the structural finding is stated
here as the loop's outcome: *the adopter-facing walk converged to clean and
stayed clean; the kit's residual finding generator is its documentation
meta-layer — module READMEs cross-describing each other's contracts, and this
register describing itself.* The owner ruled (2026-08-20) that polishing that
tail past the point of adopter impact is negative-return; findings below that
materiality bar are now rejected, not fixed.

| # | Finding | Disposition |
|---|---|---|
| M03-1 | Module 03's "full veto list" named four tokens; the shipped gate vetoes on five (`UNSTARTABLE:` omitted). | **FIXED** — five named. |
| M02-1 | Module 02's README quoted the two-count required line the shipped pattern rejects, and named 3 of 5 veto tokens. | **FIXED** — three-count form and full veto list, matching module 03. |
| M01-1 | Module 01's contract with module 02 omitted `{{FORBIDDEN_SPAWN_TIER}}` — the key walk 7's MAJOR-1 called "the one people skip". | **FIXED** — four slots listed. |
| M02-2 | Module 02's standalone recipe never disposed of the `permissions.ask` block, landing `Edit(NONE/**)` rules the proof command cannot catch. Measured. | **FIXED** — the recipe says delete it unless enabling the tripwire, and why the proof stays green either way. |
| CA-2 | CONTEXT-ARCHITECTURE §5's diagram edges for the SessionStart and PreCompact hooks carried no NOT SHIPPED flag while BLUEPRINT's identical edges do. | **FIXED** — both edges flagged. |
| KI-3 | The walk-10 timeline row enumerates 9 items but disposes of 11. | **REJECTED** — register self-audit, below the materiality bar (owner ruling 2026-08-20). |
| KI-4 | A walk-13 self-description sentence is imprecise about which layer two findings were in. | **REJECTED** — same ruling. |
| QS7-1 | Step 7's pwsh note claimed the `mkdir` line is "silent the first time"; it prints a directory-listing table. | **FIXED** — the note describes the real output. |

---

## Review pass #15 — adversarial read of the streamlining report

The fifteenth entry is not a walk. The walk-14 close produced a streamlining
report; this pass read that report and the shipped files it described, looking
for hazards that survive a clean walk because a walk never puts the kit in the
state that triggers them. Three did. Each is a case where the kit is green and
the green is wrong, or where the printed instruction costs an adopter work that
is not theirs to lose.

The pattern across all three: a **persona walking the document in an empty
repository cannot meet any of them.** The empty repo has no pre-existing
`.gitignore`, no colleague's uncommitted work, and no second machine. The
onboarding loop converged to clean and then stopped finding these because the
walk itself is the wrong instrument for them.

| # | Finding | Disposition |
|---|---|---|
| SR2-1 | A `JUDGE_PATHS` entry covered by the adopting repo's pre-existing `.gitignore` is invisible to `git status --porcelain -- <path>`, which prints nothing and exits 0. The `judges` gate then read permanently clean over a file nobody was judging — a full `VERIFY: PASS` over a `.claude/settings.json` anyone could edit to disarm every hook. `.claude/` is a common entry in an existing ignore file, so this is reachable on a real adoption and not on the smoke's scratch repo. | **FIXED** — the startup assertion now asks `git check-ignore` about every `JUDGE_PATHS` and `CERT_PATHS` entry whenever a git-dependent gate is selected and the root is a work tree, and an excluded, untracked entry ends the run `VERIFY: ABORTED` (exit 2) naming the path. Git that cannot answer is also a refusal, not a pass. Registered as `check:judged-paths-not-excluded` with its expectation read from git. **The control is `adoption_smoke.py` phase 12**, which plants a real ignore rule over a real judge path in a real repository, in both rule shapes, and asserts that force-tracking the file clears the abort; the runner's selftest checks cover only how the assertion reacts to an injected answer. That division is itself a measured lesson: the first version of this fix corrupted every path it asked about — text-mode stdin appended a carriage return on Windows, so exact-path rules were missed and tracked files false-aborted — and all three gates were green over it, because nothing in the kit ran the shipped probe. QUICKSTART Step 4 names the failure mode beside the `.gitignore` housekeeping. |
| SR2-2 | The hook bans `git add -A`, `--all` and `.`, but both printed `git add` lines in QUICKSTART stage **directory** pathspecs (`tools`, `docs`, `src`). On a shared repo with other people's work in progress they sweep it into the adoption commit — through the kit's own enforcement layer, which reads them as compliant. | **FIXED** — both lines (Step 4 and Step 9) carry a warning at the point of use: these are directory pathspecs, run `git status` first, stash or exclude what is not the kit's. Docs only: a staging tool was considered and rejected in adversarial review. |
| SR2-3 | A hosted CI runner is a second machine, and `.claude/settings.json` carries the absolute paths of the machine that wrote it. On a runner every hook block reports `UNSTARTABLE:`, which vetoes the `hooks` gate, so CI is red on every push for a reason that is false about the project. Module 07's README said nothing about it. | **FIXED** — the "Adopt it" list now carries the reality and the documented remedy (`--skip hooks` in the CI invocation only, expected exit 3), with the cost stated in the same language modules 02 and 03 use: a permanently skipped gate certifies less. The local full run stays the certification bar. |
| SR2-4 | This register had no entry for the review pass or its findings, so the fixes would have shipped with the timeline still ending at walk 14. | **FIXED** — timeline row 15 and this section, written in the same work session as the fixes and committed with them. |

---

## Round #16 — the second authority, and what it found on its first run

The sixteenth entry is not a walk either. The kit gained an **optional**
mechanical substitution path, `tools/kit_render.py`, offered beside the by-hand
route QUICKSTART keeps as primary. The condition of building it was that the
smoke's hand-built adopter model stay exactly where it was, and that a new
phase render the same templates a second way and require the two to agree.

The phase disagreed on its first run, and the hand model was the side that was
wrong.

| # | Finding | Disposition |
|---|---|---|
| R16-1 | `adoption_smoke.py`'s Step 8 rendering deleted the collaboration profile's YAML front matter — `title`, `type`, `status`, `created`, `last_revised`, `sources` — because it stripped the template's guidance header by taking everything after the first `-->`. `PROFILE-TEMPLATE.md` is the only template in the kit whose header is not the first thing in the file; nine lines of front matter sit above it, and Step 8 instructs the adopter to delete the *comment*, not everything above it. **No checkpoint in the document could see the loss.** The front matter carries neither a `{{SLOT}}` nor a header marker word, so Step 8's own `grep` line (`\{\{\|Delete this comment on adoption\|TEMPLATE - the living`) stays green over a profile that has silently lost its provenance block. | **FIXED** — the hand model now excises the comment and keeps the text above it (`adoption_smoke.py`, Step 8 block), and Step 8's assertion gained the clause that would have caught it: the rendered profile must still start with its front matter. **The check that found it is `adoption_smoke.py` phase 13**, which renders the same templates a second way and diffs. The arbiter was neither authority: QUICKSTART Step 8 names what to delete, and it ruled for the tool. That ordering is now written into the phase's own failure hint, because "the check disagreed, so I edited the expectation until it agreed" is the shape a collapse of this guard would take. |

**Why this is the entry worth reading.** Every earlier entry in this register
was found by a person walking the document. This one was found by a *second
implementation of the same instruction*, and it was invisible to every human
check the kit ships — including the one written specifically to guard that
file. A defect that survives its own checkpoint is only reachable by an
independent expectation, which is the argument for keeping the hand model and
the tool apart, and for never resolving a disagreement between them by editing
whichever side is easier to change.

The tool was then reviewed spec-side against the punch list before any of it
was committed. Two of the five majors were defects inside the tool's own
headline guards: an output path constrained against the kit clone but not
against the target repository, so a `LEDGERS_DIR` of `../shared-docs` wrote
four files outside the adopter's repo and reported `PASS`; and a structural
merge that compared matcher strings as text, so `Write|Edit|NotebookEdit`
against `Edit|Write|NotebookEdit` appended a duplicate block — the gate then
firing twice — under a note saying the matcher "was NOT wired". Both are the
same shape as R16-1: a guard whose reach stops just short of the case that
reaches it, reporting green. Both are fixed, each with a negative control in
`kit_render.py --selftest` and an end-to-end control in phase 13.

---

## Round #17 — the adversarial personas, and the doctor

The seventeenth entry is not a walk either. Three independent **LLM-persona
evaluation reads** of the shipped kit — a controls graybeard, a team-lead
evaluator, and a skeptic — were run against `fcd64b1` *[this section first said
`2c18c53`; corrected 2026-08-21. All three prompts name `fcd64b1`, the reads
started at 22:13 on 2026-08-20, `fcd64b1` was committed at 22:11 that evening,
and `2c18c53` landed at 01:42 the next day.]*, and their findings were then
attacked in turn by a fourth read that conceded, rebutted or rescoped each one
against the owner's materiality bar. A read is not a walk: no scratch project
was created and no `QUICKSTART.md` command was executed. The three prompts are
published at `docs/walks/evaluation-reads.md`. The owner ratified four items.
This round implements them.

The pattern in the ratified four is worth naming, because it is not the pattern
of the earlier walks. **Nothing here is a silent green.** Every one is a
*disclosure* finding: a mechanism that behaves exactly as its source says it
behaves, described by a sentence somewhere else in the kit that says something
stronger. In a kit whose thesis is that confident sentences must not outrun
measurements, that is the finding.

| # | Finding | Disposition |
|---|---|---|
| R17-1 | **The blanket-add ban had eight measured functional equivalents that passed silently**, and the docstring called the rule "DENIED outright". Found independently by all three persona reads: `git add -Av`, `git -C <path> add -A`, `git stage -A`, `git add -u`, `git add :/`, `git add '*'`, `git commit -am`, and — the worst, because nobody types it to evade anything — **any indented occurrence**, since one leading space or tab defeated the `^` anchor. That is the normal shape of a command inside an `if` or a `for`. | **NARROWED, NOT CLOSED**, and the status word is deliberate: see R17-5, which is the second round on this same rule and found ten more. (a) The pattern covers command position with indentation, git's global options before the subcommand, the `stage` synonym, combined short-flag clusters containing `A` or `u`, `--all` / `--update`, `.`, `:/` and `*` quoted or bare, and `git commit` with an `a`-bearing flag cluster. **Eight deny fixtures** — `t`, `u`, `v`, `w`, `x`, `y`, `z`, `aa`, one per measured form — plus the control `ab`, proving the scan does not read flags out of a quoted commit message. Fixtures `r` and `s` belong to R17-2, not to this row. (b) The durable answer — judge the INDEX, not the string — is **RECORDED, NOT BUILT**, with the reason: a PreToolUse hook runs *before* the command, when `git diff --cached` still describes the world as it was, so the index judgement belongs in a git `pre-commit` hook at the moment the index is final. Until a project installs one, the compensating pair is the pattern plus the sweep list the gate prints when it denies, and `kit_doctor.py`'s dirty-paths check on demand. Neither stages anything. Both error directions are disclosed at `BLANKET_ADD`, beside point 1's, and **no completeness is claimed**. |
| R17-2 | **A `//` inside a string literal blanked the rest of its line**, taking any `agent(` call on that line with it — count 0 vs 0, which is silence. A URL is an ordinary thing to find in a workflow script, and the failure direction was a false ALLOW of an undeclared spawn. | **FIXED.** `strip_script_comments()` is now one scanner that recognises comments and string literals in source order, blanking comment text and string *contents* while preserving offsets. It has to be one pass: masking strings first would make `// don't` open a literal at the apostrophe and blank the rest of the file. Fixture `r` is the defect; fixture `s` is the control that the masking does not eat a `model:` sitting outside the string. **The first version of this fix shipped its two residuals in the WRONG DIRECTION** — the docstring called them "a loud, immediate, fixable deny" and both were measured as silent false allows, the same mechanism as the defect. Both are now closed (fixtures `ac`, `ad`) and the surviving residuals are stated as silent-allow: see R17-6. |
| R17-3 | **The cert-green token is an unsigned self-assertion.** No HMAC, no proof the runner ran; the file is gitignored and outside `JUDGE_PATHS`, so anything that can write a file can mint one. A security professional read it as a stronger attestation than it is. | **DECIDED AND LABELLED (owner-ratified 2026-08-20; the keying analysis accepted on review 2026-08-21), with the surviving half built.** The keying question was evaluated honestly and the answer is no: the agents this token governs run shell commands as the owner, with the owner's filesystem and environment, so there is nowhere to put a key they cannot read — not an environment variable, not a file outside the repository, not the settings file. A signature would raise forgery from "write a file" to "read a file, then write a file" while making the token read as an attestation it is not, which is a *worse* label, not a better control. So: the label ships, and it ships **inside the artifact** (a `label` field in the token itself), in `cert_green()`, in README's new Security scope section, and on every `kit_doctor.py` run. The half of the item that survives the keying decision is built: **`verify.py --mint-cert-token`** writes the token from the runner's single `PASS` return, carrying sha, timestamp and gate headlines, so the ordinary way to hold a token is to have certified rather than to have asserted. It is opt-in — a run that lifts a control should be asked for, not a side effect. |
| R17-4 | **The kit contained zero words of security scope**, repo-wide, while shipping controls that a public audience reads as security controls. | **FIXED** — README has a `Security scope` section: what the kit governs (correctness, cost, process integrity) and the four things it does not defend against (a malicious agent, prompt injection, credential exfiltration, supply chain), with the cert-green token and the hook's heuristics named specifically because both look stronger than they are. |

**Two same-class riders, absorbed into the doctor** rather than into the hook,
with the dispositions stated rather than implied. Both carry ids, because every
other finding in this register is citable by one and a JUDGMENT-LEDGER row has
to be able to name them:

- **R17-R1 — the hook's interpreter is outside the startability check.** The fixture
  harness proves a settings command names a script that *exists*; nothing
  proved the *interpreter* resolves. `PYTHON_BIN` ships as the bare word
  `python`, and the kit's own README documents the host where that breaks —
  stock Debian and Ubuntu ship `python3` with no shim. On that host every hook
  call produces no output, `--armed` still reports armed, and the run certifies
  a disarmed enforcement layer. **`doctor:hook-interpreter`** resolves the
  interpreter of every wired hook command against the filesystem and PATH.
  Scoped honestly: resolution is not execution, and an interpreter that starts
  and then crashes is the dead-man clause's job.
- **R17-R2 — the protected-path tripwire matches case-sensitively.** On Windows and on
  default macOS a differently-cased spelling of the protected path opens the
  same file and the tripwire says nothing; `cd` then a relative path, and
  symlinks or junctions, do the same. **The matching semantics were
  deliberately not changed** — folding case would be wrong on Linux, where the
  two spellings really are different files, and a gate that asks about a path
  the owner did not protect is the false positive that gets gates deleted.
  Instead point 4 joins point 1 on the disclosure list, in `touches_protected()`
  and in the module docstring, and **`doctor:protected-case`** *probes* the
  filesystem the tree is actually on — not `os.name`, because case-sensitive
  NTFS directories and case-sensitive APFS volumes both exist — and says what
  the mismatch costs there.

**And the tool the streamlining pass funded.** `tools/kit_doctor.py` is the
adopter-runnable "check my adoption" command: fifteen checks — ten in the full
diagnosis, and five more under `--level1` for a documents-only adoption —
`HEALTHY` / `ATTENTION`, exit 0 / 1 / 2. The verdict word is deliberately not `PASS` —
that word belongs to the runner that runs the gates, and this tool runs none.
It stages nothing (an earlier design offered to `git add` what its dirty-paths
check found, and that design was killed in review), and `--selftest` holds the
prohibition to the source: the git verbs it uses are recovered from this file's
own text and checked against a read-only allowlist.

Two things about it are worth reading:

- **Every one of its checks is registered** — all fifteen — and
  `expectation_lint.py` now
  cross-checks the `doctor:` family against `kit_doctor.py` in both directions,
  exactly as it does the fixture family. That generalisation is the point: ten
  unregistered checks in one commit would have grown this register's own named
  blind spot faster than the lint that discloses it.
- **Run against the kit's own checkout it reports `ATTENTION`, and that is the
  correct answer.** The kit ships two `example_*` gates QUICKSTART Step 3 tells
  you to replace, and no `docs/ORACLE-<gate>.md` pages, because the kit is not
  an adoption. A diagnosis tool that made an exception for its own repository
  would be the first thing an adopter learned to distrust. The residual is
  recorded in the Open list below.

### The spec-side review of that work, and what it found

None of it was committed before a reviewer took the punch list, the owner's
rulings and the diff — never the implementer's report — and re-measured the
result. Fourteen findings. All four of the round's judgment calls came back
sound; the defects were in the hardening.

**Two of the four blockers were the SAME error direction the fixes were meant
to close.** That is the finding worth keeping:

| # | Finding | Disposition |
|---|---|---|
| R17-5 | **The widened blanket-staging pattern scanned across newlines**, because its token separator was `\s`, which matches newline. The scan ran off the end of the git command and through every following line until it met a quote or a `;&|`, so any later `-A`, `-u`, `.`, `*` or `a`-bearing flag denied the whole block. Five ordinary two-line blocks measured denying, `git commit -F msg.txt` followed by `ls -la` among them. The fix for the bypasses built the dead alarm the same file's own comment warns against. **And ten further real bypasses** were found in one session after three persona reads had already been through the rule: `git add ./`, `git add "-A"`, `git add --al`, `env`/`sudo`/`time`/`VAR=` prefixes, `sh -c`, a backslash continuation, `$(…)`, backticks, and `git add ':(top)'`. | **FIXED** for the false-deny class — every separator inside a command is `[ \t]`, never `\s`, and fixtures `ae`, `af` hold the line. The measured cost is that a blanket flag reached only by a backslash continuation stops matching, and that form was already a false negative, so nothing was lost. **NARROWED** for the bypasses: `./`, quoted flags, long-option prefixes, the assignment and wrapper prefix family, `$( … )` and `:(top)` are closed with a fixture each (`ag`–`am`); `git add --dry-run` is now deliberately allowed, because it stages nothing and it is the command an operator reaches for after a deny (fixture `an`). Nested shells, backslash continuations, backticks, `xargs`, aliases, runtime-built commands and post-quote flags are **NOT closed and are named** where the rule is defined. Backticks are excluded on purpose: a backtick code span in a commit message is commoner than the legacy substitution form. **No completeness is claimed anywhere**, and the durable index-based fix stays recorded. |
| R17-6 | **The string-literal fix disclosed its two residuals in the wrong direction.** The docstring called a regex literal with escaped slashes and a JS private field "a loud, immediate, fixable deny"; both were measured as **silent false allows** — over-blanking removes the `agent(` call with everything else, the count falls to 0 vs 0, and the gate says nothing. Same mechanism and same direction as the defect the fix was written for. In a kit whose thesis is that confident sentences must be measured, a disclosure that says a residual fails safe when it fails open is worse than no disclosure. | **FIXED, both of them, rather than re-labelled.** The scanner now recognises a regex literal when a `/` appears where an expression may start (and leaves division alone after an identifier, digit, `)` or `]`), and treats `#` as an ordinary character when it touches a `.` or an identifier, so `this.#id` survives while `x = 1  # note` is still a comment. Fixtures `ac` and `ad`. What genuinely survives — a `#` that is neither a comment nor a private field, a `/` in expression position after an unrecognised keyword, an `agent(` inside a template-literal interpolation, and a non-spawn `model:` — is now stated **as silent false allow**, with the one false-deny direction marked as such. |
| R17-7 | **`kit_doctor.py` wrote into the tree it was diagnosing**, then reported its own residue back as the adopter's dirty tree. Importing the target's `verify.py` and `hook_model_gate.py` left `__pycache__/*.pyc` beside each, which the dirty-paths check duly listed. The module docstring said "the only writes this tool performs are to stdout". The rule was applied to the case probe — which flips an existing filename rather than creating one — and missed for the imports. | **FIXED** — `sys.dont_write_bytecode = True` ahead of every import, asserted in `--selftest` against the interpreter's own state rather than against the source text, and verified live: `git status --porcelain -uall` on a scratch adoption is byte-identical before and after, with no `__pycache__` anywhere. |
| R17-8 | **The security-scope section carried one sentence a hostile reader could disprove** — "the hook's four rules are string heuristics; each one discloses both of its error directions in its own source". Point 2 discloses nothing and is not a string heuristic; point 4 disclosed one direction. Thirteen of the section's fourteen claims fact-checked clean. | **FIXED, by making it true rather than by softening it.** Point 4 gained its false-ask direction (a substring match fires on a longer path containing the configured one, and on prose mentioning it), point 1's directions were corrected under R17-6, and the sentence now says *three* rules are heuristics, names them, states that point 2 compares declared fields and is exact, and adds that no completeness is claimed. |

Nine smaller items were dispositioned in the same pass: a quoted or unquoted
interpreter path containing a space (the default Windows install location) is
no longer a false ATTENTION; the doctor's "every red line names a fixing step"
rule moved from a hand-enumerated selftest list into a `Finding` constructor
invariant, after a reviewer's mutation walked past the list; the never-stages
guard now reads every `git` argv literal in the file rather than the two shapes
it happened to use; a hand-written cert token reports `INFO` rather than `OK`;
the case probe looks one level down when a top level offers nothing to flip;
and the register's own counts, status words and stale fixture line were
corrected here.

---

## The walk labels, corrected

The adversarial read of entry 17 opened with an attack on this document, and it
was right. This register described its adoption tests as "independent adoption
tests" performed by "a fresh reader" on "stranger onboarding walks", while
`BLUEPRINT.md` and `DECISION-BRIEF.md` recorded that the evidence base was AI
personas. Those are two different claims about the same evidence, in the same
repository, in the document titled "measured, not hidden". The attack was ruled
funded by the owner on 2026-08-20 and closed on 2026-08-21.

What changed, and what did not:

- **The label is now the same everywhere.** Every claim that a walk or an
  evaluation was performed says who performed it: an LLM running a written
  persona. Twelve files carry the same wording as this register —
  `README.md`, `BLUEPRINT.md`, `DECISION-BRIEF.md`, `ROADMAP.md`, `LEVEL-1.md`,
  `checks-registry.json`, `tools/adoption_smoke.py`,
  `tools/expectation_lint.py`, both module-02 hook sources and its README, and
  module 03's README. Where the word
  "independent" survives it means either independent *of one another*, with the
  instrument named beside it, or an independent *adopter*, which is the thing
  the kit still does not have.
- **The two instruments are named apart.** Walks 8–14 are LLM-persona adoption
  walks: a scratch repository, every command executed. The three runs of entry
  17 are LLM-persona evaluation reads: the shipped repository, read only. They
  find different classes of defect and their counts are not merged.
- **`docs/walks/` publishes the prompts.** Every walk in the 8–14 loop and every
  entry-17 read has a page carrying its prompt verbatim, the commit it ran
  against, the finding count this register carries, and a distillation of what
  it did. **Entries 1–7 have no page**: they predate the fixed adoption charter
  those seven share, and their prompts were not retained. The index states that
  scope, what is retained, what is not, and — in one paragraph — what a reader
  can and cannot verify from what is published.
- **No finding count moved.** Relabelling the evidence does not change what the
  evidence found, and nothing in the timeline, the escape-rate table or any
  walk section was renumbered or rescored by this change.
- **What is not fixed:** no human has walked the document. That is an open item
  below and a `ROADMAP.md` entry, not something a relabel can close.
- **One bookkeeping debt, named rather than left implicit.** Entry 17's row now
  records two attacks from that round as closed, and round 17's item count in
  the escape-rate table does not include them. That is correct while this round
  is open — the published rate must not move mid-round — but it leaves the
  register asserting a closure its own denominator cannot see. **The coordinator
  owes the decision at stage close:** whether the two later-funded items join
  round 17's row or open a round of their own, decided once, in the open, and
  recorded with the arithmetic. Counting them would *lower* the published rate,
  since neither had a check behind it, so leaving them out is the unflattering
  direction and not a convenient one.

The residual worth stating: an honest label on a self-administered study makes
the study honest, not independent. `docs/walks/` says so in those terms.

---

## Round #21 — the brownfield round: an existing project, and an existing repository

The twenty-first entry is two instruments, and neither is a walk into an empty
directory. The first is a **measured adoption walk into an existing project**
with a real pytest suite, a pre-existing `.gitignore` and uncommitted work in
the tree. The second is the kit's own **Level-1 dogfood adoption** of the OAR
program repository, which already had ledgers, a hand-written `kit.config`, and
documents that write *about* the kit.

The pattern across every finding below: **the install steps assume an empty
repository, and the checks are green over what an existing one loses.** A walk
into a scratch directory cannot meet any of them. It has no config to destroy,
no ledgers to collide with, no records that quote the kit, and no test runner
to wire.

| # | Finding | Disposition |
|---|---|---|
| P3W-6 | No guidance anywhere for wiring an existing test runner, and the shape contract sits in `examples/fake_suite.py` — a file QUICKSTART tells the adopter stays behind in the kit. The string `pytest` appeared once in the whole kit, as a directory name to skip. The measured consequence: an adopter who points a gate straight at `pytest -q` gets `46 passed, 4 skipped`, a numerator with no denominator, so a collapsed collection prints `3 passed` and certifies. That is the silent-green class this kit exists to prevent, reachable by obeying the documents. The walker authored a 161-line adapter from scratch and invented every design decision in it. | **FIXED** — `modules/03-verification/gate_line.py` ships the adapter, with `GATE-LINE.md` as its page and a `--gate-spec` mode that prints the `GATES` entry built from the tool's own patterns, so payload and gate cannot drift. **Proven for pytest and for nothing else, in the tool's own words:** six suites in `examples/pytest_suites/` are run for real by `--capture-golden`, and what pytest reported is committed in `examples/pytest-golden.json` — all pass, pass with skips, failures, errors, a collapsed collection, and a deselected subset. `--selftest` replays all six, re-runs them live wherever pytest is installed, and prints `LIVE HALF NOT RUN` with the reason where it is not (this kit's CI downloads nothing, so that is the CI path). Two negative controls carry the class: a 72-point grid proving that no combination of counts with a zero collection can be green, and the assertion that pytest's own `-q` summary — every one of the six, as captured — is REFUSED by the required pattern. Registered as `selftest:gate-line` plus a `golden:` row per case, cross-checked both ways by `expectation_lint.py`, which now runs over four families. **Residual, asserted out loud in the selftest rather than left to be discovered:** a collection that shrank from 50 to 3 still emits a self-consistent `3/3`, and only `expect_min` catches it — which is why `--gate-spec` takes a `--floor` and why `GATE-LINE.md` says to measure that floor with `--collect-only` rather than guess it. Every runner other than pytest is labelled UNPROVEN by the tool, in its help, in its `--emit` output and on its page. |
| P3W-3 | The runner's `VERIFY: ABORTED` message for a gitignored judge path printed the wrong remedy for an existing repository: *"Remove the rule that covers it."* On the measured walk that rule was `.gitignore:1:.claude/`, which also covers `.claude/sidequest.json`, `.claude/cert-green.json` and `.claude/settings.local.json` — three files the kit's own `.gitignore` says must never be committed, one of them the certification token. Obeying the printed remedy commits session state and the cert token. The correct remedy, force-tracking the single file under the intact rule, was already proven by `adoption_smoke.py` phase 12 and named in this register, and appeared in neither the message nor QUICKSTART. Cost: four minutes grepping a 107 KB file the adopter was never routed to. | **FIXED** — the abort now prints three steps in order: `git add -f <the path>` and commit it, with the note that phase 12 proves this clears the abort; `git check-ignore -v <the path>` if you want to know which rule it was; and removing the rule ONLY if it covers nothing else, with the cost named in the same sentence. Bound in two places so the message and the proof cannot drift: `verify.py --selftest` asserts that the force-track remedy appears and appears FIRST, ahead of the diagnostic and the rule removal, and that the removal clause is conditional; `adoption_smoke.py` phase 12 asserts the same ordering on the message a real repository actually produced, immediately above the control that force-tracks the file and requires the run to start. |
| F1 | `LEVEL-1.md` step 2 prints `cp /path/to/kit/kit.config.example ./kit.config` with no brownfield branch. `cp` overwrites without asking on pwsh, bash and Git Bash, and the dogfood repository already had a hand-written config carrying `JUDGE_PATHS`, `CERT_PATHS`, `GATE_COMMAND`, `VERIFY_RUNNER` and real tier names. Running the line as written destroys all of it. The lane did not run it, which is the point: the loss is invisible afterwards, so nothing would have reported it. | **FIXED** — `doctor:l1-config-complete` reads `kit.config.example` as the registry of every key the templates interpolate and names each one this repository's config is short of. Its fixing step says APPEND at the shipped value, and says in the same red that copying the example over an existing config destroys the answers in it. Step 2 carries the one sentence the check enforces. The expectation is a genuinely different artifact from the subject, so the row needs no waiver. **Residual, stated in the finding:** it judges the PRESENCE of keys only — whether a value is an answer or a shipped example is `doctor:l1-rendered`'s question. Where no `kit.config.example` can be found the check reports UNKNOWN rather than passing. |
| F2 | The kit's four ledger filenames are hard-coded and `LEDGERS_DIR` is the only thing an adopter can move, so on a repository that already keeps ledgers the install has three possible outcomes and `LEVEL-1.md` named none of them. The dogfood repository had `docs/LESSONS-LEARNED.md` and `docs/TOKEN_LEDGER.md`, both named in its README as the ledger set. Two of the three outcomes were green: install alongside, and overwrite. | **FIXED** — `doctor:l1-ledger-collision` compares every `*.md` in `LEDGERS_DIR` against the kit's four names on a normalised stem (case, punctuation and the `.md` suffix removed, containment counted as collision, which is what the measured spellings needed) and reports each collision with all three dispositions named: rename onto the kit's name and carry the content forward; freeze the existing file as the record up to adoption; or move `LEDGERS_DIR`. It changes nothing, and says so. Step 3 carries the same branch. |
| F3 | `doctor:l1-rendered` could not tell a surviving placeholder from a document *about* placeholders. It fired on a judgment-ledger row whose named check was, verbatim, "doctor selftest 149 (forced-red Example Project / your-top-tier-model...)" — the strings are the row's subject, and the only remedy the document offered was to substitute them, which means editing a truthful record of what was fixed and when. **This was a red that could not be cleared by following the document**, and it was live on a real adopter's tree when the fix was written. | **FIXED** — the shipped-value scan now reads each document through `scannable_for_shipped()`, which blanks fenced code blocks, inline code spans, and any line carrying the marker `oar:quotes-example`, for the table cell where backticks would be wrong. **The exemptions apply to that scan only:** an unsubstituted `{{SLOT}}` and a surviving template header block are defects wherever they appear, fence included. **Every exemption is visible** — the finding prints how many lines each mechanism took out of the scan, on every run, so a document cannot go quietly green by fencing itself. Paired selftest checks carry the class: each exemption is asserted GREEN on a quoted string and RED on the same string unquoted, and the measured ledger row is one of the literals. **Residual, stated:** a real defect hidden inside a fenced block is exempt too. A fenced block is displayed as literal example text rather than as the document's own assertion, and the printed counts are the compensating control. |
| F4 | `doctor:l1-interview` accepted any parseable date after `scheduled`, so a fabricated schedule read identically to a real one. The dogfood adoption produced exactly that — a lane-invented date, which the owner's ruling then removed in favour of `not yet held`. | **FIXED** — the `scheduled` state must now say where the date came from (`scheduled <date> confirmed by <who, or which calendar>`). The red names both ways out, and one of them is `not yet held`, which is green and claims nothing — so the owner-blocked adopter, the design's whole reason for a green non-held state, is still one keystroke from green. `not yet held` and `held <date>` need no confirmation: the first claims nothing, and the second is evidenced by the profile's own answers. `PROFILE-TEMPLATE.md`'s STATUS menu and `LEVEL-1.md` step 4 carry the same wording. |
| F5 | **The anti-ratchet's own enforcement layer was prose** — the debt `FAILURE-FLOOR.md` exists to audit, carried by the floor itself. Nothing checked that the demotion review had happened, and nothing bounded the size of the text every session is required to read, although the module-01 template states "keep it SHORT" three times. The owner's question was the shortest statement of the gap: *what is checking the lessons?* | **FIXED** — two checks in the default set. `doctor:floor-staleness` reads the floor's own table and reports every rule past its demotion window, with the arithmetic printed on every run: the window comes from `DEMOTION_REVIEW_STAGES` in the config, never from the file being judged, and the stage-to-day conversion is DERIVED from the mean interval between that floor's own distinct firing dates, because no file in an adopting repository relates stages to days. Rows reading `never` or `unknown — predates recording` are reported as NOT MEASURED rather than counted either way; a row already carrying a final disposition is exempt; fewer than two distinct dates makes the window uncomputable and the check reports UNKNOWN rather than green. `doctor:binding-digest` sizes the rules file plus the newest checkpoint against **325 lines, derived by the four-step method `TOKEN-LEDGER.md` gives for the cost ratio**: (191 rendered lines of the shipped `CLAUDE.md.template`, its 36-line header block deleted as the template instructs, + the 90-line measured checkpoint norm) = 281, × 1.15 = 323.15, rounded up to the nearest 25 = 325. The arithmetic prints on every run, green included. **The first observation is bound to the file it came from:** `--selftest` measures the shipped template live and requires it to still render to 191 lines, so if the template grows, the derivation's input has moved and the selftest goes red naming both numbers. That is the same binding shape as `check:escape-ceiling-agrees`, built because that ceiling drifted silently once already. **Residual, stated on every run:** n = 2 observations, one project, LOW confidence — re-derive it from your own stages — and the check counts lines without judging whether any line earned its place. Both checks report `n/a`, not green, on a tree with no floor or no rules file: whether the documents are installed at all is `doctor:l1-documents`' question, and two reds for one fact is how a tool teaches its reader to skim. **ERRATA, added round 26 (finding R26-3).** Every number in the `doctor:binding-digest` half of this cell is the measurement as it stood when the check shipped, and it was written in the PRESENT tense, so a reader auditing this row against the shipped check found a mismatch with nothing marking it. Rounds 24, 25 and 26 moved the template four times — 191 → 206 → 209 → 219 → 224 rendered lines — and the ceiling twice, 325 → 350 → 375. **As shipped today: 224 + 90 = 314, × 1.15 = 361.1, rounded up to the nearest 25 = 375, and `--selftest` requires the template to render to 224.** Read the figures above as this row's history and `tools/kit_doctor.py`'s derivation comment as the current statement. This register's exemption from `citation_lint` exists so a finding can quote text as it was; this cell was not quoting a finding but describing a live check, which is the direction the exemption also shields. Marked by hand, and recorded as an oracle candidate in round 26 rather than as a check. |

| P3W-1 | `QUICKSTART.md` step 6 printed `cp <template> ./CLAUDE.md` unconditionally. On the measured repository that destroys a 41-line rules file carrying the fixture rule, the skip rule and the style rules — no backup, no warning, and no check anywhere in the document can tell a merged rules file from a clobbered one: an overwritten `CLAUDE.md` reaches `VERIFY: PASS`. The step's only acknowledgement of a pre-existing rules file was the Level-1 case, which is a file the kit itself put there. | **FIXED** — the `cp` is now conditional, marked in the block itself as the new-file route, and the step carries a merge instruction for the other case: render to `CLAUDE.md.kit-new` and merge, or merge from the template by hand, with the existing rules preserved **verbatim** under a marked heading and the two sets read against each other for conflicts. The step also states what no check can see, so the `git diff` before the Step 9 commit is named as the only thing that will show a clobber. The same collision is row 1 of the new `EXISTING-PROJECT.md`. |
| P3W-2 | `QUICKSTART.md` step 4 said to *substitute the slots in the template into `.claude/settings.json`*. The template's `permissions` block contains only `ask`; the measured file carried 10 `allow` and 2 `deny` rules, one of them a control the project's own `CLAUDE.md` depended on. Substituting drops all twelve silently — a permission that no longer exists cannot fail. The step's verb throughout was *substitute and place*, and the structural merge that avoids this was offered one screen later as an optional convenience for people who dislike retyping paths. | **FIXED** — the copy block now carries the merge instruction at the point of loss, and the render section is retitled *"optional on an empty repo, required on one that already holds these files"*, stating that by-hand at Step 4 and Step 6 destroys existing files and that the tool merges the settings as JSON with `permissions.allow` and `permissions.deny` left in place. Step 1 routes an existing-project adopter to `EXISTING-PROJECT.md` before Step 1's first command. No code change: the tool already did this, and `adoption_smoke.py` phase 13 already asserted its fidelity. |
| P3W-4 | Step 4's printed commit line, `git add tools .claude kit.config .gitignore src tests docs && git commit`, has two independent failures on a repository someone is working in. `src` is a directory pathspec, so a half-finished feature lands in a commit titled *"adopt the kit"*. `git add .claude` exits 1 when the directory is ignored, printing `The following paths are ignored by one of your .gitignore files` — and the step's troubleshooting note named only `fatal: pathspec`, missing the signature an existing repository is most likely to hit. The line is joined with `&&`, so the commit never runs. **Re-measured during the fix pass, and worse than the walk recorded:** on git 2.54 the ignored-path failure exits 1 and stages every OTHER path on the line, work in progress included, so the index is left holding unfinished work while the run still reads red. Only the missing-path failure is atomic (exit 128, index untouched). | **FIXED** — the clean-tree warning in the block is strengthened and now points at the paragraphs below it; those paragraphs give the two failure modes with the file-naming form that avoids the first (name the kit's own files, drop `src` and `tests`, one line and no backslash continuations) and the `git add -f` plus `.claude/settings.json` form that avoids the second. Path substitution stays licensed and is now stated twice. The checkpoint's troubleshooting bullet names **both** signatures with what each does to the index, and says to run `git status` and `git reset` after the non-atomic one. Step 9's commit line carries the same pointer. **Two behaviours the re-walk measured that the walk had not:** the ignored-path add is not atomic (above), and force-tracking does not stop `git add` objecting — on git 2.54, while the `.claude/` rule stands, every later add naming a path under it fails the same way, the exact already-tracked file included, so the `-f` is permanent or the path comes off the line. Both are in the step and in `EXISTING-PROJECT.md`. |
| P3W-5 | Both required green checkpoints — Step 4's *"must print: VERIFY: PASS"* and Step 9's *"must still print: VERIFY: PASS"* — are unreachable on any repository with legitimate work in progress inside `CERT_PATHS`. The measured run: `VERIFY: FAIL (exit 1) … RED: judges`, with `THE CERTIFIED TREE is NOT COMMITTED` naming one modified file under `src/`. The runner is correct; the document never addressed the state, so an adopter with unfinished work chose unaided between committing it to manufacture a green and abandoning the final checkpoint. | **FIXED** — both checkpoints now document the state. Step 4 carries the sanctioned route as runnable commands: back up the diff outside the repository and note its sha256, stash, certify, restore — with the instruction to take **both** backups and to verify byte-identity after, and the statement that certification is a property of a tree so a tree holding unfinished work has not been certified. Step 9 repeats it as two facts to record rather than one, the red with the work on disk and the green with it stashed, and adds the discriminator: a red naming anything other than work you know about is a real finding. No code change — the runner's behaviour was right. |
| P3W-14 | Step 1 is titled *"Create your repo"* and printed `mkdir -p … && git init` with no existing-project branch, though a later step acknowledged the empty-repo case as the special one. | **FIXED** — Step 1 opens with two routes. The existing-repository route skips the `mkdir`/`git init` pair and carries the `kit.config` collision the same walk found at Level 1: `cp` overwrites without asking on every shell this document names, so copy the example to a scratch name and append only the keys you are missing. The code block marks which lines belong to which route. |
| P3W-15 | *"Treat the kit as read-only"* sits at Step 1 while Steps 0 and 2 require executing Python inside the kit clone, which writes `__pycache__/` beside any script it imports — a fact Step 4 states in another context. Cosmetic: the kit's own `.gitignore` covers the directory, and the walk verified no new bytecode was produced and the kit's `git status` was empty at start and finish. | **FIXED** — one paragraph at the claim: read-only means you never edit a file of the kit's, not that nothing is ever written under it; the kit's `.gitignore` covers the bytecode so its `git status` stays empty; and on a clone that is read-only at the filesystem level Python skips writing it and the same commands still run. |
| P3W-3 *(document half)* | The code half of this finding fixed the runner's abort message. The document half remained: `QUICKSTART.md` step 4 named the gitignored-judge-path failure and the `git check-ignore -v` diagnostic and stopped before the fix, so an adopter who hit the abort had nowhere in the document to go. | **FIXED** — the step now prints `git add -f .claude/settings.json` as a runnable line, states that the ignore rule stays intact, names `adoption_smoke.py` phase 12 as the proof, and makes rule removal the last resort with the reason: a directory rule such as `.claude/` also covers session state and the certification token, one of which this same step tells the adopter to add to their ignore file. The wording matches the abort message's own order, so the two cannot teach different remedies. |
| P3W-6 *(document half)* | The code half shipped `gate_line.py` and `GATE-LINE.md`. The document half remained: nothing routed an adopter with an existing test suite to either, and `ORACLE-WORKSHEET.md`'s REQUIRED OUTPUT LINE field still asked for a line with no shape guidance anywhere near it. | **FIXED** — Step 3 names `GATE-LINE.md` as the contract to read before writing the required line, and says what a bare `pytest -q` gate cannot detect. Step 4 item 5 carries the existing-suite route as runnable commands: copy the adapter, see the line, print the `GATES` entry with `--gate-spec`, put `tools/gate_line.py` in `JUDGE_PATHS`, size the floor with `--collect-only`, and run the adapter's own selftest **in the kit clone**, since the copy list does not bring `examples/` across. `ORACLE-WORKSHEET.md` gains a section under the worksheet stating the four properties of a judgeable line — self-consistent ratio, veto vocabulary, subset suffix, measured floor — and pointing at the page. |
| P3W-8 | Step 9's expectation model predicted *"exactly one tracked file should hit"*, allowed `CLAUDE.md` as a documented second on two branches, and declared a third the escape — but its diagnostic prose modelled **paths only**. The token list the same step specifies includes your **name**, which hits in `docs/collaboration-profile.md` by construction (Step 8 just wrote it) and in any pre-existing package metadata. Three tracked files hit on the measured walk against a budget of one; the checkpoint was unreachable as specified. | **FIXED** — the diagnostic is scoped to path-shaped tokens, and a table names the three files that legitimately hit and why: the settings file, the profile the document just had you write, and pre-existing author metadata (`pyproject.toml`, `package.json`, `AUTHORS`, a copyright line). The budget is restated as a rule rather than a number — every hit reviewed and every hit explained, one `--exclude` per reviewed file — with the escape redefined as a file you cannot account for, and the prohibition on deleting a token restated. The checkpoint carries the same wording. |
| P3W-9 | `kit_render.py` runs at Step 4 and renders the Step 6, 7 and 8 files immediately, but `JUDGE_PATHS` and `CERT_PATHS` are reconciled at the end of Step 4 and `KNOWLEDGE_DIR` is decided at Step 6. The measured `CLAUDE.md.kit-new` carried the pre-reconciliation `CERT_PATHS` value, already wrong when it was read. Unset keys are handled correctly; the defect is confined to keys that had a value and then changed. | **FIXED** — the render section states the consequence where it happens, names the three keys that move after that point, and gives two remedies: render the Step 6/7/8 files again at the end of Step 6, or grep the rendered files for the two values once Step 6 is done. |
| P3W-10 | `PROFILE-TEMPLATE.md` carries the `KNOWLEDGE_DIR` source-of-truth decision inside its header comment, and `kit_render.py` strips that header. Step 8's instruction 1 exists to make the adopter read that sentence before deleting it — so on the render path the instruction has nothing to act on and the decision has already been deleted unread, the exact outcome the sentence warns against. | **FIXED** — warned at the point of loss, in the render section: the header the tool strips carries a decision Step 8 depends on, so open `PROFILE-TEMPLATE.md` in the kit and read it now, decide with the rest of the `KNOWLEDGE_DIR` decision at Step 6, and write the answer into the profile's maintenance clause at Step 8. Step 8's instruction 1 carries the same branch for a reader who arrives there on the render path. |
| P3W-11 | `kit_doctor.py`'s `doctor:vacuous-gate` asks for a `docs/ORACLE-<gate>.md` page for **every** gate in `RUN_ORDER`, three of which ship with the kit. `QUICKSTART.md` step 3 asks for **one** page, so an adopter who follows the document exactly lands at permanent `[ATTENTION] … 3 gate(s) cannot fail as configured` over gates they did not write — and the walk watched two of those three go red, so "cannot fail" is not true of them. | **FIXED on the document side, to the shipped behaviour.** The doctor is unchanged: the reason it prints for those three is `no ORACLE-<gate>.md page`, which is a missing record rather than an inert gate. Step 3's checkpoint now says so, names the three gates, and gives three honest answers — write the pages, accept the ATTENTION and record why in `docs/FAILURE-FLOOR.md`, or read the finding rather than counting it. Step 7 carries the same note where the doctor is introduced, together with `doctor:version` and the reminder that the verdict word is HEALTHY or ATTENTION and never PASS. **Residual:** the finding's headline still reads "cannot fail as configured" for a gate whose only gap is the page. Recorded, not changed this round. |
| P3W-12 | Step 4's printed pwsh `.gitignore` append used `Add-Content`, whose default line terminator is CRLF, and wrote five CRLF lines into an LF file. Verified with `cat -A`. Hygiene, not breakage — the rules resolve either way — but it leaves a tracked file with mixed endings on the first command an adopter runs in their own repository. | **FIXED** — the printed block now reads the terminator the file already uses and appends that one, through `ForEach-Object` with `-NoNewline` on `Add-Content`. **The first fix was wrong and the re-walk caught it:** hard-coding LF is correct on an LF working tree and creates the same mix in the other direction on a CRLF one, which is what a Windows checkout with `core.autocrlf` on actually has — measured, 15 CR against 4 LF-only appended lines. The shipped form was then measured on all three cases: LF file stays 0 CR / 6 LF, CRLF file stays 6 CR / 6 LF, no file at all gets 0 CR / 4 LF, which is what the `printf` form produces. The paragraph beneath states the residual honestly: the `printf` form carries the same hazard in the other direction on a CRLF tree, and a `.gitattributes` is the general answer. |
| P3W-13 | No step in `QUICKSTART.md` copied the kit's `VERSION` file, and `kit_doctor` reports `[ATTENTION] doctor:version — no VERSION file` with a fix instruction of its own. A gap between the adoption document's copy lists and a shipped diagnostic's expectation. | **FIXED** — `cp /path/to/kit/VERSION ./VERSION` joins Step 4's copy block, `VERSION` joins Step 4's commit line and the file-naming form beside it, and a short paragraph says what the file is for: nothing reads it at runtime, the doctor compares it against the tools' own version, and it is how a repository running newer `tools/` against a stale stamp gets found. Refresh it when you pull kit updates. |
| P3W-16 | After adoption the project's certification is `python tools/verify.py`, which the rendered `CLAUDE.md` names as the single command; the measured project's CI ran `pytest -q` across three interpreters and none of the floor, ceiling, subset veto, hook arming or judge surface. From Step 6 the local gate proves strictly more than CI, and CI is the control outside the blast radius. Nothing told an existing-project adopter the divergence had opened, and module 07 is deferred to *"the following week"*. | **FIXED as documentation** — the divergence is row 7 of `EXISTING-PROJECT.md`, with the walk's own disposition recorded as the recommended one: do not modify CI mid-adoption, log the gap as adoption debt in the project's `docs/FAILURE-FLOOR.md`, and close it when module 07 lands. **Not fixed as a control:** nothing checks that an adopting project's CI runs the same command as its local gate. Recorded here rather than presented as closed. |
| P3W-7 | **RECORDED OPEN, not fixed this round.** The gate table cannot express an exact count on a secondary capture group. The schema offers one floor (`expect_min` with `min_group`) and `ceilings` that are maxima only, so "skips == exactly 4" is not statable: a ceiling of 4 catches a **new** skip and lets a **vanished** one through. A skip that quietly started passing is a change to what the suite proves, and the schema cannot assert it. Until this round the workaround was inferable only from `examples/fake_suite.py`, a file QUICKSTART tells the adopter stays behind in the kit. | **OPEN, with the fix shape and a working route.** The route exists and is now routed to: `gate_line.py --expect-skips <n>` asserts the equality **in the payload** and prints `SKIP SET CHANGED: expected 4, got 3`, which the gate's `fail_pattern` vetoes on, and `GATE-LINE.md` states the limitation in a section of its own. **The fix shape, for the round that takes it:** an `expect_exact` field beside `ceilings`, taking a (group, value, label) triple the way `ceilings` does, so the assertion lives where the other numeric assertions live and shows up in `--list`. **No schema change this round** — the gate table is the interface every adopter's runner carries, and widening it is a change to a shipped contract that deserves its own round with its own selftest cases rather than riding a documentation pass. |
| F6 | Found while fixing F1, on the same instrument: `LEVEL-1.md` Route A tells the adopter that a `KIT RENDER: INCOMPLETE` run naming `{{PROTECTED_PATH}}` is *"the expected Level-1 result, not a failure."* That holds only when `kit.config` was copied from `kit.config.example`. On a repository whose config predates the kit — the case F1 is about — the tool renders from the config it finds and names every key the templates interpolate that the config does not define, so `INCOMPLETE` carries a longer list and is a report about the config rather than the one documented slot. An adopter told the run is expected reads past it. | **FIXED** — the claim is scoped to the copied-config path by name, and the pre-existing-config case gets its own paragraph: expect a longer list, read it, and act on it through `doctor:l1-config-complete`, which names every missing key, and step 2's rule that you append at the shipped value and never copy the example over the file. |

**What this round did not fix, and where that is recorded.** One finding from
the measured walk is **recorded open**: P3W-7, the gate schema's inability to
express an exact count on a secondary capture group, with its fix shape in the
row above and a working payload-side route shipped in `gate_line.py`. One is
**fixed as documentation only**: P3W-16, the CI divergence — nothing checks
that an adopting project's CI runs the same command as its local gate. One
**residual** stands inside a fix: `doctor:vacuous-gate`'s headline still reads
"cannot fail as configured" for a kit-shipped gate whose only gap is a missing
oracle page (P3W-11).

**Two pages this round added that are not findings.** `EXISTING-PROJECT.md` is
the collision list the MAJORs above come from — one row per collision, with the
measured behaviour and the workaround proven for it, and its provenance stated
on the page: one LLM-persona walk, 2026-08-22, findings recorded here.
`docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md` is the walk method itself, written
for an adopter's own documentation: preflight, the fresh-reader lane spec,
persona variation, the `document:line` citation rule, errata landing with its
register row in the same commit as the fixes, and the termination rules from
module 01's "WHEN THE LOOP ENDS".

**Not yet written here, and owed at round close:** this round has no timeline
row and no escape-rate row. Both are round-close artifacts — the escape row
needs the review's classification of which findings an existing check should
have caught, and the register's own rule is that a timeline entry and its
escape row land in the same commit.

---

## Round #22 — the agent front door: `ONBOARD.md`

The twenty-second entry is not a walk and not a review. It is a **build**: one
shipped document, `ONBOARD.md`, addressed to an AI agent that has been dropped
into a project and asked to adopt the kit.

**What it is.** A sequencing and division-of-labour layer over the documents
already shipped. It routes an agent through `README.md`, `DECISION-BRIEF.md`,
`LEVEL-1.md` or `QUICKSTART.md`, `EXISTING-PROJECT.md`, `GATE-LINE.md`, the
oracle worksheet, the seed interview and `docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md`;
it classifies the host as greenfield or existing and routes to the
existing-project branch; it sorts every instruction on the adoption path into
MECHANICAL, SHIPPED DEFAULT or OWNER JUDGMENT; and it requires the third class
to be handed back to the owner as an explicit punch list with named states.

**What it is not.** It is not an installer, not a tool and not a script, and it
executes nothing itself. Every state change it describes is a command a shipped
document already prints, run through a tool the kit already ships, under the
guards those tools already carry — the render tool's containment and
never-overwrite guards, the runner's startup assertion and judges gate, the
force-track remedy for an ignored judged path, and the backup-stash-certify
cycle for a tree with work in progress. No new mechanism was added to the
adoption path, and no shipped instruction was changed.

**The two constraints it was built under**, both owner rulings carried from the
round that funded it:

- **No artifact executes state changes on the adopter's behalf.** A staging tool
  was designed for this slot and killed in review three times; the surviving
  shape is an agent walking the shipped documents under the existing guards.
- **Honest deferral over simulated judgment.** The mechanical half of an
  adoption compresses. The judgment half — the Step 3 oracle, the Step 8 seed
  interview, the Level-1 decisions — does not, and `ONBOARD.md` forbids
  answering it on the owner's behalf. The precedent it copies is `LEVEL-1.md`
  Step 4's interview states, where `not yet held` is a **green** state because a
  stated non-answer is an answer and an invented date is not.

**What is unmeasured, and said so on the page.** Whether routing an agent
through `ONBOARD.md` changes adoption time or completeness against an agent
working from `README.md` alone has no data behind it. The document states this
in its own opening, forbids any speed claim for the route, and forbids restating
the kit's published budgets as its own numbers. The measurement is a later
round's work.

**Collateral in this build:** a routing paragraph at the top of `README.md`'s
"Start here" (agents land at `ONBOARD.md`; the human doors are unchanged) and an
`ONBOARD.md` row in `README.md`'s repository-layout block. Nothing else was
restructured.

**The spec-side adversarial review, and the fix pass.** The build was reviewed
spec-side — the charter, the diff and the shipped tree, with no implementer
report read — against the two binding constraints above. Verdict:
APPROVE-WITH-PUNCH-ITEMS, 0 CRITICAL, 1 MAJOR, 6 MINOR, 2 NIT, 1 rejected below
the bar, 3 pre-existing observations. Both rulings held at the design level: the
reviewer could not find a state-changing command the shipped documents do not
print, and could not construct a path where an agent following the page answers
the seed interview or the oracle worksheet. One review round, per the register's
loop-termination rule; the items rode this fix pass.

| # | Finding | Disposition |
|---|---|---|
| F1 | Reported MAJOR: a fabricated quotation. `ONBOARD.md` attributed to `DECISION-BRIEF.md` limitation 2 the words *"produced no usable human time estimate"*, and a tree-wide grep on the full phrase and on the fragment "usable human" returned only `ONBOARD.md` itself. Compounded by the following instruction, *"Use the same words rather than new ones"*, which directs an obedient agent to copy the string into a report an owner may quote onward. | **FIXED, AND THE FINDING IS PARTLY CORRECTED.** The quotation is **not fabricated.** The words are in `DECISION-BRIEF.md` at lines 40-41 — "It produced no usable human time estimate — it measures an agent executing tool calls" — **wrapped across a line break** between "usable" and "human", which is why a line-oriented grep on either string returned nothing. The real defect is the **section**: those words are in the "one figure with a full walk behind it" paragraph, which cross-references limitation 2 parenthetically; limitation 2 itself does not contain them. So the class is a **miscitation, not an invention** — the same class as F8 and F9, not the round-19 class. Downgraded from MAJOR to MINOR on that evidence. Fixed by citing `DECISION-BRIEF.md`:40-41, quoting the fuller sentence exactly, and rewriting the propagation instruction so it can only apply to text that exists: copy the wording from the lines you are citing, with the document open, never from memory; a quotation that cannot be found in the document it names is a finding against the page; if you cannot locate the string, drop the quotation marks and cite the section for the idea. **The review's method error is now a shipped control** — see the oracle below, whose most important negative control is that a wrapped quotation must still be found. |
| F2 | `KNOWLEDGE_DIR` was classed a SHIPPED DEFAULT the agent may take when the host tree names no knowledge base. The host tree cannot answer the question: absence of a mention in a repository is not evidence of absence in the owner's working world, and the owner having such a place while the repo never names it is the likely case. Consequence: `doctor:l1-knowledge-dir` goes green over an answer the agent supplied, which is the end state the deferral taxonomy exists to prevent. | **FIXED** — reclassified OWNER JUDGMENT on both branches. Where the host names such a place, `DEFERRED` for the owner to confirm; where it names none, still `DEFERRED`, with the repo path `docs` carried as a **provisional** value on `LEVEL-1.md`:84-86's second branch so the mechanical half proceeds, and the punch text required to state in words that the agent could not observe whether such a place exists. `DEFAULT-TAKEN` is named as the state this one may not use, with the reason: the doctor greening over an unmade decision is the leak the ruling forbids. |
| F3 | Two judgments `ONBOARD.md` §4 assigns to the owner — `CERT_PATHS` scope and the keep-or-delete of each seed lesson — had no standing row in §7, whose items were D-1…D-5 only, and appeared in neither of the two lists that would otherwise catch them. So two decisions the page itself calls the owner's could be taken by the agent with no punch-list row required anywhere. `CERT_PATHS` is the more material: a `VERIFY: PASS` then certifies a scope nobody ruled. | **FIXED** — **D-6** (`CERT_PATHS`: what is being certified, and why these paths; landing at `verify.py`'s constant, which is authoritative, and the matching `kit.config` key) and **D-7** (each seed lesson, keep or delete; landing at `<LEDGERS_DIR>/LESSONS.md`) added to the standing-items table. §4's `CERT_PATHS` bullet is reclassified OWNER JUDGMENT on **every** layout rather than SHIPPED DEFAULT on the assumed one, and the step table's Step 4 and Step 7 rows now name D-6 and D-7. D-7's citation is the shipped ledger's own "Seed lessons — earned in the reference build" section and its instruction to delete any that do not apply. |
| F4 | The vacuous-gate "default" was not a shipped default. `QUICKSTART.md`:409-415 presents three honest answers and prescribes none, while `ONBOARD.md`'s own definition of SHIPPED DEFAULT requires a prescribed value **and** a named revisit condition. The sentence declared the choice the owner's and then took it, assigning no punch-list state. | **FIXED** — reclassified OWNER JUDGMENT, recorded `DEFERRED`, with the three answers named and the one the tree is held in stated explicitly: accept the ATTENTION and record why, because it is the only one of the three that writes nothing on the owner's behalf. Writing the `docs/ORACLE-<gate>.md` pages to make the check green is named as the owner's choice, not the agent's. |
| F5 | **The round's one escape.** "Both example entries go" omitted `RUN_ORDER`, and the reassurance cited the wrong selftest section. Measured on a scratch copy of the runner: deleting the two entries from `GATES` alone leaves selftest **section I** red — `[FAIL] no gate in RUN_ORDER is unmentioned by any check that RAN`, `got ['example_unit', 'example_lint']` — while deleting them from `GATES` **and** `RUN_ORDER` prints `VERIFY SELFTEST: PASS — 106 checks`. The headline claim was true but only under the complete edit, which the sentence did not state; the deferred-oracle route that deletes both with no replacement is a case `QUICKSTART.md` never contemplates, so `ONBOARD.md` is where the instruction has to be complete. | **FIXED** — the instruction now names both places, in bold, with the consequence of the under-edit spelled out and section **I** cited as the section that bites, alongside section F's actual role (resolving a live gate name at runtime, which is what `QUICKSTART.md`:775-777 says of it). The runner's own header warning — a permanently-skipped gate in `RUN_ORDER` reports PARTIAL and can never certify — is cited with it. **The review's experiment was re-run during the fix pass and reproduced exactly**, both variants, on a scratch copy; the live tree was not modified to measure it. |
| F6 | `ONBOARD.md`'s two own command blocks — §2's six classification probes and §6's clock read — were bash-only, against the kit's convention of pairing every shell-hazardous block with a `⚠ pwsh:` companion (`QUICKSTART.md` carries them at Steps 1, 2, 4, 6, 8 and 9). Nothing breaks under PowerShell, but a missing path in a two-path `ls` raises a non-terminating error that common tooling reports as a failed command, and this is the **first** document a Windows agent reads. | **FIXED** — both blocks gain a `⚠ pwsh:` companion in the kit's existing form. The probe companion splits the two-path `ls` into one `Test-Path` per line, so no shell reports a partial failure for an answer that is simply "not found", and states why. The clock companion uses `Get-Date -Format`, removing the quoting hazard rather than restating it. Both were run under PowerShell 7 during the fix pass and their output recorded. |
| F7 | The §4 section header read "The four Step-1 values that are not fill-ins" and misassigned two of the four. `QUICKSTART.md`:203-207 states the opposite: `CERT_PATHS` comes back at the end of Step 4 and `KNOWLEDGE_DIR` at Step 6, and `OWNER_ROLE` is not a Step-1 key on that path at all — the string appears there once, in Step 7's slot list. `ONBOARD.md` contradicted its own header twice inside the same section, and D-4's citation was half wrong for the same reason. An agent taking the header literally fills at Step 1 two keys the shipped document says to leave, which is the measured render-early defect. | **FIXED** — retitled "The four values that are decisions, not fill-ins", with an opening paragraph citing `QUICKSTART.md`:203-207 as the authority and naming the render-early defect as the consequence of getting it wrong. Each bullet now carries its actual step in its heading. D-4's citation is corrected to name `LEVEL-1.md` Step 2 for both values and to separate the `QUICKSTART.md` path's Step 1 (tier names) from its Step 7 (`OWNER_ROLE`). The step table's Step 1 row is corrected to say which of the three this step actually asks for. |
| F8 | NIT, same family as F1. `"An afternoon of thinking… does not compress."` was rendered as one quoted string. "An afternoon of thinking" is `QUICKSTART.md`:361's Step 3 heading; "does not compress" is not in Step 3 — it is the budget paragraph at `QUICKSTART.md`:20 and `DECISION-BRIEF.md`:35. The ellipsis fused two sources into one apparent quotation. | **FIXED** — unfused. The row now cites the heading at :361 and the budget paragraph's "is thinking work and does not compress" at :20 as two statements from two places, and says so. |
| F9 | NIT. R3 attributed both `git add` behaviours to "`QUICKSTART.md` Step 4, failure modes 1 and 2". Step 4's numbered mode 1 is the directory-pathspec case and mode 2 is the ignored-`.claude` case; the missing-path / exit-128 / stages-nothing behaviour is in the unnumbered paragraph at `:806-811` and in the checkpoints block at `:896-900`. Both exit codes and both staging behaviours were stated correctly — only the pointer was wrong. | **FIXED** — cited as "the two failure signatures", which is the document's own phrase at `:896-900` ("There are two failure signatures, not one"), with the missing-path half also pointed at `:806-811`. |
| F10 | **REJECTED — below the materiality bar.** "The branches are inline at Steps 1, 4, 6 and 9" omits Step 3, where `EXISTING-PROJECT.md` row 6 also lands. | **REJECTED**, reviewer's own reason carried verbatim: `ONBOARD.md`'s reading order item 5 already routes the existing-suite case to `modules/03-verification/GATE-LINE.md` — its own words are "first if the thing the host must not break is a test suite it already has" — so no adopter is misrouted. |
| F11 | **NEW — found by this round's oracle on its first live run, not by the review.** `ONBOARD.md` rendered *"Decide now and write the decision down"* as a quotation from `QUICKSTART.md` Step 6. The string is nowhere in `QUICKSTART.md`; what :1005-1006 actually says is that where the two rule sets conflict, "that is a decision to make now and write down, not a duplicate to leave standing". A paraphrase dressed as a quotation — the same class as F1, F8 and F9, and a sixth instance the review's citation audit did not reach. | **FIXED** — the real words are quoted, with the line citation. Recorded here as the first thing the new lint caught, on a tree that had already been read adversarially by a dedicated reviewer. |
| P1 | Pre-existing, ruled into this pass. `kit_doctor.py`'s module docstring said "The **ten** default checks" and "the **five** `doctor:l1-*` checks", and `--help` repeated the five, while `--list` derived **12** and **7** from `CHECKS` and `L1_CHECKS` and the code comments said twelve and seven. `git show HEAD:tools/kit_doctor.py` carries the identical "five" at both sites, so it predates this round. | **FIXED, by derivation rather than by correction.** The docstring carries `{N_FULL}` / `{N_L1}` sentinels substituted from `len(CHECKS) - len(L1_CHECKS)` and `len(L1_CHECKS)` immediately after those lists are defined, guarded for `python -OO`, which strips docstrings; `--help` interpolates the same value. The numbers cannot drift again because they are no longer typed. The docstring's third figure — ATTENTION on **six** checks when the full set is run against a Level-1 tree — is not a `len()` of anything, so it was **measured** instead: a Level-1 tree was built in a scratch directory and the full diagnosis run against it, reporting exactly six (`doctor:version`, `judge-paths-exist`, `judge-paths-agree`, `vacuous-gate`, `hook-interpreter`, `floor-staleness`). The number was right; the sentence is amended to "most of them about files the adopter was told not to install", since two of the six are not, and the docstring now says which figure is derived and which a reader must still check by hand. |

**THE ROUND'S MANUFACTURED ORACLE — `tools/citation_lint.py`.** F1 was the second
sighting of the attribution class. The first was round 19, whose three MAJORs
shared one root cause — attribution written from memory rather than from the
source, including one invented quotation — recorded there as an **oracle
candidate** and never built. By the register's own promotion rule, one sighting
is an anecdote and two is a pattern, so the narrow version was built this round.

**What it checks:** a quoted string attributed to a named kit document must
appear in that document. Two attribution shapes, both requiring a backticked
filename — a leading reference with an optional locator (`` `FILE.md`:40-41 ``,
`` `FILE.md` Step 4 ``) followed by the quotation within 200 characters, and a
trailing parenthesised reference within 60 characters of the closing quote.
Comparison is on **whitespace-flattened** text on both sides.

**What it cannot see, stated on the tool's own page and here:** paraphrase, which
is the larger half of the class; a right quotation under a **wrong locator**,
which is the actual F1 defect, because the tool asks whether the string is in the
file and not whether it is in the section named; anything not attributed to a kit
`.md` file; and attributions whose file is not in the tree being linted, which are
skipped with the count printed. Quotations shorter than four words are treated as
named output lines rather than prose. One waiver ships, printed on every run: an
exemplar in `SEED-INTERVIEW.md` that shows the adopter a sentence to write rather
than quoting the document it names.

**The design is the review's own method error, inverted.** The F1 grep was
line-oriented and the source wrapped, so a real quotation was reported as
invented. A check built the obvious way would not merely miss defects, it would
**manufacture** them. `CITE(wrapped-quote)` asserts both halves — that a
line-oriented search misses the string and that this tool finds it — and is the
most important control in the file.

**Seen red before handoff three times, and every red changed the tool.** First,
the end-to-end forced red on a scratch copy reported **clean** over a planted
fabrication: the quote pattern excluded newlines, so a quotation wrapping at the
linting document's own margin was never seen — the tool had the same blind spot
as the defect it was built to catch. Fixed, with `CITE(wrapped-attribution)`
planted over it. Second, the first live run returned five findings, of which
three were one class: a file reference in an earlier **paragraph** pulled onto an
unrelated quotation. Fixed by a paragraph-boundary rule, with
`CITE(paragraph-break)` planted over it; of the two survivors, one was F11 above
and one a self-coined phrase in scare quotes, now unquoted. Third, the run
against **this register entry** — the row describing the tool — returned five
more, which resolved into two prose defects of the author's own (both fixed
here), one quote-pairing defect where an odd number of quote marks inside a
table cell captured 300 characters of prose as a quotation, and two instances of
a class the tool should not be asking about at all: a findings register quotes
text **as it was**, beside a disposition reading FIXED, so those words are absent
from the fixed tree by construction. `KNOWN-ISSUES.md` is therefore exempt as a
document class, with the count printed on every run and the residual disclosed —
a genuine miscitation written into the register is exempt too. **Thirteen
negative controls, registered as a fifth `citation:` family in
`checks-registry.json`** and cross-checked both ways by
`expectation_lint.py`, so a control dropped from the selftest is reported rather
than silently lost — the same argument the doctor, the escape-rate controls and
the golden fixtures made before it. Wired into CI as two steps: the selftest and
the lint, and a **forced-red step that inverts the exit code** and passes only
when a planted fabrication is caught, run on a copy in a temporary directory so
the kit's tree is never modified to test a check against it.

**Collateral in the fix pass:** one paragraph in `DECISION-BRIEF.md`'s "What it
is" naming the watermelon effect — green outside, red inside — as the
audience-recognisable statement of the gap, with the brief's existing bridge line
identified as that effect restated for AI, and three shipped counters named:
forced red, the state-word contract, and the escape rate. No new claim: each
counter already ships, and the paragraph closes on the boundary the brief already
states, that this is not a security boundary.

**Not yet written here, and owed at round close:** this round has no timeline row
and no escape-rate row. Both are round-close artifacts, and the register's rule
is that a timeline entry and its escape row land in the same commit.

---

## Round #23 — calibration defaults, and the realignment ask

The twenty-third entry is not a walk and not a review. It is a **build**: one
shipped document, `modules/08-collaboration/DEFAULTS.md`, offering module 08 a
second route to the collaboration profile.

**What it is.** Part 1 is a pre-filled starting state — the calibration values of
one long-running AI-assisted engineering program, distilled to classes and
de-identified, grouped the way `PROFILE-TEMPLATE.md` is grouped, one sentence
per value, each with an id. Part 2 is the realignment ask: the seed interview
restructured as a walk down those values, each one kept, overridden or deleted,
ending in the same `docs/collaboration-profile.md` the blank-page route produces.

**What it is not.** It is not a replacement for `SEED-INTERVIEW.md`, and it is
not a new default. The blank-page route remains the shipped default path — the
same ruling shape the optional render tool ships under, offered beside the
by-hand route rather than in front of it. No shipped document was restructured,
`PROFILE-TEMPLATE.md` was not edited, and no check, tool or slot changed.

**Collateral in this build:** two routing sentences (`QUICKSTART.md` Step 8 and
`LEVEL-1.md` Step 4), one row in `modules/08-collaboration/README.md`'s files
table with its adopt-alone count corrected from three documents to four, one
clause on `README.md`'s module-08 row, one cell in `ONBOARD.md`'s reading-order
table, and one paragraph in `ONBOARD.md` §7 — **and that paragraph is not a
routing sentence.** It classifies `DEFAULTS.md` as a SHIPPED DEFAULT source for
the pre-ruling working contract, extends `DEFAULT-CONTRACT.md`'s in-force
standing to a class of values the eight do not cover, and issues three
prohibitions: no default in a verbatim answer block, no default in the overrides
table as an override, and no move of the `INTERVIEW:` line off `not yet held`.
It is the most load-bearing edit in the build, and it is recorded as a normative
addition rather than as routing prose, because understating one as the other is
the class of thing this register exists to catch.

**The constraint it was built under.** The values crossing into the kit are
calibration *shapes* — how a decision is presented, what an unanswered item
costs, what ends trust — never personal content. No names, employers, project
names, anecdotes, quoted personal sentences or machine paths. The build ran
`tools/deident_scan.py` over the whole kit tree against a token list held
outside it, and the coordinator re-scanned independently before the commit.

**The two design decisions that carry the doctrine.**

- **A default is a working contract, not an answer.** The page is a SHIPPED
  DEFAULT source in `ONBOARD.md` §4's sense for the contract an agent runs under
  before the owner has ruled, and it is explicitly **not** an answer to D-2. An
  agent may cite it and record `DEFAULT-TAKEN`; it may not write a default into
  the profile's verbatim blocks or move the `INTERVIEW:` line off `not yet held`.
- **A kept default is recorded as a kept default.** The route produces the same
  artefact and no downstream step branches on which route was taken, but the
  profile stays legible about provenance: the owner's words and a ratified
  default are different things, and the fabrication rule requires a reader to be
  able to tell them apart.

**What is unmeasured, and said so on the page.** Whether walking an owner down a
pre-filled starting state produces a better or faster profile than the blank
page has no data behind it. The page makes no effectiveness claim, states the
circularity of its own argument (the reason to offer the route is one of the
values on it), and names the blank page as the better instrument for an owner
who overrides that value.

**The spec-side adversarial review, and the fix pass.** The build was reviewed
spec-side — the charter, the working-tree diff and the shipped tree, with no
implementer report read — against the two binding constraints above, with
re-identification as the lead attack. Verdict: APPROVE-WITH-PUNCH-ITEMS, 0
CRITICAL, 2 MAJOR, 6 MINOR, 3 NIT, 6 rejected below the bar. Both constraints
held at the design level: the reviewer could not construct a path where the page
answers D-2, moves the `INTERVIEW:` line, or lets an agent execute a state change
on the adopter's behalf. **The re-identification attack found no leak** — a
hostile-profiler pass over the page against the surface the kit already
publishes returned nothing reconstructible beyond it, no direct identifier, and
no anecdote residue. One review round, per the register's loop-termination rule;
the items rode this fix pass.

| # | Finding | Disposition |
|---|---|---|
| M1 | MAJOR. The betrayal-group anchoring mitigation was void on the solo-owner path. The page asks question 5 open before showing CAL-F1…F4, but that instruction sits in Part 2, about seventy lines below the four rows themselves. The kit routes a solo adopter here as both walker and owner in three places, so a solo owner reads the four candidates before writing their own answer — silently, and with nothing in the record showing it happened. | **FIXED, and fixed above Part 1 rather than only inside Part 2.** A section, "Before you read Part 1, if you are the owner", now stands immediately before Part 1: write your own answer to question 5 first, dated, and do not read Part 1 until it is written down. Placing it above Part 1 is what makes it route-independent — every route into the page lands at the top, so the instruction precedes any sight of the four however the reader arrived. Restated at two more sites: Part 2's "Who and when" and the CAL-F group note, and in `modules/08-collaboration/README.md`'s "Working solo?" note, which owns the solo case most directly. |
| M2 | MAJOR. KEEP had no landing site. The page routed OVERRIDE by an explicit table and DELETE by a sentence, and left KEEP — the disposition the route produces most of — with only what the record must *carry*, never where it goes. The only profile sections available are shaped for authored trait prose with an evidence sentence, which is the exact form the page forbids, so an obedient agent was put where the page's instructions could not all be satisfied at once. | **FIXED.** "Where an override lands" is now "Where each disposition lands" and routes all four states. KEEP lands inline in its group's profile section in a fixed one-line form — `CAL-B2 ratified <date> — kit default, not the owner's words.` plus the value in one sentence — and never as a bolded trait claim with an evidence sentence, with the reason stated: a ratified default has no sighting in this project and no words of the owner's behind it. DELETE and `NOT REACHED` are routed in the same section. |
| m1 | MINOR. "This page points at it rather than restating it" was false for eight values, each a one-sentence restatement of a `DEFAULT-CONTRACT.md` value, only two of which carried the "listed here so the walk reaches it" justification. Three had already drifted into addition. Nothing compares a restatement to its authority; the citation lint reaches quoted strings only, and these are correctly unquoted. | **FIXED, wording.** The claim now says what the page does — it names a value in one sentence so the walk reaches it, and points at the authority — and adds the tie-breaker: **where the two differ, the cited document governs.** The "listed here so the walk reaches it" parenthetical is extended to all eight rows, so the pattern is visible rather than inferred. |
| m2 | MINOR. CAL-C5 restated the process-ratio numerals. 0.40 already has an authority in this register with a four-step derivation, and the row published it with a second provenance story; the 0.60 all-in tripwire appeared **nowhere else in the kit** and arrived with no cluster maximum, no n and no confidence — the placeholder the row's own group note warns against. | **FIXED.** Both numerals are dropped from CAL-C5. The row now points at the two authorities — `TOKEN-LEDGER.md`, "The ceiling", for the method, and this register's "The ratio ceiling" for the kit's own derivation with its n and confidence — and says: derive yours, do not adopt one. The value survives; one authority holds it. **0.60 is not published anywhere in the kit.** If it is ever to be, it belongs in "The ratio ceiling" with the same four-step treatment 0.40 got. |
| m3 | MINOR. A taken calibration default left no record in the tree. `ONBOARD.md` requires the punch list to live in the tree as well as the report, and for these values there was no permitted place: not the overrides table, not the verbatim blocks, and `DEFAULTS.md` is never copied. The next session would read `INTERVIEW: not yet held` — correct — with no way to learn the agent had been running under thirty-three unratified values. | **FIXED, one paragraph.** Where an agent has taken values from the page, it adds one line to the profile's `STATUS` section, beside the sentence already there recording the eight as in force and unconfirmed, naming the page and the ids taken. `STATUS` is neither a verbatim block nor the overrides table, so this is permitted and creates no new file. |
| m4 | MINOR. A closed partial walk recorded four counts and no ids, so a later reader knew *how many* values were still unratified and could not know *which* — and the not-reached set is not recoverable by subtraction, because a kept value is in the profile and a deleted one is absent, while an unwalked one looks exactly like a deleted one. | **FIXED, one clause.** The revision-log entry now lists the not-reached **ids**, with the reason stated: it is what makes a partial walk resumable and what stops an unwalked default reading as a ruled one. |
| m5 | MINOR. The page said the walk asks the same five subjects, and its order list named six groups, with the mapping never given. Q2 (checkpoint shape) had no named home at all — its content is split across CAL-C1 and CAL-B5 in two different groups, neither of which said so. A completed walk was safe; a **partial** walk left the agent judging whether all five subjects were put to the owner with nothing to judge against, and a wrong answer there moves the `INTERVIEW:` line. | **FIXED, one table.** Part 2's order section now carries the five-question to six-group mapping, with Q2 shown explicitly as requiring both CAL-C1 and CAL-B5, and states that the two groups carrying no seed question — How they think, and Blind spots — can be skipped without a subject going uncovered. |
| m6 | MINOR. This entry described "three routing sentences and one README row", and one of the three was `ONBOARD.md` §7's fourteen-line normative paragraph, which creates a SHIPPED DEFAULT source and issues three prohibitions. Understating a normative addition as routing prose is the class of thing this register exists to catch. | **FIXED, wording.** Split out into a named "Collateral in this build" subsection above, matching Round #22's shape, with the `ONBOARD.md` paragraph called what it is and the other collateral enumerated per site. |
| n1 | NIT. The C-group note called CAL-C5 and CAL-C6 both "numbers from the source program". CAL-C6 is the loop-termination rule: no measured figure, no decimal point, and the kit ships it in full in module 01. | **FIXED, wording.** "CAL-C5 carries figures from the source program; CAL-C6 restates a rule the kit ships in full." |
| n2 | NIT. DELETE was the only disposition with no actor named — "The value does not apply to this project" — while KEEP and OVERRIDE both name the owner. Combined with the blind-spots group's stated DELETE default, an agent could close that whole group without the owner and still satisfy "every id has one". Bounded harm: DELETE writes nothing into the profile. | **FIXED, two words.** "The **owner** says the value does not apply to this project", with the `if they gave one` clause kept and clarified — the ruling is not optional; only the reason is. |
| n3 | NIT. Part 2 item 4 asserted the profile's promotion rule binds the route without saying how a KEEP satisfies it. A ratified default has zero sightings in the adopting project, so a literal reading forbade writing any KEEP into the profile. | **FIXED, one clause.** The item now states the resolution that was sound but unstated: the promotion rule governs what the AI *observes*, not what the owner *states* — a ratified default, like a seed-interview answer, enters on the owner's ruling rather than on a second sighting, and both always have. |
| A9 | The review independently enumerated seven unedited sites that describe module 08 and ruled on each: **three FIX, four LEAVE.** | **THREE FIXED, FOUR LEFT AS RULED.** Fixed: `README.md`'s module-08 row gains a clause naming the optional calibration (a shipped document absent from the top-level module map is invisible above the module's own README); `ONBOARD.md` reading-order row 7 gains `DEFAULTS.md` marked optional, because §7 now has the agent cite a page the reading order never told it to open; and `modules/08-collaboration/README.md`'s "Working solo?" note, which is M1's third fix site. Left, as ruled: `README.md`'s Level-1 routing (naming the option there promotes the second route at the layer where the default path is chosen); `ONBOARD.md` §4's step-8 row, whose "OWNER JUDGMENT, absolutely" is the strongest doctrinal sentence in the kit on this subject and would be weakened by qualification; module 08's file contract at "No other substitution exists here", **verified rather than passed over** — `DEFAULTS.md` carries zero slots, so the claim still holds unedited; and `DECISION-BRIEF.md`'s "five required" and `LEVEL-1.md`'s six-document counts, **also verified** — the page is read in the kit clone and never copied, so neither count moves and editing either would be wrong. |
| R1-R6 | Six findings **rejected below the materiality bar**, each with the reviewer's one-line reason. | **REJECTED**, reasons carried: (1) "two unrelated projects" as newly disclosed shape — `BLUEPRINT.md` already publishes "n=2 projects, one owner" and names both. (2) `BLUEPRINT.md`'s "collaboration-layer evidence is n=1" against the A-note's "two unrelated projects" — both true (one owner, two projects); no reader is misled by the pair. (3) The `QUICKSTART.md` insertion sits above the blank-page steps — it is labelled Optional and names the route below as the default; ordering alone does not make it primary. (4) Thirty-three `DEFAULT-TAKEN` punch rows is a heavy list — volume, not a defect; the states and their requirements are correct. (5) `DEFAULT-CONTRACT.md` default 3 (verbatim capture) has no CAL id — the page never claims to enumerate the eight, and CAL-A3 covers the adjacent ground. (6) "Three checks name module 08 by path" against the four references found — all four name `PROFILE-TEMPLATE.md`, the substantive claim holds, and the count wording changes nothing an adopter sees. |

**ORACLE CANDIDATES from this round — recorded, not built.** Every one of the
eleven findings was an oracle candidate: no check that existed before this round
covered any of them, which is the arithmetically expected shape for a prose-only
build and is also the finding worth recording, because `DEFAULTS.md` is now one
of the most normative documents in the kit and not one line of it is
mechanically checked. Two of the eleven suggest cheap, general oracles:

- **Ordering lint.** An instruction of the form "do not show X before Y" must
  appear **above** X in the same document. Catches M1.
- **Closed-set routing lint.** A document that defines a closed set of states
  must name a landing site for each one. Catches M2, and would have caught the
  shape of m4.

Neither was a shipping requirement of this round, and neither is built. They are
recorded here as candidates for the promotion rule to act on at a second
sighting, which is the same route `citation_lint.py` took in Round #22.

**Two owner-funded additions rode this fix pass**, on the Round #20
tiering-economics precedent (positioning prose funded by the owner, landing in
one place, compressed rather than expanded, making no new claim).

- **An at-scale statement**, in `README.md` as "At scale, and where it breaks",
  placed immediately after "Why files, and where this sits" because that section
  already carries the not-a-runtime position and the compose-with-a-framework
  argument, and the floor's third item is the direct continuation of it. It
  states the per-seam-not-per-mass scaling model (the kit rides git's scaling
  model — many per-repository instances, nothing centralised, with the ratio
  metrics scale-invariant by construction), gives the existence proof for the
  mechanisms at organisational scale (file-based, check-based, ledger-based
  control programs already run globally under SOX, COSO and ISO — an existence
  proof for the mechanisms, explicitly **not** evidence about this kit, and no
  audit function has consumed anything it produces), and concedes the floor
  plainly: judgment plurality (single-seat today, `ROADMAP.md` tracks it),
  certification composition across trust boundaries (no attestation chain
  ships — compose with supply-chain attestation rather than rebuilding it), and
  high agent concurrency, where an orchestration engine is genuinely required
  (the graph says what ran; the rails say whether the green was real — a
  composition that is architecturally clean and **empirically untested**, with
  no measured instance of the two running together). The section closes by
  saying it is architecture argument and not measurement.
- **A prerequisites statement**, consolidated in `README.md` under
  "Prerequisites" ahead of "Start here", with a four-line summary on
  `DECISION-BRIEF.md`'s cost table and a pointer from `QUICKSTART.md` Step 0.
  Git was previously **stated nowhere**, which made the kit's deepest dependency
  the only undisclosed one; Python 3.10+ was stated only in Step 0 and the
  harness assumption only in `BLUEPRINT.md` §9. Step 0 gains `git --version` as
  its first line and its checkpoint is corrected from nine lines to ten.
  **No version floor was invented.** The statement says no minimum git version
  has been derived, names the six git commands the kit actually uses, and
  records that every git behaviour the kit cites was **measured on git 2.54** —
  the honest form, and the one the citation lint's spirit requires of a number.
  pytest and GitHub Actions are labelled optional where they already live.

**Not yet written here, and owed at round close:** this round has no timeline row
and no escape-rate row. Both are round-close artifacts, and the register's rule
is that a timeline entry and its escape row land in the same commit.

---

## Round #24 — the drop-and-go acceptance run, and its fix pass

The twenty-fourth entry is two instruments in one round. First an **acceptance
run**: an LLM-persona agent, given nothing but the instruction to adopt the kit
into a host starting at `ONBOARD.md`, adopted the kit @ `15c2ded` into a
prepared existing project — a real pytest suite, CI, an evidence binder, a
`.claude/`-covering ignore file, a pre-existing `CLAUDE.md` and settings file,
and uncommitted work in progress. It ran the `LEVEL-1.md` path to
`LEVEL 1: HEALTHY (exit 0)` and reported **six findings against the documents**
and one self-inflicted incident. Then the **fix pass** below, which dispositioned
all six.

**What the run is evidence for, and what it is not.** It is the first end-to-end
exercise of `ONBOARD.md` as a route rather than as a document, and the first one
where the host was somebody else's project rather than an empty directory. It is
still an agent executing tool calls: its 11m 55s of wall-clock is tool-time, the
run says so, and no speed claim is made from it here or there.

**The host's punch list is not registered here.** The run raised seven items
(H-1…H-7) for the host's owner — module 01 not adopted, the scan not run, an
ignore rule over a judged path, and so on. Those are the adoption's output
working exactly as `ONBOARD.md` §7 designs it, not defects in the kit, and
registering them would inflate this round's denominator with somebody else's
decisions.

| # | Finding | Disposition |
|---|---|---|
| F1 | `ONBOARD.md`:41 told the agent Step 0 is **nine** lines. Round 23 had added `git --version` and corrected `QUICKSTART.md`'s own checkpoint from nine to ten; the copy of that number in `ONBOARD.md` — which names `QUICKSTART.md` Step 0 by name — was left behind. Cost nothing this run; the hazard is an agent counting to nine and stopping before the live fixture run, the only line in Step 0 that exercises a settings file rather than a selftest. | **FIXED**, and the class was **promoted to a check** — see the oracle below. The number is now ten, and the count lint reads it against the block it names on every run and on every push. |
| F2 | `LEVEL-1.md`:184-189 stated the expected render result as **one** unfilled slot (`{{PROTECTED_PATH}}`). `kit_render.py` treats a shipped placeholder as UNSET, and `kit.config.example` ships all four tier names in the `your-…` shape, so a config copied from the example yields **five**. An adopter who takes `CLAUDE.md` is told to expect one red and gets five, with no page saying the other four are normal. | **FIXED, and CORRECTED AGAIN BY THIS ROUND'S REVIEW (M1, M2, n1).** The first fix stated the tool's real summary line but named the wrong precondition: it promised **five** unfilled slots on a `kit.config` copied from the example, where the real result on that config is **six** — `{{KNOWLEDGE_DIR}}` is the sixth — and the `NONE` branch two screens earlier yields six as well, which is F2's own defect reproduced on a documented branch. The step now carries a three-row table, one row per answer step 1 offers, each with the summary line that branch actually produces (reproduced on three scratch hosts) and what is unfilled on it, quoted through `each named above`. Each slot then gets its disposition: the four tier names are step 2's decision arriving late (fill them and re-render if you run agents; if you do not, the rules file is the conditional sixth document and the tiering prose goes with it, deletion recorded); `{{PROTECTED_PATH}}` is the module-02 tripwire the template marks *delete if unused*; and `{{KNOWLEDGE_DIR}}` is step 1's decision rather than a slot to delete — answer it and re-render. The closing paragraph states which of them redden step 5 and which do not, per branch: `doctor:l1-knowledge-dir` is green on `NONE`, so `doctor:l1-rendered` is the only thing between an adopter and a document pointing at a directory called NONE. |
| F3 | **The round's escape, ruled so.** `doctor:l1-documents` reported the host's own untouched 30-line `CLAUDE.md` as `CLAUDE.md (module 01 as prose)`. The green line then certified **six** documents where five were installed, and REMOVAL COST named a file the adoption never wrote — a reader following it literally deletes the owner's own rules. The neighbouring member of this class was already recorded (`EXISTING-PROJECT.md`:49: no check can tell a merged rules file from a clobbered one); this is the third, and a check existed, covered the surface, and answered the wrong question. | **FIXED, code and documents.** The doctor now decides **present** against **adopted** by the kit's own template fingerprints — eight slot-free **fingerprints** of `modules/01-governance/CLAUDE.md.template` — seven section headings and one rule sentence, which is why the reader-facing lines no longer call them all headings — two or more of which mean the file carries module 01's prose however it got there. A pre-existing file is not counted, is not scanned for shipped values, and is named in the finding with the numbers the decision used; REMOVAL COST never names it. **Why fingerprints and not git:** step 5 runs before the commit, where an adopted rules file is dirty and a pre-existing one is clean — git would report the two backwards — and after the commit a merged file is indistinguishable from an overwritten one by history alone. **Residual, stated in the tool and in `LEVEL-1.md`:** an adoption that deleted nearly every kit heading reads as the host's own file, and a host file carrying two of the kit's section titles reads as adopted; a merged file reads as adopted, which is correct, and its removal is a revert, which the line already says. Both directions are negative controls in `--selftest`, the fingerprint literals are cross-checked against the shipped template, and both end states were run against a scratch host. **CORRECTED BY THIS ROUND'S REVIEW (M3, M4, M10, m4, m5, m6), all at the reader-facing surface the first fix left uncontrolled.** The green line used to read `host CLAUDE.md is the owner's own, untouched — it carries none of module 01's prose, this level did not install it`: three claims of provenance that a count of fingerprints cannot establish, and all three false on a trimmed adoption (a genuinely adopted 10.7 KB file whose headings were reworded, which the template's own instruction 2 invites). It now claims only what the mechanism supports — `carries fewer than 2 of module 01's 8 fingerprints (N found)` — and states the limit of that reading out loud. The detail line no longer says `carries none` beside `1 of 8 found`. The ADOPTED branch prints the same two integers, which is the direction that lets REMOVAL COST name a file and was the direction with no printed evidence. REMOVAL COST's closing clause names no rules file at all: it used to offer ``CLAUDE.md`` and ``.gitignore`` as the usual merge targets on every run, including the run whose line above had just promised the removal cost does not name it. **The structural fix is M10:** the three summary lines are now `level1_summary_lines()`, a pure function the selftest reads, with controls asserting the not-adopted line's numbers, that ``CLAUDE.md`` appears in no part of REMOVAL COST on that run, and that it does appear on the adopted run. The first fix was tested where it computes and not where it speaks. |
| F4 | `ONBOARD.md`:235-243 offered a binary — the host runs no agents, or the host runs agents with the tiers unevidenced — and the measured host was neither. It has a `CLAUDE.md` and a `.claude/settings.json` with 10 allow rules, so an assistant demonstrably works in it; it contains no agent, tier, spawn, lane or charter vocabulary anywhere, so tiered spawning is unevidenced. The blocking branch's stated consequences are all Level-2 mechanics that do not exist at Level 1. | **FIXED** — the third case is now shipped, and it codifies what the run itself did rather than inventing a resolution. Harness configuration present, agent vocabulary absent: do not pick a branch; classify the underlying question (does this project run agents, in the sense the four keys describe) as OWNER JUDGMENT under §4's own definition, record it in §7 `DEFERRED` where the mechanical half continued and `BLOCKED` where it stopped, leave the keys unset, and write into the punch text what was searched for and not found. |
| F5 | `ONBOARD.md` §4 and `LEVEL-1.md` disagreed on whether the rules file is conditional. `LEVEL-1.md`:157 makes it conditional on running agents; `ONBOARD.md`'s no-agents branch presumed it installed and then partly deleted, which is only possible if it was taken. | **FIXED by yielding, which is what the page already says to do.** `ONBOARD.md`:16-20's rule — where this page and a shipped document disagree, the shipped document wins and the disagreement is a finding — **worked on first contact**: the run detected the conflict, named `LEVEL-1.md` as governing, took the conditional reading, and reported the disagreement rather than picking a side. The page is now aligned: the no-agents branch says the honest act on the `LEVEL-1.md` path is not to install the file and to say so, with the delete-and-record instruction scoped to the `QUICKSTART.md` path where Step 6 installs it, and §4's step-6 row states the conditionality and names `LEVEL-1.md` as the authority. |
| F6 | `LEVEL-1.md`:320's de-identification scan requires `--tokens <a-path-outside-this-repo>`; `ONBOARD.md`:521-523's fence permits writes inside the host plus one named report file. **The intersection is empty**, so an agent obeying both cannot run the step as printed. The run did not run it, did not invent a fourth location and did not weaken the command. | **FIXED as a documented capability grant**, which is what the fence's existing implicit exception (the report path) always was. §8 now states it with four properties, all requirements. **The owner ruled the granularity after this round's review (M5) found the permissive reading:** the clause presented the report path as an existing instance of the *same single* capability and then enumerated two artifact types for it, so an agent handed a report path — that is, every run — could conclude a granted path existed and write the token list beside it, citing the clause at every step, leaving DEFAULT-CLOSED unreachable in the common case. The properties as shipped are: **DEFAULT-CLOSED, PER ARTIFACT** (no path designated *for a given artifact* → the capability to write that artifact does not exist, and the dependent step is recorded NOT RUN citing the clause); **HUMAN-GRANTED**, extended with *you never infer a grant from a path's existence* — a path handed to you, a directory that is there and writable, or an artifact of yours already sitting in it are none of them grants; **ENUMERATED PURPOSE, ONE PER PATH** (a grant covers one artifact type at one path; the two enumerated types each require their own explicitly designated path; the report path is not a token-list path and neither is its directory; a granted path is a file unless the operator named a directory); **USE-RECORDED** (the report names every granted path, the artifact type each was granted for, and every file written there), now carrying its self-attestation residual. A closing paragraph states the ordinary outcome — report written, scan NOT RUN, punch item raised — as the designed one rather than a degraded one. `LEVEL-1.md`'s rule is unchanged and now points at the clause, and its Step 6 prose says a path given for something else is not a grant for this. **The rejected alternative, and why:** a token list inside the tree is one force-add from published. |
| A1 | **Owner-ruled, queued before this round and landing in it: the anti-ratchet mirror.** The register's declined-oracle reasoning existed as one clause inside Round #23's escape row and nowhere in the shipped doctrine, so an adopting project inherited the promotion rule and not its reverse gear. | **SHIPPED.** Module 01's WHEN THE LOOP ENDS gains rule 7: a round may decline to build an oracle it was offered, the declination is a **recorded bet**, and future findings of that class count against the round that declined. The ORACLE-DECLINED row shape is defined beside it, and module 04's judgment-ledger status legend describes that shape rather than redefining it. **This round's review (M7, M8, M9, n3) found the doctrine's own paperwork short in three ways, all fixed in the fix pass:** module 01 gave a six-field row for a four-column table, which drops cells in a markdown renderer, so the row is now written in the ledger's own four columns and module 01 is the single authority for it; *counts against the round that declined* had no arithmetic home, so module 04 now states the convention — a declined-class finding is **not** an escape (an escape is what an existing check should have caught, and a declined class has no check), it is a coverage gap with a named owner, and attribution is one citation of the declining round's row in the finding's register entry, changing no metric and touching `escape_rate.py` not at all — and states how a bet closes: the check is later built and the row is marked `SUPERSEDED` citing it, or a later round re-declines the class, appends its own row and holds the bet from then on. The kit also shipped the doctrine with zero conforming instances; this round's own declinations, below, are the first. **The first instance is retro-cited, not rewritten:** Round #23's escape row already states that if either of its two recorded-not-built oracles is later built and the class produces findings, those count against the round that declined the check. That sentence is the doctrine's first use; rule 7 is the doctrine. |

**THE ROUND'S MANUFACTURED ORACLE — `tools/count_lint.py`.** The citation lint's
own docstring names the class it declines to cover: *a claim in a document should
be verifiable against the source it names — quoted strings, cited steps, stated
counts.* F1 is the third member, and this is the narrow version of it.

**What it checks:** a stated count whose target it can locate must match the
target. Three ways a count names a target, and nothing else counts as naming
one: a count phrase that **opens** a paragraph ending in a colon, over the table,
list or fenced block immediately below it; a line count in the paragraph
immediately **after** a fenced block; and — F1's shape — a count naming another
document's section in backticks, over the single fenced block in that section.
Countable lines are non-blank, non-comment lines with a wrapped command counted
once.

**What it cannot see, stated on the tool's page and here:** prose counts with no
locatable target, which is the larger half of the class by volume and is skipped
with the count printed on every run; semantic counts (*two version checks, five
selftests* describes what the ten lines are, not how many there are); counts of
things outside the documents; ambiguous targets, which are skipped rather than
guessed at; and counts inside this register, which records what a count used to
be beside its correction — exempt as a document class the same way the citation
lint exempts it, with the same disclosed residual.

**Seen red before handoff, twice, and both reds changed the tool.** First, on the
live tree with F1 unfixed: one finding, `ONBOARD.md`:41, `counted 10, stated 9`.
Second, and this is the one that changed the design: the first build let a count
phrase anywhere inside a colon-ended paragraph claim the block below it, and its
first live run **reported 23 findings against this kit of which 22 were its
own** — 21 of them one class (*one pass*, *4 is what lets*, *eight defaults*:
numbers that merely sit in a paragraph which happens to end in a colon). The rule
is now that the phrase must **open** the paragraph, and the cost of that
narrowing is stated in the tool (*Run these ten commands:* is no longer seen).
The twenty-second was a different class and a worse one: `QUICKSTART.md` Step 4's
correct *three lines* was reported as a defect, because the third of its three
commands is a pipeline written across two physical lines. A command that wraps
now counts once, which is the sibling of the citation lint's most important
control — there a quotation that wraps in its source must still be found — and is
planted as `COUNT(wrapped-command)`. **Nineteen negative controls, registered as
a sixth `count:` family in `checks-registry.json`** and cross-checked both ways
by `expectation_lint.py` — seventeen at handoff, plus the two this round's
review added (see the vocabulary ceiling below). Wired into CI as two steps:
step 2b8 runs the selftest and the lint as two commands, and step 2b9 is the
forced-red half that inverts the exit code and passes only when a planted stale
count is caught, run on a copy in a temporary directory so the kit's own tree
is never modified to test a check against it.

**Collateral in this fix pass:** the binding digest's ceiling was **re-derived**,
twice, which is the binding working rather than a defect. Rule 7 grew the
module-01 template from 191 rendered lines to 206, and the review's fix pass grew
it again to 209 when the row shape was refitted to the ledger's four columns.
`kit_doctor.py --selftest` fails on a stale constant naming both numbers, and the
derivation was re-run each time rather than the assertion relaxed: (209 + 90) ×
1.15 = 343.85, rounded up to the nearest 25 → `DIGEST_CEILING_LINES = 350`, with
n = 2 and LOW confidence unchanged. The ceiling lands on 350 both times because
the arithmetic puts it there, not because a number was left alone.

### The adversarial review of this round, and its fix pass

The round was reviewed spec-side against the owner's F-gate rulings and the diff,
on the uncommitted work at `15c2ded`. **Verdict: APPROVE-WITH-PUNCH-ITEMS** — 0
CRITICAL, 10 MAJOR, 7 MINOR, 3 NIT, 6 rejected below the materiality bar, 0
HALTs. Per module 01's loop-termination rules that is approved: the items rode
this one fix pass and bought no second round. Every item above has been
dispositioned in the row it belongs to; the items with no home in an F-row are
the doctrine's own paperwork (M7–M9, below), the count lint's disclosure gaps
(m2, m3, m7) and the two stale line citations (m1).

**Read the MAJOR count at its true size.** Ten MAJOR findings against a round
whose predecessor drew two is a spike, and the honest reading is scope rather
than a fall in quality: this round shipped **two builds, one piece of doctrine
and six acceptance-run fixes in a single lane**, where round 23 shipped one
theme. Nine of the ten are wording at a reader-facing surface — the tenth, M10,
is the structural reason the other four in its group existed at all. Nothing in
the review was unsafe to ship, and the reviewer said so.

**The escape rate for the review is 0 of 20, and that zero is not a quality
signal.** No check that existed at `15c2ded` should have caught any of the
findings, which is honest — the round's checks are new — and it is evidence that
the checked surface is young rather than that the loop is learning. The number
worth watching is the twenty oracle candidates the review named, and the
declinations recorded below are this round's answer to them.

**The two stale citations, and both lints' shared blind spot (m1).** The F6
clause shipped citing `LEVEL-1.md`:320 twice for the de-identification scan; the
round's own +36 lines in that document had moved it, and :320 by then read
"DOES NOT CERTIFY". Corrected to the command at :398 and the rule at :402. The
class is invisible to both lints **by design** — the citation lint requires a
quoted string, and the count lint's `SECTION_REF` excludes the bare `:N` line
form because a line range names no enumerable section — so both tools now
disclose that blindness in their stated scope, naming each other. A disclosure,
not a build; the check is declined below.

**The count lint's second blind spot (m2), disclosed rather than closed.** Its
`NUMBERS` vocabulary stops at *twenty* and its digit form reads three digits, so
"thirty rows", "twenty-five checks" and "1024 lines" were matched by nothing:
not checked, not skipped, and absent from the skip total the tool's own docstring
calls "the disclosure". The review proved it by planting five false counts
written with the word *ninety* and watching all five vanish. **The ceiling stays
and the disclosure is completed**, because widening what the tool checks widens
what it can be wrong about, and v1 buys its low false-positive rate by reading
few numbers. A second pattern now recognises the tens words, their hyphenated
forms and digit runs of four or more, for the sole purpose of counting those
phrases as **skipped with a reason of their own** — it decides nothing and can
never produce a finding. Eight real phrases became visible on the live tree the
day it landed. Residual of the disclosure itself, stated: "a hundred lines" and
spelled compounds beyond the tens remain invisible.

**Two smaller corrections in the same tool.** Its module docstring is now a raw
string, ending a `SyntaxWarning` printed on every local run and both CI steps
(m3); and its two statements about the first live run — "22 findings, 21 its
own" — are corrected to the register's 23 and 22, which were right (m7).

### Rule 7 applied to this round — the declined oracles

The review named twenty oracle candidates. Three were built into this fix pass
(the `level1_summary_lines` control, and the count lint's two vocabulary
controls). The rest are declined, and rule 7 says a declination is a recorded bet
rather than a silence. These are the doctrine's first conforming rows, written in
the four columns module 01 now prescribes:

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| ORACLE-DECLINED: a document that quotes a tool's summary line disagreeing with what the tool prints on the state the document names — run the tool in a fixture tree and string-match the quoted line | round 24 | not built: needs a fixture-tree harness no kit tool has yet, and the fix pass corrected the two live instances by hand; trigger: a third finding of this class, or the first one that reaches an adopter | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a bare `` `DOC.md`:N `` citation whose line number has drifted — minimum viable, N exists in DOC.md; better, the cited line's section carries a keyword from the citing sentence | round 24 | not built: the minimum-viable form is nearly free and nearly worthless, and the useful form needs a section resolver the citation lint has already declined once (its v2 question); trigger: the section resolver landing, or a third stale citation | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a kit tool emitting a warning on stderr — run the tools under `-W error`, or assert an empty stderr, in CI | round 24 | not built: one instance, one character to fix, and `-W error` over every tool risks reddening CI on a dependency's deprecation the kit does not control; trigger: a second warning shipping to CI | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a stated count whose target the count lint cannot locate — prose counts, semantic counts, counts of things outside the documents, ambiguous targets | round 24 | not built: it is the tool's declared out-of-scope surface, the larger half of the class by volume, and covering it needs a target resolver rather than a wider pattern; trigger: a wrong count of this shape reaching an adopter, which the skip count is the standing disclosure for | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a stated count written with a number above the checking vocabulary (the tens words, hyphenated forms, digit runs of four or more) | round 24 | not built: v1 keeps its checking surface small on purpose and the fix pass completed the disclosure instead, so these phrases are now skipped and counted rather than invisible; trigger: a wrong count of this shape found by hand | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a number stated in a tool's source disagreeing with the same number in this register — the count lint reads no `.py` and exempts the register as a document class | round 24 | not built: two exemptions would have to be reversed to reach it, and both are load-bearing; trigger: a second disagreement of this shape | **ORACLE-DECLINED** |

None of these was built in this pass, deliberately: rule 7's point is that the
declination is recorded, not that it is avoided. A later finding of any of these
classes cites the row above it, per module 04's attribution convention.

**Not yet written here, and owed at round close:** this round has no timeline row
and no escape-rate row. Both are round-close artifacts, and the register's rule
is that a timeline entry and its escape row land in the same commit. The
escape-rate row will carry the review's own items alongside the acceptance run's,
with the MAJOR-count spike read as scope — two builds, doctrine and six findings
closed in one lane.

---

## Round #26 — the adversarial battery: an evaluation read and a prior-art audit

The twenty-sixth entry is two adversarial instruments run against the shipped
kit at `2ad480a`, both read-only, and one implementation lane closing what the
owner ruled GO.

**Instrument 1 — an LLM-persona evaluation read** in the kit's own vocabulary: a
principal-engineer persona with a controls and QA background, no prior contact
with the kit, deciding whether to recommend adoption. It read `ONBOARD.md`,
`DEFAULTS.md`, `GATE-LINE.md`, `EXISTING-PROJECT.md` and `JUDGMENT-LEDGER.md` in
full, ran the kit's own Step 0 battery and every selftest, and recomputed the
whole escape-rate table by hand before running the instrument. **Verdict:
ADOPT-PARTIAL** — 0 CRITICAL, 2 MAJOR, 4 MINOR, 2 NIT, 14 GOOD, 0 halts.

**Instrument 2 — a prior-art audit**: a redundancy hunt over the kit's
load-bearing claims against live artifacts, plus an ancestry audit of the
doctrine document. Fourteen live web searches and twelve page fetches, with
every reference carrying a verification tier. **Verdict: the composition claim
stands narrowly and is eroding; the ancestry audit FAILS for `BLUEPRINT.md`,
which names no ancestor for any mechanism.**

**What the evaluation read confirmed, and it is worth recording beside the
defects.** The escape register's arithmetic reproduced exactly — nineteen
rounds, 208 items, 35 escapes, 16.8%, with all nineteen per-round percentages
recomputed by hand and matching, and the tool's published block reproduced
character for character. Every claim on `GATE-LINE.md` matched `gate_line.py`.
The P3 baseline was green on the first attempt on a Windows host. The read's own
summary of why it recommended adoption at all is the part worth keeping: it
found instances of failure modes this register had already published — round 24
discloses the bare-locator blind spot that produced the locator finding below,
round 20 names the claims-more-than-it-verifies class that produced the doctor
finding — which is a different and better situation than finding failure modes
the kit had not disclosed.

| # | Finding | Disposition |
|---|---|---|
| R26-1 | **MAJOR. `ONBOARD.md` §8's capability grant and §5's R4 had an empty intersection on the common brownfield case.** §8 enumerated exactly two artifact types an agent may write outside the host — the handoff report and the de-identification token list — and forbade everything else under any grant. But `QUICKSTART.md`:915-927 makes a third mandatory: the work-in-progress backup, `wip.patch`, written outside the repository, with :925 requiring both backups. `ONBOARD.md` restates that route as binding twice and never names the artifact. So the designed outcome for a brownfield host with uncommitted work inside `CERT_PATHS` — the case `EXISTING-PROJECT.md` exists to serve, and where it records the collision as measured — was a HALT that no document anticipated, with no `NOT RUN` disposition and no punch-item route. Aggravating: §8's premise sentence asserted that the token list is the one artifact the kit keeps out of the tree, which `QUICKSTART.md`:919 makes false as stated. **This is round 24's F5 class exactly** — the fence/token-file empty intersection — resolved then for one artifact and never generalised to the class. | **FIXED, and generalised this time.** The enumeration is now labelled a CURRENT LIST of three, set by the shipped documents rather than by the clause, and **the extension rule is stated as part of the grant**: every artifact type a shipped document requires to be written outside the host gets its own operator-designated path on the same four properties, and where none was designated the step is recorded NOT RUN citing the clause, as a §7 punch item. The rule therefore reaches a fourth artifact type without another round. The work-in-progress backup is added with its consequence stated in full: with no granted backup path the agent does not stash, does not certify, records the certifying run NOT RUN, and hands back a punch item naming the path the owner would have to grant — rather than committing the work to clear the tree, which is what R4 exists to forbid. The paragraph states why this is no longer a HALT under either §5's "do not invent a fourth" or §3's contradiction rule. The false premise sentence is corrected to name both artifacts and the reason each is kept out. **All four grant properties survive unchanged as requirements** — default-closed per artifact, human-granted, single-purpose-per-path, use-recorded. R4 in §5 now points forward to the clause as the source of the path it needs. |
| R26-2 | **MAJOR. `WHEN THE LOOP ENDS` rule 8 shipped an unverifiable citation into every adopter's rules file.** The rule's authority is one measured instance, and the instance read "the reference register's round 24 — nine self-catches in one round, including the rulebook-size lint firing on the growth rule 7 itself caused." Three independent defeats of verification. The register is never named in the template and no step copies it into a host, so the adopter held a pointer to a document they could not identify. "Nine self-catches" appears in this whole kit exactly once — at :55, the round-25 row asserting it; round 24's timeline row and its section enumerate nothing of the kind. And "the rulebook-size lint" is not a check name; the check is `doctor:binding-digest`. `CLAUDE.md.template` renders into the host, so this shipped into adopters' repositories, in the newest and least-read doctrine, in the finding class `DEFAULTS.md`'s own betrayal line CAL-F3 names. The root cause is round 19's, recorded here: attribution written from working memory of a round the author had just run. | **FIXED, and the count now matches what this register carries.** Rule 8 names the source (`KNOWN-ISSUES.md` in the kit repository, rounds 22-25), states that the file stays in the kit clone and is never copied into the host so the adopter knows where to read it, uses the real check id `doctor:binding-digest` and says what that check does, and cites **four** self-catches instead of nine — one per round, each recoverable from this register's own timeline rows: the citation lint red on its author's two unregistered controls (round 22) and again on its author's prose mid-pass (round 23), the adoption smoke catching the fix lane writing an unsubstituted slot (round 24), and `doctor:binding-digest` red on the growth rule 8 itself caused (round 25). **Nothing in the rendered rule is now unverifiable by an adopter.** The unsourced count at :55 is left standing as what was written, with an errata marker beside it rather than a silent edit. |
| R26-3 | **MINOR. This register described a currently-shipped check in the present tense with two-revisions-stale numbers.** Finding F5's disposition (:879) states that `doctor:binding-digest` sizes against 325 lines derived from a 191-line template, and that `--selftest` requires the template to still render to 191 lines. Shipped at the time of the read: 219 and 375. The register's exemption from `citation_lint` is sound for quoted findings text — a register quotes text as it was, beside a disposition reading FIXED — but this cell was not quoting a finding; it was describing a live check, and the exemption shields forward-looking claims in the same motion. A reader auditing the register against the artifact found a mismatch with no errata marker. | **FIXED by errata, and the mechanism named rather than hidden.** An ERRATA block now closes that cell: the numbers above it are marked as this row's history, the shipped values are stated (224 + 90 = 314, x 1.15 = 361.1, rounded up to 375, selftest requiring 224), and the reader is pointed at `tools/kit_doctor.py`'s derivation comment as the current statement. The gap the exemption creates is stated in the errata itself. **No check built** — see the declined-oracle row below; distinguishing a quoted finding from a live description is a judgment this register's shape does not currently expose to a tool. |
| R26-4 | **MINOR. `kit_doctor.py`'s binding-digest derivation carried stale prose beside current constants, and the selftest's own assertion label was arithmetically wrong.** The shipped constants were right. The explanation was one and two revisions behind: the four-step comment still narrated 191 → 206 → 209 and "lands on 350 both times", and its STEP 3 opened at 350 while quoting 375's figures. The finding proper is the selftest label at :3085 — "the ceiling is the derivation's arithmetic, not a free-standing number: **(209 + 90) x 1.15**, rounded up to 25", where (209 + 90) x 1.15 = 343.85 → 350, not the 375 the check was asserting. **The check passed because both sides of the assertion read the live constant, so the sentence a human reads was never compared to anything.** That is the claims-more-than-it-verifies class this register names at round 20, on the check built to prevent exactly this drift, and it is invisible to `count_lint` because these are code comments rather than prose claims. Mitigating: every number that PRINTS on a run is computed from the live constants, so no user-visible figure was ever wrong. | **FIXED at the structural layer, not the wording layer.** The label is now BUILT FROM THE CONSTANTS with a format string, so the prose a human reads is a third reader of the same source and cannot go stale again — the previous fix shape would have been to retype the numbers. The four-step comment is rewritten with current figures (224 rendered, 314 digest, 375 ceiling, 61 lines and 16.3% below the line, 448 for a doubled template) and now carries the re-derivation history as an explicit dated list, because each re-derivation is evidence the guard fires. The binding note states that when the constant moves, STEPS 1-3 are re-stated with it. |
| R26-5 | **MINOR. Four `document:line` locators in `ONBOARD.md` did not point at what they cited**, plus two imprecise ones. `:422` cited `DECISION-BRIEF.md`:40-41 for a quotation actually at :64-65, where :40 is a section heading. `:535` cited `QUICKSTART.md`:1005-1006 for text at :1011-1012. `:308` cited `:775-777` for a claim at :778-780. `:212` cited `(:361)` for a heading at :366. Imprecise: `:226` cited `:203-207` for a quotation at :208-209, and `:367` cited `:806-811` for a failure signature at :861. **The `:422` instance is self-indicting** — it sits four lines above the passage ordering the reader to copy quotations "from the lines you are citing, with the document open, and never from memory", and §8 requires findings to carry the line, not the section, not the gist. | **ALL SIX FIXED**, each re-verified with the target document open rather than from the finding's report. The two imprecise ones were in scope because they are the same class and the same cost to correct. **This finding CLOSES round 24's declined-oracle bet on stale bare locators**, whose recorded trigger was "the section resolver landing, or a third stale citation" — six is past three, and the class is attributed to round 24 per module 04's convention. Whether the check is now built is an owner decision and is not taken here; the bet is recorded as triggered. One related observation, recorded and not fixed: the quotation at `ONBOARD.md`:306 is real but its source is `verify.py`:1484's selftest section header, not the `QUICKSTART.md` line the sentence cites; the citation now points at the claim's document and the quotation is the tool's own label. |
| R26-6 | **HIGH, from the prior-art audit. `BLUEPRINT.md` contained zero external citations.** A grep for eighteen ancestry-bearing terms across the doctrine document returned only the kit's own vocabulary. Mutation testing (§5.5), defect escape rate (§2 and §11), SRE error budgets (§6), IV&V (§4), requirements traceability (§1), SRE postmortem culture (§8) and the andon cord (§4) are all present and all unattributed, under the framing "each law paid for at least once on the reference builds". That framing is true and it is also the failure mode: a reader who knows mutation testing reads §5.5 and either concludes the author does not know the 1978 literature or concludes the author knew and did not say. Both readings cost more than the citation. **The audit was explicit that the discipline exists elsewhere in the program** — `README.md` names SOX, COSO, ISO, SLSA and sigstore; `DECISION-BRIEF.md` hands the reader watermelon reporting — and stops at this one document. | **FIXED with a section rather than a standing instruction**, which is this kit's own structure-over-sentences rule applied to a prose failure. `BLUEPRINT.md` §12 "Lineage" ships as the document's last word: a mechanism → named ancestor → what this kit added table covering all ten gaps the audit named, each row carrying its source's verification tier, opening with the honest framing that a practice two independent derivations arrive at is better evidenced than one only this project found. Three inline lines were added at the points a hostile reader trips first, where a forward reference is too slow — §5 law 5 (mutation testing), §2 (defect escape rate), §6 (SRE error budgets). **Sourcing discipline, stated:** only references the audit marked FETCHED or SEARCH-URL are cited. The andon cord's Toyota origin was RECALLED-UNVERIFIED and ships **explicitly labelled unverified in its own row** rather than dropped or asserted; the promotion-and-demotion row states that no named artifact was found and reports the negative result rather than inventing an ancestor. |
| R26-7 | **HIGH, from the prior-art audit. `README.md` positioned the kit against the wrong neighbours.** "Why files, and where this sits" named only LangGraph and CrewAI, which are orchestration runtimes the kit composes with, not the governance-layer projects it actually sits beside. The audit named three live ones a reader reaches in one search — Chock (Apache-2.0; policy committed to the repo compiled to pre-tool-use hooks and CI gates, with per-surface enforcement labelled enforced / enforced-at-commit / advisory, which is functionally this kit's Zone A/B honesty shipped as compiler output), Agentic OS (the same evidence-gated thesis as drop-in files across several harnesses), and Microsoft's Agent Governance Toolkit (a runtime control plane with an SRE package). **Not naming a competitor a reader will find in one search is the same failure class as not naming an ancestor.** | **FIXED.** The compose-with-orchestrators paragraph is kept unchanged, and a peer paragraph follows it naming all three with one sentence each on the real difference, sourced only from the audit's classifications. No disparagement: Agentic OS is cited as convergent evidence strengthening the file-first argument rather than as a rebuttal of it, and Microsoft AGT's threat model is stated as the one this kit declines rather than as a weakness. `COMPARISON.md` is named as the full table. |
| R26-8 | **MEDIUM, from the prior-art audit. The self-application claim has near neighbours, so "we apply it to ourselves" is no longer distinctive.** Three artifacts in the 2026 literature publish self-hosting or dogfooding evidence about themselves. The distinction survives — all of them publish coverage or completeness scores, which is the flattering direction, and none publishes a miss rate with denominators that is allowed to rise — but the kit's decision surface was leading with composition, which is the weaker of its two claims and the one measurably eroding. | **FIXED, surgically, at the two places the claim is made** — `README.md`'s opening and `DECISION-BRIEF.md`'s "What it is". Both now state the differentiator as CONDUCT rather than composition: the discipline applied to itself with the unflattering number published, leading with the 50.0% and 42.9% spikes rather than the 21.7% average, and stating in each place that the composition claim has a short half-life and is not the one to weigh. `BLUEPRINT.md` §11's evidence bullet is untouched by the owner's instruction — surgical sentences, not a restructuring. |
| R26-9 | **Owner-funded. There was no public page a reader could check the kit's claims against.** The audit produced a per-claim classification the kit had no home for, and a comparison that lives only in a private report is a comparison the reader cannot audit. | **SHIPPED: `COMPARISON.md`** at the kit root, date-stamped as of 2026-08-22, opening with the standing invitation — if you know an artifact that makes a row wrong, name it and we will cite it. It carries all eighteen load-bearing claims classified REDUNDANT-BY, PARTIAL-OVERLAP or NO-MATCH-FOUND with sources at their verification tiers; the composition scorecard against the four closest candidates; an explicit "where a competitor is simply better" section; and a "what this page does not establish" section stating that a NO-MATCH-FOUND means the queries were run and the results read, and nothing more. The headline is published before the table and states the unflattering half first: the composition claim is narrow and eroding, and the conduct claim is the durable one. `README.md` routes to it from "Start here" and lists it in the repository layout. **One correction made while building it:** the audit's summary line said eleven of the eighteen claims are PARTIAL-OVERLAP; recounting from its own table gives twelve rows carrying that verdict — eight wholly and four in part. The page publishes the recount with the enumeration visible rather than carrying the number forward. |
| R26-10 | **LOW, from the prior-art audit. De-identification gating is REDUNDANT-BY gitleaks and TruffleHog for the secret class, and the incumbents were never named.** `README.md`'s existing label — a publication aid, not a data-loss control — was already honest; the gap was that the tools that own the class went unnamed, in the one component where an incumbent does the adjacent job better. | **FIXED in two places.** `README.md`'s security-scope bullet now names both incumbents, states the difference between them (one decides whether a string looks like a secret, the other whether it works), says to run one of them for that class, and states that what `deident_scan.py` covers is program-identity tokens — a name, a username, an employer, machine path fragments — which have no detectable shape and can only come from a list. `tools/deident_scan.py`'s own docstring carries the same statement, because the tool's help is what an adopter reads before the README section. Both close with the same sentence: a green here says nothing whatever about secrets. |
| R26-11 | **DISCLOSURE, not a defect. `agt doctor` is a name collision.** Microsoft's Agent Governance Toolkit ships `agt doctor` and `agt verify` alongside this kit's `kit_doctor.py` and `verify.py`. The tools do different jobs — AGT is a runtime control plane aimed at the hostile agent this kit explicitly declines to defend against — but a reader searching either name will meet both. | **DISCLOSED in both places a reader could hit it**: `README.md`'s peer paragraph and `COMPARISON.md`'s C16 row, in each case stated as a collision disclosed here rather than left to be discovered, with the difference in job named in the same sentence. No rename: the collision costs a reader one sentence, and a rename would cost every existing adopter their commands. |
| R26-12 | **SELF-CATCH, recorded because rule 8 says to expect one.** `citation_lint` went red on this round's own new prose, in the fix pass for R26-2 — the round whose whole subject is making rule 8's self-coverage citation verifiable. Both hits were the same shape: a rhetorical phrase in quotation marks sitting within the glue distance of a backticked `.md` filename, which the lint correctly reads as an attribution and correctly reports as absent from the named document. One was in `COMPARISON.md`, one in `DECISION-BRIEF.md`. | **FIXED** — the quotation marks are dropped and the phrase is stated as prose in both places, which is one of the two remedies the lint's own red prints. **No defect in the check.** Recorded because rule 8's claim is that a new rule's arrival draws its own red at maximal irony, and this is the round-26 instance of it: the check built in round 22 firing on the round documenting the doctrine that predicts it. **A second self-catch in the same lane, caught by hand and not by a tool:** the R26-8 edit added a paragraph to `DECISION-BRIEF.md` above line 64, which moved the very quotation R26-5 had just re-pointed `ONBOARD.md`:422 at — so the lane fixing four stale locators created a fifth, in the same pass, in the same finding. Caught by re-verifying every touched locator against the FINAL tree rather than against the tree as it stood when the fix was written, and corrected to :76-77. **That re-verification step is the finding**: fixing a locator and editing its target document in one round are independent acts whose collision nothing checks, and the class is the round-24 declined oracle's, now triggered above. |

**Collateral: the ceiling re-derived a fourth time, and the red was observed
before any constant moved.** R26-2's rewrite grew `CLAUDE.md.template` from 219
to 224 rendered lines. `kit_doctor.py --selftest` failed first, naming both
numbers — `got 224, want 219` — exactly as its binding promises, and only then
was `DIGEST_SHIPPED_RULES_LINES` moved. **The ceiling itself did not move:**
(224 + 90) x 1.15 = 361.1, which rounds up into the same 25-line bucket, so
`DIGEST_CEILING_LINES` stays 375. That is the arithmetic holding a number in
place rather than a number being left alone, and the comment now says which.

### Rule 7 applied to this round — the declined oracles

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| ORACLE-DECLINED: a present-tense description of a live check inside this register drifting from the artifact it describes — the register is exempt from `citation_lint` by design, and the exemption shields forward-looking claims in the same motion that makes it honest about history | round 26 | not built: separating a cell that quotes a finding from a cell that describes a live check needs a distinction this register's shape does not expose to a tool, and the errata convention is the cheaper control; trigger: a second forward-looking claim in this register found stale, or the register growing a marker that makes the two cell kinds machine-separable | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a stale bare `` `DOC.md`:N `` locator — **round 24's bet, now TRIGGERED.** Round 24 declined this class with the trigger "the section resolver landing, or a third stale citation"; round 26 found six in one document | round 24, re-raised round 26 | not built in this lane: the useful form needs the section resolver `citation_lint` has declined twice, and this is a build decision the owner funds rather than a fix pass takes; trigger MET — the class is attributed to round 24 per module 04's convention, the bet is fired, and the build-or-re-decline decision is owed at the owner's gate | **SUPERSEDED by round 27** — resolved at the owner's gate, both ways: BUILT in the line-window form (`citation_lint`'s window check, `citation:window-*`), RE-DECLINED in the bare-bounds form. See Round #27's rule-7 table for the resolution row and its measured recall |
| ORACLE-DECLINED: a quotation whose real source is a tool's source line rather than the document the sentence cites — `citation_lint` reads no `.py`, so a quotation lifted from a selftest section header and attributed to a document passes | round 26 | not built: one instance, and widening the lint to read Python source widens what it can be wrong about against a corpus where quoted strings are output lines rather than prose; trigger: a second instance, or a quotation of this shape reaching an adopter | **ORACLE-DECLINED** |

**Not yet written here, and owed at round close:** this round has no timeline row
and no escape-rate row. Both are round-close artifacts and the coordinator's, and
this register's rule is that a timeline entry and its escape row land in the same
commit. One finding this round is an escape by the register's own definition —
R26-4 names the class round 20 published, and a check that existed was green
over it. R26-5 is NOT an escape: its class was ORACLE-DECLINED in round 24,
and module 04's convention (stated in `JUDGMENT-LEDGER.md`'s legend) is that
a finding of a declined class is a coverage gap attributed to the declining
round's bet — counting it as an escape would make the number mean two
things. The escape row is where that reading is published rather than here.

---

## Round #27 — the fired bet's build: recall, and the line window

Round 24 declined the stale-locator oracle and filed it as a rule-7 bet. Round
26 attributed six locator findings to it. This round is what rule 7 says
happens next: the bet is resolved at the owner's gate, in public, with the
built check's recall measured against the six findings that fired it.

**The order was forced by round 26's own m4 finding, and the order mattered.**
`citation_lint`'s selftest section E asserted only that the lint saw SOME
attributions in the kit's documents. That is a presence count, not recall, and
it was green while the lint could not see a real ten-word attribution at
`ONBOARD.md`:227-228. Building a window check on top of an extractor whose
reach was unmeasured would have produced a check that looked stronger and
covered less. So the recall floor was built first, and it immediately paid for
itself — see R27-1.

| # | Finding | Disposition |
|---|---|---|
| R27-1 | **ESCAPE. A quotation in `ONBOARD.md` did not match its source, and `citation_lint` was green over it for four rounds.** `ONBOARD.md`:227 quoted `QUICKSTART.md` as "four keys come back later, each at the step that needs it". `QUICKSTART.md`:208 begins the sentence "**Four** keys come back later" — the quotation silently lowercases a sentence-initial capital. The lint's whole subject is whether a quoted string appears in the document it names, and this one does not, verbatim. It was invisible because shape B's glue forbade a backtick between the reference and the quotation, and this sentence names two config keys on its way there. **Round 26's m4 raised the reach gap and recorded "no live defect: the quotation is real." That reading is now corrected: there was a live defect, and the reach gap was hiding it.** An unmeasured reach does not merely miss defects — it converts them into evidence that nothing is wrong. | **FIXED at both layers.** The quotation is corrected to the source's own capital. The glue now admits COMPLETE inline code spans and lets the existing `MD_REF` post-filter decide attribution, which is where that rule always lived; the glue and quotation are matched inside a LOOKAHEAD so a match consumes only the reference, without which `finditer` swallows the span and `CITE(intervening-ref)` is silently repealed (proven: removing the lookahead reds that control). Measured recall over the shipped kit: **40 → 44 attributions, none lost**; checked quotations 28 → 30. Section E is replaced by `RECALL_FLOOR`, four NAMED attributions asserted extracted-and-present, registered as `citation:recall-floor`. **Red-provable, proven:** reverting the glue to its pre-round-27 form reds exactly the m4 row and no other. |
| R27-2 | **SELF-CATCH on this round's own new work, uncounted as an item.** The registry row for `citation:window-normalisation` was flagged SELF-REFERENTIAL by `expectation_lint` on its first run, before any waiver was written: subject and expectation are two functions in one file. | **WAIVED WITH ITS REASON, not relabelled.** The finding is correct and the shape is kept deliberately — the property asserted IS an agreement between two normalisations, and there is no third artifact that defines it. What keeps it above a tautology is stated in the row: the two are independently implemented (a regex substitution and a character walk), and the equality is asserted over all 48 shipped documents rather than a literal the test wrote. Residual accepted and stated: an author who rewrites both in lockstep passes. Recorded because the alternative — re-pointing `expectation_from` at "the kit's own documents" — would have cleared the lint by relabelling, which is the failure this register exists to catch. |

### The bet, resolved — what was built and what was re-declined

**BUILT: the line window.** For an attribution carrying a LINE locator
(`FILE.md`:N or `:N-M`), the lint now checks that the quotation actually sits
at those lines. Tolerance **0**, comparison **overlap**. Overlap is what makes
zero defensible: it already absorbs a quotation that wraps past a single-line
locator, and a range wider than the quotation. Line numbers come from
`flatten_with_lines()`, which produces the same normalised string as
`flatten()` — asserted equal over every shipped document, because a window
layer that normalised differently could report a quotation both present and
absent. Five new registered controls (`citation:window-lines`,
`window-stale`, `window-locator`, `window-repeat`, `window-normalisation`),
forced red before shipping and proven end to end: a stale locator in a fixture
tree exits 1 and prints where the quotation really is.

**The tolerance is a measurement, not a taste.** Recall against the six R26-5
defects at each candidate tolerance: **±0 → 3, ±1 → 2, ±2 → 2, ±3 → 2, ±5 →
1**. Every non-zero tolerance costs a real defect, because the tightest of the
six sits ONE line outside its cited range (`:203-207` for a quotation at
:208-209). A locator is a mechanical fact about a file, not an estimate.

**MEASURED RECALL: 3 of 6, published as measured.** The reviewer's counsel at
the owner's gate predicted 4 of 6. The prediction was one high, and the
published number is the measured one. The three reached — `:422`
(`DECISION-BRIEF.md`:40-41 for a quotation at :76-77), `:535`
(`QUICKSTART.md`:1005-1006 for :1011-1012) and `:226` (`:203-207` for
:208-209) — were validated as FIXTURES reconstructed from the battery reports,
with each stale locator reverted in memory against the real current source. The
kit tree was never mutated to a stale state. **Note that `:226` is reachable
only because R27-1 was fixed first**: before the glue fix its quotation was not
extracted at all, so building the window first would have measured 2 of 6 and
attributed the shortfall to the window design.

The three not reached are named rather than assumed covered, and the reasons
are in the tool's own OUT OF SCOPE block:

- `:212` — the stale line sits in a BARE trailing locator, `(:361)`, naming a
  line but no file, while the attribution's own locator is a section name
  (`Step 3`). The bare `` `DOC.md`:N `` form is the shared gap this register
  has disclosed since round 24.
- `:367` — a locator with no quotation anywhere near it. The window check needs
  a needle.
- `:308` — counsel's fourth. The quotation sits about 150 characters BEFORE its
  reference with an intervening parenthesis, past what shape A's glue allows.
  Widening the glue that far would trade a known miss for unknown false
  findings, which is the wrong trade for a tool whose green is the product.

**RE-DECLINED: the bare-bounds form.** The v1 shape round 24 described —
assert only that line N exists in DOC.md — was measured against the same six
and detects **0 of 6**, because every one of the six points at a line that
exists and holds the wrong text. A check that cannot fail on any instance of
the class it names is not a weak check, it is a vacuous one, and shipping it
would have moved the register's coverage claim without moving its coverage.
The re-declination is filed as a fresh bet below rather than closing the class.

### Rule 7 applied to this round — the declined oracles

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| ORACLE-DECLINED: a stale bare `` `DOC.md`:N `` locator, BARE-BOUNDS FORM — assert only that the cited line number exists in the cited document | round 24, re-declined round 27 | not built: measured against the six R26-5 defects it detects 0 of 6 — every one names a line that exists and holds the wrong text, so the check is vacuous on its own class; the useful half shipped this round as the line-window check instead; trigger: a finding whose defect IS an out-of-range line number, which this form would catch and the window form would not | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a stale locator carrying no quotation of its own, or one separated from its quotation by more than the glue allows — the three of six the window check does not reach | round 27 | not built: two of the three need the section resolver `citation_lint` has now declined three times, and the third needs a glue wide enough to manufacture findings; the limits are published in the tool's OUT OF SCOPE block so the green is not read as covering them; trigger: a third stale locator of these shapes after this round, or the section resolver landing | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a `RECALL_FLOOR` row that goes stale because the kit's prose legitimately changed, corrected by editing the row rather than by investigating the recall loss | round 27 | not built: distinguishing "the prose moved" from "the pattern's reach shrank" needs a judgment no tool in this kit can make, and the floor's value comes from being expensive enough to notice; trigger: a floor row edited in the same commit that changes the extractor, which is the shape that would hide a reach regression | **ORACLE-DECLINED** |

### The escape reading, and a conflict the arithmetic surfaced

**Not yet written here, and owed at round close:** this round has no timeline
row and no escape-rate row. Both are round-close artifacts and the
coordinator's, on the same rule round 26 recorded. The reading they should
carry is stated here so it is not re-derived later.

**R27-1 is an escape** by this register's own definition: `citation_lint`
existed from round 22, its stated subject covers exactly this class, and it was
green over the defect. This is not the round-20 shape — the defect was not
inside a check built this round, it was in shipped prose a four-round-old check
was pointed at. **R27-2 is a self-catch on this round's own new work**; the
closest precedent is R26-12, which counted a self-catch as an item with no
escape attributed. **The six R26-5 locators are not recounted**: module 04's
convention makes a declined-class finding a coverage gap attributed to the bet,
and the bet being resolved this round does not retroactively convert them into
escapes.

That gives round 27 **2 items, 1 escape (50.0%)** on the R26-12 reading, or
1/1 (100.0%) if R27-2 is excluded as own-new-work. Cumulative, computed by the
tool against both readings rather than by hand: **37/222 (16.7%) over 21
rounds** on the two-item reading and 37/221 (16.7%) on the one-item reading,
either way up from 36/220 (16.4%). The cumulative figure barely moves, which is
the point of publishing a denominator — one small round cannot swing it, and
the per-round ceiling alarm below is reacting to something the cumulative
number correctly ignores.

**The conflict, stated rather than resolved here.** Either reading puts the
latest round over `escape_rate.py`'s 35.0% per-round ceiling, and the tool
exits 1 on that condition, which CI runs and the `escapes` gate reads. **A
two-item round cannot fall below a 35% ceiling unless it has zero escapes** —
the smallest non-zero rate available at n = 2 is 50%. The ceiling has no
minimum denominator, so on a small round it fires on arithmetic rather than on
evidence, which is the exact small-tail noise this register already warns about
in the trend paragraph and at rounds 18 and 25. **This is a decision for the
owner's gate, not for a build lane**, and three shapes are available: give the
ceiling a minimum denominator below which it reports rather than fails; let a
round declare itself too small to rate, as rounds 1–6 already do with
UNCOUNTABLE; or accept the red and let the round close over an acknowledged
ceiling breach. Recording the choice matters more than which one is taken —
the wrong move is to enlarge the denominator until the number behaves, which
this register would then be unable to tell apart from an honest count.

**RULED (owner's gate, 2026-08-23): the first shape, with the floor derived
rather than picked.** The per-round ceiling arms only at
n >= ceil(100/ceiling) — 3 at the shipped 35.0% — because below that the
smallest non-zero rate is already over the ceiling and the gate measures
arithmetic, not learning. The floor is computed by `min_countable()` in
`escape_rate.py` from the ceiling itself, never configured: a knob would
invite tuning it until the gate stops finding things. Below the floor the
round still enters the cumulative numbers unchanged and the required line
carries **`state SMALL-N`** — chosen over "MEASURED-SMALL-N" because the
gate pattern alternates on MEASURED and would prefix-match that quietly; a
runner whose hand-written transcription of the pattern is not updated goes
red instead, which is the two-authorities design working. The rejected
shapes, with the owner's reasons on record: UNCOUNTABLE hides a real number
behind a word that means "unrecoverable", which this round's counts are not;
accepting the red makes a red CI mean nothing. Negative controls:
`escape:nc-xv` (a small round does not arm the gate; its numbers still enter
the cumulative rate; a round AT the floor is gated; a small CLEAN round is
SMALL-N too, so its green cannot claim a ceiling it could not have failed;
the pre-round-27 pattern refuses the new state word). The status board keeps
the cumulative rate on a SMALL-N round and renders the state word as a
literal suffix — hiding a fully measured number behind the word would drop
information from the glance. **The ruling's accepted residual, disclosed by
its review:** the floor makes the per-round gate partition-sensitive — the
same evidence split into sub-floor rounds exits 0 where one round of it
exits 1, and no check fires on a sustained sub-floor run; the cumulative
rate, trend line and per-run SMALL-N line are the compensating disclosure,
and their reader is a person. Stated in the tool's own SMALL-N block and on
the `escape:nc-xv` registry row as well as here.

---

## Round #28 — the capsule doctrine, and three defects a prose round found

This round shipped one document — `modules/08-collaboration/CAPSULE.md`, the
sync-capsule doctrine — from three hostile lane reports and a binding
corrections file produced the day before. No tooling was written and no check
was added, so every finding below is a prose or data defect, and the round's
own zero-escape reading is stated with its reasoning rather than left to be
read as a clean run.

**The framing decision that shaped the document, recorded because it reversed
an earlier claim.** An ancestry hunt ruled the capsule's governance doctrine
REDUNDANT-BY: append-only, supersede-in-place, authority-gated revision and
verbatim provenance are each established practice in at least two independent
professions, and the complete assembly exists in Architecture Decision Records,
already applied to AI agent context by published 2026 practitioner work and at
least one shipping product. A predecessor prior-art lane had described the same
doctrine as an absence in the field. That reading was correct about the
AI-artifact field it searched and wrong about the world. The document therefore
describes the doctrine as **imported**, names an ancestor in the same paragraph
as every doctrine claim, carries the ancestry table, and states the residual as
subject matter — professional practice governs records of decisions about the
work; this governs a record of decisions about the working relationship — and
as nothing larger.

| # | Finding | Disposition |
|---|---|---|
| R28-1 | **A shipped figure was stated as measured when it is an internal estimate.** `CONTEXT-ARCHITECTURE.md`'s sync-capsule paragraph said the owner *measured* the relational ramp at roughly 30% of the context window. The figure is one owner's observation on one workstation, uninstrumented. Grounding cost is an established and citable construct in the human-computer interaction literature; this magnitude is not measured anywhere either prior-art lane could find, and that negative finding itself rests on web searches rather than a database sweep. The word "measured" is the whole defect: it converts an estimate into evidence at no cost to the writer and at every cost to the reader. | **FIXED.** The sentence now says the owner *put* the ramp at roughly 30% and labels it, in bold and in the same sentence, an internal estimate from one owner on one workstation rather than an instrumented measurement. The same label binds `CAPSULE.md`, which repeats the figure once, under the label, in its unmeasured list. |
| R28-2 | **A shipped instruction contradicted the doctrine this round shipped.** The same paragraph told the reader to maintain the relational memory files "like any cache" and to **delete what goes stale**. The capsule doctrine is append-only: an entry is retired by being promoted into the durable profile or superseded in place, never deleted. Both sentences were in the tree at the same time, one of them in a document a walker reads early. **This round created the contradiction and is the one that has to own it** — the doctrine did not exist when the cache sentence was written, and a reader hitting both would have had no way to tell which was current. | **FIXED.** The instruction now reads as a governed record rather than a cache — append on a new confirmed pattern, supersede in place on a correction, retire only by promotion — and it points at `CAPSULE.md` for the governance in full and for what about the practice is unmeasured. |
| R28-3 | **SELF-CATCH: a stated count inside `checks-registry.json` went stale the moment this round added a document.** The `citation:window-normalisation` waiver reason argued that the check is worth more than a tautology because its equality is asserted "over all 48 SHIPPED DOCUMENTS" rather than over a literal the test wrote. That was true at round 27 and false the moment `CAPSULE.md` landed, making 49. Neither lint sees it: `count_lint` enumerates markdown documents and the registry is JSON, and the tool's own OUT OF SCOPE block already discloses that a count with no locatable target is skipped. **The reason field was arguing the check's value from a number that nothing checks.** | **FIXED, and fixed by removing the trap rather than by bumping the number.** The reason now asserts the equality over *every shipped document the lint enumerates*, records both counts and the round each belonged to, and names this finding. Bumping 48 to 49 would have left the same defect armed for the next document added. |

### Rule 7 applied to this round — the declined oracles

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| ORACLE-DECLINED: a stated count inside a NON-MARKDOWN shipped file — a `checks-registry.json` reason, a `kit.config` comment — going stale; candidate shape: sweep non-markdown shipped files for digit-plus-document-noun pairs and assert each against the citation lint's own runtime enumeration | round 28 (R28-3) | not built: `count_lint`'s three ways of naming a target are all markdown shapes (an introducer before a table or list, a trailing line noun after a fence, a cross-document section locator), and a JSON reason field has none of them. The only true source for "how many documents does the lint enumerate" is the lint's own runtime enumeration, so the check would assert a number against the tool that produces it — the self-referential shape `expectation_lint` already flags. The fix taken instead removes the number rather than checking it; trigger: a second stale count in a non-markdown file, or any stale count a reader acts on | **ORACLE-DECLINED** |
| ORACLE-DECLINED: two shipped documents giving contradictory instructions for the same practice; candidate shape: a keyword-pair sweep over a curated list of practice nouns (delete, retire, append, fold) flagging any two shipped documents whose sentences about the same noun carry opposing verbs, the flagged pair routed to a person for the meaning call | round 28 (R28-2) | not built: deciding that "delete what goes stale" contradicts "retire by promoting" is a reading of meaning, and no tool in this kit reads meaning. The kit's existing cover for the class is the module-README file contract and spec-side review, both of which need a person. Naming it here rather than claiming coverage; trigger: a third cross-document contradiction after round 26's and this one | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a number shipped without its provenance label — an estimate presented as a measurement; candidate shape: a provenance lint flagging any numeral within one sentence of "measured" or "observed" that carries neither a source locator nor an estimate label, checked against a maintained number-provenance table | round 28 (R28-1) | not built: a check cannot tell an estimate from a measurement without an authority saying which each number is, and building that authority means maintaining a table of every number in the kit and where it came from — the artifact the check was supposed to make unnecessary. The class is real and its cost is real; the honest state is uncovered and declared. Trigger: a second unlabelled estimate shipping, at which point the table is cheaper than the class | **ORACLE-DECLINED** |

### The escape reading

**Zero escapes, and the reasoning is published because an unexplained zero is
the shape this register distrusts.** All three findings are coverage gaps by
module 04's definition: no existing check covers a figure's provenance label
(R28-1), a contradiction of meaning between two documents (R28-2), or a count
inside a file no lint reads (R28-3). Each now carries a declined-oracle bet, so
a second sighting of any of the three classes is attributed to this round under
rule 7 rather than to the round that finds it.

**The alternative reading, stated rather than hidden — and, per the round's
review (NIT-1), stated completely.** R28-3 is a self-catch on the round's own
new document, and R28-2 is a contradiction this round itself created; the
own-new-work exclusion applied consistently removes both, so the fully
excluded alternative is 1 item, not 2. It sits under the derived denominator
floor and would publish `state SMALL-N`. Every reading gives 0.0%, because
none contains an escape. The three-item reading is the one in the table,
because it is the larger denominator on a zero-escape round and therefore the
*less* flattering of the available claims about coverage.

**Fix-pass addendum (post-review, coordinator-direct).** The round's
spec-side review returned APPROVE-WITH-PUNCH-ITEMS with worst finding MAJOR
— a rise over round 27's MINOR, read by the review as a coupling (the first
round to ship a kit document that is also a material in the program's own
pre-registered experiment) rather than build decay; the confound is now
registered in the experiment's pre-registration with both dispositions
pre-committed. All punch items fixed pre-commit, including: the one-screen
doctrine summary added to `CAPSULE.md`; seven aphoristic flourishes cut —
recorded as the **third firing of the prose-voice rule** (2026-08-20 ask,
2026-08-22 battery, this round), which trips the rule's own promotion
trigger in the program's failure-floor table, owner ruling queued; the
ancestry table's unverified chronology labeled; these three bet rows given
their candidate check shapes; and the kit README's module-08 row updated for
`CAPSULE.md` — that stale row is the same class as R28-3's family and is
recorded here as a fourth uncounted instance rather than a counted item,
because no covering check exists either way and recounting after review
would change denominators the review already verified. Disclosed, not
hidden.

**What this round does not establish.** A prose round with no new check cannot
lower the escape rate through learning; it lowers the cumulative figure
arithmetically, from 16.7% to 16.4%, by adding three clean items to the
denominator. The trend word flips from RISING to FALLING on the same
arithmetic. Both movements are the small-tail noise this section already warns
about at rounds 18, 25 and 27, and neither is evidence that the net improved.

---

## Round #29 — the front door: handing the reader the check

**This round was driven by the first read of this kit by a person outside the
program.** Every prior evaluation read in this register was an LLM persona,
labelled as one. This reader is a practising security engineer with about ten
years in vulnerability management and security operations. He read the
published material on his own time, at the owner's invitation, and returned two
sentences, verbatim:

> "it is a lot of AI writing to sift through which just hurts my eyes. and
> double check coverage for completeness with a manual validation check of
> claims against established tools."

**The entry-path data is the more useful half.** He skimmed `BLUEPRINT.md`
lightly and stopped; he read `COMPARISON.md` properly. Long-form prose was
filtered out before it was evaluated and the table was not. He then asked for a
manual validation of claims against established tools *after* reading the page
that classifies this kit's claims against named live artifacts. The table did
not fail to be found. It failed to persuade, because its rows are claims about
the AI-tooling landscape verified by an AI-run program that is itself in that
landscape. That is this kit's own thesis — a green produced by the party it
evaluates is not evidence — applied to this kit, and it is correct.

**What this instrument is and is not.** n = 1, self-selected, with a
long-standing personal prior about the owner's ideas that no document changes.
Nothing in the feedback evaluates the kit's ideas; by the owner's own reading
the reader did not get far enough to judge them, so the thesis here is
unexamined rather than rejected. It is also the first entry in this register
with **no prompt to publish**: the read was unprompted and self-directed, which
is what makes it independent and also what makes it unreproducible.
`docs/walks/` carries the prompt behind every other finding count in this
repository and cannot carry this one.

| # | Finding | Disposition |
|---|---|---|
| R29-1 | **`COMPARISON.md` asked the reader for trust on the one page whose whole job is to refuse it.** The page classifies eighteen load-bearing claims against named live artifacts and gives every source a verification tier, but it nowhere states **who produced the classifications**, and it nowhere hands the reader a procedure for checking a row. Its "What this page does not establish" section discloses that the audit ran once, on one day, by one reader — a limit of the *search*. It does not disclose the structural problem, which is that the auditor and the subject are the same party. The kit publishes its escape rate with exactly that disclosure attached in the same paragraph; the comparison page shipped without it. The first person outside the program to read the page found the gap on one reading. | **FIXED.** A "Verify these rows yourself" section now opens the page. It states the self-attestation problem in its first sentence, gives the per-row five-to-ten-minute procedure keyed to the verification tiers each row already carries, points the reader at the NO-MATCH-FOUND rows first as the rows that sound strongest and are worth the least, and routes corrections through the standing invitation the page already carried. **No claim was softened and no row was changed.** What was missing was the instrument, not the honesty, and adding honesty-flavoured prose instead of the procedure would have been the failure this round exists to avoid. |
| R29-2 | **The comparison page never stated its axis, so an absence reads as a verdict.** Every neighbour on the page is an agent-governance artifact — a tool that constrains, records or verifies what AI agents do inside a repository. The reader's "established tools" come from a vulnerability-management and security-operations seat, where the phrase means scanners, SIEM and compliance tooling. The page compares against none of those and never said so. An unstated axis makes the NO-MATCH-FOUND rows read as claims about the whole field rather than about one corner of it, which is a larger claim than the audit ran and a larger claim than the page intends. | **FIXED AS A DISCLOSURE, NOT AS A ROW-SET.** The new preamble names the axis, says why those neighbours were chosen (they make the closest claims), and states plainly that a VM/SecOps reader's tools were never compared and that their absence is not a verdict because those rows were never run. The row-set for that axis is queued and is out of this round's scope by the owner's ruling. Shipping the disclosure without the rows is the honest interim state and is labelled as one on the page itself. |
| R29-4 | **SELF-CATCH on this round's own new work (R26-12 / R27-2 precedent): the sources legend claimed three tiers and three classifications while the table uses four of each, and the new preamble pointed at it as complete.** The legend defined `[FETCHED]`, `[SEARCH-URL]` and `[UNVERIFIED]` while row C3 carries `[RECALLED-UNVERIFIED]`, and defined three classifications while C18 carries `COMPOSITION-STANDS`; the preamble written this round said the legend "defines the vocabulary in full", which was false at the moment it shipped. `count_lint` was correctly green — the stated counts matched the bullets present — so the defect was a complete-looking enumeration, not a stale number. | **FIXED.** The legend now defines all four tiers (including `[RECALLED-UNVERIFIED]` as the weakest, a lead only) and all four classifications (including `COMPOSITION-STANDS` as a claim about the assembly only), both counts corrected, and the preamble's pointer is now true. Counted as this round's fourth item. |
| R29-3 | **`README.md` routed a practitioner through prose to reach the three artifacts that are not prose.** The kit's most practitioner-legible artifacts — the escape table, the comparison page, and the published walk prompts — were each reachable only from inside a paragraph of long-form prose, and two of them only from paragraphs several screens down. The reader skimmed the long-form architecture document, stopped, and never reached the escape table at all. The kit's AI authorship was disclosed across several documents but nowhere in the first screen of the front door, which is where a 2026 reader's slop prior is actually formed. **This is a routing defect, not a content defect:** every artifact the finding asks for already existed and had existed for rounds. | **FIXED, NARROWLY.** An "If you read nothing else" block now sits on the front door's first screen, after the opening wedge paragraphs and before everything long-form, with one line each for the escape table, the comparison page and the walks directory, plus the AI-authorship statement in plain words. Whether it moves higher still is the owner's call at the gate. The larger front-door work the same finding argues for — a demonstration asset at the top, and a restructure of the long-form routing below — is OUT of this round by the owner's ruling and is not claimed here. What shipped is placement. |

### Rule 7 applied to this round — the declined oracles

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| ORACLE-DECLINED: a skim-test / front-door instrument — what a reader actually reaches in the first thirty seconds, measured | round 29 (R29-3) | not built: the check would have to model a reader, and no instrument in this kit reads a document the way a reader does. Every lint here reads a document for internal consistency against a locatable target — a quoted string against its source, a stated count against the block it names, a check's expectation against its subject — and none of them has an opinion about whether anyone gets that far. The mechanisable half (assert the front door's first N rendered lines link to each of the three named artifacts) is a check whose expectation is a list this round wrote, which is the self-referential shape `expectation_lint` flags, and it would go green on a block nobody reads. The honest state is uncovered and declared. Trigger: a second independent reader reporting they did not reach an artifact the front door routes to, or the demonstration-first restructure landing — which is the point at which a placement regression becomes cheap to introduce and expensive to notice | **ORACLE-DECLINED** |
| ORACLE-DECLINED: a page that verifies claims about third parties without disclosing who produced the verification; candidate shape: a presence check that a designated disclosure section exists and is non-empty on each page in a maintained list of documents making third-party claims | round 29 (R29-1) | not built: the presence of a disclosure section is checkable and its adequacy is not, and a presence check over one document is a check whose expectation is the sentence this round wrote — it would pass on a heading with nothing under it. Generalising it means maintaining a table of which shipped documents make claims about third parties, which is the artifact the check was supposed to make unnecessary; round 28 declined the provenance-label class for the same reason. Trigger: a second shipped page classifying external artifacts, at which point there are two instances and the enumeration is a real target rather than a list of one | **ORACLE-DECLINED** |
| ORACLE-DECLINED: an unstated comparison axis — a document whose absences a reader will take as verdicts; candidate shape: require every comparison or survey document to carry a named axis-statement section, checked for presence and non-emptiness against a maintained list of such documents | round 29 (R29-2) | not built: deciding that an absence *will be read* as a verdict is a reading of what a reader infers, and no tool in this kit reads meaning. The cover the kit does have is spec-side review and the standing correction invitation, both of which need a person. Trigger: a third finding whose defect is what a reader infers rather than what the document states — counting round 28's cross-document contradiction and this one | **ORACLE-DECLINED** |

### The escape reading

**Three findings, no escapes, and the zero is published with its reasoning
because this register distrusts an unexplained zero.** No check in this kit
covers any of the three surfaces. R29-1's surface is whether a page discloses
who produced its verification; R29-2's is whether an absence will be read as a
verdict; R29-3's is what a reader reaches before they stop. Every lint here
reads a document for internal consistency against a locatable target, and none
of the three surfaces is a locatable target. All three now carry a
declined-oracle bet under rule 7, so a second sighting of any of them is
attributed to this round rather than to the round that finds it.

**The counter-argument to the zero-escape classification, stated and then
answered (the escape-table row promises it, so it is paid here).** The
strongest version: round 28's own escape reading names spec-side review as
this kit's cover for meaning-class defects, `COMPARISON.md` passed a
round-26 spec-side review, and the self-attestation gap R29-1 describes was
on that page then and was not caught — a check existed, covered the surface,
and was green, which is the escape definition. The answer, and the reading
carried: this register has counted only mechanical checks as checks since
round 23, and reclassifying human review as a check would retroactively
convert most of the register's clean rounds. The zero stands on that
convention, with the convention named rather than assumed.

**The alternative reading, stated rather than hidden.** R29-2 and R29-3 are
both restatements of one defect — the front door does not hand the reader the
check — and folding them into R29-1 gives 2 items (R29-4, a self-catch on the
round's own new work, folds out under the same own-new-work exclusion), which
sits under the derived denominator floor and would publish `state SMALL-N`.
Every reading gives 0.0%, because none contains an escape. The four-item
reading is the one carried here, on round 28's precedent: it is the larger
denominator on a zero-escape round.

Readings were computed against a scratch copy of this ledger and are quoted
as the tool printed them; the timeline and escape-table rows were then
appended at the coordinator's close pass, and the entry-kind paragraph under
the timeline now names the human read as its own kind.

Reading A, four items:

```
ESCAPE RATE: 37/229 items (16.2%) over 23 rounds; latest 0/4 (0.0%); ceiling 35.0%; state MEASURED
```

Reading B, two items:

```
ESCAPE RATE: 37/227 items (16.3%) over 23 rounds; latest 0/2 (0.0%); ceiling 35.0%; state SMALL-N
```

**Two round-28 bets fired in this round's own review, recorded here per rule
7 (the R26-5 / round-27 precedent — a declined-class finding is a coverage
gap attributed to the bet's round, not an escape of the finding round; the
zero above is unchanged):**

1. **R28-2's bet (cross-document contradiction) FIRED — third instance.**
   The round's README block claimed `docs/walks/` holds "the prompt behind
   every finding count" while the same round's register prose stated the
   opposite, both in the tree at once. Fixed this round (the block now
   matches the walks README's own scoping). Build-or-re-decline is owed at
   the owner's gate.
2. **R28-1's bet (unlabelled estimate) FIRED — second instance.** The
   preamble shipped "it takes five to ten minutes" as fact; the figure is a
   charter estimate nobody has timed. Fixed this round (labelled an
   estimate). The bet's own candidate shape ("a numeral within one sentence
   of 'measured' or 'observed'") would NOT have caught this instance —
   neither word appears — so the class is wider than the declined check's
   reach, which the owner should weigh at the same gate.

**What this round does not establish, and the part worth reading twice.** The
cumulative rate has now fallen 16.7 → 16.4 → 16.2 across rounds 27, 28 and 29,
and no new check was built in round 28 or in round 29. Two consecutive prose
rounds moved the headline down by adding clean items to a denominator, and the
trend word goes to FLAT on the same arithmetic. **A number that improves while
nothing improves is a number an adopter should read with its denominator**,
which is the whole reason this table publishes one. Neither movement is
evidence that the net improved. The finding that drove this round came from
outside the net entirely — from a person, on a surface no instrument in this
kit points at, and the three bets filed above are the record of that rather
than a repair of it.

**Fix-pass addendum (post-review, coordinator-direct).** The round's
spec-side review returned APPROVE-WITH-PUNCH-ITEMS, worst finding MAJOR
(two): the preamble's stated procedure dead-ended on the rows it told the
reader to start with (fixed — two procedures, the sourceless rows made the
argument), and the README block shipped a universal walks claim its own
round's register prose contradicted (fixed — scoped to the walks README's own
coverage; the contradiction is R28-2's bet firing, recorded above). All punch
items fixed pre-commit, including R29-4's filing, the legend completion, the
counter-argument payment, the bet shapes, and two more prose flourishes cut —
the **fourth firing of the prose-voice rule**, recorded in the program's
failure-floor table where its promotion is already triggered. The review
also named the brake signal plainly: worst-finding severity has run MAJOR →
MINOR → MAJOR → MAJOR across rounds 26–29, with one root-cause class under
both of this round's MAJORs — a universal quantifier asserted over an
enumerable target nobody enumerated — found four times in four rounds and
declined as an oracle each time. The review's candidate check (extend
`count_lint`'s target-location from numerals to universal quantifiers whose
predicate is literal token presence) is at the owner's gate with the two
fired bets. Per the loop-termination doctrine, that severity pattern is a
redesign signal: no further prose round ships against these surfaces until
the owner rules on the quantifier class.

---

## Round #30 — the transplant, and the check the class finally bought

**Two instruments drove this round and neither was a walk.** Three cold
LLM-persona evaluation reads of the published kit, each required to end in a
verdict — ADOPT, PILOT or PASS — rather than in an opinion. And one **executed
increment**: the owner of a two-year-old internal AI advisory project, outside
this program and with no prior exposure to the kit, authorised a Level-1
adoption of the kit into it and one improvement carried out under the kit's
discipline. `docs/CASE-STUDY-INCREMENT.md` is the public account.

**The three verdicts were PILOT, PILOT and PILOT.** Nobody returned ADOPT and
nobody returned PASS. Each read named a runnable artifact as the reason — a
diagnostic that goes red on its own author's repository, an exit-code
contract, a switch labelled *make yourself fail* — and none named a paragraph.
All three bounced off the same surface: a 292 KB findings register, grepped
rather than read, by readers who were each looking for the same table inside
it. That is what the front-door work in this round answers, and it is why the
register now opens with that table.

**What the instrument is and is not.** Three reads, one increment, all four
performed by a language model running a written persona rather than by a
person. The increment met one repository, one language, one afternoon, and a
tree clean enough that four of the six collisions `EXISTING-PROJECT.md`
documents were never exercised. Every claim this round makes about
transplantability is bounded by that, and the case study states it twice.

| # | Finding | Disposition |
|---|---|---|
| R30-1 | **The front door spent its first screen arguing about novelty, and the readers it was written for stopped before reaching anything they could run.** All three cold reads converted on an exit code, and all three reported the same routing failure: the artifacts that persuade — the escape table, the comparison page, the walk prompts — were reachable only from inside long-form prose, and the register holding the first of them was three times the length of the front door. Round 29 fixed the placement of a routing block. It did not fix what the reader meets first, and the owner's ruling for this round said so plainly: make the human door more consumable without losing what is there. | **FIXED, by relocation rather than deletion.** `README.md` now opens with a short statement of what the kit is (three sentences and the rails line), then a worked demonstration quoted from the increment's own gate output, then a three-command quickstart, then the round-29 routing block, the module map and an honest status. Ten sections moved intact into `docs/` with a one-line pointer left in the routed index; the build lane's report carries the word-count parity accounting. Nothing was deleted. Every anchor into a moved section — in `COMPARISON.md`, `DECISION-BRIEF.md`, `QUICKSTART.md`, `ONBOARD.md`, `BLUEPRINT.md` and one tool docstring — was updated to name the new location. |
| R30-2 | **The register claimed "the prompts behind every walk are published under `docs/walks/`", which is false of entries 1–7.** Found by the build lane while writing the quantifier check, in the one document the check exempts. `docs/walks/README.md` states its own coverage and says entries 1–7 predate the loop; this sentence, one screen above the timeline, said otherwise. **This is the fifth instance of the universal-over-an-unenumerated-target class** and the second one in this program's own front matter. | **FIXED in place with a dated correction**, as this register's convention requires: the sentence is scoped to the seven adoption walks and three evaluation reads, the exclusion of entries 1–7 is stated, and the original wording is named rather than silently replaced. **The check built this round does not catch it**, because a findings register is exempt from both of `count_lint`'s layers as a document class — the exemption's own disclosed residual, arriving live. |
| R30-3 | **`count_lint` printed `clean - exit 0` over a run that located a target for 15 of 769 count phrases.** Reported by one of the cold reads, with the arithmetic done: 1.9% coverage, printed in green, using the word this kit reserves for a complete result. The kit's own state-word doctrine — PARTIAL exists because "the check did not run" and "the check passed" must never render alike — was not being applied to the kit's own lint. The reader called it his one substantive criticism of the kit's internals, and he was right. | **FIXED.** The summary line now carries a state word and a denominator, and `CLEAN` is printed only when nothing was skipped. `citation_lint` took the same treatment and prints the half it cannot measure on the line below its verdict. `expectation_lint` was audited and needed no change: it already prints its full denominator and every waiver on every run, and has no undisclosed skip. **The exit code deliberately did not move**, with the reason stated in the tool: over the claims it located the verdict is complete, and a lint that exits non-zero because a document contains English is a lint people learn to skip. |
| R30-4 | **`COMPARISON.md`'s C11 overclaimed, and a reader running the page's own procedure produced the counterexample.** The row asserted that no named artifact ships a last-fired column with a forced disposition, and called itself the cleanest unmatched claim in the kit. Firewall policy recertification tooling ships a last-hit date column, automated unused-rule reports and a forced disposition at recertification — two of the row's three properties, in a shipped named product. | **FIXED, and the provenance is the point.** C11 now carries the citation the reader supplied at the `[UNVERIFIED]` tier with its honest caveat, its claim narrowed to the one property that survives — zero demotions treated as itself a defect — and the retired sentence named. The preamble's list of rows carrying no source, the outright-versus-sub-claim partition and the tally paragraph were all corrected to match. **This is the first yield of the standing correction invitation, and the row says so.** |
| R30-5 | **Four Level-1 documentation defects that seven internal walks did not find.** Surfaced by the executed adoption: a render branch table whose three rows predict 6, 6 and 5 unfilled slots and enumerate no row for the adopter who correctly filled the tier names in the previous step (that adopter gets 1); a printed commit line omitting `.gitignore`, which Step 3 tells you to edit, leaving the ignore rule uncommitted with `doctor:l1-committed` unable to notice; and two render-step judgment calls the page never named — an empty `.claude/` left behind by the deleted seventh render, and the tool's deliberate abort on a leftover `.kit-new`. | **ALL FOUR FIXED in `LEVEL-1.md`**, each carrying the reason it was found. The branch table gains the subtraction rule rather than a fourth row, because the fourth case is not a step-1 branch. The commit line names `.gitignore` with the condition under which to drop it. Both judgment calls are stated where the render step is described. |
| R30-6 | **SELF-CATCH on this round's own new work (R26-12 / R27-2 / R29-4 precedent): the quantifier layer manufactured a finding against a correct sentence on its first live run, and swallowed a heading into a sentence on its first CI rehearsal.** The first: a published walk prompt holds a 400-word persona instruction in one fenced block; "executing every command as printed" sits deep inside it and a later clause quotes the word "done", and the layer read that quotation as the claim's predicate. The second: a page whose heading carries no full stop put the heading and the claim into one sentence, so the opening rule rejected a claim that does open its paragraph. | **BOTH FIXED BEFORE ANY COMMIT, and both are now registered controls** (`quant:mid-sentence`, and the paragraph-scoping rule the CI rehearsal forced). The narrowing is the count layer's own opening rule applied one level up: a universal is a claim about a target only when it is what the sentence is about. Same shape as `count:wrapped-command`, which the count layer's first live run forced in round 24 for the same reason — a checker that manufactures findings against correct text is worse than no checker. |

### The check this round built, and what it does not cover

Round 29's review named one root cause under both of its MAJORs — a universal
quantifier asserted over a target the writer could have enumerated and did not
— found four times in four rounds and declined as an oracle each time. It
recommended one narrow check and stated its own limits. That check is built.

- **`count_lint` gains a quantifier layer.** A universal (`every`, `each`,
  `all`) or a negative (`no`, `none of the`) plus a noun naming a target the
  tool already enumerates — a table's rows, a list's items, a fenced block's
  lines — where the predicate is the presence of a **literal token**, is
  asserted against every element of that target. The negative inverts the
  test. Fifteen controls, all registered under a new `quant:` family that the
  expectation lint recovers from the source; five of the fifteen exist only to
  stop the layer manufacturing findings.
- **Forced red first, and in CI both ways.** Round 29's F1 sentence over the
  shape of the table it quantified goes red on the three rows that carry no
  bracketed source; the same page with every row sourced must stay green, and
  CI asserts both directions.
- **What it does not cover, stated because a check whose limits are not
  published gets read as covering more than it does.** Round 29's F2 — "the
  prompt behind every finding count here" — names no enumerable target and is
  **skipped with its reason** rather than caught. That is still a change:
  before this round the sentence was invisible to every check in the kit, and
  it is now a disclosed skip inside a printed denominator. Written over an
  enumerable target the same claim is caught, and the selftest holds both
  halves so neither can be quietly moved. Partial cover, published as partial.
  A second limit found by this round's review and stated here: **the layer's
  motivating instance is uncovered in its own document.** Round 29's F1
  sentence, restored into the real `COMPARISON.md`, is skipped rather than
  caught, because that page holds two tables and the layer's location rule
  requires exactly one candidate target; every selftest and CI fixture is a
  single-table page. The check covers the class's shape, not the page that
  taught it the shape.
- **The layer's reach on this kit's own tree is one claim.** The run locates a
  target for exactly one universal in the whole repository, and that one is in
  the front door this round wrote. A layer that decides one claim across every
  shipped document is a narrow instrument (the exact counts — claims decided,
  skips, and documents — are printed on every run rather than stated here,
  which is the R28-3 lesson applied); the honest reading is that most
  universals in this kit's prose sit too far from anything enumerable for a
  lint to reach them.

### Rule 7 applied to this round — the fired bets, resolved

| Ruling (verbatim where possible) | Landed in | Enforcing check | Status |
|---|---|---|---|
| ORACLE-DECLINED, round 28: cross-document contradiction — one shipped document instructing the opposite of another. FIRED in round 29 as its third instance, and resolved here. | round 28 (R28-2), fired round 29 | **RE-DECLINED in the meaning-reading form, with mechanical partial cover now built.** Reading two documents for contradiction requires a reader of meaning, and no tool in this kit reads meaning; that half is declined again and the cover remains spec-side review, which is human-shaped. What changed is that the largest *mechanical* sub-shape of the class is now covered: round 29's own instance was a universal quantifier over an unenumerated target, and `count_lint`'s quantifier layer decides that shape where the target is enumerable and discloses it as a skip where it is not. The bet is therefore not re-declined empty-handed. Trigger, re-armed and tightened: a fourth instance whose two documents both make **enumerable** claims — the case where a mechanical check would have caught it and did not, which converts the declination into a defect of this ruling rather than a coverage gap. | **RE-DECLINED (partial cover built)** |
| ORACLE-DECLINED, round 28: a figure stated as fact when it is an internal estimate. FIRED in round 29 as its second instance, and resolved here. | round 28 (R28-1), fired round 29 | **RE-DECLINED, with the shape shortfall recorded rather than repaired.** Round 28's candidate shape was "any numeral within one sentence of 'measured' or 'observed'". The round-29 firing carried neither word — the preamble said the check is per-row and takes five to ten minutes — so **the declined check would not have caught the instance that fired the bet**, and that is the most useful thing this resolution records. The wider shape that would catch it is a provenance label on every numeral in published prose, which means maintaining a table of which numbers are measured; that is the artifact the check was supposed to make unnecessary, and round 29 declined the same construction for the same reason. Trigger, tightened to a third instance **with its source named**: a third unlabelled estimate shipping in public prose, at which point the class has fired three times and the table is cheaper than the class. | **RE-DECLINED (shape widened, not built)** |
| ORACLE-DECLINED, round 29: a skim-test / front-door instrument — what a reader actually reaches in the first thirty seconds, measured. **Both of its triggers fired this round.** | round 29 (R29-3), fired round 30 | Not resolved by this round, and not built. Its two triggers were a second independent reader reporting they did not reach an artifact the front door routes to, and the demonstration-first restructure landing. Three readers reported the first and the second landed in this round's own diff, so the bet has fired on both counts and is recorded here with **resolution owed at the owner's gate**. The mechanisable half is unchanged and remains narrow: assert that the front door's first N rendered lines link to each of the three named artifacts. It is cheaper than it was, because the front door is now short enough for N to be a defensible number rather than an argument. | **FIRED — resolution owed** |
| ORACLE-DECLINED, round 30: a universal claim written inside a findings register, which both lint layers exempt as a document class. | round 30 (R30-2) | not built. The exemption exists because a register records what a claim USED TO BE beside its correction, so checking those against the fixed tree asks the wrong question; narrowing the exemption to claims about the current tree needs a reader who can tell a historical quotation from a live assertion. Candidate shape, stated so it can be argued with: check quantifier claims in a register's **front matter only** — the prose above the first finding table — where nothing is historical by construction. Trigger: a second live universal found in register front matter, at which point the front-matter restriction is a real target rather than a boundary drawn around one defect. | **ORACLE-DECLINED** |
| ORACLE-DECLINED, round 30: a comparison row's claim about the world, checked against the world. | round 30 (R30-4) | not built, and not buildable inside this kit. A NO-MATCH-FOUND verdict is a claim about a search, and no check in this repository can run that search or judge its result. The cover that exists is the published per-row procedure and the standing correction invitation, which produced this round's correction on their first real use — an instrument with n = 1 and a person in the loop. Trigger: a second reader-supplied correction, at which point the useful mechanical artifact is not a check on the rows but a record of who checked which row and when, and that is a ledger rather than a lint. | **ORACLE-DECLINED** |
| ORACLE-DECLINED, round 30: the Level-1 render branch table's predicted slot counts, checked against a real render run. | round 30 (R30-5) | not built, and the candidate is a real one: render into a scratch repository once per branch of Step 1's decision, and assert that the tool's printed unfilled-slot count matches the row the table predicts for that branch. `adoption_smoke.py` already scaffolds throwaway repositories and already performs a mechanical adoption, so the machinery exists and this is a phase rather than a tool. Declined this round on scope — it is a build with its own review, and this round already shipped a check. Trigger: a second defect in a predicted-output table anywhere in the adoption path. The class is "a document predicting a tool's output", and this is its first instance. | **ORACLE-DECLINED** |

### The escape reading

**Six findings, no escapes, and this zero is more expensive to state than the
last two.** Taken one at a time:

- **R30-1** is a routing defect on a surface no instrument in this kit points
  at, and round 29's bet against exactly that class fired here. Under rule 7's
  accountability arithmetic a declined-class finding is a coverage gap
  attributed to the bet's round, not an escape of the finding round.
- **R30-2** sits on a surface both lint layers exempt by design, with the
  exemption's residual disclosed on every run since round 24. No check covered
  it, and the one built this round still does not.
- **R30-3** and **R30-4** were found by the round-30 recon reads — LLM
  personas this program ran with zero context, not people outside it. Nothing
  in this kit reads a tool's verdict vocabulary against its own coverage, and
  nothing in it can check a claim about the world.
- **R30-5** was found by an adoption on a host this program does not maintain.
  `adoption_smoke.py` performs `QUICKSTART.md`, not `LEVEL-1.md`, and no check
  compares a document's predicted output to a real run.
- **R30-6** is a self-catch on the round's own new work, which by the round-20
  precedent is not an escape: a defect in a check built this round had no
  pre-existing check to escape.

**The counter-argument, stated and then answered.** The strongest version:
this round found the fifth instance of a class the program has been paying for
since round 26, and it found it in its own front matter while building the
check for that class. If the class is that persistent, the argument runs, then
something in this kit should have been catching it by round 30, and calling
every instance a coverage gap is how a register avoids ever moving its own
number. The answer, and the reading carried: an escape in this register is a
check that existed, covered the surface and was green. Until this round no
check covered the class at all, which is the definition of a coverage gap, and
rule 7 has attributed the class to its declining rounds each time rather than
letting it go unowned. What the counter-argument does establish, and it is
recorded rather than deflected: **from round 31 the excuse is gone for the
shape the check covers.** The check exists now, its subject is stated, and
the next instance on an enumerable target is an escape. The bound on that
sentence, per this round's own review: the class has so far recurred mostly
on surfaces that are not tables, lists or fenced blocks — directories,
corpora, evidence bases — and those remain outside the check's reach, so a
recurrence there is still a coverage gap, disclosed in advance rather than
argued after.

**The alternative reading, stated rather than hidden.** R30-6 is a self-catch
on the round's own new work; folding it out under the own-new-work exclusion
gives 5 items, which is still above the derived denominator floor of 3, so the
gate stays armed and the state word does not change. Both readings give 0.0%,
because neither contains an escape. The six-item reading is the one carried
here, on the round-28 and round-29 precedent: it is the larger denominator on
a zero-escape round.

Both readings were computed against scratch copies of this ledger, created
under a temporary directory and deleted after the run, and are quoted as the
tool printed them.

Reading A, six items:

```
ESCAPE RATE: 37/235 items (15.7%) over 24 rounds; latest 0/6 (0.0%); ceiling 35.0%; state MEASURED
```

Reading B, five items:

```
ESCAPE RATE: 37/234 items (15.8%) over 24 rounds; latest 0/5 (0.0%); ceiling 35.0%; state MEASURED
```

**What this round does not establish.** The cumulative rate has now fallen
16.7 to 16.4 to 16.2 to 15.7 across rounds 27 to 30, and three of those four
movements are denominator growth on rounds that built no check. Round 30 built
one, and a check built after the findings cannot retroactively catch them, so
this round's fall is arithmetic exactly like the last two. The transplant is
one host, one language, one afternoon and a language-model adopter: evidence
that the documents survive contact with a repository they were not written
for, and not evidence that they survive contact with a second one. The three
cold reads were three language models, which is the same instrument limit
every finding count in this register carries.

---

### Round #30's fix-pass addendum (post-review, coordinator-direct)

The round's spec-side review returned APPROVE-WITH-PUNCH-ITEMS, worst
finding MAJOR (three), and stated in the convention's required words that
its worst finding was again in the quantifier class — the sixth instance,
on the front door. All punch items were fixed before the commit:

- **The independence claims now agree across all four surfaces** (the case
  study, `BLUEPRINT.md`, the front door, and this register): the brownfield
  host is the same owner's project, built before this program and never
  governed by it; the independence is in the zero-context agents, not the
  host; and no surface says "readers outside the program" about
  program-run persona reads. This alignment is flagged at the owner-preview
  gate, because the owner ruled on naming and the review found the
  independence wording was the load-bearing half.
- **The walks claim was made true rather than weakened**: the three
  round-30 recon prompts are published (`docs/walks/read-30-recon-*.md`,
  paths redacted), the walks README's coverage table carries entry 30, and
  the front door's evidence sentence now enumerates every instrument —
  walks, persona reads, the human read (no prompt to publish), and the
  increment.
- **The quantifier layer took the review's precision findings**: no-verb
  quantifier sentences are recorded as skips instead of silently excluded
  (the printed denominator grew from 1,371 to 2,242 and coverage fell from
  1.4% to 0.8% — the honest direction); the adjective window landed with
  its own registered control (`quant:adjective`, selftest 43 → 44); the
  exclusion rationale's direction word was corrected; and the layer's
  motivating instance being uncovered in its own two-table document is
  stated in the what-it-does-not-cover list above.
- **`expectation_lint` joined the state-word family** (`PASS - N registry
  entrie(s) checked, 0 self-referential`), with `adoption_smoke` phase 11
  and `QUICKSTART.md`'s expected-output line updated to match.
- **Eight prose flourishes cut** — the fifth firing of the prose-voice
  rule, in the round that executed its promotion, logged in the program's
  failure-floor record. One review NIT (a narrower-than-true redirect the
  review located in `QUICKSTART.md`) was not located by the fix pass and is
  carried openly to the quest report for the reviewer's line reference.
- The escape reading's "from round 31 the excuse is gone" was bounded to
  the shape the check covers, per the review's residual.

### Round #30's second fix-pass addendum — the owner-preview edit pass

At the owner-preview gate the owner rejected the committed front door's
shape ("what am I even looking at here?") and ruled a reshape: orient
first, then route, then demonstrate, with the audiences served in order
and not labeled. The reshape was reviewed by a second spec-side review
(same convention: charter + owner rulings + diff, no implementer report),
which returned APPROVE-WITH-PUNCH-ITEMS, worst finding MAJOR (six). All
punch items were dispositioned before the commit:

- **The quantifier class's seventh instance**: the reshape's claims-audit
  door widened "every load-bearing claim" to "each one". Restored. The
  same door bullet also promised commands the section does not contain;
  deleted.
- **The pass over-added**: the demonstration was stated three times in
  twenty lines and the quickstart still carried the door paragraph the
  new door section superseded. Four of the six MAJORs resolved by
  deletion; the fix pass removed more lines than it wrote.
- **The deident gate fired in-pipeline**: the chartered pre-release scan
  found six hits sitting in the committed round-30 recon prompts — an
  internal tier codename (three) and the public hosting address (three).
  Redacted with disclosure at the point of elision; the walks README's
  redaction table gained rows for both. Not an escape: the check that
  exists for this class caught it at the position it is chartered to run,
  before anything synced.
- **The recon prompts' host description** (product category, runtime
  stack, repository layout) exceeded the release's ruled generic form and
  is now redacted as `<HOST-DESCRIPTION>`, disclosed on each page and
  defined in the redaction table. Coordinator's disposition at the
  deident gate; the owner can loosen it at the preview gate at the cost
  of one commit.
- **The walks README counted ten runs where its own table two screens up
  lists thirteen.** Pre-existing at the round-30 commit, corrected. No
  check covered it: the runs are recorded in private program records the
  quantifier layer cannot enumerate, so this is not an escape but a
  recorded instance of the R28-2 class (cross-document contradiction,
  RE-DECLINED above) — a data point against that bet's re-declination,
  not a resolution of it.
- **One coined idiom cut** ("earns a slot") — the prose-voice family's
  sixth firing, and the first against the owner's same-day feedback that
  repeated stock idioms are an AI-writing fingerprint. One MINOR
  (unmeasured reading-time figures stated bare, second instance) FILED
  as a data point toward the R28-1 third-instance trigger, per that
  bet's standing re-declination.

## Open — what genuinely remains

- **No human has walked `QUICKSTART.md` end to end.** Every finding count in
  this register comes from an LLM persona, and the 90–120 minute budget is a
  sum of per-step estimates reconciled against persona walks, not a
  human-factors measurement. Publishing the prompts (`docs/walks/`) makes the
  method checkable and the study reproducible; it does not make it independent.
  A human adoption walk is on `ROADMAP.md` and is not on record.

- **The Level-1 checks judge document SHAPE, not content, and the path's
  30–45 minute figure is unmeasured.** `kit_doctor.py --level1` reads whether
  the six documents exist, are rendered, are committed and carry the two
  answers Level 1 asks for. A ledger with a correct header and no rows passes
  every one of them, and so does a profile whose observations are wrong. The
  green line prints that limit on every run rather than leaving it here. One
  smaller residual in the same area: `LEVEL-1.md`'s budget is a sum of per-step
  estimates by the maintainer, not a walk anyone timed. (The default diagnosis
  still reports ATTENTION against a Level-1 tree — it reads a runner and a
  settings file that level does not install — but it no longer leaves the
  reader there: when it finds Level-1 documents, no runner and no wired hook,
  it prints a line naming `--level1` above the verdict.)
- **`modules/07-ci/verify.yml.template` has never been executed with real
  slots.** Placeholders only an adopter can fill. Unproven, labelled so in its
  own README.
- **`.github/workflows/kit-ci.yml` cannot be proven locally.** It is verified
  by pushing and watching. Until then "host-agnostic" rests on dependency-free
  Python, a path-hygiene pass, the pwsh block executed live by phase 9, and
  selftests that pass here.
- **`statusline.ps1.template` was proven three passes ago and not since.** It
  is unchanged; `tools/statusline.py` is the variant under active test and the
  one module 05 recommends.
- **`--runner` and `--plant-f1` work only on an UNADAPTED runner.** Both drive
  the scaffold by renaming `example_unit` and deleting `example_lint`, so a
  runner whose example gates have already been replaced aborts with "update
  this script". Loud, not silent — and deliberately not fixed: adopted-runner
  support is a feature, and this was a fix pass.
- **Phase 9 walks the QUICKSTART's *commands*, not its *prose*.** A step whose
  explanation is wrong while its commands still run will pass. Fourteen walks in,
  prose is where nearly every finding comes from — an argument for the next
  reader, not against the check. Walk 11 narrowed the gap once: the walk now
  reproduces the *state* a reader's repository is in (an edited `kit.config`
  carried from Step 6 to Step 9) rather than only the commands, which is how
  F-1 escaped three passes in a row.
- **The expectation lint cannot see an unregistered check.** Narrowed for two
  families now — the hook fixtures against `hook_fixtures.py` and the doctor's
  checks against `kit_doctor.py`, both directions — but everything else still
  depends on the author adding a row. Waived in the registry, in the open.
- **Point 3 of the hook is a heuristic too, the durable fix is not built, and
  NO COMPLETENESS IS CLAIMED.** Its covered list grew twice in one week and the
  second round found ten forms after three persona reads had been through the
  first.
  Still open and silent: a nested shell (`sh -c 'git add -A'`), a backslash
  line continuation, backtick command substitution (excluded on purpose — a
  backtick code span in a commit message is commoner than the substitution
  form), `xargs git add`, an alias, a command built at runtime, a blanket flag
  after a quoted argument, and any script the command invokes. Judging the
  *index* catches all of them, and a PreToolUse hook cannot do it — it runs
  before the command. The right home is a git `pre-commit` hook, and none
  ships. Compensating pair, stated wherever it is relied on: the pattern, the
  sweep list the gate prints on a deny, and `kit_doctor.py`'s dirty-paths
  check. Widening also bought a false-deny direction — `^[ \t]*` matches an
  indented occurrence inside a heredoc or a multi-line commit message — taken
  deliberately, because a false deny is loud and fixable. An earlier version
  bought a much worse one by using `\s` as its token separator; see R17-5.
- **Point 4 of the hook is a heuristic and cannot be made otherwise by a
  string matcher.** Case folding on a case-insensitive filesystem, `cd` then a
  relative path, and symlinks or junctions are all silent-allow directions.
  Disclosed in `touches_protected()` and in the module docstring; measured for
  the host you are on by `doctor:protected-case`. Not fixed by folding case,
  because that would be wrong on Linux.
- **The cert-green token is unsigned and unsignable at this privilege level.**
  Anything able to write a file can mint one. Labelled in four places
  including inside the artifact; see round #17 for the keying analysis. If your
  harness ever runs agents under a principal that cannot read the owner's
  files, the HMAC becomes worth building and the analysis flips.
- **The kit ships no `docs/ORACLE-<gate>.md` pages of its own**, so
  `kit_doctor.py` reports `ATTENTION` against the kit's own checkout for all
  four of its gates. Correct rather than broken — two of the four are the
  example gates QUICKSTART tells you to delete — but it means the kit ships no
  *filled* worked example of `ORACLE-WORKSHEET.md`, which is the artifact an
  adopter would most like to copy. Recorded, not built.
- **`verify.py --mint-cert-token`'s write path is exercised only by a
  certifying run.** Its refusal on a non-PASS verdict, its payload and its path
  resolution are all covered by `--selftest`; the four lines that resolve HEAD
  and write the file cannot run while the judge surface is dirty, which is by
  construction the state of a tree that has just changed the runner. The first
  green certification after this round is what proves them.
- **The statusLine command has no startability check** (hook commands do). A
  mis-pathed board fails silently — observability, not enforcement. Fix shape
  recorded in the release-walk section above.
- **Point 1 of the hook is a heuristic** — counting after comments and string
  contents are blanked. Three silent-false-allow directions were closed in
  round #17 (a URL in a string literal, a regex literal with escaped slashes, a
  JS private field). What remains, and every item is a **silent false allow**:
  a `#` that is neither a comment nor a private field (`const c = #fff`); a `/`
  in expression position that is really division after a keyword the scanner
  does not know; an `agent(` written inside a template-literal interpolation;
  and a `model:` in a data structure that is not a spawn. The single false-deny
  direction is an unterminated quote. All of it is in the scanner's docstring.
  A parser is the real answer and is out of scope for a gate.
- **~625KB of mostly text** (624,761 bytes, 51 tracked files, no binaries)
  measured on the walk-11 errata tree, 2026-08-20 — well above the original
  ~150KB guidance. A deliberate trade: the reasoning travels with each template.
  **This number moves with every errata pass** (it was ~525KB / 50 files when
  first recorded, and 585,001 bytes at `641b392`): it is a measurement at one
  commit, not a budget. Re-measure with `git ls-files` rather than trusting the
  figure.

### Whose settings file? — the team story (walk 11, F-3 and F-7)

**The kit is written for one owner and one orchestrator seat, and the wiring
assumes it.** Measured on a second machine: rewrite the absolute paths in the
committed `.claude/settings.json` to a plausible teammate's root and you get
three `UNSTARTABLE:` lines, `HOOK NOT ARMED`, and
`VERIFY: FAIL — RED: judges, hooks`. The file is required to hold absolute
paths (a hook that cannot start enforces nothing), is committed, and is inside
`JUDGE_PATHS` — per-machine, shared, and judged at the same time. Every
recovery available today costs something: edit it locally and the `judges` gate
stays red; edit and commit and the first developer breaks.

Four more single-seat assumptions travel with it, none of them wrong and none
of them decided for a team: one `docs/collaboration-profile.md` filename (the
name the rules file names) against module 08's advice to run the interview per
person; one `RATIO_CEILING` with no guidance on aggregating several people's
ratios; one `OWNER_ROLE` that several rules bind decisions to; and a cert-green
token that is gitignored and therefore per-machine by construction — the safe
direction, but unstated.

Why it is recorded rather than closed: this is **design work, not errata**.
Deciding it badly is worse than leaving it open, and the decision belongs to a
team that has one.

**Fix shape, when someone wants it:** generate `.claude/settings.json` from a
template plus per-machine values (the kit's own `.gitignore` already names
`.claude/settings.local.json` for the overlay half), and then rule explicitly on
whether the *generated* file stays inside `JUDGE_PATHS` — a generated file that
is judged reintroduces the same problem one layer up. Everything else in the
config split already works for a team: `kit.config` / `kit.config.local` is
documented in both directions, and a second clone certified green with no
`kit.config.local` at all.

Until that exists, README says "any stack and any model" and names team
adoption as undocumented, and QUICKSTART Step 4 carries the measured
consequence under "One machine per settings file".

### The resume wiring in CONTEXT-ARCHITECTURE §6 is not shipped (walk 11, F-4)

`CONTEXT-ARCHITECTURE.md` §6 describes three hooks in shipping-grade detail —
**SessionStart** (capped resume brief, ASCII-safe JSON, liveness markers),
**PreCompact** (the two-hop disk relay, with the measured finding that
PreCompact output cannot carry `additionalContext`), and a **handoff
PreToolUse** gate that denies subagent writes under the reports tree. **The kit
ships none of them.** The strings `SessionStart` and `PreCompact` appear in no
module, template, settings file or tool, and `hook_model_gate.py` has no
reports-tree branch.

The content is good and was paid for on the reference build; what was missing
was the label. §6 now opens with a NOT SHIPPED banner in the style module 07
uses for `verify.yml.template`, BLUEPRINT's diagram edges carry the flag, and
the forward references in §2–3 say the hook does not exist.

**Fix shape, when someone wants it:** each hook is small — the SessionStart
brief is a read of the newest checkpoint plus a hard character cap; PreCompact
is a write of one gitignored state file plus a liveness marker. What is not
small is the fixture table §6 itself demands: negative controls, a dead-man
fixture, an encoding regression, and for the handoff gate a fixture *pair*
submitted from both the subagent and operator sides. Build the fixtures with the
hook or the kit gains a control it cannot prove.

### No checkpoint template ships (walk 11, F-5)

The rendered rules file opens with `ON RESUME: read the newest
{{CHECKPOINT_GLOB}} FIRST`. On day one there is no such file: **no module ships
a checkpoint template, no QUICKSTART step writes one, and no check notices its
absence** — while module 04 ships four skeletons for lower-traffic documents.
The shape contract exists as prose in the governance template itself (four
clauses, ~90 lines) and in `CONTEXT-ARCHITECTURE.md` §3.

Labelled rather than built: the template line now says the first checkpoint is
written at the first stage close, and QUICKSTART Step 6 says the same on the
adopter's path. That makes the instruction true; it does not make the artifact
exist.

**Fix shape, when someone wants it:** a `CHECKPOINT-TEMPLATE.md` in module 01
with the four clauses as headings and one worked example, plus a stage-close
checklist line that names it. Cost is small; the reason it was not done in an
errata pass is that a new shipped template disturbs the slot registry and the
smoke's phase-10 counts, which is a change to checked material rather than to
prose.

---

**Meta-lesson, fourteen walks in.** Every walk found something the previous
layer missed, and each fix added a check that makes that class loud.
Walk 7 (release audit) found three, all one class, now a lint. Walk 8 found one
more — a detector that skipped most of its subjects while reporting a green
count — and its fix makes the check state its own coverage. Walk 9 found a scan
that certified a tree it had not read. Walk 10 found the general form: **a
load-bearing instruction in prose beside a checkpoint that measures something
else**, and the fix pattern is to move the instruction into the checkpoint.

Walk 11 found the next layer out, and it is a different shape. Its findings are
not silent greens; they are **true sentences about the reference build printed
as if they were true about this kit** — hooks described but not shipped, a
resume anchor with no artifact, a team claim with one seat behind it. The class
is *unlabelled provenance*, and no check catches it, because every sentence
involved is accurate about something. The countermeasure the kit already owns is
module 07's practice of labelling the one unproven file loudly; walk 11's errata
applies it to three more places. Walk 13 confirmed the hands-on walk now runs
clean end to end; its six findings were all in the meta layer — this register's
own bookkeeping and cross-module attributions — which is where walk 11's class
predicts they would be. (Walk 12 had found the last in-walk defects: six, led
by the one template artifact no checkpoint reached.)

There is also a rework signal worth naming: walk 10's S3-F1 was introduced by
walk 9's K-3 fix, and walk 11's F-1 was introduced by that chain. Three
consecutive errata passes each broke the same printed commit line in a new way.
Phase 9 walks the commands, and the commands kept passing, because the walk's
scaffold did not have the state a reader's repository had. That is why walk 11's
fix changes the *walk* as well as the document: the smoke now edits `kit.config`
at Step 6 and certifies at the end of Step 9, the way a reader does.

The kit's own central claim, demonstrated on itself: **a suite written by the
author tests the author's mental model.** Only somebody else's hands find the
gap between the model and the artefact. The durable fix is never the patch — it
is the check that makes the class loud, and where possible one that walks the
*user's* path rather than the author's.
