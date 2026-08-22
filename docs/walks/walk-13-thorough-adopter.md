# Walk 13 — LLM-persona adoption walk: the thorough adopter

**Register entry:** 13 · **Ran:** 2026-08-20 · **Kit commit:** `404da28` ·
**Findings, per the register:** 6 (0 major, 3 minor, 3 nit) · **All 6 fixed**

A large language model ran the persona below: the full hands-on walk, plus an
end-state audit, plus doctrine spot-checks against the shipped files. It was
not a person. See [README.md](README.md) for what that means for the evidence.

**The hands-on walk was clean.** All nine steps ran as printed in PowerShell,
every checkpoint matched observed output, and the 12-property end-state audit
found nothing broken that no checkpoint caught. The tree reached the documented
done state: `VERIFY: PASS (exit 0)`, `DEIDENT SCAN: 0 hits`, clean tree, 17
tracked files.

All six findings were in the meta layer — register bookkeeping, cross-module
attribution, and one place where a step's prose and its checkpoint disagreed.
Two of them were this register's own bookkeeping falling out of date one walk
after a fix pass had recorded that class closed.

The prompt is explicit that a clean walk honestly reported is the most valuable
possible result, and that manufacturing findings to look thorough is not
wanted. It is equally explicit that suppressing a real finding to look clean is
not wanted either. Both halves matter when reading a clean result.

`KNOWN-ISSUES.md`, "Walk #13", carries every finding and its disposition. The
fix pass is commit `24f5e13`, with a follow-on register correction in `d08b925`.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). This prompt also
named the session scratch root by its directory name; that name is redacted to
`<SCRATCH>` like the paths above. No other text was changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a thorough adopter. You do the full hands-on walk AND the claim-checks: (1) read README and follow its adopter route through QUICKSTART start to finish, executing every command as printed in pwsh and verifying every checkpoint including the runnable ones; (2) at the end, audit your finished tree against the kit's stated intent — anything broken or degraded at "done" that no checkpoint caught is a finding; (3) after the walk, read BLUEPRINT.md, CONTEXT-ARCHITECTURE.md and KNOWN-ISSUES.md and spot-check their claims against what you just built and against the shipped files — an unverifiable or contradicted claim is a finding, and a claim clearly labeled as unshipped/out-of-scope is NOT a finding. You are precise: findings cite document file and line (or exact quoted text), never a vibe.

THE KIT: `<KIT>` (a git repo; the thing you downloaded). READ-ONLY — never modify, commit to, or write inside that directory. Set PYTHONDONTWRITEBYTECODE=1 for commands you run inside it.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger6-project`. Do all adoption work there. Use your own token file for any deident step, at a path INSIDE your scratch project's parent — do not touch any file already in the <SCRATCH> root.

REPORT EVERY POINT where a document fails you: a command that does not run as printed; a step unreachable where placed; a checkpoint that does not match observed output; a term used before definition; a decision the text does not let you make; a claim your tree or the shipped files contradict. If you find NOTHING new, say so plainly — do not manufacture findings to look thorough; a clean walk honestly reported is the most valuable possible result. Equally: do not suppress a real finding to look clean.

HALT AUTHORITY: if you hit something that makes continuing meaningless, stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project where a document instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-6-thorough-2026-08-20.md`. Plain technical-writer prose. Structure: persona recap; environment; step-by-step log (one line per step that matched its checkpoint exactly; detail only where something surprised you); end-state audit table; doctrine spot-check log (claim → how checked → verdict); FINDINGS table (id, document:line, what failed, severity) or the explicit statement "No new findings"; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines (one line per finding, or "no findings").
```

## What it returned

The persona returned `verdict: FINDINGS 6` with a 23,163-byte report. Its
opening summary lines:

- The hands-on walk was clean. All nine steps ran as printed in pwsh, every
  checkpoint matched observed output, and the tree reached the documented done
  state: `VERIFY: PASS (exit 0)` and `DEIDENT SCAN: 0 hits`, clean tree, 17
  tracked files.
- No command failed to run as printed; no step was unreachable where placed; no
  term was used before definition on the adopter's route; every decision the
  text asked for was answerable.
- The 12-property end-state audit found nothing broken or degraded that no
  checkpoint had caught.
