#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/kit_doctor.py - check my adoption. One command, ten checks, no verdict
that could be mistaken for a certification.

    python tools/kit_doctor.py                 # diagnose this repository
    python tools/kit_doctor.py --root <path>   # diagnose another one
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
]


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

    # ---- report ----------------------------------------------------------
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

    verdict = "ATTENTION" if n_att else "HEALTHY"
    code = 1 if n_att else 0
    print((RED if n_att else GREEN)
          + f"KIT DOCTOR: {verdict} (exit {code}) — {len(findings)} checks, "
            f"{n_att} needing attention" + RESET)
    print("  This is a DIAGNOSIS, not a certification. `PASS` belongs to your "
          "verify runner, which runs the gates; this tool runs none.")
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
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true",
                    help="print the check inventory and exit")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.list:
        print(f"kit_doctor {KIT_VERSION} — {len(CHECKS)} checks")
        for cid, doc in CHECKS:
            print(f"  {cid:<28} {doc}")
        return 0

    start = Path(a.root).resolve() if a.root else Path.cwd().resolve()
    root = find_repo_root(start)
    if root is None:
        print(f"{RED}KIT DOCTOR: ABORTED — no .git ancestor of {start}. This "
              f"tool will not report HEALTHY about a tree it never found; "
              f"pass --root <your repository>.{RESET}", file=sys.stderr)
        return 2
    return run(root)


if __name__ == "__main__":
    raise SystemExit(main())
