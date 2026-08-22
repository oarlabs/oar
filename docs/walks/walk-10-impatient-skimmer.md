# Walk 10 — LLM-persona adoption walk: the impatient skimmer

**Register entry:** 10 · **Ran:** 2026-08-20 · **Kit commit:** `262077e` ·
**Findings, per the register:** 9 findings plus 1 end-state item
(`S3-F1`…`S3-F9`, `S3-E3`) · **9 fixed, 2 rejected with reason**

A large language model ran the persona below: read headings, code blocks,
tables and checkpoints, and pay for prose only when something breaks. It was
not a person. See [README.md](README.md) for what that means for the evidence.

The persona's primary data was **recovery cost** — when a copy-pasted command
block failed, how far did it have to read to recover, and did the needed
sentence live in the same step. It was also asked to mark each finding as
protectable by a document change or "the skimmer had it coming", and to be
honest about the difference. Two of its findings were later rejected with
reason on exactly that basis.

The walk reached the kit's full done state — `VERIFY: PASS`, clean tree,
`DEIDENT SCAN: 0 hits` — and the end-state audit then found three defects **no
checkpoint had caught**: no oracle worksheet existed at all, the rules file
would have shipped as an unrendered template carrying 45 unfilled slots, and a
gate with no oracle behind it certified green.

`KNOWN-ISSUES.md`, "Walk #10", carries every finding and its disposition. The
fix pass is commit `641b392`.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are an impatient skimmer. You do not read prose unless something forces you to. Your reading style: headings, code blocks, checkpoints, tables — that's it. You copy-paste command blocks and run them. You only go back and read the surrounding prose when a command fails, an output surprises you, or a checkpoint doesn't match — and when that happens, record HOW FAR you had to read to recover (one paragraph? the whole step? another document?). That recovery cost is your primary data. You work in PowerShell (pwsh).

WHAT COUNTS AS A FINDING for you:
- A command block that does not work when copy-pasted without reading the surrounding prose (e.g. it contains a placeholder that only the prose explains).
- A checkpoint that a skimmer passes wrongly (the state is wrong but the printed checkpoint looks satisfied).
- A step where skimming produced a broken or degraded adoption that no later checkpoint catches — say what is broken at the end that nothing flagged.
- A recovery that required reading far away from the failure (different step, different file) — cite where the needed sentence actually lives.
Rate each finding by whether a document change could protect the skimmer (e.g. the load-bearing sentence could live in the code block as a comment, or in the checkpoint) versus "the skimmer had it coming" — be honest about the difference; only the former are defects. Report both but mark them.

THE KIT: `<KIT>` (a git repo; the thing you downloaded). READ-ONLY — never modify, commit to, or write inside that directory.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger3-project`. Do all adoption work there.

METHOD: Start with README.md — skim it. Follow where it points (expected: QUICKSTART.md). Work through the steps in order at skimmer depth, actually EXECUTING every command block in pwsh. Findings cite document file and line (or exact quoted text). Go as far as the documents carry you; target is the documents' own "done" state.

HALT AUTHORITY: if you hit something that makes continuing meaningless, stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project if a document explicitly instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-3-skimmer-2026-08-20.md`. Plain technical-writer prose: short declarative sentences, active voice, no flourishes. Structure: persona recap; environment; step-by-step log (what you skimmed, what you ran, where you got forced into prose and how far you had to read); FINDINGS table (id, document:line, what failed, severity major/minor/nit, protectable-by-doc-change yes/no); end-state audit (what is broken/degraded at "done" that nothing flagged, if anything); verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero protectable findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity — protectable y/n).
```

## What it returned

The persona returned `verdict: FINDINGS 8` with a 17,383-byte report. **The
returned verdict number and the register's count differ, and the difference is
the persona's own instruction:** the handoff told it to report `FINDINGS <n>`
against a definition of DRY that counts only protectable findings, and its
report table carries nine rows (`F1`…`F9`) of which it marked one
non-protectable. The register counts all nine plus the end-state item, which is
why its row reads "9 findings + 1 end-state item". The register is the
authority; the discrepancy is recorded here rather than smoothed over.

Its first three findings, in its own summary lines, with the
document:line citations dropped and the tense shifted to past:

- F1 — the Step 4 commit line staged a directory that does not exist for anyone
  who skipped the command-less Step 3; `git add` is atomic, so nothing was
  staged and no commit happened, and the fix sentence sat 23 lines below, past
  the whole checkpoint list — major, protectable.
- F2 — Step 6's checkpoint went fully green with a rules file still holding 45
  unfilled slots and its delete-me header; the checkpoint measured the hook,
  not the rules file the step is named for — major, protectable.
- F3 — the document claimed a check on the rendered rules that no adopter could
  reach; the only implementation ran against the kit's own scaffold and never
  read the adopting repository — major, protectable.
