# Prerequisites

Relocated from `README.md` in round 30, intact.

---

Four things, none of them installed by this kit.

- **git — required, and the deepest dependency.** The certification runner's
  `judges` gate reads `git status` over the judged paths; its startup assertion
  asks `git check-ignore` about every judged and certified path; the cert-green
  token names a commit and is checked against the history. Without git those
  gates cannot run at all. **No minimum version is derived here.** Every git
  behaviour the kit cites was **measured on git 2.54** — `QUICKSTART.md` Step 4
  and `EXISTING-PROJECT.md` say so at each citation. The commands used are
  `git status --porcelain`, `git check-ignore -z --stdin`, `git rev-parse`,
  `git log`, `git merge-base` and `git add -f`. No floor has been established
  for any of them, and a floor nobody measured would be a fabricated number.
- **Python 3.10 or newer.** Every executable in the kit is a Python script: the
  runner, the hooks, the linters, the adoption smoke, the status line.
  **Standard library only** — there is no `requirements.txt`, nothing to
  install, and no virtual environment to create. Debian and Ubuntu hosts ship
  `python3` with no `python` shim unless `python-is-python3` is installed;
  substitute `python3` in every command and nothing else changes.
- **A shell: `pwsh`, `bash`, or Git Bash.** QUICKSTART's command blocks run in
  all three except in a small number of marked places; QUICKSTART's own "Shell"
  section lists them, and `adoption_smoke.py` phase 9 machine-checks the claim
  for Step 4's block.
- **A harness that fires pre-tool hooks — for modules 02, 05 and 06 only.** The
  doctrine is tool-agnostic; the enforcement *wiring* is not. Modules 02
  (enforcement), 05 (statusboard) and 06 (sidequest) assume a harness that
  fires pre-tool hooks, lets a spawn declare a model, and pipes session JSON to
  a status-line command. The Claude Code harness fits that description and is
  what the reference build ran on. Under a different harness, keep the doctrine
  and rebuild the wiring — `docs/PORTABILITY.md` prices that. Modules 01, 03,
  04, 07 and 08 assume nothing about how agents are run.

**Optional, and only where a step already says so:** **pytest**, if your gate
line runs a Python test suite — the runner judges required output lines from
any stack and does not care which; and **GitHub Actions**, which is module 07's
shipped CI workflow and the only CI system the kit ships a file for. Neither is
needed to certify locally.
