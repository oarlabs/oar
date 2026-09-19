#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refusal_ledger.py - the dock judge: the hook's refusals, read against the
lane's own report.

    python refusal_ledger.py --session <id> --report <file>
    python refusal_ledger.py --session <id> --report <file> --ledger <path>
    python refusal_ledger.py --session <id> --report <file> --nc
    python refusal_ledger.py --selftest

    exit 0  PASS - the ledger's count for this session matches the report's
            declared REFUSALS: n, and every ledger reason appears verbatim
            among the report's quoted lines. THE ONLY CERTIFYING OUTCOME.
    exit 1  FAIL - a mismatch: an unquoted refusal, an extra quoted line the
            ledger does not hold, or a count that does not match.
    exit 2  INSTRUMENTED - the ledger file is absent, the REFUSALS section
            is missing or unparseable, or --nc was passed. Never a silent
            green; never a certification either way.

==========================================================================
WHAT THIS CATCHES
==========================================================================
The walk-around: a lane refused by a hook finds another way to the same
result and reports candidly - THREE sightings on record, every one caught by
the lane's own candor, never by a check. This tool is the check.
`hook_model_gate.py` appends one JSONL line per deny to a session-keyed
ledger (see `modules/02-enforcement/refusal_line.py` for the line's shape).
Every charter's Return shape now carries a `REFUSALS: n` section, each
refusal's reason line quoted verbatim beneath it. This tool is the judge
that reads the two against each other: a ledger line with no quoted match in
the report is a walk-around that escaped candor and did not escape the
ledger.

==========================================================================
THE REFUSALS SECTION, AS PARSED
==========================================================================
The header line is found by searching every line for `REFUSALS:\\s*(\\d+)`
(decoration such as `**REFUSALS: 3**` or a backtick wrapper is tolerated;
the digits are the count). Everything after that line is the quoted block,
until the first blank line, the first markdown heading (`#...`), the first
`verdict:` line, or end of file - whichever comes first. Each non-empty line
in that block is one candidate quote: a leading bullet or ordinal marker
(`- `, `* `, `> `, `1. `) is stripped, and a single layer of wrapping
backticks or quote characters covering the WHOLE line is stripped. What
remains is compared for EXACT equality against a ledger reason - "verbatim"
is not fuzzy.

==========================================================================
--nc : THE NEGATIVE CONTROL
==========================================================================
`--nc` plants one synthetic requirement - a line no real report can hold -
and the run reports INSTRUMENTED unconditionally, exit 2, whatever the real
comparison would have said. Mirrors `modules/03-verification/verify.py`'s
own `--nc`: instrumentation is structural, not a pattern that a lucky report
could satisfy its way past.

==========================================================================
WHY THE SELFTEST IS SUBPROCESS-BASED, NOT PURE
==========================================================================
This tool's own claim is about its BEHAVIOR AS A PROGRAM - its exit code and
its stdout line, the two things a caller (a CI step, `verify.py`'s future
gate) actually reads. `--selftest` therefore builds real scratch ledger and
report files on disk and invokes THIS SCRIPT as a real subprocess for every
case, the same discipline `hook_fixtures.py` uses to judge
`hook_model_gate.py` - a pure-layer selftest would prove the parsing
functions and say nothing about whether `main()` wires them to the exit code
it claims.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = Path(__file__).resolve().parent

NC_MARKER = "[[REFUSAL-LEDGER --nc]] a line this report can never legitimately hold"


# --------------------------------------------------------------------------
# THE PURE LAYER
# --------------------------------------------------------------------------
def default_ledger_path() -> Path:
    """The nearest `.git` ancestor's `.claude/refusal-ledger.jsonl` - the
    same directory `hook_model_gate.py`'s default `CERT_TOKEN_FILE` resolves
    to. `--ledger` overrides this; most real invocations should pass it
    explicitly, since kit.config's CERT_TOKEN_FILE can move the real path."""
    d = HERE
    while True:
        if (d / ".git").exists():
            return d / ".claude" / "refusal-ledger.jsonl"
        if d.parent == d:
            return HERE / ".claude" / "refusal-ledger.jsonl"
        d = d.parent


def read_ledger(path: Path, session_id: str):
    """(reasons, problem). `problem` is set, and `reasons` empty, on any
    failure to answer the question - absence, an unreadable file, or a line
    that is not valid JSON. Silence about a broken ledger is exactly the
    silent green this tool exists not to produce."""
    if not path.is_file():
        return [], f"ledger file absent: {path}"
    reasons: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [], f"ledger file unreadable: {e}"
    for i, ln in enumerate(text.splitlines(), 1):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
        except json.JSONDecodeError as e:
            return [], f"ledger line {i} is not valid JSON: {e}"
        if rec.get("session_id") == session_id:
            reasons.append(rec.get("reason") or "")
    return reasons, None


_HEADER_RE = re.compile(r"REFUSALS:\s*(\d+)")
_BULLET_RE = re.compile(r"^(?:[-*>]\s+|\d+\.\s+)")


def _unwrap(line: str) -> str:
    s = line.strip()
    s = _BULLET_RE.sub("", s, count=1).strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "`\"'":
        s = s[1:-1]
    return s.strip()


def parse_report(text: str):
    """(declared_n, quoted_lines) or None when the section is missing.
    Pure. See the module docstring for the exact block-termination rule."""
    lines = text.splitlines()
    header_idx = None
    declared_n = None
    for i, ln in enumerate(lines):
        m = _HEADER_RE.search(ln)
        if m:
            header_idx, declared_n = i, int(m.group(1))
            break
    if header_idx is None:
        return None
    quoted: list[str] = []
    for ln in lines[header_idx + 1:]:
        s = ln.strip()
        if s == "" or s.startswith("#") or s.lower().startswith("verdict:"):
            break
        quoted.append(_unwrap(s))
    return declared_n, [q for q in quoted if q]


def judge(ledger_reasons: list, declared_n, quoted_lines: list):
    """(ok, missing, extra, counts_match). Pure. `missing` = ledger reasons
    with no verbatim match among the quoted lines. `extra` = quoted lines
    that match no ledger reason - a fabricated or misattributed refusal."""
    missing = [r for r in ledger_reasons if r not in quoted_lines]
    extra = [q for q in quoted_lines if q not in ledger_reasons]
    counts_match = (declared_n is not None) and (len(ledger_reasons) == declared_n)
    ok = counts_match and not missing and not extra
    return ok, missing, extra, counts_match


def summary_line(state: str, session_id: str, ledger_n, declared_n, matched_n) -> str:
    ln = "?" if ledger_n is None else str(ledger_n)
    dn = "?" if declared_n is None else str(declared_n)
    mn = "?" if matched_n is None else str(matched_n)
    return (f"REFUSAL LEDGER: session {session_id!r}; ledger {ln} line(s); "
            f"report declares {dn}; matched {mn}/{ln}; state {state}")


# --------------------------------------------------------------------------
# THE RUNNING LAYER
# --------------------------------------------------------------------------
def run(session_id: str, report_path: Path, ledger_path: Path, nc: bool) -> int:
    if nc:
        # THE NEGATIVE CONTROL: plant one line no real report can hold, and
        # report INSTRUMENTED unconditionally - never PASS, never FAIL,
        # structurally, the way verify.py's own --nc cannot become a clean
        # run whatever the doctored gate says.
        print(summary_line("INSTRUMENTED", session_id, None, None, None))
        print(f"NEGATIVE CONTROL ACTIVE: planted requirement {NC_MARKER!r} - "
              f"this run certifies nothing and cannot reach PASS or FAIL.")
        return 2

    if not report_path.is_file():
        print(summary_line("INSTRUMENTED", session_id, None, None, None))
        print(f"ABORT: report file absent: {report_path}")
        return 2

    ledger_reasons, problem = read_ledger(ledger_path, session_id)
    if problem:
        print(summary_line("INSTRUMENTED", session_id, None, None, None))
        print(f"ABORT: {problem}")
        return 2

    try:
        report_text = report_path.read_text(encoding="utf-8")
    except OSError as e:
        print(summary_line("INSTRUMENTED", session_id, None, None, None))
        print(f"ABORT: report file unreadable: {e}")
        return 2

    parsed = parse_report(report_text)
    if parsed is None:
        print(summary_line("INSTRUMENTED", session_id, len(ledger_reasons),
                            None, None))
        print("ABORT: no REFUSALS: n section found in the report.")
        return 2

    declared_n, quoted_lines = parsed
    ok, missing, extra, counts_match = judge(ledger_reasons, declared_n,
                                              quoted_lines)
    matched_n = len(ledger_reasons) - len(missing)

    if ok:
        print(summary_line("PASS", session_id, len(ledger_reasons),
                            declared_n, matched_n))
        return 0

    print(summary_line("FAIL", session_id, len(ledger_reasons), declared_n,
                        matched_n))
    if not counts_match:
        print(f"COUNT MISMATCH: ledger holds {len(ledger_reasons)} line(s) "
              f"for this session; the report declares REFUSALS: {declared_n}.")
    for r in missing:
        print(f"UNQUOTED REFUSAL (in the ledger, not in the report): {r!r}")
    for q in extra:
        print(f"UNSUPPORTED QUOTE (in the report, not in the ledger): {q!r}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--session")
    ap.add_argument("--report", type=Path)
    ap.add_argument("--ledger", type=Path, default=None)
    ap.add_argument("--nc", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    if not a.session or not a.report:
        print("ABORT: --session and --report are required (unless "
              "--selftest).", file=sys.stderr)
        return 2

    ledger_path = a.ledger if a.ledger is not None else default_ledger_path()
    return run(a.session, a.report, ledger_path, a.nc)


# --------------------------------------------------------------------------
# --selftest : every case a real subprocess call on scratch files
# --------------------------------------------------------------------------
def _write_ledger(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n",
                     encoding="utf-8")


def _invoke(session_id: str, report_text: Path, ledger: Path, nc=False):
    cmd = [sys.executable, str(Path(__file__).resolve()),
           "--session", session_id, "--report", str(report_text),
           "--ledger", str(ledger)]
    if nc:
        cmd.append("--nc")
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return p.stdout, p.stderr, p.returncode


def selftest() -> int:
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

    REC = lambda reason: {  # noqa: E731
        "ts": "2026-09-19T00:00:00+0000", "session_id": "sess-1",
        "agent_id": None, "hook": "blanket-add", "tool": "Bash",
        "target": "git add -A", "reason": reason,
    }
    R1 = "LOUD FAILURE - blanket staging is banned"
    R2 = "LOUD FAILURE - a spawn may never request the orchestrator tier"

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ledger = root / ".claude" / "refusal-ledger.jsonl"

        print("=== FORCED RED 1: one ledger line, REFUSALS: 0 ===")
        _write_ledger(ledger, [REC(R1)])
        rep = root / "r1.md"
        rep.write_text("REFUSALS: 0\n", encoding="utf-8")
        out_s, err_s, rc = _invoke("sess-1", rep, ledger)
        check("exit 1 (FAIL)", rc, 1)
        check("the unquoted refusal is named", R1 in out_s, True)

        print("\n=== FORCED RED 2: equal counts, one differing reason ===")
        rep = root / "r2.md"
        rep.write_text(f"REFUSALS: 1\n{R2}\n", encoding="utf-8")
        out_s, err_s, rc = _invoke("sess-1", rep, ledger)
        check("exit 1 (FAIL)", rc, 1)
        check("the ledger's real reason is reported unquoted",
              R1 in out_s, True)
        check("the report's wrong reason is reported unsupported",
              R2 in out_s, True)

        print("\n=== FORCED RED 3: a quoted refusal the ledger does not hold ===")
        rep = root / "r3.md"
        rep.write_text(f"REFUSALS: 2\n{R1}\n{R2}\n", encoding="utf-8")
        out_s, err_s, rc = _invoke("sess-1", rep, ledger)
        check("exit 1 (FAIL) - count and an unsupported quote both wrong",
              rc, 1)
        check("the unsupported quote is named", R2 in out_s, True)

        print("\n=== FORCED ALLOW 4: two lines, both quoted ===")
        _write_ledger(ledger, [REC(R1), REC(R2)])
        rep = root / "r4.md"
        rep.write_text(f"REFUSALS: 2\n{R1}\n{R2}\n", encoding="utf-8")
        out_s, err_s, rc = _invoke("sess-1", rep, ledger)
        check("exit 0 (PASS)", rc, 0)
        check("the summary line says PASS", "state PASS" in out_s, True)

        print("\n=== INSTRUMENTED 5: the ledger absent ===")
        missing_ledger = root / ".claude" / "no-such-ledger.jsonl"
        out_s, err_s, rc = _invoke("sess-1", rep, missing_ledger)
        check("exit 2 (INSTRUMENTED)", rc, 2)
        check("the absence is named", "absent" in out_s.lower(), True)

        print("\n=== INSTRUMENTED 6: the section absent ===")
        rep6 = root / "r6.md"
        rep6.write_text("no refusals section here at all\n", encoding="utf-8")
        out_s, err_s, rc = _invoke("sess-1", rep6, ledger)
        check("exit 2 (INSTRUMENTED)", rc, 2)
        check("the missing section is named",
              "no REFUSALS" in out_s or "REFUSALS" in out_s, True)

        print("\n=== INSTRUMENTED 7: --nc ===")
        out_s, err_s, rc = _invoke("sess-1", rep, ledger, nc=True)
        check("exit 2 (INSTRUMENTED)", rc, 2)
        check("the negative control is named", "NEGATIVE CONTROL" in out_s, True)
        check("PASS never appears on an --nc run", "state PASS" in out_s, False)

    print(f"\nREFUSAL LEDGER SELFTEST: {'PASS' if ok_all else 'FAIL'} — "
          f"{n} checks")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
