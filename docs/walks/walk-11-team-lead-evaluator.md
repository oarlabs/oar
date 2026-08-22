# Walk 11 — LLM-persona adoption walk: the team-lead evaluator

**Register entry:** 11 · **Ran:** 2026-08-20 · **Kit commit:** `641b392` ·
**Findings, per the register:** 18 (7 major, 7 minor, 4 nit) ·
**All 18 dispositioned FIX**

A large language model ran the persona below: a team lead deciding whether a
team of four should adopt the kit, reading doctrine before commands, then
walking `QUICKSTART.md` hands-on, then simulating a second machine. It was not
a person. See [README.md](README.md) for what that means for the evidence.

This is the largest round the register carries, and the reason is the route.
Claim-checking `BLUEPRINT.md` and `CONTEXT-ARCHITECTURE.md` against the shipped
files, auditing the register for self-consistency, and running the kit as a
*team* would are four surfaces the first three walks never touched. Every
executable behaved as documented, including the ones designed to fail; all 18
findings are documentation defects.

Its recommendation was **adopt, partially, in a different order than the kit
proposes** — the ledgers and the collaboration module first, verification and
enforcement after. `DECISION-BRIEF.md` carries that recommendation as the first
of the limitations most likely to matter to an evaluator.

`KNOWN-ISSUES.md`, "Walk #11", carries every finding and its disposition. The
fix pass is commit `b50e1d6`.

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
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-4-teamlead-2026-08-20.md`. Plain technical-writer prose. Structure: persona recap; environment; doctrine-read log (claims checked, with verdicts); hands-on log (step → command → result, condensed for steps that matched their checkpoints); FINDINGS table (id, document:line, what failed, severity); TEAM-STORY assessment (what four-person adoption leaves undefined); adopt/don't-adopt recommendation with reasons; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (id — doc:line — one-sentence description — severity).
```

## What it returned

The persona returned `verdict: FINDINGS 18` with a 32,757-byte report. Its
first three findings, in its own summary lines, with the
document:line citations dropped and the tense shifted to past:

- F-1 — no step staged the config file after Step 6 edited it, so a literal
  walk ended at `VERIFY: FAIL — RED: judges`, measured — major.
- F-2 — Step 6's first branch wrote an absolute path into the committed config,
  producing the second tracked de-identification hit that Step 9 defines as an
  escape, measured — major.
- F-3 — the kit's own `.gitignore` named the per-machine settings overlay that
  would solve the multi-developer problem, and no document mentioned it; a
  teammate's clone got `UNSTARTABLE:` lines — major.

The four architecture-level majors from this walk are why the register's team
story, the unshipped-resume-wiring entry and the checkpoint-template entry
exist as open items rather than as fixes.
