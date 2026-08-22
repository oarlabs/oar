#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/kit_render.py - the OPTIONAL mechanical substitution path.

    python tools/kit_render.py --target /path/to/your/repo
    python tools/kit_render.py --target . --set OWNER_ROLE=the owner
    python tools/kit_render.py --list        # what it renders, what it does not
    python tools/kit_render.py --selftest    # incl. three negative controls

    exit 0  PASS         every slot in every rendered file was filled, and the
                         `.kit-new` files were written.
    exit 1  INCOMPLETE   at least one slot could not be filled. The files are
                         STILL written, with the raw `{{SLOT}}` left in place
                         and every one of them named on stdout.
    exit 2  ABORTED      a refusal to start or to write: output would land
                         inside the kit clone, no `.git` above the target, a
                         `.kit-new` file already there, an unreadable template.
                         Never a render.

Read the VERDICT WORD, not `$?` alone - this kit judges runs by their output
line, and exit 2 is a refusal rather than a result.

==========================================================================
THIS IS THE OPTIONAL PATH. THE BY-HAND PATH IS THE DOCTRINE.
==========================================================================
`kit.config.example` states the kit's position and it still stands:
substitution is "by hand, deliberately, once ... the templates are documents a
human has to read and argue with before they bind anything." QUICKSTART.md
keeps that path as its primary route, and this tool is offered beside it, not
in place of it.

What the tool is for is the ONE thing hand substitution is bad at: getting the
same string into the same places without a typo. Seven adoption walks produced
transcription errors in five of them - a slot missed in one of three matcher
blocks, a path typed two ways, a header comment substituted into instead of
deleted. Those are mechanical failures, and a mechanical step removes them.
What it cannot do is read the guidance for you, and the guidance is why the
by-hand path is still first.

==========================================================================
WHAT IT RENDERS - SEVEN FILES, AND IT SAYS SO
==========================================================================
Exactly the seven files QUICKSTART has the adopter fill in:

    Step 4  modules/02-enforcement/settings.json.template -> .claude/settings.json
    Step 6  modules/01-governance/CLAUDE.md.template      -> CLAUDE.md
    Step 7  modules/04-ledgers/JUDGMENT-LEDGER.md         -> <LEDGERS_DIR>/
            modules/04-ledgers/FAILURE-FLOOR.md              <LEDGERS_DIR>/
            modules/04-ledgers/LESSONS.md                    <LEDGERS_DIR>/
            modules/04-ledgers/TOKEN-LEDGER.md               <LEDGERS_DIR>/
    Step 8  modules/08-collaboration/PROFILE-TEMPLATE.md  -> docs/collaboration-profile.md

The kit has 23 slot-carrying files under `modules/` (the number
`adoption_smoke.py` phase 10 reports). The other 16 are hand-rendered, and
`--list` prints them by name so the scope of this tool is a list rather than an
impression.

It does not copy the executable files - `verify.py`, `hook_model_gate.py`,
`hook_fixtures.py`, `statusline.py`, `deident_scan.py`. Those carry no slots;
they are copied and then EDITED, which is Step 4's six constants and the
thinking that goes with them.

==========================================================================
THE FIVE GUARDS, AND WHY EACH ONE IS THERE
==========================================================================
1. IT WRITES INSIDE THE TARGET REPOSITORY AND NOWHERE ELSE. Two containments,
   each checked on the resolved root and again on every output path:

   * NEVER INTO THE KIT CLONE. The kit is a checkout you pull; a generator that
     writes into it turns your next `git pull` into a conflict and your kit
     into a fork of itself.
   * NEVER OUTSIDE THE TARGET. `LEDGERS_DIR` is documented in
     `kit.config.example` as repo-relative, and `../shared-docs` is a plausible
     monorepo value rather than a contrived one. An output that resolves
     outside the repository you pointed at is an ABORT naming the path and the
     config key, and an absolute `LEDGERS_DIR` is refused by shape on both
     platforms - not silently made relative on one of them.

   Either violation is an ABORT (exit 2). Nothing is written on an abort.

2. IT NEVER OVERWRITES. Every render lands at `<name>.kit-new` beside the
   destination, and the tool prints a unified diff against the existing file
   so the change is read before it is taken. Moving `.kit-new` into place is a
   human act. Add `*.kit-new` to your `.gitignore` - QUICKSTART's optional-path
   note says so at the point it offers this tool. If a `.kit-new` file is
   already there, the run ABORTS rather than clobbering it; `--force` is the
   deliberate override.

3. SETTINGS ARE MERGED STRUCTURALLY, NEVER BY HAND. `.claude/settings.json` is
   the one destination that usually already exists, and the failure mode is
   named in the kit's own template, in the `__COMMENT__` block of
   `modules/02-enforcement/settings.json.template`:

       "ONE HOOK FILE, THREE MATCHER BLOCKS - not three hook files. [...]
        Wiring two blocks and forgetting the third is the classic silent
        hole: every fixture stays green and one whole class stops being
        enforced."

   A human merging two settings files by eye misses the third matcher block.
   This tool merges the parsed JSON: matcher blocks are matched on the SET of
   tool names their matcher selects (`Write|Edit|X` and `Edit|Write|X` are one
   block, not two), hook entries within a block by their `command`, and
   `permissions.ask` by set union. Keys the template does not own are left
   exactly as they were, and a value it cannot merge is never dropped in
   silence - it is replaced with a REVIEW note naming what was discarded.
   Because the merge is structural, a value carrying a double quote can no
   longer break the file it is substituted into - the SB-B failure in
   `KNOWN-ISSUES.md` is unreachable on this path.

4. IT PRINTS WHAT IT COULD NOT DO. Every `{{SLOT}}` with no value is named,
   with the file it is in and the config key that would fill it, and the run
   ends INCOMPLETE (exit 1). Every guidance header it strips is reported with
   its first line and its length, because a deleted header is content the
   adopter is now assumed to have read.

   A shipped placeholder value counts as UNSET, by the same rule the hook, the
   fixture harness and the status board use (`NONE`, empty, `your-...`,
   `/abs/path/...`, `<paste ...>`). The single documented exception is
   `RATIO_CEILING`, which QUICKSTART Step 7 names as the one shipped
   placeholder allowed to survive adoption.

5. `{{PROJECT_ROOT}}` IS RESOLVED, NEVER READ FROM CONFIG. It is resolved the
   way `adoption_smoke.py` resolves it for the settings template: the target
   repository root, as a forward-slash path. The `kit.config` key of the same
   name ships EMPTY on purpose and is a runtime fallback for `.git` discovery,
   not a source for this slot - `kit.config.example` says so in the same
   breath. `--set PROJECT_ROOT=...` is refused for the same reason.

   EVERY OTHER VALUE COMES FROM THE TARGET'S CONFIG, AND THE RUN NAMES IT.
   `kit.config` + `kit.config.local` are read from the target repository root,
   not by the four-step search the kit's other tools use - those tools live
   inside the repository they configure, this one does not, and `./kit.config`
   from a kit-clone shell resolves to the kit's own worked example.
   `$KIT_CONFIG` is honoured where it names a config OUTSIDE the kit and
   ignored with a loud warning where it names one inside it: QUICKSTART Step 2
   sets that variable at a kit path and says in its own words that failing to
   unset it "leaks into the rest of your session". Every run prints the config
   file it actually read, on the line below the repo.

==========================================================================
WHAT STILL CHECKS THIS TOOL
==========================================================================
`adoption_smoke.py` continues to build its adopter scaffold BY HAND, and its
phase 13 runs this tool over that same tree and diffs the two. Two independent
renderings of the same templates that must agree; a disagreement is a red in
the smoke, and it is deliberately not resolvable by pointing both at the same
code. Collapsing them to a single authority would delete the last independent
expectation of what a rendered kit file looks like.

WHICH SIDE WINS A DISAGREEMENT: neither, on its own authority. The hand model
is the expectation and this tool is the subject under test, so a red means
investigate BOTH - and the arbiter is the QUICKSTART step the hand model
transcribes. That is not theoretical: on phase 13's first run the two
disagreed and the DOCUMENT ruled for the tool.
"""

from __future__ import annotations

import argparse
import copy
import difflib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

KIT = Path(__file__).resolve().parent.parent

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
if os.name == "nt":
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
    except Exception:
        GREEN = RED = YELLOW = BOLD = RESET = ""

SLOT = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

# The placeholder rule, shared verbatim with hook_fixtures.py. Three readers
# disagreeing about what "configured" means is how a slot comes to be filled
# with the word that meant it was not.
PLACEHOLDER_WORDS = {"", "none", "null", "todo", "<unset>", "tbd", "changeme"}
PLACEHOLDER_SHAPES = (
    "your-", "/abs/path", "c:/abs/path", "<", "derive-from",
    "https://example.invalid", "/path/to/", "example.invalid",
)

# QUICKSTART Step 7: "One shipped placeholder is allowed to survive this
# checkpoint, by name: RATIO_CEILING, which ships as `derive-from-your-own-data`
# ... Replace it the first time you have three stages of real numbers - not
# before." One named exception, not a general softening of the rule.
PLACEHOLDER_EXEMPT_KEYS = {"RATIO_CEILING"}

# The guidance-header marker words. A leading `<!-- ... -->` comment is only
# treated as a header - and therefore stripped - if it says so about itself.
# Three different wordings are live in the kit and each step's checkpoint greps
# for its own; matching all three here is what keeps this tool honest against
# every one of them.
HEADER_MARKERS = (
    "DELETE THIS COMMENT BLOCK",       # 01-governance/CLAUDE.md.template
    "SKELETON",                        # 04-ledgers/*.md
    "Delete this block on adoption",   # 04-ledgers/*.md
    "Delete this comment on adoption",  # 08-collaboration/PROFILE-TEMPLATE.md
    "TEMPLATE",                        # both of the above
)


# ==========================================================================
# THE MANIFEST: seven files, and the sixteen this tool does not touch
# ==========================================================================
# (template path in the kit, destination in the target, kind, QUICKSTART step)
RENDERS = (
    ("modules/02-enforcement/settings.json.template",
     ".claude/settings.json", "json", "Step 4"),
    ("modules/01-governance/CLAUDE.md.template",
     "CLAUDE.md", "text", "Step 6"),
    ("modules/04-ledgers/JUDGMENT-LEDGER.md",
     "{LEDGERS_DIR}/JUDGMENT-LEDGER.md", "text", "Step 7"),
    ("modules/04-ledgers/FAILURE-FLOOR.md",
     "{LEDGERS_DIR}/FAILURE-FLOOR.md", "text", "Step 7"),
    ("modules/04-ledgers/LESSONS.md",
     "{LEDGERS_DIR}/LESSONS.md", "text", "Step 7"),
    ("modules/04-ledgers/TOKEN-LEDGER.md",
     "{LEDGERS_DIR}/TOKEN-LEDGER.md", "text", "Step 7"),
    # Step 8 names this destination literally, so this tool does too rather
    # than routing it through LEDGERS_DIR: the rules file rendered at Step 6
    # points at `<KNOWLEDGE_DIR>/collaboration-profile.md`, and the repo copy
    # is the mirror the document puts in `docs/`.
    ("modules/08-collaboration/PROFILE-TEMPLATE.md",
     "docs/collaboration-profile.md", "text", "Step 8"),
)


def slot_carrying_module_files(kit: Path) -> list[str]:
    """Every file under modules/ that uses a slot - the population phase 10 of
    the adoption smoke counts. Used to print the honest remainder."""
    out = []
    for f in sorted((kit / "modules").rglob("*")):
        if not f.is_file():
            continue
        try:
            if SLOT.search(f.read_text(encoding="utf-8")):
                out.append(f.relative_to(kit).as_posix())
        except (OSError, UnicodeDecodeError):
            continue
    return out


# ==========================================================================
# THE PURE LAYER - everything above the RUNNING LAYER banner is testable
# without a filesystem, and --selftest exercises it directly.
# ==========================================================================
def is_placeholder(value: str) -> bool:
    """Pure, and the same rule the hook, the fixture harness and the board
    apply. `PROTECTED_PATH = NONE` is the absence of a path, not a path."""
    v = (value or "").strip()
    if v.lower() in PLACEHOLDER_WORDS:
        return True
    low = v.lower()
    return any(low.startswith(p) or low == p.rstrip("/")
               for p in PLACEHOLDER_SHAPES)


def usable(key: str, value: str) -> bool:
    """A value this tool will substitute. Placeholders are UNSET, except the
    one key QUICKSTART Step 7 names."""
    if key in PLACEHOLDER_EXEMPT_KEYS:
        return bool((value or "").strip())
    return not is_placeholder(value)


def strip_header(text: str):
    """(text_without_the_guidance_header, header_or_None).

    Removes only the FIRST `<!-- ... -->` block, and only when it identifies
    itself as a template header. Everything BEFORE it survives - the
    collaboration profile opens with YAML front matter above its header
    comment, and that front matter is content (`type`, `status`, `sources`),
    not guidance. A strip rule that starts at the top of the file and runs to
    the first `-->` deletes it silently."""
    i = text.find("<!--")
    if i < 0:
        return text, None
    j = text.find("-->", i)
    if j < 0:
        return text, None
    header = text[i:j + 3]
    if not any(m in header for m in HEADER_MARKERS):
        return text, None
    return text[:i] + text[j + 3:].lstrip("\n"), header


def substitute(text: str, values: dict) -> str:
    """ONE PASS, so the result cannot depend on key order.

    A sequential `str.replace` per key expands a slot that appears inside an
    earlier key's VALUE - `PROJECT_NAME = Proj {{OWNER_ROLE}} X` renders as
    `Proj the owner X` when OWNER_ROLE is substituted after PROJECT_NAME, and
    leaves the raw token (reported UNFILLED) when it is substituted before.
    The same config then renders two different files depending on the order the
    keys happen to sit in. A single regex pass substitutes template text only,
    never substituted-in text, so the output is a function of the config rather
    than of its line order."""
    return SLOT.sub(
        lambda m: values.get(m.group(1), m.group(0)), text)


def unfilled(text: str) -> list[str]:
    return sorted(set(SLOT.findall(text)))


def walk_strings(node, fn):
    """Apply `fn` to every string in a parsed-JSON structure."""
    if isinstance(node, dict):
        return {k: walk_strings(v, fn) for k, v in node.items()}
    if isinstance(node, list):
        return [walk_strings(v, fn) for v in node]
    if isinstance(node, str):
        return fn(node)
    return node


def collect_slots(node) -> list[str]:
    found: set[str] = set()

    def see(s):
        found.update(SLOT.findall(s))
        return s
    walk_strings(node, see)
    return sorted(found)


def render_settings(template_text: str, values: dict):
    """(settings_dict, stripped_header, omitted_notes).

    Structural, not textual. The template is valid JSON with its slots inside
    strings on purpose, so the whole substitution can happen on the parsed
    object and be re-serialised by `json.dumps` - which is what makes a value
    containing a double quote harmless here (KNOWN-ISSUES SB-B)."""
    obj = json.loads(template_text)
    header = None
    if "__COMMENT__" in obj:
        block = obj.pop("__COMMENT__")
        header = "\n".join(block) if isinstance(block, list) else str(block)

    omitted = []
    # QUICKSTART Step 4's two conditional blocks, applied mechanically. Leaving
    # either one in with an unfilled slot is worse than deleting it: the
    # harness prompts about a directory that does not exist, or the status line
    # is a command nobody can start.
    if not usable("PROTECTED_PATH", values.get("PROTECTED_PATH", "")):
        perms = obj.get("permissions")
        if isinstance(perms, dict) and "ask" in perms:
            perms.pop("ask")
            omitted.append(
                "permissions.ask DELETED - PROTECTED_PATH is unset, and "
                "QUICKSTART Step 4 says to delete the whole block rather than "
                "leave the harness prompting about a path that does not exist")
            if not perms:
                obj.pop("permissions")
    if not usable("STATUSLINE_CMD", values.get("STATUSLINE_CMD", "")):
        if "statusLine" in obj:
            obj.pop("statusLine")
            omitted.append(
                "statusLine DELETED - STATUSLINE_CMD is unset, and Step 4 says "
                "NONE is not a command. Set it in kit.config.local (it is an "
                "absolute path) and re-run to get the block back")

    obj = walk_strings(obj, lambda s: substitute(s, values))
    return obj, header, omitted


def matcher_key(matcher):
    """The comparison key for a matcher block. Pure.

    A Claude Code matcher is a `|`-separated list of tool names, and the order
    of that list carries no meaning: `Write|Edit|NotebookEdit` and
    `Edit|Write|NotebookEdit` select exactly the same calls. Comparing the raw
    strings makes the second one look like a matcher nobody had wired, so the
    merge appends a duplicate block — the gate then fires twice on every
    matching call — and prints "was NOT wired", which tells the one human who
    could catch it that there is nothing to look at. A merge the docstring
    calls structural cannot compare its keys as text."""
    if not isinstance(matcher, str):
        return ("<non-string>", repr(matcher))
    return frozenset(p.strip() for p in matcher.split("|") if p.strip())


def merge_settings(existing: dict, rendered: dict):
    """(merged, notes). The mechanical answer to the hand-merge the settings
    template warns about.

    Rules, all of them structural:
      * a top-level key the template owns is replaced by the rendered value;
      * a top-level key it does not own is left exactly as it was;
      * `permissions.<list>` is a union, existing order first;
      * `hooks.<event>` is a list of matcher blocks, matched by `matcher`; a
        block that is not there is APPENDED, and within a block a hook is
        matched by `command` - same command, rendered wins; new command,
        appended. This is the step a human does by eye and gets wrong on the
        third block."""
    merged = copy.deepcopy(existing)
    notes = []

    for key, val in rendered.items():
        if key in ("permissions", "hooks"):
            continue
        if merged.get(key) != val:
            notes.append(f"{key}: replaced with the rendered value")
        merged[key] = val

    rp = rendered.get("permissions")
    if isinstance(rp, dict):
        mp = merged.setdefault("permissions", {})
        if not isinstance(mp, dict):
            mp = {}
            merged["permissions"] = mp
        for sub, entries in rp.items():
            if not isinstance(entries, list):
                mp[sub] = entries
                continue
            have = mp.get(sub)
            if isinstance(have, list):
                have = list(have)
            else:
                # MINOR-6: never discard an adopter's value in silence. The
                # neighbouring hook merge is careful not to pick a winner; this
                # branch used to replace a malformed value with [] and say
                # nothing, which is the same failure with a smaller blast area.
                if have is not None:
                    notes.append(
                        f"permissions.{sub}: REVIEW — the existing value was "
                        f"{type(have).__name__}, not a list, so it could not "
                        f"be merged. It has been REPLACED by the rendered "
                        f"entries; the discarded value was {have!r}")
                have = []
            added = [e for e in entries if e not in have]
            mp[sub] = have + added
            if added:
                notes.append(f"permissions.{sub}: added {len(added)} "
                             f"entr{'y' if len(added) == 1 else 'ies'}")

    rh = rendered.get("hooks")
    if isinstance(rh, dict):
        mh = merged.setdefault("hooks", {})
        if not isinstance(mh, dict):
            mh = {}
            merged["hooks"] = mh
        for event, blocks in rh.items():
            if not isinstance(blocks, list):
                mh[event] = blocks
                continue
            have = mh.get(event)
            if isinstance(have, list):
                have = list(have)
            else:
                if have is not None:
                    notes.append(
                        f"hooks.{event}: REVIEW — the existing value was "
                        f"{type(have).__name__}, not a list of matcher blocks, "
                        f"so it could not be merged. It has been REPLACED by "
                        f"the rendered blocks; the discarded value was "
                        f"{have!r}")
                have = []
            for block in blocks:
                matcher = block.get("matcher") if isinstance(block, dict) else None
                want = matcher_key(matcher)
                slot_i = next(
                    (i for i, b in enumerate(have)
                     if isinstance(b, dict)
                     and matcher_key(b.get("matcher")) == want),
                    None)
                if slot_i is None:
                    have.append(copy.deepcopy(block))
                    notes.append(f"hooks.{event}: matcher {matcher!r} was NOT "
                                 f"wired - block APPENDED")
                    continue
                target = have[slot_i]
                # MAJOR-2: the block was found by NORMALISED matcher, so its
                # spelling may differ from the template's. Say so rather than
                # rewriting it: the two are equivalent to the harness, and
                # silently restyling a line the adopter wrote is not this
                # tool's call.
                spelled = target.get("matcher")
                if spelled != matcher:
                    notes.append(
                        f"hooks.{event}: matcher {spelled!r} already covers "
                        f"the same tools as the template's {matcher!r} "
                        f"(equivalent, different spelling) — merged into the "
                        f"existing block rather than appending a duplicate. "
                        f"The existing spelling is left as it is")
                cur = target.get("hooks")
                if isinstance(cur, list):
                    cur = list(cur)
                else:
                    if cur is not None:
                        notes.append(
                            f"hooks.{event}[{spelled!r}]: REVIEW — the block's "
                            f"`hooks` value was {type(cur).__name__}, not a "
                            f"list, so it could not be merged. REPLACED; the "
                            f"discarded value was {cur!r}")
                    cur = []
                had = len(cur)
                for hk in block.get("hooks", []):
                    cmd = hk.get("command") if isinstance(hk, dict) else None
                    at = next((i for i, h in enumerate(cur)
                               if isinstance(h, dict)
                               and h.get("command") == cmd), None)
                    if at is None:
                        cur.append(copy.deepcopy(hk))
                        # A block that already had hooks, none of which match,
                        # is usually a STALE ABSOLUTE PATH - the settings file
                        # from another machine, or from before the repo moved.
                        # Merging leaves two commands under one matcher, which
                        # runs the gate twice and hides which copy decided.
                        # Say so; do not silently pick a winner.
                        notes.append(
                            f"hooks.{event}[{matcher!r}]: command added"
                            if not had else
                            f"hooks.{event}[{matcher!r}]: REVIEW — the block "
                            f"already had {had} hook(s) with different "
                            f"command(s) and the rendered command was "
                            f"APPENDED. Usually a stale absolute path; delete "
                            f"the one that is not yours")
                    elif cur[at] != hk:
                        cur[at] = copy.deepcopy(hk)
                        notes.append(f"hooks.{event}[{matcher!r}]: command "
                                     f"already wired, entry refreshed")
                target["hooks"] = cur
            mh[event] = have
    return merged, notes


def find_repo_root(start: Path, has_git):
    """(root, how) or (None, why). Pure given `has_git`, so --selftest walks
    both branches.

    GUARD 5. This is deliberately NOT `verify.py`'s three-branch resolver: the
    `PROJECT_ROOT` config key is not consulted, because the slot this value
    fills is not that key. `kit.config.example`: 'nothing reads a config key to
    FILL a template slot ... whether or not the key here is set.' No `.git`
    ancestor is a refusal, not a fallback - an absolute path that is wrong is
    worse than an absolute path that is missing, because `--armed` reports the
    second one and certifies the first."""
    for d in [start, *start.parents]:
        if has_git(d):
            return d, "the nearest ancestor containing .git"
    return None, ("no ancestor of the target contains .git - this tool fills "
                  "{{PROJECT_ROOT}} with a resolved repository root and will "
                  "not guess one")


def path_inside(child, parent) -> bool:
    """True when `child` is `parent` or lives under it. Case-folded and
    symlink-resolved, because the kit clone and the target are routinely two
    spellings of the same directory on Windows."""
    try:
        c = os.path.normcase(os.path.realpath(str(child)))
        p = os.path.normcase(os.path.realpath(str(parent)))
    except (OSError, ValueError):
        return False
    return c == p or c.startswith(p.rstrip(os.sep) + os.sep)


def read_target_config(root: Path, kit: Path):
    """The TARGET repository's kit.config, overlaid with its kit.config.local.

    DELIBERATELY NOT the four-step search every other tool in this kit uses.
    Those tools live inside the repository they configure, so "the current
    working directory" and "walk up from my own directory" both land on the
    right file. This one runs FROM the kit clone and points AT another
    repository, so both of those answers are wrong - and wrong in the quietest
    way, because the kit ships a filled-in `kit.config` of its own as a worked
    example. A run launched from the kit clone would have rendered the kit's
    values into the adopter's files and said PASS.

    $KIT_CONFIG still wins where it names a config outside the kit - it is an
    explicit instruction rather than an accident of where the shell happened to
    be - but NOT where it names one inside the kit checkout. QUICKSTART Step 2
    tells the reader to set that variable at a kit path and warns, in its own
    words, that failing to unset it afterwards "leaks into the rest of your
    session". The tool is offered two steps later in the same session, so the
    leaked variable is a state the document itself creates, and honouring it
    renders the KIT's values into the adopter's repository. The cwd route was
    already closed; this is the same class arriving by the other road.

    Returns (cfg, warnings). Warnings are returned rather than printed so they
    land in the run report beside everything else the run decided."""
    base = root / "kit.config"
    warnings: list[str] = []
    env = os.environ.get("KIT_CONFIG")
    if env:
        envp = Path(env)
        if not envp.is_file():
            warnings.append(
                f"$KIT_CONFIG points at {env!r}, which is not a file - using "
                f"the target's kit.config instead.")
        elif path_inside(envp, kit):
            warnings.append(
                f"$KIT_CONFIG points INSIDE THE KIT CLONE ({envp.as_posix()}) "
                f"and has been IGNORED. That variable renders the kit's own "
                f"example values into your repository. QUICKSTART Step 2 sets "
                f"it and tells you to unset it afterwards - do that now "
                f"(`unset KIT_CONFIG`, or `Remove-Item Env:KIT_CONFIG` in "
                f"pwsh). Using the target's kit.config instead.")
        else:
            base = envp

    cfg: dict[str, str] = {}
    found = False
    for path in (base, base.with_name("kit.config.local")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        found = True
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    cfg["_source"] = str(base) if found else ""
    return cfg, warnings


# ==========================================================================
# THE RUNNING LAYER
# ==========================================================================
class Result:
    """Everything a run decided, so --selftest can assert on it without
    parsing stdout."""

    def __init__(self):
        self.code = 0
        self.verdict = "PASS"
        self.abort = ""
        self.written: dict[str, str] = {}     # rel path -> text written
        self.unfilled: dict[str, list] = {}   # rel path -> slot names
        self.stripped: dict[str, str] = {}    # rel path -> header text
        self.steps: dict[str, str] = {}       # rel path -> QUICKSTART step
        self.omitted: list[str] = []
        self.merge_notes: list[str] = []
        self.diffs: dict[str, list] = {}
        self.root = None
        self.root_how = ""
        self.values: dict[str, str] = {}
        self.config_source = ""
        self.notes: list[str] = []            # decisions the run made quietly
        self.log: list[str] = []

    def say(self, line: str):
        self.log.append(line)

    def aborted(self, why: str):
        self.code, self.verdict, self.abort = 2, "ABORTED", why
        return self


def render(kit: Path, target: Path, overrides: dict | None = None,
           force: bool = False, write: bool = True) -> Result:
    """The whole run, as a value. `write=False` renders and decides without
    touching the filesystem, which is how the selftest checks the abort paths
    that must not leave a file behind."""
    r = Result()
    overrides = dict(overrides or {})

    if "PROJECT_ROOT" in overrides:
        return r.aborted(
            "--set PROJECT_ROOT is refused. This tool RESOLVES the repository "
            "root (see guard 5 in its docstring); a typed value is the failure "
            "it exists to remove.")

    root, how = find_repo_root(target.resolve(), lambda d: (d / ".git").exists())
    if root is None:
        return r.aborted(how)
    r.root, r.root_how = root, how

    # GUARD 1, checked on the ROOT before any path is computed, so the message
    # names the real mistake rather than the first file it would have hit.
    if path_inside(root, kit):
        return r.aborted(
            f"the resolved target root {root.as_posix()} is inside the kit "
            f"clone {kit.as_posix()}. This tool renders FROM a kit checkout "
            f"INTO your own repository; writing into the kit turns your next "
            f"`git pull` into a conflict. Point --target at your project.")

    cfg, cfg_warnings = read_target_config(root, kit)
    r.config_source = cfg.get("_source", "")
    for w in cfg_warnings:
        r.say(f"{YELLOW}CONFIG WARNING: {w}{RESET}")
    if not r.config_source:
        r.say(f"{YELLOW}CONFIG WARNING: no kit.config under "
              f"{root.as_posix()} - every value must come from --set, and "
              f"every slot without one will be reported UNFILLED.{RESET}")
    values = {k: v for k, v in cfg.items()
              if not k.startswith("_") and usable(k, v)}
    for k, v in overrides.items():
        if usable(k, v):
            values[k] = v
        else:
            r.say(f"{YELLOW}--set {k}={v!r} is a shipped placeholder value and "
                  f"reads as UNSET; ignored.{RESET}")
    # GUARD 5: resolved, and assigned AFTER the config and the overrides, so
    # the resolved value is the one that survives whatever either of them said.
    # (Precedence, not iteration position - assigning to an existing dict key
    # keeps that key where it was.)
    values["PROJECT_ROOT"] = root.as_posix()
    r.values = values

    # MINOR-7: a fallback is a decision the run made on the adopter's behalf,
    # and four files land in a directory nobody chose. `usable()` filters
    # placeholders out of `values`, so `LEDGERS_DIR = NONE` arrives here too.
    if "LEDGERS_DIR" in values:
        ledgers = values["LEDGERS_DIR"]
    else:
        ledgers = "docs"
        raw = cfg.get("LEDGERS_DIR")
        r.notes.append(
            f"LEDGERS_DIR is "
            + (f"set to {raw!r}, which reads as UNSET"
               if raw is not None else "not set")
            + f" - the four ledgers default to {ledgers!r}. Set LEDGERS_DIR in "
              f"kit.config if that is not where you want them.")

    # MINOR-11: Step 8's other branch. When KNOWLEDGE_DIR is an absolute path
    # outside the repo, QUICKSTART puts the profile THERE and treats
    # docs/collaboration-profile.md as a mirror. This tool writes the mirror
    # either way - it never writes outside the target repo (guard 1b) - so on
    # that branch it must say which copy it did not write.
    kd = values.get("KNOWLEDGE_DIR", "")
    if kd and (Path(kd).is_absolute() or re.match(r"^([A-Za-z]:|[/\\])", kd)):
        r.notes.append(
            f"KNOWLEDGE_DIR is an absolute path ({kd}), so QUICKSTART Step 8 "
            f"makes {kd}/collaboration-profile.md your source of truth and "
            f"docs/collaboration-profile.md a mirror. This tool renders the "
            f"MIRROR only - it does not write outside the target repository. "
            f"Copy it across yourself, or render on the repo-path branch.")

    plan = []
    for tmpl_rel, dest_pat, kind, step in RENDERS:
        tmpl = kit / tmpl_rel
        if not tmpl.is_file():
            return r.aborted(f"missing kit template {tmpl_rel}")
        # MAJOR-1: a destination has to be REPO-RELATIVE, and the two ways it
        # can stop being one fail differently on the two platforms this tool
        # claims. `.strip("/")` used to turn a POSIX absolute path into a
        # relative one silently, while a drive-qualified Windows path passed
        # through `pathlib` intact and escaped - the same config behaving two
        # ways. Refuse both shapes by name; strip only a TRAILING separator,
        # which is a spelling, not an escape.
        dest_rel = dest_pat.replace("{LEDGERS_DIR}", ledgers).rstrip("/\\")
        if re.match(r"^([A-Za-z]:|[/\\])", dest_rel) or Path(dest_rel).is_absolute():
            return r.aborted(
                f"the destination {dest_rel!r} is an absolute path. "
                f"`kit.config.example` documents LEDGERS_DIR as "
                f"repo-relative (LEDGERS_DIR = {ledgers!r}); this tool renders "
                f"into the target repository only. Give a path relative to "
                f"{root.as_posix()}.")
        dest = root / dest_rel
        out = dest.with_name(dest.name + ".kit-new")
        # GUARD 1 again, per output path. Belt and braces: a LEDGERS_DIR of
        # `../oar/modules` is a configuration nobody would write on
        # purpose and exactly the kind this has to survive.
        if path_inside(out, kit):
            return r.aborted(
                f"the output {out.as_posix()} would land inside the kit clone "
                f"{kit.as_posix()} (LEDGERS_DIR = {ledgers!r}). Refusing.")
        # GUARD 1b, the containment the first version was missing entirely.
        # `LEDGERS_DIR = ../shared-docs` is a plausible monorepo value, not a
        # contrived one, and it wrote four files outside the repository the
        # tool was pointed at and reported PASS. A tool sold as removing the
        # mistakes hand substitution makes must not add one the by-hand path
        # does not have. Same double-check discipline as guard 1: the root is
        # checked once, every output path is checked again.
        if not path_inside(out, root):
            key = ("LEDGERS_DIR = " + repr(ledgers)
                   if "{LEDGERS_DIR}" in dest_pat
                   else "destination " + repr(dest_pat))
            return r.aborted(
                f"the output {out.as_posix()} would land OUTSIDE the target "
                f"repository {root.as_posix()} ({key}). `kit.config.example` "
                f"documents LEDGERS_DIR as repo-relative, and this tool "
                f"renders into the repository you pointed it at and nowhere "
                f"else. Refusing.")
        # GUARD 2, asserted rather than assumed: the destination is NEVER the
        # adopter's file.
        if out.name == dest.name or not out.name.endswith(".kit-new"):
            return r.aborted(f"internal: refusing to write {out.as_posix()}, "
                             f"which is not a .kit-new path")
        if out.exists() and not force:
            return r.aborted(
                f"{out.as_posix()} already exists. This tool never overwrites; "
                f"read it, move it into place or delete it, then re-run. "
                f"`--force` overwrites it deliberately.")
        plan.append((tmpl, tmpl_rel, dest, dest_rel, out, kind, step))

    for tmpl, tmpl_rel, dest, dest_rel, out, kind, step in plan:
        try:
            text = tmpl.read_text(encoding="utf-8")
        except OSError as e:
            return r.aborted(f"cannot read {tmpl_rel}: {e}")

        if kind == "json":
            obj, header, omitted = render_settings(text, values)
            r.omitted.extend(omitted)
            if header:
                r.stripped[dest_rel] = header
            if dest.is_file():
                try:
                    existing = json.loads(dest.read_text(encoding="utf-8"))
                except (OSError, ValueError) as e:
                    return r.aborted(
                        f"{dest_rel} exists but is not readable JSON ({e}). A "
                        f"structural merge needs a parseable file; fix or move "
                        f"it aside, then re-run.")
                if not isinstance(existing, dict):
                    return r.aborted(f"{dest_rel} is not a JSON object")
                obj, notes = merge_settings(existing, obj)
                r.merge_notes.extend(f"{dest_rel}: {n}" for n in notes)
            left = collect_slots(obj)
            rendered_text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
        else:
            body, header = strip_header(text)
            if header:
                r.stripped[dest_rel] = header
            rendered_text = substitute(body, values)
            left = unfilled(rendered_text)

        if left:
            r.unfilled[dest_rel] = left
        r.written[dest_rel] = rendered_text
        r.steps[dest_rel] = step

        old = dest.read_text(encoding="utf-8").splitlines() if dest.is_file() else None
        if old is None:
            r.diffs[dest_rel] = []
        else:
            r.diffs[dest_rel] = list(difflib.unified_diff(
                old, rendered_text.splitlines(),
                fromfile=dest_rel, tofile=dest_rel + ".kit-new", lineterm=""))

        if write:
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(rendered_text, encoding="utf-8")
            except OSError as e:
                return r.aborted(f"cannot write {out.as_posix()}: {e}")

    if r.unfilled:
        r.code, r.verdict = 1, "INCOMPLETE"
    return r


def do_list(kit: Path) -> int:
    rendered = {t for t, _, _, _ in RENDERS}
    every = slot_carrying_module_files(kit)
    print(f"{BOLD}RENDERED BY THIS TOOL - the seven files QUICKSTART fills"
          f"{RESET}")
    for tmpl_rel, dest, _kind, step in RENDERS:
        print(f"  {step:<7} {tmpl_rel}\n          -> {dest}")
    rest = [f for f in every if f not in rendered]
    print(f"\n{BOLD}NOT RENDERED - hand-rendered, deliberately{RESET}")
    print(f"  {len(every)} files under modules/ carry slots. This tool renders "
          f"{len(rendered)} of them.\n  The other {len(rest)} are yours to "
          f"open and read:")
    for f in rest:
        print(f"    {f}")
    print("\n  The executable files QUICKSTART copies - verify.py, "
          "hook_model_gate.py,\n  hook_fixtures.py, statusline.py, "
          "deident_scan.py - carry no slots and are\n  not rendered: they are "
          "copied, then EDITED (Step 4's six constants).")
    return 0


def report(r: Result, diff_lines: int = 40) -> int:
    for line in r.log:
        print(line)
    if r.code == 2:
        print(f"\n{RED}KIT RENDER: ABORTED — {r.abort}{RESET}")
        return 2

    print(f"repo      : {r.root.as_posix()}  ({r.root_how})")
    # The provenance of the OTHER 21 values. The run has always named where
    # PROJECT_ROOT came from and stayed silent about the config that supplied
    # everything else, which is the half an adopter cannot check by eye.
    print(f"config    : {r.config_source or '<none found - --set only>'}")
    print(f"PROJECT_ROOT resolved to {r.values['PROJECT_ROOT']!r} — not read "
          f"from kit.config (guard 5)")
    print(f"values    : {len(r.values)} usable keys")

    for rel in r.written:
        # Naming the step is how a Step-4 reader sees that four ledgers and a
        # collaboration profile belong to steps they have not reached yet. The
        # profile in particular is filled from a seed interview at Step 8, and
        # a rendered template looks finished.
        print(f"\n{BOLD}{rel}.kit-new{RESET}  ({r.steps.get(rel, '')})")
        if rel in r.stripped:
            head = r.stripped[rel]
            # The first line that says something: not the comment delimiters,
            # not a rule of `=` characters.
            first = next((l.strip() for l in head.splitlines()
                          if l.strip() not in ("<!--", "-->")
                          and re.search(r"[A-Za-z]", l)), "")
            print(f"  header STRIPPED ({len(head.splitlines())} lines): "
                  f"{first[:96]}")
        if rel in r.unfilled:
            for s in r.unfilled[rel]:
                print(f"  {RED}UNFILLED{RESET} {{{{{s}}}}} — set {s} in "
                      f"kit.config (or kit.config.local if it is an absolute "
                      f"path), or pass --set {s}=...")
        d = r.diffs.get(rel)
        if d is None or not d:
            print("  NEW — no existing file at this path to diff against")
        else:
            print(f"  diff vs the file already there ({len(d)} lines):")
            for line in d[:diff_lines]:
                col = GREEN if line.startswith("+") else (
                    RED if line.startswith("-") else "")
                print(f"    {col}{line}{RESET}" if col else f"    {line}")
            if len(d) > diff_lines:
                print(f"    ... {len(d) - diff_lines} more diff lines — read "
                      f"the file")

    for note in r.omitted:
        print(f"\n{YELLOW}OMITTED{RESET} {note}")
    for note in r.notes:
        print(f"\n{YELLOW}NOTE{RESET} {note}")
    if r.merge_notes:
        print(f"\n{BOLD}STRUCTURAL MERGE{RESET} — settings merged as JSON, not "
              f"by hand (guard 3)")
        for n in r.merge_notes:
            print(f"  {n}")

    print(f"\nNothing was moved into place. Read each .kit-new, then move it "
          f"over the real file yourself.")
    print(f"Add `*.kit-new` to your .gitignore if you have not already.")
    if r.stripped:
        print(f"The stripped headers are guidance this tool deleted on your "
              f"behalf — read them in the templates the first time.")

    n_slots = sum(len(v) for v in r.unfilled.values())
    if r.code == 1:
        print(f"\n{RED}KIT RENDER: INCOMPLETE — {len(r.written)} files "
              f"written, {n_slots} unfilled slot(s) in {len(r.unfilled)} "
              f"file(s), each named above{RESET}")
        return 1
    print(f"\n{GREEN}KIT RENDER: PASS — {len(r.written)} files written, every "
          f"slot filled{RESET}")
    return 0


# ==========================================================================
# SELFTEST - the negative controls come first, because a tool that only
# proves its happy path proves that it runs, not that it guards.
# ==========================================================================
MIN_CFG = """\
PROJECT_NAME = Selftest Project
ORCHESTRATOR_TIER = top-tier
LANE_TIER = lane-tier
SWEEP_TIER = sweep-tier
MODEL_EXEMPT_TYPES = fork
FORBIDDEN_SPAWN_TIER = top-tier
GATE_COMMAND = python tools/verify.py
CERT_PATHS = src
CERT_TOKEN_FILE = .claude/cert-green.json
OWNER_ROLE = the owner
COORDINATOR_ROLE = the coordinator
KNOWLEDGE_DIR = docs/knowledge
LEDGERS_DIR = docs
REPORTS_DIR = docs/reports
CHECKPOINT_GLOB = docs/CHECKPOINT-*.md
DEMOTION_REVIEW_STAGES = 3
PROSE_VOICE = technical
PYTHON_BIN = python
RATIO_CEILING = derive-from-your-own-data
"""


def _target(tmp: Path, name: str, cfg: str = MIN_CFG, local: str = "") -> Path:
    """A throwaway adopter repo. `.git` is a bare directory on purpose: the
    resolver only asks whether it exists, so the selftest needs no subprocess
    and no git on PATH."""
    root = tmp / name
    (root / ".git").mkdir(parents=True)
    (root / "kit.config").write_text(cfg, encoding="utf-8")
    if local:
        (root / "kit.config.local").write_text(local, encoding="utf-8")
    return root


def selftest() -> int:
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}"
              + ("" if good else f"\n        got  {got!r}\n        want {want!r}"))

    # Canonical from the source, for the same reason the adoption smoke does it
    # (kit commit f608230's Windows CI red): `tempfile.gettempdir()` can hand
    # back an 8.3 short path, and a check that compares a computed path against
    # a temp path then depends on which spelling the runner's TEMP happens to
    # use. Every comparison below already resolves its expectation side, so
    # this is defence in depth rather than a fix - but it means a check added
    # later without `.resolve()` does not quietly become platform-dependent.
    tmp = Path(tempfile.mkdtemp(prefix="kit-render-selftest-")).resolve()
    try:
        full = dict(PROTECTED_PATH="/somewhere/protected",
                    STATUSLINE_CMD="python /r/tools/statusline.py")

        print(f"{BOLD}=== A. NEGATIVE CONTROL 1: an unfilled slot ==="
              f"{RESET}")
        # OWNER_ROLE removed from the config. It is used by five of the seven
        # files, so a tool that silently shipped a raw slot would ship five.
        thin = "\n".join(l for l in MIN_CFG.splitlines()
                         if not l.startswith("OWNER_ROLE"))
        t1 = _target(tmp, "unfilled", cfg=thin)
        r1 = render(KIT, t1, full)
        check("an unfilled slot is INCOMPLETE, exit 1", r1.code, 1)
        check("...with the verdict word", r1.verdict, "INCOMPLETE")
        check("...and OWNER_ROLE is named in CLAUDE.md",
              "OWNER_ROLE" in r1.unfilled.get("CLAUDE.md", []), True)
        check("...and in a ledger too, not just the first file",
              "OWNER_ROLE" in r1.unfilled.get("docs/LESSONS.md", []), True)
        check("...and the file is STILL written, raw slot and all",
              (t1 / "CLAUDE.md.kit-new").is_file(), True)
        check("...carrying the raw token so a grep finds it",
              "{{OWNER_ROLE}}" in (t1 / "CLAUDE.md.kit-new").read_text(
                  encoding="utf-8"), True)
        # A placeholder VALUE is the same news as a missing key.
        t1b = _target(tmp, "placeholder",
                      cfg=MIN_CFG.replace("OWNER_ROLE = the owner",
                                          "OWNER_ROLE = your-owner-role"))
        r1b = render(KIT, t1b, full)
        check("a shipped placeholder value reads as UNSET", r1b.code, 1)
        check("...and RATIO_CEILING is the one named exception that does not",
              "RATIO_CEILING" in r1b.unfilled.get("docs/TOKEN-LEDGER.md", []),
              False)

        print(f"\n{BOLD}=== B. NEGATIVE CONTROL 2: would-overwrite ==={RESET}")
        t2 = _target(tmp, "overwrite")
        squatter = t2 / "CLAUDE.md.kit-new"
        squatter.write_text("MINE - do not clobber\n", encoding="utf-8")
        r2 = render(KIT, t2, full)
        check("an existing .kit-new ABORTS, exit 2", r2.code, 2)
        check("...with the verdict word", r2.verdict, "ABORTED")
        check("...naming the path", "CLAUDE.md.kit-new" in r2.abort, True)
        check("...and the squatter is BYTE-IDENTICAL afterwards",
              squatter.read_text(encoding="utf-8"), "MINE - do not clobber\n")
        check("...and nothing else was written either (the abort is total)",
              (t2 / ".claude" / "settings.json.kit-new").exists(), False)
        r2f = render(KIT, t2, full, force=True)
        check("--force is the deliberate override", r2f.code, 0)
        check("...and it did overwrite the squatter",
              squatter.read_text(encoding="utf-8") != "MINE - do not clobber\n",
              True)
        # The real file is never a destination, with or without --force.
        (t2 / "CLAUDE.md").write_text("MY REAL RULES\n", encoding="utf-8")
        r2g = render(KIT, t2, full, force=True)
        check("the adopter's real CLAUDE.md is untouched by a --force run",
              (t2 / "CLAUDE.md").read_text(encoding="utf-8"), "MY REAL RULES\n")
        check("...and it was diffed against instead",
              bool(r2g.diffs.get("CLAUDE.md")), True)

        print(f"\n{BOLD}=== C. NEGATIVE CONTROL 3: output inside the kit "
              f"clone ==={RESET}")
        # GUARD 1 IS TWO LAYERS, AND EACH ONE IS ASSERTED BY ITS OWN MESSAGE.
        # Both layers say "inside the kit clone", so a substring assertion is
        # satisfied by either and a regression that deletes one is invisible -
        # measured: disabling the root-level check left this selftest at PASS.
        # The two messages are distinguished by their first clause.
        r3 = render(KIT, KIT, full)
        check("--target <the kit itself> ABORTS", r3.code, 2)
        check("...on the ROOT-LEVEL layer, by its own message",
              r3.abort.startswith("the resolved target root"), True)
        check("...naming the kit tree", "inside the kit clone" in r3.abort, True)
        check("...and wrote nothing", r3.written, {})
        check("...and left no stray file in the kit",
              (KIT / "CLAUDE.md.kit-new").exists(), False)
        r3b = render(KIT, KIT / "modules", full)
        check("a subdirectory of the kit aborts the same way", r3b.code, 2)
        # The sideways route: a target outside the kit whose LEDGERS_DIR points
        # back into it. This is the PER-OUTPUT-PATH layer, and it must be the
        # one that fires - the root here is a legitimate target.
        esc = os.path.relpath(str(KIT / "modules"), str(tmp / "escape"))
        t3 = _target(tmp, "escape",
                     cfg=MIN_CFG.replace("LEDGERS_DIR = docs",
                                         "LEDGERS_DIR = " + esc.replace("\\", "/")))
        r3c = render(KIT, t3, full)
        check("a LEDGERS_DIR pointing back into the kit aborts too", r3c.code, 2)
        check("...on the PER-OUTPUT-PATH layer, by its own message",
              r3c.abort.startswith("the output"), True)
        check("...naming the offending output path",
              "would land inside the kit clone" in r3c.abort, True)

        print(f"\n{BOLD}=== C2. NEGATIVE CONTROL 3b: output OUTSIDE the target "
              f"repo ==={RESET}")
        # `../shared-docs` is a plausible monorepo value. It used to write four
        # files outside the repository the tool was pointed at and report PASS.
        t3d = _target(tmp, "updir",
                      cfg=MIN_CFG.replace("LEDGERS_DIR = docs",
                                          "LEDGERS_DIR = ../../ESCAPED"))
        r3d = render(KIT, t3d, full)
        check("a relative LEDGERS_DIR that climbs out of the repo ABORTS",
              r3d.code, 2)
        check("...saying the output would land OUTSIDE the target repository",
              "would land OUTSIDE the target repository" in r3d.abort, True)
        check("...and naming the config key that caused it",
              "LEDGERS_DIR = '../../ESCAPED'" in r3d.abort, True)
        check("...and wrote nothing at all", r3d.written, {})
        check("...and created no directory outside the target",
              (tmp / "ESCAPED").exists(), False)
        # An ABSOLUTE LEDGERS_DIR, refused by SHAPE so that the two platforms
        # behave the same. A leading `/` used to be stripped into a relative
        # path on POSIX while a drive-qualified Windows path escaped intact.
        for label, val in (("POSIX-absolute", "/ABSESCAPE"),
                           ("drive-qualified", "C:/ABSESCAPE"),
                           ("UNC-ish", "\\\\server\\share")):
            tabs = _target(tmp, "abs-" + label,
                           cfg=MIN_CFG.replace("LEDGERS_DIR = docs",
                                               "LEDGERS_DIR = " + val))
            rabs = render(KIT, tabs, full)
            check(f"an absolute LEDGERS_DIR ({label}) is refused by shape",
                  (rabs.code, "is an absolute path" in rabs.abort), (2, True))
            check(f"...and {label} wrote nothing", rabs.written, {})

        print(f"\n{BOLD}=== D. NEGATIVE CONTROL 4: PROJECT_ROOT is resolved, "
              f"never read ==={RESET}")
        lie = "PROJECT_ROOT = /a/path/that/is/not/this/repo\n"
        t4 = _target(tmp, "projectroot", local=lie)
        r4 = render(KIT, t4, full)
        check("a kit.config PROJECT_ROOT does NOT reach the slot",
              "/a/path/that/is/not/this/repo"
              in r4.written[".claude/settings.json"], False)
        check("...the resolved root does",
              t4.resolve().as_posix() in r4.written[".claude/settings.json"],
              True)
        r4b = render(KIT, t4, dict(full, PROJECT_ROOT="/typed/by/hand"))
        check("--set PROJECT_ROOT is refused outright", r4b.code, 2)
        check("...saying why", "RESOLVES" in r4b.abort, True)
        # THE SPELLING OF THE TARGET MUST NOT REACH THE OUTPUT. Whatever
        # non-canonical form the tool is handed, the slot must get the
        # canonical one - otherwise the settings file carries a path that is
        # correct only from the shell that produced it, and any second reading
        # of the same directory disagrees with it. `sub/..` is the portable
        # case; the one that shipped a red was a Windows 8.3 alias under the CI
        # runner's TEMP (kit commit f608230). Same class: one directory, two
        # spellings.
        t4e = _target(tmp, "spelling")
        (t4e / "sub").mkdir()
        r4e = render(KIT, t4e / "sub" / ".." / "sub" / "..", full)
        check("a non-canonical --target spelling still yields a CANONICAL "
              "PROJECT_ROOT", r4e.values.get("PROJECT_ROOT"),
              t4e.resolve().as_posix())
        # `/..` rather than `..`: the template legitimately contains an
        # ellipsis ("Checking model tiers..."), and a check that cannot tell an
        # ellipsis from a parent-directory segment is a check that fires on
        # prose.
        check("...so no parent-directory segment reaches the rendered "
              "settings file", "/.." in r4e.written[".claude/settings.json"],
              False)
        check("...and it agrees with a run addressed the plain way",
              render(KIT, t4e, full, force=True).values.get("PROJECT_ROOT"),
              r4e.values.get("PROJECT_ROOT"))
        nogit = tmp / "no-git-here"
        (nogit / "sub").mkdir(parents=True)
        root, why = find_repo_root(nogit / "sub", lambda d: False)
        check("no .git ancestor is a refusal, not a guess", root, None)
        check("...and says so", "will not guess" in why, True)

        print(f"\n{BOLD}=== D2. NEGATIVE CONTROL 5: the $KIT_CONFIG leak ==="
              f"{RESET}")
        # QUICKSTART Step 2 sets this variable AT A KIT PATH and warns that
        # failing to unset it leaks into the rest of the session. The tool is
        # offered two steps later in that same session, so the leaked variable
        # is a state the document itself creates. Honouring it renders the
        # KIT's own example values into the adopter's repository.
        t4c = _target(tmp, "envleak")
        prev = os.environ.get("KIT_CONFIG")
        try:
            os.environ["KIT_CONFIG"] = str(KIT / "kit.config")
            r4c = render(KIT, t4c, full)
            check("a $KIT_CONFIG inside the kit clone is IGNORED",
                  r4c.values.get("PROJECT_NAME"), "Selftest Project")
            check("...and the kit's own PROJECT_NAME does not reach the files",
                  any("OAR" == v for v in [r4c.values.get("PROJECT_NAME")]),
                  False)
            check("...and it is refused LOUDLY, by name",
                  any("INSIDE THE KIT CLONE" in l for l in r4c.log), True)
            check("...with the remedy the document forgot to make stick",
                  any("Remove-Item Env:KIT_CONFIG" in l for l in r4c.log), True)
            check("...and the config actually read is the target's",
                  Path(r4c.config_source).parent.resolve(), t4c.resolve())
            # An explicit $KIT_CONFIG OUTSIDE the kit is still honoured: it is
            # an instruction, not an accident, and now it is printed.
            elsewhere = tmp / "elsewhere.config"
            elsewhere.write_text(MIN_CFG.replace("Selftest Project",
                                                 "Pointed Elsewhere"),
                                 encoding="utf-8")
            os.environ["KIT_CONFIG"] = str(elsewhere)
            r4d = render(KIT, _target(tmp, "envok"), full)
            check("a $KIT_CONFIG outside the kit is still honoured",
                  r4d.values.get("PROJECT_NAME"), "Pointed Elsewhere")
            check("...and the run names the config it read",
                  Path(r4d.config_source).resolve(), elsewhere.resolve())
        finally:
            if prev is None:
                os.environ.pop("KIT_CONFIG", None)
            else:
                os.environ["KIT_CONFIG"] = prev

        print(f"\n{BOLD}=== E. the happy path, and what it must contain ==="
              f"{RESET}")
        t5 = _target(tmp, "clean")
        r5 = render(KIT, t5, full)
        check("a fully configured render is PASS, exit 0", r5.code, 0)
        # This selftest runs with the KIT as the working directory, and the kit
        # ships a filled-in kit.config of its own as a worked example. A tool
        # that read `./kit.config` would render the KIT's values into the
        # adopter's files and report PASS.
        check("values come from the TARGET's kit.config, not the kit clone's",
              r5.values["PROJECT_NAME"], "Selftest Project")
        check("...seven files", len(r5.written), 7)
        check("...no unfilled slot anywhere", r5.unfilled, {})
        check("...every one of the seven landed as .kit-new",
              sorted(p.relative_to(t5).as_posix()
                     for p in t5.rglob("*.kit-new")),
              sorted(k + ".kit-new" for k in r5.written))
        settings = json.loads(r5.written[".claude/settings.json"])
        check("the settings file parses", isinstance(settings, dict), True)
        check("...with all THREE matcher blocks (the named silent hole)",
              len(settings["hooks"]["PreToolUse"]), 3)
        check("...and the __COMMENT__ block is gone",
              "__COMMENT__" in settings, False)
        check("...reported as a stripped header, not silently dropped",
              ".claude/settings.json" in r5.stripped, True)
        check("the governance header block is stripped",
              "DELETE THIS COMMENT BLOCK" in r5.written["CLAUDE.md"], False)
        check("...and reported", "CLAUDE.md" in r5.stripped, True)
        check("the ledger SKELETON header is stripped",
              "SKELETON" in r5.written["docs/LESSONS.md"], False)
        check("the profile's template comment is stripped",
              "Delete this comment on adoption"
              in r5.written["docs/collaboration-profile.md"], False)
        check("...but its YAML front matter SURVIVES (it is content)",
              r5.written["docs/collaboration-profile.md"].startswith(
                  "---\ntitle:"), True)

        print(f"\n{BOLD}=== F. the structural settings merge (guard 3) ==="
              f"{RESET}")
        # The hand-merge failure the template names: one matcher block wired,
        # the other two forgotten, plus a key of the adopter's own.
        t6 = _target(tmp, "merge")
        # Build the half-wired file from a render into THIS target, so its
        # {{PROJECT_ROOT}} is this target's. Taking it from another target
        # would compare two different absolute paths and prove nothing about
        # matcher matching.
        pre = render(KIT, t6, full)
        (t6 / ".claude").mkdir(exist_ok=True)
        one_block = json.loads(pre.written[".claude/settings.json"])
        one_block["hooks"]["PreToolUse"] = [
            one_block["hooks"]["PreToolUse"][0]]
        one_block["model"] = "an adopter key the template knows nothing about"
        (t6 / ".claude" / "settings.json").write_text(
            json.dumps(one_block, indent=2), encoding="utf-8")
        r6 = render(KIT, t6, full, force=True)
        merged = json.loads(r6.written[".claude/settings.json"])
        check("the two missing matcher blocks are APPENDED",
              len(merged["hooks"]["PreToolUse"]), 3)
        check("...and the merge SAYS which ones were not wired",
              sum(1 for x in r6.merge_notes if "was NOT wired" in x), 2)
        check("the already-wired block is not duplicated",
              [b["matcher"] for b in merged["hooks"]["PreToolUse"]],
              ["Workflow|Agent", "Bash|PowerShell", "Edit|Write|NotebookEdit"])
        check("...and carries exactly one hook entry",
              len(merged["hooks"]["PreToolUse"][0]["hooks"]), 1)
        check("an adopter key the template does not own SURVIVES",
              merged.get("model"),
              "an adopter key the template knows nothing about")
        check("permissions.ask is a union, not a duplication",
              len(merged["permissions"]["ask"]), 2)
        # The other machine's settings file - KNOWN-ISSUES' "Whose settings
        # file? - the team story". The matcher IS wired, to a command that
        # cannot start here. A silent merge would leave two hooks under one
        # matcher and no note saying which one decided.
        stale = json.loads(pre.written[".claude/settings.json"])
        stale["hooks"]["PreToolUse"][1]["hooks"][0]["command"] = (
            'python "/some/other/machine/tools/hook_model_gate.py"')
        (t6 / ".claude" / "settings.json").write_text(
            json.dumps(stale, indent=2), encoding="utf-8")
        r6b = render(KIT, t6, full, force=True)
        check("a stale command under an already-wired matcher is flagged for "
              "REVIEW", sum(1 for x in r6b.merge_notes if "REVIEW" in x), 1)
        check("...and both commands are left in place for the human to choose",
              len(json.loads(r6b.written[".claude/settings.json"])
                  ["hooks"]["PreToolUse"][1]["hooks"]), 2)
        # SB-B, made unreachable: a value with a double quote in it used to
        # produce settings that did not parse, which is a silently disarmed
        # harness. json.dumps quotes it.
        t7 = _target(tmp, "quoted")
        r7 = render(KIT, t7, dict(full,
                                  STATUSLINE_CMD='python "/a b/statusline.py"'))
        parsed = json.loads(r7.written[".claude/settings.json"])
        check("a double quote in STATUSLINE_CMD still parses (SB-B closed "
              "on this path)",
              parsed["statusLine"]["command"], 'python "/a b/statusline.py"')

        print(f"\n{BOLD}=== F2. an EQUIVALENT matcher, spelled differently ==="
              f"{RESET}")
        # `Write|Edit|NotebookEdit` selects exactly the calls
        # `Edit|Write|NotebookEdit` selects. Compared as text it looks like a
        # matcher nobody wired: the block is duplicated (the gate then fires
        # twice on every matching call) and the note says "was NOT wired",
        # which tells the one human who could catch it to look away.
        t6c = _target(tmp, "matcher-order")
        pre_c = render(KIT, t6c, full)
        (t6c / ".claude").mkdir(exist_ok=True)
        reordered = json.loads(pre_c.written[".claude/settings.json"])
        reordered["hooks"]["PreToolUse"][2]["matcher"] = "Write|Edit|NotebookEdit"
        (t6c / ".claude" / "settings.json").write_text(
            json.dumps(reordered, indent=2), encoding="utf-8")
        r6c = render(KIT, t6c, full, force=True)
        m6c = json.loads(r6c.written[".claude/settings.json"])
        check("an equivalent-but-reordered matcher is NOT duplicated",
              len(m6c["hooks"]["PreToolUse"]), 3)
        check("...and the adopter's spelling is left alone",
              m6c["hooks"]["PreToolUse"][2]["matcher"],
              "Write|Edit|NotebookEdit")
        check("...and the block still carries exactly one hook",
              len(m6c["hooks"]["PreToolUse"][2]["hooks"]), 1)
        check("...and NOTHING claims it was NOT wired",
              any("was NOT wired" in x for x in r6c.merge_notes), False)
        check("...the note says the truth instead: equivalent, merged",
              any("already covers the same tools" in x
                  for x in r6c.merge_notes), True)
        check("matcher_key is order-blind",
              matcher_key("Write|Edit|X"), matcher_key("X|Edit|Write"))
        check("...and whitespace-blind", matcher_key(" A | B "),
              matcher_key("A|B"))
        check("...but not name-blind",
              matcher_key("A|B") == matcher_key("A|C"), False)

        print(f"\n{BOLD}=== F3. a value the merge cannot merge ==={RESET}")
        # The neighbouring code is careful never to pick a winner. This branch
        # used to replace a malformed value with [] and say nothing.
        t6d = _target(tmp, "malformed")
        pre_d = render(KIT, t6d, full)
        (t6d / ".claude").mkdir(exist_ok=True)
        bad = json.loads(pre_d.written[".claude/settings.json"])
        bad["hooks"]["PreToolUse"] = {"adopters": "own structure"}
        bad["permissions"]["ask"] = "a string not a list"
        (t6d / ".claude" / "settings.json").write_text(
            json.dumps(bad, indent=2), encoding="utf-8")
        r6d = render(KIT, t6d, full, force=True)
        check("a non-list hooks event is reported, not silently dropped",
              sum(1 for x in r6d.merge_notes
                  if "hooks.PreToolUse: REVIEW" in x), 1)
        check("...naming what was discarded",
              any("own structure" in x for x in r6d.merge_notes), True)
        check("a non-list permissions.ask is reported too",
              sum(1 for x in r6d.merge_notes
                  if "permissions.ask: REVIEW" in x), 1)
        check("...naming what was discarded",
              any("a string not a list" in x for x in r6d.merge_notes), True)
        check("the pluralisation is English",
              any("added 2 entries" in x for x in r6d.merge_notes), True)
        check("...and singular when it is one",
              any("entryies" in x for x in r6d.merge_notes), False)

        print(f"\n{BOLD}=== G. the conditional blocks Step 4 describes ==="
              f"{RESET}")
        t8 = _target(tmp, "tripwire-off")
        r8 = render(KIT, t8, dict(STATUSLINE_CMD="NONE"))
        s8 = json.loads(r8.written[".claude/settings.json"])
        check("PROTECTED_PATH unset deletes permissions.ask",
              "permissions" in s8, False)
        check("STATUSLINE_CMD unset deletes statusLine", "statusLine" in s8,
              False)
        check("...both reported, not silently done", len(r8.omitted), 2)
        check("...and the hooks are still all there",
              len(s8["hooks"]["PreToolUse"]), 3)
        check("...so no {{SLOT}} survives into the settings file",
              collect_slots(s8), [])
        # A fallback is a decision made on the adopter's behalf, and four files
        # land in a directory nobody chose.
        t8b = _target(tmp, "no-ledgers-dir",
                      cfg=MIN_CFG.replace("LEDGERS_DIR = docs",
                                          "LEDGERS_DIR = NONE"))
        r8b = render(KIT, t8b, full)
        check("a LEDGERS_DIR that reads as UNSET is NOT silently defaulted",
              any("default to 'docs'" in x for x in r8b.notes), True)
        check("...and the files still land somewhere usable",
              "docs/LESSONS.md" in r8b.written, True)
        # Step 8's other branch: the profile's source of truth is outside the
        # repo and this tool renders only the mirror.
        t8c = _target(tmp, "abs-knowledge")
        r8c = render(KIT, t8c, dict(full, KNOWLEDGE_DIR="/home/me/vault"))
        check("an absolute KNOWLEDGE_DIR is called out as Step 8's other "
              "branch",
              any("renders the MIRROR only" in x for x in r8c.notes), True)
        check("...and a repo-path KNOWLEDGE_DIR says nothing about it",
              any("renders the MIRROR only" in x for x in r5.notes), False)

        print(f"\n{BOLD}=== H. the pure layer, on literals ==={RESET}")
        # ONE PASS. A slot inside a VALUE must not be expanded, or the same
        # config renders two different files depending on key order.
        check("a slot inside a substituted VALUE is not re-expanded",
              substitute("[{{PROJECT_NAME}}]",
                         {"PROJECT_NAME": "Proj {{OWNER_ROLE}} X",
                          "OWNER_ROLE": "the owner"}),
              "[Proj {{OWNER_ROLE}} X]")
        check("...in either key order",
              substitute("[{{PROJECT_NAME}}]",
                         {"OWNER_ROLE": "the owner",
                          "PROJECT_NAME": "Proj {{OWNER_ROLE}} X"}),
              "[Proj {{OWNER_ROLE}} X]")
        check("an unknown slot is left exactly as it was",
              substitute("a {{NOPE}} b", {"X": "y"}), "a {{NOPE}} b")
        check("a comment with no marker word is not a header",
              strip_header("<!-- just a note -->\nbody\n")[1], None)
        check("...and the text is returned unchanged",
              strip_header("<!-- just a note -->\nbody\n")[0],
              "<!-- just a note -->\nbody\n")
        check("text before the header survives the strip",
              strip_header("keep\n\n<!--\nSKELETON x\n-->\n\nbody\n")[0],
              "keep\n\nbody\n")
        check("NONE is not a value", is_placeholder("NONE"), True)
        check("your-lane-tier is not a value", is_placeholder("your-lane-tier"),
              True)
        check("RATIO_CEILING's shipped value is exempt, by name",
              usable("RATIO_CEILING", "derive-from-your-own-data"), True)
        check("...and the same string is not exempt anywhere else",
              usable("LANE_TIER", "derive-from-your-own-data"), False)
        check("path_inside is case-folded",
              path_inside(str(KIT).upper(), str(KIT)), True)
        check("a sibling directory is not inside",
              path_inside(str(KIT) + "-other", str(KIT)), False)
        check("the manifest is seven files", len(RENDERS), 7)
        check("...all seven templates exist in the kit",
              [t for t, _, _, _ in RENDERS if not (KIT / t).is_file()], [])
        check("...and every one of them is a slot-carrying module file",
              [t for t, _, _, _ in RENDERS
               if t not in slot_carrying_module_files(KIT)], [])

        print(f"\n{BOLD}=== I. the printing and CLI layer ==={RESET}")
        # Everything above asserts on Result objects, which is the right shape
        # for the decision layer and leaves the layer the adopter actually
        # READS unchecked. A shipped pluralisation bug lived here.
        import contextlib
        import io

        def captured(fn, *a, **kw):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = fn(*a, **kw)
            return rc, re.sub(r"\033\[[0-9;]*m", "", buf.getvalue())

        rc_p, out_p = captured(report, render(KIT, _target(tmp, "print-ok"),
                                              full), 40)
        check("report() on a clean run exits 0", rc_p, 0)
        check("...and prints the verdict line",
              "KIT RENDER: PASS — 7 files written, every slot filled" in out_p,
              True)
        check("...and names the config file it read (guard 5's other half)",
              "config    : " in out_p and "print-ok" in out_p, True)
        check("...and labels each file with its QUICKSTART step",
              "docs/collaboration-profile.md.kit-new  (Step 8)" in out_p, True)
        rc_q, out_q = captured(
            report, render(KIT, _target(tmp, "print-bad", cfg=thin), full), 40)
        check("report() on an unfilled slot exits 1", rc_q, 1)
        check("...and the UNFILLED line names the key and where to set it",
              "UNFILLED {{OWNER_ROLE}} — set OWNER_ROLE in kit.config" in out_q,
              True)
        rc_a, out_a = captured(report, render(KIT, KIT, full), 40)
        check("report() on an abort exits 2 with the verdict word",
              (rc_a, "KIT RENDER: ABORTED" in out_a), (2, True))
        # The diff truncation line, on a diff longer than the cap.
        t_d = _target(tmp, "print-diff")
        pre_d2 = render(KIT, t_d, full)
        (t_d / "CLAUDE.md").write_text("one line\n", encoding="utf-8")
        rc_d, out_d = captured(report, render(KIT, t_d, full, force=True), 5)
        check("a long diff is truncated and says how much was cut",
              "more diff lines — read the file" in out_d, True)
        # --set parsing and --target validation, the two CLI branches phase 13
        # cannot reach.
        argv = sys.argv
        try:
            sys.argv = ["kit_render.py", "--target", str(t_d), "--set", "NOPE"]
            rc_m, out_m = captured(main)
            check("main() refuses a --set that is not KEY=VALUE", rc_m, 2)
            sys.argv = ["kit_render.py", "--target", str(tmp / "nope-not-here")]
            rc_m2, _ = captured(main)
            check("main() refuses a --target that is not a directory", rc_m2, 2)
            sys.argv = ["kit_render.py"]
            rc_m3, _ = captured(main)
            check("main() refuses to run with no --target at all", rc_m3, 2)
        finally:
            sys.argv = argv
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print((GREEN if ok_all else RED)
          + f"KIT-RENDER SELFTEST: {'PASS' if ok_all else 'FAIL'} — {n} checks"
          + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render the seven slot-carrying files QUICKSTART fills, "
                    "from a kit checkout into your own repo. The by-hand path "
                    "in QUICKSTART.md remains the documented primary route.")
    ap.add_argument("--target", default="",
                    help="your repository (any directory inside it). The "
                         "repo root is resolved by walking up to .git.")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="a slot value, layered over kit.config. Repeatable. "
                         "PROJECT_ROOT is refused - it is resolved.")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing .kit-new file. Never touches "
                         "the real file either way.")
    ap.add_argument("--diff-lines", type=int, default=40,
                    help="how much of each diff to print (default 40)")
    ap.add_argument("--list", action="store_true",
                    help="print what this tool renders and what it does not")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.list:
        return do_list(KIT)
    if not a.target:
        print(f"{RED}KIT RENDER: ABORTED — --target is required (the "
              f"repository to render into). --list shows what would be "
              f"rendered.{RESET}", file=sys.stderr)
        return 2

    overrides = {}
    for item in a.set:
        if "=" not in item:
            print(f"{RED}KIT RENDER: ABORTED — --set {item!r} is not "
                  f"KEY=VALUE{RESET}", file=sys.stderr)
            return 2
        k, v = item.split("=", 1)
        overrides[k.strip()] = v.strip()

    target = Path(a.target)
    if not target.is_dir():
        print(f"{RED}KIT RENDER: ABORTED — --target {a.target!r} is not a "
              f"directory{RESET}", file=sys.stderr)
        return 2

    return report(render(KIT, target, overrides, force=a.force),
                  diff_lines=a.diff_lines)


if __name__ == "__main__":
    raise SystemExit(main())
