# Glossary

Terms this kit uses with a specific meaning. Docs link here at first use.
[check: tools/prose_floor.py — jargon terms require a link to this file]

- **andon**: the stop authority. Any agent, at any depth, may halt a run
  by returning a HALT verdict with a reason. Named for the factory cord any
  worker can pull.
- **brownfield**: an existing codebase with history, as opposed to a fresh
  (greenfield) repository.
- **cert-green**: a token the coordinator writes only when a full
  certification run passes. While the certified tree is unchanged, the
  token pre-authorizes writes that would otherwise prompt the owner. Any
  newer relevant commit voids it.
- **escape rate**: the share of findings in a round that an existing check
  should have caught. The kit's headline honesty metric; computed, not
  asserted.
- **judge surface**: the set of files a certification runner reads to
  decide its verdict; each such file is a judged path. A green run over a modified judge surface certifies
  nothing.
- **lane**: one delegated agent doing one bounded piece of work
  (implement, review, scout, write) under a written charter.
- **negative control**: a deliberate defect planted to prove a check can
  fail. A check never seen red is an unproven check.
- **oracle**: this kit's use of the testing term — an executable check
  that captures a human ruling, so the ruling never has to be re-asked.
  Oracle manufacture is turning a closed finding into such a check.
- **punch item**: one concrete finding from a review or a hands-on drive,
  tracked until it gets an explicit disposition (fixed, filed, rejected).
- **section anchor**: a citation that names a heading in the target rather
  than a line number. Two forms: the backticked filename followed by *§6*,
  or by the heading's own words in double quotes. `tools/citation_lint.py`
  resolves both against the target's headings. Prefer one to a line
  locator, which goes stale on any edit above it.
- **seen_red**: a per-check field: the date the check was last recorded
  refusing, or NEVER. An absent field is a failure; NEVER is an honest
  value.
- **charter**: the written brief a lane runs under: scope, constraints,
  HALT authority, and what it returns.
- **dead-man clause**: a fixture that fails when the enforcement layer it
  guards stops running, so a silently disabled hook cannot look green.
- **escape table** (also called **the register**): the table in
  `KNOWN-ISSUES.md` holding the kit's per-round miss rate with
  denominators. One file, one table; the judgment ledger (module 04) is a
  different file.
- **harness**: the agent-hosting environment (the CLI, its permission
  system, its hooks) that the kit's wiring runs inside.
- **INSTRUMENTED / ABORTED**: the two meanings of exit 2 from the
  certification runner: INSTRUMENTED means a planted defect was caught (a
  control worked); ABORTED means the run could not judge at all. Opposite
  kinds of news; read the word, not the code.
- **round**: one bounded unit of kit work: implement, spec-side review,
  fix pass, gates, commit.
- **slot**: a `{{PLACEHOLDER}}` in a shipped template that the adopter
  fills; the render tool names every slot it leaves unfilled.
- **spec-side**: how reviewers onboard: from the specification, rulings,
  and diff. Never from the implementer's report.
- **state word**: the one word a check prints for its own coverage: CLEAN,
  PARTIAL, FAIL, INSTRUMENTED. "Did not run" and "passed" must never
  render alike.
- **tier** (model tiering): the model class a spawned agent is declared to
  run on; the orchestrator orchestrates, lanes run on the lane tier,
  sweeps on a cheaper one. Omitting the tier silently inherits the most
  expensive seat.
- **zone**: who can rewrite a rule's enforcer. Zone A: outside the agents'
  blast radius (a human at a gate, protections the agents cannot write).
  Zone B: inside it. A Zone B rule is real but honest about its custody.
  [record: modules/04-ledgers/FAILURE-FLOOR.md]
