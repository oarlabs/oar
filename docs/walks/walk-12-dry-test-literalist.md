# Walk 12 — LLM-persona adoption walk: the dry-test literalist

**Register entry:** 12 · **Ran:** 2026-08-20 · **Kit commit:** `b50e1d6` ·
**Findings, per the register:** 6 (1 major, 2 minor, 3 nit) · **All 6 fixed**

A large language model ran the persona below: a careful literalist re-walking
the full document after the errata from walks 8–11, verifying every checkpoint
and auditing the end state against the kit's stated intent. It was not a
person. See [README.md](README.md) for what that means for the evidence.

This was the first **dry test** — a walk run to find out whether the loop had
converged rather than to break new ground. It reached the documented done
state, confirmed the prior fixes it crossed, verified the live hook with its own
configured tier values, and still found six new defects, all in the class the
register keeps recording: a committed artifact or a load-bearing rule that no
checkpoint reaches. The loop was therefore **not dry** at this walk, and the
register says so.

Its major finding was that Step 8 was the one template step whose committed
artifact no checkpoint reached, while every sibling step had one — so an
adopter could commit an unrendered slot and a template header inside the
artifact the kit calls its highest-value one, and nothing in the kit would
notice.

`KNOWN-ISSUES.md`, "Walk #12", carries every finding and its disposition. The
fix pass is commit `404da28`.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
You are a developer who has never seen this kit. You are onboarding an "orchestration kit" into a scratch project of your own, using only the kit's shipped documents. You have no other context about the kit, its authors, or its history — do not use knowledge the documents did not give you.

PERSONA: You are a careful Windows developer working in PowerShell (pwsh). You read each step fully before executing it, then execute every command exactly as printed, in the printed order. You verify every checkpoint the document states, including the runnable checkpoint lines. When a command fails as printed, that is a finding; record it, then apply the obvious repair and continue. You also verify the document's own claims about what state you are in ("you now have X") against your actual tree.

THE KIT: `<KIT>` (a git repo; the thing you downloaded). READ-ONLY — never modify, commit to, or write inside that directory. Set PYTHONDONTWRITEBYTECODE=1 for commands you run inside it.

YOUR SCRATCH PROJECT: create it at `<SCRATCH>\stranger5-project`. Do all adoption work there.

METHOD:
1. Start with the kit's README. Obey the reading order it gives you for an adopter. Work through QUICKSTART start to finish, every step, both reading and executing.
2. Report every point where a document fails you: a command that does not run as printed; a step unreachable where the document places it; a checkpoint that does not match your observed output; a term used before it is defined; a decision you could not make from the text alone; a claim about your resulting state that your tree contradicts. Cite document file and line (or exact quoted text), never a vibe.
3. Target: the documents' own "done" state, verified — including any final certification run the document prints.
4. At the end, audit your own tree against the kit's stated intent: anything broken or degraded at "done" that no checkpoint caught is a finding.

HALT AUTHORITY: if you hit something that makes continuing meaningless, stop and return verdict HALT with the reason.

HARD RULES: never run `git commit` anywhere except inside your own scratch project where a document instructs it; never touch `<PROTECTED-PATH>`; never write under `<PROGRAM-REPO>\docs\`; do not spawn subagents.

HANDOFF (mandatory format):
1. Write your FULL report to `<HANDOFF-DIR>\kit-stranger-5-drytest-2026-08-20.md`. Plain technical-writer prose. Structure: persona recap; environment; step-by-step log (condensed where a step matched its checkpoint exactly — one line per matched step); FINDINGS table (id, document:line, what failed, severity major/minor/nit); end-state audit; verdict.
2. Compute the file's byte count and SHA-256.
3. Your final message must contain ONLY: the file path, byte count, sha256, verdict (one of: DRY = zero findings, FINDINGS <n>, HALT + reason), and a summary of at most 40 lines listing each finding as one line (or "no findings" if DRY).
```

## What it returned

The persona returned `verdict: FINDINGS 6` with a 17,962-byte report. Its first
two findings, in its own summary lines, with the
document:line citations dropped and the tense shifted to past:

- F1 — Step 1 and Step 7 gave opposite rules for shipped placeholder values
  left in the committed config; nine such values survive at the document's own
  done state, and one of them is required to stay by an earlier step — minor.
- F2 — Step 6 promised that Step 8 "spells out what it means for that one
  file"; Step 8 never did, so an adopter who filled the profile template in
  place committed an unrendered slot and a template header, and no later
  checkpoint reached the file — major.
