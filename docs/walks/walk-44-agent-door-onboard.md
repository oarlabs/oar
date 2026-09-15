# Walk 44 — LLM-persona adoption walk: the agent door, ONBOARD.md (v0.1.4)

**Register entry:** 44 · **Ran:** 2026-09-15 · **Kit commit:** `e8b1a67`
(tag `v0.1.4`) · **Findings, per the register:** 3 (0 major, 2 minor, 1
nit) · done state reached, one routing-gap qualification

A large language model was given the persona below and entered the kit
through `ONBOARD.md` alone, adopting a scratch host — an empty git
repository with one commit — against the tagged public release. It was not
a person. See [README.md](README.md) for what that means for the evidence.

The walk reached Level 1's done state, with one routing gap: `ONBOARD.md`'s
tier-name cases did not cover a genuinely empty host. `KNOWN-ISSUES.md`,
this entry, carries the finding count and which of MAINT5's items close
each one.

## The prompt, verbatim

Redacted per the conventions in [README.md](README.md). No other text was
changed.

```
## Common rules for every lane (restate these in full to any helper; spawn none)

Model tier: sonnet. Never request any other tier. Spawn no subagents.

Token estimate: 120,000 per lane, cited against the ONEPAGER2 lane (sonnet,
97,092 tokens, librarian/ONEPAGER2-report-20260915.md). Stop and report at
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
   report for `C:/`, `C:\`, `Users`, and `guyot`; the count must be zero.

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

### Persona 6 — the agent door (ONBOARD.md)

You are an AI agent told to adopt this kit into a host project. Your entry
point is `ONBOARD.md` and nothing else; obey its sequencing and its division
of labour. The host is a scratch project you create first under
`<LANE>/project`: an empty git repository with one commit. The owner cannot
answer this session. Do every step ONBOARD assigns to you and none it assigns
to the owner. Produce the handoff ONBOARD requires, in the shape it requires,
inside `<LANE>/project` or `<LANE>` as it directs.

Expected outcome, declared: ONBOARD's own handoff report with its punch list,
every owner decision recorded as deferred rather than taken, and a record of
every place where ONBOARD and a shipped document disagreed, cited.
```

## What it returned

The persona returned `verdict: FINDINGS 3` (0 major, 2 minor, 1 nit). Its
findings, in its own words, with the document:line citations dropped:

- `ONBOARD.md`'s three tier-name cases — no agents, agents with tiers
  evidenced, an AI-assistant host with no agent vocabulary — did not cover
  a genuinely empty host with nothing yet to read vocabulary from — minor.
- The printed Level 1 commit line fails literally when `CLAUDE.md` was not
  taken: exit 128, nothing staged, with no line telling the agent to drop
  it — minor.
- `ONBOARD.md` called the first `FAILURE-FLOOR.md` row "mechanical" without
  saying what the row should hold — nit.

The reports themselves stay private; the register carries every finding's
disposition and this round's closing items.
