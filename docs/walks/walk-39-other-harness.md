# Walk 39 — LLM-persona adoption walk: the other harness (v0.1.4)

**Register entry:** 39 · **Ran:** 2026-09-15 · **Kit commit:** `e8b1a67`
(tag `v0.1.4`) · **Findings, per the register:** 0 (DRY) · expected outcome
reached

A large language model was given the persona below and read the kit's
front-door documents on a harness other than Claude Code, against the
tagged public release. It was not a person. See [README.md](README.md) for
what that means for the evidence.

The persona's declared outcome was reached: the front door named
`docs/PORTABILITY.md` before `QUICKSTART.md` Step 4, Steps 0 to 3 completed
unchanged, and the walk stopped at Step 4 with `docs/PORTABILITY.md` in
hand, as declared. `docs/ADOPTION-TESTS.md` records this as the walk that
measured the previously unmeasured claim.

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

### Persona 1 — the other harness (Windows, pwsh, literalist)

You are a developer who has never seen this kit. Your team's agents do not run
under Claude Code; they run under a different agent harness that has no
pre-tool hooks and no status-line command. You work on Windows in pwsh. You
obey the documents literally, every command as printed, in the printed order.
Start at the kit's README and follow the reading order it gives you.

Expected outcome, declared: the front-door documents tell you, before Step 4
of QUICKSTART, that modules 02, 05 and 06 are wired for Claude Code and that
you should read `docs/PORTABILITY.md`; Steps 0 to 3 complete unchanged; you
stop at Step 4 with PORTABILITY in hand and know what would need rewiring.
Record where you first learned this, by document:line, and whether any
document contradicted another about what you should do.
```

## What it returned

The persona returned `verdict: DRY`. Zero findings; the expected outcome was
reached as declared. One observation the lane classed as friction rather
than a finding: README's "socket" wording for module 05 read as tension
against `docs/PORTABILITY.md`'s "doctrine/wiring" split on first pass, and
resolved on a closer read. The register carries this as W1-0, RECORDED with
no change.

The reports themselves stay private; the register carries every finding's
disposition and this round's closing items.
