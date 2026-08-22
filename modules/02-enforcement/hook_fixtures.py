#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hook_fixtures.py - the gate, judged. Runnable on day one, before you have a
single project-specific check of your own.

    python hook_fixtures.py                      # run every fixture
    python hook_fixtures.py --hook <path>        # judge a DIFFERENT hook file
    python hook_fixtures.py --armed <settings>   # also assert the hook is WIRED
    python hook_fixtures.py --strict             # a skipped fixture is a failure
    python hook_fixtures.py --selftest           # judge THIS harness's own layer
    python hook_fixtures.py --make-deadman <dir> # mint a corpse hook, then exit

    exit 0  every fixture that ran reached an accepted verdict
    exit 1  at least one fixture failed
    exit 2  abort (the hook file is missing, bad usage)

WHY A HOOK NEEDS FIXTURES
=========================
A hook is the only code in a project that runs with the authority to stop
everything and is never itself exercised by the work. Nothing calls it in
development. Nothing fails when it breaks. It can be syntactically dead for
weeks, in a repository where every test is green, and the only symptom is that
things you believed were impossible quietly start happening.

TWO CLAIMS, AND THE FIRST ONE IS THE ONE PEOPLE MISS
====================================================
  1. IS IT ARMED? The fixtures below prove what the hook DECIDES. They say
     nothing about whether the harness ever CALLS it. A settings file whose
     matchers were deleted or rewired leaves every fixture green and every rule
     unenforced - the exact shape of a gate that has silently stopped guarding.
     `--armed <settings.json>` parses the settings (read-only) and asserts the
     hook is referenced at the enforcement points it needs.
  2. WHAT DOES IT DECIDE? Synthesised payloads, judged against the verdicts the
     hook's own branches document.

THE DEAD-MAN CLAUSE
===================
A hook that dies without speaking must read as FAILURE, never as "allowed".

  * A fixture whose accepted verdict is a DECISION passes on that decision being
    DELIVERED, whatever the process wrote to stderr. A hook that prints a
    deprecation warning and then correctly denies has guarded; failing it would
    be a false red, and false reds are how a suite gets ignored.
  * A fixture whose accepted verdict is SILENCE passes only if the process also
    exited 0. **Silence from a corpse is not consent.**

Prove it on your own machine before you trust any of this:

    python hook_fixtures.py --make-deadman <scratch-dir>
    python hook_fixtures.py --hook <scratch-dir>/hook_model_gate.py  # must go RED

(any writable scratch directory: /tmp/dead on Unix, %TEMP%/dead on Windows -
--make-deadman creates it. Forward slashes work in both places.)

CONDITIONAL FIXTURES ARE REPORTED, NEVER ABSORBED
=================================================
Some fixtures only mean something once `kit.config` configures the feature they
test (exempt agent types, the forbidden tier, the protected-path tripwire).
There are THREE outcomes for those, and the distinction is load-bearing:

    PASS/FAIL   the fixture ran and was judged
    SKIP        we could not tell whether the feature is wanted, or it is
                half-configured. A real gap. `--strict` fails on it.
    n/a         the feature is switched OFF ON PURPOSE. There is no untested
                surface behind it, so it is not a gap - it is reported, counted
                and printed, but it does not fail --strict.

Collapsing `n/a` into `SKIP` produced a documented contradiction: this kit's
QUICKSTART said "leave the tripwire off" in Step 1 and demanded "0 skipped" in
Step 6, so a reader who followed it in order could never reach a clean run -
and the kit's own config shipped with the tripwire ON so that its own smoke
never walked its own advice. Three states, three meanings.

WHICH CONFIG, AND THE WARNING WHEN THERE IS NONE
================================================
Search order, identical to the hook's:

    1. $KIT_CONFIG
    2. ./kit.config                  (current working directory)
    3. <this file's dir>/kit.config
    4. the nearest kit.config walking UP from this file's directory

...then `kit.config.local` from the same directory is overlaid on top
(committed file = repo-relative values; gitignored `.local` = absolute paths
and the protected location).

A run with NO config is not a run with sensible defaults - the config-driven
rules are ABSENT, and four fixtures downgrade to SKIP. A column of greens and
four skips reads as success, so this harness prints `CONFIG WARNING:` lines and
`--strict` fails on them. The verify runner's `hooks` gate vetoes on that same
string, which is how a mis-placed config becomes a red certification instead of
a quiet one.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_HOOK = HERE / "hook_model_gate.py"

VALID = {"deny", "allow", "ask", "silent"}

DEADMAN_SOURCE = '''\
# A CORPSE. Minted by hook_fixtures.py --make-deadman to prove the dead-man
# clause fires. It reads its stdin, says nothing, and dies non-zero - exactly
# what a hook with a syntax error or a missing import looks like from outside.
import sys
sys.stdin.read()
sys.stderr.write("simulated hook crash\\n")
sys.exit(9)
'''


# --------------------------------------------------------------------------
# config (only to decide which conditional fixtures are meaningful)
# --------------------------------------------------------------------------
def _read_pairs(path: Path, into: dict) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            k, v = line.split("=", 1)
            into[k.strip()] = v.strip()


def load_config():
    """(config, source-or-None, other-kit.configs-that-exist).

    The search order is the hook's, verbatim - $KIT_CONFIG, ./kit.config,
    <this dir>/kit.config, then the nearest kit.config walking UP - followed
    by a `kit.config.local` overlay from the same directory. It is duplicated
    here rather than imported because this harness must be able to judge a
    hook it does not share a directory with (that is what --hook is for).

    The third return value is what makes the silent failure LOUD. If we loaded
    nothing but a kit.config exists up-tree, this run is about to test a gate
    whose config-driven rules do not exist - and without the warning it prints
    eleven greens and four skips and looks like success."""
    env = os.environ.get("KIT_CONFIG")
    cands = ([Path(env)] if env else []) + [
        Path.cwd() / "kit.config",
        HERE / "kit.config",
    ] + [d / "kit.config" for d in HERE.parents]
    # M-6: FOUR sources, identical to the hook's. This harness used to add a
    # fifth (walking up from the cwd), which meant it could load a config the
    # gate it is testing would never see - a harness whose environment differs
    # from the thing it certifies is measuring a different program.
    existing: list[Path] = []
    for c in cands:
        try:
            if not c.is_file():
                continue
            r = c.resolve()
            if r not in existing:
                existing.append(r)
        except OSError:
            continue
    if not existing:
        return {}, None, []
    src = existing[0]
    cfg: dict = {}
    _read_pairs(src, cfg)
    _read_pairs(src.with_name("kit.config.local"), cfg)
    return cfg, src, existing[1:]


CFG, CFG_SOURCE, CFG_OTHERS = load_config()


# ---- THE SHARED UNSET RULE (one definition, three readers) --------------
# A value is UNSET when it is missing, empty, a NONE-family word, OR
# PLACEHOLDER-SHAPED. The last clause is the one that was missing, and it cost
# a ship-blocker: the kit ships 14 illustrative values, and every one of them
# is a perfectly ordinary non-empty string. `FORBIDDEN_SPAWN_TIER =
# your-top-tier-model` reads as a configured rule and guards a tier nobody will
# ever request, so the rule LOOKS enforced and is not.
#
# "It is set to the example value" and "it is set" must not be the same state.
PLACEHOLDER_WORDS = {"", "none", "null", "todo", "<unset>", "tbd", "changeme"}
PLACEHOLDER_SHAPES = (
    "your-",                # your-top-tier-model, your-runtime, your-lane-...
    "/abs/path",            # /abs/path/to/your/repo
    "c:/abs/path",
    "<",                    # <paste the checksum from ...>
    "derive-from",          # derive-from-your-own-data
    "https://example.invalid",
    "/path/to/",
    "example.invalid",
)


def is_placeholder(value: str) -> bool:
    """Pure, and shared verbatim by the hook, the fixture harness and the
    board. Three readers disagreeing about what "configured" means is how a
    gate comes to be judged by a harness looking at a different program."""
    v = (value or "").strip()
    if v.lower() in PLACEHOLDER_WORDS:
        return True
    low = v.lower()
    return any(low.startswith(p) or low == p.rstrip("/")
               for p in PLACEHOLDER_SHAPES)


def cfg_get(key):
    """A configured value, or None. **NONE and empty mean UNSET** - the same
    rule the hook uses, because a harness that disagrees with the gate about
    what "configured" means cannot judge it. `PROTECTED_PATH = NONE` is the
    absence of a path, not a path named NONE."""
    v = CFG.get(key)
    if v is None:
        return None
    v = v.strip()
    return None if is_placeholder(v) else v


def cfg_list(key):
    return [x.strip() for x in (cfg_get(key) or "").split(",") if x.strip()]


EXEMPT = cfg_list("MODEL_EXEMPT_TYPES")
FORBIDDEN = cfg_get("FORBIDDEN_SPAWN_TIER") or ""
LANE = cfg_get("LANE_TIER")
TRIPWIRE = (cfg_get("PROTECTED_PATH_ENABLED") or "").lower() in {"1", "true",
                                                                 "yes", "on"}
# Whether the key was WRITTEN AT ALL, which is a different fact from whether it
# is true. "the owner turned this feature off" and "nobody has said" must not
# collapse into the same report - see tripwire_status() below.
TRIPWIRE_DECLARED = "PROTECTED_PATH_ENABLED" in CFG


def tripwire_status():
    """None to RUN the fixture, else ("N/A"|"SKIP", reason).

    THE THIRD STATE, and it resolves a real contradiction in this kit's own
    documentation. QUICKSTART Step 1 says "do not enable the tripwire yet";
    Step 6's checkpoint demands "0 skipped"; the verify runner's hooks gate
    puts a ceiling of 0 on skips. Following the documentation in order made
    VERIFY: PASS unreachable, and the kit's own config quietly shipped with the
    tripwire ON so its own smoke never walked its own advice.

    The bug was the vocabulary, not the thresholds. A feature that is switched
    OFF ON PURPOSE has no untested surface - there is nothing to be uncertain
    about, so it is not a gap and must not be counted as one. A feature nobody
    has declared IS a gap: we cannot tell whether it was meant to be on.

        N/A   the owner turned it off. Nothing to test. Not a gap.
        SKIP  we cannot tell, or it is half-configured. A real gap.
    """
    if TRIPWIRE and PROTECTED:
        return None
    if TRIPWIRE and not PROTECTED:
        return ("SKIP", "PROTECTED_PATH_ENABLED is true but PROTECTED_PATH is "
                        "unset - the tripwire is half-configured")
    if TRIPWIRE_DECLARED:
        return ("N/A", "tripwire disabled by config "
                       "(PROTECTED_PATH_ENABLED=false)")
    return ("SKIP", "no kit.config declares PROTECTED_PATH_ENABLED - cannot "
                    "tell whether a tripwire is wanted")
PROTECTED = cfg_get("PROTECTED_PATH")

# SB-2. When no real protected path is configured, fixtures l and m must still
# build a payload - and it must NOT be the placeholder the hook also reads.
# With `PROTECTED_PATH = NONE`, the old payload was `cp ./out.bin NONE/out.bin`
# and the hook substring-matched the literal word, so a completely
# unconfigured tripwire produced two PASSING fixtures. Fixture and defect moved
# together, which is the same class already closed for kit.config.
#
# A synthetic sentinel cannot collide with anything a config could name, so if
# these fixtures ever run unconfigured they fail honestly instead of passing.
SYNTHETIC_PROBE = "/__kit_probe__/no-protected-path-is-configured"
PROBE_PATH = PROTECTED or SYNTHETIC_PROBE


# --------------------------------------------------------------------------
# the fixture table
#   (id, label, accepted verdicts, payload, status-or-None, note, expect_text)
#
# `expect_text` (M-3) is a substring the DECISION REASON must contain. A
# fixture that only reads permissionDecision cannot see a deny whose
# remediation tells the reader to type a literal placeholder - which is what
# an unconfigured LANE_TIER used to produce ("add model: 'your lane tier'").
# The decision was right and the sentence was useless, and only the sentence
# reaches a human.
# --------------------------------------------------------------------------
def cert_token_present() -> bool:
    """Is there a cert-green token that could make the tripwire ALLOW?

    Read so fixtures l and m can name ONE verdict instead of two. An accept-set
    of {ask, allow} can never fail for its stated reason - whatever the hook
    says is on the list - and a fixture that cannot fail is counted vanity
    (M-5). Where the live state is knowable, the fixture asserts it."""
    root = cfg_get("PROJECT_ROOT")
    tok = cfg_get("CERT_TOKEN_FILE") or ".claude/cert-green.json"
    try:
        base = Path(root) if root else Path.cwd()
        return (base / tok).is_file()
    except OSError:
        return False


def fixtures() -> list[tuple]:
    # With no token on disk the hook CANNOT answer `allow`; say so exactly.
    _tw = {"ask", "allow"} if cert_token_present() else {"ask"}
    _tw_note = ("CONDITIONAL: allow iff a cert-green token covers the tree"
                if cert_token_present() else
                "no cert-green token exists, so `ask` is the ONLY correct "
                "answer - asserted exactly, not as one of two")
    f: list[tuple] = [
        ("a", "Workflow: agent() with NO model:", {"deny"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "const r = await agent({prompt: 'do a thing'});"}},
         None, "", None),

        ("b", "Workflow: model: on every agent()", {"silent"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "const r = await agent({prompt: 'x', model: 'lane'});"}},
         None, "", None),

        ("c", "Agent spawn without model", {"deny"},
         {"tool_name": "Agent",
          "tool_input": {"subagent_type": "general-purpose", "prompt": "x"}},
         None, "", None),

        ("d", "Agent spawn with model", {"silent"},
         {"tool_name": "Agent",
          "tool_input": {"subagent_type": "general-purpose", "prompt": "x",
                         "model": "lane"}},
         None, "", None),

        ("e", "Bash `git add -A`", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add -A"}},
         None, "", None),

        ("f", "PowerShell `git add -A`", {"deny"},
         {"tool_name": "PowerShell", "tool_input": {"command": "git add -A"}},
         None, "the ban must not be escapable by choosing the other shell "
               "tool", None),

        ("g", "Bash `git add .` after a `&&`", {"deny"},
         {"tool_name": "Bash",
          "tool_input": {"command": "cd sub && git add ."}},
         None, "command position, not line start", None),

        ("h", "Bash `git add specific.txt`", {"silent"},
         {"tool_name": "Bash", "tool_input": {"command": "git add specific.txt"}},
         None, "", None),

        ("i", "PROSE mentioning the banned form", {"silent"},
         {"tool_name": "Bash",
          "tool_input": {"command": "git commit -m 'ban git add -A in the hook'"}},
         None, "precision: the gate must not block its own documentation",
         None),

        # ---- THE MEASURED BYPASSES -------------------------------------
        # Three independent persona reads of the shipped kit found the same
        # class in one afternoon: the ban was a regex anchored at `^` or after `;&|`,
        # matching only `-A`, `--all` and `.`. Every fixture below walked past
        # it and left the run green. One fixture per measured form, because a
        # single fixture covering several would not say WHICH one regressed.
        ("t", "Bash: INDENTED `git add -A` inside a block", {"deny"},
         {"tool_name": "Bash",
          "tool_input": {"command": "if true; then\n    git add -A\nfi"}},
         None, "the worst of the set: one leading space or tab is the normal "
               "shape of a command inside an if or a for, not an evasion",
         None),

        ("u", "Bash: `git -C <path> add -A` (a global option first)", {"deny"},
         {"tool_name": "Bash",
          "tool_input": {"command": "git -C /tmp/other-repo add -A"}},
         None, "the subcommand is not the second token", None),

        ("v", "Bash: `git add -Av` (combined short flags)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add -Av"}},
         None, "-A is not always its own token", None),

        ("w", "Bash: `git stage -A` (the synonym)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git stage -A"}},
         None, "`stage` is `add` under another name", None),

        ("x", "Bash: `git add -u` (every tracked modification)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add -u"}},
         None, "blanket over tracked files rather than over the tree", None),

        ("y", "Bash: `git add :/` (the whole-repo pathspec)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add :/"}},
         None, "sweeps untracked files, which is the cited hazard", None),

        ("z", "Bash: `git add '*'` (the quoted glob)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add '*'"}},
         None, "quoting keeps the shell out of it and git does the sweep",
         None),

        ("aa", "Bash: `git commit -am` (stage and commit in one)", {"deny"},
         {"tool_name": "Bash",
          "tool_input": {"command": "git commit -am 'wip'"}},
         None, "the add never appears as a separate command", None),

        ("ab", "Bash: a quoted message CONTAINING a blanket flag", {"silent"},
         {"tool_name": "Bash",
          "tool_input": {"command":
                         "git commit -m \"refactor: add -a flag to the parser\""}},
         None, "THE CONTROL for the widened pattern. The scan must not read "
               "flags out of a quoted argument, or the ban starts blocking "
               "ordinary commit messages and gets deleted", None),

        # ---- THE FALSE-DENY CLASS THE WIDENING CREATED -----------------
        # The first widened pattern used `\s` between tokens, and `\s` matches
        # NEWLINE, so the token scan ran off the end of the git command and
        # through every following line until it met a quote or a `;&|`. Five
        # ordinary two-line blocks were measured DENYING. These are the shape
        # that matters: a targeted git command followed by an unrelated one
        # carrying a token that happens to look like a blanket marker.
        ("ae", "Bash: `git commit -F msg.txt` then `ls -la` on the next line",
         {"silent"},
         {"tool_name": "Bash",
          "tool_input": {"command": "git commit -F msg.txt\nls -la"}},
         None, "the scan must not leave the line it started on: `-la` carries "
               "an `a` and belongs to a different command", None),

        ("af", "Bash: `git add README.md` then `cd .` on the next line",
         {"silent"},
         {"tool_name": "Bash",
          "tool_input": {"command": "git add README.md\ncd ."}},
         None, "the same class with the `.` marker one line down", None),

        ("an", "Bash: `git add --dry-run .` (stages nothing)", {"silent"},
         {"tool_name": "Bash",
          "tool_input": {"command": "git add --dry-run ."}},
         None, "a dry run is the command an operator reaches for to see what a "
               "blanket add WOULD take; denying it blocks the remedy", None),

        # ---- THE SECOND ROUND OF MEASURED BYPASSES ---------------------
        # Found by one reviewer in one session AFTER three persona reads had
        # already been through this rule. Each is a distinct alternation branch, so one
        # fixture each: a shared fixture would not say which branch regressed.
        ("ag", "Bash: `git add \"-A\"` (the quoted flag)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add \"-A\""}},
         None, "two quotes from the form this rule is named for", None),

        ("ah", "Bash: `git add ./` (one character from `git add .`)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add ./"}},
         None, "", None),

        ("ai", "Bash: `git add --al` (git resolves long-option prefixes)",
         {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add --al"}},
         None, "`--al` is `--all` as far as git is concerned", None),

        ("aj", "Bash: `FOO=1 git add -A` (an assignment prefix)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "FOO=1 git add -A"}},
         None, "git is not the first token", None),

        ("ak", "Bash: `sudo git add -A` (a wrapper prefix)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "sudo git add -A"}},
         None, "the env/sudo/time/nohup family", None),

        ("al", "Bash: `git add ':(top)'` (pathspec magic)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "git add ':(top)'"}},
         None, "stages from the repository root whatever the cwd", None),

        ("am", "Bash: `echo $(git add -A)` (command substitution)", {"deny"},
         {"tool_name": "Bash", "tool_input": {"command": "echo $(git add -A)"}},
         None, "a command position the anchor did not know about", None),

        ("j", "Agent spawn requesting the orchestrator tier by name", {"deny"},
         {"tool_name": "Agent",
          "tool_input": {"subagent_type": "general-purpose", "prompt": "x",
                         "model": FORBIDDEN or "<unset>"}},
         None if FORBIDDEN else ("SKIP", "kit.config sets no "
                                 "FORBIDDEN_SPAWN_TIER"), "",
         # M-3: the deny must NAME the tier to use, from config. An
         # unconfigured LANE_TIER renders a labelled placeholder, never prose
         # that reads like advice.
         (LANE if LANE else "<LANE_TIER unset in kit.config>")),

        ("k", "Agent spawn, no model, EXEMPT type", {"silent"},
         {"tool_name": "Agent",
          "tool_input": {"subagent_type": (EXEMPT[0] if EXEMPT else "<none>"),
                         "prompt": "x"}},
         None if EXEMPT else ("SKIP", "kit.config lists no "
                              "MODEL_EXEMPT_TYPES"),
         "the type carries its own model", None),

        ("l", "Shell command touching the protected path", _tw,
         {"tool_name": "Bash",
          "tool_input": {"command": f"cp ./out.bin {PROBE_PATH}/out.bin"}},
         tripwire_status(), _tw_note, None),

        ("m", "Edit into the protected path", _tw,
         {"tool_name": "Edit",
          "tool_input": {"file_path": f"{PROBE_PATH}/config.yaml"}},
         tripwire_status(), _tw_note, None),

        # M-4. One commented-out `model:` used to satisfy the tier rule for a
        # completely different, undeclared agent() call. Comments are stripped
        # before counting now, so this must still DENY.
        ("p", "Workflow: agent() with no model, `model:` only in a comment",
         {"deny"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "// remember to add model: 'lane' here\n"
                                   "const r = await agent({prompt: 'x'});"}},
         None, "comments are stripped before the count", None),

        ("q", "Workflow: agent() with no model, `model:` in a block comment",
         {"deny"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "/* model: 'lane' */\n"
                                   "await agent({prompt: 'x'});"}},
         None, "/* */ too", None),

        # A `//` inside a STRING LITERAL used to blank the rest of its line,
        # taking the `agent(` call on that line with it. The count fell to
        # 0 vs 0 and the gate said NOTHING - a false ALLOW of an undeclared
        # spawn, produced by a URL, which is an ordinary thing to find in a
        # workflow script. Strings are masked in the same pass as comments now.
        ("r", "Workflow: a URL in a string literal must not blank the agent() "
              "call on its line", {"deny"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "const u = 'https://example.invalid/x';"
                                   " const r = await agent({prompt: 'z'});"}},
         None, "the string-literal false-allow direction", None),

        ("s", "Workflow: the same script WITH a model: declaration",
         {"silent"},
         {"tool_name": "Workflow",
          "tool_input": {"script": 'const u = "https://example.invalid/x";\n'
                                   "await agent({prompt: 'z', model: 'lane'});"}},
         None, "THE CONTROL for the masking: blanking string CONTENTS must "
               "not eat the declaration sitting outside them", None),

        # THE SAME MECHANISM, TWO MORE WAYS. Both of these were shipped as
        # DISCLOSED RESIDUALS in the wrong direction - the docstring called them
        # "a loud, immediate, fixable deny" and they were measured as SILENT
        # false allows, exactly like the URL above. Over-blanking removes the
        # agent() call with everything else and the count falls to 0 vs 0.
        ("ac", "Workflow: a regex literal containing an escaped slash", {"deny"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "const re = /https:\\/\\//;"
                                   " await agent({prompt: 'z'});"}},
         None, "`\\/` used to read as the start of a `//` comment", None),

        ("ad", "Workflow: a JS private field (`this.#id`)", {"deny"},
         {"tool_name": "Workflow",
          "tool_input": {"script": "this.#id = 1;"
                                   " await agent({prompt: 'z'});"}},
         None, "a `#` touching a `.` or an identifier is not a comment; a `#` "
               "after whitespace still is, because shell and Python scripts "
               "go through the same scanner", None),

        ("n", "An unrelated tool call", {"silent"},
         {"tool_name": "Read", "tool_input": {"file_path": "README.md"}},
         None, "the gate has no opinion about tools it does not govern",
         None),

        ("o", "Malformed input (not the expected shape)", {"silent"},
         {"nonsense": True},
         None, "fail-open on garbage; a gate that dies on odd input gets "
               "removed", None),
    ]
    return f


# --------------------------------------------------------------------------
# claim 1: is it armed?
# --------------------------------------------------------------------------
def matcher_arms(matcher: str, tool: str) -> bool:
    """Does this PreToolUse matcher cover this tool? Pure, and selftested.

    SHIP-BLOCKER. This was `tool in matcher` - a SUBSTRING test against a field
    the harness evaluates as a REGEX. Three measured consequences, all of them
    maximal green over an unwired gate:

      * a matcher of "NotebookEdit" reported `armed: Edit`, so Edit could be
        entirely unwired and the harness still exited 0;
      * "BashOutput" reported `armed: Bash` - and the blanket-`git add` ban,
        which lives on the Bash branch, was silently dead;
      * inversely, the perfectly valid wildcard ".*" reported UNARMED,
        which teaches people to distrust the check.

    A tool is armed iff the matcher FULLY matches the tool name, which is how
    the harness decides. `fullmatch` handles alternation ("Edit|Write") for
    free, and an empty matcher means "everything". A matcher that is not valid
    regex arms nothing and says so - refusing to guess is the point."""
    m = (matcher or "").strip()
    if m in ("", "*"):
        return True          # harness convention: no matcher = every tool
    try:
        return re.fullmatch(m, tool) is not None
    except re.error:
        return False


SCRIPT_SUFFIXES = (".py", ".ps1", ".sh", ".js", ".mjs", ".rb", ".pl", ".exe")


def hook_script_from_command(cmd: str):
    """The script a hook command would run, or None. Pure.

    SB-A. `--armed` proved a settings file NAMED the hook. It did not prove the
    named file EXISTS - so a settings entry pointing at a moved, renamed or
    never-copied script reported `armed:` for every tool and exited 0, while
    the harness would fail to start the hook on every single call. Silent, and
    maximal green.

    Deliberately simple: take the last quoted-or-bare token that looks like a
    script. Interpreters, flags and `-File` all fall away without needing to
    know any particular shell's grammar."""
    if not cmd:
        return None
    toks = re.findall(r'"([^"]+)"|\'([^\']+)\'|(\S+)', cmd)
    flat = [a or b or c for a, b, c in toks]
    for tok in reversed(flat):
        if tok.startswith("-"):
            continue
        if tok.lower().endswith(SCRIPT_SUFFIXES):
            return tok
    return None


def resolve_hook_script(raw: str, settings_path: Path):
    """(path, existed). Tried as absolute, then relative to the repo root the
    settings file implies (`<repo>/.claude/settings.json` -> `<repo>`), then
    relative to the working directory - which is the set of places a harness
    plausibly resolves it from."""
    cand = Path(raw)
    tries = [cand] if cand.is_absolute() else [
        settings_path.resolve().parent.parent / raw,
        Path.cwd() / raw,
    ]
    for t in tries:
        try:
            if t.is_file():
                return t, True
        except OSError:
            continue
    return tries[0], False


def check_armed(settings_path: Path, hook: Path) -> tuple[bool, list[str]]:
    """Parse the settings file (read-only) and assert the hook is referenced.

    Deliberately loose about SHAPE and strict about PRESENCE: harnesses differ
    in how hooks are declared, and a schema assertion here would rot. What
    cannot rot is 'the string naming this hook appears under a PreToolUse
    matcher covering the tools it governs'.
    """
    notes: list[str] = []
    try:
        s = json.loads(settings_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, [f"UNARMED: {settings_path} does not exist"]
    except Exception as e:
        return False, [f"UNARMED: {settings_path} could not be parsed: {e!r}"]

    pre = (s.get("hooks") or {}).get("PreToolUse") or []
    name = hook.name
    covered: set[str] = set()
    bad: list[str] = []
    for entry in pre:
        matcher = str(entry.get("matcher") or "")
        cmds = " ".join(str(h.get("command") or "")
                        for h in (entry.get("hooks") or []))
        if name not in cmds:
            continue
        # SB-A: named is not the same as startable.
        for h in (entry.get("hooks") or []):
            raw = hook_script_from_command(str(h.get("command") or ""))
            if raw is None:
                continue
            resolved, exists = resolve_hook_script(raw, settings_path)
            if not exists:
                bad.append(
                    f"UNSTARTABLE: matcher {matcher!r} names {raw!r}, which "
                    f"does not exist (looked for {resolved}). The harness "
                    f"would fail to start this hook on every call, and a hook "
                    f"that cannot start enforces nothing.")
        if matcher.strip() not in ("", "*"):
            try:
                re.compile(matcher)
            except re.error as e:
                bad.append(f"UNARMED: matcher {matcher!r} is not valid regex "
                           f"({e}) - the harness will not match anything with "
                           f"it, so this block arms nothing")
                continue
        for tool in ("Workflow", "Agent", "Bash", "PowerShell", "Edit",
                     "Write", "NotebookEdit"):
            if matcher_arms(matcher, tool):
                covered.add(tool)
    notes.extend(bad)
    want = {"Workflow", "Agent", "Bash", "Edit"}
    missing = sorted(want - covered)
    for t in sorted(covered):
        notes.append(f"armed: {t}")
    for t in missing:
        notes.append(f"UNARMED: no PreToolUse matcher wires {name} for {t}")
    return (not missing and not bad), notes


# --------------------------------------------------------------------------
# claim 2: what does it decide?
# --------------------------------------------------------------------------
def run_fixture(hook: Path, payload: dict, timeout: int = 30):
    try:
        p = subprocess.run([sys.executable, str(hook)],
                           input=json.dumps(payload).encode("utf-8"),
                           capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.decode("utf-8", "replace").strip(), \
            p.stderr.decode("utf-8", "replace").strip()
    except Exception as e:
        return -1, "", f"launch failed: {e!r}"


def judge(rc: int, so: str, se: str, accept: set[str], expect_text=None):
    """Returns (ok, got, why). The dead-man clause lives here.

    `expect_text` asserts a substring of the DECISION REASON. Only the reason
    reaches a human, and a correct decision with a useless sentence is a
    half-working gate: the reader is told to type a placeholder."""
    if so:
        try:
            blob = json.loads(so)
            got = (blob.get("hookSpecificOutput", {})
                   .get("permissionDecision")) or "<no decision key>"
            reason = (blob.get("hookSpecificOutput", {})
                      .get("permissionDecisionReason") or "")
        except Exception:
            got, reason = "<unparseable stdout>", ""
        ok = got in accept
        why = f"got {got!r}"
        if ok and expect_text:
            if expect_text in reason:
                why += f"; reason names {expect_text!r}"
            else:
                ok = False
                why += (f"; but the REASON does not contain {expect_text!r} - "
                        f"the decision is right and the sentence a human "
                        f"reads is not. Reason was: {reason[:180]!r}")
        if se:
            why += f"  [note: stderr {se[:100]!r} - not fatal, a decision was delivered]"
        if rc != 0:
            why += f"  [note: rc={rc} - not fatal, a decision was delivered]"
        return ok, got, why
    if rc != 0:
        return False, "silent", (
            f"DEAD-MAN: no output and rc={rc} - silence from a corpse is not "
            f"consent. stderr={se[:160]!r}")
    ok = "silent" in accept
    why = "silent (clean exit)" if ok else (
        "DEAD-MAN: a must-decide fixture produced NO output - a silently dead "
        "gate reads as failure, never as allowed")
    if se:
        why += f"  [note: stderr {se[:100]!r}]"
    return ok, "silent", why


# ==========================================================================
# --selftest : the harness's own pure layer, judged
# ==========================================================================
# The fixtures judge the HOOK. Nothing judged the harness, and the harness
# contained a ship-blocker for weeks: `tool in matcher`, a substring test on a
# field the harness evaluates as a regex, which reported maximal green over an
# unwired gate. A checker with no checker of its own is the oldest hole there
# is.
def selftest() -> int:
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    print("=== A. matcher_arms: the matcher is a REGEX, not a substring ===")
    check("an exact name arms its own tool", matcher_arms("Bash", "Bash"), True)
    check("alternation arms every branch",
          [matcher_arms("Edit|Write|NotebookEdit", t)
           for t in ("Edit", "Write", "NotebookEdit")], [True, True, True])
    check("...and nothing else", matcher_arms("Edit|Write", "Bash"), False)

    # THE IMPOSTOR CLASS - each of these reported ARMED under the substring
    # test while the named tool was entirely unwired.
    check("IMPOSTOR: 'NotebookEdit' does NOT arm Edit",
          matcher_arms("NotebookEdit", "Edit"), False)
    check("IMPOSTOR: 'BashOutput' does NOT arm Bash (the git-add ban lived here)",
          matcher_arms("BashOutput", "Bash"), False)
    check("IMPOSTOR: 'WriteFile' does NOT arm Write",
          matcher_arms("WriteFile", "Write"), False)
    check("IMPOSTOR: 'AgentOutput' does NOT arm Agent",
          matcher_arms("AgentOutput", "Agent"), False)
    check("...but 'NotebookEdit' does arm NotebookEdit",
          matcher_arms("NotebookEdit", "NotebookEdit"), True)

    # THE INVERSE - a valid wildcard that used to report UNARMED, which
    # teaches people the check is broken and to stop reading it.
    check("the '.*' wildcard arms everything",
          [matcher_arms(".*", t) for t in ("Bash", "Edit", "Workflow")],
          [True, True, True])
    check("an empty matcher arms everything", matcher_arms("", "Bash"), True)
    check("'*' is treated as the harness convention, not as regex",
          matcher_arms("*", "Bash"), True)
    check("a real regex works as a regex",
          matcher_arms("^(Bash|PowerShell)$", "PowerShell"), True)
    check("invalid regex arms NOTHING rather than guessing",
          matcher_arms("Edit|[", "Edit"), False)

    print("\n=== B. cfg_get: NONE and empty mean UNSET ===")
    for placeholder in ("NONE", "none", "", "  ", "null", "TODO"):
        n += 1
        got = None
        try:
            CFG["__probe__"] = placeholder
            got = cfg_get("__probe__")
        finally:
            CFG.pop("__probe__", None)
        good = got is None
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {placeholder!r} reads as UNSET"
              + ("" if good else f"  (got {got!r})"))
    CFG["__probe__"] = "/real/path"
    check("a real value survives", cfg_get("__probe__"), "/real/path")
    CFG.pop("__probe__", None)

    print("\n=== A2. SB-A: named is not the same as STARTABLE ===")
    check("a quoted posix path is extracted",
          hook_script_from_command('python "tools/hook_model_gate.py"'),
          "tools/hook_model_gate.py")
    check("an unquoted path is extracted",
          hook_script_from_command("python tools/hook_model_gate.py"),
          "tools/hook_model_gate.py")
    check("pwsh -File is extracted, and the flag is not mistaken for it",
          hook_script_from_command(
              'pwsh -NoProfile -ExecutionPolicy Bypass -File "C:/r/h.ps1"'),
          "C:/r/h.ps1")
    check("a bare interpreter with no script yields None",
          hook_script_from_command("python -c pass"), None)
    check("an empty command yields None", hook_script_from_command(""), None)
    check("a path with spaces survives quoting",
          hook_script_from_command('python "/a b/c d/hook.py"'),
          "/a b/c d/hook.py")
    _me = Path(__file__).resolve()
    _set = _me.parent / ".claude" / "settings.json"
    check("an existing script resolves and exists",
          resolve_hook_script(str(_me), _set)[1], True)
    check("a missing script resolves and does NOT exist",
          resolve_hook_script("tools/definitely-not-here.py", _set)[1], False)

    print("\n=== B2. SB-C: the kit's own example values read as UNSET ===")
    # Every one of these is a real value shipped in kit.config.example. Each is
    # a perfectly ordinary non-empty string, and each would otherwise configure
    # a rule that guards nothing.
    shipped = [
        "your-top-tier-model", "your-mid-tier-model", "your-small-model",
        "your-runtime", "your-runtime --version", "your-runtime-1.2.3.zip",
        "/abs/path/to/your/knowledge-base", "/abs/path/outside/the/repo/verify-out",
        "/abs/path/to/statusboard.txt", "/abs/path/to/your/repo/tools/statusline.py",
        "https://example.invalid/your-runtime-1.2.3.zip",
        "<paste the checksum from the publisher's own sums file>",
        "derive-from-your-own-data", "NONE",
    ]
    for v in shipped:
        n += 1
        good = is_placeholder(v)
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] shipped placeholder "
              f"{v[:44]!r} reads as UNSET")
    check("a real tier name is NOT a placeholder",
          is_placeholder("claude-opus-4"), False)
    check("a real absolute path is NOT a placeholder",
          is_placeholder("/home/dev/project"), False)
    check("a real URL is NOT a placeholder",
          is_placeholder("https://github.com/org/repo/releases/x.zip"), False)
    check("a value that merely CONTAINS 'your' is not a placeholder",
          is_placeholder("bring-your-own-key"), False)

    print("\n=== C. the synthetic probe cannot collide with a config ===")
    check("the probe path is not derived from PROTECTED_PATH",
          SYNTHETIC_PROBE.startswith("/__kit_probe__"), True)
    check("an unset protected path yields the synthetic probe, not a "
          "placeholder string",
          "NONE" in PROBE_PATH if PROTECTED is None else True, False
          if PROTECTED is None else True)

    print("\n=== D. judge(): the dead-man clause and the reason text ===")
    deny = json.dumps({"hookSpecificOutput": {
        "permissionDecision": "deny",
        "permissionDecisionReason": "use model: 'lane-tier' instead"}})
    check("an accepted decision passes", judge(0, deny, "", {"deny"})[0], True)
    check("a reason-text assertion passes when the text is there",
          judge(0, deny, "", {"deny"}, "lane-tier")[0], True)
    check("M-3: a right decision with the WRONG SENTENCE fails",
          judge(0, deny, "", {"deny"}, "your lane tier")[0], False)
    check("silence from a corpse is not consent",
          judge(9, "", "boom", {"silent"})[0], False)
    check("silence from a clean exit is a verdict",
          judge(0, "", "", {"silent"})[0], True)
    check("a decision delivered despite stderr still counts",
          judge(0, deny, "a warning", {"deny"})[0], True)

    print()
    print(f"HOOK-FIXTURE SELFTEST: {'PASS' if ok_all else 'FAIL'} — {n} checks")
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the hook fixture harness.")
    ap.add_argument("--hook", default=str(DEFAULT_HOOK))
    ap.add_argument("--armed", default="",
                    help="settings file to check the hook is wired into")
    ap.add_argument("--strict", action="store_true",
                    help="a SKIPPED fixture counts as a failure")
    ap.add_argument("--make-deadman", default="",
                    help="write a corpse hook into this dir and exit")
    ap.add_argument("--selftest", action="store_true",
                    help="judge this harness's OWN pure layer - the matcher "
                         "parser, the unset-config rule, the reason-text "
                         "assertion and the dead-man clause. Runs no hook.")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if a.selftest:
        return selftest()

    if a.make_deadman:
        d = Path(a.make_deadman)
        d.mkdir(parents=True, exist_ok=True)
        f = d / "hook_model_gate.py"
        f.write_text(DEADMAN_SOURCE, encoding="utf-8")
        print(f"corpse hook written: {f}")
        # The path this process was actually invoked by, not a bare filename:
        # the printed command has to work from where the reader is standing,
        # and they are rarely standing in this directory.
        me = Path(sys.argv[0]).resolve()
        print(f'now run:  python "{me}" --hook "{f}"')
        return 0

    hook = Path(a.hook).resolve()
    if not hook.exists():
        print(f"ABORT: no hook at {hook}", file=sys.stderr)
        return 2
    instrumented = hook != DEFAULT_HOOK.resolve()

    print(f"hook      : {hook}")
    if instrumented:
        print("            *** INSTRUMENTED RUN - this is NOT the wired hook ***")

    # ---- the config report, and the warning that used to be missing -----
    # A hook running with NO config is not a hook with sensible defaults: the
    # forbidden-tier rule, the exempt types and the protected path simply do
    # not exist, and this harness quietly downgrades four fixtures to SKIP.
    # Eleven greens and four skips looks like success. It is not, and this is
    # where the run says so - in a line the verify runner's `hooks` gate also
    # vetoes on ("CONFIG WARNING").
    config_warnings: list[str] = []
    env_cfg = os.environ.get("KIT_CONFIG")
    if env_cfg and not Path(env_cfg).is_file():
        config_warnings.append(
            f"$KIT_CONFIG points at {env_cfg!r}, which is not a file")
    if CFG_SOURCE is None:
        print("config    : NONE - running on built-in defaults")
        config_warnings.append(
            "no kit.config was found by any of the four search steps "
            "($KIT_CONFIG, ./kit.config, <hook dir>/kit.config, then the "
            "nearest kit.config walking up). Every config-driven rule is "
            "therefore ABSENT, not merely unconfigured. QUICKSTART Step 1 "
            "creates kit.config in the repo root for exactly this reason, and "
            "module 02's own README lists the copy among its adoption "
            "commands.")
    else:
        overlay = CFG_SOURCE.with_name("kit.config.local")
        print(f"config    : {CFG_SOURCE}"
              + ("  (+ kit.config.local overlay)" if overlay.is_file() else ""))
        if CFG_OTHERS:
            config_warnings.append(
                "more than one kit.config is visible from here; the first in "
                "search order won. Others: "
                + ", ".join(str(x) for x in CFG_OTHERS[:3]))
    # M-3. With the tripwire ON but PROJECT_ROOT or CERT_PATHS unset, the
    # cert-green pre-authorisation can never evaluate: the hook falls straight
    # to `ask` forever. That is the SAFE direction, so nothing fails - which is
    # exactly why it needs saying out loud. A feature that silently cannot work
    # is indistinguishable from one that is working and has not been needed.
    # SB-C. `FORBIDDEN_SPAWN_TIER = your-top-tier-model` is the kit's own
    # example value. Read as configured, it produces a rule that guards a tier
    # nobody will ever request - enforcement-shaped, and enforcing nothing. The
    # shared unset rule makes it UNSET; this makes the consequence audible,
    # because a silently-absent rule is the exact failure this module exists
    # to prevent.
    for key, what in (("FORBIDDEN_SPAWN_TIER",
                       "no tier is forbidden by name"),
                      ("MODEL_EXEMPT_TYPES",
                       "no agent type is exempt from declaring a tier")):
        raw = (CFG.get(key) or "").strip()
        if cfg_get(key) is None:
            how = (f"is still the placeholder {raw!r}" if raw
                   else "is unset")
            config_warnings.append(
                f"{key} {how}, so {what}. A rule configured with an example "
                f"value looks enforced and is not.")
    if TRIPWIRE:
        missing = [k for k in ("PROJECT_ROOT", "CERT_PATHS")
                   if not cfg_get(k)]
        if missing:
            config_warnings.append(
                f"the tripwire is ON but {' and '.join(missing)} "
                f"{'is' if len(missing) == 1 else 'are'} unset, so cert-green "
                f"pre-authorisation can NEVER fire - every protected touch "
                f"will ask forever. Safe, but not what the token is for.")
    for w in config_warnings:
        print(f"CONFIG WARNING: {w}")
    print()

    armed_ok = True
    if a.armed:
        armed_ok, notes = check_armed(Path(a.armed), hook)
        print("--- claim 1: is the hook ARMED? ---")
        for n in notes:
            print(f"  {n}")
        print()

    print("--- claim 2: what does it DECIDE? ---")
    passed = failed = skipped = na = 0
    for fid, label, accept, payload, status, note, expect_text in fixtures():
        if status:
            state, reason = status
            if state == "N/A":
                na += 1
            else:
                skipped += 1
            print(f"[{state:<4}] {fid}. {label}  ({reason})")
            continue
        rc, so, se = run_fixture(hook, payload)
        ok, got, why = judge(rc, so, se, accept, expect_text)
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        tail = f"   ({note})" if note else ""
        print(f"[{'PASS' if ok else 'FAIL'}] {fid}. {label} -> accept "
              f"{sorted(accept)}; {why}{tail}")
        if not ok:
            print(f"       payload: {json.dumps(payload)}")
            print(f"       stdout : {so[:400]}")

    total = passed + failed
    print()
    # Three numbers, because there are three states and collapsing any two of
    # them is how a suite comes to report green about nothing. `n/a` is not a
    # softer `skipped`: it means the feature is off by the owner's choice, so
    # there is no untested surface behind it.
    print(f"HOOK FIXTURES: {passed}/{total} passed, {skipped} skipped, "
          f"{na} n/a" + ("" if armed_ok else ", HOOK NOT ARMED"))
    if a.strict and skipped:
        print("STRICT: a skipped fixture is a failure - complete kit.config. "
              "(n/a is not a skip: it means the feature is off on purpose.)")
        return 1
    if a.strict and config_warnings:
        print("STRICT: a config warning is a failure - a gate tested without "
              "its config is a gate whose rules were never loaded.")
        return 1
    return 0 if (failed == 0 and armed_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
