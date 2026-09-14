# Walk 36 — LLM-persona adoption walk: the team-lead evaluator (v0.1.2)

**Register entry:** 36 · **Ran:** 2026-09-13 · **Kit commit:** `1395e92`
(tag `v0.1.2`) · **Findings, per the register:** 16 (4 major, 5 minor, 7 nit),
plus 6 verified non-defects · no HALT

A large language model was given the persona below: a team lead deciding
whether four developers should adopt this kit. It read doctrine before
commands, cross-checked every doctrine claim against the shipped modules,
tools and its own hands-on walk of `QUICKSTART.md` against the tagged public
release, and assessed the team story — what four people adopting this
leaves undefined. It was not a person. See [README.md](README.md) for what
that means for the evidence.

Every executable did what its documentation said, including the ones built
to fail; the defects were in the documents and in the team story, not in
the runner. Recommendation: adopt partially, not the full QUICKSTART, and
not yet as a four-seat certification. `KNOWN-ISSUES.md`, this entry, carries
the finding count and which of this pass's items close each one.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
You are a developer who has never seen this kit. You have no context about it, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a team lead evaluating whether your team of four developers should adopt this "orchestration kit". You read doctrine before commands: start with README, then BLUEPRINT.md and CONTEXT-ARCHITECTURE.md and KNOWN-ISSUES.md (the evaluator's route, if README offers one), and only then work through QUICKSTART hands-on. You cross-check claims: when a doctrine document asserts something ("X is enforced", "Y is measured", "Z degrades gracefully"), you verify it against the modules, the tools, and your own hands-on walk. A claim you cannot verify from the shipped material is a finding. Internal contradictions between documents are findings. Terms used before definition are findings. You also evaluate the TEAM story: what breaks or is undefined when four people adopt this rather than one (whose kit.config.local, whose knowledge dir, who runs certification, what happens on a second machine).

THE KIT: `<KIT>` (a git repo; the thing you downloaded). READ-ONLY — never modify, commit to, or write inside that directory.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger4-project`. Work in pwsh. Do the QUICKSTART hands-on there after the doctrine read — actually execute the commands, in order.

WHAT COUNTS AS A FINDING:
- A doctrine claim (BLUEPRINT, CONTEXT-ARCHITECTURE, module READMEs) you cannot verify from the shipped material, or that the material contradicts.
- Contradictions between documents, or between a document and a tool's behavior.
- A command that does not run as printed; a checkpoint that does not match; a step unreachable in order.
- A term used before it is defined, or a decision the text does not let you make.
- A team-adoption question the documents leave undefined where a team lead needs an answer.
Every finding cites document file and line (or exact quoted text), not a vibe. Distinguish severity (major/minor/nit) and mark findings that are "deliberately out of scope and honestly labeled by the kit" as non-defects.

HALT AUTHORITY: if you hit something that makes continuing meaningless, stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project if a document explicitly instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-4-teamlead-2026-09-13.md`. Plain technical-writer prose. Structure: persona recap; environment; doctrine-read log (claims checked, with verdicts); hands-on log (step → command → result, condensed for steps that matched their checkpoints); FINDINGS table (id, document:line, what failed, severity); TEAM-STORY assessment (what four-person adoption leaves undefined); adopt/don't-adopt recommendation with reasons; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity).
```

## What it returned

The persona returned `verdict: FINDINGS 16 (4 major, 5 minor, 7 nit)`, plus
6 verified non-defects, no HALT. Its first three findings, in its own
summary lines, with the document:line citations dropped and the tense
shifted to past:

- F-1 — one tree carried three version identities: README said 0.1.0,
  `VERSION` read 0.1.1, the tag the register pointed at was v0.1.2 — major.
- F-2 — README's seen-red ratio (35 of 208) was stale against the lint's own
  printed line (43 of 217) — minor.
- F-3 — the file-targeted `git add` form's stated reason for omitting
  `.claude/settings.json` did not hold on a repository with no ignore rule
  over `.claude/`, leaving `judges` red after the commit — major.

The reports themselves stay private; the register carries every finding's
disposition and this pass's closing items.
