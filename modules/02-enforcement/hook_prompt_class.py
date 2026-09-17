#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hook_prompt_class.py -- a UserPromptSubmit hook that tags each prompt with a
class and a suggested route, before whoever reads it next reads it. It
SUGGESTS. It never routes, never blocks, never edits the prompt.

PRIOR ART, named so nothing here is a re-invention:
  - `modules/02-enforcement/hook_model_gate.py`: the hook SHAPE this module
    copies -- one JSON object on stdin, one line out, fail-open on anything
    it cannot parse (module docstring, "THIS FILE NEEDS NO EDITING.
    Everything project-specific is read from `kit.config`"). Its config
    loader (`find_config()` line 119-138, `_read_pairs()` line 148-157,
    `load_config()` line 160-176, `is_placeholder()` line 227-236,
    `cfg_get()` line 239-254) is duplicated below rather than imported, the
    same reason `hook_fixtures.py` gives for duplicating it instead of
    importing it (that harness's own module docstring, "WHICH CONFIG":
    "duplicated here rather than imported because this harness must be able
    to judge a hook it does not share a directory with").
  - `modules/02-enforcement/hook_fixtures.py`: the ARMED check (its module
    docstring, claim 1, "THE FIRST ONE IS THE ONE PEOPLE MISS") is why this
    hook's own `--selftest` proves what it decides and says nothing about
    whether a harness ever calls it -- that is `settings.json.template`'s
    job, wired the same way `hook_model_gate.py` is.
  - `kit.config` lines 43-50 (the tiers block: generic names an adopter
    replaces, `FORBIDDEN_SPAWN_TIER` etc.) is the pattern this module's own
    two new slots, `LOCAL_TIER` and `PROMPT_CLASS_FIXTURES`, follow: a
    generic name and a `kit.config.local` escape hatch for anything true
    only on one machine (`kit.config` and `kit.config.local`, "later
    wins", same file's own header comment).
  - `tools/deident_scan.py`: the reason the class lists and the shipped
    fixtures below carry no owner's words. This hook's own template
    fixtures file is deliberately the neutral file that scanner is built to
    find nothing in.

WHAT IS NEW HERE, kit-shaped rather than ported verbatim from the seat this
lane took it from:
  - the class word/pattern lists are DATA, not constants: they load from
    `prompt_class.template.json` beside this file, then from whatever
    `kit.config`'s `PROMPT_CLASS_FIXTURES` slot names (a `kit.config.local`
    path), later wins per class. No list in this SOURCE FILE carries an
    owner's or a seat's words -- see the STANDING GUARD in the charter that
    built this file.
  - the tier-2 local model call is `LOCAL_TIER`-driven (`kit.config`):
    `NONE` means tier 1 only and the call is never attempted; any other
    value is `host:port/model`, and any host that is not loopback is
    refused BY CODE before a single byte is sent.
  - the routes are this kit's own vocabulary (`kit.config`'s
    `COORDINATOR_ROLE` and `SWEEP_TIER` slots), not the seat's.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
TEMPLATE_FILE = HERE / "prompt_class.template.json"

# ---------------------------------------------------------------------
# config -- duplicated from hook_model_gate.py's loader (prior art, above),
# not imported, for the same reason hook_fixtures.py gives for duplicating
# it: this hook must resolve a config even when it is copied somewhere that
# does not share a directory with the rest of module 02.
# ---------------------------------------------------------------------
def find_config() -> Path | None:
    """1. $KIT_CONFIG  2. ./kit.config  3. <this file's dir>/kit.config
    4. the nearest kit.config walking UP from this file's directory."""
    env = os.environ.get("KIT_CONFIG")
    cands = ([Path(env)] if env else []) + [
        Path.cwd() / "kit.config",
        HERE / "kit.config",
    ] + [d / "kit.config" for d in HERE.parents]
    for c in cands:
        try:
            if c.is_file():
                return c
        except OSError:
            continue
    return None


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


def load_config() -> dict:
    cfg: dict[str, str] = {}
    p = find_config()
    if p is None:
        return cfg
    _read_pairs(p, cfg)
    _read_pairs(p.with_name("kit.config.local"), cfg)
    cfg["_source"] = str(p)
    return cfg


PLACEHOLDER_WORDS = {"", "none", "null", "todo", "<unset>", "tbd", "changeme"}
PLACEHOLDER_SHAPES = (
    "your-", "/abs/path", "c:/abs/path", "<", "derive-from",
    "https://example.invalid", "/path/to/", "example.invalid",
)


def is_placeholder(value: str) -> bool:
    v = (value or "").strip()
    if v.lower() in PLACEHOLDER_WORDS:
        return True
    low = v.lower()
    return any(low.startswith(p) or low == p.rstrip("/")
               for p in PLACEHOLDER_SHAPES)


def cfg_get(cfg: dict, key: str):
    v = cfg.get(key)
    if v is None:
        return None
    v = v.strip()
    return None if is_placeholder(v) else v


CFG = load_config()
CFG_DIR = Path(CFG["_source"]).resolve().parent if CFG.get("_source") else Path.cwd()
COORDINATOR_ROLE = cfg_get(CFG, "COORDINATOR_ROLE") or "the coordinator"
SWEEP_TIER = cfg_get(CFG, "SWEEP_TIER") or "sweep-tier"
LOCAL_TIER_RAW = cfg_get(CFG, "LOCAL_TIER")
PROMPT_CLASS_FIXTURES_RAW = cfg_get(CFG, "PROMPT_CLASS_FIXTURES")

CLASS_ORDER = ("RULING", "DESIGN", "CAPTURE", "PRESENCE", "QUESTION")
FEW_SHOT_CLASSES = ("RULING", "DESIGN", "CAPTURE", "PRESENCE", "QUESTION")
FEW_SHOT_INDEX = 0

# Routes, one per class, text only -- this kit's own vocabulary, no seat
# words: `readback` is module 08's own term (CAPSULE.md), the sweep tier and
# the coordinator role are `kit.config`'s own slots.
ROUTES = {
    "RULING": "execute, then a one-line readback",
    "QUESTION": f"read under a small threshold; past it, an investigation "
                f"pass at {SWEEP_TIER}",
    "DESIGN": "read and acknowledge; nothing is chartered from it alone",
    "CAPTURE": "log it to the record, then continue",
    "PRESENCE": "acknowledge only; nothing fires",
    "UNSURE": f"{COORDINATOR_ROLE} decides",
}


# ---------------------------------------------------------------------
# class data -- loaded, never hard-coded. `prompt_class.template.json`
# ships the neutral default; `PROMPT_CLASS_FIXTURES` (a kit.config.local
# path) overlays it, later wins PER CLASS KEY, exactly like kit.config's own
# split (committed default, gitignored machine-specific overlay).
# ---------------------------------------------------------------------
def _resolve_fixtures_path() -> Path | None:
    if not PROMPT_CLASS_FIXTURES_RAW:
        return None
    p = Path(PROMPT_CLASS_FIXTURES_RAW)
    return p if p.is_absolute() else (CFG_DIR / p)


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _merge_layer(base: dict, overlay: dict) -> dict:
    """One level of {"classes": {...}, "fixtures": {...}}, per-class-key
    replace: an overlay class/fixture list REPLACES the base's entry for
    that same class name; a class the overlay does not mention is
    inherited from base untouched. This is what makes the generator's
    output (item 3) mean "grade RULING against the adopter's own ledger"
    rather than "add to the neutral ten" -- and what makes an overlay that
    only ever writes `fixtures.RULING` leave every other class alone."""
    out = {"classes": dict(base.get("classes") or {}),
           "fixtures": dict(base.get("fixtures") or {})}
    for section in ("classes", "fixtures"):
        for k, v in (overlay.get(section) or {}).items():
            out[section][k] = v
    return out


def load_class_data() -> dict:
    base = _read_json(TEMPLATE_FILE)
    fx_path = _resolve_fixtures_path()
    overlay = _read_json(fx_path) if fx_path and fx_path.is_file() else {}
    return _merge_layer(base, overlay)


CLASS_DATA = load_class_data()


def _class_words(label: str) -> list[str]:
    return list((CLASS_DATA.get("classes") or {}).get(label, {}).get("words") or [])


def _class_openers(label: str) -> list[str]:
    return list((CLASS_DATA.get("classes") or {}).get(label, {}).get("openers") or [])


def _has_word(text: str, phrase: str) -> bool:
    """Whole-word / whole-phrase, case-insensitive."""
    pat = r"(?<![A-Za-z0-9])" + re.escape(phrase) + r"(?![A-Za-z0-9])"
    return re.search(pat, text, re.IGNORECASE) is not None


def tier1_matches(prompt: str, class_data: dict | None = None) -> list[str]:
    """Every class tier 1 matches, in CLASS_ORDER. Deterministic word/
    pattern matching, case-insensitive, whole words. `class_data` is
    injectable so the selftest can invert lists without mutating module
    globals mid-run."""
    cd = class_data if class_data is not None else CLASS_DATA
    classes = cd.get("classes") or {}
    text = prompt or ""
    hit: list[str] = []
    if any(_has_word(text, w) for w in (classes.get("RULING") or {}).get("words") or []):
        hit.append("RULING")
    if any(_has_word(text, w) for w in (classes.get("DESIGN") or {}).get("words") or []):
        hit.append("DESIGN")
    if any(_has_word(text, w) for w in (classes.get("CAPTURE") or {}).get("words") or []):
        hit.append("CAPTURE")
    if any(_has_word(text, w) for w in (classes.get("PRESENCE") or {}).get("words") or []):
        hit.append("PRESENCE")
    stripped = text.strip()
    openers = (classes.get("QUESTION") or {}).get("openers") or []
    starts_interrogative = any(
        re.match(r"^\s*" + re.escape(o) + r"(?![A-Za-z0-9])", stripped,
                  re.IGNORECASE)
        for o in openers
    )
    trailing_q = stripped.endswith("?")
    # Same precedence as the source this was ported from: a RULING or a
    # DESIGN hit already carries an order or a tell, so QUESTION does not
    # also fire for those two; CAPTURE and PRESENCE, below it, do not
    # suppress it.
    if (starts_interrogative or trailing_q) and "RULING" not in hit and "DESIGN" not in hit:
        hit.append("QUESTION")
    return hit


def classify_tier1(prompt: str, class_data: dict | None = None) -> tuple[str, list[str]]:
    hits = tier1_matches(prompt, class_data)
    if len(hits) == 1:
        return hits[0], hits
    if len(hits) >= 2:
        return "MIXED", hits
    return "", hits


def route_for(label: str, members: list[str]) -> str:
    if label == "MIXED":
        return "; ".join(
            f"{m}->{ROUTES.get(m, ROUTES['UNSURE'])}" for m in members)
    return ROUTES.get(label, ROUTES["UNSURE"])


# ---------------------------------------------------------------------
# TIER 2 -- one local-model call on the residue. Loopback only: refused BY
# CODE before the call, whatever LOCAL_TIER names.
# ---------------------------------------------------------------------
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")
OLLAMA_TIMEOUT_S = 3

_CLASS_SET_TEXT = "RULING, QUESTION, DESIGN, CAPTURE, PRESENCE, or MIXED"

# Incremented ONLY immediately before the actual network call, so a
# selftest can assert LOCAL_TIER=NONE never causes one (item 6d): the
# counter is truth about attempts, not about intent.
CALL_ATTEMPTS = [0]


def parse_local_tier(raw: str | None) -> tuple[str, str] | None:
    """(host:port, model), or None when LOCAL_TIER is unset/NONE -- the
    kit.config comment's own words: "a local tier is a loopback endpoint
    and a model name, host:port/model, no scheme". Split on the FIRST
    slash only: a model name may itself contain one (registry/name
    style)."""
    if not raw or "/" not in raw:
        return None
    host_port, model = raw.split("/", 1)
    host_port, model = host_port.strip(), model.strip()
    if not host_port or not model:
        return None
    return host_port, model


_HOSTPORT_BAD_CHARS = ("@", "/", "\\")


def _host_port_is_wellformed(host_port: str) -> bool:
    """Refused OUTRIGHT, before any URL is built: an at-sign, a slash, a
    backslash or any whitespace inside `host_port` is credential or path
    syntax that has no business in a bare `host:port` pair -- and an
    at-sign is exactly what let finding 1's userinfo form (
    `localhost:11434@<foreign-host>`) slip past a first-colon split, since
    URL syntax takes the host to be everything after the LAST at-sign,
    never the first colon."""
    if not host_port:
        return False
    if any(c in host_port for c in _HOSTPORT_BAD_CHARS):
        return False
    return not any(c.isspace() for c in host_port)


def _is_loopback_url(url: str) -> bool:
    """The refusal that matters: parse the exact URL that would be
    requested with `urlsplit` -- the way `urllib.request` itself resolves
    a host, LAST at-sign wins, brackets strip for an IPv6 literal -- and
    check the hostname it resolves to against `LOOPBACK_HOSTS`. Never a
    first-colon split on the raw `host_port` string (finding 1)."""
    try:
        hostname = urlsplit(url).hostname
    except ValueError:
        return False
    return hostname is not None and hostname.lower() in LOOPBACK_HOSTS


def _is_loopback_host_port(host_port: str) -> bool:
    """Fail-closed at two layers, both required: `host_port` carries no
    credential/path syntax (checked first, before any URL is built), AND
    the URL that would actually be requested parses to a loopback
    hostname (checked second, on the assembled URL, never on `host_port`
    alone)."""
    if not _host_port_is_wellformed(host_port):
        return False
    return _is_loopback_url(f"http://{host_port}/api/generate")


def _diagnose_local_tier(raw: str | None) -> str | None:
    """Why a SET `LOCAL_TIER` will never be reached, one line naming the
    reason -- printed once by `main()` so a mistyped value degrades LOUDLY
    to stderr instead of silently to `by rules` on every prompt forever
    (finding 6). Returns None when `LOCAL_TIER` is unset, NONE, or usable.
    The four reasons named, in the order checked: malformed, userinfo,
    scheme, non-loopback."""
    if not raw:
        return None
    parsed = parse_local_tier(raw)
    if parsed is None:
        return f"malformed: want host:port/model, no scheme (got {raw!r})"
    host_port, _model = parsed
    if "@" in host_port:
        return ("userinfo syntax in host:port is refused outright "
                 f"(got {host_port!r})")
    last = host_port.rsplit(":", 1)[-1]
    if not last.isdigit():
        return ("a scheme prefix, not a bare host:port -- want "
                 f"host:port/model, no scheme (got {host_port!r})")
    if not _is_loopback_host_port(host_port):
        return ("non-loopback host: "
                 f"{host_port!r} is not 127.0.0.1, localhost, or ::1")
    return None


LOCAL_TIER = parse_local_tier(LOCAL_TIER_RAW)
LOCAL_ENABLED = LOCAL_TIER is not None
LOCAL_TIER_DIAGNOSTIC = _diagnose_local_tier(LOCAL_TIER_RAW)


def _few_shot_block(class_data: dict | None = None) -> str:
    """Five MESSAGE/LABEL lines pulled from the class data's fixtures by
    index, one per class -- never pasted into the source. Any load
    failure (missing class, short list) is skipped rather than raised:
    fail open, tier 2 just asks without examples."""
    cd = class_data if class_data is not None else CLASS_DATA
    fixtures = cd.get("fixtures") or {}
    lines = []
    for cls in FEW_SHOT_CLASSES:
        phrases = fixtures.get(cls)
        if isinstance(phrases, list) and len(phrases) > FEW_SHOT_INDEX:
            item = phrases[FEW_SHOT_INDEX]
            text = item.get("text") if isinstance(item, dict) else item
            if text:
                lines.append(f"MESSAGE: {text}\nLABEL: {cls}")
    return "\n\n".join(lines)


def tier2_classify(prompt: str, host_port: str, model: str,
                    timeout: float = OLLAMA_TIMEOUT_S) -> tuple[str, float, bool]:
    """(label, elapsed_ms, cold). On ANY failure -- a refused
    (non-loopback) endpoint, no server, timeout, an unparseable answer --
    returns ("UNSURE", elapsed_ms, cold): fail open, never guessing. The
    prompt text goes to a local process only: never to a file, never to a
    log. `cold` is True only on a timeout (the first call on a cold model
    can exceed a 3 s timeout; `keep_alive: 30m` below keeps it warm for
    the next one)."""
    start = time.monotonic()
    if not _is_loopback_host_port(host_port):
        return "UNSURE", (time.monotonic() - start) * 1000.0, False
    few_shot = _few_shot_block()
    prompt_text = (
        f"Classify the following user message into exactly one label "
        f"from this set: {_CLASS_SET_TEXT}. Reply with only the label, "
        f"nothing else.\n\n"
        + (f"{few_shot}\n\n" if few_shot else "")
        + f"MESSAGE:\n{prompt}"
    )
    body = json.dumps({
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "think": False,
        "keep_alive": "30m",
    }).encode("utf-8")
    url = f"http://{host_port}/api/generate"
    try:
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"},
            method="POST")
        CALL_ATTEMPTS[0] += 1
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        elapsed = (time.monotonic() - start) * 1000.0
        answer = json.loads(raw).get("response", "").strip().upper()
        for c in ("RULING", "QUESTION", "DESIGN", "CAPTURE", "PRESENCE", "MIXED"):
            if c in answer:
                return c, elapsed, False
        return "UNSURE", elapsed, False
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000.0
        cold = isinstance(exc, TimeoutError) or "timed out" in str(exc).lower()
        return "UNSURE", elapsed, cold


# ---------------------------------------------------------------------
# combined classify + one-line render
# ---------------------------------------------------------------------
def classify(prompt: str, use_local: bool = True) -> tuple[str, str, str, float, bool]:
    """(label, route, by, elapsed_ms, cold). Tier 1 first; tier 2 only on
    residue, and only when `use_local` AND `LOCAL_TIER` names a real
    endpoint -- `LOCAL_TIER = NONE` means tier 1 only, and tier 2 is never
    reached, never merely refused at the network layer."""
    label, members = classify_tier1(prompt)
    if label:
        return label, route_for(label, members), "rules", 0.0, False
    if not use_local or not LOCAL_ENABLED:
        return "UNSURE", ROUTES["UNSURE"], "rules", 0.0, False
    host_port, model = LOCAL_TIER
    t2_label, elapsed, cold = tier2_classify(prompt, host_port, model)
    if t2_label == "UNSURE":
        return "UNSURE", ROUTES["UNSURE"], "rules", elapsed, cold
    return (t2_label, route_for(t2_label, [t2_label]), f"local:{model}",
            elapsed, False)


def format_line(label: str, route: str, by: str, elapsed_ms: float,
                 cold: bool = False) -> str:
    last_field = "cold" if cold else f"{int(round(elapsed_ms))} ms"
    return (f"PROMPT-CLASS: {label} \u00b7 route {route} \u00b7 by {by} "
            f"\u00b7 {last_field}")


# ---------------------------------------------------------------------
# the generator -- `--build-fixtures <ledger>`. Reads a JUDGMENT-LEDGER-
# shaped table, pulls the quoted ruling cell of each row, writes them as
# RULING fixtures to the `.local` path. Never into the repository.
# ---------------------------------------------------------------------
RULING_CELL_RE = re.compile(r'^\|\s*\*?"(.+?)"\*?\s*\|')


def rulings_from_ledger(text: str) -> list[str]:
    """The quoted ruling cell of each table row, verbatim, in order. A row
    with no quoted cell (an ORACLE-DECLINED row, a lineage citation, a
    skeleton placeholder line still reading literally
    "<their exact words>") does not match and is silently skipped -- this
    generator only ever claims the rows that carry a real quotation."""
    out = []
    for line in text.splitlines():
        m = RULING_CELL_RE.match(line)
        if not m:
            continue
        cell = m.group(1).strip()
        if not cell or cell == "<their exact words>":
            continue
        out.append(cell)
    return out


def build_fixtures(ledger_path: Path, out_path: Path) -> int:
    """Writes {"fixtures": {"RULING": [...]}} to `out_path`, merging with
    whatever that file already holds for OTHER classes/keys (so a repeat
    run does not clobber a hand-written DESIGN/CAPTURE/PRESENCE/QUESTION
    overlay someone put in the same file). Returns the count written."""
    text = ledger_path.read_text(encoding="utf-8")
    rulings = rulings_from_ledger(text)
    existing = _read_json(out_path) if out_path.is_file() else {}
    existing.setdefault("classes", {})
    existing.setdefault("fixtures", {})
    existing["fixtures"]["RULING"] = [
        {"text": r, "reason": "from the ledger's own quoted ruling cell"}
        for r in rulings
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    return len(rulings)


def cmd_build_fixtures(ledger_arg: str) -> int:
    ledger_path = Path(ledger_arg)
    if not ledger_path.is_file():
        print(f"ABORT: no ledger at {ledger_path}", file=sys.stderr)
        return 2
    out_path = _resolve_fixtures_path()
    if out_path is None:
        print("ABORT: kit.config sets no PROMPT_CLASS_FIXTURES path",
              file=sys.stderr)
        return 2
    count = build_fixtures(ledger_path, out_path)
    print(f"{count} RULING fixture(s) written to {out_path}")
    return 0


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    if "--build-fixtures" in argv:
        i = argv.index("--build-fixtures")
        if i + 1 >= len(argv):
            print("usage: --build-fixtures <ledger-path>", file=sys.stderr)
            return 2
        return cmd_build_fixtures(argv[i + 1])
    if LOCAL_TIER_DIAGNOSTIC:
        print(f"PROMPT-CLASS: LOCAL_TIER is set but unusable: "
              f"{LOCAL_TIER_DIAGNOSTIC}", file=sys.stderr)
    use_local = "--no-local" not in argv
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}
    prompt = payload.get("prompt", "") if isinstance(payload, dict) else ""
    if not isinstance(prompt, str):
        prompt = ""
    if prompt.strip() == "":
        print(format_line("UNSURE", ROUTES["UNSURE"], "rules", 0.0))
        return 0
    label, route, by, elapsed, cold = classify(prompt, use_local=use_local)
    print(format_line(label, route, by, elapsed, cold))
    return 0


# ---------------------------------------------------------------- selftest
def _tier1_accuracy(class_data: dict) -> tuple[dict, list]:
    per_class: dict[str, list[int]] = {}
    misses = []
    fixtures = class_data.get("fixtures") or {}
    for label, phrases in fixtures.items():
        if label not in CLASS_ORDER:
            continue
        if not isinstance(phrases, list):
            continue
        got_ok = 0
        for item in phrases:
            text = item.get("text") if isinstance(item, dict) else item
            out_label, _ = classify_tier1(text, class_data)
            if out_label == label:
                got_ok += 1
            else:
                misses.append((label, text, out_label))
        per_class[label] = [got_ok, len(phrases)]
    return per_class, misses


def selftest() -> int:
    ok = [True]
    ran = [0]

    def check(name, cond, detail=""):
        ran[0] += 1
        mark = "pass" if cond else "FAIL"
        print(f"  {mark}  {name}" + (f"  {detail}" if detail and not cond else ""))
        if not cond:
            ok[0] = False

    print("hook_prompt_class selftest")

    # (a) every template fixture labels correctly at tier 1.
    per_class, misses = _tier1_accuracy(CLASS_DATA)
    for label, (hits, total) in sorted(per_class.items()):
        frac = hits / total if total else 0.0
        check(f"(a) {label} template fixtures label correctly: "
              f"{hits}/{total} ({frac:.1%})", hits == total, f"{hits}/{total}")
    if misses:
        print("  misses:")
        for label, phrase, got in misses:
            print(f"    expected {label}, got {got or 'EMPTY'!r}: {phrase!r}")

    # (b) inverting the RULING list into DESIGN's role reds the run.
    inverted = json.loads(json.dumps(CLASS_DATA))  # deep copy, no mutation of CLASS_DATA
    classes = inverted.get("classes") or {}
    ruling_words = (classes.get("RULING") or {}).get("words") or []
    classes.setdefault("DESIGN", {})["words"] = ruling_words
    classes.setdefault("RULING", {})["words"] = []
    inv_per_class, _ = _tier1_accuracy(inverted)
    r_hits, r_total = inv_per_class.get("RULING", [0, 1])
    check("(b) forced red: inverting RULING's words into DESIGN's slot "
          "reds RULING accuracy",
          (r_hits / r_total if r_total else 0.0) < 1.0, f"{r_hits}/{r_total}")

    # (c) a LOCAL_TIER naming a non-loopback host is refused before any
    # call -- widened past one plain foreign host (finding 2): the
    # userinfo form (finding 1's own failing input, a placeholder host),
    # a non-loopback bracketed IPv6 literal, a trailing-dot host and a
    # scheme-prefixed value. Each must be refused with zero call attempts.
    c_cases = {
        "a plain foreign host": "10.0.0.5:11434",
        "the userinfo form (finding 1's failing input)":
            "localhost:11434@foreign-host.invalid",
        "a non-loopback bracketed IPv6 literal": "[2001:db8::1]:11434",
        "a trailing-dot host": "localhost.:11434",
        "a scheme-prefixed value": "http:",  # what parse_local_tier leaves
                                              # of "http://127.0.0.1:11434"
    }
    for case_name, host_port in c_cases.items():
        before = CALL_ATTEMPTS[0]
        bad_label, _, _ = tier2_classify("approve the plan", host_port,
                                          "some-model")
        check(f"(c) forced red: {case_name} is refused before any call",
              bad_label == "UNSURE" and CALL_ATTEMPTS[0] == before,
              (host_port, bad_label, CALL_ATTEMPTS[0] - before))
    print(f"  (c) case count: {len(c_cases)}")

    # (3) the URL parse admits the bracketed IPv6 loopback form, which the
    # old first-colon split could not (README's own claim); the bare,
    # unbracketed form is not admitted, because "::1:11434" is ambiguous
    # host:port syntax that no URL parser can split -- fail-closed, not a
    # defect, and the README says "bracketed" for exactly this reason.
    # Predicate only, never a connection (the network rule): admission is
    # proved by the predicate and by `urlsplit`, exactly like a refusal.
    check("(3) the bracketed IPv6 loopback is admitted by the predicate",
          _is_loopback_host_port("[::1]:11434"))
    check("(3) the bare, unbracketed IPv6 loopback cannot be expressed as "
          "host:port and is refused fail-closed, never admitted",
          not _is_loopback_host_port("::1:11434"))

    # (d) LOCAL_TIER NONE never attempts a call (assert by the counter).
    before = CALL_ATTEMPTS[0]
    saved_local, saved_enabled = LOCAL_TIER, LOCAL_ENABLED
    globals()["LOCAL_TIER"], globals()["LOCAL_ENABLED"] = None, False
    try:
        classify("this residue prompt matches no tier-1 class at all",
                 use_local=True)
    finally:
        globals()["LOCAL_TIER"], globals()["LOCAL_ENABLED"] = saved_local, saved_enabled
    check("(d) LOCAL_TIER NONE never attempts a call",
          CALL_ATTEMPTS[0] == before, CALL_ATTEMPTS[0] - before)

    # (e) an empty prompt, non-JSON garbage and residue each read UNSURE
    # and exit 0 -- driven through main() itself with stubbed stdin, not
    # just through classify(), so the exit code main() actually returns
    # is the thing asserted (finding 4: the old check never executed
    # main()'s empty-prompt branch at all).
    import contextlib
    import io

    def _run_main(stdin_text: str) -> tuple[int, str]:
        buf = io.StringIO()
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        try:
            with contextlib.redirect_stdout(buf):
                rc = main(["--no-local"])
        finally:
            sys.stdin = old_stdin
        return rc, buf.getvalue()

    for case_name, stdin_text in (
        ("an empty prompt", '{"prompt": ""}'),
        ("non-JSON garbage", "not json at all {{{"),
        ("residue (no tier-1 class matches)",
         '{"prompt": "this residue prompt matches no tier-1 class at all"}'),
    ):
        rc, out = _run_main(stdin_text)
        check(f"(e) {case_name} through main(): exit 0, UNSURE",
              rc == 0 and "PROMPT-CLASS: UNSURE" in out, (rc, out.strip()))

    # (f) the generator on a synthetic ledger writes the expected count to
    # a temp .local path and nothing into the tree.
    import shutil
    import subprocess
    import tempfile

    def _git_porcelain(root: Path) -> str | None:
        """A snapshot, not an assertion by itself: `git status --porcelain`
        read from CFG_DIR, the box's own root, so this floor holds whether
        or not the module directory is the only place a regression could
        write (finding 5: the old check watched only `HERE`, never the
        directory the generator's real default target resolves against).
        Any failure to read one (not a repo, git missing) returns None,
        treated by the caller as "cannot prove it," never as a pass."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], cwd=str(root),
                capture_output=True, text=True, timeout=10)
        except Exception:
            return None
        return result.stdout if result.returncode == 0 else None

    scratch = Path(tempfile.mkdtemp(prefix="promptclass-selftest-"))
    try:
        ledger = scratch / "JUDGMENT-LEDGER.md"
        ledger.write_text(
            '| Ruling | Landed in | Enforcing check | Status |\n'
            '|---|---|---|---|\n'
            '| *"adopt the routing line"* | x | y | **CHECKED** |\n'
            '| *"merge the gauge basis"* | x | y | **CHECKED** |\n'
            '| ORACLE-DECLINED: no quoted cell here | round 1 | not built | '
            '**ORACLE-DECLINED** |\n'
            '| *"<their exact words>"* | — | — | **PENDING** |\n',
            encoding="utf-8")
        out_path = scratch / "prompt_class.local.json"
        before_listing = sorted(p.name for p in HERE.iterdir())
        before_git = _git_porcelain(CFG_DIR)
        count = build_fixtures(ledger, out_path)
        after_listing = sorted(p.name for p in HERE.iterdir())
        after_git = _git_porcelain(CFG_DIR)
        check("(f) the generator writes the expected count (2, skipping "
              "the ORACLE-DECLINED and placeholder rows)", count == 2, count)
        check("(f) the generator wrote to the temp .local path",
              out_path.is_file())
        check("(f) nothing changed in this module's own directory",
              before_listing == after_listing)
        check("(f) nothing changed in the box's tracked tree "
              "(git status --porcelain, read from CFG_DIR)",
              before_git is not None and before_git == after_git,
              (before_git, after_git))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    # (6) a mistyped LOCAL_TIER is diagnosed by name, never dropped silently.
    diag_cases = {
        "malformed": ("no-slash-here", "malformed"),
        "userinfo": ("localhost:11434@foreign-host.invalid/some-model",
                     "userinfo"),
        "scheme": ("http://127.0.0.1:11434/llama3", "scheme"),
        "non-loopback": ("10.0.0.5:11434/some-model", "non-loopback"),
    }
    for reason, (raw, keyword) in diag_cases.items():
        got = _diagnose_local_tier(raw)
        check(f"(6) LOCAL_TIER diagnostic names the reason: {reason}",
              bool(got) and keyword in got, got)
    check("(6) a usable LOCAL_TIER has no diagnostic",
          _diagnose_local_tier("127.0.0.1:11434/llama3") is None)
    check("(6) LOCAL_TIER unset/NONE has no diagnostic",
          _diagnose_local_tier(None) is None)

    # (7) FLOOR, the kit's own vacuous-gate rule: a missing or empty
    # template reads FAIL here, never PASS, because `_read_json` swallows
    # every failure and would otherwise let (a) simply vanish with nothing
    # red to show for it. Observed floor today: five classes, ten fixtures
    # each -- a number that should only ever rise.
    fixtures = CLASS_DATA.get("fixtures") or {}
    classes_present = sorted(set(CLASS_ORDER) & set(fixtures))
    check(f"(7) FLOOR: five classes present ({len(classes_present)}/5)",
          len(classes_present) == 5, classes_present)
    for label in CLASS_ORDER:
        n = len(fixtures.get(label) or [])
        check(f"(7) FLOOR: {label} carries at least ten fixtures ({n})",
              n >= 10, n)

    # (7) FLOOR: a minimum check count, so a collapsed run (an import that
    # silently skips a whole section) cannot read PASS over near-nothing.
    # Observed 33 today; this number should only ever rise.
    MIN_CHECKS = 30
    check(f"(7) FLOOR: at least {MIN_CHECKS} checks ran ({ran[0]})",
          ran[0] >= MIN_CHECKS, ran[0])

    print()
    print(f"PROMPT CLASS SELFTEST: {'PASS' if ok[0] else 'FAIL'}")
    return 0 if ok[0] else 1


if __name__ == "__main__":
    raise SystemExit(main())
