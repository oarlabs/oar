#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/adoption_smoke.py - a gate on the kit's own ADOPTION PATH.

    python tools/adoption_smoke.py            # scaffold, adopt, assert
    python tools/adoption_smoke.py --keep     # leave the scaffold on disk
    python tools/adoption_smoke.py --verbose  # echo every child command's tail
    python tools/adoption_smoke.py --plant-f1 # NEGATIVE CONTROL: put the
                                              # original defect back; expects
                                              # INSTRUMENTED, exit 2

    exit 0  PASS          every phase green, uninstrumented
    exit 1  FAIL          a phase went red - OR --plant-f1 was passed and the
                          planted defect went UNDETECTED, which is the same
                          kind of news
    exit 2  INSTRUMENTED  --plant-f1 was passed and the control fired as
                          required - never a certification
    exit 2  ABORT         the kit tree is not where this script expects it

WHY THIS EXISTS
===============
The kit's own certification proves the kit works *in the kit*. It says nothing
about the thing the kit actually ships, which is a SET OF INSTRUCTIONS for
copying files into somebody else's repository.

That gap is not theoretical. An LLM-persona adoption walk followed QUICKSTART
literally in a scratch project and the runner's repo root resolved to
`<repo>/tools/` - so `git -C tools status -- src` returned an empty string
with exit 0, an empty porcelain is how "clean" is spelled, and the gate whose
entire job is noticing an uncommitted tree became a gate that could not fail.
It was green. It was green about nothing. Every check in the kit passed while
that was true, because no check in the kit had ever been COPIED anywhere.

So this script performs the QUICKSTART mechanically, in a throwaway git repo,
and asserts the result. The kit now has a check on the only surface its users
ever touch.

THE PHASES
==========
    1. SCAFFOLD   a throwaway repo: git init, src/, tools/, one commit
    2. ADOPT      copy the runner, the hook, the fixture harness; fill
                  kit.config; wire settings.json from the template; repoint
                  one gate at the scaffold's own suite; DELETE the other
                  example gate (which is what Step 4 tells adopters to do)
    3. SELFTEST   the copied runner's own bench must still pass with the
                  example gates gone - the F2 regression
    4. CERTIFY    a full run must be VERIFY: PASS, exit 0
    5. THE TRAP   dirty a certified path and assert `judges` goes RED. This is
                  the F1 regression, and it is the reason this file exists.
    6. ASSERTION  point CERT_PATHS at a path that does not exist and assert
                  the runner ABORTS (exit 2) naming it, rather than reporting
                  a clean green about nothing.

Phases 5 and 6 are the load-bearing ones. Phases 1-4 only establish that there
is something real to break.
"""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT = Path(__file__).resolve().parent.parent
RUNNER = KIT / "modules" / "03-verification" / "verify.py"
HOOK = KIT / "modules" / "02-enforcement" / "hook_model_gate.py"
FIXTURES = KIT / "modules" / "02-enforcement" / "hook_fixtures.py"
SETTINGS_TMPL = KIT / "modules" / "02-enforcement" / "settings.json.template"
BOARD = KIT / "tools" / "statusline.py"
# Module 04's instrument and the one ledger the runner's `escapes` gate reads.
# Both land at STEP 4, not Step 7, and that ordering is load-bearing for the
# same reason the settings file's is: the startup assertion refuses to run
# over a path that is not in the tree, and Step 4 ends in a certification run.
ESCAPE_RATE = KIT / "modules" / "04-ledgers" / "escape_rate.py"
JUDGMENT_LEDGER = KIT / "modules" / "04-ledgers" / "JUDGMENT-LEDGER.md"
LINT = KIT / "tools" / "expectation_lint.py"

# SB-C: a governance file that still contains a shipped example value is a rule
# nobody is enforcing, written down as though somebody were.
#
# IMPORTED, NOT COPIED. This pattern used to be defined here, and a second,
# narrower copy of the same idea then grew inside `tools/kit_doctor.py
# --level1` - the kit's oldest defect class (two readers of one rule, drifting
# apart) arriving by a new road. The definition now lives beside the shared
# unset rule in `modules/02-enforcement/hook_model_gate.py` and both checkers
# read it from there. There is no fallback copy on purpose: this file only ever
# runs inside a kit checkout, and a silent local copy is the thing being
# prevented.
def _load_rendered_placeholder():
    # Bytecode writing is suppressed for the duration: importing a module by
    # path drops a `__pycache__` beside the file it read, and this file's
    # own phase 13 hashes the kit tree it is standing in.
    prior = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("_oar_shared_rule", HOOK)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.RENDERED_PLACEHOLDER
    finally:
        sys.dont_write_bytecode = prior


RENDERED_PLACEHOLDER = _load_rendered_placeholder()

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
if os.name == "nt":
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
    except Exception:
        GREEN = RED = YELLOW = BOLD = RESET = ""


# --------------------------------------------------------------------------
# the scaffold's own tiny test suite - this is the adopter's "one real gate"
# --------------------------------------------------------------------------
SUITE = '''\
#!/usr/bin/env python3
"""The scaffolded project's test suite. Prints ONE required output line
carrying both numbers, so the gate can assert "all of them" with a
backreference rather than "at least some of them"."""
CASES = ["it adds", "it subtracts", "it refuses to divide by zero",
         "it round-trips unicode"]
for c in CASES:
    print(f"  [PASS] {c}")
print(f"unit_suite: {len(CASES)}/{len(CASES)} cases passed")
'''

# The selftest check an adopter is told to add at QUICKSTART Step 4 item 4.
# Adding it here is not cheating - it is the step, performed mechanically, and
# without it the runner's section I correctly reports the gate as uncovered.
ADOPTER_CHECKS = '''    print(c(BOLD, "\\n=== S. this project's own gate ==="))
    check("unit_suite: a green suite line passes",
          judge_gate(GATES["unit_suite"],
                     "unit_suite: 4/4 cases passed")[0], True)
    check("unit_suite: zero of zero is a catastrophe, not a pass",
          judge_gate(GATES["unit_suite"],
                     "unit_suite: 0/0 cases passed")[0], False)
    check("unit_suite: a partial ratio does not match the backreference",
          judge_gate(GATES["unit_suite"],
                     "unit_suite: 3/4 cases passed")[0], False)

'''


# THE SMOKE'S MODEL OF THE ADOPTER: the values a reader substitutes into the
# governance template at Step 6. It is a HAND-MAINTAINED transcription and must
# track the template's SLOTS manifest. PROSE_VOICE was added to the template
# without updating this list; CI went red on 3a448eb (2026-08-20) - the class
# guard working as intended.
#
# It takes the protected path as an argument because that one value is the
# scaffold's own geography. Phase 13 reads the same table to drive the render
# tool, so the two renderings are compared on MECHANICS - substitution, header
# stripping, JSON merge - rather than on whether two hand-typed lists of values
# happen to agree.
def gov_slots(protected: str):
    return (("PROJECT_NAME", "Scaffolded Project"),
            ("LANE_TIER", "lane-tier"),
            ("SWEEP_TIER", "sweep-tier"),
            ("ORCHESTRATOR_TIER", "orchestrator-tier"),
            ("FORBIDDEN_SPAWN_TIER", "orchestrator-tier"),
            ("MODEL_EXEMPT_TYPES", "fork"),
            ("GATE_COMMAND", "python tools/verify.py"),
            ("CERT_PATHS", "src"),
            ("CERT_TOKEN_FILE", ".claude/cert-green.json"),
            ("PROTECTED_PATH", protected),
            ("OWNER_ROLE", "the owner"),
            ("COORDINATOR_ROLE", "the coordinator"),
            ("KNOWLEDGE_DIR", "docs/knowledge"),
            ("LEDGERS_DIR", "docs"),
            ("REPORTS_DIR", "docs/reports"),
            ("CHECKPOINT_GLOB", "docs/CHECKPOINT-*.md"),
            ("DEMOTION_REVIEW_STAGES", "3"),
            ("PROSE_VOICE", "technical"))


def run(cmd, cwd, verbose=False):
    """(rc, combined output)."""
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, timeout=600)
    out = (p.stdout.decode("utf-8", "replace")
           + p.stderr.decode("utf-8", "replace"))
    if verbose:
        for line in out.strip().splitlines()[-12:]:
            print(f"        | {line}")
    return p.returncode, out


def git(args, cwd):
    return run(["git", "-c", "user.name=adoption smoke",
                "-c", "user.email=smoke@example.invalid", *args], cwd)


def _tracked(cwd) -> set:
    """The repo-relative paths git would publish - the same set the deident
    scanner narrows to under `--tracked-only`."""
    rc, out = git(["ls-files"], cwd)
    return {ln.strip() for ln in out.splitlines() if ln.strip()} if rc == 0 \
        else set()


# --------------------------------------------------------------------------
# phase 2: the mechanical adoption
# --------------------------------------------------------------------------
def adapt_runner(text: str) -> str:
    """QUICKSTART Step 4, performed with a regex instead of a human.

    Every substitution here corresponds to one numbered instruction, and the
    asserts mean this script fails loudly if the runner is refactored out from
    under it - rather than silently testing a file it did not actually
    change."""
    def sub(pattern, repl, why, count=1, flags=0):
        nonlocal text
        new, n = re.subn(pattern, repl, text, count=count, flags=flags)
        if n != count:
            raise SystemExit(f"ADOPTION SMOKE ABORT: could not {why} "
                             f"(pattern {pattern!r} matched {n} times, "
                             f"expected {count}). The runner changed shape; "
                             f"update this script.")
        text = new

    # Step 4.1 - the two path lists
    sub(r"JUDGE_PATHS = \[[^\]]*\]",
        'JUDGE_PATHS = [\n'
        '    "tools/verify.py",\n'
        '    "tools/hook_model_gate.py",\n'
        '    "tools/hook_fixtures.py",\n'
        '    ".claude/settings.json",\n'
        '    "kit.config",\n'
        ']',
        "set JUDGE_PATHS", flags=re.S)
    sub(r'CERT_PATHS = \[[^\]]*\]', 'CERT_PATHS = ["src"]',
        "set CERT_PATHS", flags=re.S)
    sub(r'HOOK_FIXTURES = "[^"]*"', 'HOOK_FIXTURES = "tools/hook_fixtures.py"',
        "repoint HOOK_FIXTURES")
    # Step 4.1b - module 04's two constants. They ship with the KIT's values
    # (its own tool path, its own KNOWN-ISSUES.md table) exactly as JUDGE_PATHS
    # and HOOK_FIXTURES do, so an adopter repoints them here or the startup
    # assertion aborts naming a file they do not have.
    sub(r'ESCAPE_TOOL = "[^"]*"', 'ESCAPE_TOOL = "tools/escape_rate.py"',
        "repoint ESCAPE_TOOL")
    sub(r'ESCAPE_LEDGER = "[^"]*"',
        'ESCAPE_LEDGER = "docs/JUDGMENT-LEDGER.md"', "repoint ESCAPE_LEDGER")

    # Step 4.2 - repoint the surviving gate at this project's real suite
    sub(r'"modules/03-verification/examples/fake_suite\.py"', '"src/suite.py"',
        "repoint the unit gate")

    # Step 4.3 - DELETE BOTH EXAMPLE GATES.
    #
    # The previous version of this script deleted one and kept the other, then
    # printed "example gates DELETED". That label was false, and the gate it
    # kept was precisely the one whose name three selftest checks hard-coded -
    # so the smoke could not see the bug that shipped because of it. A phase
    # whose label overstates what it did is worse than a missing phase: it
    # occupies the slot where the real check would have gone.
    #
    # `example_unit` is RENAMED to this project's own gate (the rename covers
    # its key, its patterns and its selftest references in one pass), and
    # `example_lint` is removed outright.
    text = text.replace("example_unit", "unit_suite")
    start = text.index('    "example_lint": dict(')
    end = text.index("\n    ),\n", start) + len("\n    ),\n")
    text = text[:start] + text[end:]
    return text


def adapt_runner_finish(text: str) -> str:
    sub_pairs = [
        ('RUN_ORDER = ["judges", "hooks", "escapes", "unit_suite", '
         '"example_lint"]',
         'RUN_ORDER = ["judges", "hooks", "escapes", "unit_suite"]'),
    ]
    for a, b in sub_pairs:
        if a not in text:
            raise SystemExit("ADOPTION SMOKE ABORT: RUN_ORDER changed shape; "
                             "update this script.")
        text = text.replace(a, b)
    anchor = '    print(c(BOLD, "\\n=== I. every gate in RUN_ORDER'
    if anchor not in text:
        raise SystemExit("ADOPTION SMOKE ABORT: selftest section I moved; "
                         "update this script.")
    return text.replace(anchor, ADOPTER_CHECKS + anchor)


PLANT_F1 = """\
# ======================================================================
# F1 DEFECT PLANTED by adoption_smoke.py --plant-f1. This is the code as
# it stood before the fix: the repo root is this file's own directory, and
# there is no startup assertion. Copied to <repo>/tools/ it makes the
# judges gate green forever. A negative control has to be able to put the
# bug BACK, or "we fixed it" is a sentence with nothing behind it.
# ======================================================================
"""


def plant_f1(text: str) -> str:
    """Re-introduce the original defect, exactly, so the smoke can be shown
    RED. Two edits, because the fix had two halves and either one alone would
    still catch the trap."""
    old_root = ('REPO, REPO_HOW = find_repo_root(\n'
                '    _HERE, lambda d: (d / ".git").exists(), '
                '_CFG.get("PROJECT_ROOT", ""))')
    if old_root not in text:
        raise SystemExit("ADOPTION SMOKE ABORT: cannot plant F1 - the repo "
                         "resolution changed shape; update this script.")
    text = text.replace(
        old_root,
        PLANT_F1 + 'REPO, REPO_HOW = _HERE, "F1 DEFECT PLANTED: this file\'s '
                   'own directory"')
    if "    if problems:" not in text:
        raise SystemExit("ADOPTION SMOKE ABORT: cannot plant F1 - the startup "
                         "assertion changed shape; update this script.")
    text = text.replace("    if problems:",
                        "    if False and problems:   # F1 DEFECT PLANTED")
    return text


def write_config(root: Path, protected: str) -> None:
    """kit.config as the QUICKSTART now teaches it: repo-relative and
    COMMITTED, with the absolute values in a gitignored kit.config.local.

    PROJECT_ROOT is deliberately ABSENT from the committed half. Step 1 used to
    list it among the fields to fill in, which put one machine's absolute path
    into a shared file twenty lines above the paragraph explaining why that is
    wrong. `.git` discovery covers a normal checkout; the override belongs in
    the .local file for the cases it does not."""
    (root / "kit.config").write_text(
        "PROJECT_NAME = Scaffolded Project\n"
        "ORCHESTRATOR_TIER = orchestrator-tier\n"
        "LANE_TIER = lane-tier\n"
        "SWEEP_TIER = sweep-tier\n"
        "MODEL_EXEMPT_TYPES = fork\n"
        "FORBIDDEN_SPAWN_TIER = orchestrator-tier\n"
        "GATE_COMMAND = python tools/verify.py\n"
        # S3-E3 / F-1: Step 6 resolves KNOWLEDGE_DIR as a DECISION and
        # substitutes it into the rules file, and the key must land in the
        # committed config too or the two documents answer the same question
        # differently with nothing reading either. Step 1 explicitly defers the
        # key ("KNOWLEDGE_DIR at Step 6"), so the scaffold ships the SHIPPED
        # PLACEHOLDER here and Step 6 below edits it, exactly as a reader does.
        # Writing the final value here made the walk skip the state that hid
        # F-1: a kit.config modified after Step 4's commit, inside JUDGE_PATHS,
        # with only Step 9's commit line left to stage it.
        "KNOWLEDGE_DIR = /abs/path/to/your/knowledge-base\n"
        "JUDGE_PATHS = tools/verify.py, tools/hook_model_gate.py, "
        "tools/hook_fixtures.py, .claude/settings.json, kit.config\n"
        "CERT_PATHS = src\n"
        # ENABLED is a shareable boolean; the PATH is one machine's geography,
        # so they live in different halves. Not fussiness: the class guard
        # caught the committed half carrying an absolute path, which made
        # Step 9's own documented remediation unreachable.
        "PROTECTED_PATH_ENABLED = true\n"
        "CERT_TOKEN_FILE = .claude/cert-green.json\n"
        "PYTHON_BIN = python\n",
        encoding="utf-8")
    (root / "kit.config.local").write_text(
        f"PROJECT_ROOT = {root.as_posix()}\n"
        f"PROTECTED_PATH = {protected}\n", encoding="utf-8")


def write_settings(root: Path, protected: str) -> None:
    """The harness wiring, from the template, with the slots filled - and it
    is written in STEP 4, before the first verify run, because the runner's
    `hooks` gate names this file and the startup assertion (correctly) refuses
    to start without it. Creating it in Step 6 made Steps 4 and 5 unreachable
    in document order."""
    tmpl = SETTINGS_TMPL.read_text(encoding="utf-8")
    # SB-B: the RECOMMENDED branch - the portable board, at an ABSOLUTE path,
    # with NO double quotes in the value. The value lands inside a JSON string,
    # so a `"` here produces settings that do not parse, and unparseable
    # settings mean no hooks either.
    for slot, val in (("PROJECT_ROOT", root.as_posix()),
                      ("PROTECTED_PATH", protected),
                      ("PYTHON_BIN", "python"),
                      ("STATUSLINE_CMD",
                       f"python {root.as_posix()}/tools/statusline.py")):
        tmpl = tmpl.replace("{{" + slot + "}}", val)
    left = re.findall(r"\{\{[A-Z_]+\}\}", tmpl)
    if left:
        raise SystemExit(f"ADOPTION SMOKE ABORT: settings template still has "
                         f"unfilled slots {sorted(set(left))}")
    # SB-B/MJ-1: parse it. Substitution is the step that can produce invalid
    # JSON, and the failure is silent in the worst way - the harness simply has
    # no hooks.
    parsed = json.loads(tmpl)
    cmd = (parsed.get("statusLine") or {}).get("command", "")
    if '"' in cmd:
        raise SystemExit("ADOPTION SMOKE ABORT: the substituted statusLine "
                         "command contains a double quote; the settings file "
                         "would not parse in a less lucky arrangement.")
    (root / ".claude" / "settings.json").write_text(tmpl, encoding="utf-8")


def scaffold(root: Path, planted: bool = False) -> None:
    (root / "src").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / ".claude").mkdir()
    (root / "src" / "suite.py").write_text(SUITE, encoding="utf-8")
    (root / "README.md").write_text("# scaffolded project\n", encoding="utf-8")

    for src, name in ((RUNNER, "verify.py"), (HOOK, "hook_model_gate.py"),
                      (FIXTURES, "hook_fixtures.py"), (BOARD, "statusline.py"),
                      (ESCAPE_RATE, "escape_rate.py")):
        shutil.copy2(src, root / "tools" / name)
    # The judgment ledger lands with the runner, because the runner's
    # `escapes` gate names it and a named path that is not in the tree aborts
    # the run. Step 7 substitutes its slots; Step 4 only has to make it exist.
    (root / "docs").mkdir(exist_ok=True)
    shutil.copy2(JUDGMENT_LEDGER, root / "docs" / "JUDGMENT-LEDGER.md")

    # the runner, adapted per QUICKSTART Step 4
    rt = (root / "tools" / "verify.py").read_text(encoding="utf-8")
    rt = adapt_runner(rt)
    rt = adapt_runner_finish(rt)
    if planted:
        rt = plant_f1(rt)
    (root / "tools" / "verify.py").write_text(rt, encoding="utf-8")

    # kit.config, at the REPO ROOT - which is the whole point of search step 4
    protected = (root / "protected").as_posix()
    write_config(root, protected)
    write_settings(root, protected)

    (root / ".gitignore").write_text(
        "__pycache__/\n*.pyc\nkit.config.local\n.claude/sidequest.json\n",
        encoding="utf-8")


# --------------------------------------------------------------------------
# ==========================================================================
# THE CLASS GUARD: walk the QUICKSTART in DOCUMENT ORDER
# ==========================================================================
# Phases 1-7 above prove the adoption WORKS. They do not prove it works
# IN THE ORDER THE DOCUMENT PRESCRIBES, because they set the whole scaffold up
# in one function before asserting anything.
#
# That distinction is not academic. Steps 4 and 5 both aborted for a reader
# following the document, because `.claude/settings.json` was not created
# until Step 6 - and every phase above sailed through, because `scaffold()`
# wrote that file up front. The earlier fix (moving the file into Step 4) was
# an instance fix. THIS is the class fix: the sequence itself is now executed
# and each checkpoint is asserted reachable at the moment the document claims
# it is.
#
# Each entry is one documented command plus the checkpoint the QUICKSTART
# promises for it. A checkpoint that names an exit code is asserted on its
# VERDICT WORD as well - "exit 2" alone is ambiguous between INSTRUMENTED and
# ABORTED, and judging by line rather than by code is this kit's own doctrine.
def document_order(tmp: Path, py: str, verbose: bool = False):
    """(ok, [(label, ok, detail)]) - the QUICKSTART, obeyed literally."""
    root = tmp / "doc-order-project"
    (root / "src").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / ".claude").mkdir()
    (root / "docs").mkdir()
    (root / "src" / "suite.py").write_text(SUITE, encoding="utf-8")
    (root / "docs" / "README.md").write_text("# my docs index\n",
                                             encoding="utf-8")
    # S3-F8: Step 3 is thinking work and is not walked, but its ARTEFACT is a
    # precondition of Step 4's commit checkpoint, which now names the worksheet
    # page by path. A skimmer skips Step 3 (it has no command block), reaches a
    # fully green adoption, and owns a gate whose oracle nobody wrote. The
    # checkpoint asks for the file; this walk supplies it, as a reader who did
    # Step 3 would.
    (root / "docs" / "ORACLE-unit_suite.md").write_text(
        "# Oracle - unit_suite\n\nRequired line: `unit_suite 4/4`\nFloor: 4\n",
        encoding="utf-8")
    git(["init", "-q"], root)

    res = []

    def step(label, ok, detail=""):
        res.append((label, bool(ok), detail))
        return bool(ok)

    def vr(*args):
        return run([py, "tools/verify.py", *args], root, verbose)

    # ---- Step 2: the dead-man clause, because it is one python call -----
    # M-9: cheap, and it is the step that proves the gate can be RED. A walk
    # that only exercises the green path is a walk that would not have noticed
    # the harness reporting maximal green over an unwired hook.
    shutil.copy2(FIXTURES, root / "tools" / "hook_fixtures.py")
    shutil.copy2(HOOK, root / "tools" / "hook_model_gate.py")
    corpse = tmp / "corpse"
    rc, _ = run([py, "tools/hook_fixtures.py", "--make-deadman", str(corpse)],
                root, verbose)
    rc2, out2 = run([py, "tools/hook_fixtures.py", "--hook",
                     str(corpse / "hook_model_gate.py")], root, verbose)
    step("Step 2 · the dead-man clause makes a corpse hook RED",
         rc == 0 and rc2 != 0 and "DEAD-MAN" in out2, _last(out2))

    # ---- SB-3: the Step 4 shell block, executed in pwsh ------------------
    # The README claims an adopter ran this whole document in PowerShell. That
    # claim was false as written: `mkdir -p tools .claude` is a positional-
    # parameter error in pwsh, at a load-bearing step. Claims about shells are
    # now MEASURED where a shell is available, and honestly skipped where it
    # is not.
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if not pwsh:
        step("Step 4 · the shell block runs in pwsh (SKIPPED: no pwsh here)",
             True, "no pwsh/powershell on PATH - claim unmeasured on this host")
    else:
        shell_root = tmp / "pwsh-step4"
        shell_root.mkdir()
        block = ("mkdir -p tools; "
                 "mkdir -p .claude; "
                 "Copy-Item '{src}' 'tools/verify.py'".format(
                     src=str(RUNNER).replace("\\", "/")))
        pr = subprocess.run([pwsh, "-NoProfile", "-Command", block],
                            cwd=str(shell_root), capture_output=True,
                            text=True, timeout=120)
        made = ((shell_root / "tools" / "verify.py").is_file()
                and (shell_root / ".claude").is_dir())
        step("Step 4 · the documented shell block RUNS in pwsh",
             pr.returncode == 0 and made,
             " ".join((pr.stderr or "").split())[:170] or "no directories made")

    # ---- Step 4: gitignore, copy, wire, adapt ---------------------------
    (root / ".gitignore").write_text(
        "__pycache__/\n*.pyc\nkit.config.local\n.claude/sidequest.json\n",
        encoding="utf-8")
    for src, name in ((RUNNER, "verify.py"), (HOOK, "hook_model_gate.py"),
                      (FIXTURES, "hook_fixtures.py"), (BOARD, "statusline.py"),
                      (ESCAPE_RATE, "escape_rate.py")):
        shutil.copy2(src, root / "tools" / name)
    # Step 4 lands the judgment ledger too - see the constant's comment. The
    # step's own copy list says so, and the reason is the one Step 4 already
    # gives for the settings file: a gate that names a missing path aborts,
    # and Step 4 ends in a certification run.
    (root / "docs").mkdir(exist_ok=True)
    shutil.copy2(JUDGMENT_LEDGER, root / "docs" / "JUDGMENT-LEDGER.md")
    rt = adapt_runner_finish(adapt_runner(
        (root / "tools" / "verify.py").read_text(encoding="utf-8")))
    (root / "tools" / "verify.py").write_text(rt, encoding="utf-8")
    protected = (root / "protected").as_posix()
    write_config(root, protected)
    write_settings(root, protected)

    # ---- Step 1's checkpoint, asserted over the config written above -----
    # S3-F5: Step 1 had no checkpoint at all, so its mandatory fills lived only
    # in prose and PROJECT_NAME was caught nowhere in the whole document. The
    # step now ends in a runnable line; this is that line, in Python, over the
    # config this walk writes for the scaffold.
    cfg = (root / "kit.config").read_text(encoding="utf-8")
    unfilled = re.findall(
        r"(?m)^(?:PROJECT_NAME *= *Example Project *$"
        r"|(?:ORCHESTRATOR|LANE|SWEEP|FORBIDDEN_SPAWN)_TIER *= *your-.*$)", cfg)
    named = re.findall(
        r"(?m)^(PROJECT_NAME|ORCHESTRATOR_TIER|LANE_TIER|SWEEP_TIER"
        r"|FORBIDDEN_SPAWN_TIER|GATE_COMMAND) *=", cfg)
    # S5-F4: GATE_COMMAND is the sixth key the checkpoint PRINTS but the fifth
    # is the last one the step calls a fill - it ships correct for the layout
    # Step 4 builds. What the step now asks for is confirmation, so what is
    # asserted here is that the key is present AND carries a runnable value,
    # not that somebody typed a new one.
    gate = re.search(r"(?m)^GATE_COMMAND *= *(\S.*?) *$", cfg)
    step("Step 1 · the five named keys are filled, GATE_COMMAND confirmed "
         "non-empty, no shipped value survives",
         not unfilled and len(set(named)) == 6 and bool(gate),
         f"unfilled {unfilled} · present {sorted(set(named))} · "
         f"GATE_COMMAND {gate.group(1) if gate else '<empty>'!r}")

    rc, out = vr("--list")
    step("Step 4 · --list runs (nothing missing yet)",
         rc == 0 and "judges" in out, out.strip()[:160])

    rc, out = vr("--selftest")
    step("Step 4 · --selftest reaches PASS",
         rc == 0 and "VERIFY SELFTEST: PASS" in out, out.strip()[-160:])

    # The QUICKSTART promises this red, by name. A green here would mean the
    # judges gate cannot see brand-new uncommitted files.
    rc, out = vr()
    step("Step 4 · first run is RED on judges, exactly as documented",
         rc == 1 and "VERIFY: FAIL" in out and "RED: judges" in out,
         _verdict(out))

    # S3-F1: the documented commit line, NAMED PATHS, not `git add -A`. The
    # walk used to stage everything, which is exactly what the document forbids
    # (Step 4 installs a gate that denies blanket adds) and is why the walk
    # never noticed that the printed line stages `docs` and `tests`. `git add`
    # is atomic on a bad pathspec, so a reader who skipped Step 3 staged nothing
    # and committed nothing. `tests` is dropped here because this scaffold does
    # not have one - which is the substitution the document now tells you to
    # make inside the block.
    git(["add", "tools", ".claude", "kit.config", ".gitignore", "src", "docs"],
        root)
    git(["commit", "-q", "-m", "adopt the kit"], root)

    # S3-F8: the worksheet page is in the commit, by name. Nothing between
    # Step 4 and Step 9 used to mention the file again, so a gate with no
    # oracle certified green.
    committed = _tracked(root)
    step("Step 4 · the commit carries docs/ORACLE-<gate>.md (Step 3's page)",
         "docs/ORACLE-unit_suite.md" in committed,
         f"{len(committed)} tracked files")

    rc, out = vr()
    step("Step 4 · after committing, VERIFY: PASS (verdict word, not $?)",
         rc == 0 and "VERIFY: PASS" in out, _verdict(out))

    # ---- Step 5: the negative control, OUTSIDE the repo ------------------
    nc = tmp / "nc.json"
    nc.write_text('{"expect_min": {"unit_suite": 999999}}', encoding="utf-8")
    rc, out = vr("--only", "unit_suite", "--nc", str(nc))
    # THE EXIT-CODE AMBIGUITY TRAP: ABORTED is also exit 2. The checkpoint has
    # to name the verdict WORD or it passes on a runner that refused to start.
    step("Step 5 · VERIFY: INSTRUMENTED on the line (exit 2 alone is ambiguous)",
         rc == 2 and "VERIFY: INSTRUMENTED" in out and "ABORTED" not in out,
         _verdict(out))

    # ---- Step 6: standing rules, scanner, prove the hook -----------------
    # Render the standing rules the way an adopter would, with REAL values -
    # and then check that no shipped example value survived the substitution.
    gov = (KIT / "modules/01-governance/CLAUDE.md.template"
           ).read_text(encoding="utf-8")
    # S3-F2: delete the header block BEFORE substituting, which is what the
    # step says to do twice over - the `SLOTS:` line is an inventory, not
    # content, and a blind find-and-replace turns it into a list of your own
    # paths. The walk used to substitute straight through it, so it modelled
    # the adopter the document warns about.
    if "-->" not in gov:
        raise SystemExit("ADOPTION SMOKE ABORT: the governance template's "
                         "header comment changed shape; update this script.")
    gov = gov.split("-->", 1)[1].lstrip("\n")
    for slot, val in gov_slots(protected):
        gov = gov.replace("{{" + slot + "}}", val)
    (root / "CLAUDE.md").write_text(gov, encoding="utf-8")
    # This is Step 6's second checkpoint clause, run the way the step's own
    # `grep`/`Select-String` line runs it: no surviving slot, no leftover header
    # block, no shipped placeholder value. The clause exists because every OTHER
    # check in the document - the fixture run, VERIFY: PASS, the deident scan -
    # is green over an entirely unrendered CLAUDE.md.
    left_slots = re.findall(r"\{\{[A-Z0-9_]+\}\}", gov)
    left_ph = RENDERED_PLACEHOLDER.findall(gov)
    header_left = "DELETE THIS COMMENT BLOCK" in gov
    step("Step 6 \u00b7 the rendered rules carry no unfilled slot, no header "
         "block and no shipped placeholder value",
         not left_slots and not left_ph and not header_left,
         f"slots {sorted(set(left_slots))} placeholders {sorted(set(left_ph))}"
         + (" HEADER BLOCK LEFT" if header_left else ""))
    # S3-E3: the KNOWLEDGE_DIR decision has to land in BOTH places - the slot in
    # the rules file and the key in the committed config - or the two documents
    # answer the same question differently and no check reads either one.
    # F-2: the value this walk chooses is the REPO-PATH branch, which is
    # repo-relative and therefore belongs in the COMMITTED half. The other
    # branch (an absolute knowledge base) routes the key into kit.config.local
    # instead; an absolute path in the committed half is the escape Step 9
    # teaches the reader to hunt for.
    cfg_text = (root / "kit.config").read_text(encoding="utf-8")
    cfg_text = re.sub(r"(?m)^KNOWLEDGE_DIR *=.*$",
                      "KNOWLEDGE_DIR = docs/knowledge", cfg_text)
    (root / "kit.config").write_text(cfg_text, encoding="utf-8")
    kd = re.search(r"(?m)^KNOWLEDGE_DIR *= *(.+?) *$", cfg_text)
    step("Step 6 \u00b7 KNOWLEDGE_DIR agrees between kit.config and CLAUDE.md",
         bool(kd) and kd.group(1) == "docs/knowledge"
         and "docs/knowledge" in gov,
         f"kit.config says {kd.group(1) if kd else '<key absent>'!r}")
    # F-1, first half: that edit is to a file inside JUDGE_PATHS and it is now
    # UNCOMMITTED. The document has to stage it, and until this walk carried
    # the state it did not - a literal reader finished the QUICKSTART at
    # `VERIFY: FAIL - RED: judges` naming `M kit.config`. Prove the red is real
    # here so the green at the end of Step 9 means something.
    rc, out = vr()
    step("Step 6 \u00b7 the KNOWLEDGE_DIR edit reddens judges until it is staged",
         rc == 1 and "RED: judges" in out and "kit.config" in out,
         _verdict(out))
    shutil.copy2(KIT / "tools/deident_scan.py", root / "tools" / "deident_scan.py")
    # S5-F3: the scanner makes Step 9's publish-safety judgment, so it decides
    # what green means and belongs on the judge surface - by the same reasoning
    # that puts kit.config there. It cannot join at Step 4, because a
    # JUDGE_PATHS entry that is not in the tree aborts the runner and the file
    # does not exist until this copy. Step 6 adds it to BOTH halves: the
    # authoritative constant in verify.py and the documentation line in
    # kit.config.
    vt = (root / "tools" / "verify.py").read_text(encoding="utf-8")
    if '    "kit.config",\n' not in vt:
        raise SystemExit("ADOPTION SMOKE ABORT: JUDGE_PATHS changed shape; "
                         "update this script.")
    (root / "tools" / "verify.py").write_text(
        vt.replace('    "kit.config",\n',
                   '    "kit.config",\n    "tools/deident_scan.py",\n', 1),
        encoding="utf-8")
    cfg_text = (root / "kit.config").read_text(encoding="utf-8")
    (root / "kit.config").write_text(
        re.sub(r"(?m)^(JUDGE_PATHS *=.*)$", r"\1, tools/deident_scan.py",
               cfg_text), encoding="utf-8")
    # The document promises this red by name, and promises Step 9's commit
    # clears it. Assert the red here so the green at the end of Step 9 is a
    # measurement rather than an assumption.
    rc, out = vr()
    step("Step 6 · the scanner joins JUDGE_PATHS and reddens judges until "
         "Step 9 stages it",
         rc == 1 and "RED: judges" in out and "deident_scan.py" in out,
         _verdict(out))
    rc, out = run([py, "tools/hook_fixtures.py", "--strict",
                   "--armed", ".claude/settings.json"], root, verbose)
    step("Step 6 · fixtures: armed, strict, 0 skipped, no CONFIG WARNING",
         rc == 0 and "UNARMED" not in out and "CONFIG WARNING" not in out
         and "0 skipped" in out,
         [l for l in out.splitlines() if "HOOK FIXTURES" in l][-1:] or out[-160:])

    # ---- Step 7: the ledgers, copied BY NAME -----------------------------
    # S5-F5: the step's first line is `mkdir -p docs/reports`, two levels, so
    # the directory REPORTS_DIR names - and the rendered rules file names twice
    # - exists in the tree at done. It used to be `mkdir -p docs`, and the
    # standing rules ended up pointing at a directory nobody had created.
    (root / "docs" / "reports").mkdir(parents=True, exist_ok=True)
    # THREE ledgers here, not four: the judgment ledger landed at Step 4 with
    # the runner that reads it. Assert it is still there before copying the
    # rest, so a future edit that moves it back to Step 7 shows up as this
    # step failing rather than as an abort three checks later.
    step("Step 7 · the judgment ledger arrived at Step 4 (the runner's "
         "escapes gate names it) and is still in the tree",
         (root / "docs" / "JUDGMENT-LEDGER.md").is_file(),
         "docs/JUDGMENT-LEDGER.md is missing - Step 4's copy list dropped it")
    for name in ("FAILURE-FLOOR.md", "LESSONS.md", "TOKEN-LEDGER.md"):
        shutil.copy2(KIT / "modules/04-ledgers" / name, root / "docs" / name)
    kept = (root / "docs" / "README.md").read_text(encoding="utf-8")
    reports_ok = (root / "docs" / "reports").is_dir() and "docs/reports" in gov
    step("Step 7 · all four ledgers are in the tree (three copied here, the "
         "judgment ledger at Step 4), REPORTS_DIR exists, docs/README.md is "
         "NOT clobbered",
         all((root / "docs" / n).is_file() for n in
             ("JUDGMENT-LEDGER.md", "FAILURE-FLOOR.md", "LESSONS.md",
              "TOKEN-LEDGER.md")) and kept.strip() == "# my docs index"
         and reports_ok,
         "" if kept.strip() == "# my docs index" else "README.md was overwritten")

    # STEP 7'S SECOND INSTRUCTION, ON ONE LEDGER: "Then substitute their slots
    # and delete their header blocks." The walk leaves all four unrendered,
    # which models a reader who skipped that sentence and leaves the four files
    # with no hand rendering for phase 13 to diff against.
    #
    # ONE OF THE FOUR IS RENDERED HERE, AND ONLY ONE. `PROJECT_NAME`,
    # `OWNER_ROLE`, `LEDGERS_DIR`, `REPORTS_DIR` and `DEMOTION_REVIEW_STAGES`
    # all appear in CLAUDE.md, which phase 13 already diffs byte for byte, so
    # hand-rendering the other three would add no expectation the diff does not
    # already carry. `RATIO_CEILING` appears in TOKEN-LEDGER.md and NOWHERE
    # ELSE, and it is the single documented placeholder exemption in the kit -
    # so without this, the behaviour of that exemption is asserted only by the
    # tool's own selftest, which is an expectation read from its own subject.
    tok = (KIT / "modules/04-ledgers/TOKEN-LEDGER.md").read_text(
        encoding="utf-8")
    if "-->" not in tok:
        raise SystemExit("ADOPTION SMOKE ABORT: the TOKEN-LEDGER skeleton's "
                         "header comment changed shape; update this script.")
    _o = tok.index("<!--")
    _c = tok.index("-->", _o) + len("-->")
    tok = tok[:_o] + tok[_c:].lstrip("\n")
    for slot, val in (("PROJECT_NAME", "Scaffolded Project"),
                      ("OWNER_ROLE", "the owner"),
                      ("LEDGERS_DIR", "docs"),
                      # THE EXEMPTION, EXERCISED. Step 7 names this value as
                      # the one shipped placeholder allowed to survive
                      # adoption, so an adopter substitutes it unchanged.
                      ("RATIO_CEILING", "derive-from-your-own-data")):
        tok = tok.replace("{{" + slot + "}}", val)
    (root / "docs" / "TOKEN-LEDGER.md").write_text(tok, encoding="utf-8")
    tok_slots = re.findall(r"\{\{[A-Z0-9_]+\}\}", tok)
    step("Step 7 · TOKEN-LEDGER.md is hand-rendered, RATIO_CEILING's shipped "
         "value survives by name, no slot and no SKELETON header left",
         not tok_slots and "SKELETON" not in tok
         and "derive-from-your-own-data" in tok,
         f"slots {sorted(set(tok_slots))}")

    # ---- Step 8: the collaboration profile, rendered like every template ---
    # S5-F2: Step 8 is a conversation and is not walked - but it COPIES A
    # TEMPLATE and commits the result, and until this block existed nothing in
    # the kit checked that copy for the two things every other template step is
    # checked for. The interview is not simulated here; the file it produces is.
    prof = (KIT / "modules/08-collaboration/PROFILE-TEMPLATE.md"
            ).read_text(encoding="utf-8")
    if "-->" not in prof:
        raise SystemExit("ADOPTION SMOKE ABORT: the profile template's header "
                         "comment changed shape; update this script.")
    # The step's own order: substitute the slot with the SAME value Step 6
    # chose, then delete the header block once it has been acted on.
    #
    # DELETE THE COMMENT, NOT EVERYTHING ABOVE IT. Step 8 names what goes:
    # "the `<!-- … -->` comment that opens `TEMPLATE - the living
    # collaboration profile`". This template is the only one in the kit whose
    # header is NOT the first thing in the file - nine lines of YAML front
    # matter (`title`, `type`, `status`, `created`, `last_revised`, `sources`)
    # come first, and they are content. Splitting on the first `-->` and
    # keeping the tail deleted them silently, and no checkpoint in the document
    # could see it: the front matter carries neither a slot nor a header marker
    # word, so Step 8's own grep line stays green over a profile that has lost
    # its provenance block. Found by phase 13, which renders the same template
    # a second way and diffs the two.
    prof = prof.replace("{{KNOWLEDGE_DIR}}", "docs/knowledge")
    _open = prof.index("<!--")
    # Search for the CLOSE from the OPEN, not from position 0. A `-->` above
    # the header comment would put _close before _open and the slice would
    # corrupt this file quietly - and this file is the independent expectation,
    # so phase 13 would report the damage as the tool's fault.
    _close = prof.index("-->", _open) + len("-->")
    prof = prof[:_open] + prof[_close:].lstrip("\n")
    (root / "docs" / "collaboration-profile.md").write_text(prof,
                                                            encoding="utf-8")
    prof_slots = re.findall(r"\{\{[A-Z0-9_]+\}\}", prof)
    prof_header = ("Delete this comment on adoption" in prof
                   or "TEMPLATE - the living" in prof)
    front = prof.startswith("---\ntitle:")
    step("Step 8 · the rendered profile carries no unfilled slot and no "
         "template header block, and KEEPS its YAML front matter",
         not prof_slots and not prof_header and front,
         f"slots {sorted(set(prof_slots))}"
         + (" HEADER BLOCK LEFT" if prof_header else "")
         + ("" if front else " FRONT MATTER DELETED - the header strip took "
                            "the title/type/status/sources block with it"))

    # ---- Step 9, first item: COMMIT what Steps 6-8 produced --------------
    # K-1. The scan below is `--tracked-only` and the last commit was Step 4's.
    # Until this commit joined the document, the walk reached a green scan over
    # a tree holding no rules file, no ledgers and no collaboration profile -
    # which is what a reader obeying the printed order got. Named paths, like
    # every other commit here, because Step 4 installs a gate that denies
    # blanket adds.
    # F-1: `kit.config` is in the printed line because STEP 6 EDITED IT. Leave
    # it out and the document ends uncertifiable on a file it told you to
    # change - measured on walk 11, and invisible to this walk until the walk
    # started carrying the edit.
    # S5-F3: `tools/verify.py` joins the printed line because Step 6 edited it
    # (the scanner's JUDGE_PATHS entry). It is itself a judge path, so an
    # unstaged edit to it ends the document RED - the same trap `kit.config`
    # was in before F-1.
    before = len(_tracked(root))
    git(["add", "CLAUDE.md", "tools/deident_scan.py", "tools/verify.py",
         "docs", "kit.config"], root)
    git(["commit", "-q", "-m", "standing rules, ledgers, profile"], root)
    tracked = _tracked(root)
    step("Step 9 · the Step 6-8 output is COMMITTED before the scan runs",
         len(tracked) > before and "CLAUDE.md" in tracked
         and "docs/LESSONS.md" in tracked and "docs/JUDGMENT-LEDGER.md" in tracked
         and "docs/collaboration-profile.md" in tracked,
         f"{before} tracked before, {len(tracked)} after")

    # F-1, second half: the state the document LEAVES YOU IN. Step 9 now ends
    # in a certification run, and this is it. A red here means the printed
    # commit line does not stage everything the document told the reader to
    # change - which is exactly the defect, and it is worth a phase of its own
    # rather than an inference from a clean scan.
    rc, out = vr()
    step("Step 9 · the document ENDS certifiable: VERIFY: PASS after the commit",
         rc == 0 and "VERIFY: PASS" in out, _verdict(out))

    # ---- Step 9: the scanner, and its OWN advice ------------------------
    # The scaffold's absolute path stands in for the adopter's username: it is
    # baked into .claude/settings.json's hook commands, exactly as Step 1 warns.
    tok = tmp / "tokens.txt"
    secret = root.parent.name          # a path component that IS in settings.json
    tok.write_text(secret + "\n", encoding="utf-8")
    (root / "kit.config.local").write_text(
        f"PROJECT_ROOT = {root.as_posix()}\n# {secret}\n", encoding="utf-8")

    rc_all, out_all = run([py, "tools/deident_scan.py", "--root", ".",
                           "--tokens", str(tok), "--strict"], root, verbose)
    step("Step 9 · the warned-about hit is REAL (scan is not vacuous)",
         rc_all == 1 and "HIT" in out_all, _last(out_all))

    rc_t, out_t = run([py, "tools/deident_scan.py", "--root", ".",
                       "--tokens", str(tok), "--strict", "--tracked-only"],
                      root, verbose)
    step("Step 9 · --tracked-only drops the gitignored kit.config.local",
         "kit.config.local" not in out_t, _last(out_t))

    # K-1. The checkpoint now tells the reader to read the printed scope line
    # rather than trust it. Assert the same thing: the scope the scan reports
    # is the whole tracked tree it just committed, not the Step 4 subset.
    m = re.search(r"git-tracked files only \((\d+) tracked\)", out_t)
    step("Step 9 · the printed scope covers the whole tracked tree",
         bool(m) and int(m.group(1)) == len(tracked),
         (m.group(0) if m else "no scope line printed")
         + f" · git ls-files: {len(tracked)}")

    # SB-B: this walk takes the portable board at an absolute path AND keeps
    # the permissions.ask block (its scaffold enables the tripwire), so the
    # hits are Step 9's tripwire-ON row: three hook commands + one statusLine +
    # two permissions.ask, all inside .claude/settings.json. K-1 added a second
    # tracked file to that branch: CLAUDE.md now interpolates {{PROTECTED_PATH}}
    # and is committed before the scan, so the tripwire-ON branch has TWO
    # reviewed files. The recommended branch (tripwire off, the protected-path
    # section deleted at Step 6) has only the settings file. What is asserted
    # here is the FILE SET, not the count.
    REVIEWED = (".claude/settings.json", "CLAUDE.md")
    only_reviewed = all(any(f in ln for f in REVIEWED)
                        for ln in out_t.splitlines()
                        if ln.strip().startswith("HIT"))
    step("Step 9 · every tracked hit is inside one of the two reviewed files "
         "(tripwire-ON branch: settings.json and CLAUDE.md)",
         only_reviewed, "" if only_reviewed else _last(out_t))


    rc_x, out_x = run([py, "tools/deident_scan.py", "--root", ".",
                       "--tokens", str(tok), "--strict", "--tracked-only",
                       "--exclude", ".claude/settings.json",
                       "--exclude", "CLAUDE.md"], root, verbose)
    step("Step 9 · ...and the documented remediation REACHES 0 hits",
         rc_x == 0 and "0 hits" in out_x, _last(out_x))

    return all(ok for _, ok, _ in res), res


def _verdict(out: str) -> str:
    for line in re.sub(r"\033\[[0-9;]*m", "", out).splitlines():
        if "VERIFY:" in line or "SELFTEST:" in line:
            return line.strip()[:170]
    return out.strip()[-140:]


def _last(out: str) -> str:
    lines = [l for l in re.sub(r"\033\[[0-9;]*m", "", out).strip().splitlines()
             if l.strip()]
    return lines[-1][:170] if lines else ""


# ==========================================================================
# PHASE 12: the gitignored judge path
# ==========================================================================
# THE HAZARD. `git status --porcelain -- <a path the repo's ignore rules
# exclude>` prints nothing and exits 0, whatever the file says. A JUDGE_PATHS
# entry in that state makes the `judges` gate read clean forever, so the runner
# certifies a settings file anyone can edit to disarm every hook. `.claude/` is
# a common entry in a pre-existing `.gitignore`, which is why the scaffolded
# adoption above never meets this: its `.gitignore` is the one QUICKSTART Step
# 4 writes, and that file covers no judged path.
#
# WHY THIS PHASE EXISTS AND THE SELFTEST IS NOT ENOUGH. The runner's own
# selftest exercises the startup assertion with an injected probe, so it proves
# how the assertion REACTS to an answer. It cannot prove the shipped probe
# gets a true answer out of git. The first version of that probe sent its
# paths through text-mode stdin, which on Windows appended a carriage return
# to every path but the last: exact-path ignore rules were missed entirely
# (the hazard survived, VERIFY: PASS) and correctly tracked files false-aborted
# with a remedy message that could not clear the abort. Every selftest check
# passed. Only a real repository, a real rule and a real subprocess can see
# that, so this phase builds all three.
#
# Two rule SHAPES, because they fail differently: an exact-path rule and a
# directory-prefix rule. Then the control: force-track the file and commit it -
# the remedy the abort message prints - and the run must start.
IGNORED_JUDGE_STEPS = (
    "verify.py's exclusion probe: check git_excluded() in "
    "modules/03-verification/verify.py - it must send NUL-terminated bytes to "
    "`git check-ignore -z --stdin` and never text-mode newlines")


def excluded_judge_path(tmp: Path, py: str, verbose: bool = False):
    """(ok, [(label, ok, detail)]) - a real repo, a real ignore rule, the
    shipped probe."""
    root = tmp / "ignored-judge-project"
    (root / "tools").mkdir(parents=True)
    (root / ".claude").mkdir()
    (root / "src").mkdir()
    (root / "src" / "keep.txt").write_text("certified tree\n", encoding="utf-8")
    (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")

    # QUICKSTART Step 4's two constants, set to the smallest honest pair: one
    # judged FILE that an ignore rule can cover, one certified directory. The
    # asserts mean this phase fails loudly if the runner is refactored out from
    # under it rather than silently testing a file it did not change.
    text = RUNNER.read_text(encoding="utf-8")
    for pattern, repl in ((r"JUDGE_PATHS = \[[^\]]*\]",
                           'JUDGE_PATHS = [\n    ".claude/settings.json",\n]'),
                          (r'CERT_PATHS = \[[^\]]*\]', 'CERT_PATHS = ["src"]')):
        text, n = re.subn(pattern, repl, text, count=1, flags=re.S)
        if n != 1:
            raise SystemExit(f"ADOPTION SMOKE ABORT: could not set the path "
                             f"lists for the excluded-judge-path phase "
                             f"(pattern {pattern!r} matched {n} times). The "
                             f"runner changed shape; update this script.")
    (root / "tools" / "verify.py").write_text(text, encoding="utf-8")

    res: list[tuple[str, bool, str]] = []

    def step(label, ok, detail=""):
        res.append((label, ok, detail))

    def verify_judges():
        return run([py, "tools/verify.py", "--only", "judges"], root, verbose)

    def set_rule(rule: str):
        (root / ".gitignore").write_text(rule + "\n", encoding="utf-8")
        git(["add", ".gitignore"], root)
        git(["commit", "-q", "-m", f"ignore rule {rule}"], root)

    git(["init", "-q"], root)
    git(["add", "tools", "src", ".claude"], root)   # named paths, never -A
    git(["commit", "-q", "-m", "the judged tree"], root)

    # A judged path that no rule covers must not be disturbed by any of this.
    rc, out = verify_judges()
    step("control: with no ignore rule the run starts and judges is GREEN",
         rc == 3 and "judges clean" in out,
         "" if rc == 3 else f"exit {rc} · {_verdict(out)}")

    # The file has to leave the index for a rule to be able to hide it - which
    # is exactly the state an adopter is in when their pre-existing .gitignore
    # covered the path before they ever created it.
    git(["rm", "-q", "--cached", ".claude/settings.json"], root)
    git(["commit", "-q", "-m", "untrack the settings file"], root)

    for shape, rule in (("exact-path", ".claude/settings.json"),
                        ("directory-prefix", ".claude/")):
        set_rule(rule)
        # Ground truth, straight from git, independent of the runner.
        rc_gt, _ = git(["check-ignore", "-q", ".claude/settings.json"], root)
        rc_st, out_st = git(["status", "--porcelain", "--",
                             ".claude/settings.json"], root)
        step(f"{shape} rule: git agrees the judged path is hidden "
             f"(check-ignore rc 0, status EMPTY)",
             rc_gt == 0 and not out_st.strip(),
             f"check-ignore rc={rc_gt} · status {out_st.strip()!r}")

        rc, out = verify_judges()
        clean = re.sub(r"\033\[[0-9;]*m", "", out)
        named = "judged path '.claude/settings.json' is EXCLUDED" in clean
        step(f"{shape} rule: the runner ABORTS (exit 2) and NAMES the path "
             f"exactly", rc == 2 and named,
             "" if (rc == 2 and named) else
             f"exit {rc} (want 2), path named exactly = {named}. "
             f"{IGNORED_JUDGE_STEPS}")
        # THE PRINTED REMEDY, ASSERTED AGAINST THE ONE THIS PHASE PROVES.
        # P3W-3: the message used to say "remove the rule that covers it",
        # which on the directory-rule shape below means deleting `.claude/`
        # from the ignore file - and that rule also covers session state and
        # the certification token. The remedy the control at the end of this
        # phase actually demonstrates is `git add -f <the one file>`, so the
        # message has to print that one, first.
        remedy_ok = ("git add -f .claude/settings.json" in clean
                     and clean.index("git add -f")
                     < clean.index("git check-ignore"))
        step(f"{shape} rule: the printed remedy is the one THIS phase proves "
             f"(`git add -f <the file>`, ahead of the rule removal)",
             remedy_ok,
             "" if remedy_ok else
             f"the abort message does not lead with the force-track remedy. "
             f"The control below force-tracks the file and requires the run "
             f"to start; a message that instead tells an existing repo to "
             f"delete its `.claude/` rule commits session state and the "
             f"cert token. Offending text: "
             f"{next((l for l in clean.splitlines() if 'EXCLUDED' in l), '')[:200]!r}")
        # The mangled-path signature of the transport defect, asserted by
        # itself: a quoted or escaped path is not a path, and the message tells
        # the adopter to paste it into a command. Signatures, not a raw
        # backslash-r scan: the message prints the repo root, and any Windows
        # path with a directory starting in "r" (runneradmin on a hosted CI
        # runner) contains backslash-r legitimately.
        mangled_ok = ("\r" not in clean.replace("\r\n", "\n")
                      and '"' + ".claude" not in clean
                      and '\\r"' not in clean)
        offending = next((l for l in clean.splitlines()
                          if ".claude" in l), "")[:170]
        step(f"{shape} rule: the message carries no mangled path "
             f"(no CR, no core.quotePath escaping)",
             mangled_ok,
             "" if mangled_ok else
             (f"mangled signature in {offending!r}" if rc == 2
              else "skipped: no abort message to inspect"))

    # THE CONTROL, and it is the remedy the abort message itself prints. The
    # directory rule is still in force; the path is simply tracked again.
    git(["add", "-f", ".claude/settings.json"], root)
    git(["commit", "-q", "-m", "force-track the settings file"], root)
    rc_gt, _ = git(["check-ignore", "-q", ".claude/settings.json"], root)
    rc, out = verify_judges()
    step("THE REMEDY WORKS: force-tracked under the same rule, the run STARTS "
         "and judges is GREEN",
         rc_gt == 1 and rc == 3 and "judges clean" in out,
         "" if rc == 3 else
         f"git says ignored={rc_gt == 0}, runner exit {rc} · {_verdict(out)}. "
         f"A tracked path is not hidden from `git status`, so this abort is "
         f"false and its printed remedy cannot clear it. {IGNORED_JUDGE_STEPS}")

    # THE LAST PATH IN THE BATCH, and a CERT_PATHS entry rather than a judge
    # path. Both halves of the `judges` gate ask git the same question, so an
    # excluded certified tree is the same silent green. The position matters
    # on its own: the probe sends all the paths in one payload, and the
    # transport defect this phase exists for spared whichever path came last.
    git(["rm", "-q", "-r", "--cached", "src"], root)
    git(["commit", "-q", "-m", "untrack the certified tree"], root)
    (root / ".gitignore").write_text(".claude/\nsrc/\n", encoding="utf-8")
    git(["add", ".gitignore"], root)
    git(["commit", "-q", "-m", "ignore rule over the certified tree"], root)
    rc, out = verify_judges()
    clean = re.sub(r"\033\[[0-9;]*m", "", out)
    step("an excluded CERT_PATHS entry, LAST in the batch, aborts and is NAMED",
         rc == 2 and "judged path 'src' is EXCLUDED" in clean,
         "" if rc == 2 else
         f"exit {rc} (want 2) · {_verdict(out)}. The certified tree is judged "
         f"by the same `git status` call as the judge surface, and the last "
         f"path in the batch is the one a framing bug drops. "
         f"{IGNORED_JUDGE_STEPS}")

    return all(ok for _, ok, _ in res), res


# ==========================================================================
# PHASE 10: the slot registry, checked against itself
# ==========================================================================
# `kit.config.example` claims to be the complete registry of every slot, and
# each template opens with a `SLOTS:` line claiming to list the slots IT uses.
# Both claims were prose. A template using an unregistered slot ships a raw
# `{{TOKEN}}` into somebody's production config; a manifest that disagrees with
# its own body sends a reader hunting for a slot that is not there, or worse,
# lets them think they have substituted everything when they have not.
#
# Three assertions, all mechanical:
#   * every slot any template uses is defined in kit.config.example;
#   * every template's own SLOTS manifest matches the slots in its body;
#   * every slot the WALK DOCUMENTS name in prose is defined there too.
SLOT_TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

# THE WALK DOCUMENTS - checked for REGISTRY MEMBERSHIP only. These are not
# templates: nobody substitutes them, so they carry no `SLOTS:` manifest and
# there is nothing to diff one against. What they DO carry is slot names in
# their prose, and a walk document naming a slot the registry does not define
# sends its reader hunting for a key that does not exist. That half is
# mechanical, so it is checked.
#
# THE HEADLINE COUNTS STAY MODULES-ONLY, deliberately. `kit_render.py`'s
# docstring quotes the "23 slot-carrying files under modules/" figure this
# phase reports, so a headline whose population silently grew would make that
# cross-reference wrong while both files still looked right.
WALK_DOCS = ("QUICKSTART.md", "LEVEL-1.md")


def split_manifest(text: str):
    """(manifest, body). The manifest is the `SLOTS:` header block - the line
    naming slots, plus the run of lines that carry tokens. Everything else is
    body.

    TWO SHAPES, both real in this kit. The header line may carry tokens itself
    (`SLOTS: {{A}} {{B}}`), or it may be a bare heading whose tokens start on
    the NEXT line (`SLOTS USED IN THIS FILE`, then an indented block). The
    first version of this detector required the word and a token on the SAME
    line, so every multi-line inventory scored as "no manifest" and its file
    was skipped in silence - which is how CLAUDE.md.template shipped a body
    slot its own inventory omitted.

    The token run must start IMMEDIATELY after the heading. That is what keeps
    prose which merely mentions slots (verify.py's module docstring names four
    constants, then lists related kit.config keys three lines down) from being
    read as an inventory it never claimed to be."""
    lines = text.splitlines()
    man_idx = set()
    for i, ln in enumerate(lines):
        if not re.search(r"\bslots?\b", ln, re.I):
            continue
        if SLOT_TOKEN.search(ln):
            man_idx.add(i)          # tokens on the heading line itself
            j = i + 1
        elif i + 1 < len(lines) and SLOT_TOKEN.search(lines[i + 1]):
            j = i + 1               # bare heading, tokens start on the next line
        else:
            continue                # a mention of slots, not an inventory
        while j < len(lines) and SLOT_TOKEN.search(lines[j]):
            man_idx.add(j)
            j += 1
    man, body = set(), set()
    for i, ln in enumerate(lines):
        (man if i in man_idx else body).update(SLOT_TOKEN.findall(ln))
    return man, body


def slot_problems(kit: Path):
    problems = []
    try:
        registry = {m.group(1) for m in re.finditer(
            r"(?m)^([A-Z0-9_]+)\s*=",
            (kit / "kit.config.example").read_text(encoding="utf-8"))}
    except Exception as e:
        return [f"kit.config.example is unreadable: {e!r}"], 0, 0, 0
    n_templates = 0
    n_nomanifest = 0
    for f in sorted((kit / "modules").rglob("*")):
        if not f.is_file():
            continue
        try:
            t = f.read_text(encoding="utf-8")
        except Exception:
            continue
        if not SLOT_TOKEN.search(t):
            continue
        rel = f.relative_to(kit).as_posix()
        man, body = split_manifest(t)
        for slot in sorted((man | body) - registry):
            problems.append(f"{rel}: uses {{{{{slot}}}}}, which "
                            f"kit.config.example does not define")
        if not man:
            # No inventory to check this body against. Counted and printed,
            # never silent: an uncounted skip is how a template escapes the
            # manifest assertion without anyone noticing.
            n_nomanifest += 1
            continue
        n_templates += 1
        for miss in sorted(body - man):
            problems.append(f"{rel}: body uses {{{{{miss}}}}} but the SLOTS "
                            f"manifest omits it")
        for extra in sorted(man - body):
            problems.append(f"{rel}: SLOTS manifest lists {{{{{extra}}}}} but "
                            f"the body never uses it")
    n_walk = 0
    for name in WALK_DOCS:
        f = kit / name
        if not f.is_file():
            problems.append(f"{name}: named as a walk document and not there")
            continue
        n_walk += 1
        for slot in sorted(set(SLOT_TOKEN.findall(
                f.read_text(encoding="utf-8")))):
            if slot not in registry:
                problems.append(f"{name}: names {{{{{slot}}}}} in prose, which "
                                f"kit.config.example does not define")
    return problems, n_templates, n_nomanifest, n_walk


# ==========================================================================
# PHASE 13: the optional render tool, DIFFED AGAINST THE HAND MODEL
# ==========================================================================
# `tools/kit_render.py` is the optional mechanical substitution path QUICKSTART
# offers beside the by-hand one. This phase is what keeps it honest.
#
# TWO AUTHORITIES, ON PURPOSE. `document_order()` above renders the adopter's
# files BY HAND and continues to do so unchanged: a person transcribed the
# QUICKSTART into it, and that transcription is the thing that caught the
# PROSE_VOICE drift when a slot was added to a template and nobody updated the
# walk. The tool is a program. Requiring them to AGREE is a real check;
# collapsing them - having the walk call the tool, or the tool read the walk -
# would leave one authority and no independent expectation of what a rendered
# kit file looks like. The first run of this phase disagreed, and the hand
# model was the one that was wrong (Step 8's front matter).
#
# WHY IT IS SAFE TO RUN THE TOOL OVER THE FINISHED HAND MODEL. The tool writes
# only `<name>.kit-new` files. That is its second guard, and this phase asserts
# it directly: every hand-rendered file is hashed before and after.
#
# WHAT IT DOES NOT COVER, stated rather than implied. The hand model COPIES
# three of the four ledgers at Step 7 without substituting their slots, so
# there is no hand rendering of THOSE THREE to diff against; they are checked
# here against Step 7's own printed checkpoint instead - no surviving slot, no
# SKELETON header - which is weaker than a diff.
#
# The fourth, TOKEN-LEDGER.md, IS hand-rendered and byte-diffed, because it
# carries `RATIO_CEILING` and nothing else in the kit does. That key is the
# single documented placeholder exemption, so leaving it to the tool's own
# selftest would be an expectation read from its own subject - the exact class
# `expectation_lint.py` exists to surface. The other three carry only slots
# CLAUDE.md also carries, and CLAUDE.md is byte-diffed, so hand-rendering them
# would add no expectation the diff does not already hold.
# The third phase outcome. A sentinel rather than a bare string so `ok is True`
# and `ok == SKIP` can never be confused by a truthy value drifting in.
SKIP = "SKIP"

RENDER_TOOL = KIT / "tools" / "kit_render.py"

HAND_RENDERED = ("CLAUDE.md", ".claude/settings.json",
                 "docs/collaboration-profile.md", "docs/JUDGMENT-LEDGER.md",
                 "docs/FAILURE-FLOOR.md", "docs/LESSONS.md",
                 "docs/TOKEN-LEDGER.md")

RENDER_STEPS = ("check the substitution and header-stripping in "
                "tools/kit_render.py against the hand rendering in "
                "document_order() above - one of the two is wrong, and the "
                "printed diff says which lines. WHICH SIDE WINS: neither on "
                "its own authority. The hand model is the EXPECTATION and the "
                "tool is the SUBJECT UNDER TEST, so investigate both, and let "
                "the QUICKSTART step the hand model transcribes arbitrate - "
                "the document is the third party. On this phase's first run "
                "the two disagreed and Step 8 ruled for the tool. Editing "
                "whichever side is easier to change is how guard 6 collapses.")


def json_first_diff(want, got, path="settings"):
    """Where two parsed-JSON structures first disagree, as a readable string.

    A CHECK THAT COMPARES OBJECTS MUST NOT REPORT KEY LISTS. This sub-step
    asserts `t_obj == h_obj` - full structural equality - and its failure
    detail used to print `sorted(t_obj)` vs `sorted(h_obj)`. When the two
    differ in a VALUE, which is the usual case, those two lists are identical
    and the message says nothing. Worse, it looks like evidence: the Windows CI
    red on kit commit f608230 printed two identical key lists and sent the
    first reader hunting for a missing key. The message now names the path to
    the first difference and shows both values."""
    if type(want) is not type(got):
        return (f"{path}: type differs - hand has {type(want).__name__}, "
                f"tool has {type(got).__name__}")
    if isinstance(want, dict):
        for k in sorted(set(want) | set(got)):
            if k not in want:
                return f"{path}.{k}: present in the tool's output only"
            if k not in got:
                return f"{path}.{k}: present in the hand model only"
            if want[k] != got[k]:
                return json_first_diff(want[k], got[k], f"{path}.{k}")
        return f"{path}: no difference found (the two are equal)"
    if isinstance(want, list):
        if len(want) != len(got):
            return (f"{path}: length differs - hand has {len(want)}, tool has "
                    f"{len(got)}")
        for i, (a, b) in enumerate(zip(want, got)):
            if a != b:
                return json_first_diff(a, b, f"{path}[{i}]")
        return f"{path}: no difference found (the two are equal)"
    return f"{path}: hand has {want!r}, tool has {got!r}"


def render_agrees(tmp: Path, py: str, verbose: bool = False):
    """(ok, [(label, ok, detail)]) - the tool run over phase 9's tree."""
    root = tmp / "doc-order-project"
    res: list[tuple[str, bool, str]] = []

    def step(label, ok, detail=""):
        res.append((label, bool(ok), detail))
        return bool(ok)

    if not (root / "CLAUDE.md").is_file():
        step("phase 9's hand-rendered tree is on disk to compare against",
             False, "document_order() did not leave a rendered tree")
        return False, res
    if not RENDER_TOOL.is_file():
        step("tools/kit_render.py is shipped", False, f"missing {RENDER_TOOL}")
        return False, res

    before = {rel: (root / rel).read_bytes() for rel in HAND_RENDERED
              if (root / rel).is_file()}

    # ---- PRE-FLIGHT: the two sides must agree on the SPELLING of the root --
    # Guard 5 says the tool RESOLVES the repository root rather than being told
    # it. That is right, and it means the walk must hand the tool a directory
    # whose resolved form is the one the walk itself embedded in the settings
    # file. When those diverged - an 8.3 short TEMP on the Windows CI runner -
    # every downstream symptom was three appended hook entries, which reads as
    # a merge defect and is not one. Assert the real condition here, so the
    # failure names the cause instead of the symptom.
    step("PRE-FLIGHT: the hand model's repo root is already canonical, so the "
         "tool's resolution of it cannot produce a second spelling",
         root == root.resolve(),
         f"the walk built {root.as_posix()} but it resolves to "
         f"{root.resolve().as_posix()} - two spellings of one directory. "
         f"Every rendered {{{{PROJECT_ROOT}}}} would differ from the tool's, "
         f"and the settings merge would append rather than match. Canonicalise "
         f"`tmp` where it is created in main()."
         if root != root.resolve() else "")

    protected = (root / "protected").as_posix()
    values = list(gov_slots(protected)) + [
        # The three the governance template does not carry: two settings slots
        # and the ledger's one documented survivor.
        ("STATUSLINE_CMD", f"python {root.as_posix()}/tools/statusline.py"),
        ("PYTHON_BIN", "python"),
        ("RATIO_CEILING", "derive-from-your-own-data"),
    ]
    cmd = [py, str(RENDER_TOOL), "--target", str(root)]
    for k, v in values:
        cmd += ["--set", f"{k}={v}"]
    rc, out = run(cmd, root, verbose)
    step("the tool renders the whole set: KIT RENDER: PASS, exit 0, no "
         "unfilled slot", rc == 0 and "KIT RENDER: PASS" in out,
         _last(out) if rc != 0 else "")

    after = {rel: (root / rel).read_bytes() for rel in HAND_RENDERED
             if (root / rel).is_file()}
    changed = sorted(k for k in before if before[k] != after.get(k))
    step("GUARD 2: not one hand-rendered file was touched - the tool writes "
         "only .kit-new", not changed, f"modified {changed}")

    def newfile(rel):
        p = root / (rel + ".kit-new")
        return p.read_text(encoding="utf-8") if p.is_file() else None

    # ---- the exact diffs: three text files, byte for byte ----------------
    for rel in ("CLAUDE.md", "docs/collaboration-profile.md",
                "docs/TOKEN-LEDGER.md"):
        tool_text = newfile(rel)
        hand_text = (root / rel).read_text(encoding="utf-8")
        if tool_text is None:
            step(f"{rel}: the tool wrote a .kit-new", False, "no file")
            continue
        same = tool_text == hand_text
        detail = ""
        if not same:
            diff = list(difflib.unified_diff(
                hand_text.splitlines(), tool_text.splitlines(),
                fromfile=rel + " (hand)", tofile=rel + ".kit-new (tool)",
                lineterm=""))
            detail = (" | ".join(d for d in diff[2:10]) + f" ... "
                      f"{len(diff)} diff lines. {RENDER_STEPS}")
        step(f"{rel}: the tool's rendering is BYTE-IDENTICAL to the hand "
             f"model's", same, detail)

    # ---- the settings file: structural, because the tool MERGED ----------
    # The hand model already wrote .claude/settings.json, so the tool took its
    # merge path. If the two renderings agree, the merge is a semantic no-op
    # and the parsed objects are equal. If the tool substituted anything
    # differently, the merge appends rather than matching, and the structure
    # assertions below name which block.
    tool_settings = newfile(".claude/settings.json")
    hand_settings = (root / ".claude" / "settings.json").read_text(
        encoding="utf-8")
    try:
        t_obj = json.loads(tool_settings or "")
        h_obj = json.loads(hand_settings)
    except ValueError as e:
        step(".claude/settings.json: both renderings parse as JSON", False,
             f"{e}")
        t_obj = h_obj = None
    if t_obj is not None:
        step(".claude/settings.json: the structural merge of the tool's "
             "rendering into the hand model's file is a NO-OP - the two agree "
             "key for key", t_obj == h_obj,
             "" if t_obj == h_obj else
             f"first difference at {json_first_diff(h_obj, t_obj)}. "
             f"{RENDER_STEPS}")
        blocks = (t_obj.get("hooks") or {}).get("PreToolUse") or []
        arms = [b.get("matcher") for b in blocks if isinstance(b, dict)]
        step(".claude/settings.json: all THREE matcher blocks, one hook each "
             "- the merge appended nothing",
             len(blocks) == 3
             and all(len(b.get("hooks", [])) == 1 for b in blocks),
             f"matchers {arms}, hook counts "
             f"{[len(b.get('hooks', [])) for b in blocks]}. A count of two "
             f"under one matcher means the tool's command string differs from "
             f"the hand model's - usually {{{{PROJECT_ROOT}}}}.")

    # ---- the other three ledgers: Step 7's checkpoint, not a diff --------
    # TOKEN-LEDGER.md is byte-diffed above. These three carry only slots that
    # CLAUDE.md already carries, and CLAUDE.md is byte-diffed, so a hand
    # rendering of them would add no expectation the diff does not hold
    # already. What is left uncovered here is a wrong-but-well-formed value in
    # a slot unique to one of these three - and there is none.
    ledger_problems = []
    for name in ("JUDGMENT-LEDGER.md", "FAILURE-FLOOR.md", "LESSONS.md"):
        rel = "docs/" + name
        text = newfile(rel)
        if text is None:
            ledger_problems.append(f"{rel}: no .kit-new written")
            continue
        left = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
        if left:
            ledger_problems.append(f"{rel}: unfilled {left}")
        if "SKELETON" in text:
            ledger_problems.append(f"{rel}: SKELETON header block survived")
    step("the other three ledgers meet Step 7's checkpoint - no surviving "
         "slot, no SKELETON header (checked, not diffed: the hand model copies "
         "those three unrendered, and every slot they carry is already covered "
         "by the CLAUDE.md byte-diff)",
         not ledger_problems, "; ".join(ledger_problems))

    # ---- GUARD 1, against the real kit tree ------------------------------
    # The selftest proves the refusal in process. This is the only place it is
    # aimed at the actual kit checkout, which is the thing it exists to
    # protect - the same argument phase 12 makes about the exclusion probe.
    strays_before = {p for p in KIT.rglob("*.kit-new")}
    rc_k, out_k = run([py, str(RENDER_TOOL), "--target", str(KIT)], KIT,
                      verbose)
    strays = sorted(p.relative_to(KIT).as_posix()
                    for p in KIT.rglob("*.kit-new") if p not in strays_before)
    for p in strays:                      # never leave the kit tree dirty
        (KIT / p).unlink(missing_ok=True)
    step("GUARD 1: pointed at the kit clone itself the tool ABORTS (exit 2), "
         "names it, and writes nothing into the kit",
         rc_k == 2 and "inside the kit clone" in out_k and not strays,
         f"exit {rc_k} · wrote {strays} into the kit tree · {_last(out_k)}"
         if (rc_k != 2 or strays) else "")

    # ---- GUARD 1b, against a real repository -----------------------------
    # `LEDGERS_DIR = ../shared-docs` is a plausible monorepo value. It used to
    # write four files outside the repository the tool was pointed at, create
    # the directory on the way, and report PASS. The selftest proves the
    # refusal in process; this proves it end to end with a real target, a real
    # subprocess and a real filesystem - the same argument phase 12 makes.
    outside = tmp / "OUTSIDE-THE-TARGET"
    rel_out = os.path.relpath(str(outside), str(root)).replace("\\", "/")
    # `--force` because the run above already left `.kit-new` files in this
    # tree, and guard 2 would otherwise abort first - with exit 2 and the wrong
    # message, which is a sub-check that passes on the wrong evidence. The
    # containment refusal happens while the plan is built, before any write, so
    # --force changes nothing about what this measures.
    rc_e, out_e = run([py, str(RENDER_TOOL), "--target", str(root), "--force",
                       "--set", f"LEDGERS_DIR={rel_out}"], root, verbose)
    step("GUARD 1b: an output path that climbs OUT of the target repo ABORTS "
         "(exit 2), names the config key, and creates nothing outside",
         rc_e == 2 and "OUTSIDE the target repository" in out_e
         and not outside.exists(),
         f"exit {rc_e} · {outside} exists={outside.exists()} · {_last(out_e)}"
         if (rc_e != 2 or outside.exists()) else "")

    return all(ok for _, ok, _ in res), res


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate the kit's adoption path.")
    ap.add_argument("--keep", action="store_true",
                    help="leave the scaffold on disk and print its path")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--runner", default="",
                    help="Adopt THIS verify.py instead of the kit's. Without "
                         "it the smoke copies the KIT's pristine runner, so it "
                         "tests the kit rather than your edits. NOTE THE "
                         "LIMIT: the scaffold adapts the runner by renaming "
                         "`example_unit` and deleting `example_lint`, so a "
                         "runner that has already been ADAPTED (its example "
                         "gates replaced) will abort with 'update this "
                         "script'. --runner is for a copy you have edited "
                         "around the examples, not one you have finished "
                         "adopting.")
    ap.add_argument("--plant-f1", action="store_true",
                    help="NEGATIVE CONTROL: re-introduce the original repo-root "
                         "defect in the scaffold's copy of the runner. The "
                         "expected outcome is FAIL. A green run under this flag "
                         "means this smoke has stopped detecting the thing it "
                         "was written for.")
    a = ap.parse_args()

    global RUNNER
    if a.runner:
        RUNNER = Path(a.runner).resolve()
        print(f"{YELLOW}adopting {RUNNER} instead of the kit's runner{RESET}")
    for f in (RUNNER, HOOK, FIXTURES, SETTINGS_TMPL, RENDER_TOOL):
        if not f.exists():
            print(f"ABORT: missing kit file {f}", file=sys.stderr)
            return 2

    # CANONICALISE THE SCAFFOLD ROOT ONCE, HERE, AT THE SOURCE.
    #
    # Every path this walk embeds in a rendered file derives from `tmp`, and on
    # Windows `tempfile.gettempdir()` can hand back an 8.3 SHORT path - the
    # hosted CI runner's TEMP is under `C:\Users\RUNNER~1\...`. The render tool
    # resolves the repository root it is given (guard 5, `Path.resolve()`,
    # which expands 8.3 aliases); this walk used the directory exactly as
    # `mkdtemp` spelled it. Two spellings of one directory, two different
    # `{{PROJECT_ROOT}}` strings, and the settings merge - which matches hook
    # entries by their `command` - saw three commands it had never seen and
    # appended all three. Signature: hook counts [2, 2, 2]. Windows CI went red
    # on kit commit f608230 while Linux CI and every local run stayed green,
    # because only Windows has 8.3 aliases.
    #
    # `Path.resolve()` is idempotent, so resolving here and again in the tool
    # cannot disagree: the two sides are canonicalised by the same standard
    # library call from the same starting directory. The walk is NOT importing
    # the tool's resolution to achieve this - that would delete guard 5's
    # independent expectation - it is independently applying the same rule the
    # QUICKSTART states, which is that {{PROJECT_ROOT}} is the absolute path to
    # the repo root. An 8.3 alias is an absolute path but it is not that path:
    # it is a per-volume alias that need not exist at all, since 8.3 generation
    # can be switched off.
    tmp = Path(tempfile.mkdtemp(prefix="adoption-smoke-")).resolve()
    root = tmp / "scaffolded-project"
    results: list[tuple[str, bool, str]] = []

    def phase(name, ok, detail=""):
        """`ok` is True, False, or SKIP - three outcomes, three words."""
        results.append((name, ok, detail))
        tag = (f"{YELLOW}SKIP{RESET}" if ok == SKIP else
               f"{GREEN}PASS{RESET}" if ok is True else f"{RED}FAIL{RESET}")
        print(f"  [{tag}] {name}" + (f"\n         {detail}" if detail else ""))

    try:
        print(f"{BOLD}adoption smoke — scaffolding into {root}{RESET}")
        if a.plant_f1:
            print(f"{YELLOW}*** NEGATIVE CONTROL: the F1 repo-root defect has "
                  f"been planted in the scaffold. FAIL is the expected and "
                  f"correct outcome. ***{RESET}")

        # ---- 1. scaffold ------------------------------------------------
        scaffold(root, planted=a.plant_f1)
        git(["init", "-q"], root)
        git(["add", "-A"], root)      # a throwaway scaffold, not a real repo
        rc, _ = git(["commit", "-q", "-m", "scaffold"], root)
        phase("1. scaffold: a real git repo with the kit copied in",
              rc == 0 and (root / ".git").exists())

        py = sys.executable
        vr = ["tools/verify.py"]

        # ---- 2/3. the copied runner's own bench -------------------------
        rc, out = run([py, *vr, "--selftest"], root, a.verbose)
        ok = rc == 0 and "VERIFY SELFTEST: PASS" in out
        phase("2. selftest passes with BOTH example gates deleted (F2)", ok,
              "" if ok else out.strip().splitlines()[-1] if out.strip() else "no output")

        # Section A/B must have ACTUALLY skipped, and no example gate may
        # survive anywhere - otherwise "the example gates are deleted" is a
        # sentence rather than a fact, which is how the section-F bug shipped.
        skipped_ab = "A/B skipped" in out
        rc2, listing = run([py, *vr, "--list"], root)
        no_examples = rc2 == 0 and "example" not in listing
        phase("3. ...on the guarded path, with NO example gate left anywhere",
              skipped_ab and no_examples,
              "" if (skipped_ab and no_examples) else
              f"A/B skipped={skipped_ab}; --list still mentions an example gate"
              f" = {'example' in listing}")

        # ---- 4. a full certification ------------------------------------
        rc, out = run([py, *vr], root, a.verbose)
        ok = rc == 0 and "VERIFY: PASS" in out
        line = next((l for l in out.splitlines() if "VERIFY:" in l), "")
        phase("4. a full run certifies: VERIFY: PASS, exit 0", ok,
              re.sub(r"\033\[[0-9;]*m", "", line).strip())

        # The repo root must have resolved to the SCAFFOLD ROOT, not to
        # tools/. Compared as a resolved path, not by looking for the
        # substring "tools" - a long temp path made the substring version pass
        # under the planted defect, which is a check that agrees with whatever
        # it is shown.
        reported = ""
        for l in re.sub(r"\033\[[0-9;]*m", "", out).splitlines():
            if l.strip().startswith("repo:"):
                reported = l.split("repo:", 1)[1].split("  (")[0].strip()
        root_ok = bool(reported) and Path(reported).resolve() == root.resolve()
        phase("5. the runner resolved the repo root above tools/ (F1)",
              root_ok,
              "" if root_ok else f"resolved to {reported!r}, expected {root}")

        # ---- 6. THE TRAP ------------------------------------------------
        # Dirty a CERTIFIED path. Under the old file-relative root this stayed
        # green forever, because `git -C tools status -- src` prints nothing.
        (root / "src" / "uncommitted.py").write_text("# not committed\n",
                                                     encoding="utf-8")
        rc, out = run([py, *vr, "--only", "judges"], root, a.verbose)
        ok = rc == 1 and "RED: judges" in out and "uncommitted.py" in out
        phase("6. THE F1 TRAP: a dirty certified path turns `judges` RED", ok,
              "" if ok else f"exit {rc} - the trap has RECURRED")
        (root / "src" / "uncommitted.py").unlink()

        # ---- 7. the startup assertion -----------------------------------
        rt = (root / "tools" / "verify.py").read_text(encoding="utf-8")
        (root / "tools" / "verify.py").write_text(
            rt.replace('CERT_PATHS = ["src"]',
                       'CERT_PATHS = ["a-path-that-does-not-exist"]'),
            encoding="utf-8")
        rc, out = run([py, *vr, "--only", "judges"], root, a.verbose)
        ok = rc == 2 and "a-path-that-does-not-exist" in out
        phase("7. a path that does not exist ABORTS (exit 2) and is NAMED", ok,
              "" if ok else f"exit {rc} - a missing cert path went unnoticed")
        (root / "tools" / "verify.py").write_text(rt, encoding="utf-8")

        # ---- 8. MAJOR-2: the config is part of the judge surface --------
        # An uncommitted kit.config edit changes what the hook DECIDES, and
        # the fixture guarding the affected rule reads its expectation from
        # the same file - so the fixture moves with it and sees nothing. The
        # judges gate is the only thing that can catch this for every key.
        cfg = root / "kit.config"
        before = cfg.read_text(encoding="utf-8")
        cfg.write_text(before.replace("FORBIDDEN_SPAWN_TIER = orchestrator-tier",
                                      "FORBIDDEN_SPAWN_TIER = nothing-is-forbidden"),
                       encoding="utf-8")
        rc, out = run([py, *vr], root, a.verbose)
        ok = rc == 1 and "RED: judges" in out and "kit.config" in out
        phase("8. MAJOR-2: an uncommitted kit.config edit turns `judges` RED",
              ok, "" if ok else f"exit {rc} - a weakened rule certified clean")
        cfg.write_text(before, encoding="utf-8")

        # ---- 9. THE CLASS GUARD: the QUICKSTART, in document order ------
        if a.plant_f1:
            phase("9. QUICKSTART in document order (skipped under --plant-f1)",
                  True, "the planted defect would red it for the wrong reason")
        else:
            ok_seq, seq = document_order(tmp, py, a.verbose)
            for label, sub_ok, detail in seq:
                tag = f"{GREEN}ok  {RESET}" if sub_ok else f"{RED}RED {RESET}"
                print(f"        [{tag}] {label}"
                      + (f"\n               {detail}" if detail and not sub_ok
                         else ""))
            phase("9. THE CLASS GUARD: QUICKSTART steps 1-2, 4-7, step 8's "
                  "rendered profile and step 9 are each reachable when the "
                  "document is obeyed IN ORDER", ok_seq,
                  "" if ok_seq else "a documented step cannot be completed "
                                    "where the document places it")

        # ---- 10. the slot registry, checked against itself --------------
        probs, n_t, n_skip, n_walk = slot_problems(KIT)
        for x in probs[:12]:
            print(f"        {RED}slot{RESET} {x}")
        # The headline states COVERAGE, not just the green count. The previous
        # wording read as "all templates checked" while ten slot-using files
        # carried no detected manifest and were skipped without a number.
        phase(f"10. every slot in all {n_t + n_skip} slot-using files under "
              f"modules/ is registered, and the {n_t} of them that carry a "
              f"SLOTS manifest match their bodies ({n_skip} carry no manifest: "
              f"registry checked, body-vs-manifest not applicable) — plus the "
              f"{n_walk} walk document(s) at the root, registry-checked on the "
              f"slots they name in prose", not probs,
              "" if not probs else f"{len(probs)} manifest/registry problem(s)")

        # ---- 11. THE CLASS, AS A LINT -----------------------------------
        # Eight defects across six walks were one defect: a check whose
        # expectation comes from the artifact it is asserting about. This is
        # that design question promoted to a mechanical layer.
        rc, out = run([py, str(LINT)], KIT, a.verbose)
        # r30 fix pass: the lint's green line joined the state-word family
        # ("PASS - N registry entrie(s) checked, 0 self-referential").
        clean = rc == 0 and ("EXPECTATION LINT: PASS" in out
                             and "0 self-referential" in out)
        n_waived = sum(1 for ln in out.splitlines() if "WAIVED -" in ln)
        phase(f"11. no check reads its expectation from its own subject "
              f"({n_waived} legitimate self-references, each waived with a "
              f"printed reason)", clean,
              "" if clean else _last(out))

        rcn, outn = run([py, str(LINT), "--selftest"], KIT, a.verbose)
        nc_ok = rcn == 0 and "EXPECTATION-LINT SELFTEST: PASS" in outn
        phase("11b. ...and the lint itself fires on both reconstructed "
              "negative controls (fixture-j and armed-check patterns)", nc_ok,
              "" if nc_ok else _last(outn))

        # ---- 12. THE GITIGNORED JUDGE PATH ------------------------------
        # The only place in the kit that runs the shipped exclusion probe
        # against a real repository. The runner's selftest cannot: it injects
        # an answer, and a probe that returned the wrong answer for every path
        # once passed the whole suite.
        ok_ex, ex = excluded_judge_path(tmp, py, a.verbose)
        for label, sub_ok, detail in ex:
            tag = f"{GREEN}ok  {RESET}" if sub_ok else f"{RED}RED {RESET}"
            print(f"        [{tag}] {label}"
                  + (f"\n               {detail}" if detail and not sub_ok
                     else ""))
        phase("12. a gitignored judged path ABORTS the runner by name — "
              "exact-path rule and directory rule, JUDGE_PATHS and CERT_PATHS, "
              "first and last in the batch — and force-tracking clears it",
              ok_ex,
              "" if ok_ex else "the judges gate can be blinded by an ignore "
                               "rule, or a tracked path false-aborts")

        # ---- 13. THE OPTIONAL RENDER TOOL, DIFFED AGAINST THE HAND MODEL --
        # Two independent renderings of the same seven templates, required to
        # agree. The hand model above is unchanged and remains the
        # transcription a person maintains; this adds the second opinion.
        if a.plant_f1:
            # ASSERT THE PRECONDITION, DO NOT ASSERT THE REASON. The reason
            # ("phase 9 did not run, so there is no tree to diff") is a claim
            # about the world; the precondition is checkable. The same shape
            # phase 3 above uses for the runner's A/B sections - it asserts
            # that they ACTUALLY skipped rather than trusting that they did.
            absent = not (tmp / "doc-order-project" / "CLAUDE.md").is_file()
            phase("13. kit_render.py agrees with the hand model",
                  SKIP if absent else False,
                  "phase 9 is skipped under --plant-f1, and its hand-rendered "
                  "tree is verified absent, so there is nothing to diff "
                  "against" if absent else
                  "SKIP CLAIMED BUT FALSE: a hand-rendered tree IS on disk at "
                  f"{tmp / 'doc-order-project'}, so this phase could have run "
                  "and refused to. The skip branch is reachable when it should "
                  "not be - check the condition that selected it.")
        else:
            ok_rn, rn = render_agrees(tmp, py, a.verbose)
            for label, sub_ok, detail in rn:
                tag = f"{GREEN}ok  {RESET}" if sub_ok else f"{RED}RED {RESET}"
                print(f"        [{tag}] {label}"
                      + (f"\n               {detail}" if detail and not sub_ok
                         else ""))
            phase("13. the OPTIONAL render tool agrees with the hand-built "
                  "adopter model, writes only .kit-new, and refuses to write "
                  "into the kit clone", ok_rn,
                  "" if ok_rn else "the two renderings of the same templates "
                                   "disagree, or a guard did not hold")

    finally:
        if a.keep:
            print(f"\nscaffold kept: {root}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    # A SKIPPED PHASE IS ITS OWN WORD AND ITS OWN ARITHMETIC. Counting a skip
    # as green is the anti-pattern this kit names about gates and had inside
    # its own runner: "the check did not run" and "the check passed" must never
    # look the same. Phase 13's `--plant-f1` branch reported PASS and left the
    # headline at 14/14, so unwiring the phase with one flipped token produced
    # a fully green run that certified nothing.
    passed = sum(1 for _, ok, _ in results if ok is True)
    failed = sum(1 for _, ok, _ in results if ok is False)
    skipped = sum(1 for _, ok, _ in results if ok == SKIP)
    total = len(results)
    print()
    # THE VERDICT VOCABULARY, borrowed from the verify runner's own contract:
    # an instrumented run gets its OWN WORD and its OWN NONZERO EXIT, so a
    # human reading the line and a script reading `$?` reach the same
    # conclusion. The previous version printed FAIL and exited 0 - the two
    # audiences disagreed, and the one that automates would have been told the
    # adoption path was fine.
    #
    #   0  PASS          every phase green, uninstrumented. The only good run.
    #   1  FAIL          a phase went red - or the planted defect went
    #                    UNDETECTED, which is the same kind of news.
    #   2  INSTRUMENTED  --plant-f1 was passed. Never a certification, and
    #                    "PASS" is unreachable from here.
    tally = f"{passed}/{total} phases" + (f", {skipped} SKIPPED" if skipped
                                          else "")
    if a.plant_f1:
        # The control's own control, and it reads RED COUNT rather than green
        # count: a phase that skips is not evidence the defect was detected,
        # so `passed == total` would let a skip disguise a control that had
        # stopped firing.
        if failed == 0:
            print(RED + f"ADOPTION SMOKE: FAIL — {tally}, NOTHING RED "
                        f"WITH THE DEFECT PLANTED" + RESET)
            print(RED + "NEGATIVE CONTROL DID NOT FIRE: this smoke no longer "
                        "detects the defect it exists for. Fix the smoke "
                        "before trusting any green from it." + RESET)
            return 1
        print(YELLOW + f"ADOPTION SMOKE: INSTRUMENTED — {failed} of "
                       f"{total} phases red with the F1 defect planted, as "
                       f"required ({tally}). This run certifies nothing."
              + RESET)
        return 2

    # A SKIP CANNOT CERTIFY. Nothing is expected to skip on the shipped path,
    # so a skip here means a phase was disabled and the run must say FAIL
    # rather than count it green.
    verdict = "PASS" if (failed == 0 and skipped == 0) else "FAIL"
    print((GREEN if verdict == "PASS" else RED)
          + f"ADOPTION SMOKE: {verdict} — {tally}" + RESET)
    if verdict == "FAIL" and skipped:
        print(RED + f"{skipped} phase(s) SKIPPED on a normal run. A skipped "
                    f"phase and a passing phase must never look the same; "
                    f"nothing is expected to skip here." + RESET)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
