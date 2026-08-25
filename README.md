# OAR — Orchestration & Agent Rails

**Process governance for AI-agent software development, shipped as plain
files.** OAR is a scaffold you drop into a repository where AI agents build
software: standing rules the agents are onboarded under, permission hooks that
enforce those rules mechanically, a certification runner whose green can be
proven real, and ledgers that turn the owner's rulings into permanent checks,
or record why they could not be. Stock Python, no dependencies, no service,
nothing to install.

**Rails, not a runtime.** OAR does not schedule, route, or execute agents. It
composes with whatever framework does.

**The problem it exists for:** an agent stack can tell you what the agents
did. It cannot tell you whether the green was real — whether the checks a
project trusts actually ran, and have ever been seen to fail. OAR makes that
answerable.

**What it is not:** a security boundary (`docs/SECURITY-SCOPE.md` states this
in full), an agent framework, or a finished enterprise product — it is
single-owner today, with team adoption in active design (Project status,
below).

---

## Pick a door

- **`DECISION-BRIEF.md`** — deciding whether to adopt it: what it buys,
  what it costs, what it deliberately does not do. Three minutes.
- **The demonstration, below** — real certification-gate output from an
  existing project of the same owner, before and after one kit-governed
  improvement.
- **`LEVEL-1.md`** — adopting it: 30–45 minutes, reversible, no code
  installed into your repository.
- **`ONBOARD.md`** — you are an AI agent that has been told to adopt this.
- **`COMPARISON.md`** — the claims audit: each load-bearing claim classified
  against named live artifacts.

---

## The demonstration

The kit's Level 1 was adopted into a two-year-old internal AI advisory project
— an existing codebase, not a scratch repository; the same owner's project,
built before this program and never previously governed by it — and one
improvement was then executed by a zero-context agent under the kit's
discipline:
make that project's certification gate unable to certify a test suite that
never ran.

Its own gate, before and after:

```
BEFORE   ✓ smoke_test  88 pass  |  0 FAIL  |  0 warn  |  32 skip
         => GREEN — this tree is golden                                   (exit 0)

AFTER    ✓ smoke_test  SMOKE: PASS - 120 checks selected  |  88 pass  |  0 FAIL  |  0 warn  |  32 skip (27% skipped)
         ✓ behavioral  behavioral_api: PASS - 30/30 assertions ran, 30 passed, 0 failed
         => GREEN — this tree is golden                                   (exit 0)
```

Both say GREEN. The difference is that the second one says what ran. In the
before state the behavioral suite had executed **zero of its thirty
assertions** and the gate could not tell.

Five states, where the old gate printed one:

| # | What was true of the tree | What the gate printed |
|---|---|---|
| 1 | the suite never ran, and nothing was wrong with the tree | `(skip: fixture customer '<fixture>' not present)`, exit 0 — and the gate above it read GREEN |
| 2 | the same tree, after the gate line landed and before the fixture did | `behavioral_api: PARTIAL - COLLAPSED COLLECTION: 0 of 30 assertions ran - the net did not execute`, then `=> RED — NOT golden, do not ship`, exit 1 |
| 3 | the fixture present, every assertion executed | `behavioral_api: PASS - 30/30 assertions ran, 30 passed, 0 failed`, exit 0 |
| 4 | negative control — the fixture hidden, no test file edited | `behavioral_api: PARTIAL - COLLAPSED COLLECTION: 0 of 30 assertions ran - the net did not execute`, exit 1 |
| 5 | planted regression — one data row changed, no test file edited | `behavioral_api: FAIL - 30/30 assertions ran, 29 passed, 1 FAILED`, exit 1 |

Rows 4 and 5 are the part that makes rows 1–3 mean anything: the gate was
proven red twice without editing a test file. `PARTIAL - 0 of 30 ran` and
`FAIL - 30/30 ran, 1 FAILED` are different sentences; the old gate printed the
same thing for both, and for a clean run.

Those lines are quoted from the run that produced them. The host is described
generically on purpose and the fixture path is redacted as `<fixture>`;
nothing else in them was changed. The full account — three cold reads of this
kit by personas who had never seen it, the adoption, the fix, and the first
escape rate that project ever computed — is in
[`docs/CASE-STUDY-INCREMENT.md`](docs/CASE-STUDY-INCREMENT.md), including
what it does not establish.

---

## Quickstart

Clone this repository. Nothing is installed: every executable here is stock
Python 3.10+ with no dependencies, and `docs/PREREQUISITES.md` states the
four things you need.

Three commands, and none of them writes to your project:

```bash
python tools/adoption_smoke.py --plant-f1
python tools/kit_doctor.py --root .
python modules/04-ledgers/escape_rate.py --ledger KNOWN-ISSUES.md
```

The first plants a known defect into a throwaway adoption and requires the
kit's own gate to catch it — it exits 2 and prints `This run certifies
nothing`. The second runs the diagnostic against this tree and returns
ATTENTION, which is explained under Project status below. The third computes
the kit's own miss rate from the register's table.

The doors are above; `docs/START-HERE.md` routes the rest.

---

## If you read nothing else

Three artifacts, each a check you can run rather than a claim to accept:

- **The escape table** — `KNOWN-ISSUES.md`, "The kit's own numbers": the share
  of findings this kit's own checks should have caught, per round, with
  denominators, including the rounds where it rose. Computed on every
  certifying run, not asserted in a sentence.
- **`COMPARISON.md`** — every load-bearing claim classified against named live
  artifacts, including where an incumbent does the job better. It opens with
  the procedure for checking the rows yourself.
- **`docs/walks/`** — the prompts behind the persona adoption walks and
  evaluation reads this register counts, published so the method can be
  disputed rather than trusted; the directory's own README states exactly
  which register entries it covers.

**Most of the words in this repository were written by an AI under one human
owner's supervision. The machinery that keeps those words honest is what the
kit ships.**

---

## Module map

| Module | What it gives you | Runs on day one? |
|---|---|---|
| **01-governance** | The standing-rules document (tiering, HALT authority, hygiene, stage-close checklist, oracle manufacture, promotion/demotion) and four charter templates: implementer, spec-side reviewer, scout, synthesis writer. | Prose — yes |
| **02-enforcement** | A PreToolUse gate (model tiers, blanket-add ban, optional protected-path tripwire with *cert-green pre-authorization* — a token the coordinator mints at a fully certified run, which lets writes into the protected path through without prompting for as long as the certified tree is unchanged, and lapses the moment it is not), the harness wiring, and a fixture harness with a dead-man clause that runs as shipped. | **Yes — executable** |
| **03-verification** | A certification-runner skeleton: required-line judging, numeric floors, the PASS/FAIL/INSTRUMENTED/PARTIAL exit contract, a built-in negative-control facility, a judge-paths-clean gate, a `hooks` gate that certifies the enforcement layer, an `escapes` gate that publishes your escape rate against a ceiling, a startup assertion that refuses to run when the paths it judges are missing, and a `--selftest` that judges the judges. Includes `ORACLE-WORKSHEET.md`: how to manufacture a check when none comes free. | **Yes — executable** |
| **04-ledgers** | Four skeletons: judgment ledger (ruling → check, plus the machine-read escape-rate table), failure floor (rule → layer + zone + last-fired), lessons (numbered, status-marked, thirteen portable seeds), token ledger (actuals + process/implementation ratio + rework). Plus `escape_rate.py`, the instrument for the headline metric: it computes the escape rate from the judgment ledger's table, prints a required output line, and is what module 03's `escapes` gate runs. | Documents — yes; the tool is executable and optional |
| **05-statusboard** | A status line showing live agents and their model tiers, a terrain-colored context bar with a clear mark, a sidequest banner with a staleness amber, and an opt-in escape-rate segment that renders module 04's number and a per-round sparkline (the Python board only — the pwsh variant does not carry that segment). Two implementations of one contract: portable Python (`tools/statusline.py`; `--selftest` renders all four banner states) and a pwsh variant. Includes the flag-file contract. | **Yes — executable** |
| **06-sidequest** | A bounded-detour skill: snapshot first, flag lifecycle, explicit close, durable record. | Prose — yes |
| **07-ci** | A CI workflow that pins and checksum-verifies its toolchain, selftests the judges first, and asserts an exact exit code. Includes `BRANCH-PROTECTION.md`, which distinguishes tripwire from gate. | After slot substitution |
| **08-collaboration** | Eight evidenced defaults, a five-question seed interview, and a living-profile scaffold written from evidence rather than self-description — plus an optional pre-filled calibration an owner can be walked down instead of the blank page, and the sync-capsule doctrine (`CAPSULE.md`): a governed record of the working relationship, its fold rules, and what about it is unmeasured. | Documents — yes |

Modules are separately adoptable and coupled only through documented file
contracts. Every module README states its contract and what breaks if you take
the module alone. `docs/ADOPTION-LEVELS.md` says which to take first.

---

## Project status

**Ready today for a single owner, or a team with one owner who holds the
certification.** That is the configuration the reference build ran in and the
one the LLM-persona adoption walks measured.

**`kit_doctor.py` reports ATTENTION on this kit's own tree, and that is
deliberate.** If the diagnostic returned green on its own author's
repository, that green would be untested. What it currently reports is that
some of the kit's own example gates carry no page recording what they catch
and what they looked like red — and it prints the step that fixes it.

**Multi-seat team adoption is in active design** — the one gap between the
current state and full team use. The kit is written throughout for one
committed settings file, one owner role, one certification token; none of
that is wrong for a team, it is simply undecided, and deciding it well is the
current design focus. `ROADMAP.md` tracks it, and `KNOWN-ISSUES.md` under
"Whose settings file?" records the fix shape. "Enterprise-ready" for OAR means
that design landing; it is coming, not here.

One person maintains this kit, working with AI agents, on a best-effort basis.
There is no SLA. Issues are read; fixes land when the materiality bar says
they should. The bus factor is one and that is disclosed rather than dressed
up — the same standard this kit asks of every control it ships. If that risk
is disqualifying for your organization, the label gave you the information
you needed.

The evidence base is one reference build; seven **LLM-persona adoption
walks** — a language model given a persona and a scratch repository, not a
person; six **LLM-persona evaluation reads** (three of the shipped kit,
three of the kit plus a brownfield host); one read by a practising engineer
outside the program; and one executed brownfield increment
(`docs/CASE-STUDY-INCREMENT.md`). `KNOWN-ISSUES.md` records what each found;
`docs/walks/` publishes the prompts for the walks and the persona reads and
states exactly which register entries it covers — the human read has no
prompt to publish. A human adoption walk is planned and not yet on record. `docs/ADOPTION-TESTS.md` carries the per-module results.

Version `0.1.0`. Apache-2.0.

---

## Security scope

**This kit is not a security boundary, and no part of it should be presented
to a security reviewer as one.** It governs correctness, cost and process
integrity — the failure modes of an honest agent doing competent work badly.
It does not defend against a hostile agent, prompt injection, credential
exfiltration, or your supply chain, and `docs/SECURITY-SCOPE.md` states each
of those in full, along with the two mechanisms here that look stronger than
they are.

---

## Where the rest of it went

The long-form material moved out of this file in round 30 so that the front
door leads with something you can run. Nothing was deleted.

Every row below names a path under `docs/`:

| Read this | For |
|---|---|
| `docs/START-HERE.md` | the full routing by reader — agent, decider, adopter, evaluator — with the budgets |
| `docs/CASE-STUDY-INCREMENT.md` | the brownfield increment behind The demonstration, and its limits |
| `docs/PREREQUISITES.md` | the four things you need, and the version floor deliberately not invented |
| `docs/ADOPTION-LEVELS.md` | what Levels 1, 2 and 3 each install and cost |
| `docs/POSITIONING.md` | conduct rather than composition, and the three named neighbours |
| `docs/WHY-FILES.md` | why the controls are plain files, and what kind of process can run on these rails |
| `docs/AT-SCALE.md` | per-seam rather than per-mass, and the three places it breaks |
| `docs/SECURITY-SCOPE.md` | what this kit does not defend against, in full |
| `docs/PORTABILITY.md` | what ports as-is, what the wiring costs to translate, and the evidence caveat |
| `docs/ADOPTION-TESTS.md` | the per-module walk results, including the two that failed |
| `docs/REPOSITORY-LAYOUT.md` | every file in this repository and what it is for |
| `docs/walks/` | the prompt behind every published walk, and the method for your own documents |

---

## The doctrine in one paragraph

The product of a serious build is not the build. It is the growing set of
permanent, executable checks that capture the owner's judgment, so no ruling
ever has to be sampled from a human twice. Every punch item is an un-automated
test that has just revealed itself. Agents are governed exactly enough to keep
that loop honest, and every control is labeled with whether the agents it
governs could rewrite it — a rule enforced by the hands it binds is a real
rule with an honest name, and a rule pretending otherwise is a hazard.
