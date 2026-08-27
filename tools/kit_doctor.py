#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/kit_doctor.py - check my adoption. One command, two check sets, no
verdict that could be mistaken for a certification.

    python tools/kit_doctor.py                 # diagnose this repository
    python tools/kit_doctor.py --root <path>   # diagnose another one
    python tools/kit_doctor.py --level1        # the documents-only diagnosis
    python tools/kit_doctor.py --selftest      # judge this tool's own layer
    python tools/kit_doctor.py --list          # print the check inventory

    exit 0  HEALTHY   - no check reported ATTENTION
    exit 1  ATTENTION - at least one check did. Every such line names the step
                        that fixes it.
    exit 2  ABORT     - the tool could not work out what it was looking at
                        (no repository root, no kit.config). It refuses rather
                        than reporting HEALTHY about a tree it never found.

==========================================================================
THE VERDICT WORD IS NOT `PASS`, AND THAT IS THE POINT
==========================================================================
`PASS` belongs to `verify.py`, which runs the project's gates and returns one
exit code that means "the checks this project trusts ran and were green".
This tool runs no gates. It reads configuration, asks git some questions, and
looks at the shape of the adoption. It can tell you that a gate CANNOT FAIL;
it cannot tell you that a gate PASSED. Those are different claims and they must
not share a word, or an adopter comes away believing a diagnosis certified
something.

So: HEALTHY / ATTENTION. The doctor diagnoses. It does not certify.

==========================================================================
WHAT IT WILL NEVER DO
==========================================================================
IT NEVER STAGES ANYTHING. An earlier design had the dirty-paths check offer to
`git add` the files it found, and that design was killed in review: a tool that
diagnoses blanket staging must not be able to perform blanket staging, and a
diagnostic that mutates the tree it is diagnosing has changed its own subject.
The only writes this tool performs are to stdout.

It also runs no gate, mints no token, and edits no config.

==========================================================================
TWO CHECK SETS, AND WHY THEY DO NOT MIX
==========================================================================
The {N_FULL} default checks read a verify runner, a settings file and a hook. A
tree adopted by `LEVEL-1.md` has none of those on purpose: Level 1 installs
documents. Running the default set against it would report ATTENTION on six
checks, most of them about files the adopter was told not to install, which is
a tool teaching its reader to ignore it.

(The two counts in this section are NOT typed here. They are substituted from
`len(CHECKS)` and `len(L1_CHECKS)` immediately after those lists are defined,
because the typed versions drifted: this docstring said "ten" and "five" while
the lists held 12 and 7, and nothing related the prose to the code. The six is
measured rather than derived - run the full set against a Level-1 tree - and it
is the one number in this file a reader still has to check by hand.)

So `--level1` runs the {N_L1} `doctor:l1-*` checks instead, over the documents
Level 1 does install. They judge SHAPE - present, rendered, committed, and
carrying the two answers Level 1 asks for. They judge no CONTENT and run no
gate, and the green summary says so in the same breath as the green: what it
certifies, what it does not, and what removing the level costs.

==========================================================================
RUNNING IT ON THE KIT'S OWN CHECKOUT
==========================================================================
It reports ATTENTION, and that is the correct answer. The kit ships two
`example_*` gates that QUICKSTART Step 3 tells you to replace, and it ships no
`docs/ORACLE-<gate>.md` pages for them because they are illustrations rather
than oracles. The vacuous-gate check says exactly that, by name. A diagnosis
tool that made an exception for its own repository would be the first thing an
adopter learned to distrust.

==========================================================================
PORTABILITY
==========================================================================
Stock Python, no dependencies, Windows and POSIX.

Two path rules, both of them scar tissue. Directory comparisons go through
`same_path()`, which resolves symlinks and case-folds, because "the repository
root the doctor was pointed at" and "the repository root the verify runner
discovered for itself" are routinely two spellings of one directory on Windows
- and when they are two spellings of two DIFFERENT directories, every constant
this tool reads out of the runner describes a tree it is not looking at. And
filesystem case-sensitivity is PROBED rather than inferred from `os.name`,
because a case-sensitive directory on NTFS and a case-sensitive APFS volume
both exist.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

# THE FIRST STATEMENT THAT RUNS, and it belongs ahead of every import of a
# target's code. This tool imports the diagnosed repository's `verify.py` and
# `hook_model_gate.py` to read their constants as data, and Python writes a
# `__pycache__/*.pyc` beside every module it imports. Measured on a scratch
# adoption whose .gitignore carried no `__pycache__` rule: two new untracked
# directories, which the doctor's own dirty-paths check then reported back to
# the adopter as their dirty tree. A tool that diagnoses a working tree must not
# write into one - the same rule `filesystem_folds_case()` already follows by
# flipping the case of a file that is already there instead of creating one. It
# was applied to the case probe and missed for the imports.
sys.dont_write_bytecode = True

# THE VERSION THIS TOOL BELONGS TO. Compared against the `VERSION` file in the
# tree being diagnosed - two artifacts, so the comparison is a real check: copy
# a newer `tools/` into a repo whose `VERSION` was never refreshed and this is
# what says so.
KIT_VERSION = "0.1.0"

HERE = Path(__file__).resolve().parent

GREEN, RED, YELLOW, CYAN, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[1m", "\033[0m")
try:
    # BOTH streams. The abort message goes to stderr, and an unreconfigured
    # stderr renders the em dash in it as mojibake on a Windows console - a
    # small thing, in the one message an adopter sees when nothing else worked.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
if os.name == "nt":
    try:
        import ctypes
        _k = ctypes.windll.kernel32
        _k.SetConsoleMode(_k.GetStdHandle(-11), 7)
    except Exception:
        GREEN = RED = YELLOW = CYAN = BOLD = RESET = ""


# ==========================================================================
# THE PURE LAYER
# Everything above the RUNNING LAYER banner is a pure function of its
# arguments: no clock, no filesystem, no subprocess. That is what makes
# --selftest able to reconstruct real defects instead of probing fakes.
# ==========================================================================
OK, ATTENTION, NA, INFO = "OK", "ATTENTION", "n/a", "INFO"

# Every git verb this tool is allowed to use. Not decoration: --selftest
# recovers the verbs from this file's own source and holds them to this set, so
# "it never stages anything" is a check rather than a promise in a docstring.
READ_ONLY_GIT = {"rev-parse", "check-ignore", "status", "log", "merge-base"}
# ...and the verbs that would make the promise false. Named explicitly so the
# selftest can assert the allowlist and the prohibition separately: an
# allowlist that quietly grew a mutating verb would otherwise pass its own
# check.
MUTATING_GIT = {"add", "stage", "commit", "reset", "checkout", "restore",
                "rm", "mv", "push", "clean", "apply", "stash", "update-index"}


class Finding:
    """One check's answer. `fix` is mandatory on ATTENTION: a red line that
    does not name the fixing step is a line the reader has to go and research,
    and a diagnosis nobody can act on is a diagnosis nobody runs twice.

    AN INVARIANT, NOT A CONVENTION. The rule started as a selftest section that
    constructed each red branch by hand and asserted every one carried a fix.
    A reviewer's mutation removed the fixing step from a branch the list had
    never enumerated - `judge_paths_exist([])` - and the suite stayed green. A
    hand-maintained list of branches is exactly the shape this kit distrusts
    everywhere else, so the rule moved into the constructor, where it covers
    branches nobody remembered and branches nobody has written yet."""

    def __init__(self, state: str, headline: str, detail: str = "",
                 fix: str = ""):
        if state == ATTENTION and not (fix or "").strip():
            raise ValueError(
                f"Finding({headline!r}) reports ATTENTION with no fixing step. "
                f"Every red line names the step that fixes it - that is the "
                f"tool's contract with the reader, and it is enforced here "
                f"rather than in a list of branches somebody has to remember "
                f"to extend.")
        self.state = state
        self.headline = headline
        self.detail = detail
        self.fix = fix

    def __repr__(self):                        # selftest readability
        return f"Finding({self.state}, {self.headline!r})"


def path_inside(child, parent) -> bool:
    """True when `child` is `parent` or lives under it. Case-folded and
    symlink-resolved, the same rule `tools/kit_render.py` uses."""
    try:
        c = os.path.normcase(os.path.realpath(str(child)))
        p = os.path.normcase(os.path.realpath(str(parent)))
    except (OSError, ValueError):
        return False
    return c == p or c.startswith(p.rstrip(os.sep) + os.sep)


def choose_config(env, env_is_file: bool, env_inside_kit: bool,
                  target_cfg, target_exists: bool):
    """(the config to read, notes). Pure.

    DELIBERATELY NOT the four-step search every other tool in this kit uses,
    and this function is the fix for a defect the tool's own first live run
    produced. Those tools live inside the repository they configure, so "the
    current working directory" and "walk up from my own directory" both land on
    the right file. This one runs FROM a kit checkout and points AT another
    repository, so both of those answers are wrong - and wrong in the quietest
    way, because the kit ships a filled-in `kit.config` of its own as a worked
    example. Pointed at an empty repository from inside the kit, the first
    version of this tool loaded the KIT's config and reported the kit's
    settings as the adopter's. `kit_render.py` documents the same class for the
    same reason; this is it arriving by a third road.

    `$KIT_CONFIG` still wins where it names a config OUTSIDE the kit checkout -
    that is an explicit instruction rather than an accident of where the shell
    happened to be - but never where it names one inside it. QUICKSTART Step 2
    sets that variable at a kit path and warns that failing to unset it leaks
    into the rest of the session, so honouring it here would diagnose the kit."""
    notes = []
    if env:
        if not env_is_file:
            notes.append(f"$KIT_CONFIG points at {env!r}, which is not a file "
                         f"- ignored; using the target's kit.config.")
        elif env_inside_kit:
            notes.append(f"$KIT_CONFIG points INSIDE the kit checkout ({env}) "
                         f"and has been IGNORED. That variable would diagnose "
                         f"the kit's own configuration and report it as yours.")
        else:
            return env, notes
    return (target_cfg if target_exists else None), notes


def same_path(a, b) -> bool:
    """One directory, however it is spelled. Case-folded and symlink-resolved,
    the same rule `tools/kit_render.py` uses, for the same reason: on Windows
    the two paths being compared are routinely two spellings of one place, and
    a naive `==` reports a difference that does not exist."""
    try:
        return (os.path.normcase(os.path.realpath(str(a)))
                == os.path.normcase(os.path.realpath(str(b))))
    except (OSError, ValueError):
        return False


def split_list(raw: str) -> list:
    return [x.strip() for x in (raw or "").split(",") if x.strip()]


# ---- check 1: the version stamp -----------------------------------------
def judge_version(stamp, tool_version: str) -> Finding:
    """`stamp` is the VERSION file's contents, or None when there is no file.

    HONEST ABOUT WHAT A STAMP IS. This records which kit version a tree was
    adopted from. Nothing verifies that the files in the tree MATCH that
    version - a stamp is a claim by whoever last copied files in, and the only
    thing mechanically checkable is whether the stamp and the tools disagree
    with each other. That is worth checking, because it is exactly the state a
    partial re-copy leaves behind, and it is the question nobody could ask
    before: did the kit update break us."""
    if stamp is None:
        return Finding(
            ATTENTION, "no VERSION file",
            "This tree records no kit version, so a later run cannot tell "
            "which release your copied tools came from.",
            "Copy the kit's `VERSION` file to the root of this repository. "
            f"The tools in this checkout came from {tool_version}.")
    s = stamp.strip()
    if not s:
        return Finding(ATTENTION, "empty VERSION file",
                       "The file exists and says nothing.",
                       "Write the kit version into it, one line, no prefix - "
                       f"e.g. `{tool_version}`.")
    if s != tool_version:
        return Finding(
            ATTENTION, f"VERSION {s} but tools from {tool_version}",
            f"The stamp in this tree says {s}; kit_doctor.py was copied from "
            f"{tool_version}. A partial re-copy leaves exactly this state, and "
            f"the halves that did not move are the ones to look at.",
            "Re-copy the whole `tools/` and `modules/` set from one kit "
            "checkout, then refresh `VERSION` from that same checkout.")
    return Finding(OK, f"kit {s}",
                   "The stamp and this tool agree. Note what that does and "
                   "does not prove: it proves the stamp matches THIS file, "
                   "not that every other copied file is from that release.")


# ---- check 2: the config, and the rules a placeholder silently deletes ---
def judge_config(source, cfg: dict, placeholder) -> Finding:
    """`placeholder` is a callable(str) -> bool - the hook's own rule, passed
    in rather than re-implemented. Three readers disagreeing about what
    "configured" means is how a gate comes to be judged by a harness looking
    at a different program, and a fourth copy of the rule here would be the
    fourth reader."""
    if source is None:
        return Finding(
            ATTENTION, "no kit.config found",
            "The tree being diagnosed has no `kit.config` at its root, and "
            "this tool will not fall back to the kit's own worked example - "
            "that would report the kit's settings as yours. Every "
            "config-driven rule in the hook is therefore ABSENT here, not "
            "merely unconfigured, and nothing in the hook's output says so.",
            "QUICKSTART Step 1: copy `kit.config.example` to `kit.config` in "
            "your repository root and fill the list that step names.")
    # Keys whose placeholder value silently switches a rule off. Not every
    # key: only the ones where "still the example value" and "configured"
    # produce different enforcement.
    load_bearing = {
        "FORBIDDEN_SPAWN_TIER": "no model tier is forbidden by name, so the "
                                "rule that stops a spawn asking for the "
                                "orchestrator tier does not exist",
        "LANE_TIER": "the hook's deny messages cannot name the tier a reader "
                     "should use instead",
        "MODEL_EXEMPT_TYPES": "no agent type is exempt, so exempt spawns are "
                              "denied rather than allowed",
        "JUDGE_PATHS": "the runner is judging a path list that came from "
                       "somewhere other than this config",
    }
    unset = [k for k in sorted(load_bearing)
             if placeholder((cfg.get(k) or "").strip())]
    if unset:
        return Finding(
            ATTENTION, f"{len(unset)} load-bearing key(s) still unset",
            "\n".join(f"      {k} is unset or still a placeholder - "
                      f"{load_bearing[k]}" for k in unset),
            "QUICKSTART Step 1's fill list names every one of these. A rule "
            "configured with an example value looks enforced and is not.")
    return Finding(OK, f"config at {source}",
                   "Every load-bearing key carries a real value.")


# ---- check 3: do the judged paths exist? --------------------------------
def judge_paths_exist(judged: list, exists) -> Finding:
    missing = [p for p in judged if not exists(p)]
    if not judged:
        return Finding(ATTENTION, "no judged paths",
                       "The runner names no JUDGE_PATHS and no CERT_PATHS, so "
                       "the `judges` gate is asking git about nothing at all "
                       "and reporting it clean.",
                       "QUICKSTART Step 4: name the files that decide what "
                       "green MEANS at the top of your verify runner.")
    if missing:
        return Finding(
            ATTENTION, f"{len(missing)} judged path(s) missing",
            "\n".join(f"      {p} does not exist under the repository root"
                      for p in missing),
            "Either the paths are wrong or the root is. `git status "
            "--porcelain -- <a path that does not exist>` prints nothing and "
            "exits 0, and nothing is how clean is spelled - fix the list at "
            "the top of your verify runner (QUICKSTART Step 4).")
    return Finding(OK, f"{len(judged)} judged path(s) present")


# ---- check 4: are any of them EXCLUDED by the ignore rules? -------------
def judge_paths_excluded(judged: list, excluded: list, note: str) -> Finding:
    """The same class the runner's startup assertion catches at certification
    time, asked on demand. A judged path the repo's own ignore rules exclude is
    invisible to `git status`, so the judges gate reads clean over it forever
    whatever the file says."""
    if note:
        return Finding(
            ATTENTION, "git could not answer",
            f"      {note}",
            "An excluded judged path reads as clean forever, and this tool "
            "will not guess. Fix the git installation or run from inside the "
            "work tree.")
    if excluded:
        return Finding(
            ATTENTION, f"{len(excluded)} judged path(s) EXCLUDED by ignore rules",
            "\n".join(f"      {p} is ignored and untracked, so "
                      f"`git status --porcelain -- {p}` prints nothing "
                      f"whatever the file says" for p in excluded),
            "`git check-ignore -v <path>` names the rule and the file it came "
            "from. Remove that rule, then commit the path. `.claude/` in a "
            "pre-existing ignore file is the common cause, and "
            "`.claude/settings.json` is the file that decides whether your "
            "hooks run at all.")
    return Finding(OK, "no judged path is excluded")


# ---- check 5: hook config and runner constants agree -------------------
def judge_paths_agree(cfg_paths: dict, runner_paths: dict,
                      runner_root_matches=None) -> Finding:
    """The runner holds JUDGE_PATHS and CERT_PATHS as constants; `kit.config`
    holds them as keys, and the ENFORCEMENT HOOK reads the config copy.

    THE REAL CONSEQUENCE, stated because a bare "these two lists differ" reads
    as tidiness: `cert_green()` in the hook decides whether a protected-path
    write is pre-authorised by asking whether CERT_PATHS are clean and covered
    - using the CONFIG's list. The runner certified using ITS list. When the
    two disagree, the hook is pre-authorising writes on the strength of a
    certification that judged a different set of files. Both halves report
    green while meaning different things by it.

    The runner is authoritative: it is the program that produces the verdict.

    `runner_root_matches` is the second half, and it is a second-machine
    finding rather than a config one: the runner discovers ITS repository root
    by walking up from its own file, so a runner living outside the tree the
    doctor was pointed at is judging one repository while this report describes
    another. False means they are genuinely different directories, not two
    spellings of one - the comparison is symlink-resolved and case-folded."""
    problems = []
    if runner_root_matches is False:
        problems.append(
            "      The verify runner resolved a DIFFERENT repository root "
            "than the one being diagnosed. Every constant read out of it "
            "below describes that other tree.")
    for key in ("JUDGE_PATHS", "CERT_PATHS"):
        want = runner_paths.get(key)
        got = cfg_paths.get(key)
        if want is None or got is None:
            continue
        if [p.replace("\\", "/") for p in want] != [p.replace("\\", "/")
                                                    for p in got]:
            only_cfg = [p for p in got if p not in want]
            only_run = [p for p in want if p not in got]
            problems.append(
                f"      {key} differs. verify.py is authoritative.\n"
                f"        only in kit.config : {only_cfg or 'nothing'}\n"
                f"        only in verify.py  : {only_run or 'nothing'}")
    if problems:
        return Finding(
            ATTENTION, "hook config and runner disagree about what is judged",
            "\n".join(problems),
            "Make `kit.config` match the constants at the top of your verify "
            "runner, and run both from inside the same repository. Until they "
            "match, the hook's cert-green check and the runner's judges gate "
            "are green about different sets of files.")
    return Finding(OK, "hook config and runner name the same judged paths")


# ---- check 6: gates that cannot fail ------------------------------------
def judge_vacuous_gates(gates: dict, run_order: list, computed: set,
                        oracle_exists) -> Finding:
    """A gate is VACUOUS when it cannot fail for the reason it claims to check.

    Three disjuncts, each a measured shape:
      * the required line has NO CAPTURE GROUP, so there is no number to put a
        floor on and `expect_min` is silently inert;
      * the FLOOR is <= 1, which any run producing one of anything satisfies -
        a floor of 1 over a suite that has quietly shrunk to a single case is
        the shape this check exists for;
      * there is NO `docs/ORACLE-<gate>.md` page, so nobody ever wrote down
        what the gate is supposed to catch or what it looked like red.

    Computed gates are exempt from the first two: they have no required line by
    construction, and the runner already refuses `--nc` overrides for them
    because nothing would consult one. They are still asked for an oracle page.

    A prose counter-example in a worksheet cannot reach the novice who believes
    their gate is real. This can."""
    problems = []
    for name in run_order:
        spec = gates.get(name) or {}
        why = []
        if name not in computed:
            pat = spec.get("require") or ""
            if not pat:
                why.append("no `require` pattern at all - the gate's log is "
                           "never judged")
            else:
                try:
                    if re.compile(pat).groups == 0:
                        why.append("the `require` pattern has no capture "
                                   "group, so there is no number to floor and "
                                   "`expect_min` is inert")
                except re.error as e:
                    why.append(f"the `require` pattern does not compile ({e})")
            mn = spec.get("expect_min")
            if mn is not None and mn <= 1:
                why.append(f"the floor is {mn}: any run producing one of "
                           f"anything clears it")
        if not oracle_exists(name):
            why.append(f"no ORACLE-{name}.md page - nothing records what this "
                       f"gate catches or what it looked like red")
        doc = (spec.get("doc") or "")
        if doc.startswith("EXAMPLE"):
            why.append("this is one of the kit's shipped EXAMPLE gates, which "
                       "QUICKSTART Step 3 tells you to replace")
        if why:
            problems.append(f"      gate {name!r}:\n"
                            + "\n".join(f"        - {w}" for w in why))
    if problems:
        return Finding(
            ATTENTION, f"{len(problems)} gate(s) cannot fail as configured",
            "\n".join(problems),
            "Fill in `modules/03-verification/ORACLE-WORKSHEET.md` for each "
            "gate named above and put the filled page at "
            "`docs/ORACLE-<gate-name>.md` (QUICKSTART Step 3), then set the "
            "`require` pattern and floor from what that page says the gate "
            "catches. A gate whose floor is 1 has not been given a floor.")
    return Finding(OK, f"{len(run_order)} gate(s) can fail")


# ---- check 7: what a blanket add would sweep up ------------------------
def judge_dirty_paths(porcelain: str, judged: list) -> Finding:
    """DIAGNOSTIC ONLY. It names files; it never stages one.

    `git add -A` takes everything in this list. The hook's point 3 denies the
    blanket forms, but a PreToolUse hook runs BEFORE the command, when the
    index still describes the world as it was, so the hook can only judge the
    STRING. This is the other half of that pair: the list the string was
    hiding, printed at the moment a human can still look at it.

    It reports ATTENTION only when a JUDGED path is dirty, because that has a
    consequence beyond taste - certification is a property of a tree, and a
    dirty judge path means the gates would be enforcing rules that exist only
    in this working copy. An ordinary dirty tree during a working session is
    not a finding, and a tool that called it one would be ignored by lunch."""
    entries = []
    for ln in (porcelain or "").splitlines():
        if len(ln) < 4:
            continue
        entries.append((ln[:2].strip() or "??", ln[3:].strip()))
    if not entries:
        return Finding(OK, "working tree clean",
                       "A blanket add would sweep up nothing.")
    dirty_judged = [(s, p) for s, p in entries
                    if any(p == j or p.startswith(j.rstrip("/") + "/")
                           for j in judged)]
    listing = "\n".join(f"      {s} {p}" for s, p in entries[:25])
    if len(entries) > 25:
        listing += f"\n      ... +{len(entries) - 25} more"
    body = ("These are the files `git add -A` would take. This tool stages "
            "nothing; it only names them.\n" + listing)
    if dirty_judged:
        return Finding(
            ATTENTION,
            f"{len(entries)} dirty, {len(dirty_judged)} of them JUDGED",
            body + "\n"
            + "\n".join(f"      JUDGED and uncommitted: {p}"
                        for _, p in dirty_judged),
            "Commit the judged paths before you certify. A run over a dirty "
            "judge surface enforces rules that exist only in this working "
            "copy, and `verify.py`'s judges gate will refuse it anyway.")
    return Finding(INFO, f"{len(entries)} path(s) a blanket add would sweep",
                   body)


# ---- check 8: can the hook's interpreter start? ------------------------
def interpreter_token(cmd: str, resolves) -> str:
    """The interpreter a hook command names. Pure; `resolves` is a
    callable(str) -> bool.

    THREE SHAPES, AND THE SECOND ONE IS THE DEFAULT WINDOWS INSTALL. A naive
    `cmd.split()[0].strip('"')` splits on whitespace BEFORE it strips quotes,
    so `"C:/Program Files/Python312/python.exe" hook.py` yields
    `"C:/Program` - which resolves to nothing, and the check then reports
    ATTENTION about the very arrangement its own fixing step recommends ("or an
    absolute path if your harness does not inherit your PATH").

      1. QUOTED. `shlex` in non-POSIX mode keeps the quotes on the token and
         does not treat a Windows backslash as an escape; the quotes come off
         afterwards. POSIX mode would turn `C:\\Python\\python.exe` into
         `C:Pythonpython.exe`.
      2. UNQUOTED WITH SPACES. Unresolvable in general - `a b` is either one
         path or a program and an argument - so the longest space-joined prefix
         that actually RESOLVES wins, which is how Windows itself reads it.
      3. BARE. One token, as before.

    Falls back to the first token when nothing resolves, so an ATTENTION still
    names something the reader recognises."""
    text = (cmd or "").strip()
    if not text:
        return ""
    try:
        toks = shlex.split(text, posix=False)
    except ValueError:
        toks = text.split()
    toks = [t.strip("\"'") for t in toks if t]
    if not toks:
        return ""
    if resolves(toks[0]):
        return toks[0]
    for k in range(2, len(toks) + 1):
        joined = " ".join(toks[:k])
        if resolves(joined):
            return joined
    return toks[0]


def judge_interpreter(commands: list, resolve) -> Finding:
    """`commands` are the hook command strings from the settings file;
    `resolve` is a callable(token) -> path-or-None.

    THE OTHER HALF OF A CLASS THE KIT ALREADY PAID FOR. The fixture harness
    checks that a matched command names a SCRIPT THAT EXISTS, because a
    settings entry pointing at a moved file reported `armed:` for every tool
    while the harness failed to start the hook on every call. The INTERPRETER
    half was left open, and the kit's own README documents the host where it
    bites: stock Debian and Ubuntu ship `python3` with no `python` shim, and
    the settings template invokes `{{PYTHON_BIN}}`, which ships as the bare
    word `python`. On that host every hook invocation produces no output, the
    harness proceeds, `--armed` still reports armed, and the run certifies a
    disarmed enforcement layer.

    RESOLUTION IS NOT EXECUTION, and this check does not claim it is. An
    interpreter that resolves and then crashes on start is the dead-man
    clause's job (`hook_fixtures.py`, which runs the hook and fails on silence
    from a non-zero exit). This closes the case where there is nothing to
    crash."""
    if not commands:
        return Finding(
            ATTENTION, "no hook commands found",
            "The settings file names no PreToolUse hook command, so nothing is "
            "wired and every rule in the enforcement module is inert.",
            "QUICKSTART Step 4 wires the hook into `.claude/settings.json`; "
            "`modules/02-enforcement/settings.json.template` is the shape.")
    bad = []
    for cmd in commands:
        tok = interpreter_token(cmd, lambda t: resolve(t) is not None)
        if not tok:
            continue
        if resolve(tok) is None:
            bad.append((tok, cmd))
    if bad:
        return Finding(
            ATTENTION, f"{len(bad)} hook command(s) UNSTARTABLE",
            "\n".join(f"      interpreter {t!r} does not resolve to an "
                      f"executable on this host\n        in: {c[:110]}"
                      for t, c in bad),
            "Set PYTHON_BIN in `kit.config` to something this host has - "
            "`python3` on stock Debian/Ubuntu, or an absolute path if your "
            "harness does not inherit your PATH - and re-render "
            "`.claude/settings.json`. A hook whose interpreter cannot start "
            "produces no output on every call, which the harness reads as "
            "'no opinion'.")
    return Finding(OK, f"{len(commands)} hook command(s) startable",
                   "Each command's interpreter resolves on this host. "
                   "Resolution is not execution - the dead-man clause in "
                   "hook_fixtures.py covers the rest.")


# ---- check 9: the protected path, on THIS filesystem -------------------
def judge_protected_case(enabled: bool, protected: str,
                         case_insensitive) -> Finding:
    """`case_insensitive` is None when it could not be probed.

    The tripwire is a substring match on a normalised string. On a
    case-insensitive filesystem - Windows, and macOS by default - a
    differently-cased spelling of the protected path opens the same file and
    the tripwire says nothing. Measured, in both the shell and the Edit
    branches.

    Folding inside the hook would be wrong on Linux, where the two spellings
    really are different files, and a gate that asks about a path the owner did
    not protect is the false positive that gets gates deleted. So the honest
    control is to say which host you are on and what it costs there."""
    if not enabled:
        return Finding(NA, "protected-path tripwire disabled",
                       "Nothing to be uncertain about: the feature is off by "
                       "the owner's choice, so there is no untested surface "
                       "behind it.")
    if not protected:
        return Finding(
            ATTENTION, "tripwire ON, no PROTECTED_PATH",
            "PROTECTED_PATH_ENABLED is true and PROTECTED_PATH is unset or "
            "still a placeholder. The tripwire is half-configured and guards "
            "nothing.",
            "Put the absolute path in `kit.config.local` (it is machine-"
            "specific and gitignored), or set PROTECTED_PATH_ENABLED = false.")
    if case_insensitive is None:
        return Finding(
            ATTENTION, "could not probe filesystem case sensitivity",
            "This tool could not determine whether the filesystem folds case, "
            "so it cannot say whether the tripwire's substring match is "
            "bypassable here.",
            "Treat the tripwire as case-sensitive: write the protected path "
            "in commands exactly as `kit.config` spells it.")
    if case_insensitive:
        return Finding(
            ATTENTION, "case-insensitive filesystem: the tripwire is bypassable",
            f"      PROTECTED_PATH is {protected!r} and this filesystem folds "
            f"case, so a differently-cased spelling reaches the same file and "
            f"the tripwire stays silent. `cd` followed by a relative path, and "
            f"symlinks or junctions into the location, do the same.",
            "Know it and work with it: spell the protected path as kit.config "
            "spells it, and do not treat point 4 as a boundary. It is friction "
            "that resolves toward the human, not a control that cannot be "
            "walked around. The same three directions are disclosed in "
            "`touches_protected()`.")
    return Finding(OK, "case-sensitive filesystem",
                   "A differently-cased spelling is a different file here, so "
                   "the substring match is not bypassable that way. `cd` then "
                   "relative, and symlinks, still are.")


# ---- check 10: the cert-green token ------------------------------------
def judge_cert_token(token, covered, dirty) -> Finding:
    """`token` is the parsed token dict, or None. `covered` and `dirty` are
    git's answers, or None when they could not be asked.

    THE POINT OF THIS CHECK IS THE LABEL. The token is the one control in the
    kit that turns a human prompt into an automatic allow, and it is an
    ordinary file: anything that can write a file can mint one, including the
    agents the tripwire governs. There is no signature and there is deliberately
    none - an HMAC needs a key, and at this privilege level there is nowhere to
    put a key the agent cannot read, so a signature would raise forgery from
    "write a file" to "read a file, then write a file" while making the token
    read as an attestation it is not. Saying so on every run is the control."""
    label = ("A cert-green token is a CONVENIENCE, not an authorization: it is "
             "unsigned, and anything able to write a file can mint one. It "
             "records that a run said PASS. It does not prove one ran.")
    if token is None:
        return Finding(NA, "no cert-green token", label)
    sha = (token.get("sha") or "").strip()
    if not sha:
        return Finding(ATTENTION, "token names no sha",
                       f"      The file exists and carries no `sha`, so "
                       f"nothing can be checked against it.\n      {label}",
                       "Delete it and mint a real one with "
                       "`python <your verify runner> --mint-cert-token`.")
    hand = "minted_by" not in token
    if covered is False or dirty is True:
        why = ("the certified paths have changed since it was minted"
               if covered is False else
               "the certified paths are dirty in this working copy")
        return Finding(
            ATTENTION, f"token {sha[:12]} no longer covers this tree",
            f"      It is stale: {why}. The hook falls back to asking the "
            f"owner, which is the safe direction - but a stale token in the "
            f"tree reads to a human as though certification still holds.\n"
            f"      {label}",
            "Re-certify and mint again "
            "(`python <your verify runner> --mint-cert-token`), or delete the "
            "file.")
    if covered is None or dirty is None:
        return Finding(
            ATTENTION, f"token {sha[:12]} could not be evaluated",
            f"      git could not be asked whether this token still covers "
            f"the tree.\n      {label}",
            "Run from inside the work tree, or delete the token: the hook "
            "treats a token it cannot evaluate as no token at all.")
    if hand:
        # INFO rather than OK. `minted_by` is the one field separating an
        # asserted token from a certified one, and a reader scanning the state
        # column for red would never reach the sentence in the body that says
        # so. There is nothing to FIX - a hand-written token is allowed - which
        # is what INFO is for in this tool.
        return Finding(
            INFO, f"token {sha[:12]} covers this tree, but was HAND-WRITTEN",
            f"      No `minted_by` field, so nothing connects this token to a "
            f"run of the verify runner. `--mint-cert-token` writes one from "
            f"the runner's single PASS return.\n      {label}")
    return Finding(OK, f"token {sha[:12]} covers this tree", f"      {label}")


# ==========================================================================
# THE ANTI-RATCHET PAIR - checks 11 and 12, and what they are for
# ==========================================================================
# The kit's standing rules say a floor grows monotonically until people route
# around it, and that a routed-around floor enforces nothing while costing
# everyone attention. Two rules exist to stop that: the demotion review, which
# disposes of quiet rules at every phase gate, and "keep the rules file short",
# which the module-01 template states three times. The enforcement layer for
# both was PROSE - the exact debt `FAILURE-FLOOR.md` exists to audit - and the
# owner's question was the shortest possible statement of the gap: what is
# checking the lessons?
#
# These two answer it, and neither judges CONTENT. One reads dates out of the
# floor's own table; the other counts lines. A ledger of excellent rules that
# nobody has fired in a year and a rules file of noise both pass every other
# check in this tool.
FLOOR_ROW = re.compile(r"^\|(?!\s*[-:]+\s*\|)(.+)\|\s*$", re.M)
FLOOR_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
# The demotion review's disposition vocabulary, from the module-04 template.
# A rule already carrying a final disposition is not overdue for one.
FLOOR_FINAL_STATUS = ("ACCEPTED",)


def parse_floor_rows(text: str) -> list:
    """[{rule, layer, zone, status, last_fired}] from the floor's markdown
    table. Pure.

    Deliberately tolerant about columns and strict about the one that matters:
    a row is only judged when it has at least five cells and the fifth is
    where the template puts `Last fired`. The template's own EXAMPLE rows are
    skipped by the angle-bracket prompt in their first cell - they are
    instructions, not rules this project holds."""
    out = []
    for m in FLOOR_ROW.finditer(text or ""):
        cells = [c.strip() for c in m.group(1).split("|")]
        if len(cells) < 5:
            continue
        rule = cells[0]
        if not rule or rule.lower() == "rule" or rule.startswith("<"):
            continue
        out.append({"rule": rule, "layer": cells[1], "zone": cells[2],
                    "status": cells[3], "last_fired": cells[4]})
    return out


def floor_staleness(rows: list, window_stages: int, today) -> dict:
    """The demotion review's arithmetic, as a pure function. `today` is passed
    in - the caller reads the clock, this does not.

    THE WINDOW IS DERIVED FROM THIS PROJECT'S OWN DATES, not inherited. The
    configured window is a number of STAGES and the table records DAYS, and no
    file in an adopting repository relates the two - so the interval between
    this floor's own distinct firing dates is the conversion, and it is the
    only measurement available that is about this project rather than about
    somebody else's. Fewer than two distinct dates makes it uncomputable, and
    the report says so rather than substituting a guess."""
    dated, never, unusable, exempt = [], [], [], []
    for r in rows:
        raw = r["last_fired"]
        status = r["status"].replace("*", "").strip().upper()
        if any(status == s for s in FLOOR_FINAL_STATUS):
            exempt.append(r["rule"])
            continue
        m = FLOOR_DATE.search(raw)
        if m:
            dated.append((r["rule"], date(int(m.group(1)), int(m.group(2)),
                                          int(m.group(3)))))
        elif raw.lower().startswith("never"):
            never.append(r["rule"])
        else:
            # `unknown - predates recording` is a sanctioned value, and an
            # angle-bracket prompt is an unfilled template row. Neither can be
            # measured, and the template says guessing a date here destroys
            # the only input the review has - so neither is guessed at.
            unusable.append((r["rule"], raw))
    distinct = sorted({d for _, d in dated})
    if len(distinct) < 2:
        return {"rows": len(rows), "dated": dated, "never": never,
                "unusable": unusable, "exempt": exempt, "window_days": None,
                "interval": None, "stale": [], "distinct": len(distinct)}
    span = (distinct[-1] - distinct[0]).days
    interval = span / (len(distinct) - 1)
    window = int(round(window_stages * interval))
    stale = sorted(((rule, (today - d).days) for rule, d in dated
                    if (today - d).days > window),
                   key=lambda t: -t[1])
    return {"rows": len(rows), "dated": dated, "never": never,
            "unusable": unusable, "exempt": exempt, "window_days": window,
            "interval": interval, "stale": stale, "distinct": len(distinct)}


def judge_floor_staleness(rep: dict, window_stages: int, source) -> Finding:
    """Every run prints the arithmetic, green or red. A threshold nobody can
    reconstruct is a threshold nobody will argue with, and an anti-ratchet
    check that cannot be argued with is the ratchet."""
    if source is None:
        # n/a, NOT a red. Whether the floor is installed at all is
        # `doctor:l1-documents`' question and it asks it by name; this check
        # ages a floor that exists. A second check reporting the same absence
        # is a second red for one fact, and a tool that reds twice for one
        # reason is a tool people learn to skim.
        return Finding(
            NA, "no FAILURE-FLOOR.md in this tree",
            "      Module 04 is not installed here, so there is no floor to "
            "age. This is n/a, not green: nothing here knows whether any rule "
            "in this project is quiet. `doctor:l1-documents` is the check "
            "that asks whether the ledgers are installed at all.")
    if not rep["rows"]:
        return Finding(
            ATTENTION, "the failure floor has no rules in it",
            f"      Read {source}, found no table rows. A floor with no rows "
            f"passes every check by having nothing to check.",
            "Write down the rules this project actually holds, with the layer "
            "that enforces each - `modules/04-ledgers/README.md`.")
    arithmetic = (
        f"      ARITHMETIC: {rep['distinct']} distinct firing date(s) in "
        f"{source}"
        + ("" if rep["window_days"] is None else
           f"; mean interval between them {rep['interval']:.1f} days; window "
           f"= DEMOTION_REVIEW_STAGES ({window_stages}) x that interval = "
           f"{rep['window_days']} days"))
    unmeasured = ""
    if rep["unusable"]:
        unmeasured += (f"\n      NOT MEASURED ({len(rep['unusable'])} row(s) "
                       f"with no usable date): "
                       + ", ".join(f"{r} ({v!r})"
                                   for r, v in rep["unusable"][:5]))
    if rep["never"]:
        unmeasured += (f"\n      NOT MEASURED ({len(rep['never'])} row(s) that "
                       f"have never fired): " + ", ".join(rep["never"][:5])
                       + ". A rule that has never fired cannot be dated, so "
                       "its quiet period is not computable here - it is still "
                       "the demotion review's business.")
    if rep["exempt"]:
        unmeasured += (f"\n      NOT JUDGED ({len(rep['exempt'])} row(s) "
                       f"already carrying a final disposition): "
                       + ", ".join(rep["exempt"][:5]))
    if rep["window_days"] is None:
        return Finding(
            OK, f"{rep['rows']} floor rule(s) read; staleness NOT COMPUTABLE",
            f"{arithmetic}\n"
            f"      Two distinct firing dates are the minimum this project "
            f"needs before its own review interval can be derived, and there "
            f"{'is' if rep['distinct'] == 1 else 'are'} {rep['distinct']}. "
            f"This is UNKNOWN, not clean.{unmeasured}")
    if rep["stale"]:
        shown = "\n".join(f"      {rule}: last fired {days} days ago"
                          for rule, days in rep["stale"][:8])
        more = ("" if len(rep["stale"]) <= 8 else
                f"\n      ...and {len(rep['stale']) - 8} more")
        return Finding(
            ATTENTION, f"{len(rep['stale'])} floor rule(s) are overdue for a "
                       f"demotion disposition",
            f"{shown}{more}\n{arithmetic}{unmeasured}",
            "At this phase gate, give each one RETIRE, DEMOTE a layer, or "
            "RE-AFFIRM with the reason it is quiet - a tripwire is quiet "
            "because nothing crossed it, and that is what re-affirm is for. "
            "Then update its Last fired or its Status. Zero demotions across "
            "a whole phase is itself a finding.")
    return Finding(
        OK, f"no floor rule is past its demotion window",
        f"{arithmetic}\n      Every dated rule fired inside the window, so "
        f"nothing is waiting on a disposition. This says the review is not "
        f"OVERDUE; it does not say the review happened.{unmeasured}")


# ---- check 12: the binding digest, and the anti-ratchet on its size ------
# THE CEILING, DERIVED. The rules file is the one text a harness loads into
# every window; the checkpoint is the one carrier between sessions. Together
# they are what a session reads before it does anything, and their cost is
# paid on every session rather than once. The module-01 template states the
# rule three times ("keep it SHORT", "delete every rule you cannot yet
# enforce", "each line traceable to something that went wrong") and nothing
# measured it.
#
# The four-step derivation is the one `TOKEN-LEDGER.md` gives for the cost
# ratio and `KNOWN-ISSUES.md` uses for the escape-rate ceiling.
#
# STEP 1 - the observations, measured rather than estimated. The kit's shipped
# rules template renders to 251 lines (287 in the file, minus the 36-line
# header block the template tells the adopter to delete). The checkpoint's
# shape contract carries a MEASURED norm of about 90 lines, published in
# CONTEXT-ARCHITECTURE section 3, BLUEPRINT section 7 and the rules template
# itself. The shipped binding digest is therefore 251 + 90 = 341 lines.
# STEP 2 - 341 x 1.15 = 392.15, rounded up to the nearest 25: 400.
# RE-DERIVED FIVE TIMES NOW - TWICE IN ROUND 24, AGAIN IN ROUND 25, AGAIN IN
# ROUND 26, AGAIN IN ROUND 32 - WHICH IS THE BINDING WORKING rather than a
# number being chased.
# The history, because each re-derivation is evidence the guard fires:
#   round 24  the declined-oracle clause (WHEN THE LOOP ENDS, rule 7) grew the
#             template 191 -> 206 rendered lines, and that clause's own fix
#             pass grew it again to 209. Ceiling landed on 350 both times.
#   round 25  rule 8 itself, the self-coverage rule, tripped the guard on
#             arrival exactly as its own text predicts: 209 -> 219, ceiling
#             re-derived 350 -> 375.
#   round 26  rule 8's measured-instance citation was rewritten to name its
#             source and the real check id: 219 -> 224. Ceiling re-derived and
#             UNCHANGED at 375, because (224 + 90) x 1.15 = 361.1 still rounds
#             up into the same 25-line bucket.
#   round 32  the SHIP REQUIREMENTS section - a forced red, a recorded seen-red
#             date and a lineage row before a claim-bearing component ships -
#             plus its stage-close step grew the template 224 -> 251, and the
#             ceiling was re-derived 375 -> 400. The guard fired on the round
#             that wrote the section, in the run that was verifying it.
# Measured, not assumed: run with a stale constant the selftest fails naming
# both numbers (`got 251, want 224` the last time), which is exactly what the
# binding below promises. The ceiling is re-derived from each new measurement
# rather than the assertion relaxed, and it is allowed to stay where it is
# when the arithmetic puts it there.
# STEP 3 - the backwards sanity check, and one half of it is evidence while
# the other is arithmetic. The half that carries no information: at 400 the
# kit's own shipped pair passes, which is true by construction because step 2
# set the ceiling above it. The half that does: the shipped pair sits 59 lines
# (14.8%) below the line rather than at it, so ordinary project-specific
# additions fit, while a rules file that has merely DOUBLED from the shipped
# template (502 lines) breaches it on its own with no checkpoint at all. That
# is where this threshold actually sits.
# STEP 4 - n = 2 observations, one project, one maintainer's measurement. LOW
# confidence, and lower than the escape-rate ceiling's. Re-derive it from your
# own first three stages; a ceiling inherited from somebody else's project is
# the mistake `TOKEN-LEDGER.md` exists to prevent.
#
# THE FIRST OBSERVATION IS BOUND TO THE FILE IT CAME FROM. `--selftest`
# measures `modules/01-governance/CLAUDE.md.template` and requires it to still
# be DIGEST_SHIPPED_RULES_LINES rendered lines; if the template grows, the
# derivation's input has moved and the selftest goes red naming both numbers,
# rather than the ceiling silently ceasing to mean what this comment says it
# means. The numbers in this comment are part of the same contract: when the
# constant below moves, STEP 1, STEP 2 and STEP 3 are re-stated with it.
DIGEST_SHIPPED_RULES_LINES = 251
DIGEST_CHECKPOINT_NORM_LINES = 90
DIGEST_CEILING_LINES = 400


def rendered_template_lines(text: str) -> int:
    """The line count of a template AFTER the adopter deletes its header
    block, which every template's last header line instructs. Pure."""
    lines = (text or "").splitlines()
    if lines and lines[0].lstrip().startswith("<!--"):
        for i, line in enumerate(lines):
            if "-->" in line:
                return len(lines) - (i + 1)
    return len(lines)


def judge_binding_digest(parts: list, ceiling: int) -> Finding:
    """`parts` is [(label, line_count)] - the rules file, and the newest
    checkpoint when there is one.

    WHAT THIS DOES NOT MEASURE: whether any of those lines is worth its place.
    A digest of 300 excellent lines and a digest of 300 lines of noise are the
    same number here. The rule this promotes is about COST, which is
    countable; the rule about value is the one line 4 of the template's HOW TO
    USE IT block states, and it stays prose."""
    if not parts:
        # n/a for the same reason as the floor's absence above: this check
        # SIZES a digest, and whether one exists is module 01's question.
        return Finding(
            NA, "no rules file and no checkpoint in this tree",
            "      There is no text here that every session is guaranteed to "
            "read, so there is nothing to size. This is n/a, not green - a "
            "project with no binding digest has not passed this check, it has "
            "sidestepped it. Module 01 installs the rules file; the first "
            "checkpoint is written at a stage close.")
    total = sum(n for _, n in parts)
    breakdown = " + ".join(f"{lab} {n}" for lab, n in parts)
    arithmetic = (
        f"      ARITHMETIC: {breakdown} = {total} lines, against a ceiling of "
        f"{ceiling} derived from the kit's own shipped pair "
        f"({DIGEST_SHIPPED_RULES_LINES} rendered template lines + "
        f"{DIGEST_CHECKPOINT_NORM_LINES} measured checkpoint norm = "
        f"{DIGEST_SHIPPED_RULES_LINES + DIGEST_CHECKPOINT_NORM_LINES}, x1.15, "
        f"rounded up to the nearest 25). n = 2 observations: LOW confidence, "
        f"and this is a number to re-derive from your own stages.")
    if total > ceiling:
        return Finding(
            ATTENTION, f"the binding digest is {total} lines, over the "
                       f"{ceiling}-line ceiling",
            f"{arithmetic}\n"
            f"      This text is re-read at the top of every session and "
            f"competes for attention with the work. A rules file people learn "
            f"to skim enforces nothing while costing everyone the tokens.",
            "Delete rules you cannot yet enforce or do not yet believe; move "
            "a rule you are not ready to bind into the failure floor as a "
            "proposal; move resume-critical detail out of the rules file and "
            "into the checkpoint. Or raise the ceiling - deliberately, in a "
            "reviewed commit, with your own arithmetic beside it.")
    return Finding(
        OK, f"the binding digest is {total} lines, under {ceiling}",
        f"{arithmetic}\n      Counted, not judged: this says the digest is "
        f"affordable, not that any line in it has earned its place.")


# ==========================================================================
# THE LEVEL-1 LAYER - seven checks over documents, and no gate anywhere
# ==========================================================================
# `LEVEL-1.md` is the kit's documents-only entry: four ledgers, a collaboration
# profile, the governance rules as prose, and no `.claude/settings.json`, no
# hook and no verify runner. Nothing in the default diagnosis above applies to
# that tree - it reads a runner that is not there and a settings file that was
# never written - so `--level1` runs a separate set that reads only what Level 1
# installs.
#
# WHAT THESE CHECKS ARE, EXACTLY. They judge the SHAPE of documents: present at
# the paths this repository names, rendered (no surviving `{{SLOT}}`, no
# template header block, no shipped placeholder path), committed to git, and
# carrying the two answers Level 1 asks for - the KNOWLEDGE_DIR decision and
# the seed interview's status. They judge no CONTENT: a ledger with a correct
# header and no rows passes every one of them. That limit is printed on every
# green run rather than left to this comment, because a reader who believes a
# green line means more than it does is the failure this whole kit exists to
# prevent.
#
# THE VERDICT WORD IS STILL NOT `PASS`. `verify.py` runs gates; this runs none.
# Level 1 reports HEALTHY over documents, and the summary states what it does
# not certify and what removing it costs.
L1_LEDGERS = ("JUDGMENT-LEDGER.md", "FAILURE-FLOOR.md", "LESSONS.md",
              "TOKEN-LEDGER.md")
L1_PROFILE = "collaboration-profile.md"
L1_RULES = "CLAUDE.md"

# ==========================================================================
# PRESENT IS NOT ADOPTED - the module-01 fingerprints
# ==========================================================================
# Round 24's acceptance run adopted the kit into a repository that already had
# a 30-line `CLAUDE.md` of its own. The adoption never opened it for writing.
# This check reported it as `CLAUDE.md (module 01 as prose)`, the green line
# certified six documents where five had been installed, and the REMOVAL COST
# line told a reader to delete a file the adoption never wrote. On an existing
# project, presence-at-a-path and adoption are different facts.
#
# THE MECHANISM, and it is a choice with a cost: the kit's own TEMPLATE
# FINGERPRINTS. These strings are section headings and rule sentences of
# `modules/01-governance/CLAUDE.md.template` - seven headings and one rule
# sentence, which is why the reader-facing lines call them FINGERPRINTS and
# not "section headings" (round 24 review, m6) - that carry no {{SLOT}}, so they
# survive rendering unchanged; a file carrying at least MIN of them is module
# 01 as prose, however it got there. Held as literals because an adopted tree
# has no `modules/` directory to read, and held to the shipped template by a
# `--selftest` cross-check that runs whenever this tool sits in a kit checkout
# - the same arrangement `L1_LEDGERS` ships under.
#
# WHY NOT GIT PROVENANCE: the honest question is "did this adoption write this
# file", and git cannot answer it at the moment the check runs. Step 5 runs
# BEFORE the commit, so an adopted rules file is untracked or modified and a
# pre-existing one is clean - which would report the two backwards - and after
# the commit a MERGED file (the route `EXISTING-PROJECT.md` prescribes for a
# host that already has rules) is indistinguishable from an overwritten one by
# commit history alone. Fingerprints answer the question the reader is asking.
#
# THE RESIDUAL, STATED IN BOTH DIRECTIONS:
#   - An adoption that deleted or rewrote nearly every kit heading - which the
#     template's own instruction 2 invites - reads as PRE-EXISTING. The check
#     then understates what was installed. WHAT THE OUTPUT MAY THEREFORE SAY
#     (round 24 review, M3): the printed lines claim the COUNT and nothing
#     about provenance. This mechanism cannot establish that a file is the
#     owner's own, that it is untouched, or that this level did not install
#     it; it establishes that the file carries fewer than MIN of the kit's
#     fingerprints. Both branches print the two integers they used, and the
#     not-adopted line names the reworded-adoption case out loud.
#   - A host file that happens to contain two of these headings reads as
#     ADOPTED. It would have to contain the kit's own section titles to do it.
#   - A MERGED file reads as ADOPTED, which is correct: module 01's prose is
#     in it. Removing it is then a revert rather than a delete, which is what
#     the REMOVAL COST line already says of a merged document.
L1_RULES_FINGERPRINTS = (
    "MODEL TIERING",
    "HALT authority",
    "WHEN THE LOOP ENDS",
    "Reviewers onboard SPEC-SIDE",
    "ORACLE MANUFACTURE",
    "STRUCTURE OVER SENTENCES",
    "Stage close checklist",
    "Certification is a property of a",
)
# Two, not one: one heading is a coincidence a host document could reach on its
# own vocabulary; two of the kit's own section titles in one file is the kit's
# prose. Stated as a number here so it can be argued with.
L1_RULES_MIN_FINGERPRINTS = 2

# The template header blocks. A document still carrying one is a document
# nobody read to the end: each block's last line tells the adopter to delete it.
L1_HEADER_MARKERS = ("SKELETON - copy to", "Delete this block on adoption",
                     "DELETE THIS COMMENT BLOCK", "TEMPLATE - the living",
                     "Delete this comment on adoption")

# Shipped values that survived into a rendered document. THE PATTERN IS NOT
# DEFINED HERE: it is `RENDERED_PLACEHOLDER` in the shipped
# `hook_model_gate.py`, imported by `placeholder_rule()` and passed in, because
# `tools/adoption_smoke.py` phase 9 asks the same question about the same class
# of file and two narrower copies of one rule is this kit's oldest defect
# class. The first version of this check carried a one-element list of its own
# and reported HEALTHY over six documents titled `Example Project`.

# THE ONE EXEMPTION, BY NAME. QUICKSTART Step 7 allows exactly one shipped
# value to survive adoption: RATIO_CEILING, which ships as
# `derive-from-your-own-data` and lands in TOKEN-LEDGER.md. The kit's advice is
# to derive that number from your own first stages rather than adopt someone
# else's, so flagging it would be telling the adopter to violate the document
# they are following. Held as a constant so --selftest can assert the exemption
# instead of trusting that nobody added the string to the list above.
L1_ALLOWED_SHIPPED = ("RATIO_CEILING", "derive-from-your-own-data")

L1_SLOT = re.compile(r"\{\{[A-Z0-9_]+\}\}")

# QUOTED TEXT IS NOT AN UNFILLED SLOT. A document that WRITES ABOUT the kit -
# a judgment ledger recording that a check was forced red over `Example
# Project`, a lessons entry quoting a shipped tier name - carries those strings
# as its subject, not as a fill-in nobody made. The first version of this check
# could not tell the two apart, and the repository it fired on hardest was the
# kit's own program repo: a red that could only be cleared by editing a
# truthful record of what was fixed and when.
#
# Three exemptions, all VISIBLE - the check reports how many lines each one
# took out of the scan, on every run, so a document cannot go quietly green by
# fencing itself.
#   * fenced code blocks (``` or ~~~) - example output is example output;
#   * inline code spans (`like this`) - the ordinary way prose quotes a value;
#   * any line carrying the marker below, for a table cell or a sentence where
#     backticks would be wrong.
# THE EXEMPTIONS APPLY TO THE SHIPPED-VALUE SCAN ONLY. An unsubstituted
# `{{SLOT}}` and a surviving template header block are defects wherever they
# appear, including inside a fence: a document quoting a slot is quoting
# something the reader can also see was never filled in.
L1_QUOTE_MARKER = "oar:quotes-example"
L1_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
L1_CODE_SPAN = re.compile(r"`[^`\n]*`")

# The profile's STATUS block: `INTERVIEW:  not yet held | scheduled <date>
# confirmed by <who/where> | held <date>`. The shipped line is a MENU, and the
# three states are the three answers. An owner-blocked interview - the junior's
# normal end state, because a junior is never the owner - is `not yet held` or
# a CONFIRMED `scheduled <date>`, and both are green here.
#
# WHY `scheduled` CARRIES A CONFIRMATION AND THE OTHER TWO DO NOT. A date is
# the one field on this line that a model or a hurried adopter can supply from
# nothing: "scheduled 2026-08-22" parses, reads as diligence, and is
# indistinguishable from a real calendar entry. That is exactly what happened
# on this kit's own dogfood adoption - a lane invented the date, and the
# coordinator's ruling was to remove it and record `not yet held`. So the
# scheduled state has to say where the date came from. `not yet held` needs no
# confirmation because it claims nothing, and `held <date>` is a claim about
# the past that the profile's own answers evidence.
L1_INTERVIEW = re.compile(r"^\s*INTERVIEW:\s*(.+?)\s*$", re.M)
L1_INTERVIEW_STATES = re.compile(
    r"^(not yet held|scheduled\s+\S.*|held\s+\S.*)$", re.I)
# `confirmed <something>` / `confirmed by <someone>`, anywhere after the date.
L1_INTERVIEW_CONFIRMED = re.compile(r"\bconfirmed\b\s*(by\b)?\s*\S+", re.I)


def scannable_for_shipped(text: str):
    """(the text the shipped-value scan may read, exemption counts). Pure.

    Quoted regions are blanked rather than deleted so that nothing shifts:
    this function's only job is to stop the shipped-value pattern matching
    text a document is QUOTING. See L1_QUOTE_MARKER above for why.

    The residual, and it is real: a defect hidden inside a fenced block is
    exempt too. A fenced block is displayed as literal example text rather
    than as the document's own assertion, which is why the exemption is
    defensible - and the counts are printed on every run so that a document
    which fenced half of itself is visible rather than merely green."""
    out, counts = [], {"fenced": 0, "spans": 0, "marked": 0}
    in_fence = False
    for line in (text or "").splitlines():
        if L1_FENCE.match(line):
            in_fence = not in_fence
            counts["fenced"] += 1
            out.append("")
            continue
        if in_fence:
            counts["fenced"] += 1
            out.append("")
            continue
        if L1_QUOTE_MARKER in line:
            counts["marked"] += 1
            out.append("")
            continue
        n = len(L1_CODE_SPAN.findall(line))
        if n:
            counts["spans"] += n
            line = L1_CODE_SPAN.sub("", line)
        out.append(line)
    return "\n".join(out), counts


def l1_render_problems(rel: str, text: str, shipped_pattern=None) -> list:
    """Every rendering defect in one Level-1 document. Pure: text and the rule
    in, problems out, so --selftest reconstructs each defect from a literal
    rather than from a file it also wrote.

    Three defect kinds, all measured on real adoptions: a slot nobody
    substituted, a header block nobody deleted, and a shipped example value
    that was copied through instead of being replaced.

    `shipped_pattern` is the kit's `RENDERED_PLACEHOLDER`, or None when this
    tool is running outside a kit checkout and could not import it. None means
    the third scan does not run; it never means a narrower one silently does.

    THE ONE EXEMPTION IS APPLIED HERE, BY NAME. The shared pattern matches
    `derive-from-your-own-data`, and QUICKSTART Step 7 tells the adopter to
    keep exactly that value in TOKEN-LEDGER.md until they have three stages of
    their own numbers. Flagging it would be telling the reader to violate the
    document they are following.

    THE QUOTING EXEMPTIONS are applied to the shipped-value scan only, by
    `scannable_for_shipped()`. The slot and header scans below read the whole
    document."""
    out = []
    for slot in sorted(set(L1_SLOT.findall(text))):
        out.append(f"{rel}: {slot} was never substituted")
    for marker in L1_HEADER_MARKERS:
        if marker in text:
            out.append(f"{rel}: the template header block is still there "
                       f"({marker!r})")
    if shipped_pattern is not None:
        scannable, _ = scannable_for_shipped(text)
        hits = [h for h in dict.fromkeys(shipped_pattern.findall(scannable))
                if h != L1_ALLOWED_SHIPPED[1]]
        for hit in hits:
            out.append(f"{rel}: the shipped example value {hit!r} is in the "
                       f"rendered document - the fill-in behind it was never "
                       f"made")
    return out


def level1_hint(has_runner: bool, has_hook: bool, l1_docs: list) -> str:
    """The wrong-mode pointer, as a pure function of three facts the default
    diagnosis has already established. Empty string when the tree is not a
    Level-1 adoption.

    WHY IT EXISTS. The default set reads a verify runner, a settings file and a
    hook. A Level-1 tree has none of them by design, so an adopter who runs the
    obvious command gets red lines about files they were told not to install -
    which is a tool teaching its reader to ignore it. The three facts are
    already computed by the checks above; nothing new is probed."""
    if has_runner or has_hook or not l1_docs:
        return ""
    return (f"{len(l1_docs)} of the documents `LEVEL-1.md` installs are here "
            f"({', '.join(l1_docs)}), and this tree has no verify runner and "
            f"no wired hook. The checks above are the Level-2/3 set, reporting "
            f"on files that level deliberately does not install. Run "
            f"`--level1` for the checks that apply to this tree.")


def rules_file_provenance(text):
    """(is_adopted, [fingerprints found]) for a host rules file. Pure.

    `text` None means there is no such file; the answer is then (None, []).
    See the L1_RULES_FINGERPRINTS block for the mechanism and its residual."""
    if text is None:
        return None, []
    hits = [f for f in L1_RULES_FINGERPRINTS if f in text]
    return len(hits) >= L1_RULES_MIN_FINGERPRINTS, hits


def judge_l1_documents(required: list, optional: list) -> Finding:
    """`required` is [(label, path_or_None)]. `optional` is
    [(label, path_or_None, adopted_or_None, fingerprints)] - `adopted` is None
    when the file is absent, True when it carries module 01's prose, and False
    when a file of that name is there but is the host's own.

    PRESENT IS NOT ADOPTED. A document that is simply there is not a document
    this adoption installed, and on an existing project the difference decides
    what the removal cost may name."""
    optional = [(o + (None, []))[:4] if len(o) < 4 else o for o in optional]
    missing = [lab for lab, p in required if p is None]
    absent_opt = [lab for lab, p, a, _ in optional if p is None]
    host_own = [(lab, hits) for lab, p, a, hits in optional
                if p is not None and a is False]
    # THE ADOPTED BRANCH PRINTS ITS NUMBERS TOO (round 24 review, M4). The
    # decision that lets REMOVAL COST name a file is the one a reader most
    # needs the basis of, and before this it was the only branch that printed
    # none. Both branches now carry the same two integers.
    found = ([lab for lab, p in required if p is not None]
             + [f"{lab} — {len(h)} of {len(L1_RULES_FINGERPRINTS)} "
                f"fingerprints found; {L1_RULES_MIN_FINGERPRINTS} is the floor"
                for lab, p, a, h in optional if p is not None and a])
    tail = ("" if not absent_opt else
            f"\n      NOT TAKEN (optional at this level): "
            f"{', '.join(absent_opt)}. Level 1 recommends the governance "
            f"rules as prose; it does not require them.")
    for lab, hits in host_own:
        tail += (
            f"\n      PRESENT BUT NOT ADOPTED: {lab.split()[0]} carries too "
            f"little of module 01's prose to read as an adoption "
            f"({len(hits)} of {len(L1_RULES_FINGERPRINTS)} fingerprints found; "
            f"{L1_RULES_MIN_FINGERPRINTS} is the floor). It is "
            f"not counted as a Level-1 document and the removal cost below "
            f"does not name it — deleting it could remove rules that are the "
            f"owner's own. If you MEANT to adopt module 01 as prose over an "
            f"existing "
            f"rules file, the route is `EXISTING-PROJECT.md`: render, read the "
            f"diff, then merge by hand with the kit's rules as the base and "
            f"your existing rules preserved verbatim under a marked heading.")
    if missing:
        return Finding(
            ATTENTION, f"{len(missing)} Level-1 document(s) missing",
            f"      Missing: {', '.join(missing)}\n"
            f"      Found: {', '.join(found) or 'nothing'}{tail}",
            "Install them - `LEVEL-1.md` steps 3 and 4 - or point the doctor "
            "at the repository that has them with `--root <path>`.")
    return Finding(
        OK, f"{len(found)} Level-1 document(s) present",
        "      " + "\n      ".join(found) + tail)


def level1_summary_lines(n_scanned: int, commit_clause: str, rules_adopted,
                         rules_hits: list, outside_disp: list,
                         removal: list) -> list:
    """The lines a GREEN Level-1 run ends in: CERTIFIES, DOES NOT CERTIFY,
    REMOVAL COST, and the two conditional lines between them. Returned rather
    than printed so the SENTENCES can carry negative controls.

    ROUND 24's REVIEW, M10, IS WHY THIS IS A FUNCTION. F3's fix was tested
    where it computes (`rules_file_provenance`, `judge_l1_documents`) and not
    where it speaks, and four findings shipped at the two print sites this
    function now holds. A control that reads what the reader reads is the
    layer that was missing.

    `rules_adopted` is True, False or None (no such file). `removal` is the
    file list REMOVAL COST names. Colour is included because the caller prints
    these verbatim; assertions match on substrings."""
    out = [
        f"  {BOLD}CERTIFIES{RESET} — and only this: the "
        f"{n_scanned} document(s) listed above exist where this "
        f"repository names them, carry no unsubstituted {{{{SLOT}}}}, no "
        f"template header block and no shipped example value, "
        f"{commit_clause}, and record the KNOWLEDGE_DIR decision and the "
        f"seed interview's status."]
    if rules_adopted is False:
        # THE LINE ROUND 24's F3 EXISTS FOR, REWORDED BY ITS REVIEW (M3). A
        # reader following REMOVAL COST literally deletes what it names, so a
        # file this level may not have written is called out above that line.
        # What the sentence may claim is bounded by what the fingerprint count
        # can establish: a COUNT, never a provenance. "the owner's own",
        # "untouched" and "this level did not install it" were three claims
        # the mechanism cannot make, and on a trimmed adoption all three were
        # false about a file the level had installed.
        out.append(
            f"    NOT ADOPTED, AND NOT COUNTED ABOVE: host {L1_RULES} carries "
            f"fewer than {L1_RULES_MIN_FINGERPRINTS} of module 01's "
            f"{len(L1_RULES_FINGERPRINTS)} fingerprints "
            f"({len(rules_hits)} found), so this check reads it as a rules "
            f"file of your own, does not count it above, and the removal cost "
            f"below does not name it. THE LIMIT OF THAT READING: if module 01 "
            f"WAS adopted here and its headings were reworded, the count is "
            f"the same and this check cannot tell the two apart — you can, so "
            f"say which it is in your report.")
    if outside_disp:
        out.append(
            f"    NOT IN THAT COMMIT CLAIM: {', '.join(outside_disp)} — read "
            f"and rendering-checked, but outside this work tree, so its "
            f"commit state was not judged by anything here.")
    out.append(
        f"  {BOLD}DOES NOT CERTIFY{RESET}: any behaviour. No gate ran — "
        f"Level 1 installs none. Nothing enforces these rules, no agent is "
        f"checked against them, no hook fires, and the CONTENT of these "
        f"documents is not judged: a ledger with a correct header and no "
        f"rows passes every check above. `PASS` belongs to `verify.py`, "
        f"which Level 2 installs (`QUICKSTART.md`).")
    # THE CLOSING CLAUSE NAMES NO RULES FILE (round 24 review, m5). It used to
    # offer `CLAUDE.md` and `.gitignore` as "the usual two" merge targets, on
    # every run - including the run whose line above had just promised that
    # the removal cost does not name it. The merge case is stated generically;
    # a rules file that this level DID install is already in the list above.
    out.append(
        f"  {BOLD}REMOVAL COST{RESET}: {len(removal)} file(s) "
        f"in this repository — {', '.join(removal)}"
        + (f" — plus {len(outside_disp)} outside it" if outside_disp else "")
        + ". No settings file, no hook and no harness wiring were "
          "installed, so there is nothing merged into `.claude/` to unpick. "
          "Delete the files this line names and the level is gone — EXCEPT "
          "where you merged one of them into a file you already had "
          "(`.gitignore` is the usual case), which is a revert rather than a "
          "delete.")
    return out


def exemption_line(exempted) -> str:
    """The quoting exemptions, printed. Pure, and it prints NOTHING when no
    exemption fired, so an ordinary adoption's green line is unchanged.

    A silent exemption is an exemption nobody can audit: the whole reason this
    check may skip a region is that documents legitimately quote the kit, and
    the compensating control for 'legitimately' is that the reader is told how
    much was skipped and by which mechanism."""
    if not exempted:
        return ""
    parts = [(f"{exempted.get('fenced', 0)} line(s) inside fenced blocks"
              if exempted.get("fenced") else ""),
             (f"{exempted.get('spans', 0)} inline code span(s)"
              if exempted.get("spans") else ""),
             (f"{exempted.get('marked', 0)} line(s) marked "
              f"`{L1_QUOTE_MARKER}`" if exempted.get("marked") else "")]
    parts = [p for p in parts if p]
    if not parts:
        return ""
    return ("\n      QUOTED TEXT NOT SCANNED for shipped example values: "
            + ", ".join(parts) + ". A document may quote the kit; this is how "
            "much of it was taken out of that one scan. Slots and template "
            "headers were still scanned everywhere.")


def judge_l1_rendered(problems: list, n_scanned: int,
                      shipped_scanned: bool = True,
                      exempted=None) -> Finding:
    """`shipped_scanned` is False when the shared shipped-value rule could not
    be imported. The finding then says so on its own line: a green that covers
    two of three defect kinds must not read like a green that covers three.

    `exempted` is the quoting-exemption tally from `scannable_for_shipped()`,
    reported on every run for the same reason."""
    narrowed = ("" if shipped_scanned else
                "\n      SCAN NARROWED: `hook_model_gate.py` was not found "
                "beside this tool, so shipped example values (`Example "
                "Project`, the `your-...` tier names, `/abs/path/to/...`) "
                "were NOT scanned for. Run this tool from a kit checkout to "
                "get the full scan.")
    narrowed += exemption_line(exempted)
    if problems:
        shown = "\n".join(f"      {p}" for p in problems[:12])
        more = ("" if len(problems) <= 12 else
                f"\n      ...and {len(problems) - 12} more")
        return Finding(
            ATTENTION, f"{len(problems)} rendering defect(s) in "
                       f"{n_scanned} document(s)",
            f"{shown}{more}{narrowed}",
            f"Substitute the slot or the shipped example value, or delete the "
            f"header block the template tells you to delete - `LEVEL-1.md` "
            f"step 3. If the document is QUOTING the kit rather than carrying "
            f"an unfilled slot - a ledger row recording what a check was "
            f"forced red over, say - put the value in backticks or a fenced "
            f"block, or add `{L1_QUOTE_MARKER}` to that line; the check then "
            f"reports how many lines it skipped instead of failing over a "
            f"truthful record.")
    return Finding(
        OK, f"{n_scanned} document(s) fully rendered",
        f"      No surviving slot, no template header block, and no shipped "
        f"example value - the `your-...` tier names, `/abs/path/to/...`, "
        f"`Example Project` and the rest of the families the kit's shared "
        f"rule carries. One shipped value is allowed through by name: "
        f"{L1_ALLOWED_SHIPPED[0]} as `{L1_ALLOWED_SHIPPED[1]}`, which "
        f"QUICKSTART Step 7 tells you to keep until you have three stages of "
        f"your own numbers.{narrowed}")


def judge_l1_committed(git_ok: bool, untracked: list, dirty: list) -> Finding:
    """git_ok is False when the command failed or the tree is not a repository.
    A failed command's silence is not a clean tree - the same trap the judges
    gate was built around."""
    if not git_ok:
        return Finding(
            ATTENTION, "git could not be asked about these documents",
            "      A failed git command returns empty output, which is "
            "indistinguishable from a clean tree. Nothing here is known.",
            "Run the doctor inside the work tree, or `--root <repository>`; "
            "`git init` if this is not a repository yet.")
    if untracked:
        return Finding(
            ATTENTION, f"{len(untracked)} Level-1 document(s) not committed",
            "      Untracked: " + ", ".join(untracked) + "\n"
            "      An untracked document is not adopted: it is not on any "
            "diff, no reviewer sees it change, and it disappears with the "
            "working copy.",
            "Commit them - `LEVEL-1.md` step 6 names the files.")
    if dirty:
        return Finding(
            ATTENTION, f"{len(dirty)} Level-1 document(s) have uncommitted "
                       f"changes",
            "      Dirty: " + ", ".join(dirty),
            "Commit the change, or revert it - `LEVEL-1.md` step 6.")
    return Finding(OK, "every Level-1 document is committed",
                   "      Tracked by git and identical to the committed "
                   "version, so what this check read is what a reader of the "
                   "repository gets.")


def judge_l1_knowledge_dir(raw, shipped_placeholder: bool, exists) -> Finding:
    """`raw` is the KNOWLEDGE_DIR value as configured, or None when the key is
    absent. `exists` is whether the directory it names is there, or None when
    the question does not arise.

    NONE IS A DECISION HERE, and it is the one place in this kit where that
    word is not simply UNSET. `kit.config.example` says so: set KNOWLEDGE_DIR
    to NONE when you have no knowledge base outside the repository, and
    substitute a repo path at the two sites that interpolate the slot. The
    shared `is_placeholder()` rule reads NONE as unset - correct for every
    other key - so this check asks the NONE question first and by name."""
    if raw is None or not str(raw).strip():
        return Finding(
            ATTENTION, "the KNOWLEDGE_DIR decision is not recorded",
            "      Level 1 asks for two decisions and this is the first: "
            "where durable knowledge lives outside this repository. The "
            "templates interpolate it unconditionally, so an unmade decision "
            "becomes a source-of-truth sentence pointing at nothing.",
            "Set KNOWLEDGE_DIR in `kit.config` (a repo path such as `docs`) "
            "or in `kit.config.local` (an absolute path) - `LEVEL-1.md` "
            "step 1.")
    val = str(raw).strip()
    if val.upper() == "NONE":
        return Finding(
            OK, "KNOWLEDGE_DIR = NONE - decided",
            "      No knowledge base outside the repository, so the repo "
            "copies ARE source of truth rather than mirrors. The two "
            "documents that interpolate the slot must name a repo path "
            "(`docs`), not the literal word NONE; `doctor:l1-rendered` is "
            "what would catch the placeholder if they did not.")
    if shipped_placeholder:
        return Finding(
            ATTENTION, f"KNOWLEDGE_DIR is still the shipped value {val!r}",
            "      That is the value the kit ships, not an answer. Every "
            "document rendered from it points at a directory nobody has.",
            "Replace it with your own path, or with NONE if you have no such "
            "place - `LEVEL-1.md` step 1.")
    if exists is False:
        return Finding(
            ATTENTION, f"KNOWLEDGE_DIR names {val!r}, which is not there",
            "      The decision is recorded and the directory is missing, so "
            "every source-of-truth reference resolves to nothing.",
            "Create the directory, or point the key at one that exists - "
            "`LEVEL-1.md` step 1.")
    return Finding(OK, f"KNOWLEDGE_DIR = {val}",
                   "      Recorded, and the directory is there.")


def judge_l1_interview(line) -> Finding:
    """`line` is the value after `INTERVIEW:` in the profile, or None when the
    profile carries no such line.

    AN OWNER-BLOCKED INTERVIEW IS GREEN, and that is a deliberate design
    decision rather than leniency. The person adopting the kit is often not the
    person whose judgment binds - a junior never is - and a check that goes red
    until someone else's calendar opens teaches its reader to ignore it. What
    is red is the UNANSWERED state: the shipped menu still sitting there, so
    nobody ever said which of the three is true.

    AN UNCONFIRMED SCHEDULE IS NOT GREEN, and that is not a retreat from the
    paragraph above. A date is the one field here that can be produced from
    nothing and still parse, so `scheduled 2026-08-22` reads exactly like a
    real calendar entry and exactly like an invention - which is what this
    kit's own dogfood adoption produced, a lane-invented date the coordinator
    then had to remove. The scheduled state therefore has to say where the
    date came from. The owner-blocked adopter is still green in one keystroke:
    `not yet held` claims nothing and needs no confirmation."""
    if line is None:
        return Finding(
            ATTENTION, "the profile records no interview status",
            "      `PROFILE-TEMPLATE.md` ships an `INTERVIEW:` line in its "
            "STATUS block. Without it a reader cannot tell a profile built "
            "from answers from one built from assumptions.",
            "Add the line back and state which of the three states is true - "
            "`LEVEL-1.md` step 4.")
    val = str(line).strip()
    if "|" in val or "<date>" in val:
        return Finding(
            ATTENTION, f"the interview status is still the shipped menu: "
                       f"{val!r}",
            "      The menu lists the three states; it is not an answer to "
            "which one holds.",
            "Replace the line with one state: `not yet held`, `scheduled "
            "<a real date>`, or `held <a real date>` - `LEVEL-1.md` step 4.")
    if not L1_INTERVIEW_STATES.match(val):
        return Finding(
            ATTENTION, f"the interview status {val!r} is not one of the three "
                       f"states",
            "      The three the template defines are `not yet held`, "
            "`scheduled <date>` and `held <date>`. A fourth wording is not "
            "readable by anyone but its author.",
            "Rewrite it as one of the three - `LEVEL-1.md` step 4.")
    if val.lower().startswith("held"):
        return Finding(OK, f"seed interview {val}",
                       "      The profile's answers came from the owner.")
    if (val.lower().startswith("scheduled")
            and not L1_INTERVIEW_CONFIRMED.search(val)):
        return Finding(
            ATTENTION, f"the scheduled interview is UNCONFIRMED: {val!r}",
            "      A date that parses is not a date somebody agreed to. This "
            "line says an interview is booked, and nothing in it says who "
            "booked it or where the date came from - so an invented date and "
            "a real calendar entry read identically here, and the profile "
            "then carries a schedule the owner has never seen.",
            "Either say where the date came from - `scheduled <date> "
            "confirmed by <who, or which calendar>` - or, if it was never "
            "agreed, write `not yet held`, which is green and claims nothing "
            "- `LEVEL-1.md` step 4.")
    return Finding(
        OK, f"seed interview: {val} - recorded honestly",
        "      A green end state, and it does not mean the profile is "
        "finished. Until the interview is held, every default in "
        "`DEFAULT-CONTRACT.md` is in force UNCONFIRMED and the betrayal line "
        "is unknown - the single riskiest gap on that page. Whoever owns the "
        "judgment has to answer five questions; the adopter usually is not "
        "that person.")


# ---- the brownfield pair: an existing config, and existing ledgers --------
# Both of these exist because the documents' install steps assume an EMPTY
# repository and the kit's own dogfood adoption was not one. Step 2 prints
# `cp kit.config.example ./kit.config`, which destroys a hand-written config;
# step 3 installs four ledgers at fixed names beside whatever ledgers the
# repository already had. Neither loss is visible afterwards, so neither is
# a sentence's job.
def judge_l1_config_complete(missing: list, n_registered: int,
                             source) -> Finding:
    """`missing` is the keys `kit.config.example` registers that this
    repository's config (both halves) does not carry. `source` is where the
    example was read from, or None when it could not be found.

    THE POINT IS NOT TIDINESS. A key the config never carried renders as an
    unfilled slot in whatever document interpolates it, and the obvious
    remedy - re-copy the example over the config - is the one that destroys
    the answers already in the file. So the missing keys are named, and the
    destructive remedy is named as destructive, in the same red."""
    if source is None:
        return Finding(
            ATTENTION, "the shipped config registry could not be read",
            "      `kit.config.example` is the list of every key the "
            "templates interpolate, and this tool could not find it. Nothing "
            "here knows whether this repository's config is complete: this "
            "is UNKNOWN, not clean.",
            "Run this tool from a kit checkout, or point `--root` at a tree "
            "beside one.")
    if missing:
        shown = ", ".join(missing[:14])
        more = "" if len(missing) <= 14 else f" ...and {len(missing) - 14} more"
        return Finding(
            ATTENTION, f"{len(missing)} config key(s) the templates use are "
                       f"not in this repository's config",
            f"      Missing: {shown}{more}\n"
            f"      Read from {source} ({n_registered} keys registered). "
            f"Every template interpolates these unconditionally, so a key "
            f"that is absent here becomes an unfilled slot in a rendered "
            f"document - or, worse, a rendered sentence pointing at nothing.",
            "APPEND the missing keys to your `kit.config` at their shipped "
            "values. Do NOT copy `kit.config.example` over an existing "
            "`kit.config`: `cp` overwrites without asking on every shell the "
            "documents name, and it destroys the answers already in that "
            "file - `LEVEL-1.md` step 2.")
    return Finding(
        OK, f"the config carries every key the templates use "
            f"({n_registered} registered)",
        f"      Checked against {source}. This says the keys are PRESENT; "
        f"whether their values are answers rather than shipped examples is "
        f"`doctor:l1-rendered`'s question, on the documents they render into.")


def normalised_ledger_stem(name: str) -> str:
    """A ledger filename reduced to what a reader would call it. Pure.

    `TOKEN_LEDGER.md`, `TOKEN-LEDGER.md` and `token ledger.md` are one name
    wearing three spellings, and a check that compares filenames literally
    sees three different files."""
    stem = re.sub(r"\.md$", "", (name or "").strip(), flags=re.I)
    return re.sub(r"[^A-Z0-9]", "", stem.upper())


def l1_ledger_collisions(present: list) -> list:
    """[(the file that was already there, the kit ledger it collides with)].
    Pure: filenames in, collisions out.

    A COLLISION IS A CONTAINMENT, not just an equality. The measured case was
    `LESSONS-LEARNED.md` beside the kit's `LESSONS.md` and `TOKEN_LEDGER.md`
    beside `TOKEN-LEDGER.md`: two documents answering one question, one of
    them the repository's real history and the other the one the kit's checks
    read. The kit's stems are all seven characters or longer, so containment
    does not fire on incidental short words."""
    out = []
    for name in present:
        if name in L1_LEDGERS:
            continue                      # the kit's own file, at its own name
        stem = normalised_ledger_stem(name)
        if not stem:
            continue
        for kit_name in L1_LEDGERS:
            kit_stem = normalised_ledger_stem(kit_name)
            if stem == kit_stem or kit_stem in stem or stem in kit_stem:
                out.append((name, kit_name))
                break
    return out


def judge_l1_ledger_collision(collisions: list, where: str) -> Finding:
    """The kit's ledger filenames are fixed - `kit_doctor` hard-codes them and
    `LEDGERS_DIR` is the only thing an adopter can move - so on a repository
    that already keeps ledgers, installing them means one of three outcomes.
    The documents name none of them, and the checks green on two: install
    alongside, and overwrite. Only the reader can tell those apart afterwards,
    and only if somebody tells the reader they happened."""
    if not collisions:
        return Finding(
            OK, "no ledger name collides with a pre-existing one",
            f"      Every kit ledger in {where} is at the kit's name and "
            f"nothing else in that directory answers the same question under "
            f"a different spelling.")
    shown = "\n".join(f"      {a}  collides with the kit's  {b}"
                      for a, b in collisions[:8])
    more = ("" if len(collisions) <= 8 else
            f"\n      ...and {len(collisions) - 8} more")
    return Finding(
        ATTENTION, f"{len(collisions)} pre-existing ledger(s) collide with the "
                   f"kit's names",
        f"{shown}{more}\n"
        f"      Two documents answering one question is not a stable end "
        f"state: the kit's checks read the kit's name, and your history is in "
        f"the other file. Nothing here has been changed or lost - this is a "
        f"decision that was never put to anyone.",
        "Pick one and record it: RENAME the existing ledger onto the kit's "
        "name and carry its content forward; or FREEZE it as the record up to "
        "adoption and say so at the top of both files, with the kit's file "
        "the forward one; or move `LEDGERS_DIR` so the two sets do not share "
        "a directory. Whichever you pick, the repository's own README needs "
        "the same ruling - `LEVEL-1.md` step 3.")


# ==========================================================================
# THE CHECK TABLE
# Every id here has a row in checks-registry.json, and `expectation_lint.py`
# cross-checks the two lists BOTH WAYS. That cross-check is not bookkeeping:
# without it this file would have grown the kit's own named blind spot - a
# check that is invisible to the registry - by ten in a single commit.
# ==========================================================================
CHECKS = [
    ("doctor:version", "the kit version this tree was adopted from"),
    ("doctor:config", "kit.config found, and no load-bearing key left as an "
                      "example value"),
    ("doctor:judge-paths-exist", "every judged path exists under the root"),
    ("doctor:judge-paths-ignored", "no judged path is hidden from git by an "
                                   "ignore rule"),
    ("doctor:judge-paths-agree", "the hook's config and the runner name the "
                                 "same judged paths"),
    ("doctor:vacuous-gate", "no gate is incapable of failing"),
    ("doctor:dirty-paths", "what a blanket add would sweep up (names files; "
                           "stages nothing)"),
    ("doctor:hook-interpreter", "the hook's interpreter resolves on this host"),
    ("doctor:protected-case", "what the protected-path tripwire costs on this "
                              "filesystem"),
    ("doctor:cert-token", "what the cert-green token is, and what it is not"),
    ("doctor:floor-staleness", "no failure-floor rule is past its demotion "
                               "window (the anti-ratchet, with its "
                               "arithmetic)"),
    ("doctor:binding-digest", "the text every session must read is under a "
                              "derived line ceiling"),
    # ---- the --level1 set. These seven run INSTEAD of the twelve above, over
    # a tree that has documents and no runner, no hook and no settings file.
    ("doctor:l1-documents", "every document Level 1 installs is where this "
                            "repository names it"),
    ("doctor:l1-config-complete", "this repository's kit.config carries every "
                                  "key the templates interpolate"),
    ("doctor:l1-ledger-collision", "no pre-existing ledger answers the same "
                                   "question as a kit ledger under another "
                                   "name"),
    ("doctor:l1-rendered", "no surviving slot, template header or shipped "
                           "placeholder in those documents"),
    ("doctor:l1-committed", "those documents are tracked by git and have no "
                            "uncommitted change"),
    ("doctor:l1-knowledge-dir", "the KNOWLEDGE_DIR decision is recorded, and "
                                "names somewhere that exists"),
    ("doctor:l1-interview", "the profile states the seed interview's status "
                            "(owner-blocked is a green state)"),
]
# The ids that belong to `--level1`. Derived from the family prefix rather than
# hand-listed, so an eighth Level-1 check cannot be added to the table and left
# out of the run.
L1_CHECKS = [c for c, _ in CHECKS if c.startswith("doctor:l1-")]

# THE PROSE COUNTS, SUBSTITUTED RATHER THAN TYPED. A hand-maintained count in
# prose goes stale the first time a check lands - this kit's own recorded
# lesson, and the reason `.github/workflows/kit-ci.yml` dropped its count too.
# The module docstring and `--help` therefore carry `{N_FULL}` / `{N_L1}`
# sentinels and get the real numbers from the lists above. Guarded because
# `python -OO` strips docstrings and leaves `__doc__` as None.
N_FULL = len(CHECKS) - len(L1_CHECKS)
N_L1 = len(L1_CHECKS)
if __doc__:
    __doc__ = __doc__.replace("{N_FULL}", str(N_FULL)).replace("{N_L1}", str(N_L1))


# ==========================================================================
# THE RUNNING LAYER  (impure below this line)
# ==========================================================================
def read_pairs(path: Path, into: dict) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" in line:
            k, v = line.split("=", 1)
            into[k.strip()] = v.strip()


def find_config(root: Path, kit: Path):
    """The filesystem half of choose_config(). Returns (Path or None, notes)."""
    env = os.environ.get("KIT_CONFIG")
    env_is_file = False
    env_inside = False
    if env:
        try:
            env_is_file = Path(env).is_file()
        except OSError:
            env_is_file = False
        env_inside = env_is_file and path_inside(Path(env), kit)
    target = root / "kit.config"
    try:
        exists = target.is_file()
    except OSError:
        exists = False
    chosen, notes = choose_config(env, env_is_file, env_inside, target, exists)
    return (Path(chosen) if chosen else None), notes


def find_repo_root(start: Path):
    for d in [start, *start.parents]:
        if (d / ".git").exists():
            return d
    return None


def git_out(root: Path, *args, timeout=15):
    """(stdout, ok). A non-zero return code is NOT an answer - the runner
    shipped that defect once and printed PASS over a tree with no .git in it."""
    try:
        p = subprocess.run(["git", "-C", str(root), *args],
                           capture_output=True, text=True, timeout=timeout)
        return p.stdout, p.returncode == 0
    except Exception:
        return "", False


def git_excluded_paths(root: Path, rels: list):
    """(excluded subset, note). Reuses verify.py's module-level git_excluded()
    when the runner can be imported, because that function carries a
    hard-earned transport fix - NUL-separated records rather than
    newline-joined text, after the first version reached git with a carriage
    return on every path but the last on Windows and missed the defect it was
    written for. Reimplementing it here would have reimplemented the bug."""
    if not rels:
        return [], ""
    fn = getattr(RUNNER_MOD, "git_excluded", None) if RUNNER_MOD else None
    if callable(fn):
        try:
            return fn(root, rels)
        except Exception as e:
            return [], f"verify.py's git_excluded() raised {e!r}"
    try:
        p = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "-z", "--stdin"],
            input=b"".join(r.encode("utf-8") + b"\0" for r in rels),
            capture_output=True, timeout=15)
    except Exception as e:
        return [], f"git could not be run: {e!r}"
    if p.returncode not in (0, 1):
        err = " ".join((p.stderr or b"").decode("utf-8", "replace").split())
        return [], f"git check-ignore exited {p.returncode}: {err[:120]}"
    return [x.decode("utf-8", "replace")
            for x in (p.stdout or b"").split(b"\0") if x], ""


RUNNER_MOD = None


def import_runner(path: Path):
    """Import the verify runner as a module so its GATES table and constants
    can be read as data. Returns (module, note). A failure is a note, never a
    crash: the checks that need it then report ATTENTION naming the import
    error, which is more useful than a traceback and cannot be mistaken for a
    clean run."""
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location("_kit_verify", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, ""
    except Exception as e:
        return None, f"{path} could not be imported: {e!r}"


def filesystem_folds_case(root: Path):
    """True / False / None, for the volume `root` is actually on.

    PROBED, NOT INFERRED. `os.name == "nt"` is the tempting answer and it is
    wrong twice: a case-sensitive directory on NTFS and a case-sensitive APFS
    volume both exist, and this check's whole value is that it describes the
    host in front of you rather than the host in the general case.

    READ-ONLY. It flips the case of a file that is already there instead of
    creating one, because a tool that diagnoses a working tree must not write
    into it - the dirty-paths check two lines up would then be reporting a file
    this tool had just made.

    IT LOOKS ONE LEVEL DOWN when it has to. A top level holding only
    all-uppercase names (`LICENSE`, `README`, `VERSION`) offers nothing to flip,
    and the first version answered None there - reporting "could not probe" over
    an ordinary repository. One directory deeper is enough in practice and stays
    on the same volume, which is the thing being measured."""
    def probe_dir(d: Path):
        try:
            entries = sorted(os.listdir(d))
        except OSError:
            return None, []
        files = [n for n in entries
                 if n != n.upper() and (d / n).is_file()]
        subdirs = [d / n for n in entries if (d / n).is_dir()
                   and not n.startswith(".")]
        if not files:
            return None, subdirs
        try:
            return (d / files[0]).with_name(files[0].upper()).exists(), subdirs
        except (OSError, ValueError):
            return None, subdirs

    answer, subdirs = probe_dir(root)
    if answer is not None:
        return answer
    for sub in subdirs[:8]:
        answer, _ = probe_dir(sub)
        if answer is not None:
            return answer
    return None


def resolve_interpreter(tok: str):
    """A path to an executable, or None. `shutil.which` covers the PATH case,
    which is the one the Debian/Ubuntu `python` shim breaks; an absolute or
    relative path is checked directly."""
    if not tok:
        return None
    if os.sep in tok or "/" in tok:
        p = Path(tok)
        try:
            return p if p.is_file() else None
        except OSError:
            return None
    return shutil.which(tok)


def hook_commands(settings: Path) -> list:
    try:
        s = json.loads(settings.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for entry in (s.get("hooks") or {}).get("PreToolUse") or []:
        for h in entry.get("hooks") or []:
            cmd = str(h.get("command") or "").strip()
            if cmd:
                out.append(cmd)
    return out


def print_findings(findings: list) -> int:
    """Print one findings list in check-table order and return the number
    needing attention. Shared by the full diagnosis and `--level1`, so the two
    modes cannot drift into printing a red line differently."""
    order = {cid: i for i, (cid, _) in enumerate(CHECKS)}
    findings.sort(key=lambda kv: order.get(kv[0], 99))
    n_att = 0
    for cid, f in findings:
        colour = {OK: GREEN, ATTENTION: RED, NA: CYAN, INFO: YELLOW}[f.state]
        print(f"  {colour}[{f.state:^9}]{RESET} {cid:<28} {f.headline}")
        if f.detail:
            for ln in f.detail.splitlines():
                print(f"      {ln}" if not ln.startswith("  ") else ln)
        if f.state == ATTENTION:
            n_att += 1
            print(f"      {BOLD}FIX:{RESET} {f.fix}")
        print()
    return n_att


def run(root: Path) -> int:
    global RUNNER_MOD
    findings: list = []

    def add(cid: str, f: Finding):
        findings.append((cid, f))

    cfg_path, cfg_notes = find_config(root, HERE.parent)
    cfg: dict = {}
    if cfg_path:
        read_pairs(cfg_path, cfg)
        read_pairs(cfg_path.with_name("kit.config.local"), cfg)

    # The hook's own placeholder rule, borrowed rather than copied.
    placeholder = None
    hook_path = root / "modules" / "02-enforcement" / "hook_model_gate.py"
    if not hook_path.is_file():
        hook_path = root / "tools" / "hook_model_gate.py"
    if hook_path.is_file():
        mod, _ = import_runner(hook_path)
        placeholder = getattr(mod, "is_placeholder", None) if mod else None
    if not callable(placeholder):
        def placeholder(v):                    # noqa: F811 - documented fallback
            return not (v or "").strip()

    def cfg_get(key):
        v = (cfg.get(key) or "").strip()
        return "" if placeholder(v) else v

    # ---- the runner -----------------------------------------------------
    runner_rel = cfg_get("VERIFY_RUNNER") or "tools/verify.py"
    runner_path = root / runner_rel
    runner_note = ""
    if runner_path.is_file():
        RUNNER_MOD, runner_note = import_runner(runner_path)
    else:
        runner_note = (f"no verify runner at {runner_rel} (set VERIFY_RUNNER "
                       f"in kit.config to its path)")

    print(f"{BOLD}kit doctor{RESET} — diagnosing {root}")
    print(f"  config : {cfg_path or 'NONE FOUND in the tree being diagnosed'}")
    print(f"  runner : {runner_path if RUNNER_MOD else runner_note}")
    for note in cfg_notes:
        print(f"  {YELLOW}CONFIG NOTE:{RESET} {note}")
    print()

    # ---- 1. version ------------------------------------------------------
    vfile = root / "VERSION"
    stamp = None
    if vfile.is_file():
        try:
            stamp = vfile.read_text(encoding="utf-8")
        except OSError:
            stamp = ""
    add("doctor:version", judge_version(stamp, KIT_VERSION))

    # ---- 2. config -------------------------------------------------------
    add("doctor:config", judge_config(cfg_path, cfg, placeholder))

    # ---- judged paths, from the RUNNER when it imported ------------------
    if RUNNER_MOD:
        judge_paths = list(getattr(RUNNER_MOD, "JUDGE_PATHS", []) or [])
        cert_paths = list(getattr(RUNNER_MOD, "CERT_PATHS", []) or [])
    else:
        judge_paths = split_list(cfg.get("JUDGE_PATHS", ""))
        cert_paths = split_list(cfg.get("CERT_PATHS", ""))
    # Deduplicated, order preserved. A path in both lists is the normal case -
    # the kit's own CERT_PATHS entry is also a JUDGE_PATHS entry - and listing
    # it twice made the first live run report "8 judged path(s) missing" over
    # seven distinct paths, which is the kind of arithmetic a reader checks.
    judged = list(dict.fromkeys(judge_paths + cert_paths))

    # ---- 3. do they exist? -----------------------------------------------
    add("doctor:judge-paths-exist",
        judge_paths_exist(judged, lambda p: (root / p).exists()))

    # ---- 4. are they excluded? -------------------------------------------
    _, in_tree = git_out(root, "rev-parse", "--is-inside-work-tree")
    if not in_tree:
        add("doctor:judge-paths-ignored", Finding(
            ATTENTION, "not a git work tree",
            f"      {root} is not a git work tree, so nothing here can be "
            f"judged by git at all - and `git status` in a non-repo exits 128 "
            f"with EMPTY output, which is indistinguishable from a clean tree.",
            "`git init`, or run the doctor against the repository root with "
            "`--root <path>`."))
    else:
        excl, note = git_excluded_paths(root, judged)
        add("doctor:judge-paths-ignored",
            judge_paths_excluded(judged, excl, note))

    # ---- 5. do config and runner agree? ----------------------------------
    if RUNNER_MOD:
        runner_repo = getattr(RUNNER_MOD, "REPO", None)
        add("doctor:judge-paths-agree", judge_paths_agree(
            {"JUDGE_PATHS": split_list(cfg.get("JUDGE_PATHS", "")),
             "CERT_PATHS": split_list(cfg.get("CERT_PATHS", ""))},
            {"JUDGE_PATHS": judge_paths, "CERT_PATHS": cert_paths},
            None if runner_repo is None else same_path(runner_repo, root)))
    else:
        add("doctor:judge-paths-agree", Finding(
            ATTENTION, "runner not readable",
            f"      {runner_note}",
            "Point VERIFY_RUNNER in `kit.config` at your certification runner "
            "so this tool can compare its constants with the config the hook "
            "reads."))

    # ---- 6. vacuous gates -------------------------------------------------
    ledgers = cfg_get("LEDGERS_DIR") or "docs"

    def oracle_exists(name: str) -> bool:
        return any((root / d / f"ORACLE-{name}.md").is_file()
                   for d in {ledgers, "docs"})

    if RUNNER_MOD:
        add("doctor:vacuous-gate", judge_vacuous_gates(
            getattr(RUNNER_MOD, "GATES", {}) or {},
            list(getattr(RUNNER_MOD, "RUN_ORDER", []) or []),
            set(getattr(RUNNER_MOD, "COMPUTED_GATES", set()) or set()),
            oracle_exists))
    else:
        add("doctor:vacuous-gate", Finding(
            ATTENTION, "runner not readable",
            f"      {runner_note}",
            "Point VERIFY_RUNNER in `kit.config` at your certification runner "
            "so its gate table can be read."))

    # ---- 7. dirty paths ---------------------------------------------------
    porcelain, ok = git_out(root, "status", "--porcelain")
    if not ok:
        add("doctor:dirty-paths", Finding(
            ATTENTION, "git status failed",
            "      A failed command's silence is not a clean tree.",
            "Run the doctor from inside the work tree, or `--root <path>`."))
    else:
        add("doctor:dirty-paths", judge_dirty_paths(porcelain, judged))

    # ---- 8. the hook's interpreter ---------------------------------------
    settings = root / (cfg_get("HOOK_SETTINGS") or ".claude/settings.json")
    add("doctor:hook-interpreter",
        judge_interpreter(hook_commands(settings), resolve_interpreter))

    # ---- 9. the protected path on this filesystem ------------------------
    enabled = (cfg.get("PROTECTED_PATH_ENABLED", "").strip().lower()
               in {"1", "true", "yes", "on"})
    protected = cfg_get("PROTECTED_PATH")
    add("doctor:protected-case", judge_protected_case(
        enabled, protected,
        filesystem_folds_case(root) if enabled and protected else None))

    # ---- 10. the cert-green token ----------------------------------------
    tok_rel = cfg_get("CERT_TOKEN_FILE") or ".claude/cert-green.json"
    tok_path = root / tok_rel
    token = None
    if tok_path.is_file():
        try:
            token = json.loads(tok_path.read_text(encoding="utf-8"))
        except Exception:
            token = {}
    covered = dirty = None
    if token and cert_paths and in_tree:
        sha = (token.get("sha") or "").strip()
        tip, ok1 = git_out(root, "log", "-1", "--format=%H", "--", *cert_paths)
        st, ok2 = git_out(root, "status", "--porcelain", "--", *cert_paths)
        if ok1 and ok2 and sha and tip.strip():
            dirty = bool(st.strip())
            try:
                r = subprocess.run(
                    ["git", "-C", str(root), "merge-base", "--is-ancestor",
                     tip.strip(), sha], capture_output=True, timeout=15)
                covered = r.returncode == 0
            except Exception:
                covered = None
    add("doctor:cert-token", judge_cert_token(token, covered, dirty))

    # ---- 11. the anti-ratchet: is any floor rule overdue for a review? ----
    # The clock is READ HERE and passed in, so the judging layer stays pure and
    # --selftest can put any date it likes in front of it.
    floor_path = root / ledgers / "FAILURE-FLOOR.md"
    floor_rows: list = []
    floor_src = None
    if floor_path.is_file():
        floor_src = f"{ledgers}/FAILURE-FLOOR.md"
        try:
            floor_rows = parse_floor_rows(
                floor_path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            floor_rows = []
    try:
        window_stages = int((cfg_get("DEMOTION_REVIEW_STAGES") or "3").strip())
    except ValueError:
        window_stages = 3
    add("doctor:floor-staleness", judge_floor_staleness(
        floor_staleness(floor_rows, window_stages, date.today()),
        window_stages, floor_src))

    # ---- 12. the anti-ratchet: how big is the text every session reads? ---
    digest_parts = []
    rules_file = root / L1_RULES
    if rules_file.is_file():
        try:
            digest_parts.append(
                (L1_RULES,
                 len(rules_file.read_text(encoding="utf-8",
                                          errors="replace").splitlines())))
        except OSError:
            pass
    ck_glob = cfg_get("CHECKPOINT_GLOB")
    if ck_glob:
        # The NEWEST checkpoint is the one the rules file tells every session
        # to read; the older ones are superseded and nobody loads them.
        found = sorted((p for p in root.glob(ck_glob) if p.is_file()),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        if found:
            try:
                digest_parts.append(
                    (os.path.relpath(str(found[0]), str(root))
                     .replace("\\", "/"),
                     len(found[0].read_text(encoding="utf-8",
                                            errors="replace").splitlines())))
            except OSError:
                pass
    add("doctor:binding-digest",
        judge_binding_digest(digest_parts, DIGEST_CEILING_LINES))

    # ---- report ----------------------------------------------------------
    n_att = print_findings(findings)

    # THE WRONG-MODE POINTER. A Level-1 adopter runs the obvious command and
    # gets five red lines about a runner, a settings file and a hook they were
    # explicitly told not to install - a tool teaching its reader to ignore it.
    # The signal costs nothing: no runner imported, no hook wired, and the
    # documents Level 1 does install are sitting there.
    l1_docs = [f"{ledgers}/{n}" for n in L1_LEDGERS
               if (root / ledgers / n).is_file()]
    hint = level1_hint(bool(RUNNER_MOD), bool(hook_commands(settings)),
                       l1_docs)
    if hint:
        print(f"{YELLOW}  THIS LOOKS LIKE A LEVEL-1 ADOPTION{RESET} — {hint}\n")

    verdict = "ATTENTION" if n_att else "HEALTHY"
    code = 1 if n_att else 0
    print((RED if n_att else GREEN)
          + f"KIT DOCTOR: {verdict} (exit {code}) — {len(findings)} checks, "
            f"{n_att} needing attention" + RESET)
    print("  This is a DIAGNOSIS, not a certification. `PASS` belongs to your "
          "verify runner, which runs the gates; this tool runs none.")
    return code


def placeholder_rule(*bases):
    """(is_placeholder, rendered_pattern, where_they_came_from). The kit's two
    forms of one rule - "is this CONFIG VALUE still an example"
    (`is_placeholder`), and "did a shipped example value survive INTO a
    rendered document" (`RENDERED_PLACEHOLDER`) - imported from
    `hook_model_gate.py` wherever one of `bases` has a copy.

    IMPORTED, NOT RE-IMPLEMENTED. Three readers of that rule disagreeing about
    what "configured" means is the arrangement that produced the original
    defect, and the first version of this tool reproduced it by a new road: it
    scanned rendered documents against a one-element list of its own while the
    kit already carried the families. A Level-1 tree has no hook copy, so the
    kit checkout this tool runs from is the usual source.

    WHEN NEITHER IS FOUND, this tool has been copied out of a kit checkout.
    `is_placeholder` degrades to a deliberately narrower literal - it decides
    one config key, and narrower there is louder. The rendered pattern degrades
    to None rather than to a second opinion, and the check that consumes it
    then SAYS its scan was narrowed instead of printing a green that means less
    than it looks."""
    for base in bases:
        for rel in ("modules/02-enforcement/hook_model_gate.py",
                    "tools/hook_model_gate.py"):
            p = Path(base) / rel
            if p.is_file():
                mod, _ = import_runner(p)
                fn = getattr(mod, "is_placeholder", None) if mod else None
                pat = getattr(mod, "RENDERED_PLACEHOLDER", None) if mod else None
                if callable(fn):
                    return fn, pat, str(p)

    def fallback(v):
        low = (v or "").strip().lower()
        return any(low.startswith(s) for s in
                   ("/abs/path", "c:/abs/path", "/path/to/", "your-", "<"))
    return fallback, None, "built-in fallback (no hook_model_gate.py found)"


def run_level1(root: Path) -> int:
    """The documents-only diagnosis. Five checks, no runner, no settings file,
    no gate - and a summary that states its own limits."""
    findings: list = []

    cfg_path, cfg_notes = find_config(root, HERE.parent)
    cfg: dict = {}
    if cfg_path:
        read_pairs(cfg_path, cfg)
        read_pairs(cfg_path.with_name("kit.config.local"), cfg)
    is_ph, shipped_pat, ph_src = placeholder_rule(root, HERE.parent)

    ledgers = (cfg.get("LEDGERS_DIR") or "").strip() or "docs"
    know_raw = cfg.get("KNOWLEDGE_DIR")
    know_val = (know_raw or "").strip()
    know_is_none = know_val.upper() == "NONE"
    know_is_ph = bool(know_val) and not know_is_none and is_ph(know_val)

    def resolve(value: str) -> Path:
        """A configured directory as a path. Repo-relative unless it is
        already absolute - the same reading `kit.config.example` documents."""
        p = Path(value)
        return p if p.is_absolute() else (root / value)

    def disp(p) -> str:
        """A path as a reader of THIS repository would name it: repo-relative
        with forward slashes inside the tree, absolute outside it. A profile
        living in a knowledge base is genuinely elsewhere and is printed that
        way rather than as a relative path that resolves to nothing."""
        p = Path(p)
        if not path_inside(p, root):
            return str(p)
        return os.path.relpath(str(p), str(root)).replace("\\", "/")

    know_dir = (resolve(know_val)
                if know_val and not know_is_none and not know_is_ph else None)
    know_exists = None if know_dir is None else know_dir.is_dir()

    print(f"{BOLD}kit doctor — Level 1{RESET}: the documents, in {root}")
    print(f"  config : {cfg_path or 'NONE FOUND in the tree being diagnosed'}")
    print(f"  ledgers: {ledgers}/  (LEDGERS_DIR)")
    print(f"  placeholder rule read from: {ph_src}")
    for note in cfg_notes:
        print(f"  {YELLOW}CONFIG NOTE:{RESET} {note}")
    print()

    # ---- which documents, and where ------------------------------------
    required = [(rel, (root / rel) if (root / rel).is_file() else None)
                for rel in (f"{ledgers}/{name}" for name in L1_LEDGERS)]

    # The profile: source of truth is the KNOWLEDGE_DIR copy when there is
    # one, and the repo copy otherwise. Both are looked for, the first hit is
    # the one the content checks read, and a second copy is reported as the
    # mirror it is - QUICKSTART Step 8 says which is which.
    prof_candidates = (([know_dir / L1_PROFILE] if know_dir else [])
                       + [root / ledgers / L1_PROFILE,
                          root / "docs" / L1_PROFILE])
    # Deduplicated through `same_path()` rather than string equality: on the
    # ordinary configuration (LEDGERS_DIR = docs) two of these candidates are
    # one file spelled two ways, and the helper resolves symlinks and folds
    # case the way the host filesystem does instead of assuming either.
    prof_paths: list = []
    for p in prof_candidates:
        if p.is_file() and not any(same_path(p, q) for q in prof_paths):
            prof_paths.append(p)
    required.append(
        (disp(prof_paths[0]) + "  (the collaboration profile)" if prof_paths
         else f"{ledgers}/{L1_PROFILE}  (the collaboration profile)",
         prof_paths[0] if prof_paths else None))
    # The rules file: present is not adopted. A host that already had a
    # `CLAUDE.md` still has one, and this adoption may never have opened it.
    rules_path = root / L1_RULES
    rules_text = None
    if rules_path.is_file():
        try:
            rules_text = rules_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            rules_text = ""
    rules_adopted, rules_hits = rules_file_provenance(rules_text)
    optional = [(L1_RULES + " (module 01 as prose)",
                 rules_path if rules_path.is_file() else None,
                 rules_adopted, rules_hits)]

    def add(cid: str, f: Finding):
        findings.append((cid, f))

    add("doctor:l1-documents", judge_l1_documents(required, optional))

    # ---- is the config COMPLETE? -----------------------------------------
    # The registry of every key the templates interpolate is `kit.config.
    # example`, in the kit checkout. Read as a key list, not as values: what
    # this asks is whether the adopter's config carries the keys at all.
    example = None
    for base in (root, HERE.parent):
        cand = Path(base) / "kit.config.example"
        if cand.is_file():
            example = cand
            break
    if example is None:
        add("doctor:l1-config-complete",
            judge_l1_config_complete([], 0, None))
    else:
        registered: dict = {}
        read_pairs(example, registered)
        missing = [k for k in registered if k not in cfg]
        add("doctor:l1-config-complete", judge_l1_config_complete(
            sorted(missing), len(registered), disp(example)))

    # ---- does a pre-existing ledger already answer the same question? ----
    ledger_dir = root / ledgers
    present = sorted(p.name for p in ledger_dir.glob("*.md")
                     if p.is_file()) if ledger_dir.is_dir() else []
    add("doctor:l1-ledger-collision",
        judge_l1_ledger_collision(l1_ledger_collisions(present),
                                  f"{ledgers}/"))

    # ---- rendered? -------------------------------------------------------
    # A rules file that is the host's own is NOT scanned for shipped example
    # values: this check judges the documents this adoption installed, and
    # `Example Project` in somebody's own rules file is their business.
    scanned = ([p for _, p in required if p is not None]
               + [p for _, p, a, _ in optional if p is not None and a])
    if len(prof_paths) > 1:
        scanned += prof_paths[1:]
    problems = []
    exempted = {"fenced": 0, "spans": 0, "marked": 0}
    for p in scanned:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            problems.append(f"{disp(p)}: unreadable ({e.strerror})")
            continue
        problems += l1_render_problems(disp(p), text, shipped_pat)
        _, counts = scannable_for_shipped(text)
        for k in exempted:
            exempted[k] += counts[k]
    add("doctor:l1-rendered", judge_l1_rendered(problems, len(scanned),
                                                shipped_pat is not None,
                                                exempted))

    # ---- committed? ------------------------------------------------------
    # Only the copies INSIDE this repository can be judged by this repository's
    # git. A profile living in a knowledge base outside the tree is named in the
    # detail rather than silently counted as clean.
    inside = [p for p in scanned if path_inside(p, root)]
    outside = [p for p in scanned if not path_inside(p, root)]
    rels = [os.path.relpath(str(p), str(root)).replace("\\", "/")
            for p in inside]
    _, in_tree = git_out(root, "rev-parse", "--is-inside-work-tree")
    untracked, dirty = [], []
    git_ok = bool(in_tree) and bool(rels)
    if git_ok:
        porcelain, ok = git_out(root, "status", "--porcelain", "--", *rels)
        git_ok = ok
        if ok:
            for line in porcelain.splitlines():
                if len(line) < 4:
                    continue
                code, name = line[:2], line[3:].strip().strip('"')
                (untracked if code == "??" else dirty).append(name)
    f_commit = judge_l1_committed(git_ok, untracked, dirty)
    if outside and f_commit.state == OK:
        f_commit = Finding(
            f_commit.state, f_commit.headline,
            f_commit.detail + "\n      NOT JUDGED BY THIS REPOSITORY: "
            + ", ".join(str(p) for p in outside)
            + " - outside the work tree, so this repository's git says "
              "nothing about it.")
    add("doctor:l1-committed", f_commit)

    # ---- the two decisions ----------------------------------------------
    add("doctor:l1-knowledge-dir",
        judge_l1_knowledge_dir(know_raw, know_is_ph, know_exists))

    line = None
    if prof_paths:
        try:
            m = L1_INTERVIEW.search(
                prof_paths[0].read_text(encoding="utf-8", errors="replace"))
            line = m.group(1) if m else None
        except OSError:
            line = None
    add("doctor:l1-interview", judge_l1_interview(line))

    # ---- report ----------------------------------------------------------
    n_att = print_findings(findings)
    verdict = "ATTENTION" if n_att else "HEALTHY"
    code = 1 if n_att else 0
    print((RED if n_att else GREEN)
          + f"LEVEL 1: {verdict} (exit {code}) — {len(findings)} document "
            f"checks, {n_att} needing attention" + RESET)
    if n_att:
        print("  Nothing is certified while a line above is red. Each one "
              "names the step that fixes it.")
        return code

    # THE GREEN LINE, and it says what it is not. An adopter who reads a green
    # line as "the kit is working here" has been misled by their own tool: at
    # Level 1 nothing runs, nothing is enforced, and no agent is checked
    # against anything. Both halves are printed every time.
    # The commit clause is scoped to what git was actually asked about. A
    # profile living in a knowledge base outside the repository is read and
    # rendering-checked, and this repository's git says nothing about it - so
    # the summary counts it in the scan and out of the commit claim, rather
    # than sweeping it into a blanket "committed to git".
    commit_clause = ("are committed to git" if not outside else
                     f"the {len(rels)} of them inside this repository are "
                     f"committed to git")
    # The config files count. They are not documents and no check above reads
    # them as one, but the adopter added them and a removal cost that omits
    # them is a removal cost that is wrong.
    cfg_extra = [r for r in ("kit.config", "kit.config.local")
                 if (root / r).is_file()]
    # The sentences themselves live in `level1_summary_lines`, where the
    # selftest can read them (round 24 review, M10).
    for ln in level1_summary_lines(len(scanned), commit_clause, rules_adopted,
                                   rules_hits, [disp(p) for p in outside],
                                   rels + cfg_extra):
        print(ln)
    return code


# ==========================================================================
# --selftest : the doctor's own judging layer, with negative controls that
# reconstruct real defects and run the REAL functions
# ==========================================================================
def _expect_raises(fn):
    """The exception `fn` raised, or None. Keeps the selftest's assertions
    comparable values rather than try/except blocks scattered through it."""
    try:
        fn()
    except Exception as e:
        return e
    return None


def selftest() -> int:
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    print(f"{BOLD}=== A. every ATTENTION names a fixing step ==={RESET}")
    # THE STANDING RULE. It used to live only in the hand-enumerated list
    # below, and a reviewer's mutation walked past it: the fixing step was
    # removed from a branch the list had never enumerated and the suite stayed
    # green. The rule is now an INVARIANT in Finding.__init__, which covers the
    # branches nobody remembered and the ones nobody has written yet. The list
    # stays, because it also asserts that each control reaches the state it is
    # supposed to reach.
    try:
        Finding(ATTENTION, "a red line with no remedy")
        raised = False
    except ValueError as e:
        raised = "no fixing step" in str(e)
    check("THE INVARIANT: constructing an ATTENTION with no fixing step is a "
          "hard error, not a convention", raised, True)
    check("...and whitespace is not a fixing step",
          isinstance(_expect_raises(lambda: Finding(ATTENTION, "x", "d", "  ")),
                     ValueError), True)
    check("...while OK and INFO need no fix",
          [Finding(OK, "fine").state, Finding(INFO, "noted").state],
          [OK, INFO])
    reds = [
        judge_version(None, "0.1.0"),
        judge_version("0.0.9", "0.1.0"),
        judge_config(None, {}, lambda v: not v),
        judge_paths_exist(["a"], lambda p: False),
        judge_paths_excluded(["a"], ["a"], ""),
        judge_paths_excluded(["a"], [], "git exited 128"),
        judge_paths_agree({"JUDGE_PATHS": ["a"]}, {"JUDGE_PATHS": ["b"]}),
        judge_vacuous_gates({"g": {"require": "no groups here"}}, ["g"],
                            set(), lambda name: True),
        judge_dirty_paths(" M kit.config\n", ["kit.config"]),
        judge_interpreter(["python hook.py"], lambda t: None),
        judge_protected_case(True, "/frozen", True),
        judge_cert_token({"sha": "abc"}, False, False),
    ]
    check("every reconstructed defect is ATTENTION",
          sorted({f.state for f in reds}), [ATTENTION])
    check("...and every one of them names a fix",
          [f.headline for f in reds if not f.fix.strip()], [])

    print(f"\n{BOLD}=== B. doctor:version — the stamp and the tool ==={RESET}")
    check("a matching stamp is OK", judge_version("0.1.0\n", "0.1.0").state, OK)
    check("NC: a stamp from an older kit is caught",
          judge_version("0.0.9", "0.1.0").state, ATTENTION)
    check("...and the message names BOTH versions",
          all(s in judge_version("0.0.9", "0.1.0").headline
              for s in ("0.0.9", "0.1.0")), True)
    check("NC: no VERSION file at all is caught",
          judge_version(None, "0.1.0").state, ATTENTION)
    check("NC: an empty VERSION file is not a version",
          judge_version("   \n", "0.1.0").state, ATTENTION)
    check("the OK line refuses to overclaim (it says what it does not prove)",
          "not that every other copied file" in judge_version("0.1.0",
                                                              "0.1.0").detail,
          True)

    print(f"\n{BOLD}=== C. doctor:config — the placeholder rule, borrowed ==={RESET}")
    # THE REAL RULE, imported from the shipped hook. A local re-implementation
    # here would be a fourth reader of "what does configured mean", which is
    # the arrangement that produced the original defect.
    hook = (HERE.parent / "modules" / "02-enforcement" / "hook_model_gate.py")
    real_placeholder = None
    if hook.is_file():
        mod, _ = import_runner(hook)
        real_placeholder = getattr(mod, "is_placeholder", None) if mod else None
    check("the shipped placeholder rule is importable (not re-implemented)",
          callable(real_placeholder), True)
    if callable(real_placeholder):
        full = {"FORBIDDEN_SPAWN_TIER": "orchestrator-tier",
                "LANE_TIER": "lane-tier", "MODEL_EXEMPT_TYPES": "fork",
                "JUDGE_PATHS": "a.py, b.py"}
        check("a fully configured kit.config is OK",
              judge_config("kit.config", full, real_placeholder).state, OK)
        # NC: the kit's OWN shipped example value, which reads as a configured
        # rule and guards a tier nobody will ever request.
        nc = dict(full, FORBIDDEN_SPAWN_TIER="your-top-tier-model")
        f = judge_config("kit.config", nc, real_placeholder)
        check("NC: a shipped example value is NOT configured", f.state,
              ATTENTION)
        check("...and the finding names the key AND the consequence",
              ("FORBIDDEN_SPAWN_TIER" in f.detail
               and "does not exist" in f.detail), True)
        check("NC: `NONE` is not a value either",
              judge_config("kit.config", dict(full, LANE_TIER="NONE"),
                           real_placeholder).state, ATTENTION)
    check("NC: no config at all is caught",
          judge_config(None, {}, lambda v: not v).state, ATTENTION)

    print(f"\n{BOLD}=== C2. WHICH config — the defect this tool's own first "
          f"live run produced ==={RESET}")
    # Pointed at an empty repository from inside the kit checkout, the first
    # version loaded the KIT's kit.config (via the four-step search's
    # current-working-directory step) and printed the kit's settings as the
    # adopter's. Same class as kit_render.py's read_target_config, arriving by
    # a third road.
    check("the TARGET's kit.config is what gets read",
          choose_config("", False, False, "/target/kit.config", True)[0],
          "/target/kit.config")
    check("NC: a target with no kit.config yields NOTHING, never a fallback "
          "to the kit's own worked example",
          choose_config("", False, False, "/target/kit.config", False)[0],
          None)
    check("$KIT_CONFIG pointing OUTSIDE the kit wins - it is an instruction",
          choose_config("/elsewhere/kit.config", True, False,
                        "/target/kit.config", True)[0], "/elsewhere/kit.config")
    _in_kit = choose_config("/kit/kit.config", True, True,
                            "/target/kit.config", True)
    check("NC: $KIT_CONFIG pointing INSIDE the kit checkout is IGNORED "
          "(QUICKSTART Step 2 sets it and it leaks)", _in_kit[0],
          "/target/kit.config")
    check("...and the substitution is announced, not silent",
          "IGNORED" in " ".join(_in_kit[1]), True)
    _bad = choose_config("/nope", False, False, "/target/kit.config", True)
    check("a $KIT_CONFIG naming no file falls back AND says so",
          (_bad[0], "not a file" in " ".join(_bad[1])),
          ("/target/kit.config", True))
    # THE REAL path comparator behind env_inside_kit, on this filesystem.
    check("path_inside: the kit's own tools dir is inside the kit",
          path_inside(HERE, HERE.parent), True)
    # Case folding is the filesystem's property, not an assumption: an
    # uppercased path is inside only where normcase folds case (Windows), and
    # is correctly NOT inside on a case-sensitive filesystem (Linux CI). This
    # is the same case-sensitivity class doctor:protected-case probes.
    _folds = os.path.normcase("A") == os.path.normcase("a")
    check("path_inside: case sensitivity follows the filesystem",
          path_inside(str(HERE).upper(), str(HERE.parent)), _folds)
    check("path_inside: a sibling with a shared prefix is NOT inside",
          path_inside(str(HERE.parent) + "-other", str(HERE.parent)), False)

    print(f"\n{BOLD}=== D. doctor:judge-paths-* ==={RESET}")
    check("present paths are OK",
          judge_paths_exist(["a", "b"], lambda p: True).state, OK)
    check("NC: a missing judged path is caught and NAMED",
          "a" in judge_paths_exist(["a"], lambda p: False).detail, True)
    check("NC: an EMPTY judged list is itself a finding (git says nothing "
          "about nothing, and nothing reads as clean)",
          judge_paths_exist([], lambda p: True).state, ATTENTION)
    check("no exclusion is OK", judge_paths_excluded(["a"], [], "").state, OK)
    check("NC: an excluded judged path is caught",
          judge_paths_excluded(["a"], ["a"], "").state, ATTENTION)
    check("NC: git failing to answer is NOT silence",
          judge_paths_excluded(["a"], [], "git exited 128").state, ATTENTION)
    check("agreeing lists are OK",
          judge_paths_agree({"JUDGE_PATHS": ["a", "b"], "CERT_PATHS": ["c"]},
                            {"JUDGE_PATHS": ["a", "b"], "CERT_PATHS": ["c"]}
                            ).state, OK)
    check("separator spelling does not manufacture a disagreement",
          judge_paths_agree({"JUDGE_PATHS": ["a\\b"]},
                            {"JUDGE_PATHS": ["a/b"]}).state, OK)
    _dis = judge_paths_agree({"JUDGE_PATHS": ["a"]}, {"JUDGE_PATHS": ["b"]})
    check("NC: a disagreement is caught", _dis.state, ATTENTION)
    check("...and the REAL CONSEQUENCE is named, not just the difference",
         ("authoritative" in _dis.detail
          and "green about different sets of files" in _dis.fix), True)
    check("NC: a runner that resolved a DIFFERENT repository root is caught "
          "even when the two path lists agree",
          judge_paths_agree({"JUDGE_PATHS": ["a"]}, {"JUDGE_PATHS": ["a"]},
                            False).state, ATTENTION)
    check("...and matching roots with matching lists stay OK",
          judge_paths_agree({"JUDGE_PATHS": ["a"]}, {"JUDGE_PATHS": ["a"]},
                            True).state, OK)
    # THE REAL COMPARATOR, on this filesystem. The pure cases above cannot see
    # a comparator that calls two spellings of one directory different, which
    # is the second-machine defect this argument exists for.
    check("same_path: two spellings of one directory are one directory",
          same_path(HERE, HERE.parent / HERE.name), True)
    check("same_path: a trailing separator does not make a new directory",
          same_path(str(HERE) + os.sep, HERE), True)
    check("same_path: a sibling is not the same directory",
          same_path(HERE, HERE.parent), False)

    print(f"\n{BOLD}=== E. doctor:vacuous-gate — three ways to be unfailable ==={RESET}")
    good = {"g": dict(require=r"suite: (\d+)/\1 passed", expect_min=12,
                      doc="the unit suite")}
    check("a gate with a group, a real floor and an oracle page is OK",
          judge_vacuous_gates(good, ["g"], set(), lambda x: True).state, OK)
    check("NC(i): no capture group -> the floor is inert",
          "no capture group" in judge_vacuous_gates(
              {"g": dict(require="suite: all passed", expect_min=12)},
              ["g"], set(), lambda x: True).detail, True)
    check("NC(ii): a floor of 1 clears on any run producing one of anything",
          "the floor is 1" in judge_vacuous_gates(
              {"g": dict(require=r"suite: (\d+) passed", expect_min=1)},
              ["g"], set(), lambda x: True).detail, True)
    check("NC(ii-b): a floor of 0 too",
          judge_vacuous_gates(
              {"g": dict(require=r"suite: (\d+) passed", expect_min=0)},
              ["g"], set(), lambda x: True).state, ATTENTION)
    check("NC(iii): a missing ORACLE page is a finding",
          "no ORACLE-g.md page" in judge_vacuous_gates(
              good, ["g"], set(), lambda x: False).detail, True)
    check("NC(iv): a require pattern that does not compile",
          "does not compile" in judge_vacuous_gates(
              {"g": dict(require="(unclosed", expect_min=12)}, ["g"], set(),
              lambda x: True).detail, True)
    check("NC(v): no require pattern at all - the log is never judged",
          "never judged" in judge_vacuous_gates(
              {"g": dict(expect_min=12)}, ["g"], set(),
              lambda x: True).detail, True)
    check("a COMPUTED gate is exempt from the line rules but still asked "
          "for an oracle page",
          judge_vacuous_gates({"judges": dict(computed=True)}, ["judges"],
                              {"judges"}, lambda x: True).state, OK)
    check("NC: the kit's shipped EXAMPLE gates are named as such",
          "EXAMPLE gates" in judge_vacuous_gates(
              {"g": dict(require=r"x (\d+)", expect_min=12,
                         doc="EXAMPLE - replace with your test suite")},
              ["g"], set(), lambda x: True).detail, True)

    print(f"\n{BOLD}=== F. doctor:dirty-paths — names files, stages nothing ==={RESET}")
    check("a clean tree is OK", judge_dirty_paths("", []).state, OK)
    check("an ordinary dirty tree is INFO, not a failure",
          judge_dirty_paths("?? scratch.txt\n M src/a.py\n", ["kit.config"]
                            ).state, INFO)
    check("...and it NAMES what a blanket add would take",
          "scratch.txt" in judge_dirty_paths("?? scratch.txt\n", []).detail,
          True)
    _dj = judge_dirty_paths(" M kit.config\n?? scratch.txt\n", ["kit.config"])
    check("NC: a DIRTY JUDGED path is ATTENTION (certification is a property "
          "of a tree)", _dj.state, ATTENTION)
    check("...and the judged one is called out by name",
          "JUDGED and uncommitted: kit.config" in _dj.detail, True)
    check("a judged DIRECTORY covers the files under it",
          judge_dirty_paths(" M examples/fake_suite.py\n", ["examples"]
                            ).state, ATTENTION)
    check("...but not a directory that merely shares a prefix",
          judge_dirty_paths(" M examples-old/x.py\n", ["examples"]).state,
          INFO)
    # THE PROHIBITION, MADE MECHANICAL. "It never stages anything" is a
    # sentence in the module docstring, and a sentence is the weakest layer
    # this kit recognises.
    #
    # THE FIRST VERSION OF THIS CHECK WAS TOO NARROW, and a reviewer's mutation
    # proved it: it recovered verbs from the two argv SHAPES this file happens
    # to use, so `subprocess.run(["git", "add", "-A"], cwd=str(root))` - a third
    # shape - was invisible and the selftest stayed green. Recovering the
    # sanctioned shapes is still worth doing, because it proves the verbs in
    # them are read-only. What closes the hole is the second scan below: EVERY
    # argv list in this file that starts with a "git" literal, whatever its
    # shape, is read and required to carry no mutating verb.
    src = Path(__file__).read_text(encoding="utf-8")
    body = src.split("def selftest", 1)[0]
    verbs = set(re.findall(r'git_out\(\s*\w+,\s*"([a-z-]+)"', body))
    verbs |= set(re.findall(r'"git",\s*"-C",\s*str\(\w+\),\s*"([a-z-]+)"', body))
    check("the source scan actually found the git calls (an empty scan would "
          "pass this section vacuously)", len(verbs) >= 4, True)
    check("every git verb in a sanctioned call shape is READ-ONLY",
          sorted(verbs - READ_ONLY_GIT), [])
    check("...and the allowlist itself carries no mutating verb",
          sorted(READ_ONLY_GIT & MUTATING_GIT), [])
    # The shape-independent half. Any argv list literal opening with "git".
    argvs = re.findall(r'\[\s*"git"[^\]]*\]', body, re.S)
    check("the argv scan found the git argv lists (again, not vacuously)",
          len(argvs) >= 2, True)
    words = {w for a in argvs for w in re.findall(r'"([a-z][a-z-]*)"', a)}
    check("NO argv list anywhere in this file carries a MUTATING git verb, "
          "whatever shape the call is written in",
          sorted(words & MUTATING_GIT), [])
    # And the scan is proven able to see one, on a synthetic body, so a future
    # edit that breaks the regex cannot leave this section silently vacuous.
    _m = re.findall(r'\[\s*"git"[^\]]*\]',
                    'subprocess.run(["git", "add", "-A"], cwd=str(root))', re.S)
    check("NC: the argv scan DOES catch a staging call written in a third "
          "shape (the mutation that defeated the first version)",
          sorted({w for a in _m
                  for w in re.findall(r'"([a-z][a-z-]*)"', a)} & MUTATING_GIT),
          ["add"])

    print(f"\n{BOLD}=== G. doctor:hook-interpreter — the OTHER half of SB-A ==={RESET}")
    check("a resolvable interpreter is OK",
          judge_interpreter(["python hook.py"], lambda t: Path("/usr/bin/python")
                            ).state, OK)
    check("NC: THE DEBIAN CASE - bare `python` with no shim on the host",
          judge_interpreter(['python "tools/hook_model_gate.py"'],
                            lambda t: None).state, ATTENTION)
    check("...and the fix names PYTHON_BIN and python3",
          all(s in judge_interpreter(["python h.py"], lambda t: None).fix
              for s in ("PYTHON_BIN", "python3")), True)
    check("NC: no hook command wired at all",
          judge_interpreter([], lambda t: Path("/x")).state, ATTENTION)
    # THE DEFAULT WINDOWS INSTALL PATH, which contains a space. The first
    # version split on whitespace before stripping quotes, so this reported
    # ATTENTION - about the exact arrangement the check's own fixing step
    # recommends. The old selftest case used `C:/Python/python.exe`, which has
    # no space, so it certified the unquoting and missed the split.
    _winpy = "C:/Program Files/Python312/python.exe"
    _res = lambda t: Path(t) if t.endswith("python.exe") else None      # noqa: E731
    check("a QUOTED interpreter path containing a space resolves",
          judge_interpreter([f'"{_winpy}" hook.py'], _res).state, OK)
    check("...and an UNQUOTED one does too (longest resolving prefix wins, "
          "which is how Windows itself reads it)",
          judge_interpreter([f'{_winpy} hook.py'], _res).state, OK)
    check("interpreter_token: the quoted form comes back whole",
          interpreter_token(f'"{_winpy}" hook.py',
                            lambda t: t == _winpy), _winpy)
    check("interpreter_token: the unquoted form comes back whole",
          interpreter_token(f'{_winpy} hook.py',
                            lambda t: t == _winpy), _winpy)
    check("interpreter_token: a bare name is still one token",
          interpreter_token("python hook.py", lambda t: t == "python"),
          "python")
    check("interpreter_token: nothing resolves -> the FIRST token, so the "
          "ATTENTION names something the reader recognises",
          interpreter_token("nosuchpy hook.py", lambda t: False), "nosuchpy")
    check("interpreter_token: a Windows backslash path is not eaten as an "
          "escape sequence",
          interpreter_token(r'"C:\Python312\python.exe" hook.py',
                            lambda t: t == r"C:\Python312\python.exe"),
          r"C:\Python312\python.exe")
    check("interpreter_token: an empty command yields nothing",
          interpreter_token("   ", lambda t: True), "")
    check("a pwsh -File wiring resolves on its interpreter, not its script",
          judge_interpreter(['pwsh -NoProfile -File "C:/r/hook.ps1"'],
                            lambda t: Path(t) if t == "pwsh" else None).state,
          OK)
    # THE REAL RESOLVER, on this host, not a stub: a stubbed resolver cannot
    # see a resolver that resolves everything.
    check("the REAL resolver finds this running interpreter",
          resolve_interpreter(sys.executable) is not None, True)
    check("...and refuses a name no host has",
          resolve_interpreter("kit-doctor-no-such-interpreter-9f3c"), None)
    check("...and refuses a path that does not exist",
          resolve_interpreter("/no/such/dir/python"), None)
    # SECOND-MACHINE SWEEP over the path handling added for the spaced-path
    # fix. Resolution goes through the FILESYSTEM rather than through string
    # comparison, so the host's own rules about separators and case apply -
    # the same answer `same_path()` and `path_inside()` reach by resolving and
    # case-folding instead of guessing from `os.name`.
    check("...resolves the same interpreter spelled with forward slashes",
          resolve_interpreter(sys.executable.replace(os.sep, "/")) is not None,
          True)
    _exe = Path(sys.executable)
    check("...and through a path that needs resolving to find it",
          resolve_interpreter(
              str(_exe.parent / ".." / _exe.parent.name / _exe.name)
          ) is not None, True)

    print(f"\n{BOLD}=== H. doctor:protected-case — P1-F2, on the host you are on ==={RESET}")
    check("the tripwire off is n/a, not a gap",
          judge_protected_case(False, "", None).state, NA)
    check("NC: ON with no path is half-configured",
          judge_protected_case(True, "", None).state, ATTENTION)
    check("NC: a case-insensitive filesystem is a silent bypass",
          judge_protected_case(True, "/frozen", True).state, ATTENTION)
    check("...and the finding names the other two directions too",
          all(s in judge_protected_case(True, "/frozen", True).detail
              for s in ("cd", "symlink")), True)
    check("a case-sensitive filesystem is OK, and still says what remains",
          (judge_protected_case(True, "/frozen", False).state,
           "symlinks" in judge_protected_case(True, "/frozen", False).detail),
          (OK, True))
    check("NC: an unprobeable filesystem does not guess",
          judge_protected_case(True, "/frozen", None).state, ATTENTION)
    # P13: a top level holding only all-uppercase names used to answer None,
    # so an ordinary repository reported "could not probe". The probe now looks
    # one level down. Measured against the kit's own modules/ tree, whose top
    # level entries are all-uppercase-free but whose ROOT carries LICENSE and
    # VERSION alongside lowercase files.
    check("the probe answers for a directory whose files are all uppercase, "
          "by looking one level down",
          filesystem_folds_case(HERE.parent / "modules") in (True, False), True)
    # THE REAL PROBE, against the real filesystem this run is on. The pure
    # cases above cannot see a probe that always answers False - which is what
    # an inference from os.name would be on a case-sensitive Windows volume.
    _probe = filesystem_folds_case(HERE)
    check("the REAL case probe returns a decision, not a guess",
          _probe in (True, False), True)
    check("...and it agrees with the platform's usual answer here",
          _probe, os.name == "nt" or sys.platform == "darwin")

    print(f"\n{BOLD}=== I. doctor:cert-token — the label is the control ==={RESET}")
    check("no token is n/a", judge_cert_token(None, None, None).state, NA)
    check("...and the label is printed even then",
          "not an authorization" in judge_cert_token(None, None, None).detail,
          True)
    _cov = judge_cert_token({"sha": "abc123def456", "minted_by": "verify.py"},
                            True, False)
    check("a covering token is OK", _cov.state, OK)
    check("...and STILL says it is unsigned and forgeable",
          all(s in _cov.detail for s in ("unsigned", "can mint one")), True)
    check("NC: a superseded token is caught",
          judge_cert_token({"sha": "abc"}, False, False).state, ATTENTION)
    check("NC: a token over a DIRTY certified tree is caught",
          judge_cert_token({"sha": "abc"}, True, True).state, ATTENTION)
    check("NC: a token with no sha is caught",
          judge_cert_token({}, None, None).state, ATTENTION)
    check("NC: a token git could not evaluate is not trusted",
          judge_cert_token({"sha": "abc"}, None, None).state, ATTENTION)
    _hand = judge_cert_token({"sha": "abcdef123456"}, True, False)
    check("a HAND-WRITTEN token that covers the tree is INFO, not OK - the "
          "one field separating an asserted token from a certified one is not "
          "something to bury in a body a reader scanning for red skips",
          _hand.state, INFO)
    check("...and the state line itself says HAND-WRITTEN",
          "HAND-WRITTEN" in _hand.headline, True)
    check("...and it points at the command that mints a real one",
          "--mint-cert-token" in _hand.detail, True)

    print(f"\n{BOLD}=== I2. the tool writes nothing into the tree it reads ==={RESET}")
    # The imports of the target's verify.py and hook_model_gate.py used to
    # leave `__pycache__/` beside each of them, and the dirty-paths check two
    # sections up then reported that residue back to the adopter as their dirty
    # tree. Asserted on the interpreter's own state, not on the source text, so
    # a later edit that moves the statement somewhere it does not take effect
    # is caught rather than matched.
    check("bytecode writing is OFF for this process before any target module "
          "is imported", sys.dont_write_bytecode, True)
    # Measured in an EMPTY directory of its own. Asserting the absence of a
    # `__pycache__` beside the shipped files would be a check on whatever else
    # has touched this checkout - `python -m py_compile` writes one too - and a
    # check another tool can turn red is a check people learn to ignore.
    import tempfile
    _d = Path(tempfile.mkdtemp(prefix="kitdoctor-import-")).resolve()
    (_d / "probe_module.py").write_text("VALUE = 1\n", encoding="utf-8")
    _mod, _err = import_runner(_d / "probe_module.py")
    check("...a target module still imports (the guard did not break reading)",
          (getattr(_mod, "VALUE", None), _err), (1, ""))
    check("...and the import left NOTHING behind in the directory it read "
          "from - no __pycache__, no .pyc",
          sorted(p.name for p in _d.iterdir()), ["probe_module.py"])
    shutil.rmtree(_d, ignore_errors=True)

    print(f"\n{BOLD}=== I4. the anti-ratchet pair — what is checking the "
          f"lessons ==={RESET}")
    # Both of these promote a rule whose only enforcement layer was PROSE -
    # the debt FAILURE-FLOOR.md exists to audit, carried by the floor itself.
    # The clock is injected in every check below, so these run the real
    # judging layer against dates the test chose.
    _floor = (
        "| Rule | Layer | Zone | Status | Last fired | Covered / residual |\n"
        "|---|---|---|---|---|---|\n"
        "| <the rule, one line> | HOOK | B | **STRUCTURAL** | <date> | x |\n"
        "| no blanket add | HOOK (PreToolUse) | B | **STRUCTURAL** | "
        "2026-01-01 | Covered: staging. |\n"
        "| tiering declared | HOOK | B | **STRUCTURAL** | 2026-01-11 | x |\n"
        "| review is spec-side | PROSE | B | **AMBER** | 2026-01-21 | x |\n"
        "| a human at the gate | HUMAN | A | **ACCEPTED** | 2020-01-01 | x |\n"
        "| the quiet one | PROSE | B | **AMBER** | never | x |\n"
        "| the undated one | PROSE | B | **AMBER** | unknown - predates "
        "recording | x |\n")
    _rows = parse_floor_rows(_floor)
    check("the floor's table parses into rules, and the TEMPLATE's example "
          "row is not one of them",
          [r["rule"] for r in _rows],
          ["no blanket add", "tiering declared", "review is spec-side",
           "a human at the gate", "the quiet one", "the undated one"])
    _rep = floor_staleness(_rows, 3, date(2026, 1, 31))
    check("the window is DERIVED from this project's own dates: three "
          "distinct firings 10 days apart, x3 stages = 30 days",
          (_rep["distinct"], round(_rep["interval"], 1), _rep["window_days"]),
          (3, 10.0, 30))
    check("...and EXACTLY at the window nothing is stale (the boundary, "
          "stated: the oldest rule is 30 days old against a 30-day window)",
          _rep["stale"], [])
    check("...while one day later it is",
          [r for r, _ in floor_staleness(_rows, 3, date(2026, 2, 1))["stale"]],
          ["no blanket add"])
    _late = floor_staleness(_rows, 3, date(2026, 3, 1))
    check("NC: 39 days after the oldest firing, the rule that has not fired "
          "since is OVERDUE and is named with its age",
          _late["stale"], [("no blanket add", 59), ("tiering declared", 49),
                           ("review is spec-side", 39)])
    check("...and the finding says so, with the arithmetic on the same line",
          all(s in judge_floor_staleness(_late, 3, "docs/FAILURE-FLOOR.md")
              .detail
              for s in ("ARITHMETIC", "mean interval", "10.0 days",
                        "= 30 days")), True)
    check("...and its fixing step names all three dispositions",
          all(s in judge_floor_staleness(_late, 3, "docs/FAILURE-FLOOR.md")
              .fix for s in ("RETIRE", "DEMOTE", "RE-AFFIRM")), True)
    check("a row already carrying a FINAL disposition is exempt, not stale",
          ("a human at the gate" in _late["exempt"],
           any(r == "a human at the gate" for r, _ in _late["stale"])),
          (True, False))
    check("`never` and `unknown - predates recording` are NOT MEASURED, "
          "counted apart, and never guessed at",
          (_rep["never"], [r for r, _ in _rep["unusable"]]),
          (["the quiet one"], ["the undated one"]))
    check("...and the finding SAYS both, so its green does not read as "
          "covering them",
          all(s in judge_floor_staleness(_rep, 3, "docs/FAILURE-FLOOR.md")
              .detail
              for s in ("NOT MEASURED", "never fired", "no usable date")),
          True)
    _thin = floor_staleness(parse_floor_rows(
        "| Rule | L | Z | S | Last fired | R |\n|---|---|---|---|---|---|\n"
        "| only one | PROSE | B | AMBER | 2026-01-01 | x |\n"), 3,
        date(2030, 1, 1))
    check("NC: one distinct date cannot derive an interval, so staleness is "
          "NOT COMPUTABLE and is reported as UNKNOWN rather than green-by-"
          "arithmetic",
          (_thin["window_days"], _thin["stale"],
           "NOT COMPUTABLE" in judge_floor_staleness(
               _thin, 3, "docs/FAILURE-FLOOR.md").headline),
          (None, [], True))
    check("NC: a floor with no rows at all is ATTENTION - a floor with "
          "nothing in it passes by having nothing to check",
          judge_floor_staleness(floor_staleness([], 3, date(2026, 1, 1)), 3,
                                "docs/FAILURE-FLOOR.md").state, ATTENTION)
    check("no floor file at all is n/a, NOT a red - whether the ledgers are "
          "installed is doctor:l1-documents' question, and two reds for one "
          "fact is how a tool teaches its reader to skim",
          judge_floor_staleness(floor_staleness([], 3, date(2026, 1, 1)), 3,
                                None).state, NA)
    check("...and the n/a says out loud that it is not a green",
          "n/a, not green" in judge_floor_staleness(
              floor_staleness([], 3, date(2026, 1, 1)), 3, None).detail, True)
    check("CROSS-CHECK: the SHIPPED floor template contributes ZERO judged "
          "rules - its table rows are prompts, and a reader that counted "
          "them would report staleness about instructions",
          len(parse_floor_rows((HERE.parent / "modules" / "04-ledgers" /
                                "FAILURE-FLOOR.md")
                               .read_text(encoding="utf-8"))), 0)
    check("...and the reader is not simply blind: the same file with its "
          "prompts filled in DOES parse",
          len(parse_floor_rows(
              (HERE.parent / "modules" / "04-ledgers" / "FAILURE-FLOOR.md")
              .read_text(encoding="utf-8")
              .replace("<the rule, one line>", "a real rule")
              .replace("<a rule you have not structuralised>", "another")
              .replace("<a rule a human enforces>", "a third"))), 3)

    # THE CEILING'S FIRST OBSERVATION, BOUND TO THE FILE IT WAS MEASURED
    # FROM. The derivation in the comment above DIGEST_CEILING_LINES starts
    # from the shipped rules template's rendered line count. If that template
    # grows, the input has moved and the ceiling stops meaning what the
    # comment says - so this reads the file rather than trusting the number.
    #
    # ROUND 26 (m1): the third label below used to SPELL the arithmetic as
    # "(209 + 90) x 1.15" while both sides of its assertion read the live
    # constant, so the sentence a human read was never compared to anything
    # and stayed two revisions stale through 191 -> 206 -> 209 -> 219. The
    # label is now BUILT FROM THE CONSTANTS, which makes the prose a third
    # reader of the same source rather than a free-standing claim about it.
    _tmpl = (HERE.parent / "modules" / "01-governance" / "CLAUDE.md.template")
    check("the ceiling's first observation is the SHIPPED template, measured "
          "now, not a number somebody typed once",
          rendered_template_lines(_tmpl.read_text(encoding="utf-8")),
          DIGEST_SHIPPED_RULES_LINES)
    check("...and the header block really is stripped (the raw file is "
          "longer than the rendered count)",
          len(_tmpl.read_text(encoding="utf-8").splitlines())
          > DIGEST_SHIPPED_RULES_LINES, True)
    check("...and the ceiling is the derivation's arithmetic, not a "
          "free-standing number: ({} + {}) x 1.15, rounded up to 25"
          .format(DIGEST_SHIPPED_RULES_LINES, DIGEST_CHECKPOINT_NORM_LINES),
          DIGEST_CEILING_LINES,
          25 * -(-int((DIGEST_SHIPPED_RULES_LINES
                       + DIGEST_CHECKPOINT_NORM_LINES) * 1.15) // 25))
    check("a digest under the ceiling is OK",
          judge_binding_digest([("CLAUDE.md", 190), ("docs/CP.md", 90)],
                               DIGEST_CEILING_LINES).state, OK)
    check("NC: one line over the ceiling is ATTENTION - the boundary, stated",
          (judge_binding_digest([("CLAUDE.md", DIGEST_CEILING_LINES)],
                                DIGEST_CEILING_LINES).state,
           judge_binding_digest([("CLAUDE.md", DIGEST_CEILING_LINES + 1)],
                                DIGEST_CEILING_LINES).state),
          (OK, ATTENTION))
    check("NC: a rules file that has merely DOUBLED from the shipped "
          "template breaches on its own, with no checkpoint at all - this is "
          "where the threshold actually sits",
          judge_binding_digest(
              [("CLAUDE.md", DIGEST_SHIPPED_RULES_LINES * 2)],
              DIGEST_CEILING_LINES).state, ATTENTION)
    check("the arithmetic is printed on EVERY run, green included",
          [("ARITHMETIC" in judge_binding_digest(
              [("CLAUDE.md", n)], DIGEST_CEILING_LINES).detail)
           for n in (10, 999)], [True, True])
    check("...and it shows the composition, so a reader can see which half "
          "grew",
          "CLAUDE.md 200 + docs/CP.md 100 = 300" in judge_binding_digest(
              [("CLAUDE.md", 200), ("docs/CP.md", 100)],
              DIGEST_CEILING_LINES).detail, True)
    check("...and the green says what it did NOT judge",
          "not that any line in it has earned its place" in
          judge_binding_digest([("CLAUDE.md", 10)],
                               DIGEST_CEILING_LINES).detail, True)
    check("no rules file and no checkpoint is n/a, not a green zero",
          judge_binding_digest([], DIGEST_CEILING_LINES).state, NA)
    check("...and it says a project with no binding digest sidestepped this "
          "check rather than passing it",
          "sidestepped" in judge_binding_digest([],
                                                DIGEST_CEILING_LINES).detail,
          True)

    print(f"\n{BOLD}=== I3. the Level-1 layer — documents, and nothing "
          f"more ==={RESET}")
    # Every defect here was reconstructed from a literal, so these run the real
    # judges rather than probing files the selftest also wrote. The shipped
    # rule is the REAL one, imported the way the tool imports it at runtime.
    _rule, _pat, _rule_src = placeholder_rule(HERE.parent)
    check("the shared rendered-value rule was imported, not re-implemented "
          "(a None here means every shipped-value assertion below is vacuous)",
          _pat is not None, True)
    clean_ledger = ("# Acme — Token Ledger\n\n| stage | tokens |\n"
                    "|---|---|\n| R1 | 12k |\n")
    check("a rendered document has no rendering problem",
          l1_render_problems("docs/TOKEN-LEDGER.md", clean_ledger, _pat), [])
    check("NC: a slot nobody substituted is caught, by name",
          l1_render_problems("docs/LESSONS.md", "# {{PROJECT_NAME}} — Lessons",
                             _pat),
          ["docs/LESSONS.md: {{PROJECT_NAME}} was never substituted"])
    check("NC: the ledgers' SKELETON header is caught",
          [p.split(":")[0] for p in l1_render_problems(
              "docs/FAILURE-FLOOR.md",
              "<!--\nSKELETON - copy to docs/FAILURE-FLOOR.md.\n-->\n# Floor",
              _pat)],
          ["docs/FAILURE-FLOOR.md"])
    check("NC: the profile's own header block is caught (a different marker "
          "word from the ledgers', which is why both are listed)",
          len(l1_render_problems(
              "docs/collaboration-profile.md",
              "<!--\nTEMPLATE - the living collaboration profile.\n"
              "Delete this comment on adoption.\n-->\n", _pat)), 2)
    check("NC: the rules file's header block is caught",
          len(l1_render_problems(
              "CLAUDE.md", "DELETE THIS COMMENT BLOCK when you adopt.",
              _pat)), 1)
    check("NC: a shipped placeholder PATH that reached a rendered document is "
          "caught",
          l1_render_problems("CLAUDE.md",
                             "profile: /abs/path/to/your/knowledge-base/x.md",
                             _pat),
          ["CLAUDE.md: the shipped example value '/abs/path/to/' is in the "
           "rendered document - the fill-in behind it was never made"])
    # THE ESCAPE THIS FIX PASS CLOSES. Six documents titled `Example Project`
    # and four `your-top-tier-model` strings in the rules file passed as
    # HEALTHY, because this check carried a one-element list of its own while
    # the kit already enumerated the families. Both forced red here.
    check("NC: the shipped PROJECT_NAME reaching a document title is caught",
          l1_render_problems("docs/LESSONS.md",
                             "# Example Project — Lessons Learned\n", _pat),
          ["docs/LESSONS.md: the shipped example value 'Example Project' is "
           "in the rendered document - the fill-in behind it was never made"])
    check("NC: a shipped tier name copied into the rules file is caught",
          [p.split(" is in ")[0] for p in l1_render_problems(
              "CLAUDE.md", "lanes run on your-top-tier-model.\n", _pat)],
          ["CLAUDE.md: the shipped example value 'your-top-tier-model'"])
    check("THE ONE EXEMPTION HOLDS: RATIO_CEILING's shipped value is NOT a "
          "problem — QUICKSTART Step 7 tells the adopter to keep it, and the "
          "shared pattern DOES match it, so this exemption is load-bearing",
          (bool(_pat.search(L1_ALLOWED_SHIPPED[1])),
           l1_render_problems("docs/TOKEN-LEDGER.md",
                              f"ceiling: {L1_ALLOWED_SHIPPED[1]}\n", _pat)),
          (True, []))
    check("...and with no shared rule available the shipped-value scan is "
          "SKIPPED, not silently narrowed",
          l1_render_problems("docs/LESSONS.md",
                             "# Example Project — Lessons\n", None), [])
    check("...and the finding then SAYS the scan was narrowed",
          "SCAN NARROWED" in judge_l1_rendered([], 6, False).detail, True)
    check("...while the full scan's green line does not say that",
          "SCAN NARROWED" in judge_l1_rendered([], 6, True).detail, False)

    # ---- F3: a document QUOTING the kit is not a document missing a
    # fill-in. The measured instance is a judgment-ledger row recording that
    # a check was forced red over `Example Project` - a truthful record the
    # only documented remedy told the adopter to falsify. Every exemption
    # below is paired with a TRUE-POSITIVE control on the same string, so a
    # quoting exemption cannot be read as the scan going quiet.
    _quoted_row = ("| 1 (fix) | F1 fixed | doctor selftest 149 (forced-red "
                   "`Example Project` / `your-top-tier-model`) |\n")
    check("F3: a shipped value inside INLINE CODE SPANS is not a defect - "
          "the ordinary way prose quotes a value",
          l1_render_problems("docs/JUDGMENT-LEDGER.md", _quoted_row, _pat), [])
    check("F3 TRUE-POSITIVE CONTROL: the SAME strings unquoted still red",
          len(l1_render_problems(
              "docs/JUDGMENT-LEDGER.md",
              _quoted_row.replace("`", ""), _pat)), 2)
    _fenced = ("Example output:\n\n```\n# Example Project — Lessons\n```\n\n"
               "and that is what a fresh render looks like.\n")
    check("F3: a shipped value inside a FENCED BLOCK is not a defect",
          l1_render_problems("docs/LESSONS.md", _fenced, _pat), [])
    check("F3 TRUE-POSITIVE CONTROL: the same block with the fences removed "
          "reds",
          len(l1_render_problems("docs/LESSONS.md",
                                 _fenced.replace("```\n", ""), _pat)), 1)
    _marked = ("| the rule | HOOK | B | STRUCTURAL | 2026-08-21 | forced red "
               "over Example Project |  <!-- oar:quotes-example -->\n")
    check("F3: a line carrying the opt-out marker is not scanned - for the "
          "table cell where backticks would be wrong",
          l1_render_problems("docs/FAILURE-FLOOR.md", _marked, _pat), [])
    check("F3 TRUE-POSITIVE CONTROL: the same line without the marker reds",
          len(l1_render_problems("docs/FAILURE-FLOOR.md",
                                 _marked.split("<!--")[0] + "\n", _pat)), 1)
    check("F3: the exemptions are SHIPPED-VALUE ONLY - a slot inside a fence "
          "is still a slot",
          l1_render_problems("CLAUDE.md", "```\n{{PROJECT_NAME}}\n```\n",
                             _pat),
          ["CLAUDE.md: {{PROJECT_NAME}} was never substituted"])
    check("...and a template header block inside a fence is still a header "
          "block",
          len(l1_render_problems("CLAUDE.md",
                                 "```\nDELETE THIS COMMENT BLOCK\n```\n",
                                 _pat)), 1)
    check("F3: an unterminated fence does not swallow the rest of the "
          "document silently - it is counted and reported",
          scannable_for_shipped("```\nx\ny\n")[1]["fenced"], 3)
    check("F3: the exemption tally is COUNTED, per mechanism",
          scannable_for_shipped(
              "a `b` c\n<!-- oar:quotes-example -->\n```\nd\n```\n")[1],
          {"fenced": 3, "spans": 1, "marked": 1})
    check("F3: ...and REPORTED on the finding, so a document cannot go "
          "quietly green by fencing itself",
          all(s in judge_l1_rendered(
                  [], 6, True, {"fenced": 3, "spans": 1, "marked": 1}).detail
              for s in ("QUOTED TEXT NOT SCANNED", "3 line(s) inside fenced",
                        "1 inline code span", "oar:quotes-example")), True)
    check("...and an ordinary adoption with no exemption says nothing extra",
          "QUOTED TEXT NOT SCANNED" in judge_l1_rendered(
              [], 6, True, {"fenced": 0, "spans": 0, "marked": 0}).detail,
          False)
    check("...and the red's fixing step offers the exemption rather than "
          "leaving the adopter to falsify a record",
          all(s in judge_l1_rendered(["docs/x.md: bad"], 6).fix
              for s in ("backticks", L1_QUOTE_MARKER)), True)

    # ---- F1: the config the documents tell a brownfield adopter to
    # overwrite. The check names the missing keys AND names the destructive
    # remedy as destructive, because the destructive remedy is the obvious one.
    check("F1: a config missing keys the templates interpolate is ATTENTION",
          judge_l1_config_complete(["DEMOTION_REVIEW_STAGES",
                                    "RATIO_CEILING"], 40,
                                   "kit.config.example").state, ATTENTION)
    check("...and it NAMES them",
          "DEMOTION_REVIEW_STAGES" in judge_l1_config_complete(
              ["DEMOTION_REVIEW_STAGES"], 40, "kit.config.example").detail,
          True)
    check("...and the fixing step says APPEND, and says the copy DESTROYS",
          all(s in judge_l1_config_complete(
                  ["X"], 40, "kit.config.example").fix
              for s in ("APPEND", "Do NOT copy", "destroys")), True)
    check("...a complete config is OK",
          judge_l1_config_complete([], 40, "kit.config.example").state, OK)
    check("NC: with no shipped registry to read, this is UNKNOWN and says so "
          "- not a green",
          (judge_l1_config_complete([], 0, None).state,
           "UNKNOWN" in judge_l1_config_complete([], 0, None).detail),
          (ATTENTION, True))
    # THE VACUITY GUARD. This check compares against a real file, so the
    # oracle is only worth anything if that file really is a key registry.
    _example_keys: dict = {}
    read_pairs(HERE.parent / "kit.config.example", _example_keys)
    check("CROSS-CHECK: the shipped kit.config.example really is a key "
          "registry (an empty read here would make this check vacuous)",
          len(_example_keys) > 20, True)
    check("...and it registers the two keys the kit's own dogfood adoption "
          "found missing from a pre-existing config",
          sorted(k for k in ("DEMOTION_REVIEW_STAGES", "RATIO_CEILING")
                 if k in _example_keys),
          ["DEMOTION_REVIEW_STAGES", "RATIO_CEILING"])

    # ---- F2: the ledger names are fixed, and a brownfield repository
    # already has ledgers. Measured on the kit's own program repo:
    # LESSONS-LEARNED.md beside LESSONS.md, TOKEN_LEDGER.md beside
    # TOKEN-LEDGER.md - two documents answering one question, and every
    # check green.
    check("F2: an underscore spelling of a kit ledger name collides",
          l1_ledger_collisions(["TOKEN_LEDGER.md"]),
          [("TOKEN_LEDGER.md", "TOKEN-LEDGER.md")])
    check("F2: ...and a longer name containing a kit stem collides",
          l1_ledger_collisions(["LESSONS-LEARNED.md"]),
          [("LESSONS-LEARNED.md", "LESSONS.md")])
    check("F2 CONTROL: the kit's own files at the kit's own names do NOT "
          "collide",
          l1_ledger_collisions(list(L1_LEDGERS)), [])
    check("F2 CONTROL: an unrelated document does not collide",
          l1_ledger_collisions(["README.md", "ARCHITECTURE.md",
                                "SESSIONS.md"]), [])
    check("F2: the finding names all three ways out and none of them is "
          "'delete it'",
          all(s in judge_l1_ledger_collision(
                  [("TOKEN_LEDGER.md", "TOKEN-LEDGER.md")], "docs/").fix
              for s in ("RENAME", "FREEZE", "LEDGERS_DIR")), True)
    check("...and it says nothing was changed, because nothing was",
          "Nothing here has been changed or lost" in
          judge_l1_ledger_collision([("a.md", "LESSONS.md")], "docs/").detail,
          True)
    check("F2: no collision is OK", judge_l1_ledger_collision([], "docs/")
          .state, OK)

    _p = Path("docs/JUDGMENT-LEDGER.md")
    check("all documents present is OK",
          judge_l1_documents([("docs/LESSONS.md", _p)], [("CLAUDE.md", None)])
          .state, OK)
    check("...and the optional one being absent is stated, not counted as a "
          "defect",
          "NOT TAKEN" in judge_l1_documents([("docs/LESSONS.md", _p)],
                                            [("CLAUDE.md", None)]).detail, True)
    check("NC: a missing required document is ATTENTION and is named",
          [judge_l1_documents([("docs/LESSONS.md", None)], []).state,
           "docs/LESSONS.md" in
           judge_l1_documents([("docs/LESSONS.md", None)], []).detail],
          [ATTENTION, True])

    # ---- PRESENT IS NOT ADOPTED (round 24, F3) --------------------------
    # A rules file at the right path was counted as module 01 adopted as
    # prose, so a green line certified six documents where five were
    # installed and told the reader to delete the sixth. Both directions are
    # asserted here, against the REAL provenance function.
    _host_rules = ("# a host project — its own rules\n\n"
                   "Run `python -m pytest -q` before every commit. Evidence "
                   "pages live under docs/evidence/.\n")
    _adopted_rules = (
        "# a host project — binding coordinator rules\n\n"
        "## MODEL TIERING — the orchestrator orchestrates\n\n"
        "Every spawn declares an explicit model tier.\n\n"
        "## WHEN THE LOOP ENDS — review terminates by rule\n\n"
        "One review round by default.\n")
    check("F3: a host's OWN rules file is not module 01 as prose",
          rules_file_provenance(_host_rules)[0], False)
    check("F3: ...and a file carrying module 01's headings IS",
          rules_file_provenance(_adopted_rules)[0], True)
    check("F3: ...and no file at all is neither, not a false negative",
          rules_file_provenance(None), (None, []))
    check("F3: the floor is a COUNT of fingerprints, and one is not enough "
          "(a host may reach one heading on its own vocabulary)",
          rules_file_provenance("# rules\n\n## MODEL TIERING\n")[0], False)
    _pre = judge_l1_documents(
        [("docs/LESSONS.md", _p)],
        [(L1_RULES + " (module 01 as prose)", _p, False, [])])
    check("F3: NC — a PRE-EXISTING rules file is not counted as a Level-1 "
          "document",
          _pre.headline, "1 Level-1 document(s) present")
    check("F3: ...and the finding says so, in the words a reader needs",
          "PRESENT BUT NOT ADOPTED" in _pre.detail, True)
    check("F3: ...and it is still OK, not ATTENTION — the host having its "
          "own rules file is not a defect", _pre.state, OK)
    check("F3: ...and the NOT-ADOPTED line claims a COUNT, never a provenance "
          "— no 'untouched', no 'the owner's own', no 'did not install it' "
          "(round 24 review, M3)",
          [w for w in ("untouched", "did not install",
                       "carries none of module 01") if w in _pre.detail], [])
    _took = judge_l1_documents(
        [("docs/LESSONS.md", _p)],
        [(L1_RULES + " (module 01 as prose)", _p, True,
          list(L1_RULES_FINGERPRINTS[:2]))])
    check("F3: the OTHER direction — an actually adopted module-01 prose "
          "file still counts",
          [_took.headline, "PRESENT BUT NOT ADOPTED" in _took.detail],
          ["2 Level-1 document(s) present", False])
    check("F3: ...and the ADOPTED branch prints the numbers it decided on "
          "too, which is the direction that lets REMOVAL COST name a file "
          "(round 24 review, M4)",
          ["2 of 8 fingerprints found; 2 is the floor" in _took.detail,
           "2 of 8 fingerprints found; 2 is the floor" in _pre.detail],
          [True, False])

    # ---- THE PRINT SITE, NOT THE PURE LAYER (round 24 review, M10) -------
    # Everything above asserts the functions that DECIDE. These assert the
    # sentences a reader actually gets, which is where four findings of the
    # round shipped: a green line claiming provenance it could not establish,
    # an adopted branch with no numbers, and a REMOVAL COST closing clause
    # naming the very file the line above it had just promised to leave out.
    _own = level1_summary_lines(5, "are committed to git", False, ["MODEL "
                                "TIERING"], [], ["docs/LESSONS.md",
                                                 "kit.config"])
    _own_txt = "\n".join(_own)
    check("M10: NC — on a host rules file below the floor, the summary says "
          "so WITH ITS NUMBERS", ["fewer than 2 of module 01's 8 fingerprints"
                                  in _own_txt, "(1 found)" in _own_txt],
          [True, True])
    _own_cost = [ln for ln in _own if "REMOVAL COST" in ln][0]
    check("M10: NC — and `CLAUDE.md` appears in NO part of REMOVAL COST on "
          "that run, its closing merge clause included",
          L1_RULES in _own_cost, False)
    check("M10: ...and the summary states the limit of the reading rather "
          "than asserting provenance",
          ["cannot tell the two apart" in _own_txt,
           "untouched" in _own_txt, "the owner's own" in _own_txt],
          [True, False, False])
    _ado = level1_summary_lines(6, "are committed to git", True,
                                list(L1_RULES_FINGERPRINTS),
                                [], ["docs/LESSONS.md", L1_RULES,
                                     "kit.config"])
    _ado_txt = "\n".join(_ado)
    check("M10: the OTHER direction — an adopted rules file IS named in "
          "REMOVAL COST, and the not-adopted line is absent",
          [L1_RULES in _ado_txt, "NOT ADOPTED, AND NOT COUNTED" in _ado_txt],
          [True, False])
    check("M10: no such file at all — neither line fires, and the closing "
          "clause still names no rules file",
          [("NOT ADOPTED, AND NOT COUNTED" in t, L1_RULES in t)
           for t in ["\n".join(level1_summary_lines(
               5, "are committed to git", None, [], [], ["kit.config"]))]],
          [(False, False)])
    check("M10: every summary carries all three headline words, in order",
          [[w for w in ("CERTIFIES", "DOES NOT CERTIFY", "REMOVAL COST")
            if w in t] for t in (_own_txt, _ado_txt)],
          [["CERTIFIES", "DOES NOT CERTIFY", "REMOVAL COST"]] * 2)
    check("no rendering problem is OK; one is ATTENTION",
          [judge_l1_rendered([], 6).state,
           judge_l1_rendered(["docs/x.md: {{A}} was never substituted"],
                             6).state], [OK, ATTENTION])
    check("committed and clean is OK",
          judge_l1_committed(True, [], []).state, OK)
    check("NC: an UNTRACKED document is ATTENTION — an untracked document is "
          "not adopted",
          judge_l1_committed(True, ["docs/LESSONS.md"], []).state, ATTENTION)
    check("NC: a tracked document with uncommitted changes is ATTENTION",
          judge_l1_committed(True, [], ["docs/LESSONS.md"]).state, ATTENTION)
    check("NC: git failing is ATTENTION, not silence read as clean",
          judge_l1_committed(False, [], []).state, ATTENTION)
    check("KNOWLEDGE_DIR: NONE is a DECISION here, not an unset value",
          judge_l1_knowledge_dir("NONE", False, None).state, OK)
    check("...and a real directory that exists is OK",
          judge_l1_knowledge_dir("docs", False, True).state, OK)
    check("NC: no key at all is ATTENTION",
          judge_l1_knowledge_dir(None, False, None).state, ATTENTION)
    check("NC: the shipped placeholder value is ATTENTION",
          judge_l1_knowledge_dir("/abs/path/to/your/knowledge-base", True,
                                 None).state, ATTENTION)
    check("NC: a recorded directory that is not there is ATTENTION",
          judge_l1_knowledge_dir("/vault", False, False).state, ATTENTION)
    check("the interview's three states are all GREEN, owner-blocked "
          "included",
          [judge_l1_interview(v).state for v in
           ("not yet held", "scheduled 2026-09-04 confirmed by the owner",
            "held 2026-08-21")],
          [OK, OK, OK])
    check("...and an owner-blocked one still SAYS the defaults are "
          "unconfirmed",
          "UNCONFIRMED" in judge_l1_interview("not yet held").detail, True)
    # F4. A DATE THAT PARSES IS NOT A DATE SOMEBODY AGREED TO. This kit's own
    # dogfood adoption produced an invented one, and it read exactly like a
    # real calendar entry - the owner's ruling was to delete it and record
    # `not yet held`. The state stays green; the unattributed date does not.
    check("NC: a scheduled date with NO confirmation is ATTENTION - an "
          "invented schedule reads identically to a real one",
          judge_l1_interview("scheduled 2026-09-04").state, ATTENTION)
    check("...and the red names both ways out",
          all(s in judge_l1_interview("scheduled 2026-09-04").fix
              for s in ("confirmed by", "not yet held")), True)
    check("...while `confirmed by <someone>` clears it",
          judge_l1_interview("scheduled 2026-09-04 confirmed by Dana in "
                             "the team calendar").state, OK)
    check("...and so does a bare `confirmed <source>` without the `by`",
          judge_l1_interview("scheduled 2026-09-04 - confirmed "
                             "calendar-invite").state, OK)
    check("THE CONTROL: the word `confirmed` with nothing after it is not a "
          "source",
          judge_l1_interview("scheduled 2026-09-04 confirmed").state,
          ATTENTION)
    check("...and `not yet held` is still green with no confirmation asked "
          "of it (the owner-blocked adopter is one keystroke from green)",
          judge_l1_interview("not yet held").state, OK)
    check("...and a HELD date needs no confirmation either - the profile's "
          "own answers are its evidence",
          judge_l1_interview("held 2026-08-21").state, OK)
    check("NC: the shipped MENU is not an answer",
          judge_l1_interview("not yet held | scheduled <date> | held <date>")
          .state, ATTENTION)
    check("NC: `scheduled <date>` with the placeholder left in is not an "
          "answer either",
          judge_l1_interview("scheduled <date>").state, ATTENTION)
    check("NC: a fourth wording is ATTENTION",
          judge_l1_interview("we'll see").state, ATTENTION)
    check("NC: no INTERVIEW line at all is ATTENTION",
          judge_l1_interview(None).state, ATTENTION)

    # The wrong-mode pointer: a Level-1 tree running the default set.
    check("a Level-1 tree (documents, no runner, no hook) gets the --level1 "
          "pointer", "--level1" in level1_hint(False, False,
                                               ["docs/LESSONS.md"]), True)
    check("...and a Level-2 tree does not (a runner is present)",
          level1_hint(True, False, ["docs/LESSONS.md"]), "")
    check("...nor does one whose hook is wired",
          level1_hint(False, True, ["docs/LESSONS.md"]), "")
    check("...nor an empty repository with no Level-1 documents in it",
          level1_hint(False, False, []), "")

    # THE CROSS-CHECKS. Every constant above is a literal in this file, and a
    # literal describing another file drifts when that file changes. These read
    # the shipped templates and hold the literals to them - available whenever
    # this tool sits in a kit checkout, and reported as unavailable rather than
    # skipped in silence when it has been copied out on its own.
    _kit = HERE.parent
    if (_kit / "modules" / "04-ledgers").is_dir():
        check("CROSS-CHECK: L1_LEDGERS names exactly the ledger skeletons "
              "module 04 ships",
              sorted(p.name for p in
                     (_kit / "modules" / "04-ledgers").glob("*.md")
                     if p.name != "README.md"), sorted(L1_LEDGERS))
        # The module-01 fingerprints are literals for the same reason the
        # ledger names are - an adopted tree has no `modules/` to read - so
        # they are held to the shipped template here, in the kit, rather than
        # drifting quietly and reading an adopted file as the host's own.
        _tpl = (_kit / "modules" / "01-governance"
                / "CLAUDE.md.template").read_text(encoding="utf-8")
        check("CROSS-CHECK: every module-01 fingerprint is in the SHIPPED "
              "rules template",
              [f for f in L1_RULES_FINGERPRINTS if f not in _tpl], [])
        check("CROSS-CHECK: ...and the shipped template itself reads as "
              "module 01 as prose, which is the claim the fingerprints make",
              rules_file_provenance(_tpl)[0], True)
        _prof = (_kit / "modules" / "08-collaboration"
                 / "PROFILE-TEMPLATE.md").read_text(encoding="utf-8")
        _m = L1_INTERVIEW.search(_prof)
        check("CROSS-CHECK: the INTERVIEW pattern finds the status line in the "
              "SHIPPED profile template, and reads it as the unanswered menu",
              (bool(_m), judge_l1_interview(_m.group(1) if _m else None).state),
              (True, ATTENTION))
        check("CROSS-CHECK: the shipped profile template trips the rendering "
              "check (it is a template; a copy of it is not an adoption)",
              len(l1_render_problems("PROFILE-TEMPLATE.md", _prof, _pat)) > 0,
              True)
        # THE MANUFACTURED ORACLE. The escape this fix pass closes was not one
        # missing string, it was the absence of anything holding the scan to
        # what the kit SHIPS. So: read `kit.config.example`, take the values it
        # ships for the keys that get substituted into a Level-1 document, and
        # require the shared rule to catch every one of them in document text.
        # Change the shipped PROJECT_NAME to `Sample Project` without teaching
        # the rule about it and this goes red here, in the kit, rather than in
        # an adopter's tree.
        _ex = (_kit / "kit.config.example").read_text(encoding="utf-8")
        _shipped = {}
        for _k in ("PROJECT_NAME", "ORCHESTRATOR_TIER", "LANE_TIER",
                   "SWEEP_TIER", "FORBIDDEN_SPAWN_TIER", "KNOWLEDGE_DIR",
                   "RATIO_CEILING"):
            _m2 = re.search(rf"(?m)^{_k}\s*=\s*(\S.*?)\s*$", _ex)
            if _m2:
                _shipped[_k] = _m2.group(1)
        check("CROSS-CHECK: the seven keys this oracle reads are all present "
              "in kit.config.example (a missing key would make it vacuous)",
              len(_shipped), 7)
        check("THE ORACLE: every shipped example value that lands in a "
              "Level-1 document is caught by the shared rule, in document "
              "text — the escape that reported HEALTHY over six documents "
              "titled `Example Project`",
              sorted(k for k, v in _shipped.items()
                     if k != "RATIO_CEILING"
                     and not l1_render_problems("doc.md", f"x {v} y", _pat)),
              [])
        check("...and RATIO_CEILING's shipped value is the ONE the rule "
              "matches and this check deliberately lets through",
              (bool(_pat.search(_shipped["RATIO_CEILING"])),
               l1_render_problems("doc.md",
                                  f"x {_shipped['RATIO_CEILING']} y", _pat)),
              (True, []))
    else:
        check("the module cross-checks are UNAVAILABLE here (this tool has "
              "been copied out of a kit checkout) - stated, not skipped in "
              "silence", (_kit / "modules").is_dir(), False)

    print(f"\n{BOLD}=== J. the registry contract ==={RESET}")
    check("every check in CHECKS carries the doctor: family prefix",
          [c for c, _ in CHECKS if not c.startswith("doctor:")], [])
    check("no duplicate check ids", len({c for c, _ in CHECKS}), len(CHECKS))
    check("every check id is recoverable by the expectation lint's pattern "
          "(an unregistered check is invisible to it)",
          sorted(re.findall(r'^\s*\("(doctor:[a-z0-9-]+)",\s',
                            Path(__file__).read_text(encoding="utf-8"),
                            re.M)),
          sorted(c for c, _ in CHECKS))

    print()
    print((GREEN if ok_all else RED)
          + f"KIT-DOCTOR SELFTEST: {'PASS' if ok_all else 'FAIL'} — {n} checks"
          + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Diagnose a kit adoption. Diagnoses; does not certify.",
        epilog="exit 0 HEALTHY · 1 ATTENTION · 2 ABORT")
    ap.add_argument("--root", default="", help="the repository to diagnose")
    ap.add_argument("--level1", action="store_true",
                    help=f"the documents-only diagnosis: the {N_L1} "
                         "`doctor:l1-*` checks, for a tree adopted by "
                         "LEVEL-1.md (no runner, no hook, no settings file)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true",
                    help="print the check inventory and exit")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.list:
        print(f"kit_doctor {KIT_VERSION} — {len(CHECKS)} checks "
              f"({len(CHECKS) - len(L1_CHECKS)} in the full diagnosis, "
              f"{len(L1_CHECKS)} in --level1)")
        for cid, doc in CHECKS:
            mode = "L1 " if cid in L1_CHECKS else "   "
            print(f"  {mode}{cid:<28} {doc}")
        return 0

    start = Path(a.root).resolve() if a.root else Path.cwd().resolve()
    root = find_repo_root(start)
    if root is None:
        print(f"{RED}KIT DOCTOR: ABORTED — no .git ancestor of {start}. This "
              f"tool will not report HEALTHY about a tree it never found; "
              f"pass --root <your repository>.{RESET}", file=sys.stderr)
        return 2
    return run_level1(root) if a.level1 else run(root)


if __name__ == "__main__":
    raise SystemExit(main())
