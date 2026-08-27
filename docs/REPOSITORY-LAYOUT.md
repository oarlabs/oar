# Repository layout

Relocated from `README.md` in round 30, intact, with the round-30 relocations
added at the end.

---

```
oar/
  README.md              the front door (this page describes the layout it sits in)
  ONBOARD.md             the agent-facing front door: sequencing and division of
                           labour over the documents below, for an AI agent
                           adopting the kit into a project. Executes nothing
  DECISION-BRIEF.md      one page for a decider: what certifies, what it costs,
                           what is not shipped, exit cost, the honest caveats
  COMPARISON.md          every load-bearing claim classified against named live
                           artifacts - redundant, partially overlapping, or
                           unmatched - with each source's verification tier
  LEVEL-1.md             the documents-only entry: 30-45 minutes, reversible,
                           ending in `kit_doctor.py --level1`
  QUICKSTART.md          the first session, ordered, testable at every step
  EXISTING-PROJECT.md    read beside QUICKSTART on a repository that already
                           exists: one row per measured collision, with the
                           workaround proven for it
  BLUEPRINT.md           the doctrine (authored separately)
  CONTEXT-ARCHITECTURE.md   the full treatment of BLUEPRINT §7: memory, state,
                             and the window — layers, boundaries, wiring
  kit.config.example     every slot in one file
  kit.config             the kit's OWN config - committed, repo-relative
  kit.config.local.example   the gitignored overlay: absolute + protected values
  .claude/settings.json  the kit's own harness wiring (a worked example)
  deident.tokens         empty by design - see tools/deident_scan.py
  tools/deident_scan.py  scan any tree for tokens that must not be published
  tools/adoption_smoke.py    a gate on the kit's adoption path: scaffolds a
                             throwaway repo, performs QUICKSTART mechanically,
                             asserts the result, and can replant a known
                             defect to prove it still detects it
  tools/kit_render.py    OPTIONAL. Substitutes the seven files QUICKSTART has
                             you fill in, from a kit checkout into your repo.
                             Writes only <name>.kit-new; by hand stays the
                             documented path
  tools/statusline.py    the portable status board (module 05's contract)
  tools/kit_doctor.py    "check my adoption" — twelve diagnostic checks over
                             YOUR tree: judged paths that exist, are not hidden
                             by an ignore rule and agree with the hook's config;
                             gates that cannot fail; what a blanket commit
                             would sweep up; whether the hook's interpreter
                             starts; what the tripwire and the cert token are
                             and are not; whether any failure-floor rule is
                             overdue for a demotion disposition; and how big
                             the text every session must read has grown.
                             `--level1` runs seven different ones instead, for
                             a documents-only adoption: the documents are
                             present, rendered, committed, carry the two
                             decisions that level asks for, and neither the
                             config nor the ledger names collide with what an
                             existing repository already had.
                             Verdict is HEALTHY / ATTENTION, never
                             PASS — it diagnoses, it does not certify, and it
                             stages nothing
  tools/count_lint.py    is the stated number the number, and is the universal
                             claim true of every element? Two layers, one
                             summary line with a denominator and a state word
  tools/citation_lint.py is the quoted string in the document it names, and at
                             the lines it names?
  tools/skim_lint.py     is each of the three practitioner artifacts reachable
                             from inside the front door's first screen? The
                             window is a defended number in the source, not a
                             flag on the command line
  tools/repeat_lint.py   is this universal claim stated in more than one
                             document, so that correcting one copy leaves the
                             others standing? The threshold is a defended
                             number in the source and its derivation prints on
                             every run
  tools/expectation_lint.py  fails when a check reads its expectation from
                             the artifact it is asserting about, and fails when
                             a registry row carries no seen-red field
  checks-registry.json   every check's subject and expectation source, with
                         each surviving self-reference waived explicitly, and
                         a seen-red field per check holding the date of its
                         last recorded forced red or the honest value NEVER
  .github/workflows/kit-ci.yml   the core, on Linux and Windows, every push
  KNOWN-ISSUES.md        what the LLM-persona adoption walks found, and its
                           state. Opens with the escape table
  docs/walks/            the published walk and evaluation-read prompts (its
                           README states exactly which runs are covered), plus
                           WALKING-YOUR-OWN-DOCUMENTS.md: the method, written
                           for your documentation rather than the kit's
  docs/*.md              the long-form material the front door routes to:
                           positioning, why-files, at-scale, prerequisites,
                           security scope, portability, adoption tests,
                           adoption levels, start-here, this layout, and the
                           increment case study
  ROADMAP.md             ready now, in design, planned, and not shipped
  VERSION                the release stamp tools/kit_doctor.py reads
  LICENSE                Apache-2.0
  modules/01..08/        each with a README stating its file contract
```
