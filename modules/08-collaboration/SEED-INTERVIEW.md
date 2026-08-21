# The Seed Interview — five questions, fifteen minutes, once

Ask these at the start of a working relationship. They are chosen because each
one's answer changes something *structural* about how the work runs, and because
each is cheap to ask and expensive to discover by collision.

Write the answers into `PROFILE-TEMPLATE.md`. Quote them **verbatim** — the
phrasing carries information the summary loses.

---

## 1. Decision style

> **"When I've analysed something and there's a choice to make — do you want my
> recommendation with the reasoning, or the options laid out so you can pick?
> And does that change when the decision is expensive?"**

*Why it matters:* determines whether every analysis ends in a lean or a menu,
and whether a menu mid-discussion reads as thorough or as evasive. Some people
experience an unsolicited menu as being handed back their own homework.

*Listen for:* whether they distinguish **discussion mode** from **decision
mode**. Many people want conversation while thinking and a menu only once they
have signalled readiness — and presenting the menu early ends the thinking.

---

## 2. Checkpoint shape

> **"How often do you want to see real output, and what does a useful checkpoint
> look like — a demo, a written summary, a diff, a number?"**

*Why it matters:* sets the phase length and the deliverable format for every
gate in the project. Get it wrong in one direction and they are interrupted
constantly; wrong in the other and a week of work turns out to have been
pointed the wrong way.

*Listen for:* the **artefact type**. "Show me it running" and "send me the
numbers" are different projects with different instrumentation costs, and you
need to know which one you are building for before you build the harness.

---

## 3. The acceptance test

> **"When this is finished, how will you know it's good? What's the thing you'll
> check that tells you more than any of the metrics?"**

*Why it matters:* names the real oracle. Everything mechanical is scaffolding
around this answer.

*Listen for:* whether the answer is **measurable, or a feel-word**. If it is a
feel-word — "it should feel fast", "it should read like an expert wrote it" —
that is not vagueness, that is the highest-value thing in the interview. Write
it down verbatim; decomposing it into numbers is a large part of your job.

---

## 4. Pushback licence

> **"If I think you're wrong about something — a design call, a priority, a
> ruling — how do you want to hear it? And is there a point where I should just
> do it your way?"**

*Why it matters:* an assistant that never disagrees is an assistant that has
stopped adding judgement, and one that argues at the wrong moment is a
liability. This question makes the boundary explicit instead of discovering it
during a disagreement.

*Listen for:* whether they want disagreement **inline** or **flagged and
parked**, and whether "I've decided" is a full stop or an opening position.

---

## 5. The betrayal line

> **"What would make you stop trusting my output? Not annoyed — actually stop
> trusting it."**

*Why it matters:* this is the most valuable question on the list and the one
people are least often asked. The answer is a hard constraint, not a preference,
and it usually names something you would otherwise have done cheerfully in week
two.

*Listen for:* silent omissions, confident wrong numbers, work reported as
finished that is not, invented citations, quietly dropped requests. Whatever
they name goes into the profile in **bold**, and — if it can be — into a check.

---

## How to run it

- **Ask, then stop talking.** The pauses are where the qualifications live.
- **Capture verbatim.** Their phrasing carries information your summary drops.
- **Do not defend the defaults.** You are collecting overrides, not selling a
  contract.
- **Ask question 5 last**, and let it be the one they leave thinking about.

## What to do with the answers

1. Fill in `PROFILE-TEMPLATE.md` verbatim.
2. For each answer that **contradicts** `DEFAULT-CONTRACT.md`, write the
   override explicitly in the profile: *"Default 1 (recommendation-first) is
   overridden: they want the option space first, then a lean."* An unrecorded
   override is a default you will drift back into.
3. **Route each answer to the right ledger — they are not interchangeable.**

   - An **acceptance test** is a product ruling: *"it is good when X."* That is
     a row in `JUDGMENT-LEDGER.md`, ruling → check, UNCHECKED with a reason if
     no check exists yet. It is the first oracle of the project and it comes
     free with a conversation.
   - A **betrayal line** is not a product ruling. It is a rule about how the
     work is *conducted* — "never report something as finished when it is not",
     "never give me a number you cannot source". Those belong in
     `FAILURE-FLOOR.md`, as rules with a layer, a zone and a last-fired date,
     because the question they raise is *what enforces this?*, not *what would
     go red if the product changed?*

   The distinction is the same one module 04's README draws between the two
   documents, and it is worth getting right on day one: a betrayal line filed
   as a product ruling never acquires an enforcement layer, and quietly becomes
   the thing everyone remembers and nothing checks.
