# Why files, and what the bar actually is

Relocated from `README.md` in round 30, intact. Two sections: why the controls
are plain files, and what kind of process can run on these rails at all.

---

## Why files, and where this sits

The kit ships no orchestration graph, no tracing, no eval harness — a
decision, not a gap. Those tools run agents and score outputs. This kit does
a different job: proving that the checks a project trusts exist, ran, have
been seen red, and cannot be rewritten by the process they govern. The
controls are plain files because files are the one artifact the whole
toolchain can hold to account: git versions them and reports their
cleanliness, CI re-judges them on a machine no session touches, and a human
can read them. A graph definition held in a runtime is, under this kit's
threat model, a file the agent can edit — with fewer witnesses.

Running a framework? The layers compose. Keep LangGraph, CrewAI, or whatever
executes your agents; point `GATE_COMMAND` at whatever proves your project
works — the runner judges required output lines and floors from any stack,
and modules 01, 03, 04, 07 and 08 assume nothing about how agents are run.
Module 02's hooks are the one harness-specific layer, and
`docs/PORTABILITY.md` says exactly what porting them costs.

The neighbouring projects — Chock, Agentic OS, Microsoft's Agent Governance
Toolkit — are named with their claims in `docs/POSITIONING.md`, and
`COMPARISON.md` carries the row-by-row.

---

## Beyond code

The kit assumes nothing about code. It assumes a process whose record can live
in files under git, with checks that can be run and seen to fail — that is the
entire bar. A process that clears it can run on these rails; a process whose
record is a conversation, or whose checks have no red state, cannot, and
adopting the kit will not change that. Three places where the bar has actually
been cleared, all of them inside this program rather than imagined for it:

- **This kit's own program** — documentation and tooling, built under the full
  discipline, and the loop found real defects in rounds that shipped no code:
  `KNOWN-ISSUES.md` round 14 (eight documentation and cross-module-description
  findings) and round 19's prose-only build (three majors, all attribution from
  memory, one an invented quotation).
- **Control validation** — every control names its test and the test has been
  seen to fail, which is what `FAILURE-FLOOR.md` (rule → layer → last fired) and
  `JUDGMENT-LEDGER.md` (ruling → named check, or UNCHECKED) already record. No
  audit has consumed them; the claim is about the shape of the record, not about
  an engagement.
- **The operating collaboration itself** — session forks, owner rulings and the
  collaboration profile run as versioned, gated records in the program this kit
  came out of; what ships here is the machinery, in modules 06, 04 and 08.

**This is not a claim that the kit works for anything.** Where the record is
not files, or the checks cannot be seen red, the rails have nothing to hold.

A fourth place, added in round 30 and different in kind because it is outside
this program: the kit's Level 1 was adopted into an existing project nobody
here maintains, and one improvement was executed under its discipline.
`docs/CASE-STUDY-INCREMENT.md` is that account, including what it does not
establish.
