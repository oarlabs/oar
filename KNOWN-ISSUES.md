# KNOWN ISSUES — measured, not hidden

This register records what independent adoption tests found: AI agent personas
with no prior contact with the kit tried to adopt it and wrote down what
happened. That is the kit's own escape-rate loop turned on itself, and it has
found something **in all fourteen walks** — though the hands-on walks in 13 and
14 were clean; their findings were in the documentation meta-layer, and the
loop closed there by the owner's materiality ruling (see walk 14).

Entry 15 is not a walk. It is an adversarial review of the kit's own
streamlining report, and it found three measured hazards that every walk before
it had passed over.

**Rows are never deleted.** A fixed item is marked in place with what it used to
do, because that is the only honest way to calibrate how much to trust the
current claims.

---

## The entry timeline — authoritative

Every "walk N" in this document means a row in this table. Where an older
sentence used a different number, it is corrected in place with a bracketed
note; the table is what the numbers mean.

| Entry | What it was | Found | State |
|---|---|---|---|
| 1–6 | Pre-ship adoption tests: modules walked alone and in combination, one fix pass per walk | The eight instances tabulated below, plus items 1–11 in "Confirmed fixed" | fixed |
| 7 | **Release audit** — a read of the whole kit before shipping, not an adoption | Verdict **SHIP**, zero ship-blockers; 3 MAJOR + 4 NIT of day-one errata, including instances 6–8 of the class | fixed, except two NITs left OPEN by decision |
| 8 | **Stranger onboarding #1** — Windows/pwsh, literal obedience, no coach | 13 (2 major, 8 minor, 3 nit) | all 13 fixed |
| 9 | **Stranger onboarding #2** — Linux/bash conventions on a Windows host | 7 (1 major, 3 minor, 3 nit): K-1…K-7 | all 7 fixed |
| 10 | **Stranger onboarding #3** — the impatient skimmer: headings, code blocks and checkpoints only | 9 findings + 1 end-state item: S3-F1…F9, S3-E3 | 9 fixed, 2 rejected with reason |
| 11 | **Stranger onboarding #4** — a team-lead evaluator who read doctrine first, then walked, then simulated a second machine | 18 (7 major, 7 minor, 4 nit): F-1…F-18 | all 18 dispositioned FIX; four are honest-labeling fixes with the design recorded open |
| 12 | **Stranger onboarding #5** — the dry-test literalist: full re-walk after the walk 8–11 errata, end-state audit | 6 (1 major, 2 minor, 3 nit): W12-1…W12-6 | all 6 fixed |
| 13 | **Stranger onboarding #6** — the thorough adopter: full walk + end-state audit + doctrine spot-checks. **The hands-on walk was clean** — every step, checkpoint and audit property passed | 6 (0 major, 3 minor, 3 nit): KI-1, KI-2, BP-1, CA-1, M08-1, QS-1 — all meta-layer (register bookkeeping, cross-module attribution, one prose-vs-checkpoint asymmetry) | all 6 fixed |
| 14 | **Stranger onboarding #7** — the final cap walk: full walk + audit + doctrine and module-README spot-checks. **The hands-on walk was clean again** — the second consecutive clean walk | 8 (0 major, 4 minor, 4 nit): M03-1, M02-1, M01-1, M02-2, CA-2, KI-3, KI-4, QS7-1 | 6 fixed; KI-3 and KI-4 **rejected — below the owner's materiality bar** (register self-audit; ruling 2026-08-20) |
| 15 | **Streamlining review, pass 2** — not a walk: an adversarial read of the streamlining report the walk-14 close produced, and of the shipped files it described, against the owner's materiality bar | 3 measured hazards (SR2-1…SR2-3) — one silent-green defect in the runner, two documentation hazards that cost real work — plus the register entry this pass owed itself (SR2-4); the first version of the SR2-1 fix carried a Windows transport defect, caught by spec-side review before any commit (recorded in SR2-1's disposition); the first committed version of the phase-12 control then false-positived on hosted Windows CI (its raw backslash-r scan matched the runner's own `\runneradmin` home path), caught by CI on the first push and fixed the same day | all 4 fixed |

| 16 | **Second-authority round** — not a walk: `tools/kit_render.py`, the optional mechanical substitution path, was built, and a second rendering of the same templates was required to agree with the smoke's hand-built adopter model | 1 defect in a shipped check (R16-1), found by the new check on its first run. The tool itself was then reviewed spec-side before any commit: 5 major, 8 minor, 5 nit, every major live-proven — two of them defects inside the tool's own guards (an output path could escape the target repository; an equivalent-but-reordered matcher was duplicated and mislabelled), both reporting `PASS` at the time | R16-1 fixed; all 18 review items dispositioned and fixed or rejected with reason, none of them ever committed |
| 17 | **Adversarial persona round** — not a walk: three independent adversarial reads of the shipped kit (a controls graybeard, a team-lead evaluator, a skeptic), then a fourth read attacking those findings against the owner's materiality bar; then a spec-side review of the implementation before any of it was committed | 4 owner-ratified items (R17-1…R17-4) plus 2 riders (R17-R1, R17-R2), then **14 more from the review of the fix itself** (R17-5…R17-8 plus nine smaller): the hardening false-denied five ordinary two-line shell blocks, two disclosed residuals were labelled in the wrong direction, and the new doctor wrote `__pycache__` into the tree it diagnosed. Two of the four review blockers were the SAME silent-false-allow direction the fixes were meant to close | R17-1 **NARROWED, not closed** (durable index-based fix recorded, not built); R17-2, R17-4, R17-5's false-deny half, R17-6, R17-7, R17-8 fixed; R17-3 decided and labelled; both riders absorbed into `tools/kit_doctor.py`. Fixture count 17 → 40. After the fix passed all ten gates and both reviews, a doctor selftest assertion hard-coded the Windows case-folding answer for `path_inside` and false-failed on Linux CI — the fourth second-machine catch of the quest, and the first in the Windows-passes-Linux-fails direction; the assertion now derives the expected value from `os.path.normcase`, the same case-sensitivity class the doctor's own `protected-case` check probes | R17-3 decided and labelled; both riders absorbed; the CI case-folding assertion fixed on the first red |

Walks 1–7 were run against the kit as a whole by readers with some exposure to
it. Walks 8–14 are **stranger onboarding walks**: a fresh reader with no
prior contact adopts the kit into an empty repository by obeying the documents.
Entries 15, 16 and 17 are neither — see their rows.

---

## The pattern — **PROMOTED: prose design-question → mechanical lint**

Walks 1–7 found **eight** instances of one class, and after the fourth it was
clear they were one defect wearing different hats:

| # | Instance | Walk |
|---|---|---|
| 1 | the `judges` gate read only git's stdout, so "no repository" read as clean | 1 |
| 2 | the runner resolved its root from its own file location, so it judged the wrong tree and pronounced it fine | 2 |
| 3 | `--selftest` named the example gates the documentation tells you to delete | 3 |
| 4 | `kit.config` was outside the judge surface, so the config parameterising the judges could change without invalidating them | 4 |
| 5 | fixture `j` built its payload from the very key it was guarding | 4 |
| 6 | the armed check trusted the settings file to prove the settings file | 5 → **7** |
| 7 | `NONE` read as a value, so a placeholder configured a rule that guarded nothing | 5 → **7** |
| 8 | `STATUSLINE_CMD` broke the JSON it was substituted into, silently disarming the hooks | 6 → **7** |

*[Corrected 2026-08-20: the last three rows carried **fix-pass** numbers (5, 5,
6) in a column headed "Walk". All three were found by **walk 7**, the release
audit — the section below says so and always did. Instances 1–5 are walk
numbers and are unchanged.]*

**THE CLASS:** *a check whose expectation comes from the same artifact it is
asserting about cannot see a change to that artifact.* Fixture and defect move
together; the check stays green and its greenness means nothing.

### Why it is now a lint and not a ninth paragraph

The kit's own operating architecture carries a standing rule: **when a prose
rule fails, promote it a layer or accept it with the residual named.** That
rule had fired eight times against one class while the class itself was
documented only as a "design question asked of every new check" — which is
exactly the prose-only enforcement the doctrine says to distrust. Fix pass 5
made the class *legible*. This pass makes it **mechanical**:

- **`checks-registry.json`** — every check declares its **subject** and the
  artifact its **expectation** is read from.
- **`tools/expectation_lint.py`** — fails when those are the same artifact and
  no waiver explains why, and fails a waiver that carries no reason, because a
  waiver without a reason is the silent case wearing a label.
- **Negative controls in its own selftest** — instances 5 and 6 reconstructed
  as registry entries and shown red un-waived. A lint that has never flagged
  the thing it exists for is not evidence.
- **Run in three places:** `--selftest` in Step 0, the real registry in
  adoption-smoke phases 11 and 11b, and both on Linux and Windows in CI.

**Six waivers survive**, printed on every run with their reasons: four
config-driven fixtures (structurally covered by `kit.config` being in
`JUDGE_PATHS`), the armed check (only half-closable — no second source exists
for a harness's intent, but *startability* is now read from the filesystem),
and the registry checking itself. That is the honest residue of the class: not
zero, but named, visible, and each with what covers the gap instead.

**Inline literal expectations are out of scope** and marked `inline`. A
hand-written literal is the specification; it does not move when the code does.

---

## Confirmed fixed — walks 1–4, verified by later walks

| # | What it used to do | What closed it |
|---|---|---|
| 1 | **Non-git silent false green** — `git status` outside a work tree exits 128 with empty stdout, and empty porcelain is how "clean" is spelled. | `git_answer()` turns any non-zero rc into a porcelain line; the startup assertion refuses to run a git-judged gate outside a work tree. |
| 2 | **Module 03 could not run standalone**; the in-file comment said "keep them". | Module README **Step 0**, the comment reversed, and why `--skip hooks` is worse. |
| 3 | **`--selftest` broke on the README's own adaptation step.** | Section F resolves a live gate name at runtime; the smoke deletes both example gates. |
| 4 | **Module 05's holes** — module-02-dependent wiring, no defaults, a silently vanishing banner. | Inlined JSON for both boards, defaults for all seven keys, a loud amber segment, the gitignore coupling documented both ways. |
| 5 | **QUICKSTART Steps 1 and 6 were mutually exclusive.** | The third state `n/a` (off on purpose ≠ a gap); the kit's own tripwire is off. |
| 6 | **The startup assertion rejected flag VALUES as paths** — `-ExecutionPolicy Bypass` aborted the runner. | `looks_like_a_path()`, with the Bypass invocation as a named selftest case. |
| 7 | **The smoke under-tested its own label**; `--plant-f1` printed FAIL and exited 0. | Both gates deleted plus a `--list` assertion; `INSTRUMENTED` and exit 2. |
| 8 | **The shell note was backwards.** | Rewritten, and now machine-checked — see SB-3 below. |
| 9 | **`kit.config` was not in the judge surface** — an uncommitted rule-weakening edit certified clean. | The config is in `JUDGE_PATHS` in all three shipped examples; smoke phase 8 asserts it live. |
| 10 | **Steps 4 and 5 could not complete in document order.** | Settings substitution moved into Step 4; smoke phase 9 walks the document. |
| 11 | **Step 1 put an absolute `PROJECT_ROOT` in the committed config.** | Out of the fill list; `PROTECTED_PATH` too; `PROTECTED_PATH_ENABLED` stays. |

---

## Fixed in fix pass 5 — walk 7 (release audit)

*[Corrected 2026-08-20: this heading read "the sixth walk (release audit)" while
the section below it, and the section after it, both number the release audit as
walk 7. Walk 7 is correct; the "sixth" was a fix-pass number. "This pass" meant
fix pass 5, which is now named.]*

The release auditor confirmed every prior fix held: module 03 standalone was a
clean PASS, the impostor matchers were dead in four directions, and the no-git
abort behaved. It then found three more instances of the class, numbered 6–8
above.

**SB-A — `--armed` proved a settings file *named* the hook, not that the named
file *exists*.** A settings entry pointing at a moved, renamed or never-copied
script reported `armed:` for every tool and exited 0, while the harness would
fail to start the hook on every single call. The script a matched command names
is now resolved against the **filesystem** — an artifact independent of the
settings file — and a missing one reports **`UNSTARTABLE:`**, which is also a
veto token in the verify runner's `hooks` gate. QUICKSTART's over-claim ("proves
the harness actually calls it") is now the true sentence: *wired at every
enforcement point to a script that exists*, with what it still cannot tell you
stated beside it.

**SB-B — `STATUSLINE_CMD` was an absolute-path key in the committed half, and
its value contained double quotes.** Substituted into `"command": "…"` that
yields a settings file that does not parse — and unparseable settings mean **no
hooks either**, so a cosmetic slip silently disarmed the whole enforcement
layer. The key moved to `kit.config.local` alongside `PROJECT_ROOT` and
`PROTECTED_PATH`; the quote rule is stated at all three sites; the adoption
smoke now **parses** the substituted settings and refuses a double quote in the
command; and Step 9's enumeration is a table that is true on every branch (four
hits on the recommended one), asserted by phase 9 on that branch.

**SB-C — the UNSET family did not cover placeholder-shaped values.** The kit
ships fourteen of them, and every one is an ordinary non-empty string:
`FORBIDDEN_SPAWN_TIER = your-top-tier-model` reads as a configured rule that
forbids a tier nobody will ever request. Enforcement-shaped, enforcing nothing.
One shared `is_placeholder()` now covers `your-*`, `/abs/path/*`, `<paste…>`,
`derive-from-*`, `example.invalid` and the NONE family, in **all three** config
readers. Consequences flow through machinery that already existed: unset tiers
render `<KEY unset in kit.config>`, an unset `FORBIDDEN_SPAWN_TIER` or
`MODEL_EXEMPT_TYPES` raises a `CONFIG WARNING` that `--strict` fails on, and
phase 9 asserts a rendered governance file carries no surviving example value.

**Mechanical items.** The `--runner` / `--plant-f1` coupling disclosure
corrected — both are coupled to the *example gates*, so they work on an
unadapted runner and abort loudly on an **adopted** one ("if adopted", not "if
refactored"); adopted-runner support is deliberately not built. Two stale
fixture-count citations refreshed. The last unlabelled cross-module line in
`CLAUDE.md.template` labelled, so the "labels every cross-module line" claim
is true. Module 03 gained the same working-order adoption recipe module 02 has,
including the `git init` line and why it is load-bearing. And the smaller ones:
an "above" that pointed below, the Step-0 command count, the abort message
naming `HOOK_*` constants only when the `hooks` gate is actually selected, and
the size figure here.

---

## Release walk (#7): **SHIP** — with day-one errata

> **Verdict: SHIP. Zero ship-blockers.** The seventh walk was a release audit
> rather than an adoption test, and it is the first walk that did not find a
> silent green.

It did find three MAJORs and four NITs, all of them day-one errata. Dispositions:

| # | Finding | Disposition |
|---|---|---|
| MAJOR-1 | QUICKSTART Step 1's fill list omitted `FORBIDDEN_SPAWN_TIER`, so obeying the document produced one `SKIP` and made Step 6's `0 skipped` checkpoint unreachable. | **ROOT-CAUSE FIXED.** The key is in the fill list, in both QUICKSTART and module 02's recipe, with the note that it looks like a duplicate of the orchestrator tier and is the one people skip. |
| MAJOR-2 | Module 02's recipe did not say to fill the tier keys, so its own proof command could not go green by obedience. | **ROOT-CAUSE FIXED** by the same edit. Proof re-run against a config filled per the new list: `HOOK FIXTURES: 15/15 passed, 0 skipped, 2 n/a`, exit 0. *[Corrected 2026-08-21: that count is the one measured on 2026-08-20. Twenty-one fixtures for the measured blanket-staging bypasses, the false-deny class the widening created, and the string-literal defects landed in round #17, and the same command now ends `38/38 passed, 0 skipped, 2 n/a`. The `0 skipped` and the exit code are what this row was proving; the same correction is on the identical line in `README.md`.]* |
| MAJOR-3 | Step 4's copy list omitted the status board while Step 4's `STATUSLINE_CMD` step pointed at it. | **COPY STEP FIXED** (`cp …/tools/statusline.py tools/` on the recommended branch). The underlying gap is **recorded, not fixed** — see the row below. |
| NIT-7 | An `armed:` line and an `UNSTARTABLE:` line can both appear for the same tool, which reads as a contradiction. | **OPEN.** Both are true — the matcher covers the tool, the script is missing — and the run is red either way. Merging them is a presentation change to a line that is currently correct. |
| NIT-8 | The non-git abort ends with the generic `Fix: set JUDGE_PATHS / CERT_PATHS…` line, which is not the fix for that particular problem. | **OPEN.** The specific remedy (`git init`, or `--skip judges`) is in the sentence directly above it; the generic tail is redundant rather than wrong. |
| NIT-9 | `kit-ci.yml` carried the expectation-lint step twice. | **FIXED** — it was a deletion. Eleven steps, no duplicate names. |
| NIT-10 | QUICKSTART's Step 0 command count. | **FIXED** — eight commands, counted. *[Corrected 2026-08-20: the count in this disposition went stale. Step 0 has since grown to **nine** commands, and its checkpoint says nine. The block and its checkpoint agree; only this row's number was wrong.]* |

### Recorded, not fixed: statusLine startability

**SB-A's startability check covers hook commands only.** For each PreToolUse
block naming the hook, the script is resolved against the filesystem and a
missing one reports `UNSTARTABLE:`. The **`statusLine`** command gets no such
check, so a mis-pathed board fails silently: no banner, no error, and a status
line that renders nothing looks exactly like a session with nothing to report.

Why it is recorded rather than closed: the failure is **observability, not
enforcement**. A dead hook means rules stop binding; a dead board means you
stop seeing. Both deserve to be loud, but only one of them can let something
through — and this pass was chartered as errata, not features.

**Fix shape, when someone wants it:** extend `check_armed`'s existing
`hook_script_from_command` + `resolve_hook_script` pair over
`settings["statusLine"]["command"]` and emit the same `UNSTARTABLE:` token.
Perhaps twenty lines, including the fixture. The verify runner's `hooks` gate
already vetoes on that token, so nothing downstream changes.

---

## Walk #8 — stranger onboarding, Windows/pwsh, literal obedience

The eighth walk was the first post-ship onboarding test: a fresh reader adopted
the kit into an empty repo by obeying the documents literally, in pwsh, with no
coach. The walk completed — all nine QUICKSTART steps, `VERIFY: PASS` at the
end. It found 13 defects. Every executable did what its documentation said; 12
findings are documentation defects and one is a check-coverage defect.

The check-coverage defect is this walk's instance of the class: **phase 10
reported "all 13 template SLOTS manifests match their bodies" while its
detector silently skipped 10 of the 23 slot-using files** — a green count with
no coverage claim behind it. One skipped file, the governance template, really
did carry a defect (`{{PROSE_VOICE}}` missing from its inventory), and the
skipped check is why it shipped.

All 13 were fixed in one errata pass, same day:

| # | Finding | Disposition |
|---|---|---|
| W8-1 | `CLAUDE.md.template`'s SLOTS inventory omitted `{{PROSE_VOICE}}`; obeying Step 6 shipped a raw slot. | **FIXED** — inventory now lists all 18 slots. |
| W8-2 | The smoke's manifest detector required "slots" and a token on one line; multi-line inventories went unchecked, silently. | **FIXED** — multi-line detection; the headline now states coverage (14 of 23 checked, 9 carry no manifest). |
| W8-3 | Step 4's printed commit line did not stage the gate payload, so the `VERIFY: PASS` checkpoint failed as printed. | **FIXED** — line stages `tests`; checkpoint conditioned. |
| W8-4 | The shell section over-claimed `mkdir -p` portability; in pwsh an existing directory is an error, not a no-op. | **FIXED** — claim corrected, `-Force` form given. |
| W8-5 | The "following week" `--runner` command ran from neither directory and aborts on an adopted runner. | **FIXED** — replaced with what an adopter should run; the limit stated where printed. |
| W8-6 | Step 8 named `PROFILE-TEMPLATE.md` with no copy command or destination. | **FIXED** — explicit command and destination rules. |
| W8-7 | `kit.config.example` promised templates "degrade to repo-only" at `KNOWLEDGE_DIR = NONE`; no template has a NONE branch. | **FIXED** — promise replaced with the substitution instruction, noted at both interpolation sites. |
| W8-8 | Step 9 predicted exactly four deident hits; the count is path-shape arithmetic (a real walk measured 8). | **FIXED** — count made illustrative; the second-tracked-file diagnostic promoted. |
| W8-9 | Ledger seed lesson 8 shipped the narrow blanket-add rule the governance template calls wrong. | **FIXED** — reworded to the blanket rule. |
| W8-10 | Step 7 never said to substitute the ledgers' slots or delete their SKELETON blocks. | **FIXED** — instruction and checkpoint added. |
| W8-11 | `CONTEXT-ARCHITECTURE.md` was in no reading order. | **FIXED** — evaluator route added to README. |
| W8-12 | `kit.config`'s `JUDGE_PATHS`/`CERT_PATHS` vs the `verify.py` constants: nothing reconciles them and module 03's README stated the reverse relationship. Measured: no tool reads the config's `JUDGE_PATHS`; the hook's cert-green tripwire reads its `CERT_PATHS`. | **FIXED** (docs) — the constants are authoritative; the docs now say so and tell the adopter to reconcile by hand. |
| W8-13 | No step told a bare-`git init` adopter to create a source or test tree. | **FIXED** — Step 3 note. |

### Closed on the tenth walk: the document-order walk staged with `git add -A`

`document_order()` in `tools/adoption_smoke.py` used to stage its scaffold with
`git add -A` instead of the QUICKSTART's printed targeted-add line. That is why
W8-3 escaped: the walk reached `VERIFY: PASS` while a literal reader did not,
because the walk staged everything and the reader staged what the document
printed. It was also the one place the kit's own tooling used the blanket add
its governance template forbids.

**Now fixed.** The walk stages the document's named paths, dropping only the one
path its scaffold genuinely does not have — which is the substitution the
document now tells the reader to make inside the code block, because `git add`
is atomic and one bad pathspec stages nothing at all. The walk also creates
Step 3's `docs/ORACLE-<gate>.md` and asserts the commit carries it, so a gate
adopted without an oracle no longer certifies green.

---

## Walk #9 — stranger onboarding, Linux/bash conventions

The ninth walk adopted the kit with bash habits on a Windows host. It completed
all nine steps and found 7 defects, all documentation. Its major is the walk's
instance of the class: **Step 9's scan ran `--tracked-only` over a tree whose
last commit was Step 4's**, so the scan that certifies nothing personal is about
to be published never saw the rules file, the ledgers, or
`docs/collaboration-profile.md` — the one file the walk fills with a person's
verbatim words. A green scan over a tree that does not contain the profile looks
exactly like a green scan over one that does.

All 7 were fixed in one errata pass:

| # | Finding | Disposition |
|---|---|---|
| K-1 | Step 9 scanned `--tracked-only` with Steps 6–8 uncommitted, so the profile and the ledgers were unscanned and the scan could not say so. | **FIXED** — Step 9 opens with the named-path commit; the step tells the reader to read the printed `scope:` line; smoke phase 9 now walks the commit, asserts the scope widens to the whole tracked tree, and asserts the remediation reaches zero. |
| K-2 | Step 1 said only `JUDGE_PATHS` and `CERT_PATHS` come back later. `KNOWLEDGE_DIR` and `RATIO_CEILING` come back too, at Steps 6 and 7, unannounced. | **FIXED** — Step 1 names all four keys and the step each returns at. |
| K-3 | Step 3's checkpoint asked for "one filled worksheet page" and no step said where it goes or what to call it; the only hint was a parenthetical two steps later. | **FIXED** — Step 3 names `docs/ORACLE-<gate-name>.md` explicitly and says Step 4's commit line stages `docs`. *(This fix introduced walk 10's S3-F1: Step 4's commit line then named a `docs` a skimmer did not have.)* |
| K-4 | `{{PROJECT_ROOT}}` is a mandatory slot in three hook commands while the config registry ships the key of the same name empty on purpose — the slot and the key look like one thing. | **FIXED** — Step 1 separates the runtime *key* from the substituted *slot*, states that nothing fills the slot from the key, and names the `UNSTARTABLE:` an empty slot produces. |
| K-5 | Step 7's checkpoint ("no `{{` surviving") is satisfied by substituting `RATIO_CEILING`'s shipped `derive-from-your-own-data`, which the kit's own readers treat as UNSET. | **FIXED** — Step 7 names that one placeholder as a deliberate, allowed survivor, with when to replace it, and separates config *values* from template *slots*. |
| K-6 | Step 4 told the adopter to delete an `examples/` directory its own copy list never brings into the repo. | **FIXED** — the instruction states that the directory stays behind in the kit and there is nothing to delete. |
| K-7 | The NIT-10 disposition above said "eight commands, counted"; Step 0 had grown to nine. | **FIXED** — corrected in place with a bracketed update on the row itself. |

---

## Walk #10 — stranger onboarding, the impatient skimmer

The tenth walk read headings, code blocks, tables and checkpoints, and paid for
prose only when something failed. It reached the kit's full done state —
`VERIFY: PASS`, clean tree, `DEIDENT SCAN: 0 hits` — and the end-state audit
then found three defects **no checkpoint had caught**: no oracle worksheet
existed at all (Step 3 has no command block, so this persona skips it with
certainty), `CLAUDE.md` would have shipped as an unrendered template carrying 45
raw slots (Step 6's checkpoint measured the *hook*, not the rules file), and
`kit.config` and `CLAUDE.md` disagreed about `KNOWLEDGE_DIR` from day one.

**The structural finding** is worth more than any single row: *load-bearing
instructions were living in prose while the adjacent checkpoint measured
something else.* The errata pass applied one pattern throughout — move the
instruction into the checkpoint, with a runnable line in both shells.

| # | Finding | Disposition |
|---|---|---|
| S3-F1 | Step 4's printed commit line named `docs`, which a skimmer who skipped Step 3 did not have; `git add` is atomic, so nothing staged and nothing committed. **A regression introduced by walk 9's K-3 fix.** | **FIXED** — an in-block comment tells the reader to drop paths they do not have and states that one bad pathspec stages nothing at all. Counted as rework. |
| S3-F2 | Step 6's checkpoint measured the hook only, so an entirely unrendered `CLAUDE.md` passed every check in the document. | **FIXED** — the checkpoint is two bullets, the second inspecting `CLAUDE.md` itself, with a runnable line in both shells and in the smoke. |
| S3-F3 | Step 7 claimed "Step 6's own check on the rendered rules fails on any of them" — no such check existed. | **FIXED** — the false sentence is deleted and replaced by "No shipped tool checks your tree for them", which names what phase 9 does and does not cover. |
| S3-F4 | The de-identification token file's format was never stated, and a wrong-shaped file still parses and reports `0 hits`. | **FIXED** — format given in the block; the failure mode stated in the paragraph beside it. |
| S3-F5 | Step 1 had no checkpoint, so its mandatory fills lived only in prose and `PROJECT_NAME` was caught nowhere in the document. | **FIXED** — Step 1 ends in two runnable lines per shell; the smoke asserts the same thing over the config it writes. |
| S3-F6 | A commit that did not run leaves the *identical* `VERIFY: FAIL … RED: judges` line as the pre-commit run, and nothing said so. | **FIXED** — the checkpoint bullet names the ambiguity and what to check. |
| S3-F7 | Step 4's runnable block depended on edits made in prose above it, unmarked. | **FIXED** (marker half) — an in-block comment names the prerequisite. Restructuring Step 4 was out of scope. |
| S3-F8 | Nothing between Step 4 and Step 9 mentioned the worksheet again, so a gate with no oracle certified green. | **FIXED** (artifact half) — Step 4's checkpoint names `docs/ORACLE-<gate-name>.md` and gives the command to read the commit. |
| S3-E3 | `kit.config` and `CLAUDE.md` could state different answers for `KNOWLEDGE_DIR` with no check reading either. | **FIXED** — Step 6 gained "Set the key as well as the slot"; the smoke asserts the two agree. *(Walk 11's F-2 later corrected which half the key goes in.)* |
| — | **REJECTED (2):** S3-F9, that the placeholder paths in examples should be real; and S3-F8's second half, that "an afternoon of thinking" for Step 3 should be compressible. | **REJECTED with reason** — placeholder-shaped values are read as UNSET by design, which is the safer failure; and the oracle step does not compress, which is the point of the step. |

---

## Walk #11 — stranger onboarding, the team-lead evaluator

The eleventh walk was the first to read **doctrine before commands**: README →
BLUEPRINT → CONTEXT-ARCHITECTURE → KNOWN-ISSUES, then QUICKSTART hands-on, then
a second-machine simulation. It found **18** defects — the largest round — and
the reason is the route: claim-checking BLUEPRINT and CONTEXT-ARCHITECTURE
against the shipped files, auditing this document for self-consistency, and
running the kit as a *team* would are four surfaces the first three stranger
walks never touched. Every executable behaved as documented, including the ones
designed to fail; all 18 findings are documentation defects.

The walk's recommendation was **adopt, partially and in a different order than
the kit proposes**: modules 04 and 08 immediately, module 03 and then module 02
after — not a rejection, and not the full adoption the document assumes.

Four of the majors are **architecture-level**: the honest fix is a true label
plus a recorded design, not a feature. Those four appear in the open list below.

| # | Finding | Disposition |
|---|---|---|
| F-1 | Step 6 requires editing `KNOWLEDGE_DIR` in `kit.config`; Step 9's printed commit line staged only `CLAUDE.md tools/deident_scan.py docs`, so a literal walk *ends* at `VERIFY: FAIL — RED: judges`, `M kit.config`. Measured. **Rework — introduced by the walk 9/10 errata chain.** | **FIXED** — Step 9's commit line names `kit.config` and says why; Step 9 now ends in a certification run. The smoke's walk sets the key at Step 6 (leaving the config dirty, as a reader does), stages it at Step 9, and asserts `VERIFY: PASS` at the end. |
| F-2 | Step 6's *first* branch told you to write an absolute knowledge-base path into the **committed** `kit.config` — manufacturing the "second tracked file" escape Step 9 defines. Measured: `HIT kit.config`. | **FIXED** — the absolute branch routes the key into `kit.config.local`; the rule is stated plainly (an absolute path never enters the committed half); Step 9's key list and second-file note both name `KNOWLEDGE_DIR`; `kit.config.example` and `kit.config.local.example` say which half takes which value. |
| F-3 | The committed `.claude/settings.json` is simultaneously per-machine, shared, and inside `JUDGE_PATHS`; the kit's own `.gitignore` names `.claude/settings.local.json` and no document mentions it. Measured on a second machine: `UNSTARTABLE:` × 3 and `RED: judges, hooks`. | **LABELLED, recorded not fixed** — Step 4 gains "One machine per settings file" with the measured consequence and no false remedy. The split is real design work and is **open** below. |
| F-4 | `CONTEXT-ARCHITECTURE.md` §6 describes SessionStart, PreCompact and a handoff PreToolUse hook in shipping-grade detail; the kit ships none of the three and nothing said so. | **LABELLED** — §6 opens with a NOT SHIPPED banner in module 07's style; BLUEPRINT's diagram edges and its §7 closing paragraph carry the same flag; the two forward references in §2–3 say the hook does not exist. **Open** below. |
| F-5 | The rendered rules file's first binding line — "ON RESUME: read the newest checkpoint FIRST" — is unsatisfiable on day one: no checkpoint template ships, no step writes one, no check notices. | **LABELLED** — the template line now says you write the first one at your first stage close, and points at the four-clause shape contract in the paragraph below it; QUICKSTART Step 6 surfaces the same thing on the adopter's path. **Open** below. |
| F-6 | This document contradicted itself on its own walk count — "five walks", "six", "the sixth walk (release audit)", "Release walk (#7)", "eight walks in" — and walks 9 and 10 had no findings section. | **FIXED** — an authoritative walk timeline at the top; every contradicting number corrected in place with a bracketed note; findings sections added for walks 9, 10 and 11. |
| F-7 | README's "transfers to any stack, any model, any team": the team half had two adaptation notes behind it and single-seat assumptions throughout. | **FIXED (softened)** — the claim now reads "any stack and any model", with a paragraph naming what a team must decide and a pointer to the open row. |
| F-8 | QUICKSTART's "The order matters" asserted an order the nine steps do not have; two of its four clauses contradicted the steps they summarised. | **FIXED** — rewritten as "Why the nine steps are in this order" (an ordering by dependency), with the README's adoption levels named as the different thing they are (an ordering by commitment). |
| F-9 | Step 6 told you to amend a "mirror" sentence that does not exist in `CLAUDE.md.template`. | **FIXED** — the instruction now quotes the template's actual text, `(that copy is source of truth)`. |
| F-10 | Module 05 inlines `statusLine` JSON with escaped double quotes; the `STATUSLINE_CMD` substitution route bans them. Both correct, neither cross-referenced. | **FIXED** — a cross-reference at each site naming the other route, why the rule differs, and SB-B as the failure it prevents. |
| F-11 | BLUEPRINT said the seed interview takes "ten minutes" against "fifteen" at four other sites. | **FIXED** — fifteen. |
| F-12 | "Stage" is used in BLUEPRINT before its definition, and "phase" was never defined anywhere. | **FIXED** — module 04's vocabulary section now defines **phase** too, with the "read phase as round" fallback; BLUEPRINT and CONTEXT-ARCHITECTURE point at it at first load-bearing use. |
| F-13 | "cert-green pre-authorization" was used in README's module table with no definition on the evaluator's route. | **FIXED** — a defining clause at first use. |
| F-14 | `kit.config.local.example` said "`.gitignore` already excludes `kit.config.local`", which is false at Step 1 copy time — the rule lands at Step 4. | **FIXED** — the sentence is conditional and true, and tells a standalone adopter to add the rule first. |
| F-15 | Module 02's "the hook reads eight keys" against a nine-key table and nine keys in the source. | **FIXED** — nine, with the row arithmetic stated. |
| F-16 | The repository-size figure was stale (`~525KB, 50 files` against 585,001 bytes / 51 files measured at `641b392`). | **FIXED** — re-measured on this pass's tree, dated, with the prior figures kept and a note that the number moves with every errata pass. |
| F-17 | Step 9's "check `tokens : N` is the number you meant" fires falsely: the scanner de-duplicates case-insensitively, so a name and its capitalised variant are two lines that report `tokens : 1`. Measured. | **FIXED** (document, not scanner) — the dedup is documented where `N` is read. |
| F-18 | Step 4's "(20 min)" understated a JSON substitution, four constants, a gate table, a selftest case and two config keys by 2–3× for a first-timer. | **FIXED** — 45–60 minutes first time, and the hour budget in QUICKSTART, README and BLUEPRINT reconciled to the new sum (90 minutes to two hours). |

---

## Walk #12 — stranger onboarding, the dry-test literalist

The twelfth walk was the first dry-test: a careful literalist re-walked the
full document after the walk 8–11 errata, verifying every checkpoint and
auditing the end state against the kit's stated intent. It reached the
documented done state, confirmed the prior fixes it crossed, verified the live
hook with its own configured tier values, and found **6** new defects — one
major, two minor, three nits — all in the same class the register keeps
recording: a committed artifact or a load-bearing rule that no checkpoint
reaches. The loop was therefore **not dry** at walk 12.

| # | Finding | Disposition |
|---|---|---|
| W12-1 | Step 1 ("illustrative defaults you may never need") and Step 7 ("every other shipped placeholder is a fill-in you missed") gave opposite rules for the nine placeholder values that legitimately survive in the committed `kit.config` at done. | **FIXED** — Step 7's rule is scoped to the `docs/*.md` ledgers its own scan covers; Step 1 gains the deciding rule (unadopted-module keys, local-half keys, `RATIO_CEILING`); the steps cross-reference. |
| W12-2 | Step 8 was the one template step whose committed artifact no checkpoint reached: the collaboration profile could ship with a raw `{{KNOWLEDGE_DIR}}` and its template header, and nothing noticed — despite Step 6 promising "Step 8 spells out what it means for that one file". | **FIXED** — Step 8 instructs the substitution and the header deletion, carries its own runnable checkpoint in both shells, and the smoke now renders and asserts the profile. |
| W12-3 | `tools/deident_scan.py` makes Step 9's publish-safety judgment but the document never put it in `JUDGE_PATHS` — the kit's own "the config that parameterises the judges is itself a judge" reasoning, not applied. | **FIXED** — Step 6 adds the scanner to `JUDGE_PATHS` in both `verify.py` and `kit.config` (with the reason it cannot happen at Step 4); Step 9 stages `tools/verify.py`; the smoke walks the whole ripple. |
| W12-4 | Step 1 listed `GATE_COMMAND` as fill work; its shipped value is already correct and the checkpoint regex omitted it. | **FIXED** — five keys to fill plus "confirm `GATE_COMMAND`"; the smoke asserts it non-empty. |
| W12-5 | `REPORTS_DIR = docs/reports` renders into two binding rules and no step created the directory. | **FIXED** — Step 7's line is `mkdir -p docs/reports`, with the empty-directory caveat stated and the pwsh note corrected to measured behaviour. |
| W12-6 | Step 8 described `CLAUDE.md` as naming `{{KNOWLEDGE_DIR}}/collaboration-profile.md`, a file state Step 6's own checkpoint forbids. | **FIXED** — reworded to the post-substitution state, and the adjacent branch sentences aligned to Step 6's real branches. |

The walk-12 errata pass also ran a full Steps 4→9 re-walk after its own edits —
the structural answer to the rework class walks 10 and 11 recorded (three
findings across them were introduced by this loop's own errata passes). The
re-walk caught three downstream inconsistencies of the pass's own edits before
they shipped.

---

## Walk #13 — stranger onboarding, the thorough adopter

The thirteenth walk combined the full hands-on walk, the end-state audit, and
doctrine spot-checks against the shipped files. **The walk itself was clean:**
all nine steps ran as printed in pwsh, every checkpoint matched observed
output, and the 12-property end-state audit found nothing broken that no
checkpoint caught. Its six findings — 0 major, 3 minor, 3 nit — were all in
the meta layer, and two were this register's own bookkeeping falling out of
date again one walk after F-6 fixed the class.

| # | Finding | Disposition |
|---|---|---|
| KI-1 | The "authoritative" walk timeline had no row for walk 12 while a Walk #12 section existed — the table violated its own rule that it is what the numbers mean. Introduced by the walk-12 errata's own register edit. | **FIXED** — row added; and the walk-13 close adds its own row in the same commit as its section, which is the structural rule going forward. |
| KI-2 | Three sentences still said "eleven walks" against twelve documented — a recurrence of F-6, recorded FIXED one walk earlier. | **FIXED** — counts corrected; the recurrence is the finding: a hand-maintained count in prose goes stale every time a walk lands, so the count now lives primarily in the table. |
| BP-1 | BLUEPRINT's module table gave module 08's contract surface as "none — pure text" against the module's own three-item file contract. | **FIXED** — the cell states the real surface. |
| CA-1 | CONTEXT-ARCHITECTURE attributed the collaboration profile to module 01; it ships in module 08. | **FIXED** — attribution corrected. |
| M08-1 | Module 08's README claimed `kit.config` supplies a token no shipped file in the module uses. | **FIXED** — the contract names the one real token. The first fix attempt tripped the smoke's manifest detector (the word "slot" beside a token reads as an inventory) — the guard caught its own author; reworded. |
| QS-1 | Step 6 edits the runner and no later step re-ran `--selftest`, against the document's own after-every-runner-change rule. | **FIXED** — Step 6 now prints the selftest re-run where the edit happens. |

---

## Walk #14 — stranger onboarding, the final cap walk

The fourteenth walk closed the stranger-onboarding loop at its seven-stranger
cap. **The hands-on walk was clean for the second consecutive time**: all nine
steps as printed, every checkpoint matched, and a 14-property end-state audit
found nothing uncaught. All three deliberate reds produced their documented
verdict words. Eight findings, none major, all documentation.

The loop therefore ended **not-dry by its own rule** (two consecutive
zero-finding strangers never occurred), and the structural finding is stated
here as the loop's outcome: *the adopter-facing walk converged to clean and
stayed clean; the kit's residual finding generator is its documentation
meta-layer — module READMEs cross-describing each other's contracts, and this
register describing itself.* The owner ruled (2026-08-20) that polishing that
tail past the point of adopter impact is negative-return; findings below that
materiality bar are now rejected, not fixed.

| # | Finding | Disposition |
|---|---|---|
| M03-1 | Module 03's "full veto list" named four tokens; the shipped gate vetoes on five (`UNSTARTABLE:` omitted). | **FIXED** — five named. |
| M02-1 | Module 02's README quoted the two-count required line the shipped pattern rejects, and named 3 of 5 veto tokens. | **FIXED** — three-count form and full veto list, matching module 03. |
| M01-1 | Module 01's contract with module 02 omitted `{{FORBIDDEN_SPAWN_TIER}}` — the key walk 7's MAJOR-1 called "the one people skip". | **FIXED** — four slots listed. |
| M02-2 | Module 02's standalone recipe never disposed of the `permissions.ask` block, landing `Edit(NONE/**)` rules the proof command cannot catch. Measured. | **FIXED** — the recipe says delete it unless enabling the tripwire, and why the proof stays green either way. |
| CA-2 | CONTEXT-ARCHITECTURE §5's diagram edges for the SessionStart and PreCompact hooks carried no NOT SHIPPED flag while BLUEPRINT's identical edges do. | **FIXED** — both edges flagged. |
| KI-3 | The walk-10 timeline row enumerates 9 items but disposes of 11. | **REJECTED** — register self-audit, below the materiality bar (owner ruling 2026-08-20). |
| KI-4 | A walk-13 self-description sentence is imprecise about which layer two findings were in. | **REJECTED** — same ruling. |
| QS7-1 | Step 7's pwsh note claimed the `mkdir` line is "silent the first time"; it prints a directory-listing table. | **FIXED** — the note describes the real output. |

---

## Review pass #15 — adversarial read of the streamlining report

The fifteenth entry is not a walk. The walk-14 close produced a streamlining
report; this pass read that report and the shipped files it described, looking
for hazards that survive a clean walk because a walk never puts the kit in the
state that triggers them. Three did. Each is a case where the kit is green and
the green is wrong, or where the printed instruction costs an adopter work that
is not theirs to lose.

The pattern across all three: a **stranger walking the document in an empty
repository cannot meet any of them.** The empty repo has no pre-existing
`.gitignore`, no colleague's uncommitted work, and no second machine. The
onboarding loop converged to clean and then stopped finding these because the
walk itself is the wrong instrument for them.

| # | Finding | Disposition |
|---|---|---|
| SR2-1 | A `JUDGE_PATHS` entry covered by the adopting repo's pre-existing `.gitignore` is invisible to `git status --porcelain -- <path>`, which prints nothing and exits 0. The `judges` gate then read permanently clean over a file nobody was judging — a full `VERIFY: PASS` over a `.claude/settings.json` anyone could edit to disarm every hook. `.claude/` is a common entry in an existing ignore file, so this is reachable on a real adoption and not on the smoke's scratch repo. | **FIXED** — the startup assertion now asks `git check-ignore` about every `JUDGE_PATHS` and `CERT_PATHS` entry whenever a git-dependent gate is selected and the root is a work tree, and an excluded, untracked entry ends the run `VERIFY: ABORTED` (exit 2) naming the path. Git that cannot answer is also a refusal, not a pass. Registered as `check:judged-paths-not-excluded` with its expectation read from git. **The control is `adoption_smoke.py` phase 12**, which plants a real ignore rule over a real judge path in a real repository, in both rule shapes, and asserts that force-tracking the file clears the abort; the runner's selftest checks cover only how the assertion reacts to an injected answer. That division is itself a measured lesson: the first version of this fix corrupted every path it asked about — text-mode stdin appended a carriage return on Windows, so exact-path rules were missed and tracked files false-aborted — and all three gates were green over it, because nothing in the kit ran the shipped probe. QUICKSTART Step 4 names the failure mode beside the `.gitignore` housekeeping. |
| SR2-2 | The hook bans `git add -A`, `--all` and `.`, but both printed `git add` lines in QUICKSTART stage **directory** pathspecs (`tools`, `docs`, `src`). On a shared repo with other people's work in progress they sweep it into the adoption commit — through the kit's own enforcement layer, which reads them as compliant. | **FIXED** — both lines (Step 4 and Step 9) carry a warning at the point of use: these are directory pathspecs, run `git status` first, stash or exclude what is not the kit's. Docs only: a staging tool was considered and rejected in adversarial review. |
| SR2-3 | A hosted CI runner is a second machine, and `.claude/settings.json` carries the absolute paths of the machine that wrote it. On a runner every hook block reports `UNSTARTABLE:`, which vetoes the `hooks` gate, so CI is red on every push for a reason that is false about the project. Module 07's README said nothing about it. | **FIXED** — the "Adopt it" list now carries the reality and the documented remedy (`--skip hooks` in the CI invocation only, expected exit 3), with the cost stated in the same language modules 02 and 03 use: a permanently skipped gate certifies less. The local full run stays the certification bar. |
| SR2-4 | This register had no entry for the review pass or its findings, so the fixes would have shipped with the timeline still ending at walk 14. | **FIXED** — timeline row 15 and this section, written in the same work session as the fixes and committed with them. |

---

## Round #16 — the second authority, and what it found on its first run

The sixteenth entry is not a walk either. The kit gained an **optional**
mechanical substitution path, `tools/kit_render.py`, offered beside the by-hand
route QUICKSTART keeps as primary. The condition of building it was that the
smoke's hand-built adopter model stay exactly where it was, and that a new
phase render the same templates a second way and require the two to agree.

The phase disagreed on its first run, and the hand model was the side that was
wrong.

| # | Finding | Disposition |
|---|---|---|
| R16-1 | `adoption_smoke.py`'s Step 8 rendering deleted the collaboration profile's YAML front matter — `title`, `type`, `status`, `created`, `last_revised`, `sources` — because it stripped the template's guidance header by taking everything after the first `-->`. `PROFILE-TEMPLATE.md` is the only template in the kit whose header is not the first thing in the file; nine lines of front matter sit above it, and Step 8 instructs the adopter to delete the *comment*, not everything above it. **No checkpoint in the document could see the loss.** The front matter carries neither a `{{SLOT}}` nor a header marker word, so Step 8's own `grep` line (`\{\{\|Delete this comment on adoption\|TEMPLATE - the living`) stays green over a profile that has silently lost its provenance block. | **FIXED** — the hand model now excises the comment and keeps the text above it (`adoption_smoke.py`, Step 8 block), and Step 8's assertion gained the clause that would have caught it: the rendered profile must still start with its front matter. **The check that found it is `adoption_smoke.py` phase 13**, which renders the same templates a second way and diffs. The arbiter was neither authority: QUICKSTART Step 8 names what to delete, and it ruled for the tool. That ordering is now written into the phase's own failure hint, because "the check disagreed, so I edited the expectation until it agreed" is the shape a collapse of this guard would take. |

**Why this is the entry worth reading.** Every earlier entry in this register
was found by a person walking the document. This one was found by a *second
implementation of the same instruction*, and it was invisible to every human
check the kit ships — including the one written specifically to guard that
file. A defect that survives its own checkpoint is only reachable by an
independent expectation, which is the argument for keeping the hand model and
the tool apart, and for never resolving a disagreement between them by editing
whichever side is easier to change.

The tool was then reviewed spec-side against the punch list before any of it
was committed. Two of the five majors were defects inside the tool's own
headline guards: an output path constrained against the kit clone but not
against the target repository, so a `LEDGERS_DIR` of `../shared-docs` wrote
four files outside the adopter's repo and reported `PASS`; and a structural
merge that compared matcher strings as text, so `Write|Edit|NotebookEdit`
against `Edit|Write|NotebookEdit` appended a duplicate block — the gate then
firing twice — under a note saying the matcher "was NOT wired". Both are the
same shape as R16-1: a guard whose reach stops just short of the case that
reaches it, reporting green. Both are fixed, each with a negative control in
`kit_render.py --selftest` and an end-to-end control in phase 13.

---

## Round #17 — the adversarial personas, and the doctor

The seventeenth entry is not a walk either. Three independent adversarial reads
of the shipped kit — a controls graybeard, a team-lead evaluator, and a
skeptic — were run against `2c18c53`, and their findings were then attacked in
turn by a fourth read that conceded, rebutted or rescoped each one against the
owner's materiality bar. The owner ratified four items. This round implements
them.

The pattern in the ratified four is worth naming, because it is not the pattern
of the earlier walks. **Nothing here is a silent green.** Every one is a
*disclosure* finding: a mechanism that behaves exactly as its source says it
behaves, described by a sentence somewhere else in the kit that says something
stronger. In a kit whose thesis is that confident sentences must not outrun
measurements, that is the finding.

| # | Finding | Disposition |
|---|---|---|
| R17-1 | **The blanket-add ban had eight measured functional equivalents that passed silently**, and the docstring called the rule "DENIED outright". Found independently by all three readers: `git add -Av`, `git -C <path> add -A`, `git stage -A`, `git add -u`, `git add :/`, `git add '*'`, `git commit -am`, and — the worst, because nobody types it to evade anything — **any indented occurrence**, since one leading space or tab defeated the `^` anchor. That is the normal shape of a command inside an `if` or a `for`. | **NARROWED, NOT CLOSED**, and the status word is deliberate: see R17-5, which is the second round on this same rule and found ten more. (a) The pattern covers command position with indentation, git's global options before the subcommand, the `stage` synonym, combined short-flag clusters containing `A` or `u`, `--all` / `--update`, `.`, `:/` and `*` quoted or bare, and `git commit` with an `a`-bearing flag cluster. **Eight deny fixtures** — `t`, `u`, `v`, `w`, `x`, `y`, `z`, `aa`, one per measured form — plus the control `ab`, proving the scan does not read flags out of a quoted commit message. Fixtures `r` and `s` belong to R17-2, not to this row. (b) The durable answer — judge the INDEX, not the string — is **RECORDED, NOT BUILT**, with the reason: a PreToolUse hook runs *before* the command, when `git diff --cached` still describes the world as it was, so the index judgement belongs in a git `pre-commit` hook at the moment the index is final. Until a project installs one, the compensating pair is the pattern plus the sweep list the gate prints when it denies, and `kit_doctor.py`'s dirty-paths check on demand. Neither stages anything. Both error directions are disclosed at `BLANKET_ADD`, beside point 1's, and **no completeness is claimed**. |
| R17-2 | **A `//` inside a string literal blanked the rest of its line**, taking any `agent(` call on that line with it — count 0 vs 0, which is silence. A URL is an ordinary thing to find in a workflow script, and the failure direction was a false ALLOW of an undeclared spawn. | **FIXED.** `strip_script_comments()` is now one scanner that recognises comments and string literals in source order, blanking comment text and string *contents* while preserving offsets. It has to be one pass: masking strings first would make `// don't` open a literal at the apostrophe and blank the rest of the file. Fixture `r` is the defect; fixture `s` is the control that the masking does not eat a `model:` sitting outside the string. **The first version of this fix shipped its two residuals in the WRONG DIRECTION** — the docstring called them "a loud, immediate, fixable deny" and both were measured as silent false allows, the same mechanism as the defect. Both are now closed (fixtures `ac`, `ad`) and the surviving residuals are stated as silent-allow: see R17-6. |
| R17-3 | **The cert-green token is an unsigned self-assertion.** No HMAC, no proof the runner ran; the file is gitignored and outside `JUDGE_PATHS`, so anything that can write a file can mint one. A security professional read it as a stronger attestation than it is. | **DECIDED AND LABELLED (owner-ratified 2026-08-20; the keying analysis accepted on review 2026-08-21), with the surviving half built.** The keying question was evaluated honestly and the answer is no: the agents this token governs run shell commands as the owner, with the owner's filesystem and environment, so there is nowhere to put a key they cannot read — not an environment variable, not a file outside the repository, not the settings file. A signature would raise forgery from "write a file" to "read a file, then write a file" while making the token read as an attestation it is not, which is a *worse* label, not a better control. So: the label ships, and it ships **inside the artifact** (a `label` field in the token itself), in `cert_green()`, in README's new Security scope section, and on every `kit_doctor.py` run. The half of the item that survives the keying decision is built: **`verify.py --mint-cert-token`** writes the token from the runner's single `PASS` return, carrying sha, timestamp and gate headlines, so the ordinary way to hold a token is to have certified rather than to have asserted. It is opt-in — a run that lifts a control should be asked for, not a side effect. |
| R17-4 | **The kit contained zero words of security scope**, repo-wide, while shipping controls that a public audience reads as security controls. | **FIXED** — README has a `Security scope` section: what the kit governs (correctness, cost, process integrity) and the four things it does not defend against (a malicious agent, prompt injection, credential exfiltration, supply chain), with the cert-green token and the hook's heuristics named specifically because both look stronger than they are. |

**Two same-class riders, absorbed into the doctor** rather than into the hook,
with the dispositions stated rather than implied. Both carry ids, because every
other finding in this register is citable by one and a JUDGMENT-LEDGER row has
to be able to name them:

- **R17-R1 — the hook's interpreter is outside the startability check.** The fixture
  harness proves a settings command names a script that *exists*; nothing
  proved the *interpreter* resolves. `PYTHON_BIN` ships as the bare word
  `python`, and the kit's own README documents the host where that breaks —
  stock Debian and Ubuntu ship `python3` with no shim. On that host every hook
  call produces no output, `--armed` still reports armed, and the run certifies
  a disarmed enforcement layer. **`doctor:hook-interpreter`** resolves the
  interpreter of every wired hook command against the filesystem and PATH.
  Scoped honestly: resolution is not execution, and an interpreter that starts
  and then crashes is the dead-man clause's job.
- **R17-R2 — the protected-path tripwire matches case-sensitively.** On Windows and on
  default macOS a differently-cased spelling of the protected path opens the
  same file and the tripwire says nothing; `cd` then a relative path, and
  symlinks or junctions, do the same. **The matching semantics were
  deliberately not changed** — folding case would be wrong on Linux, where the
  two spellings really are different files, and a gate that asks about a path
  the owner did not protect is the false positive that gets gates deleted.
  Instead point 4 joins point 1 on the disclosure list, in `touches_protected()`
  and in the module docstring, and **`doctor:protected-case`** *probes* the
  filesystem the tree is actually on — not `os.name`, because case-sensitive
  NTFS directories and case-sensitive APFS volumes both exist — and says what
  the mismatch costs there.

**And the tool the streamlining pass funded.** `tools/kit_doctor.py` is the
adopter-runnable "check my adoption" command: ten checks, `HEALTHY` /
`ATTENTION`, exit 0 / 1 / 2. The verdict word is deliberately not `PASS` —
that word belongs to the runner that runs the gates, and this tool runs none.
It stages nothing (an earlier design offered to `git add` what its dirty-paths
check found, and that design was killed in review), and `--selftest` holds the
prohibition to the source: the git verbs it uses are recovered from this file's
own text and checked against a read-only allowlist.

Two things about it are worth reading:

- **Every one of its ten checks is registered**, and `expectation_lint.py` now
  cross-checks the `doctor:` family against `kit_doctor.py` in both directions,
  exactly as it does the fixture family. That generalisation is the point: ten
  unregistered checks in one commit would have grown this register's own named
  blind spot faster than the lint that discloses it.
- **Run against the kit's own checkout it reports `ATTENTION`, and that is the
  correct answer.** The kit ships two `example_*` gates QUICKSTART Step 3 tells
  you to replace, and no `docs/ORACLE-<gate>.md` pages, because the kit is not
  an adoption. A diagnosis tool that made an exception for its own repository
  would be the first thing an adopter learned to distrust. The residual is
  recorded in the Open list below.

### The spec-side review of that work, and what it found

None of it was committed before a reviewer took the punch list, the owner's
rulings and the diff — never the implementer's report — and re-measured the
result. Fourteen findings. All four of the round's judgment calls came back
sound; the defects were in the hardening.

**Two of the four blockers were the SAME error direction the fixes were meant
to close.** That is the finding worth keeping:

| # | Finding | Disposition |
|---|---|---|
| R17-5 | **The widened blanket-staging pattern scanned across newlines**, because its token separator was `\s`, which matches newline. The scan ran off the end of the git command and through every following line until it met a quote or a `;&|`, so any later `-A`, `-u`, `.`, `*` or `a`-bearing flag denied the whole block. Five ordinary two-line blocks measured denying, `git commit -F msg.txt` followed by `ls -la` among them. The fix for the bypasses built the dead alarm the same file's own comment warns against. **And ten further real bypasses** were found in one session after three readers had already been through the rule: `git add ./`, `git add "-A"`, `git add --al`, `env`/`sudo`/`time`/`VAR=` prefixes, `sh -c`, a backslash continuation, `$(…)`, backticks, and `git add ':(top)'`. | **FIXED** for the false-deny class — every separator inside a command is `[ \t]`, never `\s`, and fixtures `ae`, `af` hold the line. The measured cost is that a blanket flag reached only by a backslash continuation stops matching, and that form was already a false negative, so nothing was lost. **NARROWED** for the bypasses: `./`, quoted flags, long-option prefixes, the assignment and wrapper prefix family, `$( … )` and `:(top)` are closed with a fixture each (`ag`–`am`); `git add --dry-run` is now deliberately allowed, because it stages nothing and it is the command an operator reaches for after a deny (fixture `an`). Nested shells, backslash continuations, backticks, `xargs`, aliases, runtime-built commands and post-quote flags are **NOT closed and are named** where the rule is defined. Backticks are excluded on purpose: a backtick code span in a commit message is commoner than the legacy substitution form. **No completeness is claimed anywhere**, and the durable index-based fix stays recorded. |
| R17-6 | **The string-literal fix disclosed its two residuals in the wrong direction.** The docstring called a regex literal with escaped slashes and a JS private field "a loud, immediate, fixable deny"; both were measured as **silent false allows** — over-blanking removes the `agent(` call with everything else, the count falls to 0 vs 0, and the gate says nothing. Same mechanism and same direction as the defect the fix was written for. In a kit whose thesis is that confident sentences must be measured, a disclosure that says a residual fails safe when it fails open is worse than no disclosure. | **FIXED, both of them, rather than re-labelled.** The scanner now recognises a regex literal when a `/` appears where an expression may start (and leaves division alone after an identifier, digit, `)` or `]`), and treats `#` as an ordinary character when it touches a `.` or an identifier, so `this.#id` survives while `x = 1  # note` is still a comment. Fixtures `ac` and `ad`. What genuinely survives — a `#` that is neither a comment nor a private field, a `/` in expression position after an unrecognised keyword, an `agent(` inside a template-literal interpolation, and a non-spawn `model:` — is now stated **as silent false allow**, with the one false-deny direction marked as such. |
| R17-7 | **`kit_doctor.py` wrote into the tree it was diagnosing**, then reported its own residue back as the adopter's dirty tree. Importing the target's `verify.py` and `hook_model_gate.py` left `__pycache__/*.pyc` beside each, which the dirty-paths check duly listed. The module docstring said "the only writes this tool performs are to stdout". The rule was applied to the case probe — which flips an existing filename rather than creating one — and missed for the imports. | **FIXED** — `sys.dont_write_bytecode = True` ahead of every import, asserted in `--selftest` against the interpreter's own state rather than against the source text, and verified live: `git status --porcelain -uall` on a scratch adoption is byte-identical before and after, with no `__pycache__` anywhere. |
| R17-8 | **The security-scope section carried one sentence a hostile reader could disprove** — "the hook's four rules are string heuristics; each one discloses both of its error directions in its own source". Point 2 discloses nothing and is not a string heuristic; point 4 disclosed one direction. Thirteen of the section's fourteen claims fact-checked clean. | **FIXED, by making it true rather than by softening it.** Point 4 gained its false-ask direction (a substring match fires on a longer path containing the configured one, and on prose mentioning it), point 1's directions were corrected under R17-6, and the sentence now says *three* rules are heuristics, names them, states that point 2 compares declared fields and is exact, and adds that no completeness is claimed. |

Nine smaller items were dispositioned in the same pass: a quoted or unquoted
interpreter path containing a space (the default Windows install location) is
no longer a false ATTENTION; the doctor's "every red line names a fixing step"
rule moved from a hand-enumerated selftest list into a `Finding` constructor
invariant, after a reviewer's mutation walked past the list; the never-stages
guard now reads every `git` argv literal in the file rather than the two shapes
it happened to use; a hand-written cert token reports `INFO` rather than `OK`;
the case probe looks one level down when a top level offers nothing to flip;
and the register's own counts, status words and stale fixture line were
corrected here.

---

## Open — what genuinely remains

- **`modules/07-ci/verify.yml.template` has never been executed with real
  slots.** Placeholders only an adopter can fill. Unproven, labelled so in its
  own README.
- **`.github/workflows/kit-ci.yml` cannot be proven locally.** It is verified
  by pushing and watching. Until then "host-agnostic" rests on dependency-free
  Python, a path-hygiene pass, the pwsh block executed live by phase 9, and
  selftests that pass here.
- **`statusline.ps1.template` was proven three passes ago and not since.** It
  is unchanged; `tools/statusline.py` is the variant under active test and the
  one module 05 recommends.
- **`--runner` and `--plant-f1` work only on an UNADAPTED runner.** Both drive
  the scaffold by renaming `example_unit` and deleting `example_lint`, so a
  runner whose example gates have already been replaced aborts with "update
  this script". Loud, not silent — and deliberately not fixed: adopted-runner
  support is a feature, and this was a fix pass.
- **Phase 9 walks the QUICKSTART's *commands*, not its *prose*.** A step whose
  explanation is wrong while its commands still run will pass. Fourteen walks in,
  prose is where nearly every finding comes from — an argument for the next
  reader, not against the check. Walk 11 narrowed the gap once: the walk now
  reproduces the *state* a reader's repository is in (an edited `kit.config`
  carried from Step 6 to Step 9) rather than only the commands, which is how
  F-1 escaped three passes in a row.
- **The expectation lint cannot see an unregistered check.** Narrowed for two
  families now — the hook fixtures against `hook_fixtures.py` and the doctor's
  checks against `kit_doctor.py`, both directions — but everything else still
  depends on the author adding a row. Waived in the registry, in the open.
- **Point 3 of the hook is a heuristic too, the durable fix is not built, and
  NO COMPLETENESS IS CLAIMED.** Its covered list grew twice in one week and the
  second round found ten forms after three readers had been through the first.
  Still open and silent: a nested shell (`sh -c 'git add -A'`), a backslash
  line continuation, backtick command substitution (excluded on purpose — a
  backtick code span in a commit message is commoner than the substitution
  form), `xargs git add`, an alias, a command built at runtime, a blanket flag
  after a quoted argument, and any script the command invokes. Judging the
  *index* catches all of them, and a PreToolUse hook cannot do it — it runs
  before the command. The right home is a git `pre-commit` hook, and none
  ships. Compensating pair, stated wherever it is relied on: the pattern, the
  sweep list the gate prints on a deny, and `kit_doctor.py`'s dirty-paths
  check. Widening also bought a false-deny direction — `^[ \t]*` matches an
  indented occurrence inside a heredoc or a multi-line commit message — taken
  deliberately, because a false deny is loud and fixable. An earlier version
  bought a much worse one by using `\s` as its token separator; see R17-5.
- **Point 4 of the hook is a heuristic and cannot be made otherwise by a
  string matcher.** Case folding on a case-insensitive filesystem, `cd` then a
  relative path, and symlinks or junctions are all silent-allow directions.
  Disclosed in `touches_protected()` and in the module docstring; measured for
  the host you are on by `doctor:protected-case`. Not fixed by folding case,
  because that would be wrong on Linux.
- **The cert-green token is unsigned and unsignable at this privilege level.**
  Anything able to write a file can mint one. Labelled in four places
  including inside the artifact; see round #17 for the keying analysis. If your
  harness ever runs agents under a principal that cannot read the owner's
  files, the HMAC becomes worth building and the analysis flips.
- **The kit ships no `docs/ORACLE-<gate>.md` pages of its own**, so
  `kit_doctor.py` reports `ATTENTION` against the kit's own checkout for all
  four of its gates. Correct rather than broken — two of the four are the
  example gates QUICKSTART tells you to delete — but it means the kit ships no
  *filled* worked example of `ORACLE-WORKSHEET.md`, which is the artifact an
  adopter would most like to copy. Recorded, not built.
- **`verify.py --mint-cert-token`'s write path is exercised only by a
  certifying run.** Its refusal on a non-PASS verdict, its payload and its path
  resolution are all covered by `--selftest`; the four lines that resolve HEAD
  and write the file cannot run while the judge surface is dirty, which is by
  construction the state of a tree that has just changed the runner. The first
  green certification after this round is what proves them.
- **The statusLine command has no startability check** (hook commands do). A
  mis-pathed board fails silently — observability, not enforcement. Fix shape
  recorded in the release-walk section above.
- **Point 1 of the hook is a heuristic** — counting after comments and string
  contents are blanked. Three silent-false-allow directions were closed in
  round #17 (a URL in a string literal, a regex literal with escaped slashes, a
  JS private field). What remains, and every item is a **silent false allow**:
  a `#` that is neither a comment nor a private field (`const c = #fff`); a `/`
  in expression position that is really division after a keyword the scanner
  does not know; an `agent(` written inside a template-literal interpolation;
  and a `model:` in a data structure that is not a spawn. The single false-deny
  direction is an unterminated quote. All of it is in the scanner's docstring.
  A parser is the real answer and is out of scope for a gate.
- **~625KB of mostly text** (624,761 bytes, 51 tracked files, no binaries)
  measured on the walk-11 errata tree, 2026-08-20 — well above the original
  ~150KB guidance. A deliberate trade: the reasoning travels with each template.
  **This number moves with every errata pass** (it was ~525KB / 50 files when
  first recorded, and 585,001 bytes at `641b392`): it is a measurement at one
  commit, not a budget. Re-measure with `git ls-files` rather than trusting the
  figure.

### Whose settings file? — the team story (walk 11, F-3 and F-7)

**The kit is written for one owner and one orchestrator seat, and the wiring
assumes it.** Measured on a second machine: rewrite the absolute paths in the
committed `.claude/settings.json` to a plausible teammate's root and you get
three `UNSTARTABLE:` lines, `HOOK NOT ARMED`, and
`VERIFY: FAIL — RED: judges, hooks`. The file is required to hold absolute
paths (a hook that cannot start enforces nothing), is committed, and is inside
`JUDGE_PATHS` — per-machine, shared, and judged at the same time. Every
recovery available today costs something: edit it locally and the `judges` gate
stays red; edit and commit and the first developer breaks.

Four more single-seat assumptions travel with it, none of them wrong and none
of them decided for a team: one `docs/collaboration-profile.md` filename (the
name the rules file names) against module 08's advice to run the interview per
person; one `RATIO_CEILING` with no guidance on aggregating several people's
ratios; one `OWNER_ROLE` that several rules bind decisions to; and a cert-green
token that is gitignored and therefore per-machine by construction — the safe
direction, but unstated.

Why it is recorded rather than closed: this is **design work, not errata**.
Deciding it badly is worse than leaving it open, and the decision belongs to a
team that has one.

**Fix shape, when someone wants it:** generate `.claude/settings.json` from a
template plus per-machine values (the kit's own `.gitignore` already names
`.claude/settings.local.json` for the overlay half), and then rule explicitly on
whether the *generated* file stays inside `JUDGE_PATHS` — a generated file that
is judged reintroduces the same problem one layer up. Everything else in the
config split already works for a team: `kit.config` / `kit.config.local` is
documented in both directions, and a second clone certified green with no
`kit.config.local` at all.

Until that exists, README says "any stack and any model" and names team
adoption as undocumented, and QUICKSTART Step 4 carries the measured
consequence under "One machine per settings file".

### The resume wiring in CONTEXT-ARCHITECTURE §6 is not shipped (walk 11, F-4)

`CONTEXT-ARCHITECTURE.md` §6 describes three hooks in shipping-grade detail —
**SessionStart** (capped resume brief, ASCII-safe JSON, liveness markers),
**PreCompact** (the two-hop disk relay, with the measured finding that
PreCompact output cannot carry `additionalContext`), and a **handoff
PreToolUse** gate that denies subagent writes under the reports tree. **The kit
ships none of them.** The strings `SessionStart` and `PreCompact` appear in no
module, template, settings file or tool, and `hook_model_gate.py` has no
reports-tree branch.

The content is good and was paid for on the reference build; what was missing
was the label. §6 now opens with a NOT SHIPPED banner in the style module 07
uses for `verify.yml.template`, BLUEPRINT's diagram edges carry the flag, and
the forward references in §2–3 say the hook does not exist.

**Fix shape, when someone wants it:** each hook is small — the SessionStart
brief is a read of the newest checkpoint plus a hard character cap; PreCompact
is a write of one gitignored state file plus a liveness marker. What is not
small is the fixture table §6 itself demands: negative controls, a dead-man
fixture, an encoding regression, and for the handoff gate a fixture *pair*
submitted from both the subagent and operator sides. Build the fixtures with the
hook or the kit gains a control it cannot prove.

### No checkpoint template ships (walk 11, F-5)

The rendered rules file opens with `ON RESUME: read the newest
{{CHECKPOINT_GLOB}} FIRST`. On day one there is no such file: **no module ships
a checkpoint template, no QUICKSTART step writes one, and no check notices its
absence** — while module 04 ships four skeletons for lower-traffic documents.
The shape contract exists as prose in the governance template itself (four
clauses, ~90 lines) and in `CONTEXT-ARCHITECTURE.md` §3.

Labelled rather than built: the template line now says the first checkpoint is
written at the first stage close, and QUICKSTART Step 6 says the same on the
adopter's path. That makes the instruction true; it does not make the artifact
exist.

**Fix shape, when someone wants it:** a `CHECKPOINT-TEMPLATE.md` in module 01
with the four clauses as headings and one worked example, plus a stage-close
checklist line that names it. Cost is small; the reason it was not done in an
errata pass is that a new shipped template disturbs the slot registry and the
smoke's phase-10 counts, which is a change to checked material rather than to
prose.

---

**Meta-lesson, fourteen walks in.** Every independent walk found something the
previous layer missed, and each fix added a check that makes that class loud.
Walk 7 (release audit) found three, all one class, now a lint. Walk 8 found one
more — a detector that skipped most of its subjects while reporting a green
count — and its fix makes the check state its own coverage. Walk 9 found a scan
that certified a tree it had not read. Walk 10 found the general form: **a
load-bearing instruction in prose beside a checkpoint that measures something
else**, and the fix pattern is to move the instruction into the checkpoint.

Walk 11 found the next layer out, and it is a different shape. Its findings are
not silent greens; they are **true sentences about the reference build printed
as if they were true about this kit** — hooks described but not shipped, a
resume anchor with no artifact, a team claim with one seat behind it. The class
is *unlabelled provenance*, and no check catches it, because every sentence
involved is accurate about something. The countermeasure the kit already owns is
module 07's practice of labelling the one unproven file loudly; walk 11's errata
applies it to three more places. Walk 13 confirmed the hands-on walk now runs
clean end to end; its six findings were all in the meta layer — this register's
own bookkeeping and cross-module attributions — which is where walk 11's class
predicts they would be. (Walk 12 had found the last in-walk defects: six, led
by the one template artifact no checkpoint reached.)

There is also a rework signal worth naming: walk 10's S3-F1 was introduced by
walk 9's K-3 fix, and walk 11's F-1 was introduced by that chain. Three
consecutive errata passes each broke the same printed commit line in a new way.
Phase 9 walks the commands, and the commands kept passing, because the walk's
scaffold did not have the state a reader's repository had. That is why walk 11's
fix changes the *walk* as well as the document: the smoke now edits `kit.config`
at Step 6 and certifies at the end of Step 9, the way a reader does.

The kit's own central claim, demonstrated on itself: **a suite written by the
author tests the author's mental model.** Only somebody else's hands find the
gap between the model and the artefact. The durable fix is never the patch — it
is the check that makes the class loud, and where possible one that walks the
*user's* path rather than the author's.
