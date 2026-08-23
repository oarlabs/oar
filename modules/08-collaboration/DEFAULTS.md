# Calibration defaults, and the realignment ask

**These are one measured program's values, not best practice.** Every value on
this page was distilled from a single long-running AI-assisted engineering
program and reduced to its shape: the class of calibration, with the people, the
projects, the anecdotes and the quoted sentences removed. It was not surveyed,
not benchmarked, and not compared against any other program. Nothing on this
page has been measured to make an adoption faster, safer or more complete than
the blank-page route, and no such claim is made for it anywhere. **Part 2 exists
because the expected outcome of reading Part 1 is that some of it is wrong for
you.**

---

## What this page is, and which route is the default

Module 08 gives a new owner two ways to reach the same artefact — a filled
collaboration profile.

- **The blank-page route is the shipped default path.** Run
  `SEED-INTERVIEW.md`'s five questions, capture the answers verbatim, and write
  them into `PROFILE-TEMPLATE.md`. It is the route the module was built around,
  it is the route `QUICKSTART.md` Step 8 and `LEVEL-1.md` Step 4 describe, and
  nothing on this page changes it.
- **This page is the optional second route.** Part 1 is a pre-filled starting
  state. Part 2 turns the interview into a walk down that starting state, where
  each value is kept, overridden or deleted. It is offered beside the blank-page
  route, not in front of it.

**The reason the second route exists, stated so you can reject it.** In the
program these values came from, the owner ruled faster and more precisely
reacting to a stated lean than to an open question — which is default **CAL-B1**
below. So the argument for this route is itself one of the values on it. If
CAL-B1 is wrong about you, this route is probably wrong about you too, and the
blank page is the better instrument. That is not a disclaimer bolted on; it is
the honest shape of the offer.

**This page is never copied into an adopting repository.** Like
`SEED-INTERVIEW.md` and `DEFAULT-CONTRACT.md`, it is read in the kit clone and
its output lands in the profile. It carries no configuration slots, it is not a
template, and no step renders it.

---

## How an adopting agent may use this page

`ONBOARD.md` §4 sorts every instruction on the adoption path into MECHANICAL,
SHIPPED DEFAULT and OWNER JUDGMENT. This page is a SHIPPED DEFAULT source for
one thing and is explicitly not one for another. Read both halves before citing
it.

**It is a shipped default for the working contract you run under before the
owner has ruled.** That is the same standing `DEFAULT-CONTRACT.md` already has —
in force, unconfirmed — extended to the calibration classes the eight defaults do
not cover. `ONBOARD.md` §4 defines the class as one where the documents
"prescribe a default value and name the condition for revisiting it", and the
condition is named once for the whole page below. Taking a value from here is
therefore not judgment: cite this page and the value's id, and record it as a
punch item in state `DEFAULT-TAKEN` so the owner can overrule it.

**The revisit condition, for every value on this page:** the realignment walk in
Part 2, or the blank-page seed interview, whichever the owner runs. Both end the
default's unconfirmed standing. A value nobody has walked stays `DEFAULT-TAKEN`
and stays overrulable, however long it has been in force.

**It is not an answer to D-2, and it may not be used as one.** `ONBOARD.md` §4
classes the seed-interview step as OWNER JUDGMENT, absolutely, and its §7 states
the rule this page must not be used to route around: "Never write an answer the
owner did not give." Concretely:

- Do not copy a default into the profile's verbatim answer blocks — the five
  `> Q…` quotations, the betrayal-line restatements, or the one-line version.
  Those hold the owner's words or they hold nothing.
- Do not set the profile's `INTERVIEW:` line to `held` because this page exists.
  It reads `not yet held` until the owner has been put through Part 2 or the
  seed interview. `LEVEL-1.md` Step 4 states why the check is written that way:
  "A date that parses is not a date somebody agreed to".
- Do not record a value from here in the profile's overrides table as an
  override. An override is something the owner said instead of a default; a
  default nobody has ruled on is not one.

**Where a value already has a home elsewhere in the kit, this page names it in
one sentence so the walk reaches it, and points at the authority that holds
it.** One authority per value: where the sentence here and the cited document
differ, **the cited document governs.** The eight behavioural defaults are
`DEFAULT-CONTRACT.md`'s; the loop-termination rules are module 01's standing
rules, under the heading WHEN THE LOOP ENDS; the process-ratio ceiling is module
04's `TOKEN-LEDGER.md`. Every row that restates a value held elsewhere says so
in its own parentheses. This page adds the calibration classes those documents
do not carry, and marks the cross-references inline.

**A taken default leaves a record in the tree, not only in the adoption
report.** Where you have taken values from this page, add one line to the
profile's `STATUS` section, beside the sentence already there that says every
`DEFAULT-CONTRACT.md` default is in force and unconfirmed, naming this page and
the ids taken. `STATUS` is neither a verbatim answer block nor the overrides
table, so this is permitted, and it is what `ONBOARD.md`'s "Where the punch list
lives" requires: "A punch list in a file nobody opens is the same as no punch
list."

---

## Before you read Part 1, if you are the owner

The kit routes a solo adopter to this page as both walker and owner —
`LEVEL-1.md` Step 4, `QUICKSTART.md` Step 8 and this module's README each say
so. Part 1 prints four candidate betrayal lines, CAL-F1 to CAL-F4. Reading them
before you have stated your own replaces your answer with a recognition test,
which is the failure the betrayal group's design exists to avoid.

**Write your own answer to `SEED-INTERVIEW.md` question 5 first, in your own
words, and date it. Do not read Part 1 until it is written down.** Then read
Part 1, and treat CAL-F1 to CAL-F4 as four candidates to add to a list you have
already made.

This holds on every route into this page, whichever document sent you here, and
whether you arrive at Part 1 first or at Part 2 first. A walker running the ask
on somebody else carries the same obligation in the other direction, stated in
Part 2's order: ask question 5 open before showing the four.

---

# Part 1 — the starting state

The groups below are the groups `PROFILE-TEMPLATE.md` uses, in its order, so a
value can be carried across without re-sorting. Each value is one sentence, each
carries an id, and each is overridable. Nothing here is load-bearing on any
check.

Read the group note before the values in it. The notes are where the honest
caveats sit.

Thirty-three values, in six groups lettered A, B, C, E, F and G. **There is no
group D**, deliberately: `ONBOARD.md` §7 numbers its deferral punch items D-1 to
D-7, and two id schemes sharing a letter in the same conversation is a
collision waiting to happen.

## How they think

*Note: these are the values with the widest reach and the weakest evidence of
generality. They were stable across two unrelated projects in the source
program, which is two, not many.*

| id | Default |
|---|---|
| CAL-A1 | Structure comes before the feature: a proposed point fix is answered with what it means for the system, not only with the patch. |
| CAL-A2 | Any design is judged on how it decays, so the maintenance and failure story is stated unasked — staleness must degrade to silence rather than to confident wrong output. |
| CAL-A3 | Nothing is invented: claims are grounded in the record, provenance is tagged, and model-generated content is labelled as such. |
| CAL-A4 | Ideas are captured at the moment they surface — filed to the durable knowledge store, then the current task resumes — rather than held in the conversation. |
| CAL-A5 | Safeguards go in structure, not in sentences: a rule that failed as prose is promoted to a mechanical layer, or accepted with the residual named. |
| CAL-A6 | Committed and published prose is plain technical writing — short declarative sentences, defined terms, active voice — while conversation may be informal. |
| CAL-A7 | Loud failures are preferred to silent ones, at every layer including plumbing (`DEFAULT-CONTRACT.md` default 7 carries this; the value is listed here so the walk reaches it). |

## How they decide

*Note: this is the group the second route's whole argument rests on, and it is
the group a new owner is most likely to differ on. Walk it first.*

| id | Default |
|---|---|
| CAL-B1 | Every analysis ends in a stated lean with its reasoning, because the owner reacts to a recommendation faster and more precisely than to a flat option list (`DEFAULT-CONTRACT.md` default 1 carries this; the value is listed here so the walk reaches it). |
| CAL-B2 | Decision menus appear only at decision-readiness: while a question is being discussed the exchange stays in prose, and a numbered menu arrives once the owner signals they are ready to rule. |
| CAL-B3 | Rulings come in batches: a numbered list with a lean on each item is answered in one pass, often amended in transit, so items are numbered and each carries its own lean. |
| CAL-B4 | A settled decision is not reopened without new evidence; reopening it costs more trust than the decision was worth. |
| CAL-B5 | Work is delivered in phases with named stop points and exit criteria, and deferral is a first-class outcome rather than a silence. |
| CAL-B6 | The deletion option is presented honestly beside the configuration options, because the owner asks whether the thing is needed at all and is often right. |
| CAL-B7 | Hardening the existing ground is preferred to extending it, unless the cost argument favours the extension — a preference that bends to a good lean rather than a rule. |

## How they evaluate

*Note: CAL-C5 carries figures from the source program; CAL-C6 restates a rule
the kit ships in full. A number carried into a project that did not derive it is
a placeholder wearing a decimal point. Both rows say what the kit's own shipped
value is.*

| id | Default |
|---|---|
| CAL-C1 | The gate is hands-on use of real output, inspected by the owner, rather than a description of output (`DEFAULT-CONTRACT.md` default 2 carries this; the value is listed here so the walk reaches it). |
| CAL-C2 | A feel-complaint is an un-instrumented measurement: it is decomposed into numbers and regression-tested, never dismissed, and a green metric never overrules a bad feel (`DEFAULT-CONTRACT.md` default 8 carries this; the value is listed here so the walk reaches it). |
| CAL-C3 | The acceptance test is whether using the thing is a pleasure, which is a scalar over the whole build — so bisectable, individually revertable commits are a requirement of the acceptance test rather than tidiness (`DEFAULT-CONTRACT.md`, "Two consequences that follow from the list", carries this; the value is listed here so the walk reaches it). |
| CAL-C4 | The owner's own review is a first-class instrument, and each defect they catch that every automated gate passed is an oracle candidate to be written down, not an anecdote. |
| CAL-C5 | Process cost is measured per stage against a **derived** ceiling, not an adopted one: the source program derived its own figures, and the kit publishes both the method (`TOKEN-LEDGER.md`, "The ceiling") and its own derivation with its n and its confidence (`KNOWN-ISSUES.md`, "The ratio ceiling"). Derive yours; do not adopt one. |
| CAL-C6 | The review loop terminates by rule rather than by exhaustion — one round by default, approve-with-punch-items counts as approved, only a reject buys a second round, and findings below the materiality bar are rejected in writing with a one-line reason (module 01's standing rules, "WHEN THE LOOP ENDS", ship this in full; the value is listed here so the walk reaches it). |

## Pushback and disagreement

| id | Default |
|---|---|
| CAL-E1 | Disagreement is licensed and expected, delivered inline with the reasoning, because an assistant that never disagrees has stopped adding judgement. |
| CAL-E2 | Disagreement is raised before the ruling; after it, the objection is recorded and the work proceeds. |
| CAL-E3 | When something breaks the mechanism is named rather than the person, and the mechanism is then changed so the same failure cannot recur silently (`DEFAULT-CONTRACT.md` default 6 carries this; the value is listed here so the walk reaches it). |
| CAL-E4 | Honest partials are welcome and a broken deliverable is not: completeness never outranks the integrity of what ships (`DEFAULT-CONTRACT.md` default 5 carries this; the value is listed here so the walk reaches it). |

## THE BETRAYAL LINE — hard constraints

*Note: this is the group where a default is most likely to be wrong and most
expensive to leave unconfirmed. `LEVEL-1.md` Step 4 calls an unanswered
betrayal line the single riskiest gap on the profile page, and shipping four
plausible answers does not close it — it makes the gap harder to see. **Part 2
therefore asks this group open, in the seed interview's own words, before
showing these four.** Do not show them first.*

*If you are the owner reading this page yourself, the same rule binds you: your
own answer to `SEED-INTERVIEW.md` question 5 goes on paper, dated, before you
read the four rows below. The instruction and its reasoning are stated in full
in the section immediately above Part 1.*

| id | Default |
|---|---|
| CAL-F1 | An item on a list that receives no disposition — a silent skip — ends trust, because it forces the owner to re-derive the whole list to find out what happened to it (`DEFAULT-CONTRACT.md` default 4 carries this; the value is listed here so the walk reaches it). |
| CAL-F2 | Work reported as finished that is not finished. |
| CAL-F3 | A fabricated fact, number or citation, including a quotation attributed to a document that does not contain it. |
| CAL-F4 | A green that was manufactured rather than earned — a check narrowed, a red stashed, or a gate deleted so a run could report success. |

## Blind spots — what this profile is probably wrong about

*Note: this is the one group where a default is a hypothesis about a person the
kit has never met. Everything above describes how work is conducted; this
describes where the owner's own strengths turn against them, which is not
transferable evidence. **The default disposition for this whole group is
DELETE.** Keep a row only if the owner recognises it, and record it with the
date they did.*

| id | Default |
|---|---|
| CAL-G1 | The hardening reflex defers the payoff: another cycle of robustness is always defensible, and the work that proves the thesis keeps sliding right. |
| CAL-G2 | Capture discipline produces backlog sprawl: parked ideas accumulate faster than they are retired, and convergence has to be pushed deliberately. |
| CAL-G3 | Validation runs against curated fixtures rather than real users, and internal quality questions crowd out the external ones. |
| CAL-G4 | Project context concentrates in few places and few sessions, which makes any one of them load-bearing. |
| CAL-G5 | The owner retains the judgement-heavy and cosmetic work, and becomes the bottleneck on a class of task that could be delegated. |

`PROFILE-TEMPLATE.md` also asks for two blind spots about the record itself —
where the observation base is thin, and where the AI's own bias distorts what it
noticed. Those are written from this project's evidence and have no defaults.

## The two slots with no default

- **The opening paragraph** — who the owner is in this project and what they are
  optimising for. Project-specific by construction. The walk asks for it.
- **The one-line version** — the single sentence handed to a fresh session. It
  is composed at the end of the walk from what survived it, not carried over.

## Where each disposition lands

Part 2 defines four states — KEEP, OVERRIDE, DELETE and `NOT REACHED`. Each one
has a landing site in the profile, named here, so that no walker has to invent
one.

**OVERRIDE.** `PROFILE-TEMPLATE.md` has one overrides table, and it is scoped to
the eight defaults in `DEFAULT-CONTRACT.md`. Route by that mapping:

| Value on this page | Maps to | An override goes |
|---|---|---|
| CAL-A7, CAL-B1, CAL-C1, CAL-C2, CAL-C3, CAL-E3, CAL-E4, CAL-F1 | one of the eight | the profile's overrides table, with the default's number and name |
| everything else | nothing in the eight | inline in the profile section that holds the group, with the value's id beside it |

An empty overrides table is a real answer and always was: it means the eight
hold. It does not mean the walk was skipped — the `INTERVIEW:` line says that.

**KEEP**, which is the disposition this route produces most of. A kept default
lands **inline in the profile section that holds its group**, as a single line
in a fixed form:

```
CAL-B2 ratified <date> — kit default, not the owner's words. <The value, one sentence.>
```

It is never written as a bolded trait claim followed by an evidence sentence.
That shape is `PROFILE-TEMPLATE.md`'s form for a trait the AI observed and can
cite evidence for, and a ratified default is neither — it has no sighting in
this project and no words of the owner's behind it. The fixed form exists so
that a later reader can tell the two apart at a glance, which is the whole
reason this route is defensible. Where the value maps to one of the eight, the
overrides table stays empty on that row: a keep is not an override.

**DELETE.** The value does not appear in the profile at all. Record it in the
walk's revision-log entry only.

**`NOT REACHED`.** The ids go in the revision-log entry, listed, not counted —
see "What comes out" below.

---

# Part 2 — the realignment ask

The seed interview asks five open questions. This walk asks the same five
subjects as a diff against Part 1. It produces the same artefact, and it is not
a different interview: the questions in `SEED-INTERVIEW.md` are the authority on
what is being asked and why, and this page only changes the shape of the asking.

**Who and when.** The same person the seed interview needs: whoever owns the
judgement on this project. Once, early. Budget twenty to thirty minutes rather
than fifteen — a walk down thirty-three values takes longer than five questions,
and the extra time is the point of taking this route rather than a cost of it.

**If you are running this walk on yourself**, which is the common case on a
first adoption, write your answer to `SEED-INTERVIEW.md` question 5 **before you
read Part 1**, in your own words, and date it. Do not read CAL-F1 to CAL-F4
until it is written down. There is no second party here to hold the ordering for
you, so the ordering has to be held by you, before the reading starts — the same
instruction is above Part 1 for a reader who arrives there first.

## The order

1. **How they decide** (CAL-B1…B7) — first, because CAL-B1 is the assumption
   the whole route rests on and the owner should get to break it early.
2. **How they think** (CAL-A1…A7).
3. **How they evaluate** (CAL-C1…C6).
4. **Pushback and disagreement** (CAL-E1…E4).
5. **Blind spots** (CAL-G1…G5) — offered as candidates to delete, not to
   confirm.
6. **The betrayal line** — last, and **asked open first.** Put
   `SEED-INTERVIEW.md`'s question 5 to the owner in its own words and capture
   the answer verbatim before CAL-F1…F4 are shown at all. Then show the four and
   ask whether any of them belongs on their list too. `SEED-INTERVIEW.md` says
   to ask question 5 last and let it be the one they leave thinking about;
   putting a menu of four in front of it first would replace their answer with a
   recognition test.

**Which group carries which of the five questions.** The walk covers the seed
interview's five subjects across six groups, and the mapping is not one to one.
It is stated here so that a walk which stops early can be judged against it
rather than guessed at.

| `SEED-INTERVIEW.md` question | Subject | Covered by |
|---|---|---|
| Q1 | Decision style | the whole of **How they decide** (CAL-B1…B7) |
| Q2 | Checkpoint shape | **CAL-C1** (what a checkpoint is made of: real output, inspected) and **CAL-B5** (how often: phases with named stop points) — two groups, both required |
| Q3 | Acceptance test | the whole of **How they evaluate** (CAL-C1…C6) |
| Q4 | Pushback licence | the whole of **Pushback and disagreement** (CAL-E1…E4) |
| Q5 | The betrayal line | the **open ask** at the head of the betrayal group, before CAL-F1…F4 are shown |

**How they think** (CAL-A1…A7) and **Blind spots** (CAL-G1…G5) carry no seed
question. They are calibration the interview does not ask for, and a walk that
skips them has still covered all five subjects.

## The three dispositions

Every id gets exactly one, and the walk is not finished until every id has one.
Where each of them lands in the profile is Part 1's section "Where each
disposition lands", which routes all four states — including KEEP, in a fixed
form that cannot be mistaken for prose the owner authored.

| Disposition | Meaning | What the record must carry |
|---|---|---|
| **KEEP** | The owner recognises the value as theirs | The id, the date, and the fact that it is a kept default, in the fixed form given under "Where each disposition lands". Never rewritten as prose the owner appears to have authored |
| **OVERRIDE** | The owner wants something else | Their words, verbatim, plus the id of the default they displaced, so the record shows what was there before |
| **DELETE** | The **owner** says the value does not apply to this project | The id, the date, and the reason in the owner's words if they gave one. The ruling is not optional; only the reason is. The value does not appear in the profile at all |

**A fourth state exists for the walk itself, not for a value: `NOT REACHED`.**
A walk that runs out of time closes explicitly — every id carries a disposition
or `NOT REACHED`, and the profile says how far the walk got, **by id**. A
default nobody reached is not a default the owner kept, and the difference is
exactly the difference `DEFAULT-CONTRACT.md` draws between overriding
deliberately and eroding accidentally.

## How to run it

- **Read the value, then stop talking.** The same rule the seed interview
  carries: the pauses are where the qualifications live.
- **Capture verbatim** when the owner overrides. `SEED-INTERVIEW.md` states the
  reason: "Their phrasing carries information your summary drops."
- **Do not defend the defaults.** `SEED-INTERVIEW.md` says this of the eight,
  and it applies harder here, where there are more of them and they arrive
  pre-written. You are collecting overrides.
- **Watch for agreement that is politeness.** A written default anchors, and a
  keep is cheaper to say than an override. Where an owner keeps a value without
  engaging with it, ask them to say it in their own words — and if they do,
  record those words as an OVERRIDE rather than a KEEP, even where the meaning
  is the same. Their sentence is better evidence than the kit's.
- **A default the owner argues with is the most valuable minute in the walk.**
  It is the one place this route beats the blank page, and the argument, not the
  verdict, is what goes in the profile.

## What this route does not change

Stated as a list because each line is a rule the route could plausibly be read
as relaxing, and none of them is relaxed.

1. **The owner's verbatim answers are still the owner's.** An override is
   recorded in their words, uncompressed, exactly as the blank-page route
   records an answer.
2. **A kept default is recorded as a kept default.** It is never restyled into
   an authored answer, never quoted as though the owner said it, and never
   placed in one of the profile's `> Q…` verbatim blocks. `ONBOARD.md` §7's
   rule governs the whole route: "Never write an answer the owner did not
   give." A kept default is an answer the owner *ratified*, and the record says
   which of the two it is.
3. **`INTERVIEW:` reads `held <date>` only when all five subjects were put to
   the owner**, including the betrayal line. A partial walk leaves the line at
   `not yet held` — which is green, claims nothing, and is the honest value —
   with the coverage recorded beside it.
4. **The profile's own rules still bind it, as they bind the blank-page route.**
   Promotion on second sighting, evidence per claim, no speculation about
   motive, supersede rather than delete. `PROFILE-TEMPLATE.md` states the first:
   "One sighting is an anecdote. Two is a pattern". The promotion rule governs
   what the AI *observes*, not what the owner *states*: a ratified default,
   like a seed-interview answer, enters the profile on the owner's ruling rather
   than on a second sighting, and both have always entered that way.
5. **The routing of answers to ledgers is unchanged.** An acceptance test is a
   row in the judgment ledger; a betrayal line is a rule with a layer in the
   failure floor. `SEED-INTERVIEW.md`, "What to do with the answers", is the
   authority and this route does not touch it.
6. **The blank-page route remains available at any point.** An owner who finds
   the walk is anchoring them can stop, discard Part 1, and answer the five
   questions cold. Nothing downstream is invalidated by the switch.

## What comes out

The same file the blank-page route produces: a filled
`docs/collaboration-profile.md`, at the same path, with the same sections, meeting
the same checkpoint. **No downstream step, check or tool branches on which route
was taken**, and none should be added.

The profile is nonetheless legible about provenance, and that is deliberate
rather than a leak of the route. Each value in it is one of two things — the
owner's words, or a default they ratified with an id and a date — and the
fabrication rule requires the reader to be able to tell them apart. A profile
that hid the difference would be the failure this whole module exists to
prevent, and it would be worse under this route than under the other, because
this route produces more of the second kind.

Record the walk in the profile's revision log as one entry: the date, that the
realignment walk was the route, the counts kept, overridden, deleted and not
reached, **and the ids of the values not reached, listed**. Those four counts
are the honest summary of how much of this page survived contact with your
project, and they are the only number this page asks anyone to write down. The
not-reached ids are not recoverable any other way — a kept value is in the
profile and a deleted one is absent, but a value nobody walked looks exactly
like a value that was deleted. Listing the ids is what makes a partial walk
resumable, and what stops an unwalked default reading as a ruled one.
