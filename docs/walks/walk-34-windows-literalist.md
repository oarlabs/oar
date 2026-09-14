# Walk 34 — LLM-persona adoption walk: Windows/pwsh, literal obedience (v0.1.2)

**Register entry:** 34 · **Ran:** 2026-09-13 · **Kit commit:** `1395e92`
(tag `v0.1.2`) · **Findings, per the register:** 13 (0 major, 5 minor, 8 nit) ·
done state reached

A large language model was given the persona below and executed
`QUICKSTART.md` in a throwaway git repository on Windows, in PowerShell,
obeying every printed instruction literally, against the tagged public
release. It was not a person. See [README.md](README.md) for what that means
for the evidence.

The walk reached the document's stated done state: `VERIFY: PASS` and
`DEIDENT SCAN: 0 hits`. Every checkpoint output matched its printed
expectation except two (the pwsh `mkdir -p docs` duplicate, and the
`--exclude` checkpoint's one-exclude claim). `KNOWN-ISSUES.md`, this entry,
carries the finding count and which of this pass's items close each one.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a Windows developer working in PowerShell (pwsh). You follow the documents LITERALLY — every command exactly as printed, every step in the printed order, no improvisation, no fixing things silently. If a command fails as printed, that is a finding; record it and only then try the obvious repair so you can continue.

THE KIT: `<KIT>` (a git repo; treat it as the thing you downloaded). READ-ONLY — never modify, commit to, or write inside that directory.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger1-project`. Do all adoption work there.

METHOD:
1. Start with the kit's README. Obey the reading order it gives you (expected: README → QUICKSTART → module docs). Read CONTEXT-ARCHITECTURE.md and any PROSE_VOICE material when the reading order reaches them.
2. Actually EXECUTE every documented command in pwsh, in order, in your scratch project. Real shell execution, not thought experiments.
3. Report every point where a document fails you: a command that does not run as printed; a step unreachable where the document places it; a term used before it is defined; a decision you could not make from the text alone; an output that does not match what the document says you will see. Every finding must cite the document file and line number (or exact quoted text), not a vibe.
4. Go as far through onboarding as the documents carry you — target is a fully adopted kit in your scratch project with whatever "done" state the documents define (e.g. a passing verify/selftest).

HALT AUTHORITY: if you hit something that makes continuing meaningless (kit fundamentally broken, instructions circular, scratch environment unusable), stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project if a document explicitly instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; any subagent you spawn (avoid spawning any) inherits these rules and your model tier.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-1-winliteral-2026-09-13.md`. Plain technical-writer prose: short declarative sentences, active voice, no flourishes. Structure: persona recap; environment; step-by-step log (document → command → result); FINDINGS table (id, document:line, what failed, severity major/minor/nit); how far you got; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity).
```

## What it returned

The persona returned `verdict: FINDINGS 13` (0 major, 5 minor, 8 nit). Its
first three findings, in its own summary lines, with the document:line
citations dropped and the tense shifted to past:

- S1 — README stated version 0.1.0 and 208 registry rows while `VERSION` read
  0.1.1 and `expectation_lint.py` reported 217 entries — nit.
- S2 — the Step 2 pwsh block translated a bash `VAR=x cmd` line the bash
  block above it did not contain — minor.
- S3 — the second `mkdir -p docs` (Step 4.2) errored in pwsh with "already
  exists," because Step 3 had already created the directory, contradicting
  the Shell section's claim that every block runs as-is in pwsh — minor.

The reports themselves stay private; the register carries every finding's
disposition and this pass's closing items.
