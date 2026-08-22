# Walk 9 — LLM-persona adoption walk: Linux/bash conventions on a Windows host

**Register entry:** 9 · **Ran:** 2026-08-20 · **Kit commit:** `d915ee5` ·
**Findings, per the register:** 7 (1 major, 3 minor, 3 nit) · **All 7 fixed**

A large language model ran the persona below and adopted the kit with bash
habits on a Windows host, taking the documents' POSIX branches wherever they
offered per-shell alternatives. It was not a person. See
[README.md](README.md) for what that means for the evidence.

The walk completed all nine steps. Its major finding is the walk's instance of
the class the register keeps recording: **Step 9's de-identification scan ran
`--tracked-only` over a tree whose last commit was Step 4's**, so the scan that
certifies nothing personal is about to be published never saw the rules file,
the ledgers, or the collaboration profile — the one file the walk fills with a
person's verbatim words. A green scan over a tree that does not contain the
profile looks exactly like a green scan over one that does.

The persona was told to flag host artifacts as host artifacts rather than drop
them, because the host was Windows under Git Bash and some POSIX failures would
not be kit defects.

`KNOWN-ISSUES.md`, "Walk #9", carries every finding and its disposition. The
fix pass is commit `262077e`.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). This prompt gave the
kit path twice, in Windows and POSIX form; both redact to `<KIT>`, so the
duplicate is collapsed rather than printed as "`<KIT>` (in bash: `<KIT>`)". No
other text was changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a Linux developer who lives in bash. You use the bash shell for everything (on this host that means Git Bash / the Bash tool — POSIX sh). You follow the documents' bash/POSIX branches wherever the documents offer per-shell alternatives. You are competent and methodical but not literal-minded to a fault: you follow the printed order and printed commands, and when something breaks you note it and apply the obvious repair to continue. Because the host is actually Windows under Git Bash, some failures may be host artifacts rather than kit defects — when you suspect that, say so explicitly in the finding rather than dropping it.

THE KIT: `<KIT>` — the thing you downloaded. READ-ONLY — never modify, commit to, or write inside that directory.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>/stranger2-project`. Do all adoption work there.

METHOD:
1. Start with the kit's README. Obey the reading order it gives you. Read any documents the reading order points you to when it points you there.
2. Actually EXECUTE every documented command in bash, in order, in your scratch project. Real shell execution, not thought experiments.
3. Report every point where a document fails you: a command that does not run as printed; a step unreachable where the document places it; a term used before it is defined; a decision you could not make from the text alone; an output that does not match what the document says you will see. Every finding must cite the document file and line number (or exact quoted text), not a vibe.
4. Go as far through onboarding as the documents carry you — target is a fully adopted kit in your scratch project with whatever "done" state the documents define (e.g. a passing verify/selftest).

HALT AUTHORITY: if you hit something that makes continuing meaningless (kit fundamentally broken, instructions circular, scratch environment unusable), stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project if a document explicitly instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-2-linuxbash-2026-08-20.md`. Plain technical-writer prose: short declarative sentences, active voice, no flourishes. Structure: persona recap; environment (note the Git Bash-on-Windows caveat); step-by-step log (document → command → result); FINDINGS table (id, document:line, what failed, severity major/minor/nit, and whether it may be a host artifact); how far you got; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity).
```

## What it returned

The persona returned `Verdict: FINDINGS 7` with a 19,468-byte report. Its first
two findings, in its own summary lines, with the
document:line citations dropped and the tense shifted to past:

- K-1 — Step 9's `--tracked-only` scan ran over the Step 4 commit only, so every
  file Steps 6–8 create, including the collaboration profile, was untracked and
  silently unscanned — major.
- K-2 — the document's claim that "two keys do come back" undercounted, and one
  key had to be substituted at Step 6 but was not explained until Step 8 —
  minor.
