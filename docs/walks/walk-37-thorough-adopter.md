# Walk 37 — LLM-persona adoption walk: the thorough adopter (v0.1.2)

**Register entry:** 37 · **Ran:** 2026-09-13 · **Kit commit:** `1395e92`
(tag `v0.1.2`) · **Findings, per the register:** 11 (0 major, 4 minor, 7 nit) ·
done state reached

A large language model was given the persona below: the full hands-on walk,
an end-state audit of the finished tree, and doctrine spot-checks against
`BLUEPRINT.md`, `CONTEXT-ARCHITECTURE.md` and `KNOWN-ISSUES.md`, all against
the tagged public release. It was not a person. See [README.md](README.md)
for what that means for the evidence.

The hands-on walk reached every printed checkpoint including `VERIFY: PASS`
and `DEIDENT SCAN: 0 hits`; the executables behaved as documented, including
the ones designed to fail. Every finding was in the documents and the
register: one pwsh command that errors where the register claimed it was
already fixed, a version stated three ways, an end-state directory the
binding rules name that no commit held, one wrong sentence about staging on
the existing-repo route, and seven nits. `KNOWN-ISSUES.md`, this entry,
carries the finding count and which of this pass's items close each one.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a thorough adopter. You do the full hands-on walk AND the claim-checks: (1) read README and follow its adopter route through QUICKSTART start to finish, executing every command as printed in pwsh and verifying every checkpoint including the runnable ones; (2) at the end, audit your finished tree against the kit's stated intent — anything broken or degraded at "done" that no checkpoint caught is a finding; (3) after the walk, read BLUEPRINT.md, CONTEXT-ARCHITECTURE.md and KNOWN-ISSUES.md and spot-check their claims against what you just built and against the shipped files — an unverifiable or contradicted claim is a finding, and a claim clearly labeled as unshipped/out-of-scope is NOT a finding. You are precise: findings cite document file and line (or exact quoted text), never a vibe.

THE KIT: `<KIT>` (a git repo; the thing you downloaded). READ-ONLY — never modify, commit to, or write inside that directory. Set PYTHONDONTWRITEBYTECODE=1 for commands you run inside it.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger6-project`. Do all adoption work there. Use your own token file for any deident step, at a path INSIDE your scratch project's parent — do not touch any file already in the <SCRATCH> root.

REPORT EVERY POINT where a document fails you: a command that does not run as printed; a step unreachable where placed; a checkpoint that does not match observed output; a term used before definition; a decision the text does not let you make; a claim your tree or the shipped files contradict. If you find NOTHING new, say so plainly — do not manufacture findings to look thorough; a clean walk honestly reported is the most valuable possible result. Equally: do not suppress a real finding to look clean.

HALT AUTHORITY: if you hit something that makes continuing meaningless, stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project where a document instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-6-thorough-2026-09-13.md`. Plain technical-writer prose. Structure: persona recap; environment; step-by-step log (one line per step that matched its checkpoint exactly; detail only where something surprised you); end-state audit table; doctrine spot-check log (claim → how checked → verdict); FINDINGS table (id, document:line, what failed, severity) or the explicit statement "No new findings"; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines (one line per finding, or "no findings").
```

## What it returned

The persona returned `verdict: FINDINGS 11` (0 major, 4 minor, 7 nit). Its
first three findings, in its own summary lines, with the document:line
citations dropped and the tense shifted to past:

- F1 — a `mkdir -p docs` at 4.2 errored in pwsh because Step 3 had already
  created the directory, and no `-Force` form the register claimed was
  shipped actually appeared in the document — minor.
- F2 — README stated three version numbers (0.1.0 in prose, `VERSION` at
  0.1.1, the register pointing at tag v0.1.2) with no single source of
  truth — minor.
- F3 — `docs/reports/` was created empty at Step 7 and git never tracked it,
  though the rendered rules file bound two rules to that path — minor.

The reports themselves stay private; the register carries every finding's
disposition and this pass's closing items.
