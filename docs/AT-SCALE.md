# At scale, and where it breaks

The question a large organisation asks first is whether any of this survives
ten thousand repositories. The architecture's answer is that it does not scale
up; it scales out. **The rails are per-seam, not per-mass**. Everything here is
per-repository: plain files, local checks, local ledgers, nothing centralised.
That is git's own scaling model. A large organisation runs many instances of it
rather than one large one. `ONBOARD.md` and the module file contracts are what
make an instance stampable. The load-bearing numbers are scale-invariant by
construction. The [escape rate](../GLOSSARY.md) is a ratio with a published
denominator, the state words mean the same thing at any n, and `RATIO_CEILING`
is derived per project rather than set centrally.

The mechanisms are not novel at that scale. Organisations already run
file-based, check-based, ledger-based control programs globally. The internal
controls function under SOX, COSO or ISO is that shape. This kit asks for
nothing that machinery does not already ask for. It applies the discipline to
the record of AI-assisted work. That is an existence proof for the mechanisms
at organisational scale. It is not evidence about this kit, and no audit
function has consumed anything this kit produces.

**The floor**. Three places this breaks, stated before you find them.

1. **Judgment plurality**. One owner's rulings saturate. The kit is written
   throughout for one owner and one orchestrator seat. Multi-seat adoption is
   undecided rather than solved. `ROADMAP.md` under "In active design" and
   `KNOWN-ISSUES.md` under "Whose settings file?" carry the current state. At
   portfolio scale the same gap returns as a decision-rights hierarchy, which
   is organisational design and not something a kit ships.
2. **Certification composition across trust boundaries**. The runner certifies
   a tree. A large system is a graph of trees, and a green that depends on
   another repository's artifact re-imports the second-machine problem
   transitively. No attestation chain ships here, and the certification token
   is local and per-machine by design. The answer is composition with
   supply-chain attestation: signed provenance of the SLSA or sigstore class.
   The answer is not a second attestation system built inside this one.
3. **High agent concurrency genuinely requires an orchestration engine**. At
   hundreds of concurrent agents, with scheduling, retry and queueing
   semantics, you need one. This kit is not one and was never meant to be. The
   division is clean: the graph says what ran and in what order; the rails say
   whether the green was real. They meet at the record. Graph runs emit file
   evidence with red-capable checks, and the runner judges that evidence.
   **That composition is architecturally clean and empirically untested**. No
   measured instance of this kit running alongside an orchestration engine
   exists.

Project size by itself is not on that list. The kit decomposes rather than
grows. Its own context ceiling is answered by its own doctrine: a rule that
keeps costing context gets promoted to a mechanical check, which costs none.

None of this section is a measurement. The evidence base is one reference build
and one seat, with no deployment at organisational scale. Every claim above is
an argument about architecture rather than a result. `DECISION-BRIEF.md` states
what the evidence base does and does not support.
