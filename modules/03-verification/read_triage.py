#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""read_triage.py -- score a charter and its diff, suggest OFFICER or
GATES-ONLY, and print exactly one line.

    python read_triage.py --charter <file> --diff-range <rev1>..<rev2> --repo <dir>
    python read_triage.py --charter <file> --patch <diff-file>
    python read_triage.py --charter <file> --patch <diff-file> --json
    python read_triage.py --charter <file> --patch <diff-file> --bar <n>
    python read_triage.py --selftest

    exit 0  a decision was printed (OFFICER or GATES-ONLY)
    exit 3  the charter or the diff could not be read
    exit 1  --selftest found a case that did not match its expectation

==========================================================================
WHAT THIS DOES NOT DO
==========================================================================
This tool SUGGESTS. It never runs a review, never edits a file, never
blocks a merge, and never writes a decision anywhere. The coordinator
reads the one line this prints, decides OFFICER or GATES-ONLY, and logs
the disposition themselves -- the same split module 01's governance
already draws between an instrument and a ruling. A score at or above
the bar is not an order to spawn a reviewer; it is this tool's best guess,
stated with its reasons, so the coordinator does not have to re-derive
them from the diff by eye every time.

==========================================================================
PRIOR ART -- the touch set this formalizes, named so a change to the
source does not silently orphan this file
==========================================================================
- The JUDGE-SURFACE category is the reviewer charter's own check 4,
  `modules/01-governance/charters/CHARTER-reviewer.md` lines 52-55:
  "Did this diff touch anything that decides what green means -- gates,
  hooks, fixtures, CI config, cert tokens, thresholds?" That list is
  OPERATIONALIZED here as the file set `kit.config`'s own `JUDGE_PATHS`
  and `CERT_PATHS` slots already enumerate (verify.py, the examples
  fixtures, the two hooks, the settings file, kit.config itself, the
  checks registry, and the cert-green token file) plus the containment
  scanner this charter's sibling work named
  (`tools/capsule_containment.py`), which the shipped kit does not carry
  and the reviewer's list therefore could not have named. "Settings
  file" is NOT in the reviewer charter's literal six-item list (gates,
  hooks, fixtures, CI config, cert tokens, thresholds) -- it enters here
  because `kit.config`'s own `JUDGE_PATHS` lists `.claude/settings.json`
  as a judge path, and the reviewer's abstract categories fold through
  that concrete list. This is flagged in the READ TRIAGE report as a
  finding: naming it "the reviewer charter's own list, plus containment"
  undercounts by one category (settings file) unless the fold-through is
  made explicit, which this paragraph now does.
- The punch-list triage vocabulary (`modules/01-governance/PUNCH-LIST-TEMPLATE.md`
  Part 2) is a per-item human verdict table; this tool is not that table
  and does not reuse its vocabulary (OFFICER/GATES-ONLY is a routing
  decision about a whole diff, not an item disposition) -- named so the
  overlap is not mistaken for reuse.
- The one-line, self-consistent-ratio contract (`modules/03-verification/gate_line.py`
  docstring, "THE SHAPE CONTRACT") is echoed in spirit: one summary line,
  a distinct machine-readable shape, a `--selftest` that proves both
  directions. This tool's line has no ratio to be self-consistent about
  (there is one score, not a numerator and a denominator), so the
  contract is not literally reused, only its discipline.
- `read_kit_config()` below is copied, not re-invented, from
  `modules/03-verification/verify.py`'s `read_kit_config()` (its four-step
  search order: `$KIT_CONFIG`, cwd, this file's directory, then walking up)
  so `READ_TRIAGE_BAR` is found the same way every other kit.config slot is.
- "WHEN THE LOOP ENDS" (`modules/01-governance/CLAUDE.md.template`) is the
  reason this tool exists at the coordinator's request: an officer read at
  opus on every build is the current blanket rule, and this scores whether
  a given build needs it or whether the gates alone suffice -- it does not
  change the loop's own stopping rules (one round, diminishing severity,
  the verdict vocabulary), which are out of scope here.

==========================================================================
THE TERMS -- each is DATA, not a buried conditional. See TERMS below.
==========================================================================

| Term          | Points | Fires when...                                                              |
|---------------|--------|------------------------------------------------------------------------------|
| JUDGE-SURFACE | +3     | the diff touches a path in JUDGE_SURFACE_PATTERNS (a gate, hook, fixture,    |
|               |        | CI config, cert token, threshold/settings file, or a containment scanner)   |
| OUTWARD       | +3     | the CHARTER text names a push, a tag, a release, a send, or a publish as a  |
|               |        | step (a keyword scan, not a step-list parser -- see the false-positive note) |
| NEW-CLAIM     | +2     | the diff adds a new file matching a lint/gate/tool-with-selftest/claim-page  |
|               |        | pattern in NEW_CLAIM_PATTERNS                                                |
| SIZE          | +1/300 | changed lines (added+removed, excluding diff headers), capped at +3          |
| AUTHORITY     | +2     | the charter or the diff names an authorization, a signed word, an envelope, |
|               |        | or a key (a keyword scan in AUTHORITY_KEYWORDS)                             |
| SUGGEST-ONLY  | -2     | the charter contains the literal phrase "suggests, never routes"            |

OFFICER at or above READ_TRIAGE_BAR (kit.config, default 3); GATES-ONLY
below it. The bar is the adopter's slot to move.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ==========================================================================
# TERMS -- the scoring data. Every pattern list here is what item 1 asks
# for: data a reader can audit without reading the scoring logic.
# ==========================================================================

# JUDGE_SURFACE_PATTERNS: substrings matched against each changed file's
# path (case-insensitive). Sourced from kit.config's own JUDGE_PATHS and
# CERT_PATHS slots. This is a literal, hand-kept list, not a live read of
# kit.config -- selftest case (h) asserts every JUDGE_PATHS entry the
# box's own kit.config lists today matches one of these patterns, so a
# drift between the two would be caught there, not read live. (--selftest
# itself passes an explicit --bar to every case, so its verdicts do not
# depend on whichever kit.config happens to be found on the run's own
# search path -- see get_bar/read_kit_config, used only for the real,
# non-selftest bar.) Each entry is (category, substring, source).
JUDGE_SURFACE_PATTERNS = [
    ("gate", "modules/03-verification/verify.py", "kit.config JUDGE_PATHS"),
    ("gate", "gate_line.py", "kit.config JUDGE_PATHS (examples/ dir it ships from)"),
    ("gate", "_gate.py", "generic gate-file naming convention"),
    ("hook", "hook_model_gate.py", "kit.config JUDGE_PATHS"),
    ("hook", "hook_fixtures.py", "kit.config JUDGE_PATHS"),
    ("hook", "/hook_", "generic hook-file naming convention"),
    ("fixture", "modules/03-verification/examples", "kit.config JUDGE_PATHS"),
    ("fixture", "fixtures", "generic fixture-directory naming convention"),
    ("ci-config", ".github/workflows", "reviewer charter check 4, 'CI config'"),
    ("ci-config", "ci.yml", "reviewer charter check 4, 'CI config'"),
    ("cert-token", ".claude/cert-green.json", "kit.config CERT_TOKEN_FILE"),
    ("cert-token", "checks-registry.json", "kit.config JUDGE_PATHS"),
    ("threshold", "kit.config", "kit.config JUDGE_PATHS (lists itself)"),
    ("settings", ".claude/settings.json", "kit.config JUDGE_PATHS"),
    ("containment", "capsule_containment", "names a tool outside this kit; not shipped here"),
]

# NEW_CLAIM_PATTERNS: a new (added) file matching one of these substrings
# is treated as a new claim-bearing surface (module 01's SHIP REQUIREMENTS
# vocabulary: "a check, a lint, a gate, a published study, a comparison
# page"). Content patterns are checked only on files that also match a
# name pattern, so this stays a file-pattern table, not free content search.
NEW_CLAIM_NAME_PATTERNS = [
    ("new-lint", "lint.py"),
    ("new-gate", "_gate.py"),
    ("new-gate", "gate_line"),
    ("new-tool-selftest", ".py"),  # gated below on "--selftest" appearing in the added lines
    ("new-claim-page", "COMPARISON"),
    ("new-claim-page", "STUDY"),
    ("new-claim-page", "BRIEF"),
]

# AUTHORITY_KEYWORDS: word-boundary, case-insensitive.
AUTHORITY_KEYWORDS = ["authoriz", "authoris", "signed word", r"\bsigned\b", "envelope", r"\bkey\b"]

# OUTWARD_KEYWORDS: word-boundary, case-insensitive. Scanned against the
# CHARTER text, not the diff. KNOWN LIMITATION, stated rather than
# silently patched: this is a keyword scan, not a step-list parser, so a
# charter that PROHIBITS a push ("no push, no tag, no release") or that
# quotes someone else's push in reported speech reads identically to a
# charter that ORDERS one. --selftest proves the tool's own arithmetic;
# it does not prove the scan tells "no push" from "push". Item 3's real
# instances exercise this limitation and the report names the result.
OUTWARD_KEYWORDS = [r"\bpush\b", r"\btag\b", r"\brelease\b", r"\bsend\b", r"\bpublish\b"]

SUGGEST_ONLY_PHRASE = "suggests, never routes"

DEFAULT_BAR = 3


# ==========================================================================
# kit.config -- copied from modules/03-verification/verify.py's
# read_kit_config(), same four-step search order, so READ_TRIAGE_BAR is
# found the way every other slot is. See the PRIOR ART note above.
# ==========================================================================

def read_kit_config(start: Path) -> dict:
    cands: list[Path] = []
    env = os.environ.get("KIT_CONFIG")
    if env:
        cands.append(Path(env))
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


def get_bar(cfg: dict, override: int | None) -> int:
    if override is not None:
        return override
    raw = cfg.get("READ_TRIAGE_BAR")
    if raw is None:
        return DEFAULT_BAR
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_BAR


# ==========================================================================
# Diff loading and parsing
# ==========================================================================

class UnreadableInput(Exception):
    pass


def load_diff_text(diff_range: str | None, repo: str | None, patch_file: str | None) -> str:
    if patch_file:
        p = Path(patch_file)
        if not p.is_file():
            raise UnreadableInput(f"patch file not found: {patch_file}")
        try:
            text = p.read_text(encoding="utf-8", errors="strict")
        except Exception as e:
            raise UnreadableInput(f"patch file not readable as text: {patch_file} ({e})")
        return text
    if diff_range:
        if ".." not in diff_range:
            raise UnreadableInput(f"diff range has no '..': {diff_range!r}")
        rev1, rev2 = diff_range.split("..", 1)
        # Refuse a rev that begins with '-': git would read it as an
        # option, not a revision (finding 1, round 1 review -- an
        # "--output=<path>..HEAD" value reached git unguarded and wrote a
        # file at <path>). Caught here, before any subprocess starts.
        for rev in (rev1, rev2):
            if rev.startswith("-"):
                raise UnreadableInput(
                    f"diff range revision refused, begins with '-': {rev!r} -- "
                    "looks like a git option smuggled through the rev slot"
                )
        cmd = ["git"]
        if repo:
            cmd += ["-C", repo]
        cmd += ["diff", rev1, rev2, "--"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        except OSError as e:
            raise UnreadableInput(f"git diff could not be started: {e}")
        if proc.returncode != 0:
            raise UnreadableInput(f"git diff exited {proc.returncode}: {proc.stderr.strip()}")
        return proc.stdout
    raise UnreadableInput("no --diff-range and no --patch given")


class DiffFile:
    def __init__(self, path: str, is_new: bool, added: int, removed: int, added_lines: list[str]):
        self.path = path
        self.is_new = is_new
        self.added = added
        self.removed = removed
        self.added_lines = added_lines


def parse_diff(diff_text: str) -> list[DiffFile]:
    """A lightweight unified-diff parser: enough to name files, count
    added/removed lines and flag new files. Not a full patch applier."""
    files: list[DiffFile] = []
    cur_path = None
    cur_new = False
    cur_added = 0
    cur_removed = 0
    cur_added_lines: list[str] = []
    saw_diff_header = False

    def flush():
        nonlocal cur_path, cur_new, cur_added, cur_removed, cur_added_lines
        if cur_path is not None:
            files.append(DiffFile(cur_path, cur_new, cur_added, cur_removed, cur_added_lines))
        cur_path = None
        cur_new = False
        cur_added = 0
        cur_removed = 0
        cur_added_lines = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            saw_diff_header = True
            flush()
            m = re.match(r"^diff --git a/(.*?) b/(.*)$", line)
            cur_path = m.group(2) if m else line[len("diff --git "):]
            continue
        if line.startswith("new file mode"):
            cur_new = True
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+") and not line.startswith("+++"):
            cur_added += 1
            cur_added_lines.append(line[1:])
            continue
        if line.startswith("-") and not line.startswith("---"):
            cur_removed += 1
            continue
    flush()

    if not saw_diff_header:
        raise UnreadableInput("no 'diff --git' header found -- not a recognizable unified diff")
    return files


# ==========================================================================
# Term scoring
# ==========================================================================

def score_judge_surface(files: list[DiffFile]):
    hits = []
    for f in files:
        low = f.path.replace("\\", "/").lower()
        for category, pattern, source in JUDGE_SURFACE_PATTERNS:
            if pattern.lower() in low:
                hits.append((f.path, category, pattern, source))
    return (len(hits) > 0, hits)


def score_new_claim(files: list[DiffFile]):
    hits = []
    for f in files:
        if not f.is_new:
            continue
        low = f.path.replace("\\", "/")
        for category, pattern in NEW_CLAIM_NAME_PATTERNS:
            if pattern not in low:
                continue
            if category == "new-tool-selftest":
                if any("--selftest" in l for l in f.added_lines):
                    hits.append((f.path, category, pattern))
            else:
                hits.append((f.path, category, pattern))
    return (len(hits) > 0, hits)


def score_size(files: list[DiffFile]) -> int:
    """+1 per 300 changed lines, floored: nothing under 300 changed lines
    scores (finding 5, round 1 review -- ceiling division previously
    awarded +1 to any non-empty diff). Selftest case (d)'s NEW_TOOL_DIFF
    is sized to exactly 300 changed lines on purpose: its bar-1 assertion
    (OFFICER) depends on this term's +1, pinned deliberately rather than
    left incidental -- see case (g) for the analogous, deliberate test of
    AUTHORITY's own crossing."""
    changed = sum(f.added + f.removed for f in files)
    return min(3, changed // 300)  # floor division


def score_outward(charter_text: str):
    hits = []
    for kw in OUTWARD_KEYWORDS:
        for m in re.finditer(kw, charter_text, re.IGNORECASE):
            hits.append(m.group(0))
    return (len(hits) > 0, sorted(set(h.lower() for h in hits)))


def score_authority(charter_text: str, diff_text: str):
    hits = []
    for text, label in ((charter_text, "charter"), (diff_text, "diff")):
        for kw in AUTHORITY_KEYWORDS:
            for m in re.finditer(kw, text, re.IGNORECASE):
                hits.append((label, m.group(0)))
    return (len(hits) > 0, hits)


def score_suggest_only(charter_text: str):
    return SUGGEST_ONLY_PHRASE in charter_text.lower()


def run_score(charter_path: str, diff_range: str | None, repo: str | None,
              patch_file: str | None, bar_override: int | None) -> dict:
    cp = Path(charter_path)
    if not cp.is_file():
        raise UnreadableInput(f"charter file not found: {charter_path}")
    try:
        charter_text = cp.read_text(encoding="utf-8", errors="strict")
    except Exception as e:
        raise UnreadableInput(f"charter file not readable as text: {charter_path} ({e})")

    diff_text = load_diff_text(diff_range, repo, patch_file)
    files = parse_diff(diff_text)

    cfg = read_kit_config(Path(__file__).resolve().parent)
    bar = get_bar(cfg, bar_override)

    terms = []

    js_fired, js_hits = score_judge_surface(files)
    if js_fired:
        terms.append(("JUDGE-SURFACE", 3, js_hits))

    ow_fired, ow_hits = score_outward(charter_text)
    if ow_fired:
        terms.append(("OUTWARD", 3, ow_hits))

    nc_fired, nc_hits = score_new_claim(files)
    if nc_fired:
        terms.append(("NEW-CLAIM", 2, nc_hits))

    size_pts = score_size(files)
    if size_pts:
        terms.append(("SIZE", size_pts, [f"{sum(f.added + f.removed for f in files)} changed lines"]))

    auth_fired, auth_hits = score_authority(charter_text, diff_text)
    if auth_fired:
        terms.append(("AUTHORITY", 2, auth_hits))

    so_fired = score_suggest_only(charter_text)
    if so_fired:
        terms.append(("SUGGEST-ONLY", -2, [SUGGEST_ONLY_PHRASE]))

    score = sum(pts for _, pts, _ in terms)
    verdict = "OFFICER" if score >= bar else "GATES-ONLY"

    return {
        "verdict": verdict,
        "score": score,
        "bar": bar,
        "terms": [{"name": n, "points": p, "evidence": e} for n, p, e in terms],
        "files_changed": len(files),
        "charter": str(cp),
    }


def format_line(result: dict) -> str:
    reasons = ", ".join(f"{t['name']} {'+' if t['points'] >= 0 else ''}{t['points']}"
                         for t in result["terms"]) or "no terms fired"
    return f"READ TRIAGE: {result['verdict']} · score {result['score']} · {reasons}"


# ==========================================================================
# --selftest -- forced red both ways, on synthetic charters/patches under
# a temp folder. See item 2 of the charter for the five cases.
# ==========================================================================

def _mk(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


HOOK_DIFF = """diff --git a/modules/02-enforcement/hook_model_gate.py b/modules/02-enforcement/hook_model_gate.py
index 1111111..2222222 100644
--- a/modules/02-enforcement/hook_model_gate.py
+++ b/modules/02-enforcement/hook_model_gate.py
@@ -1,2 +1,3 @@
 line one
+a new line in the hook
 line two
"""

DOCS_DIFF = """diff --git a/docs/NOTE.md b/docs/NOTE.md
index 1111111..2222222 100644
--- a/docs/NOTE.md
+++ b/docs/NOTE.md
@@ -1,2 +1,3 @@
 line one
+a docs-only sentence, nothing structural
 line two
"""

ONE_LINE_DIFF = """diff --git a/docs/OTHER.md b/docs/OTHER.md
index 1111111..2222222 100644
--- a/docs/OTHER.md
+++ b/docs/OTHER.md
@@ -1,1 +1,1 @@
-old line
+new line
"""

# NEW_TOOL_DIFF is sized to exactly 300 changed lines on purpose, not by
# accident: case (d)'s bar-1 assertion depends on SIZE's +1 (see the
# comment beside score_size), and after finding 5's floor fix nothing
# under 300 lines scores, so the padding below pins that dependency
# deliberately instead of leaving it incidental.
_NEW_TOOL_PADDING = "".join(
    f"+# padding line {i:03d} to cross the SIZE floor at 300 changed lines\n"
    for i in range(297)
)
NEW_TOOL_DIFF = (
    "diff --git a/tools/new_lint.py b/tools/new_lint.py\n"
    "new file mode 100644\n"
    "index 0000000..3333333\n"
    "--- /dev/null\n"
    "+++ b/tools/new_lint.py\n"
    "@@ -0,0 +1,300 @@\n"
    "+#!/usr/bin/env python3\n"
    "+# a new lint with a --selftest\n"
    + _NEW_TOOL_PADDING +
    "+def main(): pass\n"
)

NEW_FILE_SMALL_DIFF = """diff --git a/tools/tiny_lint.py b/tools/tiny_lint.py
new file mode 100644
index 0000000..4444444
--- /dev/null
+++ b/tools/tiny_lint.py
@@ -0,0 +1,2 @@
+#!/usr/bin/env python3
+def main(): pass
"""

CHARTER_PLAIN = "# PLAIN CHARTER\n\nA charter with no outward step and no authority words.\n"

CHARTER_PUSH = ("# PUSH CHARTER\n\nItem 3: push the branch to the remote and tag "
                "the release.\n")

CHARTER_SUGGESTS = ("# SUGGESTS CHARTER\n\nThe component suggests, never routes; "
                     "it never runs a review and never edits anything.\n")

CHARTER_AUTHORITY = ("# AUTHORITY CHARTER\n\nThis build requires an authorized, "
                      "signed step before it proceeds.\n")

CHARTER_AUTHORITY_STRIPPED = ("# AUTHORITY CHARTER\n\nThis build requires a step "
                               "before it proceeds.\n")


def _invert_judge_surface_case_a(tmp: Path) -> bool:
    """Comment, per item 2: inverting the JUDGE-SURFACE term must red case
    (a). Proven here by scoring case (a)'s own diff with JUDGE_SURFACE_PATTERNS
    emptied out -- the verdict must NOT be OFFICER any more, i.e. the
    inversion is observed to change the answer rather than being a no-op."""
    charter = _mk(tmp, "charter_a.md", CHARTER_PLAIN)
    diff = _mk(tmp, "a.diff", HOOK_DIFF)
    global JUDGE_SURFACE_PATTERNS
    saved = JUDGE_SURFACE_PATTERNS
    JUDGE_SURFACE_PATTERNS = []
    try:
        result = run_score(str(charter), None, None, str(diff), 3)
    finally:
        JUDGE_SURFACE_PATTERNS = saved
    return result["verdict"] != "OFFICER"


def selftest() -> int:
    tmp_root = Path(tempfile.mkdtemp(prefix="read_triage_selftest_"))
    problems = []
    try:
        # (a) a patch touching a hook file reads OFFICER
        charter = _mk(tmp_root, "charter_a.md", CHARTER_PLAIN)
        diff = _mk(tmp_root, "a.diff", HOOK_DIFF)
        r = run_score(str(charter), None, None, str(diff), 3)
        if r["verdict"] != "OFFICER":
            problems.append(f"case (a): expected OFFICER, got {r['verdict']} ({r})")
        term_names = [t["name"] for t in r["terms"]]
        if "JUDGE-SURFACE" not in term_names:
            problems.append("case (a): JUDGE-SURFACE did not fire")

        # inversion comment, proven: emptying JUDGE_SURFACE_PATTERNS must
        # red case (a) -- i.e. the verdict changes away from OFFICER.
        if not _invert_judge_surface_case_a(tmp_root):
            problems.append("case (a) inversion: emptying JUDGE_SURFACE_PATTERNS did not change the verdict -- the term is not load-bearing")

        # (b) a docs-only patch with no outward step reads GATES-ONLY
        charter = _mk(tmp_root, "charter_b.md", CHARTER_PLAIN)
        diff = _mk(tmp_root, "b.diff", DOCS_DIFF)
        r = run_score(str(charter), None, None, str(diff), 3)
        if r["verdict"] != "GATES-ONLY":
            problems.append(f"case (b): expected GATES-ONLY, got {r['verdict']} ({r})")

        # (c) a charter naming a push reads OFFICER on a one-line diff
        charter = _mk(tmp_root, "charter_c.md", CHARTER_PUSH)
        diff = _mk(tmp_root, "c.diff", ONE_LINE_DIFF)
        r = run_score(str(charter), None, None, str(diff), 3)
        if r["verdict"] != "OFFICER":
            problems.append(f"case (c): expected OFFICER, got {r['verdict']} ({r})")
        if "OUTWARD" not in [t["name"] for t in r["terms"]]:
            problems.append("case (c): OUTWARD did not fire")

        # (d) a new tool with a selftest and the suggests-never-routes line
        # reads GATES-ONLY at the default bar and OFFICER at bar 1
        charter = _mk(tmp_root, "charter_d.md", CHARTER_SUGGESTS)
        diff = _mk(tmp_root, "d.diff", NEW_TOOL_DIFF)
        r_default = run_score(str(charter), None, None, str(diff), 3)
        if r_default["verdict"] != "GATES-ONLY":
            problems.append(f"case (d) default bar: expected GATES-ONLY, got {r_default['verdict']} ({r_default})")
        r_bar1 = run_score(str(charter), None, None, str(diff), 1)
        if r_bar1["verdict"] != "OFFICER":
            problems.append(f"case (d) bar 1: expected OFFICER, got {r_bar1['verdict']} ({r_bar1})")
        d_terms = [t["name"] for t in r_default["terms"]]
        if "NEW-CLAIM" not in d_terms or "SUGGEST-ONLY" not in d_terms:
            problems.append(f"case (d): expected NEW-CLAIM and SUGGEST-ONLY to fire, got {d_terms}")

        # (e) an unreadable diff exits 3 (a missing patch file)
        charter = _mk(tmp_root, "charter_e.md", CHARTER_PLAIN)
        missing = tmp_root / "does_not_exist.diff"
        try:
            run_score(str(charter), None, None, str(missing), 3)
            problems.append("case (e): expected UnreadableInput, got a result")
        except UnreadableInput:
            pass

        # (f) a --diff-range value that smuggles a git option into the rev
        # slot is refused before git ever runs, and no file appears at the
        # smuggled path (finding 1: previously "--output=<path>..HEAD"
        # reached git unguarded and wrote a file there).
        charter = _mk(tmp_root, "charter_f.md", CHARTER_PLAIN)
        smuggled_target = tmp_root / "case_f_smuggled_output.txt"
        smuggled_range = f"--output={smuggled_target}..HEAD"
        try:
            run_score(str(charter), smuggled_range, ".", None, 3)
            problems.append("case (f): expected UnreadableInput, got a result")
        except UnreadableInput:
            pass
        if smuggled_target.exists():
            problems.append(f"case (f): a file appeared at the smuggled path: {smuggled_target}")

        # (g) AUTHORITY: a charter naming an authorization and a signed
        # word fires the term, and removing those words moves the verdict
        # at the default bar (finding 2 -- AUTHORITY was, until this case,
        # never exercised by --selftest at all; stubbing score_authority
        # dead left the suite at 5/5 passed).
        charter_auth = _mk(tmp_root, "charter_g.md", CHARTER_AUTHORITY)
        charter_auth_stripped = _mk(tmp_root, "charter_g_stripped.md", CHARTER_AUTHORITY_STRIPPED)
        diff_g = _mk(tmp_root, "g.diff", NEW_FILE_SMALL_DIFF)
        r_with = run_score(str(charter_auth), None, None, str(diff_g), 3)
        if "AUTHORITY" not in [t["name"] for t in r_with["terms"]]:
            problems.append(f"case (g): AUTHORITY did not fire ({r_with})")
        if r_with["verdict"] != "OFFICER":
            problems.append(f"case (g) with authority words: expected OFFICER, got {r_with['verdict']} ({r_with})")
        r_without = run_score(str(charter_auth_stripped), None, None, str(diff_g), 3)
        if r_without["verdict"] != "GATES-ONLY":
            problems.append(f"case (g) without authority words: expected GATES-ONLY, got {r_without['verdict']} ({r_without})")
        if r_with["verdict"] == r_without["verdict"]:
            problems.append("case (g): removing the authorization/signed words did not move the verdict")

        # (h) every JUDGE_PATHS entry the box's own kit.config lists today
        # is covered by some pattern in JUDGE_SURFACE_PATTERNS (finding 6:
        # the pattern list is a hand-kept copy, not a live read, so a drift
        # between the two would otherwise be silent).
        cfg = read_kit_config(Path(__file__).resolve().parent)
        configured = [p.strip() for p in cfg.get("JUDGE_PATHS", "").split(",") if p.strip()]
        if not configured:
            problems.append("case (h): kit.config's JUDGE_PATHS read empty -- nothing to check")
        uncovered = []
        for path in configured:
            low = path.replace("\\", "/").lower()
            if not any(pattern.lower() in low for _, pattern, _ in JUDGE_SURFACE_PATTERNS):
                uncovered.append(path)
        if uncovered:
            problems.append(f"case (h): JUDGE_PATHS entries not covered by any pattern: {uncovered}")
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    if problems:
        print("READ TRIAGE SELFTEST: FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("READ TRIAGE SELFTEST: 8/8 cases passed (a-h), inversion proven on (a)")
    return 0


# ==========================================================================
# CLI
# ==========================================================================

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--charter")
    ap.add_argument("--diff-range")
    ap.add_argument("--repo")
    ap.add_argument("--patch")
    ap.add_argument("--bar", type=int)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.charter:
        print("READ TRIAGE: unreadable · --charter is required", file=sys.stderr)
        return 3

    try:
        result = run_score(args.charter, args.diff_range, args.repo, args.patch, args.bar)
    except UnreadableInput as e:
        print(f"READ TRIAGE: unreadable · {e}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_line(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
