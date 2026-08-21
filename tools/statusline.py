#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/statusline.py - the status board, cross-platform.

    <harness pipes session JSON on stdin>  ->  one ANSI line on stdout
    python tools/statusline.py --selftest  # render all four banner states
    python tools/statusline.py --demo      # render a sample board

This is the portable implementation of the contract in
`modules/05-statusboard/CONTRACT.md`. `statusline.ps1.template` is the
Windows-optimised variant of the same contract; either satisfies it, and
module 05's README gives the wiring JSON for both. Pick one. Running both
means two boards disagreeing about the same session.

WHY A PYTHON ONE EXISTS
=======================
The PowerShell board assumes pwsh. Everything else executable in this kit is
stock Python and runs anywhere, so the board was the single component that
quietly made the kit Windows-only. A doctrine that claims to be host-agnostic
cannot have one of its six executables refuse to start on Linux.

THE RULE THIS FILE IS BUILT ON
==============================
**Every segment is guarded, with exactly one deliberate exception.** A missing
field, an unreadable file, an absent git repo: the segment disappears and the
board still renders. A status line that throws is a status line that gets
removed within the day, and then you have no board at all.

The exception is the sidequest banner. A corrupt or unreadable flag file
renders a LOUD "state file unreadable" banner, never silence - because silence
there asserts "you are back on the main line", which would be a lie in exactly
the situation where you most need the truth. The same reasoning applies to a
`PROJECT_ROOT` this file cannot resolve: it says so on the board instead of
dropping the banner and letting an open side quest go invisible.

CONFIG
======
Read from kit.config using the same four-step search every tool in this kit
uses ($KIT_CONFIG, ./kit.config, <this dir>/kit.config, nearest walking up),
overlaid with kit.config.local. Every key has an in-module default, so this
runs with no config at all.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---- IN-MODULE DEFAULTS. The board must render before anything is set up. --
DEFAULTS = {
    "SIDEQUEST_FLAG": ".claude/sidequest.json",
    "SIDEQUEST_STALE_DAYS": "3",
    "STATUS_BAR_CELLS": "16",
    "STATUS_CLEAR_MARK_PCT": "75",
    "STATUS_BOARD_LINE_FILE": "NONE",
    "AGENT_TRANSCRIPT_DIR": "NONE",
    "PROJECT_ROOT": "",
}

ESC = "\033"


def seg(style: str, text: str) -> str:
    return f"{ESC}[{style}m{text}{ESC}[0m"


# --------------------------------------------------------------------------
# config
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


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    env = os.environ.get("KIT_CONFIG")
    cands = ([Path(env)] if env else []) + [
        Path.cwd() / "kit.config", HERE / "kit.config",
    ] + [d / "kit.config" for d in HERE.parents]
    for c in cands:
        try:
            if not c.is_file():
                continue
        except OSError:
            continue
        _read_pairs(c, cfg)
        _read_pairs(c.with_name("kit.config.local"), cfg)
        break
    return cfg


def cfg_get(cfg: dict, key: str):
    """The shared unset rule, applied to the board's own config reads."""
    v = cfg.get(key)
    return None if v is None or is_placeholder(v) else v.strip()


def as_int(cfg: dict, key: str) -> int:
    try:
        return int(str(cfg.get(key, DEFAULTS.get(key, "0"))).strip())
    except (TypeError, ValueError):
        return int(DEFAULTS.get(key, "0"))


# --------------------------------------------------------------------------
# THE PURE LAYER - everything --selftest exercises
# --------------------------------------------------------------------------
def resolve_root(cfg_root: str, start: Path, has_git) -> tuple:
    """(root, problem). `problem` is a string when the board must SAY something.

    A relative or empty PROJECT_ROOT resolves against wherever the harness
    happened to launch the board, which is not necessarily your repo - and the
    failure mode is the sidequest banner silently vanishing on a foreign cwd.
    That is precisely the silent degradation this module's own contract
    forbids, so an unresolvable root becomes a visible segment."""
    if cfg_root and not is_placeholder(cfg_root) and cfg_root != ".":
        p = Path(cfg_root)
        if p.is_absolute():
            return p, ""
    for d in [start, *start.parents]:
        if has_git(d):
            return d, ""
    if cfg_root in ("", "NONE", "."):
        return start, ("PROJECT_ROOT is not absolute and no .git ancestor was "
                       "found - repo-relative segments may be wrong")
    return Path(cfg_root), ("PROJECT_ROOT is relative - repo-relative segments "
                            "may be wrong")


def banner(raw, today: date, stale_days: int):
    """(text, style) for the sidequest banner, or None for 'no banner'.

    `raw` is the flag file's contents, or None when the file is absent.
    Absence is the main line; everything else must be visible."""
    if raw is None:
        return None
    loud = "97;101;1"        # white on red
    amber = "30;103;1"       # black on amber
    try:
        sq = json.loads(raw)
    except Exception:
        return (" ⚔  SIDEQUEST (state file unreadable) ", loud)
    if not isinstance(sq, dict) or not sq.get("slug"):
        return (" ⚔  SIDEQUEST (state file unreadable) ", loud)

    txt = f"⚔  SIDEQUEST {sq['slug']}"
    stale = False
    started = sq.get("started")
    if started:
        try:
            d0 = datetime.strptime(str(started), "%Y-%m-%d").date()
            days = 1 + (today - d0).days
            txt += f" · day {days}"
            stale = days > stale_days
        except (TypeError, ValueError):
            txt += " · day ?"
    resume = sq.get("mainline_resume")
    if resume:
        r = str(resume)
        if len(r) > 44:
            r = r[:43] + "…"
        txt += f" · main: {r}"
    if stale:
        txt = txt.replace(" · main:", " · STALE · main:", 1)
        if "STALE" not in txt:
            txt += " · STALE"
    return (f" {txt} ", amber if stale else loud)


def context_bar(pct, tokens, cells: int, mark_pct: int) -> str:
    """The bar is coloured by POSITION, not by fill, so it shows the terrain
    AHEAD rather than only where you are."""
    pct = max(0, min(100, int(round(pct))))
    mark = int(round(cells * mark_pct / 100.0))
    fill = int(round(pct / 100.0 * cells))
    out = ""
    for i in range(cells):
        if i == mark:
            out += seg("97;1", "┃")
        zone = "92" if i < cells // 2 else ("93" if i < mark else "91")
        out += seg(zone, "█") if i < fill else seg("90", "░")
    col = "91;1" if pct >= mark_pct else ("93" if pct >= 50 else "92")
    tok = ""
    if tokens:
        tok = (f" {tokens/1_000_000:.1f}M" if tokens >= 1_000_000
               else f" {tokens/1000:.0f}k" if tokens >= 1000 else f" {tokens}")
    out += seg(col, f" {pct}%{tok}")
    if pct >= mark_pct:
        out += seg("91;1", " ✂ clear")
    return out


def duration(ms) -> str:
    try:
        total = int(ms) // 1000
    except (TypeError, ValueError):
        return ""
    h, m = total // 3600, (total % 3600) // 60
    return f"{h}h{m:02d}m" if h else f"{m}m"


# --------------------------------------------------------------------------
# the impure edges, each individually guarded
# --------------------------------------------------------------------------
def read_flag(path: Path):
    try:
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""          # exists but unreadable -> the LOUD branch


def git_segment(root: Path) -> str:
    def g(*args):
        try:
            p = subprocess.run(["git", "-C", str(root), *args],
                               capture_output=True, text=True, timeout=5)
            return p.stdout.strip() if p.returncode == 0 else ""
        except Exception:
            return ""
    sha = g("rev-parse", "--short", "HEAD")
    if not sha:
        return ""
    branch = g("rev-parse", "--abbrev-ref", "HEAD") or "?"
    dirty = seg("93", "±") if g("status", "--porcelain", "-uno") \
        else seg("92", "✓")
    return seg("95", f"{branch}@{sha}") + dirty


def live_agents(cfg: dict, session_id: str) -> list:
    """Harness-specific and therefore fully optional. AGENT_TRANSCRIPT_DIR is
    NONE by default; the segment simply does not appear."""
    root = cfg_get(cfg, "AGENT_TRANSCRIPT_DIR")
    if not session_id or not root:
        return []
    try:
        d = Path(root) / session_id / "subagents"
        if not d.is_dir():
            return []
        import time
        now = time.time()
        out = []
        for f in sorted(d.rglob("agent-*.jsonl")):
            try:
                age = now - f.stat().st_mtime
            except OSError:
                continue
            if age > 45 * 60:
                continue
            meta = f.with_name(f.name.replace(".jsonl", ".meta.json"))
            tier, role = "?", "agent"
            try:
                m = json.loads(meta.read_text(encoding="utf-8"))
                tier = m.get("model") or m.get("agentType") or "?"
                role = m.get("description") or "agent"
            except Exception:
                pass
            if len(role) > 46:
                role = role[:45] + "…"
            out.append((tier, role, int(age), f.stat().st_size // 1024))
        return out[:8]
    except Exception:
        return []


def _d(payload: dict, key: str) -> dict:
    """A sub-object, or an empty one. Harness payloads are somebody else's
    JSON: a field that is a string today can be a dict tomorrow and null the
    day after, and none of those may take the board down."""
    v = payload.get(key)
    return v if isinstance(v, dict) else {}


def render(payload: dict, cfg: dict, today: date) -> str:
    parts, extra = [], []
    root, root_problem = resolve_root(
        cfg.get("PROJECT_ROOT", ""), Path.cwd().resolve(),
        lambda d: (d / ".git").exists())

    raw = read_flag(root / cfg.get("SIDEQUEST_FLAG", DEFAULTS["SIDEQUEST_FLAG"]))
    b = banner(raw, today, as_int(cfg, "SIDEQUEST_STALE_DAYS"))
    if b:
        parts.append(seg(b[1], b[0]))
    if root_problem:
        # NOT silent. An unresolvable root can hide an open side quest, and a
        # missing banner reads as "you are on the main line".
        parts.append(seg("30;103;1", f" ⚠ {root_problem} "))

    parts.append(seg("97;1", "◉  main"))

    agents = live_agents(cfg, str(payload.get("session_id") or ""))
    if agents:
        parts.append(seg("96;1", f"⚒ {len(agents)} flying"))
        for tier, role, idle, kb in agents:
            extra.append(seg("96", "  ⚒ ") + seg("95;1", str(tier))
                         + " " + seg("96;1", role)
                         + seg("90", f" · ✎ {idle}s · {kb}KB"))

    model = _d(payload, "model").get("display_name")
    if model:
        parts.append(seg("96;1", f"⚡ {model}"))

    cw = _d(payload, "context_window")
    pct = cw.get("used_percentage")
    if pct is None and cw.get("context_window_size"):
        try:
            pct = 100.0 * cw["total_input_tokens"] / cw["context_window_size"]
        except (TypeError, ZeroDivisionError, KeyError):
            pct = None
    if pct is not None:
        try:
            parts.append(context_bar(pct, cw.get("total_input_tokens") or 0,
                                     as_int(cfg, "STATUS_BAR_CELLS"),
                                     as_int(cfg, "STATUS_CLEAR_MARK_PCT")))
        except (TypeError, ValueError):
            pct = None
    if pct is None:
        # THE BOARD'S OWN ANTI-SILENCE RULE, applied to itself. A missing or
        # differently-named context key used to drop the bar entirely, and an
        # absent bar reads as "plenty of room left" - the single most dangerous
        # thing this board could imply. A dim placeholder says "I do not know",
        # which is a different sentence and the true one.
        parts.append(seg("90", "ctx ?"))

    cost = _d(payload, "cost")
    try:
        if cost.get("total_cost_usd"):
            parts.append(seg("90", f"${float(cost['total_cost_usd']):.2f}"))
    except (TypeError, ValueError):
        pass
    d = duration(cost.get("total_duration_ms"))
    if d:
        parts.append(seg("90", f"⏱  {d}"))
    try:
        la = int(cost.get("total_lines_added") or 0)
        lr = int(cost.get("total_lines_removed") or 0)
    except (TypeError, ValueError):
        la = lr = 0
    if la or lr:
        parts.append(seg("92", f"+{la}") + seg("90", "/") + seg("91", f"-{lr}"))

    gs = git_segment(root)
    if gs:
        parts.append(gs)

    board = cfg_get(cfg, "STATUS_BOARD_LINE_FILE")
    if board:
        try:
            first = Path(board).read_text(encoding="utf-8").splitlines()
            if first and first[0].strip():
                parts.append(seg("96", first[0].strip()))
        except Exception:
            pass

    return "\n".join([seg("90", " | ").join(parts), *extra])


# --------------------------------------------------------------------------
def selftest() -> int:
    ok, n = True, 0

    def check(label, got, want):
        nonlocal ok, n
        n += 1
        good = got == want
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    today = date(2026, 3, 10)
    print("=== the four banner states (CONTRACT.md) ===")

    print("  1. ABSENT (the main line):")
    check("no flag file -> NO banner at all", banner(None, today, 3), None)

    fresh = json.dumps({"slug": "kit-extraction", "started": "2026-03-10",
                        "ask": "x", "doc": "d",
                        "mainline_resume": "resume the round-11 fix pass"})
    b = banner(fresh, today, 3)
    print("  2. FRESH:", seg(b[1], b[0]))
    check("fresh banner is on the LOUD red field", b[1], "97;101;1")
    check("the fork day is day 1", "day 1" in b[0], True)
    check("fresh is not marked STALE", "STALE" in b[0], False)

    old = json.dumps({"slug": "kit-extraction", "started": "2026-03-04",
                      "mainline_resume": "resume the round-11 fix pass"})
    b = banner(old, today, 3)
    print("  3. STALE:", seg(b[1], b[0]))
    check("past the threshold the field turns AMBER", b[1], "30;103;1")
    check("...and it says STALE out loud", "STALE" in b[0], True)
    check("...and the day counter is right", "day 7" in b[0], True)
    check("the boundary day is not yet stale",
          "STALE" in banner(json.dumps(
              {"slug": "s", "started": "2026-03-08"}, ), today, 3)[0], False)

    b = banner("this is not json", today, 3)
    print("  4. CORRUPT:", seg(b[1], b[0]))
    check("a corrupt flag is LOUD, never silent", b is None, False)
    check("...and says the state file is unreadable",
          "unreadable" in b[0], True)
    check("a flag with no slug is also unreadable",
          "unreadable" in banner('{"started":"2026-03-10"}', today, 3)[0], True)

    print("\n=== truncation and the day counter ===")
    longr = json.dumps({"slug": "s", "started": "2026-03-10",
                        "mainline_resume": "x" * 100})
    check("a long resume line is truncated with an ellipsis",
          "…" in banner(longr, today, 3)[0], True)
    check("...to roughly the contract's 44 characters",
          len(banner(longr, today, 3)[0].split("main: ")[1].strip()), 44)
    check("an unparseable date degrades to 'day ?', not a crash",
          "day ?" in banner(json.dumps({"slug": "s", "started": "yesterday"}),
                            today, 3)[0], True)

    print("\n=== the root, and the loud degradation ===")
    check("an absolute PROJECT_ROOT is used as given",
          resolve_root(str(Path("/abs/repo")), Path("/x"), lambda d: False)[0],
          Path("/abs/repo"))
    check("no PROJECT_ROOT -> the nearest .git ancestor, no complaint",
          resolve_root("", Path("/a/b/c"), lambda d: d == Path("/a"))[0],
          Path("/a"))
    check("...and that is not a problem worth printing",
          resolve_root("", Path("/a/b/c"), lambda d: d == Path("/a"))[1], "")
    check("no root at all -> a VISIBLE problem, not a vanished banner",
          bool(resolve_root("", Path("/a/b"), lambda d: False)[1]), True)
    check("a RELATIVE PROJECT_ROOT with no .git is also visible",
          bool(resolve_root("../repo", Path("/a/b"), lambda d: False)[1]), True)

    print("\n=== the context bar ===")
    check("the bar has one cell per configured cell (plus the mark)",
          _visible(context_bar(50, 0, 16, 75)).count("█")
          + _visible(context_bar(50, 0, 16, 75)).count("░"), 16)
    check("under the mark there is no clear nudge",
          "clear" in context_bar(40, 0, 16, 75), False)
    check("at the mark the nudge appears",
          "clear" in context_bar(80, 0, 16, 75), True)
    check("token counts are humanised",
          "410k" in context_bar(50, 410_000, 16, 75), True)
    check("a silly percentage is clamped, not crashed",
          "100%" in context_bar(240, 0, 16, 75), True)
    # MINOR-4: an absent or misnamed context key must not silently drop the
    # bar. No bar reads as "plenty of room"; `ctx ?` reads as "I do not know".
    check("no context data at all renders a `ctx ?` placeholder",
          "ctx ?" in render({}, dict(DEFAULTS), today), True)
    check("a MISNAMED context key also renders the placeholder",
          "ctx ?" in render({"contextWindow": {"used_percentage": 40}},
                            dict(DEFAULTS), today), True)
    check("a context value of the wrong type renders it too",
          "ctx ?" in render({"context_window": {"used_percentage": "lots"}},
                            dict(DEFAULTS), today), True)
    check("real context data renders a bar and NOT the placeholder",
          "ctx ?" in render({"context_window": {"used_percentage": 40,
                                                "total_input_tokens": 1000}},
                            dict(DEFAULTS), today), False)

    print("\n=== guarded segments ===")
    check("an empty payload still renders a board",
          "main" in render({}, dict(DEFAULTS), today), True)
    check("a payload whose sub-objects are the WRONG TYPE still renders",
          "main" in render({"cost": "not a dict", "model": 7,
                            "context_window": None}, dict(DEFAULTS), today),
          True)
    check("a cost field that is not a number does not take the board down",
          "main" in render({"cost": {"total_cost_usd": "free",
                                     "total_lines_added": "many"}},
                           dict(DEFAULTS), today), True)
    check("duration survives nonsense", duration("banana"), "")

    print()
    print(f"STATUSLINE SELFTEST: {'PASS' if ok else 'FAIL'} — {n} checks")
    return 0 if ok else 1


def _visible(s: str) -> str:
    import re
    return re.sub(r"\033\[[0-9;]*m", "", s)


DEMO = {
    "session_id": "demo", "model": {"display_name": "lane-tier"},
    "context_window": {"used_percentage": 82, "total_input_tokens": 410000},
    "cost": {"total_cost_usd": 3.4567, "total_duration_ms": 5400000,
             "total_lines_added": 120, "total_lines_removed": 30},
}


def main() -> int:
    ap = argparse.ArgumentParser(description="The status board, cross-platform.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if a.selftest:
        return selftest()
    cfg = load_config()
    if a.demo:
        print(render(DEMO, cfg, date.today()))
        return 0
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    try:
        print(render(payload, cfg, date.today()))
    except Exception as e:
        # LAST-DITCH GUARD. Whatever happened, print something: a board that
        # throws is a board that gets unwired, and then there is no board.
        print(seg("91", f"statusline error: {e!r}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
