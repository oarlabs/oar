# The adoption walks — what they were, and what you can check

Every adoption test behind this kit's finding counts was performed by a
**large language model running a written persona**, not by a person. No human
has walked `QUICKSTART.md` end to end and reported findings. This directory
publishes the prompts that produced those walks so a reader can judge the
evidence rather than take the counts on trust.

`KNOWN-ISSUES.md` is the authority for what each walk found and what state each
finding is in. These pages are the provenance record behind it.

**Want to run this method on your own documentation?**
[WALKING-YOUR-OWN-DOCUMENTS.md](WALKING-YOUR-OWN-DOCUMENTS.md) is the method
itself, written for an adopter: the preflight, the fresh-reader lane spec,
persona variation, the citation rule, how errata lands, and when to stop. This
page is what the method produced here; that page is how to do it there.

---

## The two kinds of run, kept apart

They are different instruments and the kit does not blur them.

| | **LLM-persona adoption walk** | **LLM-persona evaluation read** |
|---|---|---|
| What it did | Created a throwaway git repository and executed every `QUICKSTART.md` command in it, in printed order | Read the shipped repository only. No scratch project, no command execution beyond read-only selftests |
| Register entries | 8–14 (seven walks) | 17 (three reads) and 30 (three recon reads) |
| Pages here | `walk-08-…` through `walk-14-…` | `evaluation-reads.md`; `read-30-recon-…` (three pages) |
| What it can find | A command that does not run as printed; a checkpoint that does not match; a step unreachable where placed | A claim the shipped material contradicts or cannot support |

Entry 30's three reads are a variant of the evaluation read: each persona
read this kit's public tree cold AND a private brownfield host read-only,
and returned a kit verdict plus a prioritized improvement plan for the host.
Their prompts are published here with the redactions each page discloses;
the reports they produced are program records and are summarized in
`docs/CASE-STUDY-INCREMENT.md`. The fourth lane of that exercise — the
executed increment — ran from a prompt built live around the recon
consensus and is quoted, with its outputs, in the case study rather than
published as a fixed charter page.

Entries 1–7 predate this loop: they are pre-ship module tests and one release
audit, run by the same kind of persona but without the fixed adoption charter
these seven share. Entries 15, 16 and 18 are not walks at all. Entry 29 is a
human read with no prompt to publish. The timeline in `KNOWN-ISSUES.md` is
what every entry number means.

---

## The seven adoption walks

| Entry | Persona | Ran against | Findings, per the register | Page |
|---|---|---|---|---|
| 8 | Windows/pwsh literalist, no coach | `341d47d` | 13 (2 major, 8 minor, 3 nit) | [walk-08-windows-literalist.md](walk-08-windows-literalist.md) |
| 9 | Linux/bash conventions on a Windows host | `d915ee5` | 7 (1 major, 3 minor, 3 nit) | [walk-09-linux-bash.md](walk-09-linux-bash.md) |
| 10 | Impatient skimmer — headings, code blocks, checkpoints only | `262077e` | 9 findings + 1 end-state item | [walk-10-impatient-skimmer.md](walk-10-impatient-skimmer.md) |
| 11 | Team-lead evaluator: doctrine first, then the walk, then a second machine | `641b392` | 18 (7 major, 7 minor, 4 nit) | [walk-11-team-lead-evaluator.md](walk-11-team-lead-evaluator.md) |
| 12 | Dry-test literalist: full re-walk plus end-state audit | `b50e1d6` | 6 (1 major, 2 minor, 3 nit) | [walk-12-dry-test-literalist.md](walk-12-dry-test-literalist.md) |
| 13 | Thorough adopter: walk, audit, doctrine spot-checks | `404da28` | 6 (0 major, 3 minor, 3 nit) | [walk-13-thorough-adopter.md](walk-13-thorough-adopter.md) |
| 14 | Final cap walk: walk, audit, doctrine and module-README spot-checks | `d08b925` | 8 (0 major, 4 minor, 4 nit) | [walk-14-final-cap.md](walk-14-final-cap.md) |

The three evaluation reads of entry 17 are on
[evaluation-reads.md](evaluation-reads.md).

The **"ran against"** column is the kit commit the walk started from. Each is
verifiable: the walk's own errata commit is the next one in `git log` that
names it, so `git show <sha>` is the tree the persona actually read.

---

## What is published here, and what is not

**Published:** the prompt each persona was given, verbatim except for the
redactions described below; the charter framing (persona, method, halt
authority, handoff contract); the finding count the register carries; and a
short distillation of what the run did.

**Not published, and it matters:**

- **The raw lane transcripts.** The program that ran these walks retains
  transcripts for the current phase plus one and distills each lane into a
  per-agent record before pruning. These walks are outside that window. The
  transcripts are gone; they are not withheld, and they are not attached
  anywhere.
- **The full per-walk reports.** Each persona wrote a findings report — persona
  recap, step log, findings table with severities, end-state audit, verdict.
  Those reports live in a private program repository, not in this kit. Their
  findings reach the public record through `KNOWN-ISSUES.md`, where every one is
  listed with its disposition.
- **Internal session and agent identifiers**, which identify runs inside a
  private orchestration record and would mean nothing to a reader here.

The model family is **not** on that list, because withholding a name this
repository prints on every adoption path would be a redaction that conceals
nothing. All thirteen runs — seven walks, three evaluation reads, and three
recon reads — are recorded in the distilled agent records as `model opus`:
Anthropic's Claude, top tier. That is
the single family `BLUEPRINT.md` §11 means when it states the evidence limit as
"one AI family".

### What a reader can and cannot verify from this directory

You can verify the **instrument**: the prompts are here in full — every
instruction, with only the redactions in the table above, each disclosed on the
page that carries it — so you can read exactly what each persona was told to do,
what it was told to count as a finding, and what it was forbidden to do. You
can verify the **subject**: each page names the commit the walk ran against,
and this repository's history contains it. You can verify the **response**: the errata commit that follows
each walk is in the same history, and `KNOWN-ISSUES.md` records every finding
and its disposition. You can re-run the experiment: the prompts are
reproducible instructions, and running one against a named commit is the one
check nobody here can perform for you.

You cannot verify the **execution**. There is no transcript proving that the
persona ran the commands it reported running, and no independent party observed
the runs. The counts in `KNOWN-ISSUES.md` rest on each persona's own report,
read and dispositioned by the kit's single maintainer. Treat them as what they
are: a self-administered study with its method published, not third-party
evidence.

---

## Redaction conventions

These prompts were written for a private machine and a private program
repository. Everything that identified either has been replaced by a
placeholder, marked at the point of elision:

| Placeholder | What it replaced |
|---|---|
| `<KIT>` | The absolute path of the kit checkout on the maintainer's machine |
| `<SCRATCH>` | The absolute path of the throwaway adoption repository's parent directory — which carried the orchestration session's identifier, so that identifier goes with it — and the session scratch root where a prompt named it by directory name |
| `<HANDOFF-DIR>` | The absolute path of the coordinator's report handoff directory |
| `<PROGRAM-REPO>` | The private program repository the walks were coordinated from |
| `<PROTECTED-PATH>` | A directory the program's protected-path tripwire covers |
| `<COORDINATOR-TIER>` | The program's internal codename for the tier its coordinating session runs on, quoted inside a tiering constraint. The model family that ran the recorded lanes stays named above — what is withheld is a private program label, not the evidence's family |
| `<PUBLIC-REPO-URL>` | The public mirror's hosting address as the prompt printed it — withheld so this tree names no hosting org; a reader of the public repository is already at the address the prompt named |
| `<HOST-DESCRIPTION>` | The brownfield host's description as the recon prompts stated it — product category, runtime stack, and repository layout, which together identify a private project. The release describes that host generically: a two-year-old internal AI advisory project of the same owner |

Nothing else in the prompts was changed, and where a page departs from that at
all it says so on the page — walk 9 collapses a duplicated kit path that would
otherwise print as the same placeholder twice; walks 13 and 14 redact a scratch
root the prompt named in prose. Where a prompt named a report file by name, the
name is kept and only its directory is redacted, so the private record and the
public one can be matched by anyone who holds both.

---

## Why this directory exists

An adversarial evaluation read (entry 17) found that this repository described
these walks in language a reader takes to mean people — "independent adoption
tests", "stranger onboarding", "a fresh reader" — while `BLUEPRINT.md` and
`DECISION-BRIEF.md` recorded that the evidence base was AI personas. That is
the load-bearing evidentiary claim of the kit, contradicting itself inside the
kit. The label is now consistent everywhere, and the prompts are published so
the label can be checked rather than believed.
