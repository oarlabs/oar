# COMPARISON — what this kit claims, and who else already claims it

**As of 2026-08-22.**

**If you know an artifact that makes a row on this page wrong, name it and we
will cite it.** That is a standing invitation, not a formality. This page exists
because the alternative — letting a reader find the competitor in one search and
conclude the omission was deliberate — costs more than the citation would.

---

## Verify these rows yourself

**These rows were compiled and verified by the program they describe.** An
AI-run build lane ran the searches, fetched the pages, wrote the
classifications and checked them; the maintainer ruled them. Nobody outside
this program has checked a single row. A reader who declines to take that on
faith is applying this kit's own thesis to this kit — a green produced by the
party it evaluates is not evidence — and the answer is the one the kit gives
everywhere else: do not trust the verdict, run the check.

**The check is per-row, and the checks come in two shapes.** Budget five to
ten minutes per row — an estimate, not a measurement. Most rows name an
artifact and carry a source in brackets, and the bracket states how far the
audit itself got. `[FETCHED]` means the page was retrieved and read.
`[SEARCH-URL]` means the URL was verified and the description came from a
search index rather than from a read of the page. `[UNVERIFIED]` and
`[RECALLED-UNVERIFIED]` mean the reference is a lead and nothing more; *How to
read the sources*, below, defines the vocabulary in full.

- **A row with a source:** open its source, look for the capability the row
  attributes to that artifact, and judge whether the row describes what you
  found.
- **A NO-MATCH-FOUND row:** there is nothing to open, because the claim is
  that nothing was found. The check is to run the search yourself and try to
  name one counterexample; the correction invitation at the top of the page is
  the report path. C17 and C18 carry no source for exactly this reason — and
  that is what makes them the cheapest rows to attack. **C11 used to be on
  that list. A reader ran this procedure, named a counterexample, and the row
  now carries the citation he supplied and a narrowed claim.** That is what
  this page is for, and it is the first time it has happened.

The rows are independent, so checking one is worth doing and does not commit
you to checking eighteen.

**Start with a NO-MATCH-FOUND row.** Those rows make the strongest-sounding
claim and rest on the weakest evidence. NO-MATCH-FOUND is a statement about a
search that was run on one day by one reader, not a statement about the world,
and one name falsifies it. C13, C14 and C17 carry that verdict outright;
C3, C4, C5, C7 and — since round 30's correction — C11 carry it on a
sub-claim.

**If a row is wrong, the correction mechanism is the invitation above:** name
the artifact, and the row gets cited or rewritten. That is not a formality.
The table keeps the rows conceding that an incumbent does the job better, and
the `agt doctor` name collision in C16, for the reason stated at the top of
this page.

**The axis this page compares on, stated so you can reject it.** The neighbours
here are **agent-governance** artifacts — tools that constrain, record or
verify what AI agents do inside a repository. They were chosen because they
make the closest claims to this kit's. If your established tools are
vulnerability management, SIEM, or compliance and audit tooling, this page does
not compare against them, and their absence is not a verdict: those rows were
never run. That row-set is queued and not present, and until it ships this page
is silent about that landscape rather than dismissive of it.

---

## The headline, stated before the table

Two claims run through this kit's own documents. They are not equally strong,
and the strong one is not the one a reader expects.

**The composition claim is narrow, and it is eroding.** The claim is that no
other artifact assembles rails, forced red, a ruling-to-check ledger, a
published escape rate, enforcement-zone honesty, cost ceilings and
self-application into one adoptable set. The audit behind this page did not find
a counterexample. It did find that three of those seven elements now have live,
Apache-2.0-licensed competitors that did not exist when the reference build
started, and that most individual mechanisms have both an ancestor
(`BLUEPRINT.md` §12) and a live neighbour (below). A claim resting on the
proposition that nobody has assembled this before has a short half-life in a
field this crowded, and this kit does not rest on it.

**The conduct claim is the durable one.** This kit turns its own headline
instrument on itself and publishes the number with its denominators, including
the rounds where the number went **up** — 50.0% and 42.9%, named, kept in, with
the reason given. Everyone dogfoods, and several of the artifacts below say so.
What the audit could not find a second instance of is an artifact publishing a
self-applied **miss rate**, with denominators, that is allowed to rise. Coverage
scores and completeness percentages point the flattering direction; a miss rate
does not. That is a claim about conduct rather than about invention, and conduct
is harder to copy than a file layout.

The honest summary: this kit's differentiator is evidence, not novelty. It does
not need a novelty claim to stand up, which is fortunate, because the novelty
claim is the one under pressure.

---

## How to read the sources

Every reference on this page carries one of four tiers, and no reference is
cited without one.

- **[FETCHED]** — the page was retrieved and read during the audit. The title,
  the URL and the specific claim attributed to it were read off the retrieved
  page.
- **[SEARCH-URL]** — the URL and title were returned by a live search, and the
  description is the search index's summary rather than a read of the page.
  Treat the URL as verified and the paraphrase as one remove from the source.
- **[UNVERIFIED]** — known of, not checked during the audit. Do not carry it
  onward without checking it yourself.
- **[RECALLED-UNVERIFIED]** — recalled from the audit's own working memory and
  not confirmed against any source, not even a search index. The weakest tier:
  a lead only, retained where discarding it would hide that the lead exists.

Four classifications are used, and each is a statement about **one claim**,
never about a project as a whole.

- **REDUNDANT-BY** — an existing artifact does this job, and does it better.
- **PARTIAL-OVERLAP** — an existing artifact does part of this job, or does it
  by a different route. The row states which part.
- **NO-MATCH-FOUND** — the audit searched and found nothing matching. This means
  the queries were run and the results read. It does not mean nothing exists.
- **COMPOSITION-STANDS** — the assembled set was not found in one artifact,
  while its parts each exist somewhere. A claim about the assembly only, with
  the erosion risk stated where it is used.

---

## The claims, classified

| # | The claim, and where this kit makes it | Classification | Who else, with sources |
|---|---|---|---|
| C1 | Controls are plain files under git rather than a runtime, because files are the artifact the whole toolchain can hold to account (`docs/WHY-FILES.md`) | PARTIAL-OVERLAP | **Chock** — policies committed to the repo compile to pre-tool-use hooks and CI gates, Apache-2.0 [FETCHED: `https://github.com/open-coder-ai/chock`]. **Agentic OS** — no runtime binary; a rules-and-check system over existing git workflows [FETCHED: `https://github.com/KbWen/agentic-os`]. Both are file-first by the same argument. Neither states the threat-model reason this kit states — that a graph held in a runtime is a file the agent can edit with fewer witnesses — and that framing is this kit's |
| C2 | Enforcement ranked by who can rewrite the enforcer: Zone A (human gate, server-side CI, CODEOWNERS) against Zone B, useful friction honestly labeled (`BLUEPRINT.md` §3) | PARTIAL-OVERLAP | **Chock** labels each emitted control *enforced* / *enforced-at-commit* / *advisory* and reports the coverage [FETCHED, as above] — functionally this kit's zone honesty, shipped as compiler output. The generic ancestor (local hooks are bypassable, server-side gates are not) is standard practice [SEARCH-URL: `https://hackernoon.com/how-to-build-a-governance-layer-for-claude-code-with-hooks-skills-and-agents`]. The specific contribution — ranking by the rewritability of the enforcer, and requiring every rule to carry its zone in writing — was not found stated elsewhere |
| C3 | A PreToolUse hook enforcing model tiering, a blanket-add ban and a protected-path tripwire (module 02) | PARTIAL-OVERLAP on the hook; NO-MATCH-FOUND on model-tier enforcement | **Chock** (pre-tool-use hooks from a committed policy) [FETCHED, as above]. **Provenrail Guard** (denies destructive commands pre-execution; escalations recorded) [FETCHED via `https://github.com/systempromptio/awesome-ai-agent-governance`]. **ThumbGate** (local-first PreToolUse enforcement) [RECALLED-UNVERIFIED — the audit's appendix does not confirm the listed source; retained only as a lead, not as evidence]. None enforces a **model tier** on a spawn; Chock's own feature list marks model-tier enforcement as absent. Tier enforcement is the one hook rule with no competitor found |
| C4 | Forced red — every check has been seen to fail on purpose; a negative-control facility; a dead-man clause (`BLUEPRINT.md` §5, `DECISION-BRIEF.md`) | PARTIAL-OVERLAP on the mechanism; NO-MATCH-FOUND as a shipped governance gate | The mechanism is 48 years old: mutation testing, DeMillo/Lipton/Sayward 1978 [SEARCH-URL: `https://www.scirp.org/reference/referencespapers?referenceid=953139`]. **Agentic OS** ships one negative control — a planted credential that must block the commit [FETCHED, as above]. Not found anywhere: a governance kit requiring *every* check to carry a recorded red proof, with a dead-man clause scoring a silent gate as zero rather than partial |
| C5 | Certification is one command and one exit code, under a PASS / FAIL / INSTRUMENTED / PARTIAL state-word contract (module 03) | PARTIAL-OVERLAP on the runner; NO-MATCH-FOUND on the state-word contract | Single-command CI gating with meaningful exit codes is the norm in LLM evaluation — **promptfoo**, **DeepEval** [SEARCH-URL: `https://deepeval.com/docs/introduction`, `https://aitestingguide.com/promptfoo-review/`]. **Microsoft Agent Governance Toolkit** ships `agt verify` and `agt doctor` [FETCHED: `https://github.com/microsoft/agent-governance-toolkit`]. The distinct claim — that "the check did not run" and "the check passed" must never render alike, so a partial run gets its own verdict word *and* exit code — was not found in any of them |
| C6 | Judgment ledger: every human ruling maps to a named executable check, or is recorded UNCHECKED with a reason (module 04) | PARTIAL-OVERLAP — the most heavily anticipated claim in the kit | Three live lineages. **Requirements traceability matrix**, standard QA and regulated-industry practice [SEARCH-URL: `https://www.perforce.com/resources/alm/requirements-traceability-matrix`]. **NIST OSCAL**, its machine-readable form, control to implementation statement to assessment finding [SEARCH-URL: `https://csrc.nist.gov/projects/open-security-controls-assessment-language`]. **Rel(AI)Build**, in this kit's own domain: requirement-to-file-to-test traceability inside a phase state machine for LLM coding agents [FETCHED: `https://arxiv.org/abs/2606.26924`]. The surviving differentiator is narrow but real: the ledger's left column is the owner's ruling in their own words, and UNCHECKED is a recorded state rather than a coverage gap |
| C7 | Escape rate: the share of findings an existing check should have caught, published per round with denominators, held to a ceiling, computed by a tool and gated in CI (`BLUEPRINT.md` §2, module 04) | PARTIAL-OVERLAP on the metric; NO-MATCH-FOUND as a gated instrument | The metric is standard QA, with published benchmark bands [SEARCH-URL: `https://dzone.com/articles/how-to-measure-defect-escape-rate-to-keep-bugs-out`, `https://plandek.com/blog/escaped-defects`], and it is already being discussed for AI-assisted development [SEARCH-URL: `https://www.tymiq.com/post/top-ai-software-development-metrics-2026`]. Not found: any tool that computes it from a decision ledger, prints it as a required output line on a certifying run, holds it to a declared ceiling and fails the build |
| C8 | Self-application: the kit turns its headline instrument on itself and publishes the unflattering number (`BLUEPRINT.md` §11) | PARTIAL-OVERLAP — the closest single attack on this kit's novelty | **ATM** publishes a self-hosting governance section with an overall self-hosting score and coverage figures [abstract FETCHED: `https://arxiv.org/abs/2607.00041`; the self-hosting figures are SEARCH-URL from the PDF body, not read]. **CANONIC** claims self-application by construction [abstract FETCHED: `https://arxiv.org/abs/2607.05410`; the self-application quotation is SEARCH-URL from the PDF body]. **Kitchen Loop** reports dogfooding its own codebase [SEARCH-URL: `https://arxiv.org/html/2603.25697`]. The distinction that survives: all three publish coverage or completeness scores about themselves, which is the flattering direction. None publishes a miss rate with denominators that goes up |
| C9 | Loop termination: one round by default, approve-with-punch-items is approved, only a reject buys a round, each round's worst finding must be less severe, discovery caps declared up front, AT-CAP and NOT-DRY recorded honestly | PARTIAL-OVERLAP | The round cap is common review practice with numbers attached — a target of one to two rounds, approve with comments when the findings are all nits [SEARCH-URL: `https://mtlynch.io/human-code-reviews-2/`, `https://gitautoreview.com/guides/faster-code-reviews`, `https://zylos.ai/research/2026-03-01-multi-model-ai-code-review-convergence/`]. Not found anywhere: the severity-monotonicity rule (a round whose worst finding is not less severe than the last is a redesign signal, not another round) and the AT-CAP / NOT-DRY honest-close convention |
| C10 | Cost discipline with denominators: a process-over-implementation ratio published per stage against a declared ceiling, plus a rework column (`BLUEPRINT.md` §6) | PARTIAL-OVERLAP | Direct ancestor: **SRE error budgets** — a declared ceiling, actuals measured against it, a consequence on breach [FETCHED: `https://sre.google/sre-book/embracing-risk/`]. **Microsoft AGT** ships an SRE package with SLOs, error budgets and circuit breakers for agents [FETCHED, as above], and per-agent error budgets are an active topic [SEARCH-URL: `https://www.buildmvpfast.com/blog/ai-agent-error-budget-sre-reliability-autonomous-2026`]. Not found: a **ceremony** ratio — process spend over implementation spend — anywhere |
| C11 | Promotion **and** demotion: every rule carries a last-fired date, N stages without firing forces a disposition, and zero demotions across a phase is itself a finding | NO-MATCH-FOUND, **on the third property only** | **CORRECTED IN ROUND 30, and the correction came from a reader running the procedure this page hands out.** Firewall policy recertification tooling — **Tufin** and the same class of rule-lifecycle products — ships a last-hit date column, automated unused-rule reports and a forced disposition at recertification [UNVERIFIED: named from a practitioner's own working knowledge; no page was fetched and no search index was consulted, so treat it as a lead to check rather than as a citation]. That is **two of this row's three properties, in a shipped named product**, and it governs network policy rather than agent rules. Detection engineering's periodic recertification is the same shape again. What the audit still found nowhere is the third property: treating **zero demotions as itself a defect**. The row's claim is narrowed to that property, and the previous wording — "the cleanest unmatched claim in the kit" — is retired as stronger than the evidence supported. The search log below is the original audit's, and it did not reach this class |
| C12 | De-identification gating before publication (`tools/deident_scan.py`) | **REDUNDANT-BY**, for the secret class | **gitleaks** and **TruffleHog** own pre-commit and CI secret scanning [SEARCH-URL: `https://www.jit.io/resources/appsec-tools/trufflehog-vs-gitleaks-a-detailed-comparison-of-secret-scanning-tools`]. This kit's tool scans for tokens you list yourself, which is the narrower de-identification-of-a-known-vocabulary job, and `docs/SECURITY-SCOPE.md` names both incumbents and states what this tool does not cover. This is the one component where an incumbent does the adjacent job better |
| C13 | The collaboration layer: evidenced owner defaults, a five-question seed interview, and a living owner profile the AI maintains (module 08) | NO-MATCH-FOUND | Nothing in the agent-governance landscape surveyed models the **human** as a cached artifact. **Agentic OS** carries decisions across sessions in a state file [FETCHED, as above] but models the work, not the owner. Instruction-file standards model the project. This is the kit's most differentiated module and, by its own admission, its weakest-evidenced: n = 1 owner |
| C14 | Andon cord: any lane at any depth returns a halt verdict, orchestration stops mechanically, halts are counted, and zero halts is a finding | NO-MATCH-FOUND as a shipped agent-governance mechanism | The metaphor's origin is the Toyota Production System [UNVERIFIED — the audit did not reach a primary source]. In the corpus surveyed the nearest thing is **Microsoft AGT**'s runtime kill switch and circuit breakers [FETCHED, as above], which is an operator-initiated stop, not a subordinate-initiated one. The specific claim — the *lowest* agent may stop the *whole* round, and a phase with zero stops is evidence of a broken cord — was not found |
| C15 | Spec-side reviewer onboarding: the reviewer receives the owner's verbatim findings, the rulings and the diff, never the implementer's report (`BLUEPRINT.md` §4) | PARTIAL-OVERLAP | Direct ancestor: **independent verification and validation**, where the reviewing party is separate from the developing one [SEARCH-URL: `https://csrc.nist.gov/glossary/term/independent_verification_and_validation`]. The contribution is the operational form for agents — what the reviewer must **not** be shown — plus the implementer's mandatory "consciously left out" section as a claim the reviewer cross-checks. That form was not found elsewhere |
| C16 | An agent-facing adoption path (`ONBOARD.md`), three adoption levels, and a diagnostic tool that verdicts HEALTHY or ATTENTION and never PASS | PARTIAL-OVERLAP | **Microsoft AGT** ships `agt doctor` — **a direct name collision with this kit's `kit_doctor.py`, disclosed here rather than left to be discovered** [FETCHED, as above]. **Agentic OS** offers a read-only audit entry point for existing repos [FETCHED, as above]. An **ISO 42001 toolkit** ships a 124-requirement gap assessment [FETCHED: `https://github.com/Ankit-Uniyal/iso-42001-ai-governance-toolkit`]. Not found: the deliberate diagnose-never-certify separation — a doctor that refuses to emit PASS so it can never be quoted as certification — or a front door that hands half the adoption back as an explicit punch list |
| C17 | The context layer: a checkpoint as resume anchor, fresh lanes by default with a measured 2.24x resumption penalty, distill-then-prune transcripts (`BLUEPRINT.md` §7) | NO-MATCH-FOUND | Context-persistence patterns exist as engineering advice. Nothing in the governance corpus surveyed treats context as a governed layer with measured boundary costs. This claim was not attacked as hard as the others, and the row says so |
| C18 | **The composition** — all of the above assembled into adoptable rails, self-applied, with the miss rate published | COMPOSITION-STANDS, narrowly | No artifact found holds all seven elements. See the scorecard below, and the headline above for why this is the weaker of the kit's two claims |

**The tally, recounted for this page rather than carried over.** Twelve rows
carry a PARTIAL-OVERLAP verdict — eight wholly (C1, C2, C6, C8, C9, C10, C15,
C16) and four in part, where a sub-claim is unmatched (C3, C4, C5, C7). Three
are wholly NO-MATCH-FOUND (C13, C14, C17) and one is NO-MATCH-FOUND on a
sub-claim only (C11, narrowed in round 30 by a reader's counterexample). One
is REDUNDANT-BY (C12). One is the composition claim itself (C18).

---

## The composition scorecard

The four closest candidates, scored against the seven elements the composition
claim names. Every row was built from the sources cited above.

| Candidate | Assembled as rails | Forced red | Ruling-to-check ledger | Published escape rate | Enforcement-zone honesty | Cost ceiling | Self-applied miss rate |
|---|---|---|---|---|---|---|---|
| **Chock** [FETCHED] | yes | no | no | no | **yes** | no | no |
| **Agentic OS** [FETCHED] | yes | partial — one planted secret | partial — work logs | no | partial | no | no |
| **Microsoft AGT** [FETCHED] | yes, as a runtime | no | no — an audit log is not a ruling-to-check map | no | no | **yes** — error budgets | no |
| **ATM** [abstract FETCHED] | yes | no | partial — atom-evidence | no | no | no | partial — coverage scores, not a miss rate |
| **OAR** | yes | yes | yes | yes | yes | yes | yes |

The last column is the one that carries the argument, and it is the only column
where the audit found no second instance.

---

## Where a competitor is simply better

Recorded separately, because a comparison page that never concedes anything is
marketing.

- **Secret scanning (C12).** `gitleaks` and `TruffleHog` do the credential job
  properly and this kit does not attempt it. `docs/SECURITY-SCOPE.md` names
  them.
- **Organisational management systems.** NIST AI RMF toolkits and the ISO/IEC
  42001 implementation toolkits operate one layer above this kit's
  per-repository scope — gap assessments, statements of applicability, risk
  registers, control mappings to external regimes. If that is the requirement,
  those are the instruments [FETCHED: `https://github.com/Ankit-Uniyal/iso-42001-ai-governance-toolkit`].
- **Runtime enforcement against a hostile agent.** Microsoft AGT, and the
  guardrail products in that lane, occupy the threat model this kit explicitly
  declines. `docs/SECURITY-SCOPE.md` says so and should be read before this
  kit is offered to a security reviewer.
- **Supply-chain attestation.** SLSA, in-toto and sigstore attest artifacts, and
  this kit deliberately declines to build a second attestation system inside
  itself [SEARCH-URL: `https://slsa.dev/spec/v1.0/distributing-provenance`].
  They compose; they do not compete.

---

## What this page does not establish

The audit behind it ran once, on one day, by one reader, against live web search
and a set of fetched pages. A NO-MATCH-FOUND row means the queries were run and
the results read, and nothing more. Search indexes are incomplete, the field is
moving quickly, and three of the strongest competitors named here are younger
than this kit's reference build — which is the reason the composition claim is
described as eroding rather than as safe.

One reference is recorded as unresolved rather than dropped: a search summary
attributed an escape-rate figure to a paper on agent telemetry whose abstract
does not define the term [FETCHED abstract:
`https://arxiv.org/abs/2604.05119`]. This kit makes no claim about prior use of
"escape rate" in agent governance, and if it ever does, that paper's body has to
be read first.

Corrections are welcome on the terms at the top of this page: name the artifact,
and the row gets cited or rewritten.
