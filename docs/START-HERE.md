# Start here — the doors, by who you are

`README.md` keeps a short routed index. This is the full routing, with the
budgets.

---

**An AI agent, dropped into a project and asked to adopt the kit?** Read
**`ONBOARD.md`**. It is the agent-facing front door. It sequences the documents
below. It says which half of an adoption an agent may perform, and which half
is the owner's to decide. The owner's half is handed back as an explicit punch
list, never answered on the owner's behalf. `ONBOARD.md` installs nothing and
executes nothing itself. Every command it names belongs to one of the documents
below. The doors below are the human ones and are unchanged.

**Deciding whether to adopt at all?** Read **`DECISION-BRIEF.md`** first. One
page, three minutes. It covers what the kit is and is not, what certifies at
each level, and what it costs. It also covers what is not shipped, the exit
cost, and the limitations most likely to matter to you.

**Already running something in this space, or about to search for one?** Read
**`COMPARISON.md`**. It classifies every load-bearing claim this kit makes as
redundant, partially overlapping, or unmatched against named live artifacts.
Each source carries its verification tier. It also names the one component
where an incumbent does the job better. `BLUEPRINT.md` §12 runs the same
exercise against ancestors rather than competitors.

**Adopting the documents first?** **`LEVEL-1.md`** is the 30–45 minute entry:
four ledgers, a collaboration profile, the standing rules as prose, no settings
file, no hook. It ends in a check that reads what you installed and states what
it does and does not certify. It installs no code into your repository, and it
is reversible.

**Adopting the whole thing?** Read **`QUICKSTART.md`** and work through it in
order. Every step ends in output you can run and see. A step that produces no
visible output is not finished.

**Adopting into a repository that already exists?** Read
**`EXISTING-PROJECT.md`** alongside it. `QUICKSTART.md` is written for a
repository whose only uncommitted content is the kit's own.
`EXISTING-PROJECT.md` is the measured list of where an existing project departs
from that assumption. The departures it covers are an existing `CLAUDE.md` or
`.claude/settings.json`, an ignore rule over `.claude/`, and work in progress
inside the certified paths. It also covers a test suite you already trust, and
CI that ends up proving less than the local gate. Each entry carries the behaviour that was measured and the workaround
that was proven.

Budget for that walk:

- **90 minutes to two hours** of hands-on work. Step 4, the certification
  runner and its wiring, is 45–60 minutes of that on a first adoption.
- **An afternoon** for your first [oracle](../GLOSSARY.md). Step 3 is design
  work and does not compress.
- **The seed interview** (Step 8). Fifteen minutes done the same day if you are
  the project's owner. A scheduled slot on the owner's calendar if that is
  someone else.

Those figures are a sum of per-step estimates, reconciled against walks
performed by LLM personas rather than by people. No human has walked this
document end to end. `docs/walks/` publishes the prompts behind the seven
adoption walks those figures were reconciled against, and states what they do
and do not establish.

> **Debian/Ubuntu:** the `python3` substitution rule is in
> `docs/PREREQUISITES.md`.

**Evaluating in depth?** After the brief, read **`BLUEPRINT.md`** for the
doctrine the mechanisms come from. Then read **`CONTEXT-ARCHITECTURE.md`** for
the full treatment of BLUEPRINT §7: memory, state, and the context window. It
covers which layers hold what, where the boundaries fall, and how the pieces
wire together. Neither document is needed to work through `QUICKSTART.md`.
Both are worth reading before you decide how much of the kit your project
should take.

`KNOWN-ISSUES.md` says what the kit's adoption tests found, and what state each
finding is in. LLM personas ran those tests. The exception is entry 29, a read
by a practising engineer outside the program. `docs/walks/` publishes the
prompts for the entries its own first table names, and states which entries
have no prompt to publish. `tools/repeat_lint.py` checks that a claim
corrected in one document does not survive restated in another.
