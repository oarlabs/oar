# Walk 41 — LLM-persona adoption walk: the impatient skimmer (v0.1.4)

**Register entry:** 41 · **Ran:** 2026-09-15 · **Kit commit:** `e8b1a67`
(tag `v0.1.4`) · **Findings, per the register:** 7 (3 major, 4 minor) · done
state reached

A large language model was given the persona below and read only headings,
code blocks and checkpoint lines of `QUICKSTART.md`, against the tagged
public release. It was not a person. See [README.md](README.md) for what
that means for the evidence.

The walk reached the document's stated done state. Two of the lane's own
major-severity findings were reviewed and rejected below the materiality
bar: the done state was reached in both cases, and the cited steps are
thinking work or prose by nature and do not compress. `KNOWN-ISSUES.md`,
this entry, carries the finding count and which of MAINT5's items close
each one.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
## Common rules for every lane (restate these in full to any helper; spawn none)

Model tier: sonnet. Never request any other tier. Spawn no subagents.

Token estimate: 120,000 per lane, cited against the ONEPAGER2 lane (sonnet,
97,092 tokens, <HANDOFF-DIR>/ONEPAGER2-report-20260915.md). Stop and report at
240,000 tokens with whatever you have.

HALT authority: at any point, if continuing is meaningless (the kit will not
clone, the scratch environment is unusable, the documents are circular, an
instruction would destroy something you cannot restore, a fence would have to
be crossed), stop and return `verdict: HALT` with the reason.

Hard rules:
1. Work only under your lane directory `<LANE>`, given in your launch text.
2. Clone the kit read-only:
   `git clone --branch v0.1.4 --depth 1 https://github.com/oarlabs/oar.git <LANE>/kit`.
   Never modify, commit to, or write inside `<LANE>/kit`.
3. Create your scratch project under `<LANE>/project`. Do all adoption work
   there. `git commit` only inside `<LANE>/project`, and only where a document
   instructs it.
4. Never write outside `<LANE>`. Never touch `<PROTECTED-PATH>`, this
   program's own repositories, or any other repository on this machine.
   Never push anything anywhere.
5. Use no knowledge the documents did not give you. If you repair something the
   documents did not tell you how to repair, the repair is a finding, recorded
   with what you had to invent.
6. No coach. Ask nobody anything mid-walk. If you are stuck, the document is
   where you got stuck; record it and, if the walk can continue, continue.
7. Every finding cites document:line. Verbatim goes in as verbatim: the
   command as printed, the output as received, the checkpoint as stated beside
   what appeared. Every finding carries its cost (minutes, retries, or what you
   had to author).
8. In the report, write your lane directory as `<LANE>` and the kit clone as
   `<KIT>`. Write no other absolute path, drive letter, user folder, account
   handle or owner name anywhere in the report. Before you finish, search your
   report for either Windows drive prefix, the user-folder segment, and
   `<HANDLE>`; the count must be zero.

Handoff, mandatory:
1. Write your full report to `<LANE>/report.md`. Plain technical-writer prose:
   short declarative sentences, active voice, defined terms, no flourishes.
   Structure: persona recap; environment (OS, shell, python and git versions);
   expected outcome as declared in your persona, and whether it was reached;
   step-by-step log (document → command → result); FINDINGS table (id,
   document:line, what failed, cost, severity); how far you got; token count
   as you best know it; verdict.
2. Your final message contains only: the report path, its byte count, its
   SHA-256, the verdict (one of `DRY`, `FINDINGS <n>`, `HALT <reason>`), one
   line stating whether the declared expected outcome was reached, and a
   summary of at most 40 lines listing each finding as one line
   (id — doc:line — one sentence — severity).

### Persona 3 — the impatient skimmer (Windows, pwsh)

The walk-35 persona on v0.1.4. Read only headings, code blocks and checkpoint
lines. Do not read explanatory prose. Run what the code blocks say, in order,
and compare each checkpoint to what appears. When a code block fails, that is
a finding; record it, then read the nearest prose paragraph once, and only
then continue.

Expected outcome, declared: the done state, or a list of every point where the
code blocks alone were not enough, each cited.
```

## What it returned

The persona returned `verdict: FINDINGS 7` (3 major by the lane's own
grading, 4 minor). Its first three findings, in its own words, with the
document:line citations dropped:

- Step 1's checkpoint expected filled configuration values, but only the
  prose numbered list above it did the filling; the checkpoint itself never
  said so — minor.
- Step 3's only code block could not produce the oracle worksheet page on
  its own; reaching it needed two documents read together — major by the
  lane's grading; the round rejected this below the bar, since the step is
  declared thinking work that does not compress and the done state was
  still reached.
- Step 4.3's settings-template fill was prose only, with no code block and
  no pointer to the render tool that already covers it — minor.

The reports themselves stay private; the register carries every finding's
disposition and this round's closing items.
