# Start here — the doors, by who you are

Relocated from `README.md` in round 30, intact. The front door keeps a short
routed index; this is the full routing, with the budgets.

---

**An AI agent, dropped into a project and asked to adopt the kit?** Read
**`ONBOARD.md`**. It is the agent-facing front door: it sequences the documents
below, says which half of an adoption an agent may perform and which half is the
owner's to decide, and requires the second half to be handed back as an explicit
punch list rather than answered on the owner's behalf. It installs nothing and
executes nothing itself — every command it names is one of the documents' own.
The doors below are the human ones and are unchanged.

**Deciding whether to adopt at all?** Read **`DECISION-BRIEF.md`** first — one
page: what the kit is and is not, what certifies at each level, what it costs,
what is not shipped, the exit cost, and the limitations most likely to matter
to you. Three minutes.

**Already running something in this space, or about to search for one?** Read
**`COMPARISON.md`**. It classifies every load-bearing claim this kit makes as
redundant, partially overlapping or unmatched against named live artifacts,
with each source carrying its verification tier, and it names the one component
where an incumbent does the job better. `BLUEPRINT.md` §12 does the same
exercise against ancestors rather than competitors.

**Adopting the documents first?** **`LEVEL-1.md`** is the 30–45 minute
entry: four ledgers, a collaboration profile, the standing rules as prose, no
settings file, no hook, and a check that reads what you installed and states
what it does and does not certify. It installs no code into your repository and
it is reversible.

Adopting the whole thing: read **`QUICKSTART.md`** and work through it in
order. Every step ends in output you can run and see; if a step produces no
visible output, it is not finished.

**Adopting into a repository that already exists?** Read
**`EXISTING-PROJECT.md`** alongside it. `QUICKSTART.md` is written for a
repository whose only uncommitted content is the kit's own, and that page is
the measured list of where an existing project departs from that assumption —
an existing `CLAUDE.md` or `.claude/settings.json`, an ignore rule over
`.claude/`, work in progress inside the certified paths, a test suite you
already trust, CI that ends up proving less than the local gate — each with the
behaviour that was measured and the workaround that was proven.

Budget for that walk:

- **90 minutes to two hours** of hands-on work (Step 4, the certification
  runner and its wiring, is 45–60 minutes of that on a first adoption),
- **an afternoon** for your first oracle (Step 3 is design work and does not
  compress),
- **the seed interview** (Step 8): fifteen minutes done the same day if you
  are the project's owner; a scheduled slot on the owner's calendar if that
  is someone else.

Those figures are a sum of per-step estimates, reconciled against walks
performed by LLM personas rather than by people. No human has walked this
document end to end. `docs/walks/` publishes the prompts behind every one of
those walks and states what they do and do not establish.

> **Debian/Ubuntu:** the `python3` substitution rule is in
> `docs/PREREQUISITES.md`.

**Evaluating in depth?** After the brief, read **`BLUEPRINT.md`** for the
doctrine the mechanisms come from, then **`CONTEXT-ARCHITECTURE.md`** for the
full treatment of BLUEPRINT §7 — memory, state and the context window: which
layers hold what, where the boundaries fall, and how the pieces wire together.
Neither is needed to work through `QUICKSTART.md`; both are worth reading
before you decide how much of the kit your project should take.
`KNOWN-ISSUES.md` says what the kit's adoption tests found and what state each
finding is in — every one of them run by an LLM persona, with the prompts
published under `docs/walks/`.
