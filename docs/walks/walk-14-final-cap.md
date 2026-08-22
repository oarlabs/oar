# Walk 14 — LLM-persona adoption walk: the final cap walk

**Register entry:** 14 · **Ran:** 2026-08-20 · **Kit commit:** `d08b925` ·
**Findings, per the register:** 8 (0 major, 4 minor, 4 nit) ·
**6 fixed; 2 rejected below the owner's materiality bar**

A large language model ran the persona below: the full hands-on walk, an
end-state audit, and doctrine plus module-README spot-checks, including whether
the register's own walk timeline and counts are self-consistent. It was not a
person. See [README.md](README.md) for what that means for the evidence.

This walk closed the loop at its declared seven-walk cap. **The hands-on walk
was clean for the second consecutive time**: all nine steps as printed, every
checkpoint matched, a 14-property end-state audit found nothing uncaught, and
all three deliberate reds produced their documented verdict words.

**The loop ended not-dry by its own rule.** The kit's stopping rule for a
discovery loop is two consecutive zero-finding rounds; that never happened.
Ending at a declared cap with the result recorded honestly is the alternative
the kit's own loop-termination doctrine allows, and the register states it
plainly rather than presenting a clean hands-on walk as a dry loop.

Two findings were **rejected below the materiality bar** — both were the
register auditing itself — under the owner's ruling of 2026-08-20 that
polishing that tail past the point of adopter impact is negative-return.

`KNOWN-ISSUES.md`, "Walk #14", carries every finding and its disposition. The
close is commit `00a0e2e`.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). This prompt also
named the session scratch root by its directory name; that name is redacted to
`<SCRATCH>` like the paths above. No other text was changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a meticulous adopter with evaluator instincts — the kind of engineer who both does the work and checks the paperwork. You: (1) follow README's adopter route through QUICKSTART start to finish in pwsh, executing every printed command in order and verifying every checkpoint including the runnable lines; (2) audit your finished tree against the kit's stated intent (anything broken/degraded at "done" that no checkpoint caught is a finding); (3) then read BLUEPRINT.md, CONTEXT-ARCHITECTURE.md, KNOWN-ISSUES.md and the module READMEs of the modules you adopted, spot-checking claims against your tree and the shipped files — including whether KNOWN-ISSUES' own walk timeline and counts are self-consistent. An unverifiable or contradicted claim is a finding; a claim clearly labeled unshipped/out-of-scope is NOT.

THE KIT: `<KIT>` (a git repo). READ-ONLY — never modify, commit to, or write inside it. Set PYTHONDONTWRITEBYTECODE=1 for commands run inside it.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger7-project`. Use your own token file for the deident step at a path inside your scratch project's parent — do not touch any other file in the <SCRATCH> root.

REPORT EVERY POINT where a document fails you: a command that does not run as printed; a step unreachable where placed; a checkpoint that does not match observed output; a term used before definition; a decision the text does not let you make; a claim your tree or the shipped files contradict. If you find NOTHING new, say so plainly — a clean walk honestly reported is the most valuable possible result; do not manufacture findings. Equally, do not suppress a real one.

HALT AUTHORITY: if you hit something that makes continuing meaningless, stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project where a document instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-7-final-2026-08-20.md`. Plain technical-writer prose. Structure: persona recap; environment; step-by-step log (one line per step that matched exactly; detail only where something surprised you); end-state audit table; doctrine spot-check log (claim → how checked → verdict); FINDINGS table (id, document:line, what failed, severity) or the explicit statement "No new findings"; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines (one line per finding, or "no findings").
```

## What it returned

The persona returned `verdict: FINDINGS 8` with a 19,298-byte report. Its
opening summary lines:

- The hands-on walk was clean. All nine steps ran as printed in pwsh, every
  checkpoint matched observed output, and the 14-property end-state audit found
  nothing broken that no checkpoint caught. Ended at `VERIFY: PASS` and
  `DEIDENT SCAN: 0 hits`.
- All three deliberate reds produced the documented verdict word: pre-commit
  `RED: judges`, the dead-man corpse hook `0/15`, and `VERIFY: INSTRUMENTED` on
  the negative-control floor breach.
- The findings that followed were module-README and register cross-descriptions,
  none of them major.
