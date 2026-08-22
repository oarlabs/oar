#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py - THE ONE CERTIFICATION COMMAND (skeleton).

    python verify.py                     # the full certification
    python verify.py --list              # the gates, in run order
    python verify.py --only judges       # a subset - can never certify
    python verify.py --skip example_lint
    python verify.py --out <dir>         # artefacts; MUST be outside the repo
    python verify.py --selftest          # prove this runner's own judges
    python verify.py --nc <file.json>    # negative control - see below

==========================================================================
THIS IS A SKELETON. IT RUNS AS SHIPPED.
==========================================================================
`example_unit` and `example_lint` shell out to two toy scripts in `examples/`
so a fresh adopter can watch a real PASS, a real FAIL, a real PARTIAL and a
real INSTRUMENTED run within a minute of cloning. **Replace both gates with
your own.**

`judges` is not an example - KEEP IT. `hooks` and `escapes` are not examples
either, but each names files that live in ANOTHER module: `hooks` needs module
02 and `escapes` needs module 04. If you adopted module 03 on its own, DELETE
the entry from GATES and from RUN_ORDER and drop its constants
(HOOK_FIXTURES / HOOK_SETTINGS, ESCAPE_TOOL / ESCAPE_LEDGER), or the startup
assertion will correctly refuse to start over files you do not have.
(`--skip <gate>` works too, but leaving a permanently-skipped gate in
RUN_ORDER means every run reports PARTIAL and can never certify.)

Deleting the example gates is EXPECTED and does not break `--selftest`: the
checks that are about them are guarded, and section I then asserts that every
gate in RUN_ORDER is exercised by at least one check, so a replacement gate
with no selftest goes loudly red instead of silently uncovered.

SLOTS. Six constants below the config block are the whole adoption surface:
JUDGE_PATHS, CERT_PATHS, HOOK_FIXTURES, HOOK_SETTINGS, ESCAPE_TOOL,
ESCAPE_LEDGER - all repo-relative, all asserted to exist before any gate runs.
Related kit.config keys:
{{PROJECT_ROOT}} {{JUDGE_PATHS}} {{CERT_PATHS}} {{TOOLCHAIN_PIN}}
{{VERIFY_OUT_DIR}} {{GATE_COMMAND}}

==========================================================================
THE EXIT-CODE CONTRACT
==========================================================================
    0  PASS          every gate in RUN_ORDER ran and was green, no --nc.
                     THE ONLY CERTIFYING OUTCOME.
    1  FAIL          at least one gate went red.
    2  INSTRUMENTED  --nc was passed (the run is doctored) - or ABORTED, a
                     refusal to start (bad --out, bad --nc, unknown gate).
                     Never a certification either way.
    3  PARTIAL       every gate that ran was green, but --only/--skip left at
                     least one gate of RUN_ORDER unrun.

PASS is reachable from exactly ONE place in the code. A subset run reports
PARTIAL because **"the check did not run" and "the check passed" must never
look the same**, and an exit code is the form of that sentence a shell can
read. Every CI system, every wrapper script, and every tired human at 2am
reads the code before they read the log.

==========================================================================
WHY EVERY GATE IS JUDGED BY A REQUIRED OUTPUT LINE
==========================================================================
Not by an exit code. Exit codes lie in both directions: toolchains that crash
during shutdown return garbage after doing everything right, and wrappers
swallow failures into a cheerful 0. A REQUIRED OUTPUT LINE is strictly
stronger - a run that died half-way has no required line either.

And every headline gate carries an `expect_min` FLOOR, because:

    suite: 0 identical, 0 diverged
    compile: 0/0 files compiled
    ALL 0 STEPS PASSED

are all perfectly well-formed success lines, and all three are catastrophes.
Without a floor, every gate here is green on zero. The floors live in THIS
file - inside the judge surface - precisely so that lowering one is a reviewed
commit rather than a charter edit nobody sees.

Use a backreference where "all of them" is the claim: `(\\d+)/\\1` matches
204/204 and never 203/204.

==========================================================================
THE NEGATIVE CONTROL IS BUILT IN
==========================================================================
A gate that has never been red has not been shown to work. `--nc <file.json>`
loads an override table that doctors a gate's required pattern, veto pattern
or floor WITHOUT editing a single repo file:

    { "require":      { "example_unit": "example_unit: 9999/9999 cases passed" },
      "fail_pattern": { "example_lint": "checks" },
      "expect_min":   { "example_unit": 99999 } }

An instrumented run CANNOT BE MISTAKEN FOR A CERTIFICATION, structurally:
  * instrumentation is armed by the FLAG APPEARING IN argv - `--nc`, `--nc=`,
    `--nc=missing.json`, a malformed file: every one is armed, and a load
    failure exits 2 rather than falling through to a clean run;
  * the verdict word becomes INSTRUMENTED, so "PASS" is unreachable;
  * the exit code is 2 - never 0, never 1, never 3.

Unknown keys and unknown gate names in the override file are REFUSED (exit 2):
an override that is silently ignored is worse than no override, because it
produces a green you will read as a proven negative control.

==========================================================================
--selftest
==========================================================================
Runs this file's PURE judging layer against synthetic inputs: shrunk counts,
subset lines, dirty-tree porcelain samples, every branch of the verdict
matrix. No subprocesses, no clock, no filesystem, no repo mutation. That is
what makes it possible at all - the judging layer is deliberately separated
from the running layer, and every function above the `RUNNING LAYER` banner is
pure.

Run it in CI before anything expensive. A runner whose judges are broken
cannot tell you anything about your project.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ==========================================================================
# WHERE IS THE REPO? (a load-bearing question, not a formality)
# ==========================================================================
# The obvious answer - the directory this file lives in - is WRONG the moment
# you copy the runner to <repo>/tools/verify.py, which is exactly what the
# QUICKSTART tells you to do.
#
# Get it wrong and the judges gate goes SILENTLY GREEN FOREVER:
#
#     git -C tools status --porcelain -- src
#
# returns an EMPTY STRING with rc 0 when `src` does not exist under `tools/`,
# and an empty porcelain is precisely how "clean" is spelled. The gate whose
# entire job is to notice an uncommitted tree becomes a gate that cannot fail.
# It was found by adopting this kit into a scratch project and following the
# QUICKSTART literally, which is the only way this class of defect is ever
# found.
#
# So the root is DISCOVERED, in this order:
#   1. the nearest ancestor directory containing .git
#   2. PROJECT_ROOT from kit.config (same 4-step search the hook uses)
#   3. this file's own directory - and then the STARTUP ASSERTION below will
#      almost certainly abort, which is the intended outcome
#
# And discovery is not trusted on its own: `startup_problems()` asserts that
# every JUDGE_PATHS / CERT_PATHS entry and every gate command actually EXISTS
# under the resolved root, and ABORTS (exit 2) naming the missing path. A
# runner that cannot find what it is judging must refuse to start, never
# report green.
# ==========================================================================

def read_kit_config(start: Path) -> dict:
    """kit.config, found the same 4 ways the hook finds it, then overlaid with
    kit.config.local from the same directory:

        1. $KIT_CONFIG
        2. ./kit.config              (current working directory)
        3. <this file's dir>/kit.config
        4. the nearest kit.config walking UP from this file's directory

    kit.config is COMMITTED and holds repo-relative values; kit.config.local
    is GITIGNORED and holds the absolute and protected ones. The overlay is
    what lets the committed file be honest about paths without leaking a
    machine layout."""
    cands: list[Path] = []
    env = os.environ.get("KIT_CONFIG")
    if env:
        cands.append(Path(env))
        # A $KIT_CONFIG pointing at nothing is the quietest possible way to run
        # on defaults while believing you configured something. The fixture
        # harness warns about it; so does this, on stderr, so a piped run still
        # certifies but nobody is left guessing which config it used.
        try:
            if not Path(env).is_file():
                print(f"CONFIG WARNING: $KIT_CONFIG points at {env!r}, which "
                      f"is not a file - falling through to the search order.",
                      file=sys.stderr)
        except OSError:
            pass
    cands.append(Path.cwd() / "kit.config")
    cands.append(start / "kit.config")
    cands.extend(d / "kit.config" for d in start.parents)

    cfg: dict[str, str] = {}
    for c in cands:
        try:
            if not c.is_file():
                continue
        except OSError:
            continue
        for path in (c, c.with_name("kit.config.local")):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            for line in text.splitlines():
                line = line.split("#", 1)[0].strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip()
        cfg["_source"] = str(c)
        return cfg
    return cfg


def find_repo_root(start: Path, has_git, cfg_root: str = ""):
    """(root, how). Pure given `has_git`, so --selftest walks every branch."""
    for d in [start, *start.parents]:
        if has_git(d):
            return d, "the nearest ancestor containing .git"
    if cfg_root:
        return Path(cfg_root), "PROJECT_ROOT from kit.config"
    return start, ("this file's own directory - NO .git ancestor and NO "
                   "PROJECT_ROOT in kit.config")


_HERE = Path(__file__).resolve().parent
_CFG = read_kit_config(_HERE)
REPO, REPO_HOW = find_repo_root(
    _HERE, lambda d: (d / ".git").exists(), _CFG.get("PROJECT_ROOT", ""))

# ---- SLOTS ---------------------------------------------------------------
# ALL PATHS BELOW ARE REPO-RELATIVE, resolved against the root discovered
# above. When you copy this runner into <repo>/tools/, these six constants
# are the ONLY things you must change - and if you forget, the startup
# assertion aborts naming exactly what is missing rather than certifying air.

# THE JUDGE SURFACE: paths whose contents decide what "green" MEANS. An
# uncommitted edit to any of them invalidates certification, because the run
# would be judging the tree by rules that are not in the tree.
#
# NARROW THIS. The tempting value is "tools", and it is usually wrong: a whole
# tools directory sweeps in scratch scripts, formatting passes and cosmetics,
# so certification starts failing for reasons that have nothing to do with
# judgement, and people learn to work around the gate. Name the actual judge
# FILES.
#
# AND INCLUDE THE CONFIG. **The config that parameterises the judges is itself
# a judge.** This list shipped without `kit.config` in it, and the hole was
# measured: an UNCOMMITTED `FORBIDDEN_SPAWN_TIER = nothing-is-forbidden` gave a
# clean `VERIFY: PASS`, with the hooks gate still reporting that the rules
# "decide correctly" - because the fixture that guards that rule reads its
# expected value from the same file it is guarding. Fixture and rule mutate in
# lockstep, so the fixture cannot see the change.
#
# The hole was per-key, not total: weakening MODEL_EXEMPT_TYPES IS caught,
# because fixture c's payload is hard-coded and the hook's answer moves out
# from under it. That is exactly why listing the file is the fix rather than
# hardening one fixture - the general statement is "an uncommitted edit to
# anything that decides what green MEANS invalidates the run", and only the
# judge surface can make it for every key at once.
JUDGE_PATHS = [
    "modules/03-verification/verify.py",
    "modules/03-verification/examples",
    "modules/02-enforcement/hook_model_gate.py",
    "modules/02-enforcement/hook_fixtures.py",
    ".claude/settings.json",
    "kit.config",
    # The expectation-source registry parameterises the self-reference lint the
    # same way kit.config parameterises the hook: an uncommitted waiver added
    # here would silence a check while the run still certified. Instance 4,
    # avoided rather than repeated.
    "checks-registry.json",
]

# THE CERTIFIED TREE: the paths the gates are actually about. Deliberately
# narrower than the whole repo - a docs commit must not invalidate a
# certification, or nobody will keep the token honest.
CERT_PATHS = ["modules/03-verification/examples"]

# The enforcement module, for the `hooks` gate. In an adopting repo both of
# these become "tools/hook_fixtures.py" and your harness's settings file.
HOOK_FIXTURES = "modules/02-enforcement/hook_fixtures.py"
HOOK_SETTINGS = ".claude/settings.json"

# The ledgers module, for the `escapes` gate. Both of these ship with the
# KIT's own values, exactly the way JUDGE_PATHS and HOOK_FIXTURES do: in an
# adopting repo they become "tools/escape_rate.py" and
# "docs/JUDGMENT-LEDGER.md" (your LEDGERS_DIR, your judgment ledger). The kit
# is not an adoption, and its own escape-rate table lives in KNOWN-ISSUES.md.
#
# THE LEDGER IS DELIBERATELY NOT IN JUDGE_PATHS. That list holds what decides
# *what green means*; the ledger is the SUBJECT this gate measures. Put it in
# the judge surface and every ordinary ledger append invalidates
# certification, which is how a gate gets routed around. The thing that does
# decide green here - the ceiling in the gate table below - is in THIS file,
# which IS in JUDGE_PATHS, so lowering it is a reviewed commit. The residual
# is stated in KNOWN-ISSUES: an uncommitted edit to the table can move the
# published number inside a single run, and the compensating control is that
# the number is printed on every certification, not that it is proven.
ESCAPE_TOOL = "modules/04-ledgers/escape_rate.py"
ESCAPE_LEDGER = "KNOWN-ISSUES.md"
# --------------------------------------------------------------------------

RESET, RED, GREEN, YELLOW, CYAN, BOLD = (
    "\033[0m", "\033[31m", "\033[32m", "\033[33m", "\033[36m", "\033[1m")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass
if os.name == "nt":
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
    except Exception:
        RESET = RED = GREEN = YELLOW = CYAN = BOLD = ""


def c(color: str, s: str) -> str:
    return f"{color}{s}{RESET}"


# ==========================================================================
# THE GATE TABLE
# ==========================================================================
# cmd           argv list, run from REPO. Absent for COMPUTED gates.
# timeout       seconds. A gate that hangs is a gate that failed.
# require       THE REQUIRED OUTPUT LINE, as a regex.
# fail_pattern  a veto: matches anywhere in the log and the gate is red even
#               if the required line is present.
# expect_min    THE FLOOR, asserted on min_group AFTER the regex passes.
# ceilings      [(group, max, label)] - a number that must not GROW. A second
#               warning is a new unratified warning: look at it, do not absorb
#               it.
# require_also  [(pattern, label)] - a component line that must ALSO appear.
#               A summary that passes without its component step is a summary
#               that certifies nothing.
# head          callable(match) -> the short string printed in the summary.
GATES = {
    # ---- KEEP THIS ONE -------------------------------------------------
    # Not an example. Certification is a property of a TREE: if the judge
    # surface is dirty, the gates below are enforcing rules that exist only in
    # someone's working copy.
    "judges": dict(
        computed=True, timeout=60,
        doc="the judge surface and the certified tree are committed",
    ),

    # ---- MODULE 02 ONLY. No enforcement module? DELETE THIS WHOLE ENTRY
    #      and its RUN_ORDER slot and the two HOOK_* constants. It names
    #      files that ship with module 02, and the startup assertion will
    #      (correctly) refuse to start without them. -------------------
    # The hook is the only code in the project that runs with the authority to
    # stop everything and is never exercised by the work. Nothing calls it in
    # development; nothing fails when it breaks. So certification asks the
    # fixture harness the two questions that matter - is it ARMED (wired at
    # every enforcement point in the settings file) and is it ALIVE (the
    # dead-man clause: silence from a corpse is not consent).
    #
    # --strict is deliberate: a SKIPPED fixture is a fixture that proved
    # nothing, and skipped-as-passed is the easiest way to build a suite that
    # reports green about nothing. The ceiling on group 2 says the same thing
    # a second way, so a future --strict removal still cannot go quiet.
    "hooks": dict(
        cmd=[sys.executable, HOOK_FIXTURES, "--strict", "--armed", HOOK_SETTINGS],
        timeout=180,
        # THREE numbers, and the third is mandatory in the pattern. `n/a` is
        # not a softer `skipped`: skipped means "we could not tell", n/a means
        # "the owner turned this feature off, so there is nothing behind it".
        # The ceiling is on SKIPS ONLY. Requiring the n/a field to be present
        # also means a harness that silently reverts to two-number output
        # fails here instead of quietly losing a distinction.
        require=r"HOOK FIXTURES:\s*(\d+)/\1\s+passed,\s*(\d+)\s+skipped,"
                r"\s*(\d+)\s+n/a",
        fail_pattern=r"UNARMED:|UNSTARTABLE:|DEAD-MAN|HOOK NOT ARMED|CONFIG WARNING",
        expect_min=10, min_group=1, min_label="fixtures",
        ceilings=[(2, 0, "skipped fixtures")],
        head=lambda m: (f"{m.group(1)}/{m.group(1)} armed"
                        + (f", {m.group(3)} n/a" if m.group(3) != "0" else "")),
        doc="the enforcement gate is armed, alive, and decides correctly",
    ),

    # ---- MODULE 04 ONLY. No ledgers module? DELETE THIS WHOLE ENTRY and
    #      its RUN_ORDER slot and the two ESCAPE_* constants. It names a tool
    #      and a ledger that ship with module 04, and the startup assertion
    #      will (correctly) refuse to start without them. ----------------
    # THE HEADLINE METRIC, INSTRUMENTED. The kit's claim is that the loop
    # publishes its own escape rate - an escape being an item a human reported
    # that an existing check should have caught. A claim with no instrument is
    # a slogan, so the number is computed from the ledger's table on every
    # certification and the latest round is held to a ceiling.
    #
    # THE CEILING IS INLINE, LIKE THE FLOORS ABOVE, AND FOR THE SAME REASON:
    # it lives inside the judge surface so that raising it is a reviewed
    # commit rather than a config edit nobody sees. 35.0 is DERIVED from the
    # kit's own twelve counted rounds, not adopted - the arithmetic is in
    # KNOWN-ISSUES.md, "The kit's own numbers". Re-derive it from your own
    # first rounds by the method in modules/04-ledgers/TOKEN-LEDGER.md; a
    # ceiling inherited from somebody else's project is the mistake that
    # document exists to prevent.
    #
    # THERE IS NO `expect_min` HERE, and the omission is deliberate. A floor
    # asks "did enough happen?", and for a metric where LOW IS GOOD the
    # equivalent question is "is there any data at all?" - which cannot be a
    # red, because a project on its first day genuinely has no rounds and a
    # gate that is red until the first round is a gate people learn to skip.
    # The `state` field carries it instead: it is MANDATORY in the pattern
    # below, so `NO-ROUNDS-RECORDED` is published on every certification and a
    # future tool that stopped distinguishing it from a measured zero fails
    # this gate rather than quietly reporting a flattering number.
    "escapes": dict(
        cmd=[sys.executable, ESCAPE_TOOL, "--ledger", ESCAPE_LEDGER,
             "--ceiling", "35.0"],
        timeout=120,
        require=r"ESCAPE RATE:\s*(\d+)/(\d+)\s+items\s+\((\d+\.\d)%\)\s+over\s+"
                r"(\d+)\s+rounds;\s+latest\s+(\d+)/(\d+)\s+\((\d+\.\d)%\);\s+"
                r"ceiling\s+(\d+\.\d)%;\s+state\s+(MEASURED|NO-ROUNDS-RECORDED)",
        fail_pattern=r"OVER CEILING|ESCAPE LEDGER ABORT",
        # Both component lines are REQUIRED, so neither can vanish quietly.
        # The uncounted line is how a dropped round becomes visible; the trend
        # line is the sequence the doctrine actually asks you to read.
        require_also=[
            (r"ESCAPE RATE UNCOUNTED:\s*\d+\s+round\(s\)",
             "the uncounted-rounds line"),
            (r"ESCAPE RATE TREND:", "the trend line"),
        ],
        head=lambda m: (f"{m.group(1)}/{m.group(2)} ({m.group(3)}%)"
                        if m.group(9) == "MEASURED" else "no rounds recorded"),
        doc="the loop publishes its own escape rate and the latest round is "
            "under the ceiling",
    ),

    # ---- REPLACE BOTH OF THESE ----------------------------------------
    "example_unit": dict(
        cmd=[sys.executable, "modules/03-verification/examples/fake_suite.py"],
        timeout=120,
        require=r"example_unit:\s*(\d+)/\1\s+cases passed",
        fail_pattern=r"example_unit:\s*THESE FAILED|\(subset:",
        expect_min=3, min_group=1, min_label="cases",
        head=lambda m: f"{m.group(1)}/{m.group(1)}",
        doc="EXAMPLE - replace with your test suite",
    ),
    "example_lint": dict(
        cmd=[sys.executable, "modules/03-verification/examples/fake_lint.py"],
        timeout=120,
        require=r"example_lint:\s*(\d+)\s+checks,\s*0\s+FAIL,"
                r"\s*(\d+)\s+WARN,\s*(\d+)\s+OK",
        fail_pattern=None,
        expect_min=10, min_group=1, min_label="checks",
        ceilings=[(2, 1, "WARN")],
        require_also=[(r"example_lint:\s*rule set v\d+", "the rule-set banner")],
        head=lambda m: "0 FAIL",
        doc="EXAMPLE - replace with your linter",
    ),
}

# Gates whose verdict is COMPUTED, not pattern-matched. --nc cannot doctor a
# require/fail_pattern/expect_min for these, because nothing would consult it.
COMPUTED_GATES = {"judges"}

# Gates that ask git a question. Named here so the startup assertion can refuse
# to run them outside a work tree, where git's answer ("") is indistinguishable
# from the answer that means everything is fine.
GIT_DEPENDENT_GATES = {"judges"}

# RUN ORDER, and it is deliberate: cheap structural gates first (a red judge
# means the expensive gates would be certifying the wrong tree anyway), then
# fast checks, then slow ones, then anything that needs a screen or a device.
RUN_ORDER = ["judges", "hooks", "escapes", "example_unit", "example_lint"]

NC_KEYS = {"require", "fail_pattern", "expect_min"}


# ==========================================================================
# THE PURE JUDGING LAYER
# Everything above the RUNNING LAYER banner is a pure function of its
# arguments: no clock, no filesystem, no subprocess. That is what makes
# --selftest possible, and keeping it that way is a maintenance rule, not a
# style preference.
# ==========================================================================

def judge_gate(spec: dict, text: str):
    """(ok, headline, detail, line). `line` is the required line, verbatim."""
    pat = spec.get("require")
    if not pat:
        return True, "", "", ""
    try:
        rx = re.compile(pat)
    except re.error as e:
        return False, "BAD REGEX", f"the required pattern does not compile: {e}", ""

    m = rx.search(text)
    if not m:
        detail = (f"required line absent (pattern {pat!r}). A run that died "
                  f"half-way has no required line either - that is the point.")
        # If a veto ALSO matched, name it and quote it. Without this the
        # summary says only "no line", and the reader opens the log to
        # discover the run had announced its own failure two lines in.
        veto = spec.get("fail_pattern")
        if veto:
            try:
                vm = re.search(veto, text)
            except re.error:
                vm = None
            if vm:
                detail += ("\n  ...and the veto pattern " + repr(veto)
                           + " DID match: " + repr(vm.group(0).strip())
                           + " - that is very likely the real story.")
        return False, "NO LINE", detail, ""
    line = m.group(0).strip()

    veto = spec.get("fail_pattern")
    if veto:
        try:
            vm = re.search(veto, text)
        except re.error as e:
            return False, "BAD REGEX", f"the veto pattern does not compile: {e}", line
        if vm:
            return False, "VETOED", (
                f"the required line was present but the veto pattern "
                f"{veto!r} also matched: {vm.group(0).strip()!r}"), line

    mn = spec.get("expect_min")
    if mn is not None:
        g = spec.get("min_group", 1)
        try:
            got = int(m.group(g))
        except (IndexError, TypeError, ValueError):
            return False, "NO NUMBER", (
                "the required line matched but carried no countable number at "
                f"group {g} - the floor cannot be asserted"), line
        if got < mn:
            lbl = spec.get("min_label", "items")
            return False, f"{got} < {mn}", (
                f"FLOOR BREACH: {got} {lbl}, floor {mn}. The line is "
                f"well-formed; the number SHRANK. Either something stopped "
                f"being checked, or the floor is genuinely obsolete and "
                f"lowering it is a reviewed commit."), line

    for (g, mx, lbl) in spec.get("ceilings", []) or []:
        try:
            got = int(m.group(g))
        except (IndexError, TypeError, ValueError):
            continue
        if got > mx:
            return False, f"{lbl} {got} > {mx}", (
                f"CEILING BREACH: {got} {lbl}, ceiling {mx}. A new one is "
                f"unratified: look at it, do not absorb it."), line

    for (pat2, lbl) in spec.get("require_also", []) or []:
        if not re.search(pat2, text):
            return False, "MISSING COMPONENT", (
                f"the summary line passed but {lbl} never appeared "
                f"(pattern {pat2!r}). A summary that passes without its "
                f"component step is a summary that certifies nothing."), line

    head = spec.get("head")
    return True, (head(m) if head else "ok"), "", line


def parse_porcelain(text: str) -> list:
    """`git status --porcelain` -> [(status, path)]. Pure, so --selftest can
    feed it a dirty tree without dirtying one."""
    out = []
    for ln in text.splitlines():
        if len(ln) < 4:
            continue
        out.append((ln[:2].strip(), ln[3:].strip()))
    return out


def judge_tree(porcelain: str, label: str):
    """(ok, headline, detail) for a dirty-tree gate."""
    entries = parse_porcelain(porcelain)
    if not entries:
        return True, "clean", ""
    listing = "\n".join(f"      {s or '??'} {p}" for s, p in entries[:20])
    more = "" if len(entries) <= 20 else f"\n      ... +{len(entries) - 20} more"
    return False, f"{len(entries)} dirty", (
        f"{label} is NOT COMMITTED. Certification is a property of a TREE, not "
        f"of a commit: these files change what the gates mean, and they exist "
        f"only in this working copy.\n{listing}{more}")


def git_answer(rc: int, stdout: str, stderr: str) -> str:
    """THE RETURN CODE IS PART OF THE ANSWER. Pure, so --selftest can prove it.

    `git status` in a directory git has never seen exits 128 and writes NOTHING
    to stdout. Reading only stdout therefore turns "there is no repository
    here" into `""` - the exact byte-for-byte answer that means "everything is
    committed". This runner shipped that defect, and printed
    `VERIFY: PASS (exit 0) - judges clean` over a tree with no .git in it. It
    was the quietest failure in the whole kit: nothing crashed, nothing was
    red, and the certification described a repository that did not exist.

    A failure is converted into a porcelain LINE the existing dirty-tree judge
    already knows how to fail on, rather than into a special case. One judge,
    one way of being red, and the reason quoted verbatim in the output."""
    if rc != 0:
        err = " ".join((stderr or "").split())[:200] or "<no stderr>"
        return (f"?? <git failed rc={rc}: {err}> "
                f"- silence from a failed command is not a clean tree\n")
    return stdout


def looks_like_a_path(arg: str) -> bool:
    """Is this command argument a PATH, or is it a flag's VALUE?

    Asserting the existence of every non-flag argument was a regression that
    shipped: `pwsh -NoProfile -ExecutionPolicy Bypass -File x.ps1` aborted the
    runner, because `Bypass` is not a flag and is not a file either. It is the
    canonical Windows invocation this kit's own config recommends, so the
    assertion refused to start on the configuration the kit advertises.

    The rule now: a flag (leading `-`) is never a path, a bare version-ish
    token is never a path, and anything else must LOOK like one - it contains
    a separator or an extension dot. `Bypass` does not; `.claude/settings.json`
    and `tools\\verify.py` and `suite.py` all do.

    Deliberately permissive. A bare word that really is a filename escapes the
    assertion, and the gate then fails loudly at launch time instead - a worse
    error message, but never a false abort. Refusing to start on a correct
    configuration is the more expensive mistake: it is the one that makes
    people delete the check."""
    if not arg or arg.startswith("-"):
        return False
    if re.fullmatch(r"[\d.]+", arg):           # 4.7.1, 3.12, 0
        return False
    return ("/" in arg) or ("\\" in arg) or ("." in arg)


def git_excluded(repo, rels: list):
    """Which of `rels` does this repo's ignore machinery EXCLUDE?

    Returns (the excluded subset, a note that is non-empty when git could not
    answer). Module level, not nested inside main(), so a test can call it.

    BYTES AND NUL, NOT TEXT AND NEWLINES. The first version of this function
    passed text=True with a newline-joined input. Text-mode stdin translates
    every newline to os.linesep, which on Windows is CR LF, so every path but
    the last reached git with a trailing carriage return. A CR-suffixed path is
    not in the index and does not match an exact-path ignore rule, so the check
    missed the defect it was written for and aborted on correctly tracked files
    at the same time. `-z` reads and writes NUL-separated records, which no
    layer translates, and it also turns off the core.quotePath escaping that
    made the mangled path unreadable in the message.

    Every record is NUL-TERMINATED, not NUL-separated. Both forms are accepted
    by the git this was measured against, and terminating costs nothing; a
    separator-only payload leaves the last path's framing up to the reader,
    and the last path is exactly the one the previous defect spared.

    Do not strip the parsed values. A leading or trailing space is legal in a
    pathname, and stripping one reintroduces the same class of mismatch.

    The answer already accounts for the index: git does not report a TRACKED
    file as ignored, and neither does `git status`, so a tracked file covered
    by a rule is correctly absent from this list."""
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), "check-ignore", "-z", "--stdin"],
            input=b"".join(r.encode("utf-8") + b"\0" for r in rels),
            capture_output=True, timeout=15)
    except Exception as e:
        return [], f"git could not be run: {e!r}"
    # 0 = at least one path excluded, 1 = none. Anything else is an error, and
    # an error is not an answer.
    if p.returncode not in (0, 1):
        err = " ".join((p.stderr or b"").decode("utf-8", "replace").split())
        return [], f"git check-ignore exited {p.returncode}: {err[:120]}"
    return [x.decode("utf-8", "replace")
            for x in (p.stdout or b"").split(b"\0") if x], ""


def startup_problems(repo, judge_paths, cert_paths, gates, run_order,
                     exists, is_git_worktree=None, ignored=None) -> list:
    """THE STARTUP ASSERTION. Pure: `exists` is a callable(repo-relative str)
    -> bool, `is_git_worktree` a callable() -> bool, and `ignored` a
    callable(list of repo-relative str) -> (the subset git excludes, a note
    that is non-empty when git could not answer). So --selftest walks every
    branch without touching a filesystem.

    Every path this runner is ABOUT must exist under the resolved root before
    a single gate runs. Without this check a mis-resolved root produces the
    worst outcome available - not a crash, not a red gate, but a clean green
    describing nothing at all. `git status -- <path that does not exist>`
    prints nothing and exits 0, and "nothing" is how "clean" is spelled.

    THE SECOND HALF OF THE SAME LESSON: `git status` in a directory git has
    never seen exits 128 with EMPTY stdout, which reads identically. So when a
    git-dependent gate is selected, the root must actually BE a git work tree.
    Both halves are needed - one catches the wrong tree, the other catches no
    tree at all.

    THE THIRD CASE, and the same lesson again: a path can exist, in a real
    work tree, and still be invisible to `git status` - because the repo's own
    `.gitignore` excludes it. `.claude/` is a common entry in a pre-existing
    ignore file, and an excluded `.claude/settings.json` makes
    `git status --porcelain -- <it>` print nothing whatever the file says. The
    judges gate then reads clean over the settings file that decides whether
    the hooks run at all, and the run certifies a disarmed harness.

    The exclusion probe is asked only when a git-dependent gate is selected,
    because that is the only gate an exclusion can lie to, and only when the
    root IS a work tree - outside one, "there is no repository here" is the
    diagnosis the adopter needs, and a probe that also fails would put a
    misleading line above it. It reports only UNTRACKED paths: git's exclude
    machinery does not apply the rules to a file already in the index, and
    neither does `git status`, so a tracked file matched by an ignore rule is
    judged normally and is not a problem here.

    Returns a list of human-readable problems; empty means go."""
    out = []
    for p in judge_paths:
        if not exists(p):
            out.append(f"JUDGE_PATHS entry {p!r} does not exist under {repo}")
    for p in cert_paths:
        if not exists(p):
            out.append(f"CERT_PATHS entry {p!r} does not exist under {repo}")
    for name in run_order:
        for arg in (gates.get(name, {}).get("cmd") or [])[1:]:
            a = str(arg)
            if not looks_like_a_path(a):
                continue
            if not exists(a):
                out.append(f"gate {name!r} names {a!r}, which does not exist "
                           f"under {repo}")
    git_gates = [n for n in run_order if n in GIT_DEPENDENT_GATES]
    # ORDER MATTERS HERE. The work-tree question is asked and reported FIRST,
    # and a false answer suppresses the exclusion probe: outside a repository
    # `git check-ignore` also fails, and its note would tell a reader whose
    # only problem is "there is no repo here" to suspect their git install.
    in_worktree = None if is_git_worktree is None else is_git_worktree()
    if git_gates and in_worktree is False:
        out.append(
            f"{repo} is not a git work tree, but the {', '.join(git_gates)} "
            f"gate(s) judge git state. In a non-repo `git status` exits 128 "
            f"with EMPTY output, which is indistinguishable from a clean tree "
            f"- so this run would report 'judges clean' about a tree git has "
            f"never seen. Run `git init`, or --skip {','.join(git_gates)} and "
            f"accept that nothing is checking whether the tree is committed.")
    judged = list(judge_paths) + list(cert_paths)
    ask_git = (git_gates and judged and ignored is not None
               and in_worktree is not False)
    if ask_git:
        excluded, note = ignored(judged)
        if note:
            out.append(
                f"git could not say whether the judged paths are excluded by "
                f"this repo's ignore rules ({note}). An excluded path is "
                f"invisible to `git status`, so the {', '.join(git_gates)} "
                f"gate(s) would read clean over it - and this runner will not "
                f"guess. Fix the git installation or the repo, or --skip "
                f"{','.join(git_gates)} and accept that nothing is checking "
                f"whether the tree is committed.")
        for p in excluded:
            out.append(
                f"judged path {p!r} is EXCLUDED by this repo's ignore rules "
                f"and is not tracked, so `git status --porcelain -- {p}` "
                f"prints nothing whatever the file says and the "
                f"{', '.join(git_gates)} gate(s) would read clean over it "
                f"forever. FIX, IN THIS ORDER: (1) `git add -f {p}` and "
                f"commit it - force-tracking this one file leaves the ignore "
                f"rule intact, and `adoption_smoke.py` phase 12 proves it "
                f"clears this abort; (2) if you want to know which rule it "
                f"was, run `git check-ignore -v {p}` BEFORE step (1) - a "
                f"tracked path reports nothing; (3) remove that rule ONLY if it covers nothing "
                f"else - on an existing repository a directory rule such as "
                f"`.claude/` usually also covers session state and the "
                f"certification token, and removing it commits both.")
    return out


def decide_verdict(nc_active: bool, red: list, not_run: list):
    """THE CONTRACT, in one pure function. PASS is returned from exactly one
    line in this program, and this is it."""
    if nc_active:
        return "INSTRUMENTED", 2
    if red:
        return "FAIL", 1
    if not_run:
        return "PARTIAL", 3
    return "PASS", 0


def not_run_gates(by: dict) -> list:
    return [g for g in RUN_ORDER if g not in by]


def cert_token_path(rel: str, repo, default: str):
    """Where the token goes. Pure, because getting it wrong is silent: a token
    written somewhere the hook does not look leaves the tripwire asking
    forever, which is safe and indistinguishable from a feature that works and
    has not been needed. An absolute path is taken as given; anything else is
    repo-relative, which is how every other path in this runner is read."""
    p = Path(rel or default)
    return p if p.is_absolute() else Path(repo) / p


def cert_token_payload(sha: str, headlines: list, minted_at: str) -> dict:
    """The cert-green token's contents. Pure, so --selftest can read the label.

    WHY THE RUNNER MINTS IT. The enforcement hook's protected-path tripwire
    reads this file and pre-authorises writes while the certification still
    describes the tree. Until now the file was written by hand, which made the
    one control that converts a human prompt into an automatic allow a
    NARRATED claim - the exact thing this kit's own doctrine retired. Minting
    it here, from the single line that returns PASS, means the ordinary way to
    hold a token is to have certified.

    WHY THERE IS NO SIGNATURE, and why the `label` field says so out loud. An
    HMAC needs a key. The agents this token governs run shell commands as the
    owner, with the owner's filesystem and the owner's environment, so there is
    nowhere to put a key they cannot read: not an environment variable, not a
    file outside the repository, not the settings file. A signature would raise
    forgery from "write a file" to "read a file, then write a file" while
    making the token read as an attestation it is not. The honest control at
    this privilege level is the label, so the label ships INSIDE the artifact,
    where the next reader of the file will find it."""
    return {
        "sha": sha,
        "minted_at": minted_at,
        "minted_by": "verify.py --mint-cert-token",
        "verdict": "PASS",
        "gates": list(headlines),
        "label": ("CONVENIENCE, NOT AUTHORIZATION. This file records that a "
                  "certification run returned PASS over the named sha. It is "
                  "unsigned and unsignable at this privilege level: anything "
                  "that can write a file can write this one, including the "
                  "agents the protected-path tripwire governs. Treat a token "
                  "as evidence of a run, never as proof of one."),
    }


def summary_line(verdict: str, code: int, heads: list, red: list,
                 skipped: list, elapsed: str) -> str:
    bits = " · ".join(heads) if heads else "no gate produced a headline"
    s = f"VERIFY: {verdict} (exit {code}) — {bits}"
    if red:
        s += f" — RED: {', '.join(red)}"
    if skipped:
        s += f" — NOT RUN: {', '.join(skipped)}"
    if verdict == "INSTRUMENTED":
        s += " — NEGATIVE CONTROL ACTIVE, this run certifies nothing"
    if verdict == "PARTIAL":
        s += " — every gate that ran was green; this is NOT a certification"
    if elapsed:
        s += f" — {elapsed}"
    return s


def validate_nc(nc) -> str:
    """Refuse an override table that looks like a negative control and
    controls nothing. Returns an error message, or '' when valid."""
    if not isinstance(nc, dict):
        return "--nc file must contain a JSON object"
    # Keys beginning with "_" are comments. JSON has none, and a negative
    # control that cannot explain itself gets copied without being understood.
    unknown = {k for k in nc if not k.startswith("_")} - NC_KEYS
    if unknown:
        return (f"--nc: unknown key(s) {sorted(unknown)}; allowed: "
                f"{sorted(NC_KEYS)}")
    for key in NC_KEYS:
        tbl = nc.get(key)
        if tbl is None:
            continue
        if not isinstance(tbl, dict):
            return f"--nc: {key} must be an object mapping gate -> override"
        for gate, v in tbl.items():
            if gate not in GATES:
                return (f"--nc: unknown gate {gate!r} in {key}; known gates: "
                        f"{sorted(GATES)}")
            if gate in COMPUTED_GATES:
                return (f"--nc: gate {gate!r} is judged by computation, not by "
                        f"a required output line, so a {key} override would be "
                        f"silently ignored - and an override that is silently "
                        f"ignored is worse than no override.")
            if key == "expect_min" and not isinstance(v, int):
                return f"--nc: expect_min[{gate!r}] must be an integer, got {v!r}"
            if key != "expect_min" and not isinstance(v, str):
                return f"--nc: {key}[{gate!r}] must be a string, got {v!r}"
    return ""


# ==========================================================================
# THE RUNNING LAYER  (impure below this line)
# ==========================================================================

class Result:
    def __init__(self, name: str):
        self.name = name
        self.ok = False
        self.headline = ""
        self.detail = ""
        self.line = ""
        self.seconds = 0.0
        self.log: Path | None = None


def run_cmd(cmd, cwd: Path, timeout: float, log_path: Path):
    """Returns (text, timed_out, rc). Output is streamed to a log file: a
    20-minute gate that reports nothing until the end reads exactly like a
    hang, and someone will kill it."""
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                           timeout=timeout)
        text = (p.stdout.decode("utf-8", "replace")
                + p.stderr.decode("utf-8", "replace"))
        rc, to = p.returncode, False
    except subprocess.TimeoutExpired as e:
        text = ((e.stdout or b"").decode("utf-8", "replace")
                + (e.stderr or b"").decode("utf-8", "replace"))
        rc, to = -1, True
    except Exception as e:
        text, rc, to = f"launch failed: {e!r}", -1, False
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ {' '.join(str(x) for x in cmd)}\n"
        f"(rc={rc} timed_out={to} {time.time() - t0:.1f}s)\n\n{text}",
        encoding="utf-8")
    return text, to, rc


def gate_judges(ctx, r: Result) -> None:
    """COMPUTED. Two dirty-tree questions, and they are different questions:
    the judge surface (what green MEANS) and the certified tree (what is BEING
    certified)."""
    def porcelain(paths):
        try:
            p = subprocess.run(
                ["git", "-C", str(ctx.repo), "status", "--porcelain", "--", *paths],
                capture_output=True, text=True, timeout=30)
        except Exception as e:
            return git_answer(-1, "", f"git could not be run: {e!r}")
        return git_answer(p.returncode, p.stdout, p.stderr)

    ok1, h1, d1 = judge_tree(porcelain(JUDGE_PATHS), "THE JUDGE SURFACE")
    ok2, h2, d2 = judge_tree(porcelain(CERT_PATHS), "THE CERTIFIED TREE")
    r.ok = ok1 and ok2
    r.headline = "clean" if r.ok else f"judges {h1}, tree {h2}"
    r.detail = "\n".join(x for x in (d1, d2) if x)
    r.line = f"judge-paths {h1}; cert-paths {h2}"


def gate_cmd(ctx, r: Result) -> None:
    spec = ctx.spec(r.name)
    log = ctx.out / "logs" / f"{r.name}.log"
    text, timed_out, rc = run_cmd(spec["cmd"], ctx.repo, spec["timeout"], log)
    r.log = log
    if timed_out:
        r.ok, r.headline = False, "TIMEOUT"
        r.detail = (f"no verdict after {spec['timeout']}s. A gate that hangs is "
                    f"a gate that failed; raising the timeout is a decision, "
                    f"not a fix.")
        return
    r.ok, r.headline, r.detail, r.line = judge_gate(spec, text)


class Ctx:
    def __init__(self, repo: Path, out: Path, nc: dict | None):
        self.repo = repo
        self.out = out
        self.nc = nc or {}
        self.nc_active = nc is not None

    def spec(self, name: str) -> dict:
        s = dict(GATES[name])
        for key in NC_KEYS:
            tbl = self.nc.get(key) or {}
            if name in tbl:
                s[key] = tbl[name]
        return s


RUNNERS = {"judges": gate_judges}


# --------------------------------------------------------------------------
# --selftest : the runner proving its own judges
# --------------------------------------------------------------------------
def selftest() -> int:
    ok_all = True
    n = 0
    ran: list[str] = []      # the labels of the checks that ACTUALLY ran

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        ran.append(label)
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    # ---------------------------------------------------------------
    # SECTIONS A AND B ARE ABOUT THE EXAMPLE GATES, AND THE EXAMPLE GATES ARE
    # MEANT TO BE DELETED (QUICKSTART Step 4). They are therefore GUARDED: a
    # bare GATES["example_unit"] here crashed the whole selftest with a
    # KeyError the moment an adopter did what the QUICKSTART told them to do,
    # which is a runner that punishes correct adoption.
    #
    # Deleting them does NOT reduce your coverage silently - section I asserts
    # that every gate in RUN_ORDER is exercised by at least one check below,
    # so a replacement gate with no selftest goes loudly red.
    # ---------------------------------------------------------------
    if "example_unit" in GATES and "example_lint" in GATES:
        print(c(BOLD, "=== A. the required lines, as a green run prints them ==="))
        unit_ok = "example_unit: 4/4 cases passed\n"
        lint_ok = ("example_lint: rule set v1\n"
                   "example_lint: 12 checks, 0 FAIL, 1 WARN, 11 OK\n")
        check("example_unit: a green line passes",
              judge_gate(GATES["example_unit"], unit_ok)[0], True)
        check("example_lint: a green line passes",
              judge_gate(GATES["example_lint"], lint_ok)[0], True)
        check("example_unit: the headline is the ratio",
              judge_gate(GATES["example_unit"], unit_ok)[1], "4/4")

        print(c(BOLD, "\n=== B. the ways a green line is not a green run ==="))
        check("a SHRUNK count breaches the floor",
              judge_gate(GATES["example_unit"], "example_unit: 2/2 cases passed")[0],
              False)
        check("...and the detail says FLOOR BREACH",
              "FLOOR BREACH" in
              judge_gate(GATES["example_unit"], "example_unit: 2/2 cases passed")[2],
              True)
        check("ZERO of zero is a catastrophe, not a pass",
              judge_gate(GATES["example_unit"], "example_unit: 0/0 cases passed")[0],
              False)
        check("a PARTIAL ratio does not match the backreference",
              judge_gate(GATES["example_unit"], "example_unit: 3/4 cases passed")[0],
              False)
        check("an ABSENT line fails",
              judge_gate(GATES["example_unit"], "everything went fine!")[0], False)
        check("...and says the line is absent",
              "required line absent" in
              judge_gate(GATES["example_unit"], "everything went fine!")[2], True)
        check("the VETO fires even with the required line present",
              judge_gate(GATES["example_unit"],
                         unit_ok + "example_unit: THESE FAILED: x\n")[0], False)
        check("a SUBSET run may not certify",
              judge_gate(GATES["example_unit"],
                         "example_unit: 4/4 cases passed (subset: 4 of 40)")[0],
              False)
        check("a raised CEILING fails (a second WARN is news)",
              judge_gate(GATES["example_lint"],
                         "example_lint: rule set v1\n"
                         "example_lint: 12 checks, 0 FAIL, 2 WARN, 10 OK")[0], False)
        check("a missing COMPONENT line fails the summary",
              judge_gate(GATES["example_lint"],
                         "example_lint: 12 checks, 0 FAIL, 1 WARN, 11 OK")[0], False)
        check("a FAIL count is not matched at all",
              judge_gate(GATES["example_lint"],
                         "example_lint: rule set v1\n"
                         "example_lint: 12 checks, 3 FAIL, 1 WARN, 8 OK")[0], False)
        check("a doctored (uncompilable) pattern fails loudly",
              judge_gate({"require": "([unclosed"}, "anything")[1], "BAD REGEX")
    else:
        print(c(YELLOW, "=== A/B skipped: the example gates have been "
                        "replaced, which is correct. Section I checks that "
                        "their replacements are covered. ==="))


    # ---- the `escapes` gate ------------------------------------------
    # GUARDED the same way A/B are: module 04 is separately adoptable, and a
    # bare GATES["escapes"] would crash the whole bench for anyone who did
    # what the docstring tells them to do. Section I still asserts coverage.
    #
    # THE EXPECTATION HERE IS AN INLINE LITERAL, HAND-WRITTEN, and it is a
    # SECOND transcription of a contract whose first transcription lives in
    # escape_rate.py's own selftest. That duplication is deliberate: two
    # independent hand-written copies of one line format cannot drift
    # together, and if they drift apart the live gate goes red in CI. Reading
    # the expectation out of the tool would be the self-reference class this
    # kit's `expectation_lint.py` exists to surface.
    if "escapes" in GATES:
        print(c(BOLD, "\n=== B2. the `escapes` gate: the headline metric ==="))
        esc_ok = ("ESCAPE RATE UNCOUNTED: 1 round(s) declared uncountable\n"
                  "ESCAPE RATE TREND: 42.9 -> 15.4; direction FALLING\n"
                  "ESCAPE RATE: 26/120 items (21.7%) over 12 rounds; latest "
                  "0/1 (0.0%); ceiling 35.0%; state MEASURED\n")
        esc_new = ("ESCAPE RATE UNCOUNTED: 0 round(s) declared uncountable\n"
                   "ESCAPE RATE TREND: (none); direction INSUFFICIENT-DATA\n"
                   "ESCAPE RATE: 0/0 items (0.0%) over 0 rounds; latest 0/0 "
                   "(0.0%); ceiling 35.0%; state NO-ROUNDS-RECORDED\n")
        check("escapes: a measured run passes",
              judge_gate(GATES["escapes"], esc_ok)[0], True)
        check("escapes: the headline is the published rate",
              judge_gate(GATES["escapes"], esc_ok)[1], "26/120 (21.7%)")
        check("escapes: a day-one project with NO ROUNDS still passes - a "
              "gate that is red until the first round is a gate people skip",
              judge_gate(GATES["escapes"], esc_new)[0], True)
        check("...and its headline SAYS so rather than reading as a score",
              judge_gate(GATES["escapes"], esc_new)[1], "no rounds recorded")
        check("escapes NC: a breach is vetoed even with the required line "
              "present",
              judge_gate(GATES["escapes"], esc_ok + "ESCAPE RATE: OVER "
                         "CEILING — latest round r19 5/8 (62.5%)\n")[0], False)
        check("escapes NC: an ABORT is vetoed - a missing ledger must never "
              "read as a good score",
              judge_gate(GATES["escapes"],
                         "ESCAPE LEDGER ABORT: no ledger at docs/x.md\n")[0],
              False)
        check("escapes NC: DROPPING the state word fails the pattern",
              judge_gate(GATES["escapes"],
                         esc_ok.split("; state")[0] + "\n")[0], False)
        check("escapes NC: losing the uncounted line fails, so a quietly "
              "dropped round cannot go unpublished",
              judge_gate(GATES["escapes"], "\n".join(
                  l for l in esc_ok.splitlines()
                  if "UNCOUNTED" not in l))[0], False)
        check("escapes NC: losing the trend line fails too",
              judge_gate(GATES["escapes"], "\n".join(
                  l for l in esc_ok.splitlines()
                  if "TREND" not in l))[0], False)
        check("escapes NC: an ABSENT required line fails",
              judge_gate(GATES["escapes"], "all good here!\n")[0], False)

    print(c(BOLD, "\n=== C. the dirty-tree judge (the `judges` gate) ==="))
    check("a clean porcelain parses to nothing", parse_porcelain(""), [])
    check("porcelain parses status and path",
          parse_porcelain(" M verify.py\n?? scratch.txt\n"),
          [("M", "verify.py"), ("??", "scratch.txt")])
    check("the judges gate: a dirty judge surface is RED",
          judge_tree(" M verify.py\n", "THE JUDGE SURFACE")[0], False)
    check("...and names the file",
          "verify.py" in judge_tree(" M verify.py\n", "X")[2], True)
    check("a clean surface is green", judge_tree("", "X")[0], True)

    # MAJOR-2. The config PARAMETERISES the judges, so it IS one. Left out of
    # JUDGE_PATHS, an uncommitted `FORBIDDEN_SPAWN_TIER = nothing-is-forbidden`
    # produced a clean PASS with the hooks gate still reporting that the rules
    # decide correctly - because the fixture guarding that rule reads its
    # expectation from the very file being weakened. They move together, so
    # the fixture is blind to it. Only the judge surface catches every key.
    check("the config that parameterises the judges is IN the judge surface",
          any(j == "kit.config" or j.endswith("/kit.config")
              for j in JUDGE_PATHS), True)
    check("an uncommitted config edit is therefore a RED tree",
          judge_tree(" M kit.config\n", "THE JUDGE SURFACE")[0], False)
    check("...and the gate names the file that changed",
          "kit.config" in judge_tree(" M kit.config\n", "X")[2], True)

    # NIT-3: an absent required line AND a matched veto.
    _nl = judge_gate({"require": r"ALL (\d+) PASSED",
                      "fail_pattern": r"FATAL: .*"},
                     "starting\nFATAL: the device was not found\n")
    check("an absent line PLUS a matched veto surfaces the veto",
          "FATAL: the device was not found" in _nl[2], True)
    check("...and still reports NO LINE as the headline", _nl[1], "NO LINE")
    check("an absent line with NO veto match stays a plain absence",
          "DID match" in judge_gate({"require": r"ALL (\d+) PASSED",
                                     "fail_pattern": r"FATAL"},
                                    "nothing to see")[2], False)

    # THE NON-GIT FALSE GREEN. `git status` outside a work tree exits 128 with
    # EMPTY stdout, which is byte-identical to "everything is committed".
    check("git rc=0 passes its stdout through untouched",
          git_answer(0, " M a.py\n", ""), " M a.py\n")
    check("git rc=0 with empty stdout really is clean",
          judge_tree(git_answer(0, "", ""), "X")[0], True)
    check("git rc=128 (no repository) becomes a porcelain line, not silence",
          judge_tree(git_answer(128, "", "fatal: not a git repository"),
                     "THE CERTIFIED TREE")[0], False)
    check("...and the failure reason is quoted in the detail",
          "not a git repository" in
          judge_tree(git_answer(128, "", "fatal: not a git repository"), "X")[2],
          True)
    check("...and it names the return code",
          "rc=128" in git_answer(128, "", "fatal: not a git repository"), True)
    check("a crashed git with no stderr still reds",
          judge_tree(git_answer(-1, "", ""), "X")[0], False)

    print(c(BOLD, "\n=== D. the verdict matrix, every branch ==="))
    matrix = [
        # (nc_active, red, not_run) -> (verdict, code)
        ((False, [], []), ("PASS", 0)),
        ((False, ["a"], []), ("FAIL", 1)),
        ((False, [], ["b"]), ("PARTIAL", 3)),
        ((False, ["a"], ["b"]), ("FAIL", 1)),
        ((True, [], []), ("INSTRUMENTED", 2)),
        ((True, ["a"], []), ("INSTRUMENTED", 2)),
        ((True, [], ["b"]), ("INSTRUMENTED", 2)),
        ((True, ["a"], ["b"]), ("INSTRUMENTED", 2)),
    ]
    for args, want in matrix:
        check(f"verdict{args}", decide_verdict(*args), want)
    check("PASS is unreachable while instrumented",
          any(decide_verdict(True, r_, s_)[0] == "PASS"
              for r_ in ([], ["a"]) for s_ in ([], ["b"])), False)

    print(c(BOLD, "\n=== E. the summary line says which kind of green ==="))
    check("PARTIAL says it is not a certification",
          "NOT a certification" in
          summary_line("PARTIAL", 3, ["4/4"], [], ["example_lint"], ""), True)
    check("INSTRUMENTED says it certifies nothing",
          "certifies nothing" in
          summary_line("INSTRUMENTED", 2, [], [], [], ""), True)
    check("FAIL names the red gates",
          "RED: example_unit" in
          summary_line("FAIL", 1, [], ["example_unit"], [], ""), True)

    print(c(BOLD, "\n=== F. the negative-control table refuses nonsense ==="))
    # These checks are about validate_nc, NOT about any particular gate - so
    # they resolve a live gate name at runtime instead of naming one. Three of
    # them used to hard-code "example_unit", which meant the module README's
    # own adaptation step ("delete the example gates") reddened the bench one
    # step after the file promised deletion was safe. A test that names an
    # example is a test that expires when the example does.
    LIVE = next((g for g in GATES if g not in COMPUTED_GATES), None)
    if LIVE is None:
        print(c(YELLOW, "  (no pattern-judged gate exists; F needs one)"))
    else:
        check("a valid table validates",
              validate_nc({"expect_min": {LIVE: 99999}}), "")
        check("an _underscore key is a comment, not an error",
              validate_nc({"_comment": "why this table exists",
                           "expect_min": {LIVE: 9}}), "")
        check("expect_min must be an integer",
              "must be an integer" in
              validate_nc({"expect_min": {LIVE: "lots"}}), True)
    check("an unknown key is refused",
          validate_nc({"nonsense": {}}).startswith("--nc: unknown key"), True)
    check("an unknown gate is refused",
          "unknown gate" in validate_nc({"require": {"nope": "x"}}), True)
    COMPUTED = next(iter(COMPUTED_GATES), None)
    if COMPUTED:
        check("a COMPUTED gate cannot be doctored",
              "judged by computation" in
              validate_nc({"require": {COMPUTED: "x"}}), True)
    check("a non-object table is refused",
          validate_nc(["a", "list"]).startswith("--nc file must"), True)

    print(c(BOLD, "\n=== G. not_run bookkeeping ==="))
    check("a full run leaves nothing unrun",
          not_run_gates({g: 1 for g in RUN_ORDER}), [])
    check("a subset run names what did not run",
          not_run_gates({"judges": 1}), [g for g in RUN_ORDER if g != "judges"])

    print(c(BOLD, "\n=== H. WHERE IS THE REPO, and the startup assertion ==="))
    # F1's two halves. The first discovers the root; the second refuses to run
    # when the discovered root does not contain what we claim to be judging.
    check("repo root is the nearest .git ancestor",
          find_repo_root(Path("/a/b/tools"), lambda d: d == Path("/a/b"))[0],
          Path("/a/b"))
    check("...and it says how it was found",
          find_repo_root(Path("/a/b/tools"), lambda d: d == Path("/a/b"))[1],
          "the nearest ancestor containing .git")
    check("no .git anywhere -> PROJECT_ROOT from kit.config",
          find_repo_root(Path("/a/b/tools"), lambda d: False, "/cfg/root"),
          (Path("/cfg/root"), "PROJECT_ROOT from kit.config"))
    check("no .git and no config -> this file's dir, and it SAYS so",
          "NO .git ancestor" in
          find_repo_root(Path("/a/b/tools"), lambda d: False)[1], True)

    present = {"src", "tools/hook_fixtures.py", ".claude/settings.json",
               "src/suite.py"}
    g_ok = {"g1": dict(cmd=["python", "src/suite.py"]),
            "hooks": dict(cmd=["python", "tools/hook_fixtures.py", "--strict",
                               "--armed", ".claude/settings.json"])}
    check("everything present -> no problems, the run proceeds",
          startup_problems("/r", ["src"], ["src"], g_ok, ["g1", "hooks"],
                           lambda x: x in present), [])
    check("a missing JUDGE_PATHS entry is caught and NAMED",
          startup_problems("/r", ["judge.py"], ["src"], {}, [],
                           lambda x: x in present),
          ["JUDGE_PATHS entry 'judge.py' does not exist under /r"])
    check("a missing CERT_PATHS entry is caught and NAMED",
          len(startup_problems("/r", [], ["nope"], {}, [],
                               lambda x: x in present)), 1)
    # 1 judge path + 1 cert path + g1's script + the hooks gate's two
    # non-flag arguments = 5. Under the old file-relative root, ALL FIVE of
    # these silently resolved to nothing and the run reported green.
    check("THE F1 TRAP: under a mis-resolved root, every path fires",
          len(startup_problems("/wrong", ["src"], ["src"], g_ok,
                               ["g1", "hooks"], lambda x: False)), 5)
    check("a gate naming a script that does not exist is caught",
          "does not exist" in startup_problems(
              "/r", [], [], {"g1": dict(cmd=["python", "gone.py"])}, ["g1"],
              lambda x: x in present)[0], True)
    check("flags are not mistaken for paths (--strict is not a file)",
          startup_problems("/r", [], [], g_ok, ["hooks"],
                           lambda x: x in present), [])
    check("a gate SKIPPED this run is not asserted",
          startup_problems("/r", [], [],
                           {"g1": dict(cmd=["python", "gone.py"])},
                           [], lambda x: False), [])

    # FLAG VALUES ARE NOT PATHS. Asserting every non-flag argument aborted the
    # runner on `pwsh -NoProfile -ExecutionPolicy Bypass -File x.ps1` - the
    # canonical Windows invocation this kit's own config recommends. Refusing
    # to start on a correct configuration is how a check gets deleted.
    check("a flag is not a path", looks_like_a_path("--strict"), False)
    check("`Bypass` is a flag VALUE, not a path",
          looks_like_a_path("Bypass"), False)
    check("a version string is not a path", looks_like_a_path("4.7.1"), False)
    check("a posix path is a path",
          looks_like_a_path(".claude/settings.json"), True)
    check("a windows path is a path",
          looks_like_a_path("tools\\verify.py"), True)
    check("a bare filename with an extension is a path",
          looks_like_a_path("suite.py"), True)
    pwsh = {"g": dict(cmd=["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", "tools/board.ps1"])}
    check("THE Bypass REGRESSION: the canonical pwsh invocation starts",
          startup_problems("/r", [], [], pwsh, ["g"],
                           lambda x: x == "tools/board.ps1"), [])
    check("...and a missing script in that same invocation is still caught",
          len(startup_problems("/r", [], [], pwsh, ["g"], lambda x: False)), 1)

    # THE GIT WORK TREE. The other half of the non-git false green: refuse to
    # RUN a git-judged gate where git cannot answer, instead of believing the
    # empty answer it gives.
    check("a git-dependent gate outside a work tree is refused",
          len(startup_problems("/r", [], [], {}, ["judges"],
                               lambda x: True, lambda: False)), 1)
    check("...and the message says how to proceed anyway",
          "--skip judges" in startup_problems("/r", [], [], {}, ["judges"],
                                              lambda x: True, lambda: False)[0],
          True)
    check("inside a work tree it is fine",
          startup_problems("/r", [], [], {}, ["judges"],
                           lambda x: True, lambda: True), [])
    check("a run with NO git-dependent gate does not need a work tree",
          startup_problems("/r", [], [], {}, ["example_unit"],
                           lambda x: True, lambda: False), [])
    check("an unknown work-tree state (no probe supplied) does not fire",
          startup_problems("/r", [], [], {}, ["judges"], lambda x: True), [])

    # THE GITIGNORED JUDGE PATH. The third way `git status` says nothing and
    # means nothing: the repo's own ignore rules exclude the path, so the
    # judges gate reads clean over a file nobody is judging. `.claude/` is a
    # common entry in a pre-existing ignore file and `.claude/settings.json`
    # is the file that decides whether the hooks run at all.
    #
    # THESE CHECKS COVER THE PURE LAYER ONLY - how startup_problems reacts to
    # a probe's answer. They do NOT cover git_excluded(), the shipped probe
    # that talks to git, and they must never be read as if they did: the first
    # version of that probe corrupted every path it asked about and all seven
    # of these still passed. The control for the shipped probe is
    # `adoption_smoke.py` phase 12, which plants a real ignore rule over a
    # real judge path in a real repository.
    def excluding(*names):
        """A probe that reports exactly `names` as excluded, and answers."""
        return lambda rels: ([r for r in rels if r in names], "")

    ignores_settings = excluding(".claude/settings.json")
    check("a GITIGNORED judge path is caught",
          len(startup_problems("/r", [".claude/settings.json"], [], {},
                               ["judges"], lambda x: True, lambda: True,
                               ignores_settings)), 1)
    check("...and the message NAMES the path and says it is excluded",
          all(s in startup_problems("/r", [".claude/settings.json"], [], {},
                                    ["judges"], lambda x: True, lambda: True,
                                    ignores_settings)[0]
              for s in (".claude/settings.json", "EXCLUDED")), True)
    # THE REMEDY IT PRINTS. P3W-3: the first version of this message told the
    # reader to remove the ignore rule, which on an existing repository is
    # usually a directory rule (`.claude/`) that also covers session state and
    # the certification token - so obeying the message commits both. The
    # surgical remedy is force-tracking the one judged file under the intact
    # rule, and it is the remedy `adoption_smoke.py` phase 12 already proves.
    # These checks bind the message to that order: the fix that works first,
    # the diagnostic second, the rule removal last and conditional.
    _excl_msg = startup_problems("/r", [".claude/settings.json"], [], {},
                                 ["judges"], lambda x: True, lambda: True,
                                 ignores_settings)[0]
    check("...and it prints the SURGICAL remedy - force-track this one file",
          "git add -f .claude/settings.json" in _excl_msg, True)
    check("...FIRST, ahead of the diagnostic and the rule removal",
          (_excl_msg.index("git add -f")
           < _excl_msg.index("git check-ignore")
           < _excl_msg.index("remove that rule")), True)
    check("...and removing the rule is conditional, with the cost named",
          all(s in _excl_msg for s in ("ONLY if it covers nothing else",
                                       "certification token")), True)
    check("THE CONTROL: a tracked judge path starts the run",
          startup_problems("/r", [".claude/settings.json"], [], {}, ["judges"],
                           lambda x: True, lambda: True, excluding()), [])
    check("a gitignored CERT_PATHS entry is caught too",
          len(startup_problems("/r", [], [".claude/settings.json"], {},
                               ["judges"], lambda x: True, lambda: True,
                               ignores_settings)), 1)
    check("git failing to answer is NOT silence",
          "could not say" in startup_problems(
              "/r", [".claude/settings.json"], [], {}, ["judges"],
              lambda x: True, lambda: True,
              lambda rels: ([], "git check-ignore exited 128: boom"))[0], True)
    check("a run with NO git-dependent gate is not asked about exclusions",
          startup_problems("/r", [".claude/settings.json"], [], {},
                           ["example_unit"], lambda x: True, lambda: True,
                           ignores_settings), [])
    check("the pure layer invents no answer when no probe is supplied "
          "(the SHIPPED probe is controlled by adoption_smoke phase 12)",
          startup_problems("/r", [".claude/settings.json"], [], {}, ["judges"],
                           lambda x: True, lambda: True), [])
    # OUTSIDE A WORK TREE, the work-tree problem is the whole diagnosis. The
    # exclusion probe fails there too, and its note above the real answer sent
    # a reader whose repo simply does not exist to suspect their git install.
    outside = startup_problems(
        "/r", [".claude/settings.json"], [], {}, ["judges"], lambda x: True,
        lambda: False, lambda rels: ([], "git check-ignore exited 128: boom"))
    check("a non-git tree reports the work-tree problem and nothing else",
          len(outside), 1)
    check("...and it is the work-tree problem, not a git-install red herring",
          "not a git work tree" in outside[0], True)

    if "hooks" in GATES:
        print(c(BOLD, "\n=== J. the hooks gate (enforcement, judged) ==="))
        armed = "HOOK FIXTURES: 15/15 passed, 0 skipped, 0 n/a\n"
        off = "HOOK FIXTURES: 13/13 passed, 0 skipped, 2 n/a\n"
        check("hooks gate: an armed, alive, fully-configured run passes",
              judge_gate(GATES["hooks"], armed)[0], True)
        check("hooks gate: n/a fixtures are fine (a feature off on purpose)",
              judge_gate(GATES["hooks"], off)[0], True)
        check("hooks gate: ...and the headline says how many were n/a",
              judge_gate(GATES["hooks"], off)[1], "13/13 armed, 2 n/a")
        check("hooks gate: a SKIPPED fixture fails it (skipped-as-passed)",
              judge_gate(GATES["hooks"],
                         "HOOK FIXTURES: 11/11 passed, 4 skipped, 0 n/a")[0],
              False)
        check("hooks gate: one skip alongside many n/a still fails",
              judge_gate(GATES["hooks"],
                         "HOOK FIXTURES: 12/12 passed, 1 skipped, 2 n/a")[0],
              False)
        check("hooks gate: the old two-number line no longer satisfies it",
              judge_gate(GATES["hooks"],
                         "HOOK FIXTURES: 15/15 passed, 0 skipped")[0], False)
        check("hooks gate: UNARMED settings fail it even with green fixtures",
              judge_gate(GATES["hooks"],
                         "  UNARMED: no matcher wires it for Agent\n"
                         + armed)[0], False)
        check("hooks gate: a DEAD-MAN line vetoes it",
              judge_gate(GATES["hooks"],
                         "DEAD-MAN: no output and rc=9\n" + armed)[0], False)
        check("hooks gate: an UNSTARTABLE hook script vetoes it",
              judge_gate(GATES["hooks"],
                         "UNSTARTABLE: matcher 'Bash' names 'tools/gone.py'\n"
                         + armed)[0], False)
        check("hooks gate: a CONFIG WARNING vetoes it",
              judge_gate(GATES["hooks"],
                         "CONFIG WARNING: no kit.config was found\n"
                         + armed)[0], False)
        check("hooks gate: a partial fixture ratio does not match at all",
              judge_gate(GATES["hooks"],
                         "HOOK FIXTURES: 12/15 passed, 0 skipped, 0 n/a")[0],
              False)

    print(c(BOLD, "\n=== K. the cert-green token: minted from PASS, labelled "
                  "for what it is ==="))
    _tok = cert_token_payload("abc123", ["hooks 15/15 armed"], "2026-01-01T00:00:00Z")
    check("the token carries the sha the run judged", _tok["sha"], "abc123")
    check("...and the verdict that minted it, so a reader need not infer it",
          _tok["verdict"], "PASS")
    check("...and the gate headlines, so it says what was proven",
          _tok["gates"], ["hooks 15/15 armed"])
    check("...and the HONEST LABEL travels inside the artifact, not only in "
          "the documentation nobody reads next to the file",
          all(s in _tok["label"] for s in ("CONVENIENCE, NOT AUTHORIZATION",
                                           "unsigned")), True)
    check("the label names WHO can forge it, in the file itself",
          "anything that can write a file" in _tok["label"].lower(), True)
    # The MINTING CONDITION is a verdict test, and the verdict comes from one
    # pure function. PARTIAL and INSTRUMENTED must never mint: both mean the
    # run certified nothing, and a token from either pre-authorises protected
    # writes on the strength of a run that deliberately proved less.
    check("only PASS mints: a clean-but-partial run does not",
          decide_verdict(False, [], ["hooks"])[0], "PARTIAL")
    check("...and neither does an instrumented run with no red gate",
          decide_verdict(True, [], [])[0], "INSTRUMENTED")
    check("the token lands where the hook looks: a relative CERT_TOKEN_FILE "
          "is resolved against the REPO, not the working directory",
          cert_token_path(".claude/cert-green.json", "/r", "x").as_posix(),
          "/r/.claude/cert-green.json")
    check("...an absolute one is taken as given",
          cert_token_path("/elsewhere/tok.json", "/r", "x").as_posix(),
          "/elsewhere/tok.json")
    check("...and an unset key falls back to the documented default",
          cert_token_path("", "/r", ".claude/cert-green.json").as_posix(),
          "/r/.claude/cert-green.json")

    print(c(BOLD, "\n=== I. every gate in RUN_ORDER is actually exercised ==="))
    # THE ANTI-ROT CHECK. Replace a gate and forget its selftest and this goes
    # loudly red, instead of the bench quietly shrinking to cover only the
    # gates somebody happened to write checks for a year ago.
    # Coverage is measured against the labels of the checks that ACTUALLY
    # RAN - not against this function's source text. Source text would count
    # a gate mentioned inside a guarded block that never executed, which is
    # the exact hole an adopter falls into when they delete the example gates
    # and keep the guarded checks that name them.
    _covered = " | ".join(ran)
    uncovered = [g for g in RUN_ORDER if g not in _covered]
    check("no gate in RUN_ORDER is unmentioned by any check that RAN",
          uncovered, [])

    print()
    print(c(GREEN if ok_all else RED,
            f"VERIFY SELFTEST: {'PASS' if ok_all else 'FAIL'} — {n} checks"))
    return 0 if ok_all else 1


# --------------------------------------------------------------------------
def abort(msg: str) -> int:
    """A refusal to START. Exit 2 - the same code as INSTRUMENTED, because
    both mean 'this run certified nothing', and neither may be mistaken for a
    verdict about the project."""
    print(c(RED, f"VERIFY: ABORTED — {msg}"))
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(
        description="The one certification command.",
        epilog="exit 0 PASS · 1 FAIL · 2 INSTRUMENTED/ABORTED · 3 PARTIAL")
    ap.add_argument("--only", default="", help="comma-separated subset")
    ap.add_argument("--skip", default="", help="comma-separated gates to skip")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default="", help="artefact dir (OUTSIDE the repo)")
    ap.add_argument("--nc", default=None, help="negative-control override JSON")
    ap.add_argument("--mint-cert-token", nargs="?", const="", default=None,
                    metavar="PATH",
                    help="on PASS ONLY, write the cert-green token the "
                         "enforcement hook reads (default: CERT_TOKEN_FILE "
                         "from kit.config). Opt-in: a run that lifts a "
                         "control should be asked for, not a side effect.")
    a = ap.parse_args()

    # Armed by the FLAG APPEARING IN argv, not by a successful load.
    nc_armed = any(x == "--nc" or x.startswith("--nc=") for x in sys.argv[1:])

    if a.list:
        for g in RUN_ORDER:
            print(f"  {g:<14} {GATES[g].get('doc', '')}")
        return 0

    if a.selftest:
        if nc_armed:
            return abort("--selftest takes no instrumentation: a bench whose "
                         "own judges are doctored proves nothing.")
        return selftest()

    nc = None
    if nc_armed:
        if not a.nc:
            return abort("--nc requires a file path")
        try:
            nc = json.loads(Path(a.nc).read_text(encoding="utf-8"))
        except Exception as e:
            return abort(f"--nc file could not be loaded: {e!r}")
        err = validate_nc(nc)
        if err:
            return abort(err)

    out = Path(a.out) if a.out else Path(tempfile.mkdtemp(prefix="verify-"))
    out = out.resolve()
    try:
        if out == REPO or REPO in out.parents:
            return abort(f"--out {out} is inside the repo. A run that writes "
                         f"into the tree it judges dirties that tree.")
    except Exception:
        pass
    out.mkdir(parents=True, exist_ok=True)

    only = [g.strip() for g in a.only.split(",") if g.strip()]
    skip = [g.strip() for g in a.skip.split(",") if g.strip()]
    for g in only + skip:
        if g not in GATES:
            return abort(f"unknown gate {g!r}; known: {sorted(GATES)}")
    gates = [g for g in RUN_ORDER if (not only or g in only) and g not in skip]
    if not gates:
        return abort("the --only/--skip combination selects no gates")

    # ---- THE STARTUP ASSERTION -----------------------------------------
    # Before a single gate runs: does the resolved root actually contain the
    # things this runner claims to judge? A mis-resolved root does not crash
    # and does not go red - it produces a clean green describing nothing,
    # because `git status -- <nonexistent path>` prints nothing and exits 0.
    def _is_worktree() -> bool:
        try:
            p = subprocess.run(["git", "-C", str(REPO), "rev-parse",
                                "--is-inside-work-tree"],
                               capture_output=True, text=True, timeout=15)
            return p.returncode == 0 and p.stdout.strip() == "true"
        except Exception:
            return False

    # THE THIRD CASE: a path the repo's ignore rules exclude is invisible to
    # `git status`, so the judges gate reads clean over it forever. Asked as
    # one batch, by the module-level git_excluded() so that the shipped probe
    # is reachable from a test - the first version of it was nested here, and
    # a transport bug in it survived a full green suite.
    problems = startup_problems(REPO, JUDGE_PATHS, CERT_PATHS, GATES, gates,
                                lambda rel: (REPO / rel).exists(),
                                _is_worktree,
                                lambda rels: git_excluded(REPO, rels))
    if problems:
        return abort(
            "this runner cannot judge what it claims to judge, so the run "
            "would certify nothing.\n"
            f"    repo root : {REPO}\n"
            f"    found via : {REPO_HOW}\n"
            + "".join(f"    PROBLEM   : {p}\n" for p in problems)
            + "  Fix: set "
            # THE REMEDY NAMES THE CONSTANTS THAT ARE ACTUALLY IN PLAY. It used
            # to carry a hard-coded four-name list gated on `hooks`, so an
            # abort caused BY THE ESCAPES GATE named four constants that have
            # nothing to do with it - and contradicted this file's own header,
            # which says six constants are the adoption surface. Built from the
            # selected gates instead, so a gate added later without its
            # constants here is a visible omission rather than a wrong message.
            + " / ".join(
                ["JUDGE_PATHS", "CERT_PATHS"]
                + (["HOOK_FIXTURES", "HOOK_SETTINGS"] if "hooks" in gates
                   else [])
                + (["ESCAPE_TOOL", "ESCAPE_LEDGER"] if "escapes" in gates
                   else []))
            + " at the top of this file to paths relative to THAT root "
              "(QUICKSTART Step 4), or --skip the gate that names a file you "
              "do not have.")

    ctx = Ctx(REPO, out, nc)
    print(c(BOLD, f"verify — {len(gates)} of {len(RUN_ORDER)} gates — artefacts in {out}"))
    print(c(CYAN, f"  repo: {REPO}  ({REPO_HOW})"))
    if nc_armed:
        print(c(YELLOW, "*** NEGATIVE CONTROL ACTIVE — this run cannot certify ***"))

    t0 = time.time()
    results, by, red, heads = [], {}, [], []
    for name in gates:
        r = Result(name)
        s0 = time.time()
        print(c(CYAN, f"  → {name} …"), flush=True)
        try:
            RUNNERS.get(name, gate_cmd)(ctx, r)
        except Exception as e:
            r.ok, r.headline, r.detail = False, "CRASHED", f"{e!r}"
        r.seconds = time.time() - s0
        results.append(r)
        by[name] = r
        if r.ok:
            heads.append(f"{name} {r.headline}".strip())
        else:
            red.append(name)
        colour = GREEN if r.ok else RED
        print(c(colour, f"    {'GREEN' if r.ok else 'RED  '} {name} "
                        f"{r.headline}  ({r.seconds:.1f}s)"))
        if r.line:
            print(f"      line: {r.line}")
        if not r.ok and r.detail:
            for ln in r.detail.splitlines():
                print(c(RED, f"      {ln}"))
        if r.log:
            print(f"      log : {r.log}")

    not_run = not_run_gates(by)
    verdict, code = decide_verdict(nc_armed, red, not_run)
    elapsed = f"{time.time() - t0:.1f}s"
    line = summary_line(verdict, code, heads, red, not_run, elapsed)

    (out / "verify.json").write_text(json.dumps({
        "verdict": verdict, "exit": code, "instrumented": nc_armed,
        "gates": {r.name: {"ok": r.ok, "headline": r.headline,
                           "line": r.line, "detail": r.detail,
                           "seconds": round(r.seconds, 2)} for r in results},
        "not_run": not_run, "summary": line,
    }, indent=2), encoding="utf-8")

    # ---- the cert-green token, minted from THE SINGLE PASS RETURN --------
    # Guarded on the verdict, not on the red list: PARTIAL and INSTRUMENTED
    # both mean "this run certified nothing", and a token minted from either
    # would pre-authorise protected-path writes on the strength of a run that
    # deliberately proved less than a certification.
    if a.mint_cert_token is not None:
        if verdict != "PASS":
            print(c(YELLOW, f"  cert-green token NOT minted: the verdict is "
                            f"{verdict}, and only PASS mints one."))
        else:
            tok = cert_token_path(
                a.mint_cert_token or _CFG.get("CERT_TOKEN_FILE", ""),
                REPO, ".claude/cert-green.json")
            try:
                sha = subprocess.run(
                    ["git", "-C", str(REPO), "rev-parse", "HEAD"],
                    capture_output=True, text=True, timeout=15).stdout.strip()
                if not sha:
                    raise RuntimeError("git could not name HEAD")
                tok.parent.mkdir(parents=True, exist_ok=True)
                tok.write_text(json.dumps(
                    cert_token_payload(sha, heads,
                                       time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                     time.gmtime())),
                    indent=2), encoding="utf-8")
                print(c(GREEN, f"  cert-green token minted: {tok}  (sha "
                               f"{sha[:12]} — a convenience, not an "
                               f"authorization; the file says so too)"))
            except Exception as e:
                print(c(RED, f"  cert-green token NOT minted: {e!r}"))

    print()
    print(c(GREEN if code == 0 else (YELLOW if code in (2, 3) else RED), line))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
