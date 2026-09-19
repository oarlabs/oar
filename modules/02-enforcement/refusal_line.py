#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refusal_line.py - the refusal ledger's line shape, authored once.

WHY THIS FILE EXISTS, AND WHY ITS CODE IS ALSO COPIED BY VALUE INTO THE HOOK
==============================================================================
`hook_model_gate.py` ships under a zero-import discipline: its own docstring
says "THIS FILE NEEDS NO EDITING", and module 02's README tells an adopter to
copy that ONE file into their tree (`cp .../hook_model_gate.py tools/`) and
run it standalone, reading nothing but `kit.config`. A hook that imports a
sibling module breaks the moment the sibling is not copied alongside it, and
nothing in the adopt instructions says to copy two files.

So the functions below are DUPLICATED, verbatim, inline at
`hook_model_gate.py`'s four deny points - COPIED BY VALUE, not imported. This
file is where that duplicated code is authored once, so `refusal_ledger.py`
(the dock judge) and this module's own `--selftest` can exercise the exact
shape without spawning a hook subprocess, and so a reader auditing the
duplication has a diff target. Whenever the copy inside `hook_model_gate.py`
changes, this file changes in the same commit, and the reverse - both carry a
`# COPIED BY VALUE from refusal_line.py - keep identical` marker comment at
the seam.

THE LINE
========
One JSON object per line (JSONL), appended, never rewritten:
    ts          ISO-8601, with a numeric UTC offset
    session_id  from the hook's stdin payload; "" when absent
    agent_id    from the hook's stdin payload; null when absent
    hook        which deny point fired (e.g. "workflow-tier", "agent-tier",
                "forbidden-tier", "blanket-add")
    tool        the tool_name the hook was judging
    target      the path, or the command's first 120 characters
    reason      the loud `permissionDecisionReason` line, verbatim

A FAILED WRITE NEVER CHANGES THE DECISION. `append_refusal()` swallows every
`OSError`, returns `False`, and the caller prints one warning line to stderr.
The hook's own doctrine (FAIL-OPEN, DELIBERATELY, WITH ONE EXCEPTION) does not
change for the ledger: the ledger is a record ABOUT the deny, not a condition
OF it. A hook that stopped denying because a log directory went unwritable
would be strictly worse than one that logs nothing and denies anyway.

WHY THE SELFTEST SIMULATES "READ-ONLY" BY OCCUPYING THE PATH WITH A FILE,
NOT BY CHMOD
==============================================================================
Measured on this box (Windows): `os.chmod(dir, stat.S_IREAD)` does NOT block a
new file being created inside that directory - Windows' read-only attribute on
a directory is cosmetic for Explorer and is not enforced by `open()`. A
selftest that chmods a directory and then asserts the write failed would pass
on a POSIX box and silently pass-for-the-wrong-reason on this one (the write
would succeed, `append_refusal` would return True, and the assertion "it
returned False" would simply not run the branch it claims to). The portable
stand-in used below - pointing the ledger at a path whose PARENT segment is
already occupied by an ordinary file - forces `Path.mkdir()` to raise
`FileExistsError` (an `OSError` subclass) on every platform this kit targets,
which is the same exception family a real permission denial raises. That is
the scenario actually asserted: "the ledger location cannot be written",
independent of which OS-specific mechanism produced it.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def iso_now() -> str:
    """ISO-8601 with a numeric UTC offset. The only non-pure call in this
    file - `build_refusal_record`'s `now` parameter exists so a test never
    has to call this."""
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def build_refusal_record(session_id, agent_id, hook, tool, target, reason,
                          now: str | None = None) -> dict:
    """Pure. Field order is the documented shape, not incidental -
    `json.dumps` on a plain dict preserves insertion order, and the dock
    judge and a human `cat`-ing the ledger both read left to right."""
    return {
        "ts": now if now is not None else iso_now(),
        "session_id": session_id or "",
        "agent_id": agent_id if agent_id else None,
        "hook": hook or "",
        "tool": tool or "",
        "target": (target or "")[:120],
        "reason": reason or "",
    }


def ledger_path(project_root: str, token_file: str) -> Path:
    """Beside the cert-green token file, same directory. Mirrors the
    repo-relative-unless-absolute rule `verify.py`'s `cert_token_path()`
    already uses for that same token, so the two files that share a
    directory are found by the same rule."""
    tok = Path(token_file or ".claude/cert-green.json")
    if not tok.is_absolute():
        tok = Path(project_root or ".") / tok
    return tok.parent / "refusal-ledger.jsonl"


def append_refusal(path: Path, record: dict) -> bool:
    """True on a successful append, False on ANY failure - a directory that
    does not exist and cannot be made, one that is unwritable, a full disk, a
    path segment that is actually a file. The caller's deny decision does not
    read this return value; only the warning line does."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------
# --selftest
# --------------------------------------------------------------------------
def _selftest() -> int:
    import tempfile

    ok_all = True
    n = 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    print("=== A. the record shape, pure ===")
    rec = build_refusal_record("sess-1", "agent-7", "blanket-add", "Bash",
                                "x" * 200, "LOUD FAILURE - blanket staging",
                                now="2026-09-19T12:00:00+0000")
    check("every documented field is present",
          sorted(rec.keys()),
          sorted(["ts", "session_id", "agent_id", "hook", "tool", "target",
                  "reason"]))
    check("target is truncated to 120 characters", len(rec["target"]), 120)
    check("agent_id absent reads as null, not empty string",
          build_refusal_record("s", None, "h", "t", "x", "r",
                                now="x")["agent_id"], None)
    check("session_id absent reads as empty string, not null",
          build_refusal_record(None, None, "h", "t", "x", "r",
                                now="x")["session_id"], "")
    check("the record round-trips through JSON with fields intact",
          json.loads(json.dumps(rec)), rec)

    print("\n=== B. a deny writes one line with every field ===")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "sub" / "refusal-ledger.jsonl"
        wrote = append_refusal(p, rec)
        check("append_refusal reports success", wrote, True)
        lines = p.read_text(encoding="utf-8").splitlines()
        check("exactly one line was written", len(lines), 1)
        parsed = json.loads(lines[0]) if lines else {}
        check("the written line carries every field",
              sorted(parsed.keys()) if lines else [],
              sorted(rec.keys()))
        check("a second append adds a second line, never rewrites the first",
              len(Path(p).read_text(encoding="utf-8").splitlines())
              if append_refusal(p, rec) else -1, 2)

    print("\n=== C. the ledger location cannot be written - the deny still "
          "stands, this call reports failure, and the caller's warning is "
          "the only visible effect ===")
    with tempfile.TemporaryDirectory() as td:
        # Occupy the WOULD-BE DIRECTORY with an ordinary file, portably (see
        # the module docstring for why this replaces a chmod-based test).
        blocked_dir = Path(td) / "blocked"
        blocked_dir.write_text("occupying this name so mkdir() fails",
                                encoding="utf-8")
        p = blocked_dir / "refusal-ledger.jsonl"
        wrote = append_refusal(p, rec)
        check("append_refusal reports failure, and raises nothing "
              "(the exception was caught inside the function, not by this "
              "test)", wrote, False)
        check("nothing was created at the blocked path", p.exists(), False)

    print(f"\nREFUSAL LINE SELFTEST: {'PASS' if ok_all else 'FAIL'} — "
          f"{n} checks")
    return 0 if ok_all else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print("refusal_line.py defines the ledger line's shape; it is not a "
          "standalone tool. Run with --selftest. hook_model_gate.py copies "
          "these functions by value at its deny points; "
          "modules/03-verification/refusal_ledger.py parses the JSONL lines "
          "this file's shape produces directly, with no import of this "
          "module, to avoid a cross-module-directory import.",
          file=sys.stderr)
    raise SystemExit(2)
