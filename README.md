# OAR — Orchestration & Agent Rails

**Process governance for AI-agent software development, shipped as plain
files.** OAR is a scaffold you drop into a repository where AI agents build
software. It provides standing rules for agent onboarding, permission hooks
that enforce those rules, a certification runner whose green can be proven
real, and ledgers that turn owner rulings into permanent checks. Stock
Python, no dependencies, no service, nothing to install.

OAR is not a runtime. It does not schedule, route, or execute agents. It
composes with whatever framework does.

**The problem:** an agent stack can tell you what the agents did. It cannot
tell you whether the green was real: whether the checks actually ran, and
whether anyone has watched one refuse. OAR makes the first answerable and
the second askable per check. Every check declares where its expectation
comes from and carries a `seen_red` field: the date of its last recorded
forced red, or NEVER. At version 0.1.0, 35 of the 208 rows in the check
registry (`checks-registry.json`) carry a date and 173 are NEVER;
`python tools/expectation_lint.py` prints that ratio on every run.

**What it is not:** a security boundary (`docs/SECURITY-SCOPE.md` states
this in full),
an agent framework, or a finished enterprise product. It is single-owner
today; team adoption is in active design (Project status, below).

---

## Pick a door

- **[`DECISION-BRIEF.md`](DECISION-BRIEF.md)**: deciding whether to adopt: what it buys, what
  it costs, what it deliberately does not do. Three minutes.
- **The demonstration, below**: real certification-gate output, before and
  after one kit-governed improvement.
- **[`LEVEL-1.md`](LEVEL-1.md)**: adopting the documents: 30–45 minutes, reversible, no
  code installed into your repository.
- **[`QUICKSTART.md`](QUICKSTART.md)**: the full adoption, all modules: 90
  minutes to two hours, plus an afternoon for your first
  [oracle](GLOSSARY.md).
- **[`ONBOARD.md`](ONBOARD.md)**: you are an AI agent told to adopt this.
- **[`COMPARISON.md`](COMPARISON.md)**: the claims audit: each load-bearing
  claim classified against named live artifacts.
- **[`KNOWN-ISSUES.md`](KNOWN-ISSUES.md)**: the escape table: the kit's own
  miss rate per round, with denominators, computed on every certifying run.
- **[`docs/walks/`](docs/walks/)**: the published prompts behind the kit's
  persona walks and evaluation reads, with exact coverage stated.

---

## The demonstration

The kit's Level 1 was adopted into a two-year-old internal AI advisory
project: an existing codebase, same owner, built before this program. One
improvement was then executed under the kit's discipline by an agent with
no program context: make the
project's certification gate unable to certify a test suite that never ran.

The gate, before and after:

```
BEFORE   ✓ smoke_test  88 pass  |  0 FAIL  |  0 warn  |  32 skip
         => GREEN — this tree is golden                                   (exit 0)

AFTER    ✓ smoke_test  SMOKE: PASS - 120 checks selected  |  88 pass  |  0 FAIL  |  0 warn  |  32 skip (27% skipped)
         ✓ behavioral  behavioral_api: PASS - 30/30 assertions ran, 30 passed, 0 failed
         => GREEN — this tree is golden                                   (exit 0)
```

Both say GREEN. The second says what ran. In the before state, the
behavioral suite had executed zero of its thirty assertions and the gate
could not tell.

Five states, where the old gate printed one:

| # | What was true of the tree | What the gate printed |
|---|---|---|
| 1 | the suite never ran, and nothing was wrong with the tree | `(skip: fixture customer '<fixture>' not present)`, exit 0 — and the gate above it read GREEN |
| 2 | the same tree, after the gate line landed and before the fixture did | `behavioral_api: PARTIAL - COLLAPSED COLLECTION: 0 of 30 assertions ran - the net did not execute`, then `=> RED — NOT golden, do not ship`, exit 1 |
| 3 | the fixture present, every assertion executed | `behavioral_api: PASS - 30/30 assertions ran, 30 passed, 0 failed`, exit 0 |
| 4 | negative control — the fixture hidden, no test file edited | `behavioral_api: PARTIAL - COLLAPSED COLLECTION: 0 of 30 assertions ran - the net did not execute`, exit 1 |
| 5 | planted regression — one data row changed, no test file edited | `behavioral_api: FAIL - 30/30 assertions ran, 29 passed, 1 FAILED`, exit 1 |

Rows 4 and 5 prove the gate can go red without a test file being edited.
The output lines are quoted from the run that produced them; the host is
described generically and the fixture path is redacted as `<fixture>`.
The full account, including what it does not establish, is in
[`docs/CASE-STUDY-INCREMENT.md`](docs/CASE-STUDY-INCREMENT.md).

---

## Quickstart

Clone this repository. Nothing is installed: every executable is stock
Python 3.10+ with no dependencies; `docs/PREREQUISITES.md` lists the
four things you need.

Three commands. None writes to your project:

```bash
python tools/adoption_smoke.py --plant-f1
python tools/kit_doctor.py --root .
python modules/04-ledgers/escape_rate.py --ledger KNOWN-ISSUES.md
```

1. Plants a known defect into a throwaway adoption; the kit's own gate must
   catch it (exit 2, `This run certifies nothing`).
2. Runs the diagnostic against this tree; returns ATTENTION (see Project
   status).
3. Computes the kit's own miss rate from the escape table in
   `KNOWN-ISSUES.md`.

`docs/START-HERE.md` routes the rest.

---

## If you read nothing else

Three artifacts, each a check you can run rather than a claim to accept:

- **The escape table**: `KNOWN-ISSUES.md`, "The kit's own numbers": the
  share of findings the kit's own checks should have caught, per round,
  with denominators, including the rounds where it rose.
- **`COMPARISON.md`**: every load-bearing claim classified against named
  live artifacts, including where an incumbent does the job better.
- **`docs/walks/`**: the prompts behind the persona adoption walks and
  evaluation reads, published so the method can be disputed.

Most of the words in this repository were written by an AI under one human
owner's supervision. The machinery that keeps those words honest is what
the kit ships.

---

## Module map

| Module | What it gives you | Runs on day one? |
|---|---|---|
| **01-governance** | The standing-rules document (tiering, HALT authority, hygiene, stage-close checklist, oracle manufacture, promotion/demotion) and five charter templates: implementer, spec-side reviewer, scout, synthesis writer, hostile reader (the Principal Skeptic evaluation persona). | Documents only |
| **02-enforcement** | A PreToolUse gate (model tiers, blanket-add ban, optional protected-path tripwire with cert-green pre-authorization), the harness wiring, and a fixture harness with a dead-man clause that runs as shipped. | **Yes — executable** |
| **03-verification** | A certification-runner skeleton: required-line judging, numeric floors, the PASS/FAIL/INSTRUMENTED/PARTIAL exit contract, a negative-control facility, a judge-paths-clean gate, a `hooks` gate, an `escapes` gate with a ceiling, a startup assertion, and `--selftest`. Includes `ORACLE-WORKSHEET.md`. | **Yes — executable** |
| **04-ledgers** | Four skeletons: judgment ledger, failure floor, lessons, token ledger. Plus `escape_rate.py`, which computes an escape rate from a judgment ledger's table (your project's own, once adopted; this kit points it at its escape table in `KNOWN-ISSUES.md`) and is what module 03's `escapes` gate runs. | Documents — yes; the tool is executable and optional |
| **05-statusboard** | A status line: live agents with model tiers, a context bar with a clear mark, a sidequest banner with a staleness amber, an opt-in escape-rate segment (Python board only). Two implementations of one contract (`tools/statusline.py --selftest`; pwsh variant). Includes the flag-file contract. | **Yes — executable** |
| **06-sidequest** | A bounded-detour skill: snapshot first, flag lifecycle, explicit close, durable record. | Documents only |
| **07-ci** | A CI workflow that pins and checksum-verifies its toolchain, selftests the judges first, and asserts an exact exit code. Includes `BRANCH-PROTECTION.md`. | After slot substitution |
| **08-collaboration** | Eight evidenced defaults, a five-question seed interview, a living-profile scaffold, an optional pre-filled calibration, and the sync-capsule doctrine (`CAPSULE.md`). | Documents — yes |

Modules are separately adoptable and coupled only through documented file
contracts. Every module README states its contract and what breaks if you
take the module alone. `docs/ADOPTION-LEVELS.md` says which to take first.

---

## Project status

**Ready today for a single owner, or a team with one owner who holds the
certification.** That is the configuration the reference build ran in and
the one the adoption walks measured.

`kit_doctor.py` reports ATTENTION on this kit's own tree, deliberately:
some of the kit's own example gates carry no page recording what they catch
and what they looked like red. The diagnostic prints the step that fixes it.

**Multi-seat team adoption is in active design**: the one gap between the
current state and full team use. The kit assumes one committed settings
file, one owner role, one certification token. `ROADMAP.md` tracks the
design; `KNOWN-ISSUES.md` under "Whose settings file?" records the fix
shape.

One person maintains this kit, working with AI agents, best-effort. No SLA.
The bus factor is one.

The evidence base: one reference build; seven LLM-persona adoption walks
(a language model given a persona and a scratch repository, not a person);
six LLM-persona evaluation reads (three of the shipped kit, three of the
kit plus a brownfield host); one read by a practising engineer outside the
program; one executed [brownfield](GLOSSARY.md) increment
(`docs/CASE-STUDY-INCREMENT.md`). `KNOWN-ISSUES.md` records what each
found; `docs/walks/` publishes the prompts and states exact coverage — the
human read has no prompt to publish. A human adoption walk is planned and
not yet on record. `docs/ADOPTION-TESTS.md` carries per-module results.

Version `0.1.0`. Apache-2.0.

---

## Security scope

**This kit is not a security boundary.** It governs correctness, cost, and
process integrity: the failure modes of an honest agent doing competent
work badly. It does not defend against a hostile agent, prompt injection,
credential exfiltration, or your supply chain. `docs/SECURITY-SCOPE.md`
states each limit in full, plus the two mechanisms that look stronger
than they are.

---

## Where the rest of it went

The long-form material moved out of this file into `docs/`. Nothing was
deleted.

Every row below names a path under `docs/`:

| Read this | For |
|---|---|
| `docs/START-HERE.md` | routing by reader — agent, decider, adopter, evaluator — with budgets |
| `docs/CASE-STUDY-INCREMENT.md` | the brownfield increment behind The demonstration, and its limits |
| `docs/PREREQUISITES.md` | the four things you need |
| `docs/ADOPTION-LEVELS.md` | what Levels 1, 2 and 3 each install and cost |
| `docs/POSITIONING.md` | conduct rather than composition; the three named neighbours |
| `docs/WHY-FILES.md` | why the controls are plain files |
| `docs/AT-SCALE.md` | per-seam rather than per-mass; the three places it breaks |
| `docs/SECURITY-SCOPE.md` | what this kit does not defend against, in full |
| `docs/PORTABILITY.md` | what ports as-is, what the wiring costs to translate |
| `docs/ADOPTION-TESTS.md` | per-module walk results, including the two that failed |
| `docs/REPOSITORY-LAYOUT.md` | every file in this repository and what it is for |
| `docs/walks/` | the prompts for the walks; which entries have none |

---

## The doctrine

The product of a serious build is the growing set of permanent, executable
checks that capture the owner's judgment. Every [punch item](GLOSSARY.md) is an
un-automated test that has just revealed itself. Every control is labeled
with whether the agents it governs could rewrite it.
`BLUEPRINT.md` carries the full operating architecture.
