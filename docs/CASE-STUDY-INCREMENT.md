# Case study — one increment on a project the kit had never touched

**What this is.** In August 2026 the kit was pointed at a two-year-old
internal AI advisory project, written in Python by the same owner who
maintains this kit, but built before this program existed, maintained
outside it, and never previously governed or read by it. The independence in
this study is in the AGENTS, not the host: three cold reads by LLM personas
with zero context evaluated the kit and the host and each returned a
verdict, and a fourth agent executed the work. **That fourth agent was not
zero-context**: its prompt was built live around the three reads' consensus,
so it began with their distilled conclusions about both trees. It had no
program context, which is a different and weaker claim. The owner
authorised one increment: adopt the kit at Level 1 by following its
documents as written, and execute exactly one improvement under that
discipline. This is not an independent-adopter study, and it does not claim
to be one; that limit is restated at the end.

This page is the public account of what happened. Every figure in it is quoted
from the program's records of those runs, or labelled an estimate. The host is
described generically throughout, at the owner's instruction; it is not named,
no repository is linked, and paths are redacted where they would identify it.

**What this is not.** It is not a benchmark, not a customer story, and not
evidence that the kit works generally. The section at the end states the
limits, and they are substantial: one repository, one language, one afternoon,
and the adopter was a language model rather than a person.

---

## 1. The three reads

Three lanes read the published kit cold — no prior contact with the kit — and
each was required to end in a decision rather than an opinion: **ADOPT**,
**PILOT**, or **PASS**. Each was also required to read the host and name the
first three things it would do there.

**They were not uncoached, and the prompts are published.** Each lane's charter
opens with the program's own tiering rule, its halt authority, its
out-of-bounds fences and its byte-handoff contract — three shipped kit
mechanisms — immediately above the line "YOU KNOW NOTHING about this program."
Each also carries the instruction "Every number sourced or labeled an
estimate", which is this kit's own conduct doctrine applied to the evaluator
before the evaluator reads the kit. The prompts are at
`docs/walks/read-30-recon-principal.md`, `read-30-recon-presales.md` and
`read-30-recon-secops.md`; read them beside this section rather than after it.

Each read was performed by a **large language model running a written
persona**, not by a person. That is the same instrument limit every adoption
figure this kit publishes carries, and it applies here without exception.

Three reads, three verdicts:

| The seat | What decided it | Verdict |
|---|---|---|
| a principal consultant who evaluates AI-governance tooling for regulated clients | the kit's own diagnostic returned ATTENTION on the kit's own repository, named the defect class — gates that cannot fail — and printed the step that fixes it | PILOT |
| a pre-sales solutions architect in cybersecurity | the exit-code contract, and a negative control that turns a green check red without editing a file in the repository | PILOT |
| a vulnerability-management and security-operations engineer of ten years | one command that makes the kit's own adoption gate fail on purpose, exit 2, printing that the run certifies nothing | PILOT |

Nobody returned ADOPT and nobody returned PASS.

### What they converged on, and what the prompt asked for

*[Rewritten in round 32 (R32-2), from an adversarial hostile-reader lane. This
section was headed "What they agreed on, unprompted" and reported the
convergence as independent. The prompts that produced it are published four
directories away in this same tree, and read beside the claims they falsify the
word "unprompted". The findings below are the ones that survive being read
against the instructions.]*

**The steering, stated first.** Three of the convergent observations were asked
for in the prompts:

- The ten-minute framing came from the prompts.
  `docs/walks/read-30-recon-principal.md`:45 asks the lane for "in your first
  ten minutes, where you bounced".
  `docs/walks/read-30-recon-presales.md`:38-39 asks for "Include your
  first-ten-minutes front-door path".
- "Bounced" is the prompts' own word, in two of the three charters, and it is
  the word this page used to report as a convergent observation.
- The instruments-over-prose reading was an instruction to at least one lane.
  The security-operations persona is defined as "allergic to walls of confident
  AI prose" (`docs/walks/read-30-recon-secops.md`:16-17); the same page tells it
  to "trust output lines over prose" (`docs/walks/read-30-recon-secops.md`:28)
  and that green "for you that means an output line, not a paragraph"
  (`docs/walks/read-30-recon-secops.md`:48). A lane instructed to prefer output lines to
  prose, and then reported as having independently concluded that instruments
  beat prose, is the instruction restated as a finding.

**What survives the instructions.** Three things the prompts did not ask for:

- **The verdicts.** No charter named a target verdict or ranked the three
  options. Three PILOTs, no ADOPT and no PASS, is the reads' own output.
- **The specific artifacts named.** Each lane named a *different* runnable
  artifact as decisive — the doctor's ATTENTION on the kit's own repository,
  the exit-code contract with a negative control, and the adoption smoke run
  that exits 2. The prompts asked for an output line; they did not name which.
- **All three bounced off the same surface.** The findings register was, at the
  time, 292 KB. Each read grepped it rather than reading it, and each was
  looking for the same thing inside it: the escape-rate table. One of them
  wrote that if the escape table is the reason to adopt, it is in the wrong
  container. The prompts asked where the lane bounced; they did not name the
  register, and the register is not the surface a charter would have guessed.
  That finding is the reason the register now opens with that table and the
  reason the front door was rebuilt around a demonstration.

**A counter-reading, recorded because it is the one a hostile reader reaches
unaided.** Convergence among personas of the same model family is a documented
property of the instrument rather than evidence about the subject: Xiao,
Zhang, Yang, Ma, Xuan and Huang, *The Chameleon's Limit: Investigating Persona
Collapse and Homogenization in Large Language Models* (arXiv 2604.24698,
2026-04-27), report that "agents each assigned a distinct profile nonetheless
converge into a narrow behavioral mode, producing a homogeneous simulated
population", and that "behavioral variation tracks coarse demographic
stereotypes rather than the fine-grained individual differences specified in
each persona" [FETCHED: `https://arxiv.org/abs/2604.24698`]. All three reads
ran on one model family, which `docs/walks/README.md` records. The agreement in
this section is therefore reported as an observation about three runs of one
instrument, not as triangulation across independent ones.

**Two of them declined the full kit for the same disclosed reasons**: no
multi-seat story, no integration with the assurance tooling their clients are
audited against, and an evidence base of language-model personas rather than
people. All three of those limits were already published; none was
discovered. The documents had stated each reservation before the readers
raised it, which is the outcome an honest disclosure is for.

### A commissioned read narrowed a published claim

*[Rewritten in round 32 (R32-2), from an adversarial hostile-reader lane. This
section was headed "One of them corrected a published claim" and closed on
"That is the first time the standing correction invitation has produced
anything." Both statements overstated what happened, in two independent ways
recorded below.]*

**It was a directed task, not an open invitation taken up.** The
security-operations charter instructs the lane to test "whether the
verify-these-rows-yourself comparison page holds up when you actually try a
row (try at least one sourced row and one NO-MATCH-FOUND row and report what
happened)" (`docs/walks/read-30-recon-secops.md`:39-42). The NO-MATCH-FOUND
rows are the ones `COMPARISON.md` itself names as the cheapest to attack. The
program commissioned the attack and pointed it at the row class. A standing
invitation and a commissioned task are different instruments, and this kit's
own doctrine is that they are not to be blurred. **The standing correction
invitation has not yet produced anything**, and this page previously claimed
otherwise.

**What the lane produced is a lead, not a citation.** The counterexample —
firewall policy recertification tooling shipping a last-hit date column,
automated unused-rule reports and a forced disposition at recertification —
was named from the persona's own working knowledge. No page was fetched and no
search index was consulted. `COMPARISON.md`:147 carries it under the
`[UNVERIFIED]` tier with the instruction to "treat it as a lead to check rather
than as a citation"; this page previously dropped that tier label and
stated the counterexample as established fact.

**What is real.** C11's claim is narrowed to the one property the audit still
found nowhere, the narrowing is recorded on the row with its evidence tier
intact, and the lane that produced it was reading the page's own procedure
when it did. That is a genuine result. Its provenance is a commissioned read,
and the row it narrowed still rests on an unverified lead.

---

## 2. The increment

The host's own certification gate had a defect the kit has a name and a page
for: a **collapsed collection**. A behavioral test suite declared thirty
assertions. The fixture directory those assertions read was absent from every
clone. The suite printed one skip line, ran none of them, and exited 0. The
smoke run above it consumed a pass count and a fail count, read `(0, 0)` as a
clean run, and recorded PASS. The top gate matched the string `0 FAIL` in that
output, which is true of a run in which nothing happened.

Nothing in that chain was careless. Each layer reported a numerator with no
denominator, and a numerator alone cannot distinguish a suite that passed from
a suite that never ran.

The increment made the gate unable to certify a suite that never ran:

- the suite declares its assertion count and prints a `ran/declared`
  denominator with a state word;
- a missing fixture is `PARTIAL` with a non-zero exit, not a skip;
- the smoke run publishes a selected denominator and its skip percentage, and
  a setup failure is a failure rather than a skip;
- the top gate judges the suite's own state line, and **an absent line is a
  failure** rather than a pass.

### The proof chain, in the order it was run

Every line below is quoted from the run that produced it. The host's own
directory names are redacted as `<fixture>`; nothing else was changed.

**1. The lie, before any change.** The fixture directory does not exist in
this clone.

```
$ python scripts/test_api.py
   (skip: fixture customer '<fixture>' not present)
EXIT CODE: 0

$ python scripts/golden.py --verify
  GOLDEN GATE
    ✓ smoke_test  88 pass  |  0 FAIL  |  0 warn  |  32 skip
  => GREEN — this tree is golden
GOLDEN EXIT: 0
```

**2. The gate-line change, committed before the fixture existed** — so the red
is on the record independently of the fix that greens it.

```
   ✗ FIXTURE MISSING: customer '<fixture>' not present at <path>
   behavioral_api: PARTIAL - COLLAPSED COLLECTION: 0 of 30 assertions ran - the net did not execute
EXIT: 1

  => RED — NOT golden, do not ship
GOLDEN EXIT: 1
```

The same tree that certified GREEN minutes earlier is now correctly RED.
Nothing about the tree changed except the gate's ability to describe it.

**3. Green, earned.** A synthetic fixture — fictitious, labelled as fictitious
in four places, no real company and no customer data — makes the suite
execute.

```
  behavioral_api: PASS - 30/30 assertions ran, 30 passed, 0 failed
EXIT: 0
```

Thirty of thirty, first attempt, with no assertion adjusted to fit the
fixture.

**4. Negative control, with no test file edited.** The kit's rule is that you
do not edit a test to watch the gate go red. Hiding the fixture directory
reddens the gate without touching a test file, and restoring it greens it
again.

```
$ mv "<fixture>" "<hidden>"
   behavioral_api: PARTIAL - COLLAPSED COLLECTION: 0 of 30 assertions ran - the net did not execute
EXIT: 1
$ mv "<hidden>" "<fixture>"
  behavioral_api: PASS - 30/30 assertions ran, 30 passed, 0 failed
EXIT: 0
```

**5. A planted regression, also with no test file edited.** One cell of
product data in the fixture is changed so that a classifier no longer fires.

```
   ✗ FAIL: R2 behavior frozen: <rule> (owned-but-inadequate)
  behavioral_api: FAIL - 30/30 assertions ran, 29 passed, 1 FAILED
EXIT: 1
  => RED — NOT golden, do not ship
```

**The payoff:**
`FAIL - 30/30 assertions ran, 1 FAILED` and
`PARTIAL - 0 of 30 assertions ran` are different states. The old gate printed
the same thing for both, and for a clean run.

### The final state

```
LEVEL 1: HEALTHY (exit 0) — 7 document checks, 0 needing attention
GOLDEN GATE => GREEN, exit 0, with behavioral_api: PASS - 30/30 assertions ran
```

---

## 3. The first escape number that project ever computed

The increment ended by writing the host's own judgment ledger and running the
kit's escape-rate tool over it. The first round on that repository:

```
| Round        | Items | Escapes |
|--------------|-------|---------|
| gate-honesty |   7   |    5    |
```

**Five of seven.** Four of the five were escapes for the same reason: a check
existed, ran, was green, and published a numerator without a denominator. The
fifth was a check whose stated subject named the exact failure class it missed
— a Unicode-encoding guard that asserted one module forced UTF-8 output, while
the two scripts that actually crashed on a stock Windows console did not
import that module. The guard passed. It was green over the defect it was
written for, because its reach was narrower than its claim.

A first-round rate of 71% carries no verdict either way; it has nothing to
fall from yet. What makes it worth publishing is the direction it
points. A coverage metric on that repository would have reported the same
gates, the same tests and the same green. The miss rate reported that five of
the seven things found were things the existing checks should have caught, and
that is a statement no coverage number makes.

Two further findings were dispositioned ORACLE-DECLINED rather than fixed,
each with a named check shape and a trigger that fires if the class appears
again. Declining a check and recording the bet is the kit's convention, and it
is what stops a discovery round from becoming an open-ended build.

---

## 4. What the documents got wrong

The adoption followed the kit's Level-1 path as written and surfaced four
documentation defects that seven internal walks had not:

- a branch table predicting how many unfilled slots the render tool reports,
  which did not enumerate the run an adopter gets after correctly completing
  the previous step;
- a printed commit line that omitted a file the previous step told the adopter
  to edit, leaving that edit uncommitted with nothing to notice it;
- two judgment calls at the render step that the page never named — an empty
  directory left behind by a deleted render, and a second run's deliberate
  abort on a leftover file.

All four are now fixed in `LEVEL-1.md`, each carrying the reason it was found.

None of them is severe. What matters is why they survived seven walks: the
internal walks met a repository the documents were written for, and a real
host does not. That is the lesson recorded from this increment, and it is the
strongest argument on this page for doing the same thing again on a second
host.

---

## 5. What this establishes, and what it does not

**Establishes.** The kit's Level 1 installed into an existing repository by
following its documents, and reported `LEVEL 1: HEALTHY (exit 0)`. One
improvement was executed under the kit's discipline, was proven red before it
was proven green, was proven red twice more without editing a test file, and
ended with a gate that publishes a denominator and a state word. The doctrine
transferred without the tooling: the kit's own gate-line adapter was read as a
contract and never installed, because the host has no pytest suite and did not
need one.

**Does not establish.**

- One repository, one language, one adopter, one afternoon. The host was a
  clean tree by the standards of the kit's brownfield page, so four of the six
  collisions that page documents were never exercised.
- The adopter was a language model, not a person. Every adoption figure this
  kit publishes carries that limit and this one does too.
- No timing is reported. The wall-clock here measures an agent issuing tool
  calls, not a person adopting a toolkit, and the two are not comparable.
- The fix is proven against the failure mode it targets — a collection that
  collapses to zero. It does not catch a collection that *shrinks*: delete ten
  assertions and the suite reports a self-consistent `20/20` unless the
  declared count is edited in the same change, and nothing forces that. The
  residual is stated in the host's own failure-floor record rather than left
  to be discovered.
- One defect was found and deliberately not fixed: the host's certification
  gate crashes on a stock Windows console before printing a verdict. It is
  recorded, and it is loud rather than silent — an unrunnable gate is a
  different problem from a dishonest one, and the increment's charter was
  honesty.

**The transplantability reading.** What moved to the new host was not the
tooling. It was three properties: publish a denominator beside every
numerator, prove the check red before you trust the green, and write down
which existing check should have caught each finding. All three were
implemented in the host's own scripts, in the host's own style, in one
afternoon, and none of them required a file from this kit to be copied. That
is the claim this page supports. Whether it holds on a second host is not
known, because there has not been a second host.
