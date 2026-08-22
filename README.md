# OAR — Orchestration & Agent Rails

**Your agent stack can tell you what the agents did. It cannot tell you
whether the green was real** — whether the checks a project trusts actually
ran, and have ever been seen to fail. That is the gap OAR fills.

It is a drop-in scaffold for running a multi-agent build with real controls:
governance rules that bind, enforcement hooks that fire, verification that
produces a single exit code, ledgers that record decisions, and a
collaboration contract with the human owner. It was distilled from a
multi-month, multi-agent reference build; each mechanism exists because a
specific failure made it necessary.

**OAR is rails, not a runtime** — it does not schedule, route, or execute
agents, and it composes with the frameworks that do.

---

## Start here

**Deciding whether to adopt at all?** Read **`DECISION-BRIEF.md`** first — one
page: what the kit is and is not, what certifies at each level, what it costs,
what is not shipped, the exit cost, and the limitations most likely to matter
to you. Three minutes.

**Adopting the documents first?** **`LEVEL-1.md`** is the 30–45 minute
entry: four ledgers, a collaboration profile, the standing rules as prose, no
settings file, no hook, and a check that reads what you installed and states
what it does and does not certify. It installs no code into your repository and
it is reversible.

Adopting the whole thing: read **`QUICKSTART.md`** and work through it in
order. Every step ends in output you can run and see; if a step produces no
visible output, it is not finished.

**Adopting into a repository that already exists?** Read
**`EXISTING-PROJECT.md`** alongside it. `QUICKSTART.md` is written for a
repository whose only uncommitted content is the kit's own, and that page is
the measured list of where an existing project departs from that assumption —
an existing `CLAUDE.md` or `.claude/settings.json`, an ignore rule over
`.claude/`, work in progress inside the certified paths, a test suite you
already trust, CI that ends up proving less than the local gate — each with the
behaviour that was measured and the workaround that was proven.

Budget for that walk:

- **90 minutes to two hours** of hands-on work (Step 4, the certification
  runner and its wiring, is 45–60 minutes of that on a first adoption),
- **an afternoon** for your first oracle (Step 3 is design work and does not
  compress),
- **the seed interview** (Step 8): fifteen minutes done the same day if you
  are the project's owner; a scheduled slot on the owner's calendar if that
  is someone else.

Those figures are a sum of per-step estimates, reconciled against walks
performed by LLM personas rather than by people. No human has walked this
document end to end. `docs/walks/` publishes the prompts behind every one of
those walks and states what they do and do not establish.

> **Debian/Ubuntu:** these hosts ship `python3` with no `python` shim unless
> `python-is-python3` is installed. Substitute `python3` in every command;
> nothing else changes.

**Evaluating in depth?** After the brief, read **`BLUEPRINT.md`** for the
doctrine the mechanisms come from, then **`CONTEXT-ARCHITECTURE.md`** for the
full treatment of BLUEPRINT §7 — memory, state and the context window: which
layers hold what, where the boundaries fall, and how the pieces wire together.
Neither is needed to work through `QUICKSTART.md`; both are worth reading
before you decide how much of the kit your project should take.
`KNOWN-ISSUES.md` says what the kit's adoption tests found and what state each
finding is in — every one of them run by an LLM persona, with the prompts
published under `docs/walks/`.

---

## Why files, and where this sits

The kit ships no orchestration graph, no tracing, no eval harness — a
decision, not a gap. Those tools run agents and score outputs. This kit does
a different job: proving that the checks a project trusts exist, ran, have
been seen red, and cannot be rewritten by the process they govern. The
controls are plain files because files are the one artifact the whole
toolchain can hold to account: git versions them and reports their
cleanliness, CI re-judges them on a machine no session touches, and a human
can read them. A graph definition held in a runtime is, under this kit's
threat model, a file the agent can edit — with fewer witnesses.

Running a framework? The layers compose. Keep LangGraph, CrewAI, or whatever
executes your agents; point `GATE_COMMAND` at whatever proves your project
works — the runner judges required output lines and floors from any stack,
and modules 01, 03, 04, 07 and 08 assume nothing about how agents are run.
Module 02's hooks are the one harness-specific layer, and Portability below
says exactly what porting them costs.

---

## Beyond code

The kit assumes nothing about code. It assumes a process whose record can live
in files under git, with checks that can be run and seen to fail — that is the
entire bar. A process that clears it can run on these rails; a process whose
record is a conversation, or whose checks have no red state, cannot, and
adopting the kit will not change that. Three places where the bar has actually
been cleared, all of them inside this program rather than imagined for it:

- **This kit's own program** — documentation and tooling, built under the full
  discipline, and the loop found real defects in rounds that shipped no code:
  `KNOWN-ISSUES.md` round 14 (eight documentation and cross-module-description
  findings) and round 19's prose-only build (three majors, all attribution from
  memory, one an invented quotation).
- **Control validation** — every control names its test and the test has been
  seen to fail, which is what `FAILURE-FLOOR.md` (rule → layer → last fired) and
  `JUDGMENT-LEDGER.md` (ruling → named check, or UNCHECKED) already record. No
  audit has consumed them; the claim is about the shape of the record, not about
  an engagement.
- **The operating collaboration itself** — session forks, owner rulings and the
  collaboration profile run as versioned, gated records in the program this kit
  came out of; what ships here is the machinery, in modules 06, 04 and 08.

**This is not a claim that the kit works for anything.** Where the record is
not files, or the checks cannot be seen red, the rails have nothing to hold.

---

## Security scope

**This kit is not a security boundary, and no part of it should be presented
to a security reviewer as one.**

What it governs is **correctness, cost, and process integrity**: that the
checks a project trusts exist, that they ran, that they have been seen red,
that a verdict is not narrated, that a rule is labeled with whether the agents
it governs could rewrite it, and that the money and rework are written down.
Those are the failure modes of an honest agent doing competent work badly.

What it does **not** defend against:

- **A malicious or hostile agent.** Every control here runs with the same
  privileges as the thing it governs, from files inside the repository that
  thing edits. An agent that decides to route around the gate can edit the
  hook, the fixtures, the config the hook reads, or the settings file that
  wires it. The kit's own zone labels say this in the small: Zone B is
  "useful friction, honestly labeled," and the enforcement hook is Zone B.
- **Prompt injection.** Nothing here inspects, sanitizes, or reasons about the
  content of prompts, tool output, retrieved documents, or web pages. A
  hostile instruction arriving inside a file an agent reads passes through
  every control in this kit untouched.
- **Credential exfiltration.** There is no secret scanning of agent output, no
  egress control, and no network policy. `tools/deident_scan.py` scans a tree
  for tokens *you list yourself* before you publish it; it is a publication
  aid, not a data-loss control, and it cannot see what an agent already sent.
- **Supply chain.** The kit ships stock Python and pins nothing of its own.
  Module 07's CI template checksum-pins the toolchain it downloads, and that
  is the extent of it. Nothing verifies the provenance of your dependencies,
  your models, or this kit.

Two specifics worth naming, because both look stronger than they are:

- **The cert-green token** (`modules/02-enforcement`) is a convenience, not an
  authorization. It is an unsigned JSON file, so anything that can write a file
  can mint one. There is deliberately no signature: an HMAC needs a key, and in
  a harness where the agent runs shell commands as the owner there is nowhere
  to put a key the agent cannot read, so a signature would raise forgery from
  "write a file" to "read a file, then write a file" while making the token
  read as an attestation it is not. `verify.py --mint-cert-token` writes it
  from the runner's single PASS return, and the honest label ships inside the
  file.
- **Three of the PreToolUse hook's four rules are string heuristics.** Points
  1, 3 and 4 — the workflow-script tier count, the blanket-staging ban and the
  protected-path tripwire — match text a human wrote, and each discloses its
  error directions in its own source, including the ones that fail *silently*.
  **No completeness is claimed for any of them.** Point 3's covered list grew
  twice in one week, each time because a reader spent an afternoon on it, and
  the forms still known to walk past it are named where the rule is defined.
  Point 2 — the tier declared on an agent spawn — compares declared fields
  rather than matching text, and is exact. The three heuristics raise the cost
  of a mistake; they do not make one impossible.

If you need a security boundary, put it where boundaries go — separate
credentials, a sandbox or container the agent cannot escape, egress rules, and
review at the merge point by someone the agent cannot be. This kit sits inside
that boundary and makes the work honest. It does not replace it.

`python tools/kit_doctor.py` reports these limits against your own adoption:
what your gates cannot catch, what a blanket commit would sweep up, and what
your cert-green token is and is not.

---

## Project status

**Ready today for a single owner, or a team with one owner who holds the
certification.** That is the configuration the reference build ran in and the
one the LLM-persona adoption walks measured.

**Multi-seat team adoption is in active design** — the one gap between the
current state and full team use. The kit is written throughout for one
committed settings file, one owner role, one certification token; none of
that is wrong for a team, it is simply undecided, and deciding it well is the
current design focus. `ROADMAP.md` tracks it, and `KNOWN-ISSUES.md` under
"Whose settings file?" records the fix shape. "Enterprise-ready" for OAR means
that design landing; it is coming, not here.

One person maintains the kit, working with AI agents, best-effort, no SLA —
see Maintenance below. The evidence base is one reference build plus seven
**LLM-persona adoption walks** — a language model given a persona and a scratch
repository, not a person. `KNOWN-ISSUES.md` records what each walk found and
`docs/walks/` publishes the prompt behind it. A human adoption walk is planned
and not yet on record.

---

## Module map

| Module | What it gives you | Runs on day one? |
|---|---|---|
| **01-governance** | The standing-rules document (tiering, HALT authority, hygiene, stage-close checklist, oracle manufacture, promotion/demotion) and four charter templates: implementer, spec-side reviewer, scout, synthesis writer. | Prose — yes |
| **02-enforcement** | A PreToolUse gate (model tiers, blanket-add ban, optional protected-path tripwire with *cert-green pre-authorization* — a token the coordinator mints at a fully certified run, which lets writes into the protected path through without prompting for as long as the certified tree is unchanged, and lapses the moment it is not), the harness wiring, and a fixture harness with a dead-man clause that runs as shipped. | **Yes — executable** |
| **03-verification** | A certification-runner skeleton: required-line judging, numeric floors, the PASS/FAIL/INSTRUMENTED/PARTIAL exit contract, a built-in negative-control facility, a judge-paths-clean gate, a `hooks` gate that certifies the enforcement layer, an `escapes` gate that publishes your escape rate against a ceiling, a startup assertion that refuses to run when the paths it judges are missing, and a `--selftest` that judges the judges. Includes `ORACLE-WORKSHEET.md`: how to manufacture a check when none comes free. | **Yes — executable** |
| **04-ledgers** | Four skeletons: judgment ledger (ruling → check, plus the machine-read escape-rate table), failure floor (rule → layer + zone + last-fired), lessons (numbered, status-marked, eleven portable seeds), token ledger (actuals + process/implementation ratio + rework). Plus `escape_rate.py`, the instrument for the headline metric: it computes the escape rate from the judgment ledger's table, prints a required output line, and is what module 03's `escapes` gate runs. | Documents — yes; the tool is executable and optional |
| **05-statusboard** | A status line showing live agents and their model tiers, a terrain-colored context bar with a clear mark, a sidequest banner with a staleness amber, and an opt-in escape-rate segment that renders module 04's number and a per-round sparkline (the Python board only — the pwsh variant does not carry that segment). Two implementations of one contract: portable Python (`tools/statusline.py`; `--selftest` renders all four banner states) and a pwsh variant. Includes the flag-file contract. | **Yes — executable** |
| **06-sidequest** | A bounded-detour skill: snapshot first, flag lifecycle, explicit close, durable record. | Prose — yes |
| **07-ci** | A CI workflow that pins and checksum-verifies its toolchain, selftests the judges first, and asserts an exact exit code. Includes `BRANCH-PROTECTION.md`, which distinguishes tripwire from gate. | After slot substitution |
| **08-collaboration** | Eight evidenced defaults, a five-question seed interview, and a living-profile scaffold written from evidence rather than self-description. | Documents — yes |

Modules are separately adoptable and coupled only through documented file
contracts. Every module README states its contract and what breaks if you take
the module alone.

---

## Three adoption levels

### Level 1 — documents only (30–45 minutes) — the path is `LEVEL-1.md`

Take **04-ledgers** and **08-collaboration**. Run the seed interview, or
schedule it when the owner is someone else. Start the four ledgers empty. Add
**01-governance** as prose if you have agents.

`LEVEL-1.md` walks it step by step and ends in a check you can run:
`kit_doctor.py --level1` reads the documents you installed and prints what it
certifies, what it does **not** certify, and what removing the level costs.

No harness assumptions, and **no code installed into your repository** — the
two tools that path uses run from the kit clone against your repo. This level
changes what your project records about itself, which is most of the value, and
it is the reversible one. Start here unless you have a specific reason not to.

### Level 2 — partial (a day)

Add **03-verification**: one command, one exit code, real floors, and a real
negative control. Add **02-enforcement** after a governance rule has failed at
least once — the failure tells you which rule to promote first. Promoting
rules that have never failed grows the rule set until people route around it.

### Level 3 — full (a week, mostly spent on your own gates)

Add **07-ci** for the first control outside the blast radius, then **05** and
**06** for ambient state and bounded detours. Spend the remaining time writing
the gates specific to your project. The kit provides the frame; the checks are
yours.

---

## Portability

**The doctrine is tool-agnostic. The enforcement wiring is not.**

- **Doctrine** — the oracle-manufacturing loop, the enforcement zones, the
  ledgers, the charter anatomy, the collaboration contract, the exit-code
  contract — describes how work gets proven correct. It transfers to any
  stack and any model, including projects with no AI at all.

  **Team adoption is the part that is not documented.** The kit is written
  throughout for one owner and one orchestrator seat, and the mechanics assume
  it: one committed `.claude/settings.json` carrying one machine's absolute
  paths, one `collaboration-profile.md`, one `RATIO_CEILING`, one `OWNER_ROLE`,
  and a per-machine cert-green token. None of that is wrong for a team — it is
  simply undecided, and a team has to decide it on day one. What that costs and
  what shape the answers might take is recorded in `KNOWN-ISSUES.md` under
  "Whose settings file? — the team story".
- **Wiring** — the PreToolUse hook, the settings file, the status line, the
  skill format — assumes a harness that fires pre-tool hooks, lets a spawn
  declare a model, and pipes session JSON to a status-line command. The
  Claude Code harness fits that description and is what the reference build
  ran on.

Under a different harness:

- **Modules 01, 03, 04, 07, and 08 port as-is.** They are documents and a
  Python runner; none of them asks the harness for anything.
- **Module 02** — the decisions port unchanged; the plumbing to translate is
  two functions: `out()`, which emits the decision object your harness
  expects, and the parse inside `judge()` that reads it back.
- **Module 05** ships a portable Python board (`tools/statusline.py`)
  alongside the pwsh one, so it needs no translation.
- **Module 06** — the checklist content is harness-neutral and works as prose
  in any project. The format is not: `SKILL.md` with YAML frontmatter is a
  Claude Code skill file. Elsewhere, paste the body into your standing rules
  under "when interrupted".

**Host coverage is machine-checked.** Every executable is stock Python with no
dependencies, and `.github/workflows/kit-ci.yml` runs the whole core — scanner
selftest, status-board selftest, verify selftest, hook fixtures, the dead-man
case, the adoption smoke and its negative control, and the kit's own
certification — on **ubuntu-latest and windows-latest** on every push. The one
Windows-only file is `statusline.ps1.template`, an optional variant of a
component the Python board already covers.

**Shell:** QUICKSTART's command blocks run in `pwsh`, `bash`, and Git Bash
except in a small number of marked places; QUICKSTART's own "Shell" section is
the authority and lists them all. That claim is machine-checked:
`adoption_smoke.py` phase 9 runs Step 4's block through `pwsh` where pwsh
exists, and reports plainly where it does not.

**Evidence caveat.** This is a field-tested playbook from a small number of
builds, not a proven project-agnostic template. Portability is demonstrated
when a second stack ships with it. Until then: adapt skeptically, delete
freely, and keep what earns its place.

---

## Adoption-test status

Partial-adoption tests have been run against three modules by LLM personas.
`KNOWN-ISSUES.md` is the authority; this table is a summary of it.

| Walked alone | Result as shipped | Now |
|---|---|---|
| module 05 | TRUE | unchanged |
| module 03 | **FALSE** — 3 findings, 1 silent | fixed, and re-walked clean by the release audit |
| module 02 | **FALSE** — its own README's adoption recipe did not run as written | **TRUE** — the release walk confirmed the recipe produces a working harness file; its proof command is green once the recipe's fill list is followed: `HOOK FIXTURES: 38/38 passed, 0 skipped, 2 n/a`, exit 0 *[the walk measured `15/15` on 2026-08-20. Twenty-one fixtures landed in round #17 — the measured blanket-staging bypasses, the false-deny class the widening created, and the string-literal defects — and the count moved; the number here is this kit's own run of the same command against the same filled key list, not a re-walk. The `0 skipped` and the exit code are what the walk was proving.]* |

The pattern in both failures: the contracts held; the adoption instructions
did not. "Separately adoptable" is a claim about documentation as much as
about code, and only someone else's hands can check the documentation half.
The hands that checked it here belonged to an LLM persona following a written
charter, which is a weaker instrument than a person and is labelled as one.
The unqualified claim returns when a re-test passes, not when the fixes land.

---

## Repository layout

```
oar/
  README.md              you are here
  DECISION-BRIEF.md      one page for a decider: what certifies, what it costs,
                           what is not shipped, exit cost, the honest caveats
  LEVEL-1.md             the documents-only entry: 30-45 minutes, reversible,
                           ending in `kit_doctor.py --level1`
  QUICKSTART.md          the first session, ordered, testable at every step
  EXISTING-PROJECT.md    read beside QUICKSTART on a repository that already
                           exists: one row per measured collision, with the
                           workaround proven for it
  BLUEPRINT.md           the doctrine (authored separately)
  CONTEXT-ARCHITECTURE.md   the full treatment of BLUEPRINT §7: memory, state,
                             and the window — layers, boundaries, wiring
  kit.config.example     every slot in one file
  kit.config             the kit's OWN config - committed, repo-relative
  kit.config.local.example   the gitignored overlay: absolute + protected values
  .claude/settings.json  the kit's own harness wiring (a worked example)
  deident.tokens         empty by design - see tools/deident_scan.py
  tools/deident_scan.py  scan any tree for tokens that must not be published
  tools/adoption_smoke.py    a gate on the kit's adoption path: scaffolds a
                             throwaway repo, performs QUICKSTART mechanically,
                             asserts the result, and can replant a known
                             defect to prove it still detects it
  tools/kit_render.py    OPTIONAL. Substitutes the seven files QUICKSTART has
                             you fill in, from a kit checkout into your repo.
                             Writes only <name>.kit-new; by hand stays the
                             documented path
  tools/statusline.py    the portable status board (module 05's contract)
  tools/kit_doctor.py    "check my adoption" — twelve diagnostic checks over
                             YOUR tree: judged paths that exist, are not hidden
                             by an ignore rule and agree with the hook's config;
                             gates that cannot fail; what a blanket commit
                             would sweep up; whether the hook's interpreter
                             starts; what the tripwire and the cert token are
                             and are not; whether any failure-floor rule is
                             overdue for a demotion disposition; and how big
                             the text every session must read has grown.
                             `--level1` runs seven different ones instead, for
                             a documents-only adoption: the documents are
                             present, rendered, committed, carry the two
                             decisions that level asks for, and neither the
                             config nor the ledger names collide with what an
                             existing repository already had.
                             Verdict is HEALTHY / ATTENTION, never
                             PASS — it diagnoses, it does not certify, and it
                             stages nothing
  tools/expectation_lint.py  fails when a check reads its expectation from
                             the artifact it is asserting about
  checks-registry.json   every check's subject and expectation source, with
                         each surviving self-reference waived explicitly
  .github/workflows/kit-ci.yml   the core, on Linux and Windows, every push
  KNOWN-ISSUES.md        what the LLM-persona adoption walks found, and its state
  docs/walks/            the prompt behind every walk and evaluation read, plus
                           WALKING-YOUR-OWN-DOCUMENTS.md: the method, written
                           for your documentation rather than the kit's
  ROADMAP.md             ready now, in design, planned, and not shipped
  VERSION                the release stamp tools/kit_doctor.py reads
  LICENSE                Apache-2.0
  modules/01..08/        each with a README stating its file contract
```

---

## Maintenance

One person maintains this kit, working with AI agents, on a best-effort
basis. There is no SLA. Issues are read; fixes land when the materiality bar
says they should. The bus factor is one and that is disclosed rather than
dressed up — the same standard this kit asks of every control it ships. If
that risk is disqualifying for your organization, that is a legitimate
reading of an honest label.

---

## The doctrine in one paragraph

The product of a serious build is not the build. It is the growing set of
permanent, executable checks that capture the owner's judgment, so no ruling
ever has to be sampled from a human twice. Every punch item is an un-automated
test that has just revealed itself. Agents are governed exactly enough to keep
that loop honest, and every control is labeled with whether the agents it
governs could rewrite it — a rule enforced by the hands it binds is a real
rule with an honest name, and a rule pretending otherwise is a hazard.
