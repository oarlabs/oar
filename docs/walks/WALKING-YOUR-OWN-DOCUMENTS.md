# Walking your own documents

Your onboarding document, your runbook, your README: you cannot test it by
reading it. You know what it means. The reader it is written for does not, and
the gap between those two states is invisible from where you are standing.

A **walk** closes it. Give the document to a reader who has none of your
context, tell them to obey it literally, and record everything that did not
work. This kit's own finding counts come from that method, and this page is the
method itself, written for your documents rather than the kit's.

`README.md` in this directory is the other half: what the kit's own walks
found, what they can establish, and what they cannot.

---

## 1. Preflight — do this before you commission a walk

A walk is expensive and a walk against an unstable document is wasted. Four
things first.

1. **Freeze the subject and name it by commit.** A walker reads a tree, not a
   document in the abstract. Record the commit the walk ran against; every
   finding is then reproducible, and so is the fix.
2. **Run whatever you already have.** Any selftest, linter or smoke check the
   document depends on. A walker whose first command fails on a defect you
   already knew about spends its budget on your backlog.
3. **Decide what counts as a finding, in advance.** A command that does not run
   as printed. A checkpoint whose stated output does not match. A step that is
   unreachable where it is placed. An instruction that destroys something.
   Write the list down — and write down the **materiality bar**, the level
   below which a finding is killed with a one-line reason rather than fixed.
   Deciding this after the findings arrive is how a walk becomes an argument.
4. **Decide the fences.** What the walker may write to, what it must not touch,
   and where its report goes. On a walk into a real repository this matters
   more than anything else on the list: the walk's whole point is to obey
   instructions literally, and some of your instructions may be destructive.
   Give it a throwaway copy, or give it explicit backup instructions and expect
   to need them.

---

## 2. The lane spec — a fresh reader, and no coach

The walker is a lane with one job and unusually strict rules. All five below
are load-bearing; dropping any one of them turns the walk into a review.

- **It reads the documents in the order your documents route it**, and it
  starts where a real reader starts. If your README points at a quickstart, it
  reads the README first. The routing is part of what is being tested.
- **It obeys what is printed, literally.** It runs the command as written,
  including the one that is obviously a typo. "Obviously" is the thing under
  test. Where a printed command fails, that is a finding and the walk records
  it before working around it.
- **It uses no knowledge the documents did not give it.** This is the rule that
  makes a walk different from a review, and the hardest one to hold: a capable
  reader can repair almost any document from general knowledge, silently, and
  report that everything worked. If the walker fixes something the documents
  never told it how to fix, the fix is a **finding**, recorded with what it had
  to invent.
- **There is no coach.** Nobody answers its questions mid-walk. A walker who
  can ask is testing your availability, not your document. If it is stuck, the
  document is where it got stuck, and that is the result.
- **It holds HALT authority.** Any lane, at any depth, may stop and return
  `HALT` with a reason: a contradiction it cannot resolve, an instruction that
  would destroy something it cannot restore, a fence it would have to cross. A
  walk that cannot stop will invent a way to continue, and the invention is the
  thing you least want in the report.

**One more rule, for the report:** every finding carries what it cost —
minutes, retries, or the work it had to author itself. A finding with no cost
attached cannot be triaged against the others.

---

## 3. Persona variation — one walker is one reader

The same document fails differently for different readers, and a single walk
measures a single reader. Vary the persona deliberately and record which one
produced which finding.

The axes that have actually produced distinct findings here:

| Axis | Why it separates |
|---|---|
| **Platform and shell** | Windows/pwsh against Linux/bash is the single most productive axis. A command block that runs everywhere is a claim, and it is usually false the first time. |
| **Reading style** | A literalist reads every line; a skimmer reads headings, code blocks and checkpoints only. Both are real readers. The skimmer finds what your prose was carrying that your commands were not. |
| **Prior state** | An empty directory against a repository that already exists. This kit assumed the empty case for a long time and every one of the resulting findings was invisible until somebody walked the other one. |
| **Role** | Someone following the steps against someone deciding whether to adopt at all. The evaluator does not run your commands; it reads for claims the material cannot support. |

**Persona is instruction, not costume.** "You are impatient" produces nothing.
"Read only headings, code blocks and checkpoint lines; do not read explanatory
prose" produces findings, because it is a rule the walker can obey and you can
check it obeyed.

---

## 4. Findings cite `document:line`

Every finding names the file and the line it came from. Not the section, not
the gist — the line.

Three things follow, and they are the whole reason for the rule:

- **The fix is unambiguous.** A citation is a place to edit. A vibe is a
  discussion.
- **The finding is checkable by someone who was not there.** A reader with the
  commit and the line number can decide for themselves whether the finding is
  real, which is what makes a self-administered study worth publishing at all.
- **It disciplines the walker.** A finding that cannot be cited is usually a
  preference. Requiring the citation is how preferences are filtered out
  without anyone having to argue about them.

Verbatim goes in the report as verbatim: the command as printed, the output as
received, the checkpoint as stated beside what actually appeared. A paraphrased
error message is a finding nobody can act on.

---

## 5. Errata: the register row and the fix land together

A walk produces findings; the walk's value is what you do next, and the trap is
letting the two separate.

- **Every finding gets an explicit disposition** — fixed, recorded open with a
  fix shape, or rejected below the materiality bar with a one-line reason.
  Silent skips are forbidden in both directions: neither a finding that quietly
  vanishes nor one that is polished forever.
- **The register row and the fixes land in the same commit.** A findings
  register that trails the code by a week is a register nobody trusts, and a
  fix with no row is a change nobody can trace to the reason it was made. This
  kit keeps that register in `KNOWN-ISSUES.md`, one section per round, and
  rows are never deleted — a fixed finding keeps its row and gains a
  disposition, so the record of what was once wrong survives the fix.
- **Residuals are stated.** Where a fix closes most of a finding, say what it
  did not close, in the row.

**Between walkers, errata is a handoff.** The next walker reads the fixed
document, not the previous walker's report. Handing a walker the last report
tells it what to find, which is the fastest way to manufacture agreement
between two runs that were supposed to be independent. Keep them spec-side:
the document, the commit, the charter, and nothing else.

---

## 6. When to stop

Walking is a discovery loop, and discovery loops need a cap declared before
they start. The rules are in module 01's standing rules, under **"WHEN THE LOOP
ENDS"**; two of them decide how a walk programme terminates.

- **Declare the cap up front** — how many walks, or how many rounds of
  walk-and-fix, this campaign is worth. A loop that cannot say in advance what
  would be enough will not stop on its own.
- **Closing at the cap with findings still arriving is a legitimate close, and
  it is recorded honestly: AT CAP, NOT-DRY.** That is a structural finding
  about the document, not a failure of the walk. The dishonest close is the one
  that reports "no further findings" when what happened was "we ran out of
  budget".

Two signals worth watching across rounds. **Diminishing severity:** each
round's worst finding should be less severe than the last round's. If it is
not, the document needs a redesign rather than another round. **Escape rate:**
the share of findings an existing check should have caught. If a walk keeps
finding things your own checks were green over, the fix is the check, not the
document.

---

## 7. What a walk cannot do

State this wherever you publish the results, because a reader will otherwise
assume more than the method supports.

- **A walk tests the commands, not the prose.** A step whose explanation is
  wrong while its commands still work will pass every walk you ever run.
- **A walk is not verification.** It is one reader's pass through one tree on
  one machine. It finds what that reader hit; it says nothing about what a
  different reader would have hit.
- **If your walkers are language models, say so, everywhere.** They are a real
  instrument and a cheap one, and they are not people. Describing an
  LLM-persona walk as "an independent adoption test" or "a fresh reader" reads
  to everyone else as a person, and the correction always costs more than the
  disclosure would have. This kit made that mistake, had it found in an
  adversarial read, and relabelled the whole repository; `README.md` in this
  directory carries the result.
