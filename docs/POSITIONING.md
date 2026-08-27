# Positioning — what is different here, and who the neighbours are

**What is different here is conduct, not composition**. Every mechanism in this
kit has an older name, and `BLUEPRINT.md` §12 lists the ancestors. Several now
have live competitors, named in `COMPARISON.md` with the claims they make
redundant. The claim that survives that comparison is narrower and harder to
copy. This kit turns its own headline instrument on itself and publishes the
unflattering number with its denominators. That includes the rounds where the
number went **up**, at 50.0% and 42.9%, kept in and named. A prior-art audit
run on 2026-08-22 found no other artifact publishing a self-applied miss rate
that is allowed to rise. Treat that as the reason to read on, and the
composition as a convenience.

**The neighbours, named**. Orchestration frameworks are what this kit composes
with, not what it competes with. The nearer neighbours are the other
governance-layer projects. A prior-art audit on 2026-08-22 found three that a
reader will reach in one search.

**Chock** (`open-coder-ai/chock`, Apache-2.0) commits policy to the repository
and compiles it to pre-tool-use hooks, CI gates and an agent rules file. It
labels each emitted control *enforced*, *enforced-at-commit* or *advisory*.
That is this kit's Zone A/B honesty, shipped as compiler output rather than as
a writing rule. The difference is direction. Chock generates enforcement from
one policy. This kit asks whether the checks were ever proven, and ships the
forced-red requirement, the [escape rate](../GLOSSARY.md) and the judgment
ledger that Chock does not.

**Agentic OS** (`KbWen/agentic-os`) is a rules-and-check system over existing
git workflows across several agent harnesses. It is built on the same thesis:
no step counts as done without evidence. Its existence is convergent support
for the file-first argument in `docs/WHY-FILES.md` rather than a rebuttal of
it. It carries no self-applied published miss rate, and only partial analogues
of the forced-red and ledger disciplines. `COMPARISON.md` has the row-by-row.

**Microsoft's Agent Governance Toolkit**
(`microsoft/agent-governance-toolkit`) is a runtime control plane with an SRE
package: SLOs, error budgets, circuit breakers. It aims at the hostile agent
this kit explicitly declines to defend against (see `docs/SECURITY-SCOPE.md`).
It ships an `agt doctor` command. That is a name collision with this kit's
`kit_doctor.py`, disclosed here so nobody has to discover it, and the two tools
do different jobs. `COMPARISON.md` carries the full claim-by-claim table,
including the claims where an incumbent does the job better.
