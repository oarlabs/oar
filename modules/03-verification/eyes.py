#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eyes.py -- a screenshot instrument and a look-quality loop, level 1.

Stock Python, no dependency, the browser already on the box. Three verbs an
agent runs, plus a fourth that `verify.py`'s `eyes` gate shells out to:

    python eyes.py shot --src <file-or-url> --out <dir> [--viewports W1xH1,...]
    python eyes.py ears --src <file-or-url> --out <dir>   # shot + console capture
    python eyes.py look --out <dir>                        # print the catalog
    python eyes.py look --fixture                          # calibration only
    python eyes.py gate <out-dir>                           # the verify.py gate
    python eyes.py --selftest

==========================================================================
DECISION 6, THE ASK BEFORE THE LOCAL BROWSER (binding, not a suggestion)
==========================================================================
This tool NEVER opens the owner's own browser or the owner's own profile.
Every render, every version probe, every command of any kind this file
issues to a Chromium binary carries a fresh, isolated `--user-data-dir`
under the output folder and `--headless=new`, unconditionally -- there is
no flag anywhere in this file's argument parser that removes either one
(`--selftest` proves it by reading the argv this file actually builds).

When the isolated path cannot do the job -- a page that needs a login, or a
session only the owner's own profile holds, or a render the isolated path
cannot produce -- `shot` does not fall back to the owner's browser. It
stops. The ask is to the owner, at his own prompt, by a person: tell him
which page, why the isolated render failed, and what the local browser
would expose, and let him decide. There is no `--use-local-profile` flag
and there will not be one; the isolation is structural, not a default that
a determined caller can override.
==========================================================================

WHAT THIS DOES NOT PROVE. A pixel check cannot find cut-off text -- the
mechanical half here (PNG exists, fresh against the source's sha, the
right dimensions, not blank) needs no model and runs first, but it cannot
answer any of the ten catalog questions in `look`. Those are for the
agent reading the PNG and the ears file, by eye. `look` prints the
catalog as a fixed report shape; it does not judge the image itself.
Freshness against a URL source is out of scope for the same reason a
re-fetch would be a second render, not a check: a URL source is recorded
in the manifest with no sha, and staleness is only checked for a local
file source. See `EYES.md` for the full scope statement.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import inspect
import json
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

# ==========================================================================
# THE CATALOG (the plan's section 4, the standard quality loop)
# ==========================================================================
CATALOG = [
    (1, "Cut-off text: an ellipsis, a clipped glyph at an edge, a first or "
        "last character missing."),
    (2, "Overflow: a scrollbar where the design has none; content past the "
        "viewport edge."),
    (3, "Overlap: one element drawn over another."),
    (4, "Alignment: a row whose items do not share a baseline; a grid with "
        "a ragged column; a control block that does not line up with its "
        "label."),
    (5, "Reflow on state change: rendered twice (idle and lit, empty and "
        "full), elements that moved between the two."),
    (6, "Contrast: text or a state color unreadable against its ground."),
    (7, "Indistinguishable labels: two elements that read the same after "
        "truncation."),
    (8, "Empty regions: a panel with nothing in it; a blank render."),
    (9, "The wrong state rendered: a lamp color that disagrees with the "
        "data the page claims."),
    (10, "The ears: any JavaScript error, failed fetch or warning in the "
         "log."),
]

# The fixture's known, documented calibration answers (the plan's section
# 4: "Tonight's before screenshots answer yes to 1, 2, 5 and 7"). This is a
# printed REFERENCE for a reader, not a judgment eyes.py computes -- the
# tool has no vision.
FIXTURE_EXPECTED_YES = {1, 2, 5, 7}
FIXTURE_SOURCE_REL = "modules/03-verification/examples/eyes-fixture/before-1280.png"

DEFAULT_VIEWPORT_SPEC = "1280x720,1920x1080,400x850"

# ==========================================================================
# BROWSER DISCOVERY
# ==========================================================================
BROWSER_NAMES = [
    "msedge", "msedge.exe", "chrome", "chrome.exe",
    "google-chrome", "google-chrome-stable", "chromium", "chromium.exe",
    "chromium-browser",
]

WIN_DIRS = [
    r"{pf}\Microsoft\Edge\Application\msedge.exe",
    r"{pf86}\Microsoft\Edge\Application\msedge.exe",
    r"{pf}\Google\Chrome\Application\chrome.exe",
    r"{pf86}\Google\Chrome\Application\chrome.exe",
    r"{pf}\Chromium\Application\chrome.exe",
]
MAC_DIRS = [
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]
LINUX_DIRS = [
    "/usr/bin/microsoft-edge", "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable", "/usr/bin/chromium",
    "/usr/bin/chromium-browser", "/snap/bin/chromium",
]


def _standard_dirs():
    if os.name == "nt":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        return [Path(p.format(pf=pf, pf86=pf86)) for p in WIN_DIRS]
    if platform.system() == "Darwin":
        return [Path(p) for p in MAC_DIRS]
    return [Path(p) for p in LINUX_DIRS]


def _kit_config_browser_path(start: Path) -> str | None:
    """Reads BROWSER_PATH out of kit.config / kit.config.local, the same
    overlay verify.py's own read_kit_config uses (committed file first,
    local overlay second)."""
    for d in [start, *start.parents]:
        cfg = d / "kit.config"
        if cfg.is_file():
            val = None
            for path in (cfg, cfg.with_name("kit.config.local")):
                if not path.is_file():
                    continue
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.split("#", 1)[0].strip()
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() == "BROWSER_PATH":
                            val = v.strip()
            return val
    return None


def find_browser(explicit: str | None = None,
                  search_start: Path | None = None) -> Path | None:
    """Discovery order, per the plan: an explicit override (for testing and
    for a pinned install), then PATH, then the standard per-OS program
    folders, then kit.config's BROWSER_PATH. An explicit override that does
    not exist is NO-BROWSER -- it does not fall through to the rest of the
    search, because a caller who named a path meant that path."""
    if explicit is not None:
        p = Path(explicit)
        return p if p.is_file() else None
    for name in BROWSER_NAMES:
        w = shutil.which(name)
        if w:
            return Path(w)
    for p in _standard_dirs():
        if p.is_file():
            return p
    cfg_path = _kit_config_browser_path(search_start or Path(__file__).resolve())
    if cfg_path:
        p = Path(cfg_path)
        if p.is_file():
            return p
    return None


# ==========================================================================
# THE ISOLATED RENDER (pure command-builder; see --selftest section E)
# ==========================================================================
def host_resolver_rule(allow_hosts) -> str:
    """Network is blocked by default (plan decision 5): a host-resolver
    rule that resolves nothing. `allow_hosts` punches named exceptions."""
    base = "MAP * 0.0.0.0"
    if not allow_hosts:
        return base
    return base + "," + ",".join(f"EXCLUDE {h}" for h in allow_hosts)


def build_shot_cmd(browser, target: str, width: int, height: int,
                    out_png, user_data_dir, scale: int = 1,
                    resolver_rule: str = "MAP * 0.0.0.0",
                    virtual_time_budget_ms: int = 4000,
                    extra_logging: bool = False) -> list:
    """PURE: builds the argv for one headless render and returns it; makes
    no call, touches no filesystem. `--headless=new` and an ABSOLUTE
    `--user-data-dir` are hardcoded into the return value -- there is no
    parameter on this function, and no flag on the CLI that calls it, that
    can omit either one. That is the guarantee --selftest section E reads
    back out of this function's own signature and its own output."""
    return [
        str(browser),
        "--headless=new",
        f"--user-data-dir={Path(user_data_dir).resolve()}",
        f"--window-size={width},{height}",
        f"--force-device-scale-factor={scale}",
        "--hide-scrollbars",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--host-resolver-rules={resolver_rule}",
        f"--virtual-time-budget={virtual_time_budget_ms}",
        f"--screenshot={Path(out_png).resolve()}",
    ] + (["--enable-logging=stderr", "--v=1"] if extra_logging else []) + [target]


def file_version(path: Path) -> str:
    """The Chromium binary's version, read from its own FILE METADATA --
    never by launching it.

    MEASURED ON THIS WORKSTATION: `--headless=new` combined with any
    exit-and-print flag (`--version`, `--product-version`) does not return
    -- confirmed to 90s. It is not specific to `--version`: headless=new
    with no `--screenshot`/`--dump-dom` (nothing telling it to do one thing
    and exit) simply does not exit, on this box's installed Edge
    (153.0.4234.32), with or without the network blocked. A tool that
    launched a browser for every render's version stamp would hang on this
    workstation every time, so it does not: `build_version_cmd` above still
    exists and is still proven isolated by --selftest, for a caller who
    wants a live probe and can bound it, but the render path does not call
    it by default.

    On Windows this reads the PE VERSIONINFO resource via ctypes
    (version.dll, stock, no dependency). Elsewhere it falls back to a
    version-looking sibling directory name, which is how Edge/Chrome
    installs on Linux/macOS commonly ship the versioned payload. Neither
    path is a guess presented as a fact: an unreadable version says so."""
    if os.name == "nt":
        try:
            ver = ctypes.windll.version  # type: ignore[attr-defined]
            size = ver.GetFileVersionInfoSizeW(str(path), None)
            if not size:
                return "unknown (no version resource on the binary)"
            buf = ctypes.create_string_buffer(size)
            ver.GetFileVersionInfoW(str(path), 0, size, buf)
            r = ctypes.c_void_p()
            rlen = ctypes.c_uint()
            if not ver.VerQueryValueW(buf, "\\", ctypes.byref(r), ctypes.byref(rlen)):
                return "unknown (VerQueryValueW found nothing)"

            class _FixedFileInfo(ctypes.Structure):
                _fields_ = [
                    ("dwSignature", ctypes.c_uint32),
                    ("dwStrucVersion", ctypes.c_uint32),
                    ("dwFileVersionMS", ctypes.c_uint32),
                    ("dwFileVersionLS", ctypes.c_uint32),
                    ("dwProductVersionMS", ctypes.c_uint32),
                    ("dwProductVersionLS", ctypes.c_uint32),
                    ("dwFileFlagsMask", ctypes.c_uint32),
                    ("dwFileFlags", ctypes.c_uint32),
                    ("dwFileOS", ctypes.c_uint32),
                    ("dwFileType", ctypes.c_uint32),
                    ("dwFileSubtype", ctypes.c_uint32),
                    ("dwFileDateMS", ctypes.c_uint32),
                    ("dwFileDateLS", ctypes.c_uint32),
                ]

            info = ctypes.cast(r, ctypes.POINTER(_FixedFileInfo)).contents
            ms, ls = info.dwFileVersionMS, info.dwFileVersionLS
            return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except Exception as e:
            return f"unknown (Windows version-resource read failed: {e!r})"
    try:
        for sib in path.resolve().parent.iterdir():
            if sib.is_dir() and re.fullmatch(r"\d+(\.\d+){2,3}", sib.name):
                return sib.name
    except Exception:
        pass
    return "unknown (no file-metadata probe available on this platform)"


def build_version_cmd(browser, user_data_dir) -> list:
    """PURE, same guarantee: a version probe is not exempt from isolation.
    Also carries the network-blocked default (decision 5) and disables the
    component updater -- measured on this workstation: a version probe
    without either one hung past 30s, because a fresh, offline-blocked
    profile still tries to reach the component-update service before Edge
    prints its version and exits, and the request never resolves."""
    return [str(browser), "--headless=new",
            f"--user-data-dir={Path(user_data_dir).resolve()}",
            "--host-resolver-rules=MAP * 0.0.0.0",
            "--disable-component-update", "--version"]


# ==========================================================================
# A MINIMAL PNG DECODER (stock zlib + struct; no Pillow, no dependency)
# ==========================================================================
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter_line(ftype, line: bytearray, prev: bytearray, bpp: int):
    n = len(line)
    if ftype == 0:
        return
    if ftype == 1:  # Sub
        for i in range(bpp, n):
            line[i] = (line[i] + line[i - bpp]) & 0xFF
    elif ftype == 2:  # Up
        for i in range(n):
            line[i] = (line[i] + prev[i]) & 0xFF
    elif ftype == 3:  # Average
        for i in range(n):
            a = line[i - bpp] if i >= bpp else 0
            line[i] = (line[i] + ((a + prev[i]) // 2)) & 0xFF
    elif ftype == 4:  # Paeth
        for i in range(n):
            a = line[i - bpp] if i >= bpp else 0
            c = prev[i - bpp] if i >= bpp else 0
            line[i] = (line[i] + _paeth(a, prev[i], c)) & 0xFF
    else:
        raise ValueError(f"unsupported PNG filter type {ftype}")


def decode_png(data: bytes):
    """(width, height, pixel_bytes, channels). Supports 8-bit depth,
    non-interlaced, color types 0/2/4/6 (gray, rgb, gray+alpha, rgba) --
    what Chromium's `--screenshot` writes. Raises ValueError on anything
    else (palette, 16-bit, interlaced): the caller treats a raised error as
    'cannot confirm', never as a silent pass."""
    if data[:8] != PNG_SIG:
        raise ValueError("not a PNG (bad signature)")
    pos = 8
    width = height = bitdepth = colortype = interlace = None
    idat = bytearray()
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8].decode("ascii", "replace")
        chunk = data[pos + 8:pos + 8 + length]
        pos += 8 + length + 4
        if ctype == "IHDR":
            width, height, bitdepth, colortype, _, _, interlace = struct.unpack(
                ">IIBBBBB", chunk)
        elif ctype == "IDAT":
            idat += chunk
        elif ctype == "IEND":
            break
    if width is None:
        raise ValueError("no IHDR chunk")
    if bitdepth != 8:
        raise ValueError(f"unsupported bit depth {bitdepth}")
    if interlace != 0:
        raise ValueError("unsupported: interlaced PNG")
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(colortype)
    if channels is None:
        raise ValueError(f"unsupported color type {colortype}")
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    out = bytearray(stride * height)
    prev = bytearray(stride)
    p = 0
    for row in range(height):
        ftype = raw[p]
        p += 1
        line = bytearray(raw[p:p + stride])
        p += stride
        _unfilter_line(ftype, line, prev, channels)
        out[row * stride:(row + 1) * stride] = line
        prev = line
    return width, height, bytes(out), channels


def is_blank(pixels: bytes, channels: int, threshold: int = 4,
             sample_stride: int = 97) -> bool:
    """Sampled, not exhaustive (large PNGs stay cheap to check): every
    `sample_stride`-th pixel is folded into a running min/max per channel;
    a spread at or under `threshold` across every sampled channel reads as
    one color across the frame -- blank, or near enough to it."""
    n = len(pixels)
    if n < channels:
        return True
    lo = list(pixels[0:channels])
    hi = list(pixels[0:channels])
    step = channels * max(1, sample_stride)
    i = 0
    while i + channels <= n:
        for c in range(channels):
            v = pixels[i + c]
            if v < lo[c]:
                lo[c] = v
            if v > hi[c]:
                hi[c] = v
        i += step
    return max(h - l for h, l in zip(hi, lo)) <= threshold


def make_test_png(w: int, h: int, pixel_fn, channels: int = 3) -> bytes:
    """--selftest only: builds a minimal, valid, non-interlaced 8-bit PNG
    in memory, so the forced reds below need no browser and no filesystem."""
    colortype = {1: 0, 3: 2, 4: 6}[channels]
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter type None
        for x in range(w):
            raw.extend(pixel_fn(x, y))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, colortype, 0, 0, 0)
    idat = zlib.compress(bytes(raw), 9)

    def chunk(ctype, payload):
        body = ctype.encode("ascii") + payload
        return (struct.pack(">I", len(payload)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    return PNG_SIG + chunk("IHDR", ihdr) + chunk("IDAT", idat) + chunk("IEND", b"")


def inspect_png(png: Path, want_w: int, want_h: int) -> dict:
    """{'exists','dims_ok','not_blank'} -- the mechanical half of the gate,
    filesystem-touching. The pure decode/blank logic above is what
    --selftest exercises without a filesystem."""
    if not png.is_file():
        return {"exists": False, "dims_ok": False, "not_blank": False}
    try:
        w, h, pixels, channels = decode_png(png.read_bytes())
    except Exception:
        return {"exists": True, "dims_ok": False, "not_blank": False}
    return {"exists": True, "dims_ok": (w == want_w and h == want_h),
            "not_blank": not is_blank(pixels, channels)}


# ==========================================================================
# REPO-ROOT AND HASHING HELPERS
# ==========================================================================
def repo_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / ".git").exists():
            return d
    return start


def rel_to_repo(p: Path, root: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(p)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_viewports(spec: str):
    out = []
    for tok in (spec or DEFAULT_VIEWPORT_SPEC).split(","):
        tok = tok.strip()
        m = re.fullmatch(r"(\d+)x(\d+)", tok)
        if not m:
            raise SystemExit(f"bad viewport {tok!r}, want WxH (e.g. 1280x720)")
        w, h = int(m.group(1)), int(m.group(2))
        out.append((f"{w}x{h}", w, h))
    return out


# MEASURED ON THIS WORKSTATION, against a planted probe page (console.error,
# console.warn, a failed fetch, a missing image): `--enable-logging=stderr
# --v=1` writes Chromium's OWN internal logging (extension activity,
# telemetry, component updater, account reconciliation) at the same ERROR
# and WARNING severities a naive substring match would also catch -- the
# first cut of this function matched all of it. The page's own
# console.error/console.warn/uncaught-exception output is tagged
# differently and distinctly: `INFO:CONSOLE:<line>] "<message>", source:
# <url> (<line>)`. A SECOND false-positive source sits behind that same
# tag: Edge's own built-in extensions (a coupons manager, a protocol-launch
# handler) also log through `CONSOLE:` from a `chrome-extension://` source,
# so the tag alone is not enough -- the source must not be an extension.
CONSOLE_LINE = re.compile(
    r":CONSOLE:\d+\]\s+(?P<msg>.*?),\s+source:\s+(?P<source>\S+)\s+\((?P<line>\d+)\)\s*$")


def extract_console(log_path: Path, console_path: Path) -> list:
    """RESIDUAL, disclosed rather than hidden: this reliably surfaces a
    page's own console.error, console.warn and uncaught exceptions, because
    Chromium tags all three through the same CONSOLE line. It does NOT
    reliably surface a bare failed resource load (a missing image, a
    blocked fetch) for a `file://` source on this Chromium build -- none
    printed a CONSOLE line in the planted probe unless the page's own
    script routed the failure to console itself. Catalog item 10 is
    therefore scoped to what Chromium actually reports, and EYES.md states
    this rather than implying a fuller net than the tool casts."""
    text = (log_path.read_text(encoding="utf-8", errors="replace")
            if log_path.is_file() else "")
    hits = []
    for ln in text.splitlines():
        m = CONSOLE_LINE.search(ln)
        if m and not m.group("source").startswith("chrome-extension://"):
            hits.append(ln)
    console_path.write_text(
        ("\n".join(hits) + "\n") if hits else
        "no JavaScript error, failed resource load or warning captured\n",
        encoding="utf-8")
    return hits


# ==========================================================================
# shot / ears
# ==========================================================================
def cmd_shot(args) -> int:
    root = repo_root(Path(__file__).resolve())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    src = args.src
    is_url = re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", src) is not None
    src_path = None if is_url else Path(src).resolve()
    if not is_url and not src_path.is_file():
        print(f"EYES: source not found: {src}", file=sys.stderr)
        return 2

    manifest = {
        "source": src if is_url else rel_to_repo(src_path, root),
        "source_sha256": None if is_url else sha256_file(src_path),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scale": args.scale,
        "network": {"blocked_by_default": True,
                    "allowed_hosts": list(args.allow_hosts or [])},
        "viewports": [],
    }

    browser = find_browser(args.browser, search_start=root)
    if browser is None:
        manifest["browser"] = None
        (out / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")
        print("EYES: state NO-BROWSER -- no Chromium found on PATH, in the "
              "standard program folders, or at kit.config's BROWSER_PATH. "
              "No render attempted. This is NOT-RUN, never green; see "
              "EYES.md decision 6 before pointing this at a real browser "
              "profile.")
        return 3

    # file_version() reads the binary's own metadata -- no browser command,
    # no isolation flags needed, none issued. See file_version()'s docstring
    # for the measured reason this tool does not launch Chromium for a
    # version stamp: --headless=new with no exit-and-print flag does not
    # exit, confirmed to 90s on this workstation.
    ver_text = file_version(browser)
    # The manifest is public-kit output: `browser.path` used to carry the
    # binary's absolute install path (a drive letter), which is exactly
    # what this file's own Rules section forbids in an added line. The name
    # alone is enough provenance -- which Chromium, at which version.
    manifest["browser"] = {"name": Path(browser).name, "version": ver_text}

    rule = host_resolver_rule(args.allow_hosts)
    target = src if is_url else str(src_path)
    stem = args.stem or (Path(src).stem if not is_url else "shot")
    ok_all = True
    for name, w, h in parse_viewports(args.viewports):
        udd = out / "profiles" / f"{name}-{os.getpid()}-{int(time.time()*1000)}"
        udd.mkdir(parents=True, exist_ok=True)
        png = out / f"{stem}-{name}.png"
        cmd = build_shot_cmd(browser, target, w, h, png, udd, args.scale, rule,
                              args.virtual_time_budget, extra_logging=args.ears)
        print("QUOTED BROWSER COMMAND:", " ".join(str(c) for c in cmd))
        log_path = out / f"{stem}-{name}.stderr.log"
        try:
            p = subprocess.run(cmd, capture_output=True, timeout=args.timeout)
            log_path.write_bytes((p.stdout or b"") + (p.stderr or b""))
            rc = p.returncode
        except subprocess.TimeoutExpired as e:
            log_path.write_bytes((e.stdout or b"") + (e.stderr or b""))
            rc = -1
        entry = {"name": name, "width": w, "height": h, "png": png.name, "rc": rc}
        if args.ears:
            console_path = out / f"{stem}-{name}.console.txt"
            extract_console(log_path, console_path)
            entry["console"] = console_path.name
        manifest["viewports"].append(entry)
        ok_all = ok_all and rc == 0 and png.is_file()

    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"EYES: wrote {len(manifest['viewports'])} viewport(s) to {out} "
          f"({'ok' if ok_all else 'one or more renders failed, see logs'})")
    return 0 if ok_all else 1


def cmd_ears(args) -> int:
    args.ears = True
    return cmd_shot(args)


# ==========================================================================
# look
# ==========================================================================
def print_catalog_report(viewport_label, evidence, expected_yes=None,
                          calibration=False):
    print(f"\n=== EYES CATALOG -- viewport {viewport_label} -- "
          f"evidence {evidence} ===")
    print("| # | Question | Yes/No | Locator |")
    print("|---|---|---|---|")
    for i, q in CATALOG:
        if calibration:
            yn = "yes" if i in expected_yes else "no"
            print(f"| {i} | {q} | {yn} (expected, calibration) | -- |")
        else:
            print(f"| {i} | {q} | <fill in> | <fill in> |")


def cmd_look(args) -> int:
    if args.fixture:
        print_catalog_report("1280x720 (fixture)", FIXTURE_SOURCE_REL,
                              FIXTURE_EXPECTED_YES, calibration=True)
        print(f"\nCALIBRATION -- expected yes: "
              f"{', '.join(str(i) for i in sorted(FIXTURE_EXPECTED_YES))}. "
              f"A model that misses one of these on the fixture is red "
              f"before it looks at any real page.")
        return 0
    out = Path(args.out)
    mf_path = out / "manifest.json"
    if not mf_path.is_file():
        print(f"EYES: state UNSEEN -- no manifest.json at {out}; run "
              f"`shot` first.")
        return 2
    manifest = json.loads(mf_path.read_text(encoding="utf-8"))
    for vp in manifest.get("viewports", []):
        print_catalog_report(vp["name"], vp["png"])
    print(
        "\nSave your answers as look-report.json beside the manifest:\n"
        '{"answers": {"<viewport>": {"<item#>": "yes"|"no", ...}, ...}}\n'
        "A `yes` becomes a punch item in the punch-list template's row "
        "shape, with the evidence column naming the PNG.")
    return 0


# ==========================================================================
# THE PURE GATE-JUDGING LAYER (mirrors verify.py's own separation, so
# --selftest can exercise every branch with no subprocess and no filesystem)
# ==========================================================================
def judge_state(manifest, look_report, checks, stale):
    """(state, shots, viewports, catalog_total, catalog_answered, yes,
    detail). PURE given its four arguments."""
    if manifest is None:
        return ("UNSEEN", 0, "", 0, 0, 0, "no manifest.json found")
    if manifest.get("browser") is None:
        return ("NO-BROWSER", 0, "", 0, 0, 0, "shot recorded no browser found")
    vps = manifest.get("viewports", [])
    names = [v["name"] for v in vps]
    shots = len(vps)
    for v in vps:
        c = checks.get(v["name"],
                        {"exists": False, "dims_ok": False, "not_blank": False})
        if not c["exists"]:
            return ("UNSEEN", shots, ",".join(names), 0, 0, 0,
                     f"PNG missing for viewport {v['name']}")
        if not c["dims_ok"]:
            return ("UNSEEN", shots, ",".join(names), 0, 0, 0,
                     f"PNG dimensions do not match viewport {v['name']}")
        if not c["not_blank"]:
            return ("UNSEEN", shots, ",".join(names), 0, 0, 0,
                     f"PNG for {v['name']} is blank or near-blank")
    if stale:
        return ("STALE", shots, ",".join(names), 0, 0, 0,
                 "manifest is stale against the source's sha")
    if look_report is None:
        return ("UNSEEN", shots, ",".join(names), 0, 0, 0,
                 "no look-report.json -- the catalog has not been answered")
    total = answered = yes = 0
    for vname in names:
        va = (look_report.get("answers") or {}).get(vname, {})
        for i, _ in CATALOG:
            total += 1
            v = va.get(str(i))
            if v in ("yes", "no"):
                answered += 1
                if v == "yes":
                    yes += 1
    if answered < total:
        return ("UNSEEN", shots, ",".join(names), total, answered, yes,
                 "the catalog is not fully answered")
    return ("SEEN", shots, ",".join(names), total, answered, yes, "")


def format_gate_line(state, shots, viewports, total, answered, yes) -> str:
    return (f"EYES: state {state}; shots {shots}; viewports {viewports}; "
            f"catalog {answered}/{total} answered; yes {yes}")


def compute_gate_line(out: Path) -> str:
    root = repo_root(out.resolve())
    mf_path = out / "manifest.json"
    manifest = (json.loads(mf_path.read_text(encoding="utf-8"))
                if mf_path.is_file() else None)
    lr_path = out / "look-report.json"
    look_report = (json.loads(lr_path.read_text(encoding="utf-8"))
                   if lr_path.is_file() else None)
    stale = False
    checks = {}
    if manifest and manifest.get("browser") is not None:
        src_sha = manifest.get("source_sha256")
        if src_sha is not None:
            local = root / manifest.get("source", "")
            if local.is_file():
                if sha256_file(local) != src_sha:
                    stale = True
            else:
                stale = True
        for v in manifest.get("viewports", []):
            checks[v["name"]] = inspect_png(out / v["png"], v["width"], v["height"])
    state, shots, viewports, total, answered, yes, detail = judge_state(
        manifest, look_report, checks, stale)
    line = format_gate_line(state, shots, viewports, total, answered, yes)
    return line + (f" -- {detail}" if detail else "")


def cmd_gate(args) -> int:
    print(compute_gate_line(Path(args.out)))
    return 0


# ==========================================================================
# --selftest
# ==========================================================================
def selftest() -> int:
    ok_all = True
    n = 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    print("=== A. judge_state, the pure gate layer ===")
    check("no manifest -> UNSEEN",
          judge_state(None, None, {}, False)[0], "UNSEEN")
    check("browser None -> NO-BROWSER",
          judge_state({"browser": None}, None, {}, False)[0], "NO-BROWSER")
    manifest_1v = {"browser": {"path": "x", "version": "1"},
                    "viewports": [{"name": "1280x720", "width": 1280,
                                    "height": 720, "png": "a.png"}]}
    check("PNG missing -> UNSEEN (RED, forced on a planted absence)",
          judge_state(manifest_1v, None,
                      {"1280x720": {"exists": False, "dims_ok": False,
                                     "not_blank": False}}, False)[0],
          "UNSEEN")
    check("dims wrong -> UNSEEN (RED, forced on a planted mismatch)",
          judge_state(manifest_1v, None,
                      {"1280x720": {"exists": True, "dims_ok": False,
                                     "not_blank": True}}, False)[0],
          "UNSEEN")
    good_checks = {"1280x720": {"exists": True, "dims_ok": True,
                                  "not_blank": True}}
    check("blank PNG -> UNSEEN (RED, forced on a planted blank)",
          judge_state(manifest_1v, None,
                      {"1280x720": {"exists": True, "dims_ok": True,
                                     "not_blank": False}}, False)[0],
          "UNSEEN")
    check("stale sha -> STALE (RED, forced on a planted staleness)",
          judge_state(manifest_1v, None, good_checks, True)[0], "STALE")
    check("no look-report -> UNSEEN",
          judge_state(manifest_1v, None, good_checks, False)[0], "UNSEEN")
    partial_lr = {"answers": {"1280x720": {"1": "no"}}}
    check("partially answered catalog -> UNSEEN",
          judge_state(manifest_1v, partial_lr, good_checks, False)[0], "UNSEEN")
    full_lr = {"answers": {"1280x720": {str(i): ("yes" if i in (1, 5) else "no")
                                          for i, _ in CATALOG}}}
    st, shots, vps, total, answered, yes, detail = judge_state(
        manifest_1v, full_lr, good_checks, False)
    check("fully answered, 2 yes -> SEEN", st, "SEEN")
    check("...catalog total is 10", total, 10)
    check("...catalog answered is 10", answered, 10)
    check("...yes count is 2", yes, 2)
    check("...green (GREEN, following the RED cases above): the required "
          "line renders",
          format_gate_line(st, shots, vps, total, answered, yes),
          "EYES: state SEEN; shots 1; viewports 1280x720; "
          "catalog 10/10 answered; yes 2")

    print("\n=== B. the PNG decoder and the blank check, on planted "
          "in-memory PNGs (no browser, no filesystem) ===")
    blank_png = make_test_png(20, 20, lambda x, y: (128, 128, 128))
    checker_png = make_test_png(20, 20,
                                 lambda x, y: (255, 255, 255)
                                 if (x // 4 + y // 4) % 2 == 0 else (0, 0, 0))
    bw, bh, bpix, bch = decode_png(blank_png)
    cw, ch, cpix, cch = decode_png(checker_png)
    check("decoded blank PNG dimensions", (bw, bh), (20, 20))
    check("a one-color PNG REDS the blank check", is_blank(bpix, bch), True)
    check("a checkerboard PNG is not blank (the green case)",
          is_blank(cpix, cch), False)
    near_blank = make_test_png(
        10, 10, lambda x, y: (100, 100, 100) if (x, y) != (0, 0) else (101, 100, 100))
    nw, nh, npix, nch = decode_png(near_blank)
    check("a near-blank PNG (1-value spread) still reads blank",
          is_blank(npix, nch, threshold=4), True)

    print("\n=== C. inspect_png end to end, via a temp file (still no "
          "browser) ===")
    with tempfile.TemporaryDirectory(prefix="eyes-selftest-") as td:
        p = Path(td) / "blank.png"
        p.write_bytes(blank_png)
        c1 = inspect_png(p, 20, 20)
        check("inspect_png on the planted blank: exists", c1["exists"], True)
        check("...dims_ok", c1["dims_ok"], True)
        check("...not_blank is False (RED)", c1["not_blank"], False)
        c2 = inspect_png(p, 99, 99)
        check("inspect_png with the wrong requested size: dims_ok is False "
              "(RED)", c2["dims_ok"], False)
        c3 = inspect_png(Path(td) / "nope.png", 20, 20)
        check("inspect_png on a missing file: exists is False (RED)",
              c3["exists"], False)

    print("\n=== D. browser discovery: an explicit path that does not "
          "exist is NO-BROWSER (RED, forced), never a silent fall-through ===")
    check("find_browser(explicit=<nothing there>) -> None",
          find_browser(explicit=str(Path(tempfile.gettempdir())
                                     / "eyes-selftest-no-such-browser.exe")),
          None)
    check("file_version() on a nonexistent path never raises, and says so",
          "unknown" in file_version(Path(tempfile.gettempdir())
                                     / "eyes-selftest-no-such-browser.exe"),
          True)

    print("\n=== E. isolation by construction: no argument to "
          "build_shot_cmd / build_version_cmd can drop either flag ===")
    sig_shot = inspect.signature(build_shot_cmd)
    sig_ver = inspect.signature(build_version_cmd)
    denylist = {"profile", "user_profile", "real_browser", "no_headless",
                "no_isolation", "local_profile", "use_local_profile"}
    check("build_shot_cmd has no profile/no-isolation parameter",
          bool(set(sig_shot.parameters) & denylist), False)
    check("build_version_cmd has no profile/no-isolation parameter",
          bool(set(sig_ver.parameters) & denylist), False)
    with tempfile.TemporaryDirectory(prefix="eyes-selftest-") as td:
        udd = Path(td) / "profile"
        cmd = build_shot_cmd("chrome-stub", "about:blank", 10, 10,
                              Path(td) / "x.png", udd)
        check("--headless=new is always present", "--headless=new" in cmd, True)
        udd_flags = [c for c in cmd if c.startswith("--user-data-dir=")]
        check("exactly one --user-data-dir= flag is present",
              len(udd_flags), 1)
        udd_val = udd_flags[0].split("=", 1)[1]
        check("...and its path is absolute",
              Path(udd_val).is_absolute(), True)
        vcmd = build_version_cmd("chrome-stub", udd)
        check("a version probe also carries --headless=new",
              "--headless=new" in vcmd, True)
        check("...and also carries an absolute --user-data-dir=",
              any(c.startswith("--user-data-dir=")
                  and Path(c.split("=", 1)[1]).is_absolute() for c in vcmd),
              True)

    print("\n=== F. the network default (plan decision 5) ===")
    check("no allow_hosts -> fully blocked",
          host_resolver_rule([]), "MAP * 0.0.0.0")
    check("allow_hosts adds EXCLUDE entries",
          host_resolver_rule(["fonts.example"]),
          "MAP * 0.0.0.0,EXCLUDE fonts.example")

    print("\n=== G. ears' console extractor, against a planted synthetic "
          "log with three false-positive classes and two real hits ===")
    synthetic_log = (
        '[1:1:0916/000000.000:VERBOSE1:components\\telemetry_client\\'
        'telemetry_service.cc:787] NoConsent: Microsoft.WebBrowser noise\n'
        '[1:1:0916/000000.001:ERROR:chrome\\browser\\component_updater\\'
        'x.cc:97] component update noise, not the page\n'
        '[1:1:0916/000000.002:WARNING:chrome\\browser\\extensions\\'
        'external_registry_loader_win.cc:283] extension registry noise\n'
        '[1:1:0916/000000.003:INFO:CONSOLE:5599] "extension console noise", '
        'source: chrome-extension://abc/background.js (5599)\n'
        '[1:1:0916/000000.004:INFO:CONSOLE:4] "a real page error", '
        'source: file:///C:/site/page.html (4)\n'
        '[1:1:0916/000000.005:INFO:CONSOLE:9] "Uncaught TypeError: real", '
        'source: https://example.test/app.js (9)\n'
    )
    with tempfile.TemporaryDirectory(prefix="eyes-selftest-") as td:
        log_p = Path(td) / "x.stderr.log"
        con_p = Path(td) / "x.console.txt"
        log_p.write_text(synthetic_log, encoding="utf-8")
        hits = extract_console(log_p, con_p)
        check("three browser-noise classes are excluded (RED case: a naive "
              "ERROR/WARNING match would have kept all six lines)",
              len(hits), 2)
        check("...the real page CONSOLE line survives",
              "a real page error" in hits[0], True)
        check("...the real Uncaught CONSOLE line survives",
              "Uncaught TypeError: real" in hits[1], True)
        check("...the chrome-extension:// CONSOLE line is excluded",
              any("extension console noise" in h for h in hits), False)

    print("\n=== H. the fixture calibration set matches the plan's text ===")
    check("fixture expected-yes is exactly {1, 2, 5, 7}",
          FIXTURE_EXPECTED_YES, {1, 2, 5, 7})
    check("the catalog has ten questions", len(CATALOG), 10)

    print(f"\n{n} checks; {'ALL PASS' if ok_all else 'FAILURES ABOVE'}")
    return 0 if ok_all else 1


# ==========================================================================
# CLI
# ==========================================================================
def build_parser():
    ap = argparse.ArgumentParser(
        prog="eyes.py",
        description="A screenshot instrument and a look-quality loop, level "
                     "1. Never opens the owner's own browser or profile -- "
                     "see decision 6 in this file's module docstring and in "
                     "EYES.md.")
    ap.add_argument("--selftest", action="store_true",
                     help="prove the pure judging layer against planted "
                          "reds, with no browser and no filesystem")
    sub = ap.add_subparsers(dest="verb")

    def add_render_args(p):
        p.add_argument("--src", required=True,
                        help="a repo-relative file path, or a URL")
        p.add_argument("--out", required=True, help="output directory")
        p.add_argument("--viewports", default=DEFAULT_VIEWPORT_SPEC)
        p.add_argument("--scale", type=int, default=1)
        p.add_argument("--stem", default=None)
        p.add_argument("--timeout", type=float, default=60.0)
        p.add_argument("--virtual-time-budget", type=int, default=4000)
        p.add_argument("--allow-hosts", nargs="*", default=[],
                        help="host(s) the isolated profile may resolve; "
                             "everything else stays blocked (decision 5)")
        p.add_argument("--browser", default=None,
                        help="an explicit Chromium binary path, for pinning "
                             "or for testing NO-BROWSER. There is no flag "
                             "here, and there will not be one, that points "
                             "this at the owner's own browser profile -- "
                             "see decision 6.")

    p_shot = sub.add_parser("shot", help="render at named viewports")
    add_render_args(p_shot)
    p_shot.set_defaults(func=cmd_shot, ears=False)

    p_ears = sub.add_parser("ears", help="shot, plus console capture")
    add_render_args(p_ears)
    p_ears.set_defaults(func=cmd_ears)

    p_look = sub.add_parser("look", help="print the ten-question catalog")
    p_look.add_argument("--out", default=None)
    p_look.add_argument("--fixture", action="store_true",
                         help="print the shipped fixture's calibration "
                              "answers instead of a blank template")
    p_look.set_defaults(func=cmd_look)

    p_gate = sub.add_parser("gate", help="the verify.py eyes gate")
    p_gate.add_argument("out")
    p_gate.set_defaults(func=cmd_gate)

    return ap


def main() -> int:
    ap = build_parser()
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not getattr(args, "verb", None):
        ap.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
