# Module 08 — Collaboration

The working contract with the project's owner. It is the module most often
skipped, and skipping it is how well-engineered projects produce output nobody
wanted.

## Files

| File | What it is |
|---|---|
| `DEFAULT-CONTRACT.md` | Eight evidenced defaults to run until told otherwise, each with its own "override when" clause. About a page. |
| `SEED-INTERVIEW.md` | Five questions, fifteen minutes, once. Decision style, checkpoint shape, acceptance test, pushback licence, and **the betrayal line**. |
| `PROFILE-TEMPLATE.md` | The living profile scaffold: promotion-on-second-sighting, evidence-per-claim, an overrides table, a blind-spots section, a revision log, and a maintenance contract addressed to the AI. |
| `DEFAULTS.md` | **Optional.** One program's calibration, de-identified to its shape and labelled as one program's values rather than best practice, as a pre-filled starting state — plus the realignment ask, which walks an owner down it keep/override/delete and ends in the same profile. The blank-page route above stays the default path. |
| `CAPSULE.md` | **Optional, reference doctrine.** The sync capsule: a governed, append-only record of decisions about the working relationship, read by the collaborator itself. States the convention (imported governance doctrine with its ancestry, the fold mechanism and its acceptance test) and the honest boundary — the published null, and what is unmeasured. No tooling, no adoption step; nothing in `QUICKSTART.md` or `ONBOARD.md` routes through it. |

## The three ideas

### Defaults, not laws

Every default here was arrived at expensively in a real build. Stating them
means they can be **overridden deliberately** instead of **eroded accidentally**
— and an unrecorded override is a default you will drift back into during the
first busy week.

### The profile is written by the AI, from evidence

A self-description is what someone believes about themselves. A profile built
from observed behaviour is what actually happened. Both are useful; only the
second one predicts.

Hence the two hard rules: **one sighting is an anecdote, two is a pattern** (and
carries both citations), and **never speculate about motive**. Write behaviour
and its consequence. An uncited trait is a confidently-wrong guess about a
person, and it propagates into every future session unchallenged.

Surface the profile for correction at phase gates. A profile they have never
seen is a dossier, not a collaboration document.

### The betrayal line is the highest-value question you can ask

*"What would make you stop trusting my output? Not annoyed — actually stop
trusting it."*

The answer is a hard constraint, not a preference, and it usually names
something you would otherwise have done cheerfully in week two. Whatever they
name goes into the profile in bold and, wherever possible, into a mechanical
check — which makes it the cheapest first oracle in the whole project.

## File contract with other modules

- **← 01-governance.** The standing rules end with a one-line summary of the
  eight defaults and a pointer to the profile. The pointer names the durable
  copy as source of truth.
- **→ 04-ledgers.** Acceptance tests and betrayal lines that could become
  mechanical checks open rows in `JUDGMENT-LEDGER.md`, even as UNCHECKED. That
  is the first oracle of the project and it arrives free with a conversation.
- **`kit.config`** supplies `{{KNOWLEDGE_DIR}}`, the only token this module's
  shipped files carry (in `PROFILE-TEMPLATE.md`'s header, which adoption
  deletes). No other substitution exists here.

## What breaks if you adopt this module alone

Nothing, and it is the module most worth adopting alone. Five documents, two of
them optional, no tooling, no harness assumptions, useful with any AI system or
none — the seed interview works verbatim between two humans.

If you only ever take one module from this kit, the honest recommendation is
this one, then 04.

## Adaptation notes

- **Run the seed interview once, early, and never re-run it as a survey.**
  Everything after that comes from observation. Re-interviewing signals that you
  have not been reading.
- **A team, not an individual?** Run it per person for defaults 1, 2 and 4
  (which are personal), and once for the group on 3 and 5 (which are about the
  product and the trust boundary).
- **Working solo?** You are the owner: answer the five questions yourself, in
  writing, and hold the profile to the same rules — verbatim answers, cited
  evidence, promotion on second sighting. No calendar needed; the interview
  costs fifteen minutes the day you adopt. **If you take the optional
  `DEFAULTS.md` route, write your own answer to question 5 — the betrayal line —
  before you read that page's Part 1.** Being both walker and owner removes the
  one protection the ordering gave you: four written candidates read before your
  own answer turn the question into a recognition test, and afterwards the
  result is indistinguishable from an answer you actually gave. That page states
  the same rule above its Part 1.
- **Feel-words are the payload of question 3.** Every one you decompose into a
  regression-tested number is one the human never has to notice twice. Track
  that conversion rate; it is a better health metric than most.
- **Keep the profile short enough to load every session.** A profile nobody
  reads is a profile nobody corrects, and an uncorrected profile gets more
  confidently wrong over time rather than less.
