# Walk 35 — LLM-persona adoption walk: the impatient skimmer (v0.1.2)

**Register entry:** 35 · **Ran:** 2026-09-13 · **Kit commit:** `1395e92`
(tag `v0.1.2`) · **Findings, per the register:** 11 protectable (3 major) ·
done state reached

A large language model was given the persona below: read only headings, code
blocks and checkpoints; go back to prose only when a command fails, an
output surprises, or a checkpoint does not match; record the recovery
distance as the primary data. It executed `QUICKSTART.md` in a throwaway git
repository in pwsh against the tagged public release. It was not a person.
See [README.md](README.md) for what that means for the evidence.

The walk reached the document's stated done state: `VERIFY: PASS` and
`DEIDENT SCAN: 0 hits`. Two findings were caught by a later checkpoint before
they became silent damage; the rest were not. Two further observations were
recorded and explicitly marked non-defects by the persona itself (a literal
placeholder pasted without substitution; a stale version string that cost
the skimmer nothing). `KNOWN-ISSUES.md`, this entry, carries the finding
count and which of this pass's items close each one.

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
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-3-skimmer-2026-09-13.md`. Plain technical-writer prose: short declarative sentences, active voice, no flourishes. Structure: persona recap; environment; step-by-step log (what you skimmed, what you ran, where you got forced into prose and how far you had to read); FINDINGS table (id, document:line, what failed, severity major/minor/nit, protectable-by-doc-change yes/no); end-state audit (what is broken/degraded at "done" that nothing flagged, if anything); verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero protectable findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity — protectable y/n).
```

## What it returned

The persona returned `verdict: FINDINGS 11 (protectable)`, plus two further
non-defect observations. Its first three findings, in its own summary lines,
with the document:line citations dropped and the tense shifted to past:

- F1 — the second `mkdir -p docs` at 4.2 errored in pwsh ("already exists")
  because Step 3 had already created the directory — minor, protectable.
- F2 — the 4.4 mechanical renderer merged into 4.2's unfilled
  `settings.json.template` copy, doubling every hook entry instead of
  filling it; caught by `--armed`, so not silent — major, protectable.
- F3 — the same renderer also produced unannounced Step 6/7/8 `.kit-new`
  files, which the 4.7 commit's directory-form `git add` could pick up —
  minor, protectable.

The reports themselves stay private; the register carries every finding's
disposition and this pass's closing items.
