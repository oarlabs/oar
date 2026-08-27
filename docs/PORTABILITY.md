# Portability

**The doctrine is tool-agnostic. The enforcement wiring is not.**

- **Doctrine** covers the [oracle](../GLOSSARY.md)-manufacturing loop, the
  enforcement zones, the ledgers, the charter anatomy, the collaboration
  contract, and the exit-code contract. It describes how work gets proven
  correct. It transfers to any stack and any model, including projects with no
  AI at all.

  **Team adoption is the part that is not documented**. The kit is written
  throughout for one owner and one orchestrator seat, and the mechanics assume
  it. They assume one committed `.claude/settings.json` carrying one machine's
  absolute paths, one `collaboration-profile.md`, one `RATIO_CEILING`, one
  `OWNER_ROLE`, and a per-machine [cert-green](../GLOSSARY.md) token. None of
  that is wrong
  for a team. It is simply undecided, and a team has to decide it on day one.
  `KNOWN-ISSUES.md` records what that costs and what shape the answers might
  take, under "Whose settings file? — the team story".
- **Wiring** covers the PreToolUse hook, the settings file, the status line,
  and the skill format. It assumes a harness that fires pre-tool hooks, lets a
  spawn declare a model, and pipes session JSON to a status-line command. The
  Claude Code harness fits that description and is what the reference build ran
  on.

Under a different harness:

- **Modules 01, 03, 04, 07, and 08 port as-is**. They are documents and a
  Python runner. None of them asks the harness for anything.
- **Module 02**: the decisions port unchanged. The plumbing to translate is two
  functions: `out()`, which emits the decision object your harness expects, and
  the parse inside `judge()` that reads it back.
- **Module 05** ships a portable Python board (`tools/statusline.py`) alongside
  the pwsh one, so it needs no translation.
- **Module 06**: the checklist content is harness-neutral and works as prose in
  any project. The format is not. `SKILL.md` with YAML frontmatter is a Claude
  Code skill file. Elsewhere, paste the body into your standing rules under
  "when interrupted".

**Host coverage is machine-checked**. Every executable is stock Python with no
dependencies. `.github/workflows/kit-ci.yml` runs the whole core on
**ubuntu-latest and windows-latest** on every push. The core is the scanner
selftest, the status-board selftest, the verify selftest, the hook fixtures,
the dead-man case, the adoption smoke and its
[negative control](../GLOSSARY.md), and the kit's own certification. The one
Windows-only file is `statusline.ps1.template`, an
optional variant of a component the Python board already covers.

**Shell**. QUICKSTART's command blocks run in `pwsh`, `bash`, and Git Bash
except in a small number of marked places. QUICKSTART's own "Shell" section is
the authority and lists them all. That claim is machine-checked.
`adoption_smoke.py` phase 9 runs Step 4's block through `pwsh` where pwsh
exists, and reports plainly where it does not.

**Evidence caveat**. This is a field-tested playbook from a small number of
builds, not a proven project-agnostic template. Portability is demonstrated
when a second stack ships with it. Until then: adapt skeptically, delete
freely, and keep what proves useful.

Round 30 added one data point, and it is a partial one. The kit's Level 1 was
adopted into an existing Python project outside this program, and one
improvement was executed under its discipline.
`docs/CASE-STUDY-INCREMENT.md` states what that establishes and what it does
not: one repository, one language, one afternoon, and an adopter that was a
language model rather than a person.
