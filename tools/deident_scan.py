#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/deident_scan.py - the kit's own de-identification scanner.

WHY THIS EXISTS
===============
This kit was distilled from a real project. Every template in it started life as
a file full of one person's name, one machine's absolute paths, one company's
vault, and one repository's project name. Removing those by reading carefully is
not a control - it is an intention. This scanner is the control.

It is also the tool YOU want after you adopt the kit, pointed the other way: run
it over anything you are about to publish, share, or hand to a client, with your
own private token list.

WHAT THIS IS NOT, AND WHO OWNS THAT CLASS
=========================================
This is NOT a secret scanner and it does not compete with one. `gitleaks` and
`TruffleHog` are the incumbents for credentials: the first decides whether a
string LOOKS LIKE a secret, the second whether the secret WORKS. Both detect by
shape and entropy over a maintained rule set, and neither needs you to know in
advance what you are looking for. Run one of them for that class - this tool
will not find your cloud key.

What this tool covers is the adjacent job those two do not do: PROGRAM-IDENTITY
tokens, which have no detectable shape. A person's name, a username, an
employer, a machine path fragment and an internal project name are ordinary
words; nothing separates them from prose except a list somebody wrote. So this
scanner takes the list as its input, and its whole quality is the list's
quality - which is why the run prints the token count, and why an empty list
under --strict is an ABORT rather than a green. A green here says the words on
your list are absent from the tree. It says nothing whatever about secrets.

THE CONTRACT
============
    exit 0   clean - no token from the list appears anywhere in the scanned tree
    exit 1   HITS - at least one token was found; every hit is printed
    exit 2   ABORT - bad usage, unreadable token file, empty token list with
             --strict. "The scan did not run" and "the scan found nothing" must
             never share an exit code (this is the same rule the verify runner
             in modules/03-verification is built on).

USAGE
=====
    python tools/deident_scan.py                        # scan . with ./deident.tokens
    python tools/deident_scan.py --root <dir>
    python tools/deident_scan.py --tokens <file>        # one token per line, # comments
    python tools/deident_scan.py --token alice --token acme-corp
    python tools/deident_scan.py --case-sensitive
    python tools/deident_scan.py --strict               # empty token list is an ABORT
    python tools/deident_scan.py --selftest             # prove the scanner FIRES

THE TOKEN LIST IS NOT SHIPPED WITH TOKENS IN IT
===============================================
`deident.tokens` ships EMPTY, with instructions, because a shipped token list is
itself a leak: it is a list of exactly the words someone did not want published.
Keep your real list OUTSIDE the repo (a scratch directory, a password manager
note, your CI secrets) and pass it with --tokens. The empty in-repo file exists
so the wiring is discoverable, not so it can be filled in and committed.

If your token list lives inside the scanned tree, the scanner skips that one
file automatically - otherwise every token would trivially hit itself.

WHAT IT SCANS
=============
Every text file under --root, minus:
  * the default skip directories (.git, node_modules, __pycache__, .venv, ...)
  * anything matching --exclude (repeatable glob, matched against the path
    relative to --root, forward slashes)
  * files that do not decode as UTF-8/latin-1 text (binaries are reported in the
    summary as UNSCANNED, never silently ignored - a binary can carry a name too,
    and pretending otherwise would be the silent-drop failure this kit bans)

Paths themselves are scanned as well as contents: a file named
`notes-from-alice.md` is a hit even if its contents are clean.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".idea",
    ".vs", ".gradle", "target",
}

# Extensions we will not even try to decode. Reported as UNSCANNED, not skipped
# silently.
BINARY_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tif", ".tiff",
    ".pdf", ".zip", ".gz", ".bz2", ".xz", ".7z", ".rar", ".exe", ".dll", ".so",
    ".dylib", ".pyc", ".pyo", ".class", ".jar", ".mp3", ".mp4", ".wav", ".ogg",
    ".ttf", ".otf", ".woff", ".woff2", ".psd", ".blend", ".import",
}

MAX_BYTES = 8 * 1024 * 1024  # a file larger than this is reported, not read


def load_tokens(args) -> tuple[list[str], str]:
    """Returns (tokens, source-description). Raises ValueError on a bad file."""
    tokens: list[str] = list(args.token or [])
    src = "--token flags" if tokens else ""
    path = Path(args.tokens) if args.tokens else Path(args.root) / "deident.tokens"
    if args.tokens or path.exists():
        try:
            raw = path.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001 - the message is the product
            raise ValueError(f"token file {path} could not be read: {e!r}") from e
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tokens.append(line)
        src = (src + " + " if src else "") + str(path)
    # de-duplicate, keep order, drop empties
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        k = t if args.case_sensitive else t.lower()
        if t and k not in seen:
            seen.add(k)
            out.append(t)
    return out, (src or "<none>")


def tracked_files(root: Path):
    """(paths, note). `paths` is None when git could not answer.

    WHY THIS EXISTS: the kit tells you to create `kit.config.local` and to
    gitignore it, because it holds absolute paths. Then the kit's own Step 9
    scan reddens on that file - for containing exactly what the kit told you
    to put there, in a file that will never leave your machine. A scanner whose
    honest answer is "ignore that one" every single time is a scanner people
    stop reading.

    So `--tracked-only` scans what git would actually publish. It is OFF by
    default: "what is on disk" remains the paranoid default, and narrowing the
    scan is a decision you make out loud."""
    try:
        pr = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                            capture_output=True, timeout=30)
    except Exception as e:
        return None, f"git could not be run ({e!r})"
    if pr.returncode != 0:
        err = " ".join(pr.stderr.decode("utf-8", "replace").split())[:120]
        return None, f"git ls-files failed rc={pr.returncode}: {err}"
    names = [n for n in pr.stdout.decode("utf-8", "replace").split("\0") if n]
    return names, ""


def iter_files(root: Path, excludes: list[str], only: list | None = None):
    if only is not None:
        for rel in only:
            if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
                continue
            p = root / rel
            try:
                if p.is_file():
                    yield p, rel
            except OSError:
                continue
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_SKIP_DIRS]
        for fn in filenames:
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
                continue
            yield p, rel


def read_text(p: Path) -> tuple[str | None, str]:
    """(text, note). text is None when the file could not be scanned."""
    if p.suffix.lower() in BINARY_EXT:
        return None, "binary extension"
    try:
        size = p.stat().st_size
    except OSError as e:
        return None, f"stat failed: {e!r}"
    if size > MAX_BYTES:
        return None, f"larger than {MAX_BYTES} bytes"
    try:
        data = p.read_bytes()
    except OSError as e:
        return None, f"read failed: {e!r}"
    if b"\x00" in data[:4096]:
        return None, "contains NUL bytes (binary)"
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc), ""
        except UnicodeDecodeError:
            continue
    return None, "not decodable as text"


def redact(line: str, start: int, end: int, others=None, width: int = 60) -> str:
    """Show the hit in context with EVERY known token masked - not only the one
    that produced this hit - so the scanner's own OUTPUT is safe to paste into a
    report. The whole point is defeated if proving a clean scan requires
    publishing the words you were hiding, and one line very often carries two of
    them (a name inside a path is the classic).

    `others` is the full compiled pattern list; the matched span is bracketed,
    the rest are masked in place."""
    lo = max(0, start - width)
    hi = min(len(line), end + width)
    head = line[lo:start]
    tail = line[end:hi]
    for pat in (others or []):
        head = pat.sub(lambda m: "*" * len(m.group(0)), head)
        tail = pat.sub(lambda m: "*" * len(m.group(0)), tail)
    masked = "*" * (end - start)
    head = ("..." if lo > 0 else "") + head
    tail = tail + ("..." if hi < len(line) else "")
    return (head + "[" + masked + "]" + tail).strip()


def scan(root: Path, tokens: list[str], case_sensitive: bool,
         excludes: list[str], token_file: Path | None,
         only: list | None = None):
    flags = 0 if case_sensitive else re.IGNORECASE
    # Tokens are referred to by INDEX, never by value, everywhere in the output.
    # The operator owns the list and can look #3 up; a report, a CI log, or a
    # pasted terminal buffer must not carry the words themselves.
    pats = [(i + 1, re.compile(re.escape(t), flags)) for i, t in enumerate(tokens)]
    hits: list[str] = []
    unscanned: list[str] = []
    n_files = 0

    for p, rel in iter_files(root, excludes, only):
        if token_file is not None:
            try:
                if p.resolve() == token_file.resolve():
                    continue  # the list may not hit itself
            except OSError:
                pass
        n_files += 1

        # 1. the PATH itself
        for idx, pat in pats:
            if pat.search(rel):
                hits.append(f"{rel}:<path>: path contains token #{idx}")

        # 2. the CONTENTS
        text, note = read_text(p)
        if text is None:
            unscanned.append(f"{rel}  ({note})")
            continue
        for ln, line in enumerate(text.splitlines(), 1):
            for idx, pat in pats:
                for m in pat.finditer(line):
                    hits.append(
                        f"{rel}:{ln}:{m.start() + 1}: token #{idx} -> "
                        f"{redact(line, m.start(), m.end(), [q for _, q in pats])}")
    return hits, unscanned, n_files


def selftest() -> int:
    """Prove the scanner FIRES. A scanner that has only ever returned clean is
    indistinguishable from a scanner that cannot find anything - the negative
    control is not optional (this kit's own doctrine, modules/03-verification)."""
    ok = True

    def check(label, got, want):
        nonlocal ok
        good = got == want
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"  (got {got!r}, want {want!r})"))

    with tempfile.TemporaryDirectory(prefix="deident-selftest-") as td:
        root = Path(td)
        (root / "sub").mkdir()
        (root / "clean.md").write_text("nothing to see here\n", encoding="utf-8")
        h, u, n = scan(root, ["plantedname"], False, [], None)
        check("a clean tree produces zero hits", len(h), 0)

        (root / "sub" / "dirty.md").write_text(
            "line one\nowner: PlantedName wrote this\n", encoding="utf-8")
        h, u, n = scan(root, ["plantedname"], False, [], None)
        check("a planted token is found", len(h), 1)
        check("the hit names the right file",
              h[0].startswith("sub/dirty.md:2:"), True)
        check("the hit is redacted (token not echoed, in any case)",
              "planted" in h[0].lower(), False)

        h, u, n = scan(root, ["plantedname"], True, [], None)
        check("--case-sensitive respects case", len(h), 0)

        (root / "sub" / "PlantedName-notes.md").write_text("x\n", encoding="utf-8")
        h, u, n = scan(root, ["plantedname"], False, [], None)
        # dirty.md contributes 1 content hit; the new file contributes 1 PATH hit.
        check("a token in a FILENAME is found too", len(h), 2)
        check("...and it is reported as a path hit",
              any(":<path>:" in x for x in h), True)
        check("hits name the token by INDEX, never by value",
              all(("token #" in x) for x in h), True)

        h, u, n = scan(root, ["plantedname"], False, ["sub/*"], None)
        check("--exclude removes a subtree", len(h), 0)

        (root / "bin.dat").write_bytes(b"\x00\x01plantedname\x00")
        h, u, n = scan(root, ["plantedname"], False, ["sub/*"], None)
        check("a binary is reported UNSCANNED, never silently dropped",
              any("bin.dat" in x for x in u), True)

        h, u, n = scan(root, ["plantedname"], False, [], None, only=[])
        check("--tracked-only with an EMPTY tracked list scans nothing",
              (len(h), n), (0, 0))
        h, u, n = scan(root, ["plantedname"], False, [], None,
                       only=["sub/dirty.md"])
        check("--tracked-only scans exactly the listed files", len(h), 1)
        h, u, n = scan(root, ["plantedname"], False, ["sub/*"], None,
                       only=["sub/dirty.md"])
        check("...and --exclude still applies on top of it", len(h), 0)
        h, u, n = scan(root, ["plantedname"], False, [], None,
                       only=["sub/dirty.md", "gone-from-disk.md"])
        check("a tracked path that is not on disk is skipped, not a crash",
              len(h), 1)

        tokfile = root / "deident.tokens"
        tokfile.write_text("# comment\nplantedname\n\n", encoding="utf-8")
        h, u, n = scan(root, ["plantedname"], False, ["sub/*"], tokfile)
        check("the token file does not hit itself", len(h), 0)

    print()
    print("DEIDENT SELFTEST: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan a tree for tokens that must not be published.",
        epilog="exit 0 clean - 1 hits - 2 abort")
    ap.add_argument("--root", default=".", help="tree to scan (default: .)")
    ap.add_argument("--tokens", default="",
                    help="token list file, one per line, # comments "
                         "(default: <root>/deident.tokens if it exists)")
    ap.add_argument("--token", action="append", default=[],
                    help="a single token, repeatable")
    ap.add_argument("--exclude", action="append", default=[],
                    help="glob (relative to root, forward slashes), repeatable")
    ap.add_argument("--case-sensitive", action="store_true")
    ap.add_argument("--tracked-only", action="store_true",
                    help="scan only files git TRACKS, i.e. what would actually "
                         "be published. Skips gitignored working files such as "
                         "kit.config.local. Default OFF: 'everything on disk' "
                         "stays the paranoid default, and narrowing is a "
                         "decision you make out loud. If git cannot answer, "
                         "this falls back to a full walk and SAYS SO.")
    ap.add_argument("--strict", action="store_true",
                    help="an EMPTY token list aborts (exit 2) instead of "
                         "reporting a vacuous clean. Use this in CI.")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the scanner fires on a planted token")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    root = Path(a.root).resolve()
    if not root.is_dir():
        print(f"ABORT: --root {root} is not a directory", file=sys.stderr)
        return 2
    try:
        tokens, src = load_tokens(a)
    except ValueError as e:
        print(f"ABORT: {e}", file=sys.stderr)
        return 2

    if not tokens:
        msg = ("no tokens supplied - this scan would pass vacuously. "
               "Pass --token/--tokens, or fill a PRIVATE token list.")
        if a.strict:
            print(f"ABORT: {msg}", file=sys.stderr)
            return 2
        print(f"WARNING: {msg}")

    tokfile = None
    if a.tokens:
        tokfile = Path(a.tokens)
    elif (root / "deident.tokens").exists():
        tokfile = root / "deident.tokens"

    only = None
    scope = "everything on disk"
    if a.tracked_only:
        only, note = tracked_files(root)
        if only is None:
            # NEVER silently widen or narrow. A scanner that quietly did
            # something other than what the flag said is worse than one that
            # refused.
            print(f"SCOPE WARNING: --tracked-only requested but {note}; "
                  f"falling back to a full walk of everything on disk.")
            scope = "everything on disk (--tracked-only unavailable)"
        else:
            scope = f"git-tracked files only ({len(only)} tracked)"

    hits, unscanned, n_files = scan(root, tokens, a.case_sensitive,
                                    a.exclude, tokfile, only)

    print(f"root      : {root}")
    print(f"scope     : {scope}")
    print(f"tokens    : {len(tokens)} (from {src}) "
          f"[values withheld from this output by design]")
    print(f"files     : {n_files} scanned, {len(unscanned)} unscanned")
    for u in unscanned:
        print(f"  UNSCANNED {u}")
    if hits:
        print()
        for h in hits:
            print(f"  HIT {h}")
        print()
        print(f"DEIDENT SCAN: {len(hits)} HIT(S) - exit 1")
        return 1
    print("DEIDENT SCAN: 0 hits - exit 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
