# Walk 8 — LLM-persona adoption walk: Windows/pwsh, literal obedience

**Register entry:** 8 · **Ran:** 2026-08-20 · **Kit commit:** `341d47d` ·
**Findings, per the register:** 13 (2 major, 8 minor, 3 nit) · **All 13 fixed**

This was the first post-ship adoption walk. A large language model was given
the persona below and executed `QUICKSTART.md` in a throwaway git repository on
Windows, in PowerShell, obeying every printed instruction literally. It was not
a person. See [README.md](README.md) for what that means for the evidence.

The walk completed all nine steps and ended at `VERIFY: PASS`. Twelve of its
thirteen findings are documentation defects; one is a check-coverage defect —
smoke phase 10 reported "all 13 template SLOTS manifests match their bodies"
while its detector silently skipped 10 of the 23 slot-using files, and one of
the skipped files really did carry the defect the check existed to catch.

`KNOWN-ISSUES.md`, "Walk #8", carries every finding and its disposition. The
fix pass is commit `d915ee5`.

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
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-1-winliteral-2026-08-20.md`. Plain technical-writer prose: short declarative sentences, active voice, no flourishes. Structure: persona recap; environment; step-by-step log (document → command → result); FINDINGS table (id, document:line, what failed, severity major/minor/nit); how far you got; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity).
```

## What it returned

The persona returned `verdict: FINDINGS 13` with a 20,107-byte report. Its
first three findings, in its own summary lines, with the
document:line citations dropped and the tense shifted to past:

- F1 — the governance template's own slot inventory omitted a slot its body
  used, so following `QUICKSTART.md` literally shipped a rules file with a raw
  slot — major.
- F2 — the smoke's manifest detector required the word "slots" and a token on
  one line, so 10 of 23 slot-using files were silently unchecked while the
  phase reported a complete-looking green count — major.
- F3 — the printed commit line did not stage the gate payload the same step had
  just told the adopter to write, so the post-commit run printed
  `VERIFY: FAIL — RED: judges` where the checkpoint stated `VERIFY: PASS`.
