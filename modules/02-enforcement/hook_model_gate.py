#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hook_model_gate.py - a PreToolUse gate with four enforcement points.

THIS FILE NEEDS NO EDITING. Everything project-specific is read from
`kit.config` (see FINDING THE CONFIG below), so the gate you run is the gate the
fixtures test, byte for byte, on every project that adopts it.

    STRUCTURE OVER SENTENCES. Every rule below exists because its prose version
    failed at least once in the reference build. A rule that has never failed
    does not belong here yet - see modules/04-ledgers/FAILURE-FLOOR.md for the
    promotion discipline.

THE FOUR POINTS
===============
  1. Workflow scripts   - every agent() call site declares a model tier.
                          COUNTING IS A HEURISTIC: comments and string-literal
                          CONTENTS are blanked, then `agent(` and `model:`
                          occurrences are counted. It can still be defeated (a
                          `model:` in a data structure that is not a spawn, a
                          `//` inside a regex literal). It is a floor, not a
                          parser - see strip_script_comments() for what that
                          trade buys.
  2. Agent spawns       - same rule, plus: no spawn may request the orchestrator
                          tier by name (in the reference build this half was
                          prose only, and prose does not bind a grandchild).
  3. Shell              - blanket staging (`git add -A`, `git add .`, `-u`,
                          `:/`, `*`, `git stage -A`, `git commit -a`, and the
                          same forms behind `git -C <path>` or indented inside a
                          block) is DENIED. It once swept an in-flight agent's
                          scratch file into a commit; targeted adds only.
                          ALSO A HEURISTIC, with both error directions
                          disclosed at BLANKET_ADD.
  4. Protected path     - OPTIONAL. Any shell command or Edit/Write touching the
                          protected location ASKS the owner, at any agent depth,
                          unless a cert-green token covers the current tree.
                          ALSO A HEURISTIC: it is a substring match on a string,
                          so a differently-CASED spelling of the same path on a
                          case-insensitive filesystem, a `cd` followed by a
                          relative path, and a symlink or junction into the
                          protected location all pass silently. See
                          touches_protected(). `python tools/kit_doctor.py`
                          reports the case-sensitivity of the filesystem you are
                          actually on.

ALL FOUR POINTS ARE ZONE B: useful friction, honestly labeled. Every one is a
string heuristic running with the same privileges as the agent it governs, in a
file that agent can edit. They raise the cost of a mistake. They do not stop an
adversary, and nothing in this kit does - see "Security scope" in README.md.

THE PROTOCOL
============
Reads one JSON object on stdin: `{"tool_name": ..., "tool_input": {...}}`.
Writes at most one JSON object on stdout:

    {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                            "permissionDecision": "deny"|"allow"|"ask",
                            "permissionDecisionReason": "..."},
     "systemMessage": "..."}

SILENCE IS A VERDICT, NOT AN ABSENCE - "I have no opinion, let the permission
system decide" - and it is only valid from a process that ALSO EXITED 0. That
distinction is what the fixture harness's dead-man clause tests, and it is the
difference between a gate that is quiet and a gate that is dead.

FAIL-OPEN, DELIBERATELY, WITH ONE EXCEPTION
===========================================
Unparseable stdin, a missing config, an unreadable token: the gate stays silent
and lets the harness's own permission rules decide. A hook that denies every
tool call because its config moved is a hook that gets uninstalled within the
hour, and an uninstalled gate enforces nothing at all.

The exception is the protected path: when the tripwire is ENABLED and anything
about the cert-green evaluation goes wrong, the answer is ASK. Uncertainty about
whether a touch is authorised resolves toward the human, never away.

FINDING THE CONFIG (four steps, and step 4 is the one that matters)
===================================================================
    1. $KIT_CONFIG
    2. ./kit.config                  (current working directory)
    3. <this file's dir>/kit.config
    4. the nearest kit.config walking UP from this file's directory

Step 4 is what lets `<repo>/tools/hook_model_gate.py` find `<repo>/kit.config`
- the layout the QUICKSTART produces. Whatever is found is then overlaid with
`kit.config.local` from the same directory: the committed file carries
repo-relative values, the gitignored `.local` carries absolute paths and the
protected location.

**NONE AND EMPTY MEAN UNSET** for every value read here. `PROTECTED_PATH =
NONE` is not a path; it is the absence of one, and a gate that substring-matches
the literal word would ask about `src/NONESUCH/`.

Absent config = defaults: exempt types empty, tripwire disabled, points 1-3
fully active. The gate is useful on day one, before anything is filled in -
but note that "no config" means the forbidden-tier and exempt-type rules
quietly do not exist, which is why `hook_fixtures.py --armed` prints a
CONFIG WARNING and `--strict` fails when a kit.config exists up-tree but was
not the one loaded.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
def find_config() -> Path | None:
    """THE SEARCH ORDER - exactly four steps, documented here, in QUICKSTART
    Step 6, and in this module's README, because a config that is not found is
    a config whose rules die SILENTLY:

        1. $KIT_CONFIG                    (explicit; wins over everything)
        2. ./kit.config                   (the current working directory)
        3. <this file's dir>/kit.config
        4. the nearest kit.config walking UP from this file's directory

    Step 4 is what makes `<repo>/tools/hook_model_gate.py` find
    `<repo>/kit.config`, which is the layout the QUICKSTART produces. Without
    it the hook loads no config, and every config-driven rule - the forbidden
    tier, the exempt types, the protected path - simply stops existing while
    every fixture still reports green."""
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
    """kit.config, then kit.config.local from the SAME directory, overlaid.

    The split resolves a real contradiction: the config must travel with the
    repo (or the hook finds nothing) and must NOT carry one machine's absolute
    paths (or it is both wrong for everyone else and a small privacy leak).
    So `kit.config` is COMMITTED and holds repo-relative, shareable values;
    `kit.config.local` is GITIGNORED and holds absolute paths, the protected
    location, and anything else that is true only here. Later wins."""
    cfg: dict[str, str] = {}
    p = find_config()
    if p is None:
        return cfg
    _read_pairs(p, cfg)
    _read_pairs(p.with_name("kit.config.local"), cfg)
    cfg["_source"] = str(p)
    return cfg


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


def cfg_get(cfg: dict, key: str):
    """A configured value, or None. **NONE and empty mean UNSET.**

    This is not tidiness. `PROTECTED_PATH = NONE` is a perfectly ordinary
    non-empty string, and treating it as one had three measured consequences:
    the half-configured detector could never fire from a kit-derived config;
    this gate substring-matched the literal word, so `src/NONESUCH/x` tripped
    the tripwire; and enabling the tripwire with no real path produced a
    FULLER green than configuring it correctly. A placeholder that behaves
    like a value is worse than a missing key, because a missing key is
    obviously missing."""
    v = cfg.get(key)
    if v is None:
        return None
    v = v.strip()
    return None if is_placeholder(v) else v


def as_list(cfg: dict, key: str) -> list[str]:
    raw = cfg_get(cfg, key) or ""
    return [x.strip() for x in raw.split(",") if x.strip()]


def as_bool(cfg: dict, key: str) -> bool:
    return cfg.get(key, "").strip().lower() in {"1", "true", "yes", "on"}


CFG = load_config()
EXEMPT_TYPES = set(as_list(CFG, "MODEL_EXEMPT_TYPES"))
FORBIDDEN_TIER = cfg_get(CFG, "FORBIDDEN_SPAWN_TIER") or ""
# M-3: an UNCONFIGURED tier renders as a labelled placeholder, not as prose
# that looks like advice. "Add model: 'your lane tier'" is a deny message that
# tells the reader to type the wrong thing.
LANE_TIER = cfg_get(CFG, "LANE_TIER") or "<LANE_TIER unset in kit.config>"
SWEEP_TIER = cfg_get(CFG, "SWEEP_TIER") or "<SWEEP_TIER unset in kit.config>"
PROJECT_ROOT = cfg_get(CFG, "PROJECT_ROOT") or ""
TRIPWIRE_ON = as_bool(CFG, "PROTECTED_PATH_ENABLED")
_prot = cfg_get(CFG, "PROTECTED_PATH")
PROTECTED = _prot.replace("\\", "/") if _prot else ""
TOKEN_FILE = cfg_get(CFG, "CERT_TOKEN_FILE") or ".claude/cert-green.json"
CERT_PATHS = as_list(CFG, "CERT_PATHS")


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------
def out(decision: str, reason: str, msg: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        },
        "systemMessage": msg,
    }))


# --------------------------------------------------------------------------
# the cert-green token
# --------------------------------------------------------------------------
def cert_green() -> bool:
    """The owner's nod, pre-granted - but ONLY while the certification still
    describes THIS tree.

    WHAT THIS TOKEN IS NOT - read this before you rely on it
    -------------------------------------------------------
    It is a CONVENIENCE, not an authorization. The file is an ordinary JSON
    file in an ordinary directory, so anything that can write a file can mint
    one, including the agents this gate governs. There is no signature, and
    there is deliberately none: an HMAC needs a key, and in a harness where the
    agent runs shell commands as the owner, with the owner's filesystem and the
    owner's environment, there is nowhere to put a key that the agent cannot
    read. A signature there would raise forgery from "write a file" to "read a
    file, then write a file" and would make the label MORE misleading, not
    less. The honest control is the label, and this is it.

    What the token DOES buy, and it is real: it stops a certified, unchanged
    tree from prompting the owner over and over for touches the owner has
    already approved in general. `verify.py --mint-cert-token` writes it from
    the runner's single PASS return, so the ordinary way to get one is to
    certify, not to assert.

    Three conditions, and the third is the one that is always forgotten:
      1. a token file exists and names a sha;
      2. the newest commit touching CERT_PATHS is contained in that sha;
      3. CERT_PATHS are CLEAN in `git status`.

    Condition 3 is not pedantry. In the reference build a reviewer caught the
    tripwire standing wide open while the working tree carried uncommitted edits
    to certified paths and the suite was red. Certification is a property of a
    TREE, not of the last commit that happened to land.

    Returns False on any error: a token we cannot evaluate is not a nod.
    """
    if not PROJECT_ROOT or not CERT_PATHS:
        return False
    root = PROJECT_ROOT
    try:
        tok_path = Path(root) / TOKEN_FILE
        sha = (json.loads(tok_path.read_text(encoding="utf-8")).get("sha") or "").strip()
        if not sha:
            return False

        def git(*args: str) -> str:
            return subprocess.run(["git", "-C", root, *args],
                                  capture_output=True, text=True,
                                  timeout=10).stdout.strip()

        tip = git("log", "-1", "--format=%H", "--", *CERT_PATHS)
        if not tip:
            return False
        if git("status", "--porcelain", "--", *CERT_PATHS):
            return False          # condition 3
        r = subprocess.run(["git", "-C", root, "merge-base", "--is-ancestor",
                            tip, sha], capture_output=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False


def touches_protected(s: str) -> bool:
    """Both must be true: the tripwire is ON *and* a real path is configured.

    `PROTECTED` is already normalised through cfg_get, so the literal string
    "NONE" can never reach here as a path to match.

    A SUBSTRING MATCH, AND THEREFORE A HEURISTIC. Backslashes are normalised;
    nothing else is. Three silent-allow directions, measured, disclosed here
    and in point 4 of the module docstring:

      * CASE. On Windows and on default macOS the filesystem is
        case-insensitive, so `C:/Users/OWNER/frozen-build/x` opens the same
        file as a configured `C:/Users/owner/frozen-build` and this returns
        False. Folding here would be wrong on Linux, where the two really are
        different files, and a gate that asks about a path the owner did not
        protect is the false positive that gets gates deleted. So the rule is
        stated rather than guessed, and `tools/kit_doctor.py` probes the actual
        filesystem and reports what the mismatch would cost on YOUR host.
      * `cd` THEN RELATIVE. `cd <parent> && rm -rf frozen-build` never contains
        the configured string. Any string matcher has this hole.
      * SYMLINKS AND JUNCTIONS. A link into the protected location is a
        different string.

    AND ONE FALSE-ASK DIRECTION, which is the loud one: a substring match also
    fires on a LONGER path that merely contains the configured string, so
    `PROTECTED_PATH = /build` asks about `/buildings/notes.md`; and it fires on
    any command that merely MENTIONS the path in prose or in a commit message.
    Both resolve toward the human, which is the safe direction, and both are
    fixed by configuring a path with a trailing separator or a longer prefix.

    The compensating control is that the tripwire resolves toward the human on
    every uncertainty, and that the protected location is the owner's, not the
    agent's, to move."""
    if not (TRIPWIRE_ON and PROTECTED):
        return False
    return PROTECTED in s.replace("\\", "/")


def protected_verdict(kind: str) -> None:
    """ASK unless a cert-green token covers the tree. On ANY uncertainty, ASK."""
    try:
        green = cert_green()
    except Exception:
        green = False
    if green:
        out("allow",
            f"Protected-path {kind} pre-authorised: a cert-green token covers "
            f"the newest change to the certified paths, and those paths are "
            f"clean.",
            f"Protected-path {kind} - cert-green, proceeding.")
    else:
        out("ask",
            f"PROTECTED-PATH TRIPWIRE: this {kind} touches {PROTECTED} and no "
            f"cert-green token covers the current tree (missing, superseded by "
            f"a later change, or the certified paths are dirty). Doctrine: this "
            f"prompt is the owner's nod.",
            f"Protected-path {kind} - asking the owner (no cert-green token).")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def _blank(s: str) -> str:
    """Same length, same line structure, no content. Offsets are preserved so
    the blanking cannot join two lines into one accidental match."""
    return "".join("\n" if ch == "\n" else " " for ch in s)


def strip_script_comments(src: str) -> str:
    """Blank //, /* */ and # comments AND string-literal CONTENTS before
    counting agent()/model:.

    ONE PASS, AND IT HAS TO BE. The first version stripped comments with three
    regexes and knew nothing about strings, so `const u = 'https://x/y';` blanked
    the rest of that line - including an `agent(` call sitting on it - and the
    count fell to 0 vs 0, which is SILENCE. A URL in a workflow script is
    ordinary, and the failure direction was a false ALLOW of an undeclared
    spawn. That is fixture `r`.

    Masking strings in a separate earlier pass does not work either, and the
    reason is worth writing down: `// don't` would open a literal at the
    apostrophe and blank the rest of the file. Comments and literals have to be
    recognised by the same scanner, in source order, because each one hides the
    other's delimiters.

    TWO MORE BLANKING TRAPS, CLOSED IN THE SAME PASS, AND THE REASON THEY HAD
    TO BE. Both were shipped as disclosed residuals in the FALSE POSITIVE
    direction, and the disclosure was WRONG - it was measured and both are
    SILENT FALSE ALLOWS, the same mechanism and the same direction as the URL
    defect above. Over-blanking removes the `agent(` call along with everything
    else on the line, the count falls to 0 vs 0, and the gate says nothing:

      * a JS REGEX LITERAL containing an escaped slash (`/https:\\/\\//`) used to
        read as a `//` comment. It is now recognised as a literal when a `/`
        appears where an expression may START - after `( , = : [ ! & | ? { } ;`
        or an operator, or at the beginning - and its contents are blanked like
        a string's. A `/` after an identifier, a digit, `)` or `]` is DIVISION
        and is left alone, which is what keeps `(a + b) / c` intact. Fixture
        `ac`.
      * `#` used to blank to end of line everywhere outside a string, so a JS
        PRIVATE FIELD (`this.#id = 1;`) took the rest of its line with it. A `#`
        directly after `.` or an identifier character is now an ordinary
        character. A `#` after whitespace or at line start is still a comment,
        because that is the shell and Python convention and this scanner serves
        all three languages. Fixture `ad`.

    WHAT SURVIVES, STATED IN THE RIGHT DIRECTION. Every remaining defeat below
    is a SILENT FALSE ALLOW unless marked otherwise - the gate says nothing
    about a spawn that never declared a tier, which is the failure this rule
    exists to prevent:

      * `#` at the start of a token in a language where it is neither a comment
        nor a private field (`const c = #fff`) still blanks its line. Silent.
      * a `/` in expression position that is genuinely division after a keyword
        this scanner does not know is read as a regex, and its "contents" are
        blanked to the next `/`. Silent.
      * a template literal's `${...}` interpolation is blanked with the rest of
        the literal, so an `agent(` call written inside one does not count.
        Silent.
      * `model:` inside a data structure that is not a spawn argument still
        counts as a declaration, so one undeclared `agent(` rides on it. Silent.
      * an unterminated quote is treated as an ordinary character rather than
        swallowing the file, which is the only safe reading of an apostrophe in
        prose. This is the one FALSE DENY direction: loud, immediate, fixable.

    It exists because the un-blanked count had a much easier defeat: one
    commented-out `model:` anywhere in a script silently satisfied the tier
    rule for an entirely different, undeclared agent() call.

    THE REAL ANSWER is a parser, and this gate is not the place for one. If
    your project's scripts are complex enough for that to matter, judge them
    with a linter that has an AST and let this gate keep the floor."""
    # A `/` here may begin a regex literal; anywhere else it is division.
    # Deliberately punctuation-only: a keyword list (`return`, `typeof`, `case`)
    # would add cases this scanner cannot verify, and guessing REGEX where
    # DIVISION was meant blanks real code, which is the silent direction.
    regex_ok = set("(,=:[!&|?{};+-*%~^<>\n\t ")
    ident = set("abcdefghijklmnopqrstuvwxyz"
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$")
    out: list[str] = []
    i, n = 0, len(src)
    while i < n:
        ch, two = src[i], src[i:i + 2]
        # `prev` skips spaces and tabs: it answers "what kind of position is
        # this?" for the regex/division question, where `x = /re/` and `x=/re/`
        # must read the same. `imm` is the character actually touching this one,
        # which is the only thing that separates `this.#id` from `x = 1 # note`.
        prev = next((src[k] for k in range(i - 1, -1, -1)
                     if src[k] not in " \t"), "")
        imm = src[i - 1] if i else ""
        if two == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(_blank(src[i:j]))
            i = j
        elif two == "//":
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(_blank(src[i:j]))
            i = j
        elif ch == "#" and imm != "." and imm not in ident:
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(_blank(src[i:j]))
            i = j
        elif ch == "/" and (prev == "" or prev in regex_ok):
            # A regex literal. `[...]` may contain an unescaped `/`, so the
            # character class has to be tracked or `/[/]/` closes early.
            j, in_class, closed = i + 1, False, False
            while j < n and src[j] != "\n":
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == "[":
                    in_class = True
                elif src[j] == "]":
                    in_class = False
                elif src[j] == "/" and not in_class:
                    closed = True
                    break
                j += 1
            if closed:
                out.append("/" + _blank(src[i + 1:j]) + "/")
                i = j + 1
            else:
                out.append(ch)          # not a literal after all: leave it
                i += 1
        elif ch in "\"'`":
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == ch or (src[j] == "\n" and ch != "`"):
                    break
                j += 1
            if j < n and src[j] == ch:
                out.append(ch + _blank(src[i + 1:j]) + ch)
                i = j + 1
            else:
                out.append(ch)          # unterminated: an apostrophe in prose
                i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


# ---- POINT 3: BLANKET STAGING -------------------------------------------
# ANCHORED TO COMMAND POSITION on purpose. An unanchored pattern fires on PROSE
# that merely mentions the banned form - a docs append, a commit message, this
# very comment. The reference gate blocked its own documentation within minutes
# of being born. Precision matters as much as loudness: an alarm the operator
# learns to skim is a dead alarm.
#
# WHAT IT NOW COVERS, and why the list grew. Three independent readers of the
# shipped kit found the same class in one afternoon: the old pattern was
# `git\s+add\s+(-A|--all|\.)` anchored at `^` or after `;&|`, and every one of
# these walked straight past it -
#
#     git add -Av            combined short flags
#     git -C <path> add -A   a global option before the subcommand
#     git stage -A           the synonym
#     git add -u             stages every tracked modification
#     git add :/             the whole-repo pathspec
#     git add '*'            the quoted glob
#     git commit -am         stage-and-commit in one
#         git add -A         ONE LEADING SPACE OR TAB - the normal shape of a
#                            command inside an `if` or a `for`, and the worst of
#                            the set, because nobody typed it to evade anything.
#
#     git add ./             one character from `git add .`
#     git add "-A"           two quotes from `git add -A`
#     git add --al           git resolves unique long-option PREFIXES
#     git add ':(top)'       pathspec magic for the whole repository
#     FOO=1 git add -A       an assignment prefix
#     env X=1 / sudo / time / nohup git add -A     a command prefix
#     $(git add -A)          command substitution
#
# The docstring used to call this rule "DENIED outright". That sentence outran
# its measurement, in a kit whose thesis is that confident sentences must not.
#
# THE SCAN NEVER LEAVES ITS LINE, and this is the correction that matters most.
# The first hardened version used `\s` between tokens, which matches NEWLINE, so
# the token-skipping scan ran off the end of the `git add` command and through
# every following line until it met a quote or one of `;&|`. Five ordinary
# two-line blocks were measured denying: `git commit -F msg.txt` then `ls -la`,
# `git add README.md` then `cd .`, `git add a.py` then `sort -u list.txt`. That
# is precisely the dead alarm this comment's first paragraph warns about, built
# by the fix for the bypasses. Every separator inside a command is `[ \t]` now.
# The measured cost: a blanket flag reached only by a BACKSLASH LINE
# CONTINUATION stops matching - and that form was already a false negative
# before the change, so nothing was lost.
#
# NO CLAIM OF COMPLETENESS IS MADE. A regex over one command string cannot
# reach completeness here, and the list below is what one reviewer found in one
# session after three others had already been through it.
#
# BOTH ERROR DIRECTIONS, DISCLOSED:
#   FALSE NEGATIVE (silent - the gate says nothing and the files are staged).
#     Known and NOT closed: a nested shell (`sh -c 'git add -A'`,
#     `bash -lc "..."`); a backslash line continuation; backtick command
#     substitution (`` `git add -A` `` - deliberately not matched, because a
#     backtick code span inside a commit message is far more common than the
#     legacy substitution form and matching it would deny ordinary prose);
#     `xargs git add`; a shell alias; a command built at runtime
#     (`V=git; $V add -A`); a blanket flag placed AFTER a quoted argument
#     (`git commit -m "x" -a`); and any script the command merely invokes.
#     The DURABLE fix is not a bigger regex: it is to judge the INDEX rather
#     than the string, because every bypass above ends in the same index state.
#     A PreToolUse hook cannot do that - it runs BEFORE the command, when
#     `git diff --cached` still describes the world as it was - so the index
#     judgement belongs in a git `pre-commit` hook, at the moment the index is
#     final. Until a project installs one, the compensating pair is this pattern
#     plus the sweep list this gate prints when it denies, and
#     `python tools/kit_doctor.py`, whose dirty-paths check names the same files
#     on demand. Neither stages anything.
#   FALSE POSITIVE (loud - an immediate, fixable deny). `^[ \t]*` means an
#     indented occurrence anywhere in a MULTI-LINE command matches, including
#     inside a heredoc or a multi-line commit message that quotes the rule.
#     A deliberate trade: the indented form is too common in real shell blocks
#     to leave uncovered. Quoted arguments are not scanned THROUGH for flags,
#     which is what keeps `git commit -m 'ban git add -A in the hook'` silent
#     (fixture i), and the scan cannot leave its line, which is what keeps
#     `git commit -F msg.txt` followed by `ls -la` silent (fixture ae).
# EVERY separator below is `[ \t]`, and NEVER `\s`. `\s` matches newline, and
# the one place it appears is the anchor's `[;&|]\s*`, where a newline after a
# `&&` really is the same command continuing.
_GIT_OPTS = (r"(?:[ \t]+(?:-C[ \t]+\S+|-c[ \t]+\S+|-P|--no-pager"
             r"|--git-dir(?:=\S+|[ \t]+\S+)"
             r"|--work-tree(?:=\S+|[ \t]+\S+)))*")
# Prefixes that put `git` one or more tokens later without changing what it
# does: an environment assignment, or a wrapper that execs it.
_PREFIX = (r"(?:(?:[A-Za-z_][A-Za-z0-9_]*=[^\s;&|'\"]*"
           r"|env|sudo|time|nohup|command|stdbuf|nice)[ \t]+)*")
# A token that may be skipped while looking for the blanket marker. It never
# contains a quote, so the scan stops at the first quoted argument and cannot
# reach a `-a` living inside a commit message; and it never contains a newline,
# so the scan cannot leave the command it started on.
_TOK = r"(?:[ \t]+[^\s;&|'\"]+)*?"
# `git add` resolves any unambiguous PREFIX of a long option, so `--al` is
# `--all` and `--upd` is `--update`. Both are unambiguous from their second
# character among git-add's long options.
_LONG = r"--a(?:l(?:l)?)?|--u(?:p(?:d(?:a(?:t(?:e)?)?)?)?)?"
BLANKET_ADD = re.compile(
    r"(?m)(?:^[ \t]*|[;&|]\s*|\$\([ \t]*)" + _PREFIX +
    r"git" + _GIT_OPTS + r"[ \t]+(?:"
    r"(?:add|stage)" + _TOK + r"[ \t]+(?:"
    r"['\"]?-(?=[A-Za-z]*[Au])[A-Za-z]+['\"]?"   # -A -u -Av "-A" ...
    r"|['\"]?(?:" + _LONG + r")['\"]?"           # --all --al --a --update ...
    r"|['\"]?(?:\.[/\\]?|:/|\*|:\([^)\s]*\))['\"]?"   # . ./ :/ * :(top)
    r")"
    r"|commit" + _TOK + r"[ \t]+"
    r"(?:['\"]?-(?=[A-Za-z]*a)[A-Za-z]+['\"]?|--all)"
    r")(?=$|\s|[;&|)`])")

# A DRY RUN STAGES NOTHING, so it is not blanket staging. Denying
# `git add --dry-run .` would be a false positive on the exact command an
# operator reaches for to inspect what a blanket add WOULD take - which is to
# say, on the remedy this gate's own deny message is pointing them toward.
DRY_RUN = re.compile(r"(?:^|[ \t])(?:--dry-run\b|-(?=[A-Za-z]*n)[A-Za-z]+\b)")


def blanket_add(cmd: str):
    """The matched blanket-staging form, or None.

    Matches are considered one at a time so that a dry run earlier in a
    multi-line command cannot excuse a real blanket add later in it. The dry-run
    test is scoped to the LINE the match sits on, for the same reason the token
    scan is: a flag on a different command is a different command."""
    for m in BLANKET_ADD.finditer(cmd):
        start = cmd.rfind("\n", 0, m.start()) + 1
        end = cmd.find("\n", m.end())
        line = cmd[start:] if end < 0 else cmd[start:end]
        if not DRY_RUN.search(line):
            return m.group(0).strip()
    return None


def sweep_preview(porcelain: str, limit: int = 12) -> str:
    """The files a blanket add would have taken, as a message fragment. Pure.

    The deny message used to say "run the doctor to see what this would have
    swept up", which is one more command between a blocked operator and the
    answer. The list is two lines of git away at the moment of the deny, so it
    is printed there. The doctor's dirty-paths check remains the on-demand
    route, and neither stages anything."""
    rows = [ln for ln in (porcelain or "").splitlines() if len(ln) >= 4]
    if not rows:
        return ""
    shown = "; ".join(f"{ln[:2].strip() or '??'} {ln[3:].strip()}"
                      for ln in rows[:limit])
    more = "" if len(rows) <= limit else f" (+{len(rows) - limit} more)"
    return (f" It would have swept up {len(rows)} path(s): {shown}{more}."
            f" Nothing was staged.")


def main() -> None:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return                     # fail open: see the module docstring
    tool = d.get("tool_name") or ""
    ti = d.get("tool_input") or {}

    # ---- 1. workflow scripts -------------------------------------------
    if tool == "Workflow":
        script = ti.get("script")
        if not script and ti.get("scriptPath"):
            try:
                script = Path(ti["scriptPath"]).read_text(encoding="utf-8")
            except Exception:
                script = None
        if not script:
            return
        code = strip_script_comments(script)
        n_agent = len(re.findall(r"\bagent\s*\(", code))
        n_model = len(re.findall(r"\bmodel\s*:", code))
        if n_agent > n_model:
            out("deny",
                f"LOUD FAILURE - model-tiering rule: {n_agent} agent() call "
                f"site(s) but only {n_model} model: declaration(s). Every "
                f"agent() must declare an explicit tier (e.g. "
                f"{{model: '{LANE_TIER}'}}); omitting it silently inherits the "
                f"session model, which is the orchestrator tier. Fix and "
                f"relaunch.",
                "Workflow blocked: agent() without an explicit model tier.")
        return

    # ---- 2. agent spawns -------------------------------------------------
    if tool == "Agent":
        model = (ti.get("model") or "").strip()
        stype = (ti.get("subagent_type") or "").strip()
        if FORBIDDEN_TIER and model and model.lower() == FORBIDDEN_TIER.lower():
            out("deny",
                f"LOUD FAILURE - a spawn may never request '{FORBIDDEN_TIER}' "
                f"by name. That tier orchestrates; it does not execute. Use "
                f"'{LANE_TIER}' for lane work or '{SWEEP_TIER}' for mechanical "
                f"sweeps.",
                "Agent spawn blocked: orchestrator tier requested by name.")
            return
        if model:
            return
        if stype in EXEMPT_TYPES:
            return                 # the type carries its own model
        out("deny",
            f"LOUD FAILURE - model-tiering rule: this Agent spawn declares no "
            f"model, so it would inherit the session model (the orchestrator "
            f"tier). Add model: '{LANE_TIER}' / '{SWEEP_TIER}', or use an "
            f"exempt agent type ({', '.join(sorted(EXEMPT_TYPES)) or 'none configured'}).",
            "Agent spawn blocked: no explicit model tier.")
        return

    # ---- 3/4. shell ------------------------------------------------------
    if tool in ("Bash", "PowerShell", "Shell"):
        cmd = ti.get("command") or ""
        form = blanket_add(cmd)
        if form:
            sweep = ""
            if PROJECT_ROOT:
                try:
                    p = subprocess.run(
                        ["git", "-C", PROJECT_ROOT, "status", "--porcelain"],
                        capture_output=True, text=True, timeout=10)
                    if p.returncode == 0:
                        sweep = sweep_preview(p.stdout)
                except Exception:
                    sweep = ""          # never let the preview become the story
            out("deny",
                f"LOUD FAILURE - blanket staging is banned in this repo (it "
                f"once swept an in-flight agent's scratch file into a commit). "
                f"Matched: {form!r}. Stage targeted paths: "
                f"git add <file> <file>.{sweep} `python tools/kit_doctor.py` "
                f"names the same files on demand, and `git add --dry-run` is "
                f"not blocked.",
                "Blocked: blanket staging - use targeted paths.")
            return
        if touches_protected(cmd):
            protected_verdict("command")
        return

    # ---- 4. writes -------------------------------------------------------
    if tool in ("Edit", "Write", "NotebookEdit"):
        fp = ti.get("file_path") or ti.get("notebook_path") or ""
        if touches_protected(fp):
            protected_verdict("edit")
        # No token and no match: stay SILENT so the harness's own permission
        # rules (settings.json `permissions.ask`) do the prompting. Two prompts
        # for one action trains people to click through both.
        return


if __name__ == "__main__":
    main()
