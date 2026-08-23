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
**Every segment is guarded, with deliberate exceptions.** A missing field, an
unreadable file, an absent git repo: the segment disappears and the board still
renders. A status line that throws is a status line that gets removed within
the day, and then you have no board at all.

The exceptions are the segments whose SILENCE WOULD ASSERT SOMETHING FALSE, and
there are four:

  * the sidequest banner - a corrupt or unreadable flag file renders a LOUD
    "state file unreadable" banner, because silence there asserts "you are back
    on the main line";
  * a `PROJECT_ROOT` this file cannot resolve - it says so on the board instead
    of dropping the banner and letting an open side quest go invisible;
  * the context bar - a missing or misnamed context key renders `ctx ?`, since
    an absent bar reads as "plenty of room left";
  * the escape-rate segment ONCE A LEDGER IS CONFIGURED - a missing tool, an
    unreadable ledger or a malformed table is rendered, never dropped. With no
    ledger configured the segment does not exist at all, which is the one state
    that asserts nothing.

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

# THE CONSOLE'S OWN ANSWER, CAPTURED BEFORE main() OVERRIDES IT. `main()`
# reconfigures stdout to utf-8/replace so that a pipe always receives valid
# UTF-8; after that call `sys.stdout.encoding` says "utf-8" on every host and
# has stopped being evidence about the terminal. This value is read at import,
# which is before the override, so it is the interpreter's own reading of the
# platform - and it is what the sparkline's tick set is derived from.
STDOUT_ENCODING = getattr(sys.stdout, "encoding", "") or ""
try:
    # ...and whether anybody's CODE PAGE is in the way at all. A pipe carries
    # whatever bytes are written to it and the reader decodes them - which is
    # the harness case, and the harness reads UTF-8. Only a console has a code
    # page that can refuse a glyph.
    STDOUT_IS_CONSOLE = bool(sys.stdout.isatty())
except Exception:
    STDOUT_IS_CONSOLE = False

# ---- IN-MODULE DEFAULTS. The board must render before anything is set up. --
DEFAULTS = {
    "SIDEQUEST_FLAG": ".claude/sidequest.json",
    "SIDEQUEST_STALE_DAYS": "3",
    "STATUS_BAR_CELLS": "16",
    "STATUS_CLEAR_MARK_PCT": "75",
    "STATUS_BOARD_LINE_FILE": "NONE",
    "AGENT_TRANSCRIPT_DIR": "NONE",
    "STATUS_ESCAPE_LEDGER": "NONE",
    "PROJECT_ROOT": "",
}

ESC = "\033"

# ---- the escape-rate segment ---------------------------------------------
# OPT-IN: `STATUS_ESCAPE_LEDGER` is NONE by default, and with it unset the
# segment does not exist at all. Module 05's own README says "resist adding
# segments", and that rule is right: every segment competes with the two facts
# the board exists for. This one is offered rather than imposed, and an adopter
# who never names a ledger pays nothing - not a marker, not a file read, not
# even the import of the tool.
SPARK_BLOCKS = "▁▂▃▄▅▆▇█"
# The ASCII ramp, for a console whose encoding cannot carry the blocks. Eight
# ticks, ascending ink, so the shape survives the substitution.
SPARK_ASCII = "_.:-=+*#"
# Most recent rounds drawn. Older ones are MARKED (a leading ellipsis), never
# silently dropped - a shortened sparkline that looks like the whole history
# is the same lie as a missing segment.
SPARK_MAX = 16
# Where the escape-rate tool lives, in order: beside this file (an adopter
# copies the tools it uses into `tools/`), then the kit's own module layout.
# The same two-candidate search `escape_rate.py` itself uses to find the verify
# runner. Not configurable on purpose: one more path slot buys nothing an
# adopter cannot get by putting the tool where the other tools are.
ESCAPE_TOOL_CANDIDATES = ("escape_rate.py", "../modules/04-ledgers/escape_rate.py")


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


def tick_ramp(encoding: str) -> str:
    """The tick set this stream can actually print. DERIVED, never hard-coded.

    A block-drawing sparkline on a console running cp1252 or cp437 renders as a
    row of `?`, which reads as data. The platform answer is therefore taken
    FROM the platform - the stream's own encoding is asked whether it can carry
    the blocks - rather than from a guess about which operating system tends to
    have which console. `sys.platform == "win32"` would be wrong in both
    directions: a Windows terminal set to UTF-8 draws the blocks fine, and a
    POSIX host with LANG=C does not.

    Pure: it takes the encoding NAME, so the fallback is testable without a
    console. The name the board feeds it is `STDOUT_ENCODING`, captured at
    import - BEFORE `main()` forces the stream to utf-8 - because after that
    call every host reports "utf-8" and the question has no answer left.

    THE RESIDUAL, STATED: this is the strongest signal available inside the
    process, and it is not proof. A console lying about its code page, or one
    reconfigured after the board starts, is not visible from here. It is also
    narrower than the whole board: the other segments draw block and box
    characters unconditionally, which predates this segment and is unchanged
    by it. What this buys is that the one segment carrying a METRIC never
    renders its number as a row of question marks."""
    try:
        SPARK_BLOCKS.encode(encoding or "ascii")
    except (LookupError, UnicodeEncodeError, TypeError, ValueError):
        return SPARK_ASCII
    return SPARK_BLOCKS


def ramp_for_stream(encoding: str, is_console: bool) -> str:
    """The tick set for THIS stream. Pure, and the whole platform decision.

    Two different questions, and conflating them gets one of them wrong:

      * **A pipe** - the harness case - carries the bytes `main()` writes, and
        `main()` reconfigures the stream to UTF-8 before writing any. The
        reader decodes them. No code page is involved, so the blocks are safe
        and dropping to ASCII there would degrade every board that never had a
        problem.
      * **A console** has a code page of its own, and a block character it
        cannot represent is displayed as a question mark or a wrong glyph. That
        is the LESSONS-64 case, and there the ASCII ramp is the true rendering.

    Note which fact is NOT consulted: the operating system. `sys.platform ==
    "win32"` is wrong in both directions - a Windows terminal set to UTF-8
    draws the blocks, and a POSIX host under LANG=C does not."""
    return tick_ramp(encoding) if is_console else SPARK_BLOCKS


def ellipsis(ramp: str) -> str:
    """The truncation mark, from the same decision that chose the ramp."""
    return "…" if ramp == SPARK_BLOCKS else "..."


def spark(rates, ceiling, ramp: str, cap: int = SPARK_MAX) -> tuple:
    """(ticks, hidden_count) - the rounds as a sparkline, oldest first.

    THE SCALE IS THE CEILING, not the highest round in the series. Scaling to
    the series maximum makes 1%, 2%, 1% look like a mountain range and makes
    every series look equally dramatic; scaling to the ceiling answers the
    question the ceiling is there to ask - how close was each round to the
    line - and keeps the picture comparable between one run and the next. A
    round at or over the ceiling is a FULL tick; the exact number is in the
    ledger, and the headline percentage is printed beside the sparkline.

    A round of exactly zero gets the lowest tick; a round above zero never
    does, however small. Those are different facts and the board must not
    render them the same."""
    try:
        top = float(ceiling)
    except (TypeError, ValueError):
        top = 0.0
    if top <= 0:
        top = 100.0
    seq = list(rates or [])
    shown = seq[-cap:] if cap and len(seq) > cap else seq
    out = ""
    for v in shown:
        try:
            f = float(v)
        except (TypeError, ValueError):
            f = 0.0
        if f <= 0:
            idx = 0
        else:
            idx = max(1, min(len(ramp) - 1, int(f / top * len(ramp))))
        out += ramp[idx]
    return out, len(seq) - len(shown)


def escape_text(kind: str, detail, ramp: str) -> tuple:
    """(text, style) for the escape-rate segment, or None for 'no segment'.

    NONE IS THE UNCONFIGURED CASE AND NOTHING ELSE. Once a ledger is named,
    every outcome is a rendering: a tool that could not be found, a ledger that
    aborted, a project with no rounds yet, a measured rate. The board never
    drops a configured segment, for the same reason it never drops the context
    bar - an absent number reads as a good one.

    THE NUMBERS ARE NOT COMPUTED HERE. `detail` is the report dict from
    `escape_rate.py`; this function formats it. A second ledger parser living
    in the status board is precisely the two-authorities defect that tool's own
    docstring calls this kit's oldest failure class."""
    loud = "97;101;1"        # white on red
    amber = "30;103;1"       # black on amber
    if kind == "off":
        return None
    if kind == "unavailable":
        # Configured, but the instrument is not here. Amber rather than red:
        # nothing is wrong with the project, something is wrong with the
        # wiring - and either way it is not silence.
        return (" esc UNAVAILABLE (escape_rate.py not found) ", amber)
    if kind == "abort":
        d = " ".join(str(detail or "").split())
        if len(d) > 60:
            d = d[:59] + ellipsis(ramp)
        return (f" esc LEDGER ABORT: {d} ", loud)

    rep = detail if isinstance(detail, dict) else {}
    state = str(rep.get("state") or "?")
    if state not in ("MEASURED", "SMALL-N"):
        # THE STATE WORD, VERBATIM FROM THE TOOL, and never a zero. `esc 0.0%`
        # for a project that has recorded no rounds is a flattering lie; the
        # tool's own exit-code contract makes the same distinction and this
        # segment carries it through unchanged. SMALL-N is NOT in this branch:
        # there the CUMULATIVE number is still fully measured and hiding it
        # behind the state word would drop real information from the glance -
        # it renders below with the rate kept and the word as a suffix.
        return (f"esc {state}", "90")

    ticks, hidden = spark([r.get("pct") for r in rep.get("per_round") or []],
                          rep.get("ceiling_pct"), ramp)
    if hidden:
        ticks = ellipsis(ramp) + ticks
    txt = f"esc {float(rep.get('rate_pct') or 0.0):.1f}% {ticks}"
    unc = rep.get("rounds_uncounted") or 0
    if unc:
        # The tool prints this on every run, including the zero, because a
        # field that only appears when it is interesting is a field whose
        # absence nobody notices. On one line there is no room for the zero
        # case, so the board prints it only when rounds actually left the
        # denominator - which is the half that would otherwise overstate the
        # coverage behind the number.
        txt += f" +{unc} uncounted"
    if rep.get("over_ceiling"):
        return (txt + " OVER", "91;1")
    if state == "SMALL-N":
        # The latest round is under the gate's denominator floor (round 27's
        # ruling): the per-round gate is not armed, the cumulative rate above
        # is untouched, and the literal state word says so on the glance. A
        # rising trend is not masked by it - both words are functional and
        # both fit the glance.
        sfx = " RISING" if rep.get("trend") == "RISING" else ""
        return (txt + " SMALL-N" + sfx, "93")
    if rep.get("trend") == "RISING":
        return (txt + " RISING", "93")
    return (txt, "90")


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


def load_escape_tool(here: Path = HERE):
    """`escape_rate.py` as a module, or None. The board's ONLY source of
    escape-rate numbers.

    Imported rather than run as a subprocess: a subprocess costs a whole
    interpreter start on every render, and the board renders on every message.
    Measured on the kit's own 1071-line ledger, 20 renders: import 5.8 ms
    one-off, read and parse 1.4 ms per render. See module 05's README for why
    there is no cache."""
    import importlib.util
    for cand in ESCAPE_TOOL_CANDIDATES:
        p = here / cand
        try:
            if not p.is_file():
                continue
        except OSError:
            continue
        saved = sys.dont_write_bytecode
        try:
            # THE BOARD WRITES NO FILES. That is a load-bearing property of
            # this module - it reads state and never produces any - and an
            # ordinary import would drop a __pycache__ directory beside the
            # tool on the first render.
            sys.dont_write_bytecode = True
            spec = importlib.util.spec_from_file_location(
                "_oar_escape_rate", str(p))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # THE SURFACE THE BOARD USES, checked before it is used. An older
            # copy of the tool sitting in an adopter's `tools/` imports
            # perfectly and then fails on the first attribute; UNAVAILABLE is
            # the honest reading of that, and it is a rendering rather than a
            # traceback swallowed by the last-ditch guard.
            if all(hasattr(mod, a) for a in
                   ("read_ledger", "parse_rounds", "report", "DEFAULT_CEILING")):
                return mod
            return None
        except Exception:
            return None
        finally:
            sys.dont_write_bytecode = saved
    return None


def escape_state(cfg: dict, root: Path, tool=None) -> tuple:
    """(kind, detail) - the board's read of the escape rate.

    Every failure is a KIND that renders, never a dropped segment. `tool` is
    injectable so the selftest can drive this without a search."""
    led = cfg_get(cfg, "STATUS_ESCAPE_LEDGER")
    if not led:
        return "off", None
    mod = tool if tool is not None else load_escape_tool()
    if mod is None:
        return "unavailable", None
    p = Path(led)
    if not p.is_absolute():
        # Against the RESOLVED root, not the cwd. The harness does not promise
        # a working directory, and a repo-relative ledger resolved against a
        # foreign cwd is a silently missing file.
        p = root / p
    try:
        text = mod.read_ledger(p)
    except FileNotFoundError:
        return "abort", f"no ledger at {p.as_posix()}"
    except OSError as e:
        return "abort", f"{p.as_posix()} could not be read: {e}"
    try:
        return "ok", mod.report(mod.parse_rounds(text), mod.DEFAULT_CEILING)
    except Exception as e:
        # Broad on purpose, and it does NOT swallow: a malformed ledger raises
        # the tool's LedgerError and anything else means the tool's shape has
        # moved under the board. Both end up on the board in red, which is the
        # outcome this whole segment exists to guarantee.
        return "abort", str(e) or e.__class__.__name__


def _d(payload: dict, key: str) -> dict:
    """A sub-object, or an empty one. Harness payloads are somebody else's
    JSON: a field that is a string today can be a dict tomorrow and null the
    day after, and none of those may take the board down."""
    v = payload.get(key)
    return v if isinstance(v, dict) else {}


def render(payload: dict, cfg: dict, today: date, ramp: str = None) -> str:
    if ramp is None:
        ramp = ramp_for_stream(STDOUT_ENCODING, STDOUT_IS_CONSOLE)
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

    esc = escape_text(*escape_state(cfg, root), ramp=ramp)
    if esc:
        parts.append(seg(esc[1], esc[0]))

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

    print("\n=== the escape-rate segment: the ramp, DERIVED from the stream ===")
    # FORCED RED for the encoding choice. A hard-coded block ramp renders as a
    # row of `?` on a cp1252 console, which reads as data, and no check that
    # only ever runs on a UTF-8 host would see it. The derivation is a pure
    # function of the encoding NAME, so both answers are testable here.
    check("a UTF-8 stream gets the block ramp", tick_ramp("utf-8"),
          SPARK_BLOCKS)
    check("FORCED RED: a cp1252 console CANNOT carry the blocks, so it gets "
          "the ASCII ramp", tick_ramp("cp1252"), SPARK_ASCII)
    check("...and neither can cp437", tick_ramp("cp437"), SPARK_ASCII)
    check("...nor plain ascii", tick_ramp("ascii"), SPARK_ASCII)
    check("an encoding name Python does not know falls back rather than "
          "raising", tick_ramp("not-an-encoding"), SPARK_ASCII)
    check("no encoding at all falls back too", tick_ramp(""), SPARK_ASCII)
    check("CONTROL: the two ramps are different strings of the same length, "
          "so the fallback is a substitution and not a shorter picture",
          (SPARK_BLOCKS != SPARK_ASCII, len(SPARK_BLOCKS), len(SPARK_ASCII)),
          (True, 8, 8))
    check("the truncation mark follows the same decision",
          (ellipsis(SPARK_BLOCKS), ellipsis(SPARK_ASCII)), ("…", "..."))
    check("the board derives from a captured encoding, and captures it at "
          "IMPORT - after main()'s reconfigure every host reports utf-8 and "
          "the question has no answer left",
          (isinstance(STDOUT_ENCODING, str),
           isinstance(STDOUT_IS_CONSOLE, bool)), (True, True))
    check("a PIPE gets the blocks whatever the locale says - main() writes "
          "UTF-8 to it and the reader decodes; no code page is involved",
          ramp_for_stream("cp1252", False), SPARK_BLOCKS)
    check("FORCED RED: a CONSOLE on cp1252 gets ASCII - that is the one place "
          "a code page can refuse the glyph",
          ramp_for_stream("cp1252", True), SPARK_ASCII)
    check("...and a console on UTF-8 keeps the blocks, so the fallback is not "
          "a blanket punishment of one operating system",
          ramp_for_stream("utf-8", True), SPARK_BLOCKS)

    print("\n=== the sparkline: scaled to the CEILING ===")
    check("one tick per round", len(spark([1, 2, 3, 4], 35.0, SPARK_BLOCKS)[0]),
          4)
    check("a round of exactly zero gets the lowest tick",
          spark([0], 35.0, SPARK_BLOCKS)[0], SPARK_BLOCKS[0])
    check("FORCED RED: a round ABOVE zero never gets the zero tick, however "
          "small - 'no escapes' and 'almost none' are different facts",
          spark([0.1], 35.0, SPARK_BLOCKS)[0] == SPARK_BLOCKS[0], False)
    check("...it gets the tick above it", spark([0.1], 35.0, SPARK_BLOCKS)[0],
          SPARK_BLOCKS[1])
    check("a round AT the ceiling is a full tick",
          spark([35.0], 35.0, SPARK_BLOCKS)[0], SPARK_BLOCKS[-1])
    check("a round OVER the ceiling is clamped, not an index error",
          spark([90.0], 35.0, SPARK_BLOCKS)[0], SPARK_BLOCKS[-1])
    check("the band below the ceiling is not full",
          spark([30.0], 35.0, SPARK_BLOCKS)[0] == SPARK_BLOCKS[-1], False)
    check("STATED, not hidden: the top tick is the last EIGHTH of the scale, "
          "a band and not a point - 34.0 against a 35.0 ceiling reads full",
          spark([34.0], 35.0, SPARK_BLOCKS)[0], SPARK_BLOCKS[-1])
    check("the scale is the CEILING, not the series maximum: the same round "
          "renders differently under a different ceiling",
          (spark([20.0], 35.0, SPARK_BLOCKS)[0],
           spark([20.0], 80.0, SPARK_BLOCKS)[0]),
          (SPARK_BLOCKS[4], SPARK_BLOCKS[2]))
    check("a nonsense ceiling falls back to a 0-100 scale rather than "
          "dividing by zero", spark([50.0], 0, SPARK_BLOCKS)[0],
          SPARK_BLOCKS[4])
    check("a nonsense rate is not a crash", spark(["lots"], 35.0,
                                                  SPARK_BLOCKS)[0],
          SPARK_BLOCKS[0])
    check("the ASCII ramp draws the same shape",
          spark([0, 35.0], 35.0, SPARK_ASCII)[0],
          SPARK_ASCII[0] + SPARK_ASCII[-1])
    check("a series inside the cap hides nothing",
          spark([1] * SPARK_MAX, 35.0, SPARK_BLOCKS)[1], 0)
    check("FORCED RED: a longer series is TRUNCATED and the hidden rounds are "
          "COUNTED, not silently dropped",
          spark([1] * (SPARK_MAX + 5), 35.0, SPARK_BLOCKS)[1], 5)
    check("...and the visible part is the MOST RECENT rounds",
          spark([0] * 5 + [35.0] * SPARK_MAX, 35.0, SPARK_BLOCKS)[0],
          SPARK_BLOCKS[-1] * SPARK_MAX)

    print("\n=== the escape-rate segment: the degrade states ===")
    check("UNCONFIGURED is the ONE state that renders nothing at all",
          escape_text("off", None, SPARK_BLOCKS), None)
    check("...and it is the default, so an adopter who never names a ledger "
          "gets no segment and no marker",
          escape_state(dict(DEFAULTS), Path("/nowhere"))[0], "off")
    check("...which is visible on a real board",
          "esc " in render({}, dict(DEFAULTS), today), False)
    # EVERY STATE BELOW IS CHECKED FOR 'not None' BEFORE IT IS UNPACKED. A
    # mutation that made one of them drop its segment silently is exactly the
    # defect these checks exist to catch, and it must be reported as a FAIL -
    # not as a traceback that never reaches the verdict line.
    unavail = escape_text("unavailable", None, SPARK_BLOCKS)
    check("FORCED RED: a CONFIGURED ledger with no tool is NOT the 'no "
          "segment' answer", unavail is None, False)
    unavail = unavail or ("", "")
    check("...it says UNAVAILABLE out loud", "UNAVAILABLE" in unavail[0], True)
    check("...on an amber field, not in silence", unavail[1], "30;103;1")
    ab = escape_text("abort", "no ledger at docs/JUDGMENT-LEDGER.md",
                     SPARK_BLOCKS)
    check("FORCED RED: an ABORT is never the 'no segment' answer either - a "
          "silently dropped instrument reads as a good score", ab is None,
          False)
    ab = ab or ("", "")
    check("a ledger ABORT is LOUD and names the reason",
          ("ABORT" in ab[0] and "docs/JUDGMENT-LEDGER.md" in ab[0], ab[1]),
          (True, "97;101;1"))
    long_ab = escape_text("abort", "x" * 200, SPARK_BLOCKS) or ("", "")
    check("a very long abort reason is truncated with the ramp's own mark",
          long_ab[0].endswith("… "), True)
    none_yet = {"state": "NO-ROUNDS-RECORDED", "rate_pct": 0.0,
                "per_round": [], "ceiling_pct": 35.0, "rounds_uncounted": 0}
    txt = (escape_text("ok", none_yet, SPARK_BLOCKS) or ("", ""))[0]
    check("NO ROUNDS RECORDED shows the tool's STATE WORD", txt,
          "esc NO-ROUNDS-RECORDED")
    check("FORCED RED: ...and never a zero, which would read as a good score",
          "0.0%" in txt, False)
    small_n = {"state": "SMALL-N", "rate_pct": 16.7, "ceiling_pct": 35.0,
               "rounds_uncounted": 0, "trend": "RISING",
               "over_ceiling": False,
               "per_round": [{"pct": 8.3}, {"pct": 50.0}]}
    sn_txt, sn_style = escape_text("ok", small_n, SPARK_BLOCKS) or ("", "")
    check("SMALL-N keeps the cumulative rate on the board - the number is "
          "still fully measured and hiding it would drop information from "
          "the glance", sn_txt.startswith("esc 16.7% "), True)
    check("...carries the literal state word as a suffix, on amber, and "
          "does NOT mask a rising trend beside it",
          (sn_txt.endswith(" SMALL-N RISING"), sn_style), (True, "93"))
    check("...and without a rising trend the suffix is the state word alone",
          (escape_text("ok", dict(small_n, trend="FALLING"),
                       SPARK_BLOCKS) or ("", ""))[0].endswith(" SMALL-N"),
          True)

    print("\n=== the escape-rate segment: a measured rate ===")
    measured = {"state": "MEASURED", "rate_pct": 19.3, "ceiling_pct": 35.0,
                "rounds_uncounted": 1, "trend": "FALLING",
                "over_ceiling": False,
                "per_round": [{"pct": 42.9}, {"pct": 0.0}, {"pct": 10.0}]}
    txt, style = escape_text("ok", measured, SPARK_BLOCKS) or ("", "")
    check("the headline is the rate the tool computed", txt.startswith(
        "esc 19.3% "), True)
    # PADDED, for the rule stated thirty lines above: a state that renders a
    # shorter string than expected must be reported as a FAIL, not as an
    # IndexError that kills the run before the verdict line. Spec-side review
    # planted exactly that (the MEASURED state word renamed) and got a
    # traceback with no verdict line - the kit judges by required output lines,
    # and a selftest that produces none in its failing state is judging nothing.
    check("...followed by one tick per counted round",
          (txt.split(" ") + ["", "", ""])[2],
          SPARK_BLOCKS[-1] + SPARK_BLOCKS[0] + SPARK_BLOCKS[2])
    check("rounds excluded from the denominator are named on the board - the "
          "board must not overstate the coverage behind the number",
          "+1 uncounted" in txt, True)
    check("...and are absent when there are none",
          "uncounted" in escape_text("ok", dict(measured, rounds_uncounted=0),
                                     SPARK_BLOCKS)[0], False)
    rising = escape_text("ok", dict(measured, trend="RISING"),
                         SPARK_BLOCKS) or ("", "")
    check("a RISING escape rate is called out in amber - the doctrine's own "
          "signal to stop looping and fix the check",
          ("RISING" in rising[0], rising[1]), (True, "93"))
    over = escape_text("ok", dict(measured, over_ceiling=True),
                       SPARK_BLOCKS) or ("", "")
    check("a latest round OVER the ceiling is red and says so",
          ("OVER" in over[0], over[1]), (True, "91;1"))
    # THE PRECEDENCE, and it is load-bearing in the worst case the segment
    # exists for. A rate that is BOTH over the ceiling and rising is the one
    # combination that must not be softened: `over_ceiling` is tested first, so
    # it renders red OVER, not amber RISING. Per-field checks cannot see this -
    # spec-side review swapped the two branches and passed 90/90, which is a
    # red alarm silently downgraded to amber.
    both = escape_text("ok", dict(measured, over_ceiling=True,
                                  trend="RISING"), SPARK_BLOCKS) or ("", "")
    check("FORCED RED: a round that is BOTH over the ceiling and rising "
          "renders RED and says OVER - the alarm is never downgraded to amber",
          ("OVER" in both[0], both[1]), (True, "91;1"))
    check("...and the amber style is not what that case returns",
          both[1] == "93", False)
    check("FORCED RED: an ordinary falling rate is NOT dressed as an alarm",
          (style, "OVER" in txt, "RISING" in txt), ("90", False, False))

    print("\n=== the escape-rate segment: ONE authority for the numbers ===")
    # THE DECLARED FILESYSTEM SECTION, named rather than smuggled in. Every
    # check above this line is a pure function of its arguments; these read the
    # escape-rate tool and a temporary ledger, because the defect they close is
    # a disagreement BETWEEN TWO FILES - a status board that grows its own
    # ledger parser and drifts from the tool the gate runs. No pure function of
    # this file can see that.
    import tempfile
    tool = load_escape_tool()
    if tool is None:
        # STATED, NOT SKIPPED IN SILENCE.
        check("escape_rate.py is NOT reachable from here, so the authority "
              "cross-check is UNAVAILABLE - said out loud, not passed in "
              "silence (looked in: " + ", ".join(ESCAPE_TOOL_CANDIDATES) + ")",
              True, True)
    else:
        TBL = ("| Round | Items | Escapes |\n|---|---|---|\n"
               "| r1 | 4 | 1 |\n| r2 | 16 | 4 |\n")
        rep = tool.report(tool.parse_rounds(TBL), tool.DEFAULT_CEILING)
        board = escape_text("ok", rep, SPARK_BLOCKS)[0]
        check("THE BINDING: the percentage on the board is the one "
              "escape_rate.py computed, character for character",
              f"{rep['rate_pct']:.1f}%" in board, True)
        # PRECONDITION, AND LABELLED AS ONE. This line only proves that
        # report() surfaces the ceiling it was handed, so `ceiling_pct` is the
        # field the board reads - the test built `rep` by passing
        # DEFAULT_CEILING in itself. Spec-side review measured exactly what it
        # is worth: replacing the ceiling with a literal INSIDE escape_state
        # passed 90/90 against this check. The real binding is in the
        # live-ledger section below, where the report comes from escape_state.
        check("PRECONDITION (not the binding): report() surfaces the ceiling "
              "it was handed, so `ceiling_pct` is the field the board reads",
              rep["ceiling_pct"], tool.DEFAULT_CEILING)
        check("...and the state word is the tool's spelling",
              escape_text("ok", tool.report([], tool.DEFAULT_CEILING),
                          SPARK_BLOCKS)[0],
              "esc " + tool.report([], tool.DEFAULT_CEILING)["state"])
        check("FORCED RED: change the tool's number and the board's changes "
              "with it - this segment reads a report, it does not carry a "
              "constant",
              f"{rep['rate_pct']:.1f}%" in escape_text(
                  "ok", dict(rep, rate_pct=99.9), SPARK_BLOCKS)[0], False)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = dict(DEFAULTS, STATUS_ESCAPE_LEDGER="LEDGER.md")
            check("FORCED RED: a configured ledger that is NOT THERE aborts "
                  "visibly - it does not quietly become 'no segment'",
                  escape_state(cfg, root, tool)[0], "abort")
            (root / "LEDGER.md").write_text("# no table here\n",
                                            encoding="utf-8")
            kind, detail = escape_state(cfg, root, tool)
            check("FORCED RED: a ledger with no escape-rate table aborts with "
                  "the TOOL's sentence", (kind, "good score" in str(detail)),
                  ("abort", True))
            (root / "LEDGER.md").write_text(TBL, encoding="utf-8")
            kind, detail = escape_state(cfg, root, tool)
            # `detail` is read through .get so that a mutation which makes
            # this path abort is reported as a FAIL and not as a traceback
            # that never reaches the verdict line.
            d = detail if isinstance(detail, dict) else {}
            check("a well-formed ledger is read and reported",
                  (kind, d.get("rate_pct"), d.get("state")),
                  ("ok", 25.0, "MEASURED"))
            # THE CEILING BINDING, on the report the BOARD actually produced.
            # `d` came out of escape_state, so this reads the ceiling that
            # escape_state passed to report() - which is the thing the registry
            # row claims is bound and the precondition above cannot see. Put a
            # literal in escape_state and this goes red naming both numbers.
            # KNOWN-ISSUES round 19 records the drifting-ceiling class as one
            # of this kit's own escapes; it does not get to happen twice.
            check("THE CEILING BINDING: the ceiling the board scales against "
                  "is the TOOL's DEFAULT_CEILING, read through escape_state "
                  "and not a literal in this file",
                  d.get("ceiling_pct"), tool.DEFAULT_CEILING)
            check("FORCED RED: ...and a SECOND authority for the ceiling is "
                  "what that check refuses - a board scaling against its own "
                  "number disagrees with the gate about the same ledger",
                  tool.report(tool.parse_rounds(TBL),
                              40.0)["ceiling_pct"] == tool.DEFAULT_CEILING,
                  False)
            check("...and the segment appears on a real board",
                  "esc 25.0%" in _visible(render(
                      {}, dict(cfg, PROJECT_ROOT=str(root)), today,
                      SPARK_BLOCKS)), True)
            check("a REPO-RELATIVE ledger resolves against the resolved root, "
                  "not the working directory - a foreign cwd must not make a "
                  "configured segment vanish",
                  escape_state(cfg, Path(td) / "elsewhere", tool)[0], "abort")
            check("an ABSOLUTE ledger path is used as given",
                  escape_state(dict(DEFAULTS, STATUS_ESCAPE_LEDGER=str(
                      root / "LEDGER.md")), Path("/nowhere"), tool)[0], "ok")
            # THE BOM CASE, from the same second-machine sweep that put
            # utf-8-sig in the tool. A Windows editor writes one; plain utf-8
            # would make the header row stop looking like a table row and the
            # SAME ledger would abort on one host and parse on the other.
            (root / "LEDGER.md").write_bytes(
                b"\xef\xbb\xbf" + TBL.encode("utf-8"))
            check("a ledger written with a BOM parses - the board reads it "
                  "through the tool's own reader, so it inherits that rule",
                  escape_state(cfg, root, tool)[0], "ok")
            # THE STALE-COPY CONTROL. An older escape_rate.py in an adopter's
            # `tools/` imports perfectly and then fails on the first attribute
            # the board calls. Both directions are planted here, so the
            # surface check is a real assertion and not a comment.
            (root / "escape_rate.py").write_text("X = 1\n", encoding="utf-8")
            check("FORCED RED: a tool found but MISSING one of the four names "
                  "the board calls is None, so the segment says UNAVAILABLE "
                  "instead of raising on the first attribute",
                  load_escape_tool(root), None)
            (root / "escape_rate.py").write_text(
                "def read_ledger(p): pass\ndef parse_rounds(t): pass\n"
                "def report(r, c): pass\nDEFAULT_CEILING = 35.0\n",
                encoding="utf-8")
            check("CONTROL: ...and a tool that DOES carry all four is "
                  "accepted, so the check above is not passing for the wrong "
                  "reason", load_escape_tool(root) is None, False)

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
