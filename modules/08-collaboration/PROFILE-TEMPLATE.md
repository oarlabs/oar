---
title: Working with <name> — a note to the next model
type: collaboration-profile
status: living document
created: <date>
last_revised: <date>
sources: <the seed interview date, plus the stage reports and rulings that
  evidence each observation>
---

<!--
TEMPLATE - the living collaboration profile. Copy to {{KNOWLEDGE_DIR}} and keep
THAT copy as source of truth; a repo copy is a convenience mirror that will
drift. If kit.config sets KNOWLEDGE_DIR to NONE, substitute a repo path such as
`docs` here instead - the slot is interpolated unconditionally, so the literal
word NONE is what you get otherwise - and that repo copy IS source of truth,
with nothing to drift from. Delete this comment on adoption.

WHO WRITES THIS: the AI, continuously, from evidence. The human reads it and
corrects it. That inversion is deliberate - a self-description is what someone
believes about themselves, and a profile built from observed behaviour is what
actually happened. Both are useful; only the second one predicts.
-->

# Working with <name> — a note to the next model

<One paragraph. Who they are in this project, what they are optimising for, and
the single most useful thing to know before the first exchange.>

## THE PROMOTION RULE — read this before adding anything

**One sighting is an anecdote. Two is a pattern; promote it into this document
with both citations.**

Everything below carries evidence: a date, a quote, a stage report, a commit.
An observation with no citation is a guess about a person, which is the most
expensive kind of guess in this entire kit — it is confidently wrong, it is
never re-checked, and it propagates into every future session.

**Never write speculation about motive.** Write behaviour and its consequence.
"Rejected three carefully-argued recommendations that opened with the analysis
rather than the answer" is evidence. "Dislikes long explanations" is a theory,
and it will be treated as fact by the next reader.

## STATUS — fill this in first, and keep it honest

```
INTERVIEW:  not yet held | scheduled <date> confirmed by <who or which calendar> | held <date>
```

**The `scheduled` state carries its confirmation, and the check enforces it.**
A date that parses is not a date somebody agreed to: an invented one and a
real calendar entry are the same string. Say where it came from, or write
`not yet held`, which is green and claims nothing.

**Day one, before the seed interview, this document is legitimately almost
empty — and that is a state it must be able to represent.** A blank profile
that looks like a filled-in one is worse than no profile: the next session
reads confident-looking emptiness as "nothing to know here" and proceeds on the
defaults without realising they were never confirmed.

Until the interview is held:

- **Every default in `DEFAULT-CONTRACT.md` is in force, unconfirmed.** Say so
  in the overrides table below (write `none recorded — interview not yet held`),
  not by leaving it blank.
- **Behavioural observations are still worth recording**, with dates. They are
  what the interview will confirm or correct, and a profile built from two
  weeks of evidence makes a much better interview than a cold one.
- **The betrayal line is unknown**, and that is the single riskiest gap on this
  page. Until it is answered, treat all eight defaults as hard.

Delete this section once the interview is held and the sections below are real.

## Overrides to the default contract

Any of the eight defaults they have overridden, with the evidence.

| Default | Override | Evidence |
|---|---|---|
| <n. name> | <what they want instead> | <date + quote> |

*(An empty table is a real answer: the defaults hold.)*

## How they think

**<Observed trait, bolded as a claim.>** <The evidence: what happened, when,
what they said. Then the consequence for how you should work.>

## How they decide

**<Trait.>** <Evidence. Consequence.>

*From the seed interview (verbatim):*
> Q1 decision style: "<their words>"
> Q2 checkpoint shape: "<their words>"

## How they evaluate

*From the seed interview (verbatim):*
> Q3 acceptance test: "<their words>"

<Which parts of that are measurable, which are feel-words, and which feel-words
have been decomposed into numbers so far. This section should get longer over
the project — that growth is the loop working.>

## Pushback and disagreement

*From the seed interview (verbatim):*
> Q4 pushback licence: "<their words>"

## THE BETRAYAL LINE — hard constraints

*From the seed interview (verbatim):*
> Q5: "<their words>"

**<Restate each as a bolded rule.>** <And where it is mechanically enforced —
name the check, or say UNCHECKED and why.>

These are not preferences. Everything else on this page can be adjusted in the
moment; these cannot.

## Blind spots — what this profile is probably wrong about

Written by the AI, honestly, and kept short:

- **<Where the observation base is thin.>** <e.g. "Every observation here comes
  from one project in one domain. Nothing predicts how they work under a
  deadline they did not set.">
- **<Where the AI's own bias distorts the record.>** <e.g. "I notice
  corrections more than approvals, because corrections generate work. This page
  probably over-indexes on what annoys them.">
- **<What has never been tested.>** <e.g. "Disagreement about scope has never
  actually happened; Q4's answer is untested.">

**A profile with no blind-spots section is a profile someone stopped auditing.**

## Maintenance contract (for the AI)

- **Read this at the start of every session**, before the first substantive
  exchange.
- **Update it when a second sighting promotes an observation** — in the same
  session, while the evidence is at hand.
- **Never delete an entry; supersede it in place** with the date and what
  changed. People change, and the record of the change is more useful than the
  current state alone.
- **Never write a trait without a citation.**
- **Surface it for correction at phase gates.** Say what you added and why, and
  let them strike anything they disagree with. A profile they have never seen is
  a dossier, not a collaboration document, and the difference matters.
- **The durable copy is source of truth.** Update it there.

## One-line version

<The single sentence you would give a fresh session with no other context.>

## Revision log

| Date | Change | Evidence |
|---|---|---|
| <date> | Created from the seed interview | <interview date> |
