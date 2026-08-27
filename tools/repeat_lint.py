#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
tools/repeat_lint.py - the repeat lint. Is this universal claim stated in more
than one document?

    python tools/repeat_lint.py                 # lint the kit's own documents
    python tools/repeat_lint.py --root <path>   # lint another tree
    python tools/repeat_lint.py --selftest      # incl. the negative controls
    python tools/repeat_lint.py --list          # print every claim seen and
                                                # every one skipped, with why

    exit 0  no universal claim is restated in a second document, or every
            restatement that is has a waiver naming it. The summary line says
            CLEAN or PARTIAL and prints the denominator - see THE STATE WORD
    exit 1  at least one universal claim is stated in two documents with no
            waiver
    exit 2  abort (no root, nothing to read)

==========================================================================
WHY THIS EXISTS
==========================================================================
Round 30 moved long-form text out of `README.md` into `docs/START-HERE.md`.
The round corrected two false universals in the copy that STAYED and moved the
copy that WENT unchanged. `docs/START-HERE.md`'s own first line recorded the
move as "relocated ... intact", and intact was the problem: three uncorrected
instances of a class the program had already paid for five times rode the
relocation into a document no reader of the corrected page would re-check. A
fresh-eyes read found all three from a cold start in ten minutes, two years of
apparatus notwithstanding.

That is the failure this tool exists for, and it is NOT the failure
`tools/count_lint.py`'s quantifier layer covers. That layer asks whether a
universal claim is TRUE of a target it can enumerate. This one asks a different
question, which is answerable when the first is not:

    is this universal claim written down in more than one place, so that
    correcting one copy leaves the others standing?

Neither question implies the other. A claim can be true and duplicated; a claim
can be false and unique. The two tools are siblings, each with its own
decidable question, its own exit code and its own summary line, which is this
kit's standing convention for checks - see the WHY A SEPARATE TOOL section of
`tools/count_lint.py`, which makes the same argument against fusing it with the
citation lint.

WHAT A FINDING MEANS, STATED EXACTLY, because a reader will otherwise assume
more: a finding is NOT "this sentence is wrong". It is "this sentence exists
twice, and nothing in this kit relates the two copies, so a correction applied
to one of them will not reach the other." The remedy is one of three, and all
three are legitimate:

  1. Correct both copies, and keep them under a waiver that says they are two.
  2. Delete one copy and point at the other.
  3. Rewrite one so the two say different things scoped to their own pages.

==========================================================================
WHAT IT CAN SEE, AND WHAT IT CANNOT
==========================================================================
A UNIVERSAL SENTENCE is a sentence that satisfies both:

  1. A QUANTIFIER WORD: the determiner forms `every`, `each`, `all`, `no`,
     `none of the`, and - unlike the quantifier layer, and this is the point -
     the ABSOLUTE forms `never`, `always`, `nothing`, `nobody`, `everything`,
     `everywhere` as well. The quantifier layer must skip the absolutes
     because they take no noun and therefore name no target it can enumerate.
     THIS tool needs no target: it compares two strings. The absolutes are the
     half of the class the other layer structurally cannot reach, and three of
     the round-32 instances were absolutes.
  2. A PRESENCE OR STATE VERB in the sentence. Without one the sentence is
     not making an assertion about anything, and the tool's own first run over
     this kit showed that dropping this condition doubles the denominator with
     sentence fragments.

Sentences shorter than `MIN_WORDS` normalised words are dropped: two short
sentences collide by accident, and a collision that is an accident is a
finding that wastes a reader.

TWO CLAIMS ARE THE SAME CLAIM when their normalised word sequences share a
CONTIGUOUS RUN of at least `MIN_RUN` words. Contiguous, not a bag of words:
"every row carries a source" and "no row carries a source" share four
contiguous words and mean opposite things, and a set-overlap measure would
score them identically. A shared RUN is the shape a copied sentence has, and a
copied sentence is what this tool is looking for.

NORMALISATION, stated because it is a judgment call: lowercase, markdown
emphasis and backticks and brackets removed, punctuation removed, whitespace
collapsed. What survives is the words in their order. Two sentences that
differ only in bolding are the same sentence to a reader and are the same
sentence here.

MIN_RUN = 8, AND THE DERIVATION IS PRINTED ON EVERY RUN. Measured over the
kit's own tree at `d52f8a5`, the commit this tool was written against, with
the exempt classes below already removed and **before any waiver was
written** - the waivers came out of reading these 17 pairs, so counting the
threshold against a waived tree would be deriving a number from its own
answer:

    run length >= 12   1 pair
    run length >= 10   4 pairs
    run length >=  8  17 pairs

The floor is set by the class, not by the count. The instance this kit most
needed to see - "every check has been seen to fail on purpose", written into
both `COMPARISON.md` and `DECISION-BRIEF.md`, and convicted by three
consecutive adversarial reads - shares an 8-word run. **8 is the largest
threshold at which this tool can still see the defect it was built for**, so 8
is the threshold. Going higher buys a quieter tool that misses the motivating
case; going lower buys pairs that share a stock phrase rather than a claim.
The cost is stated rather than hidden: at 8 the tool reports deliberate
restatements too, and those are dispositioned as waivers, out loud, below.

OUT OF SCOPE - stated plainly, because a check whose limits are not published
gets read as covering more than it does:

  - **Two copies inside ONE document.** A document is edited as a unit and a
    reader correcting a sentence in it can see the other one. The relocation
    exposure is between documents, and that is what is checked.
  - **A restatement in different words.** "Every walk has a published prompt"
    and "we publish the prompt for all the walks" share no eight-word run and
    are invisible here. This tool finds COPIES, which is the mechanism round
    30 actually used; it does not find PARAPHRASES, and a paraphrase carries
    the same exposure. Named as a residual rather than covered.
  - **Whether either copy is true.** That is `count_lint.py`'s quantifier
    layer's question where the target is enumerable, and nobody's where it is
    not.
  - **Exempt document classes**, printed on every run with their counts:
      * `KNOWN-ISSUES.md`, the findings register. It records what a claim USED
        TO SAY beside the correction, so a corrected sentence and its historical
        quotation necessarily collide. Exempt for the same reason and in the
        same shape as the citation lint's and the count lint's exemptions.
        RESIDUAL, STATED: a universal duplicated INTO the register is exempt too.
      * The pages carrying a VERBATIM PROMPT - `docs/walks/walk-*.md` and
        `docs/walks/read-30-*.md`. A published prompt is a record of what was
        said to a persona on a date. It cannot be corrected without falsifying
        the record, so a correction failing to travel there is not a defect.
        These pages share persona boilerplate by construction. Measured on the
        kit at `d52f8a5` with only the register exempt, run length >= 12 gave 31
        pairs and **30 of the 31 had a prompt page on both sides**. With them
        exempt too, 554 of the tree's 1,314 universal sentences are skipped and
        1 pair remains at that length.

==========================================================================
THE STATE WORD
==========================================================================
Same rule, same reason, same shape as `tools/count_lint.py`'s:

    REPEAT LINT: PARTIAL - 779 of 1371 universal claim(s) compared (56.8%),
    0 restated - exit 0

  CLEAN    every universal sentence in the tree was comparable.
  PARTIAL  at least one sat in an exempt document class. The percentage is
           printed and `--list` prints what was skipped.

A run that compares 57% of its subject does not get to print the same word as
a run that compared all of it. The exit code does not move on PARTIAL, for the
reason the count lint states about its own: coverage is a disclosure about the
SUBJECT, and a permanently red lint whose red means "this kit has a findings
register" is a red people learn to skip.
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from pathlib import Path

GREEN, RED, YELLOW, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# THE THRESHOLD AND ITS DERIVATION. See the docstring; the number is printed on
# every run beside the reason it is 8, because a threshold whose derivation
# lives only in a comment is a threshold the next edit moves.
MIN_RUN = 8
MIN_WORDS = 6
RUN_DERIVATION = (
    f"MIN_RUN={MIN_RUN} words: the largest run length at which this tool still "
    f"sees the claim it was built for (\"every check has been seen to fail on "
    f"purpose\", written into two documents, shares an 8-word run). Measured on "
    f"the kit at d52f8a5: >=12 gave 1 pair, >=10 gave 4, >=8 gave 17.")

# Both the determiner forms AND the absolutes. The absolutes are the half of the
# class the count lint's quantifier layer structurally cannot reach, because
# they take no noun; this tool needs no noun.
QUANT_WORDS = re.compile(
    r'(?<![\w-])(every|each|all|none of the|no|never|always|nothing|nobody|'
    r'everything|everywhere)(?![\w-])', re.I)

# A sentence with no verb of assertion is not a claim. Deliberately wider than
# the count lint's PRESENCE_VERB by the copula: "every walk WAS performed by a
# persona" is the exact shape of three round-32 instances and carries no
# presence verb at all.
ASSERT_VERB = re.compile(
    r'\b(names?|carr(?:y|ies)|contains?|has|have|includes?|lists?|cites?|'
    r'ends?|starts?|begins?|prints?|states?|mentions?|holds?|links?|'
    r'declares?|quotes?|shows?|spells?|uses?|reads?|publish(?:es|ed)?|'
    r'is|are|was|were|be|been)\b', re.I)

# A sentence, for this tool: text between terminators, and a markdown table
# cell boundary is a terminator too - the same rule the count lint's
# cell-boundary control established.
SENTENCE_SPLIT = re.compile(r'(?<=[.:!?])\s+|\|')

# See the docstring. Both classes are printed on every run with their counts.
EXEMPT_GLOBS = (
    "KNOWN-ISSUES.md",
    "docs/walks/walk-*.md",
    "docs/walks/read-30-*.md",
)
EXEMPT_REASONS = {
    "KNOWN-ISSUES.md":
        "a findings register records what a claim used to say beside the "
        "correction, so the two necessarily collide",
    "docs/walks/walk-*.md":
        "a published prompt is a verbatim record of what was said on a date "
        "and cannot be corrected without falsifying it",
    "docs/walks/read-30-*.md":
        "a published prompt is a verbatim record of what was said on a date "
        "and cannot be corrected without falsifying it",
}

# WAIVERS. Same convention as `tools/citation_lint.py`,
# `tools/count_lint.py` and `tools/expectation_lint.py`: a pair this tool
# correctly finds and a human has ruled deliberate is named out loud with its
# reason and PRINTED ON EVERY RUN, never suppressed silently. Keyed by the two
# document names, sorted, so the waiver survives an edit to either sentence
# that keeps them the same claim - and dies if one of them is rewritten to a
# different claim, which is what should happen.
WAIVERS: dict = {
    # RULED IN ROUND 32, on this tool's first live run. Each pair below was
    # found by the tool, read, and ruled a DELIBERATE restatement: the same
    # sentence is meant to appear in both places, and the ruling is written
    # here so that the next person to correct one of them sees the other named.
    # A waiver is not a dismissal - the pair is still found and still printed.
    # RETIRED 2026-08-26 (prose-floor round), AMENDED at its review: three
    # waivers went dead when the docs they covered were shortened and the
    # pairs stopped matching. The retirement's first rationale ("the facts
    # survive on both sides") was true but incomplete - the review proved
    # the DUPLICATIONS survive too, invisible to this matcher through
    # re-wrapping, a cross-repo move, and a period inside a bold run; the
    # same texts still match against a clean HEAD export. The waiver keys
    # are matcher-bound, so restoring them would print UNUSED against text
    # the matcher cannot see - misleading in the other direction. The gap
    # is recorded as a KNOWN-ISSUES entry (prose-floor round) and rides the
    # matcher's next revision. Retired pairs: README=docs/SECURITY-SCOPE,
    # EXISTING-PROJECT=QUICKSTART, LEVEL-1=QUICKSTART.
    ("docs/PREREQUISITES.md", "docs/WHY-FILES.md"):
        "The harness-independence claim for modules 01, 03, 04, 07 and 08, "
        "restated where a reader of either page needs it. Deliberate.",
    ("BLUEPRINT.md", "COMPARISON.md"):
        "The loop-termination rules are stated as doctrine in BLUEPRINT §2 "
        "and again as the claim under audit in COMPARISON's row. Deliberate: "
        "the comparison page must quote the claim it is auditing. "
        "Correction-travel residual, stated: if the doctrine side is "
        "corrected alone, this pair stops matching and the stale quote goes "
        "invisible to this tool - the UNUSED WAIVER line printed on that day "
        "is the tripwire, and COMPARISON's own re-audit procedure is the "
        "fallback.",
    ("ONBOARD.md", "modules/08-collaboration/PROFILE-TEMPLATE.md"):
        "The unconfirmed-defaults sentence is the same sentence in the "
        "agent-facing front door and in the profile the agent writes. "
        "Deliberate.",
    ("LEVEL-1.md", "ONBOARD.md"):
        "As above, for the same sentence on the Level-1 path.",
    ("LEVEL-1.md", "modules/08-collaboration/PROFILE-TEMPLATE.md"):
        "As above, for the same sentence on the Level-1 path.",
    ("ONBOARD.md", "modules/04-ledgers/LESSONS.md"):
        "\"A gate that has never been red is unproven\" is a LESSONS entry "
        "quoted into the onboarding path. Deliberate: it is the sentence the "
        "whole forced-red doctrine rests on.",
    ("ONBOARD.md", "modules/08-collaboration/DEFAULTS.md"):
        "DEFAULTS quotes the punch-list sentence from the onboarding path as "
        "the evidence behind a default. Deliberate, and marked as a quotation "
        "where it lands.",
    ("ONBOARD.md", "docs/walks/WALKING-YOUR-OWN-DOCUMENTS.md"):
        "The finding-quality rule (a paraphrased error message is a finding "
        "nobody can act on) is stated for the agent adopting the kit and "
        "again for the adopter running the method on their own documents. "
        "Deliberate.",
    ("modules/01-governance/PUNCH-LIST-TEMPLATE.md",
     "modules/08-collaboration/DEFAULTS.md"):
        "The silent-skip rule, stated on the template that enforces it and in "
        "the default that explains why. Deliberate.",
    ("modules/08-collaboration/DEFAULT-CONTRACT.md",
     "modules/08-collaboration/README.md"):
        "One module's contract and its own README stating the same "
        "regression rule. Deliberate.",
}


# ==========================================================================
# THE PURE LAYER - everything below decides strings, so every rule is testable
# without a tree.
# ==========================================================================
def normalise(sentence: str):
    """The words of a sentence, in order, with markdown and punctuation gone.

    One function so the finding message, the comparison and the controls all
    read the same rule."""
    s = re.sub(r'[*_>#`\[\]()]', ' ', sentence)
    s = re.sub(r'[^a-z0-9\s-]', ' ', s.lower())
    return [w for w in s.split() if w]


def longest_run(a, b) -> int:
    """The length of the longest CONTIGUOUS run of words `a` and `b` share.

    Contiguous on purpose: "every row carries a source" and "no row carries a
    source" share four words and mean opposite things, and a set measure cannot
    tell them apart."""
    if not a or not b:
        return 0
    best, prev = 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def shared_run(a, b):
    """The longest shared contiguous run itself, as a list of words. Used only
    to print the finding - a finding a reader cannot see the evidence for is a
    finding they have to take on trust."""
    best, best_end, prev = 0, 0, [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            if x == y:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, best_end = cur[j], j
        prev = cur
    return b[best_end - best:best_end] if best else []


def universal_sentences(text: str):
    """[(line number, sentence text, normalised words)] for every universal
    claim this tool can compare, plus the phrases it dropped as too short.

    Pure - it decides a string."""
    out, dropped = [], []
    for i, line in enumerate(text.splitlines(), 1):
        for piece in SENTENCE_SPLIT.split(line):
            s = piece.strip()
            if not s:
                continue
            if not QUANT_WORDS.search(s):
                continue
            if not ASSERT_VERB.search(s):
                continue
            words = normalise(s)
            if len(words) < MIN_WORDS:
                dropped.append((s, f"under {MIN_WORDS} normalised words - two "
                                   f"short sentences collide by accident"))
                continue
            out.append((i, s, words))
    return out, dropped


def is_exempt(rel: str):
    """The exemption glob covering this document, or None."""
    for g in EXEMPT_GLOBS:
        if fnmatch.fnmatch(rel, g):
            return g
    return None


def unused_waivers(findings: list, waivers: dict) -> list:
    """Waiver keys with no matching pair in this tree, sorted. Pure.

    The correction-travel tripwire: when one side of a waived pair is
    rewritten, the pair stops matching, the waiver goes dead, and the OTHER
    side may be a stale claim nothing now reports. Dead waivers are printed
    loudly rather than red - a pair can also legitimately fall under the
    threshold - and never silently."""
    live = {tuple(sorted((f["a"][0], f["b"][0]))) for f in findings}
    return [k for k in sorted(waivers) if tuple(sorted(k)) not in live]


def waiver_for(doc_a: str, doc_b: str):
    """The waiver covering this pair of documents, or None. An empty reason is
    not a waiver - it is the silent case wearing a label, the same rule the
    count lint applies to its own."""
    reason = WAIVERS.get(tuple(sorted((doc_a, doc_b))))
    return reason if reason and reason.strip() else None


def restatements(docs: dict):
    """Every universal claim stated in two documents.

    `docs` maps a relative path to its text. Returns
    (findings, comparable, skipped, dropped) where a finding is a dict naming
    both sites and the run they share. Pure: it takes strings and returns
    data, so the controls below test the rule and not the tree."""
    comparable, skipped, dropped = [], [], []
    for rel in sorted(docs):
        got, drop = universal_sentences(docs[rel])
        dropped.extend((rel, s, why) for s, why in drop)
        g = is_exempt(rel)
        if g:
            skipped.extend((rel, s, g) for _, s, _ in got)
            continue
        comparable.extend((rel, ln, s, w) for ln, s, w in got)

    findings = []
    for i in range(len(comparable)):
        rel_a, ln_a, s_a, w_a = comparable[i]
        for j in range(i + 1, len(comparable)):
            rel_b, ln_b, s_b, w_b = comparable[j]
            if rel_a == rel_b:
                continue           # one document is edited as a unit
            n = longest_run(w_a, w_b)
            if n < MIN_RUN:
                continue
            findings.append(dict(
                a=(rel_a, ln_a, s_a), b=(rel_b, ln_b, s_b), run=n,
                run_text=" ".join(shared_run(w_a, w_b)),
                waiver=waiver_for(rel_a, rel_b)))
    findings.sort(key=lambda f: (-f["run"], f["a"][0], f["a"][1]))
    return findings, comparable, skipped, dropped


def coverage_state(compared: int, skipped: int):
    """(state word, percentage compared). CLEAN only when nothing was skipped;
    PARTIAL otherwise. One function so the summary line and its control read
    the same rule - the count lint's own arrangement, and for the same
    reason."""
    seen = compared + skipped
    pct = (100.0 * compared / seen) if seen else 100.0
    return ("CLEAN" if skipped == 0 else "PARTIAL"), pct


# ==========================================================================
# THE RUNNING LAYER  (impure below this line)
# ==========================================================================
def kit_documents(root: Path):
    seen = {}
    for pat in ("*.md", "modules/*/*.md", "docs/**/*.md", "modules/**/*.md"):
        for p in root.glob(pat):
            if p.is_file():
                seen[p.resolve()] = p
    return sorted(seen.values(), key=lambda p: p.as_posix())


def run(root: Path, show_all: bool) -> int:
    paths = kit_documents(root)
    if not paths:
        print(f"{RED}REPEAT LINT: ABORT — no markdown documents under "
              f"{root}{RESET}")
        return 2

    docs = {}
    for p in paths:
        try:
            docs[p.relative_to(root).as_posix()] = p.read_text(
                encoding="utf-8")
        except OSError as exc:
            print(f"{RED}REPEAT LINT: ABORT — cannot read {p}: {exc}{RESET}")
            return 2

    findings, comparable, skipped, dropped = restatements(docs)
    problems = [f for f in findings if not f["waiver"]]
    waived = [f for f in findings if f["waiver"]]

    print()
    print(f"root      : {root}")
    print(f"documents : {len(docs)} scanned")
    print(f"threshold : {RUN_DERIVATION}")
    print(f"claims    : {len(comparable)} universal claim(s) compared, "
          f"{len(skipped)} in an exempt document class")
    for g in EXEMPT_GLOBS:
        n = sum(1 for _, _, gg in skipped if gg == g)
        print(f"  exempt  : {n:>4} in `{g}` — {EXEMPT_REASONS[g]}")
    print(f"dropped   : {len(dropped)} sentence(s) under the word floor "
          f"(printed with --list)")
    print(f"waivers   : {len(waived)} (each printed below, every run)")
    for f in waived:
        print(f"{YELLOW}  WAIVED {f['a'][0]}:{f['a'][1]} = {f['b'][0]}:"
              f"{f['b'][1]} ({f['run']} words: \"{f['run_text'][:90]}\")\n"
              f"    {f['waiver']}{RESET}")
    # A waiver whose pair no longer matches is the correction-travel case: one
    # side was probably rewritten and the OTHER side may now be the stale
    # claim. Loud, not red - a pair can also legitimately fall under the
    # threshold - but never silent (review finding, 2026-08-25).
    for a, b in unused_waivers(findings, WAIVERS):
        print(f"{YELLOW}  UNUSED WAIVER {a} = {b} — no matching pair in this "
              f"tree. One side was likely rewritten: read the OTHER side for "
              f"a stale claim before deleting this entry.{RESET}")

    if show_all:
        for rel, ln, s, _ in comparable:
            print(f"  claim {rel}:{ln}  {s[:100]}")
        for rel, s, g in skipped:
            print(f"  {YELLOW}skip{RESET}  {rel} (exempt `{g}`): {s[:80]}")
        for rel, s, why in dropped:
            print(f"  {YELLOW}drop{RESET}  {rel}: {s[:60]} — {why}")

    state, pct = coverage_state(len(comparable), len(skipped))
    coverage = (f"{len(comparable)} of {len(comparable) + len(skipped)} "
                f"universal claim(s) compared ({pct:.1f}%)")

    if problems:
        print()
        for f in problems:
            print(f"{RED}THE SAME UNIVERSAL CLAIM IS STATED IN TWO "
                  f"DOCUMENTS{RESET}  [{f['run']} shared words]")
            print(f"  {f['a'][0]}:{f['a'][1]}")
            print(f"    {f['a'][2][:150]}")
            print(f"  {f['b'][0]}:{f['b'][1]}")
            print(f"    {f['b'][2][:150]}")
            print(f"  shared   : \"{f['run_text']}\"")
            print(f"  {BOLD}Correcting one of these does not correct the "
                  f"other. Fix both and waive the pair, delete one and point "
                  f"at the survivor, or rewrite one to say something scoped "
                  f"to its own page.{RESET}")
        print()
        print(f"{RED}REPEAT LINT: {len(problems)} universal claim(s) restated "
              f"in a second document — {coverage} — exit 1{RESET}")
        return 1

    colour = GREEN if state == "CLEAN" else YELLOW
    print(f"{colour}REPEAT LINT: {state} - {coverage}, 0 restated - "
          f"exit 0{RESET}")
    return 0


# ==========================================================================
def selftest() -> int:
    """The negative controls. Each is labelled REPEAT(<id>) so the expectation
    lint can recover it from this source and report an unregistered one."""
    ok_all, n = True, 0

    def check(label, got, want):
        nonlocal ok_all, n
        n += 1
        good = got == want
        ok_all = ok_all and good
        print(f"  [{GREEN + 'PASS' + RESET if good else RED + 'FAIL' + RESET}] "
              f"{label}")
        if not good:
            print(f"        got  {got!r}\n        want {want!r}")

    print(f"{BOLD}=== A. the forced-red half: the round-30 relocation, "
          f"replanted ==={RESET}")

    # R32-1's OWN SHAPE, REPLANTED. The sentence that shipped in
    # docs/START-HERE.md after round 30 moved it out of README.md and corrected
    # only the copy that stayed. Both halves are here as they shipped.
    RELOCATION = {
        "README.md":
            "The evidence base is one reference build; seven adoption walks, "
            "and every one of them was run by an LLM persona rather than by a "
            "person.\n",
        "docs/START-HERE.md":
            "Relocated from README.md in round 30, intact.\n\n"
            "KNOWN-ISSUES.md says what the kit's adoption tests found — and "
            "every one of them was run by an LLM persona rather than by a "
            "person.\n",
    }
    got, _, _, _ = restatements(RELOCATION)
    check("REPEAT(relocation): a universal that travelled with relocated text "
          "is SEEN, and both sites are named",
          [(f["a"][0], f["b"][0], f["run"] >= MIN_RUN) for f in got],
          [("README.md", "docs/START-HERE.md", True)])
    check("...and the finding prints the run the two share, so a reader does "
          "not have to take it on trust",
          (got[0]["run_text"].endswith(
              "every one of them was run by an llm persona rather than by a "
              "person") if got else
           "NO PAIR FOUND - MIN_RUN has been raised past the motivating "
           "defect"), True)

    # THE ABSOLUTE FORM, which count_lint's quantifier layer structurally
    # cannot reach: `never` takes no noun, so it names no enumerable target.
    # Three round-32 instances were absolutes, which is why this tool's
    # quantifier vocabulary is wider than the layer it sits beside.
    ABSOLUTE = {
        "A.md": "The runner never prints a bare count without a denominator "
                "beside it in the same line.\n",
        "B.md": "Note that the runner never prints a bare count without a "
                "denominator beside it in the same line.\n",
    }
    got, _, _, _ = restatements(ABSOLUTE)
    check("REPEAT(absolute): `never` is compared here even though the "
          "quantifier layer must skip it - it takes no noun, and this tool "
          "needs none",
          [(f["a"][0], f["b"][0]) for f in got], [("A.md", "B.md")])

    # THE COPULA. Three of the round-32 instances read "every X WAS performed
    # by ...", which carries no presence verb at all. If the copula were not in
    # ASSERT_VERB this tool would have been blind to the class that motivated
    # it.
    COPULA = {
        "A.md": "Every adoption test behind this kit's finding counts was "
                "performed by a large language model, not by a person.\n",
        "B.md": "Every one of them was performed by a large language model, "
                "not by a person, and nobody has said otherwise.\n",
    }
    got, _, _, _ = restatements(COPULA)
    check("REPEAT(copula): `was performed by` is an assertion - without the "
          "copula this tool is blind to the class that motivated it",
          len(got), 1)

    print()
    print(f"{BOLD}=== B. the controls that keep it from manufacturing "
          f"findings ==={RESET}")

    # THE MOST IMPORTANT CONTROL IN THE FILE, for the same reason
    # COUNT(true-count) is the most important one in the count lint: a checker
    # that goes red on ordinary prose is a defect generator, and this kit has
    # 100 documents that share a vocabulary.
    DIFFERENT = {
        "A.md": "Every row of the table carries a bracketed source tag.\n",
        "B.md": "Every check in this kit declares where its expectation is "
                "read from.\n",
    }
    got, _, _, _ = restatements(DIFFERENT)
    check("REPEAT(different-claims): two universals about different things do "
          "NOT collide, however alike their vocabulary",
          got, [])

    # CONTIGUITY. This is the reason the measure is a run and not an overlap:
    # negation reverses the meaning and leaves the word bag almost untouched.
    NEGATED = {
        "A.md": "Every row in the sources table carries a bracketed tag "
                "naming where the claim came from.\n",
        "B.md": "No row in the sources table carries a bracketed tag naming "
                "where the claim came from.\n",
    }
    got, _, _, _ = restatements(NEGATED)
    check("REPEAT(negation): a negated restatement IS a finding - it is the "
          "same claim written twice and one of them is wrong",
          [f["run"] >= MIN_RUN for f in got], [True])
    check("...and the shared run excludes the quantifier that differs, so the "
          "printed evidence is the part that really is identical",
          (got[0]["run_text"].startswith("row in the sources table") if got
           else "NO PAIR FOUND - MIN_RUN has been raised past this control"),
          True)

    SAME_DOC = {
        "A.md": "Every one of them was run by an LLM persona rather than by a "
                "person.\n\nSome other paragraph.\n\nEvery one of them was run "
                "by an LLM persona rather than by a person.\n",
    }
    got, comp, _, _ = restatements(SAME_DOC)
    check("REPEAT(same-document): two copies in ONE document are NOT a "
          "finding - a document is edited as a unit and the second copy is "
          "visible to whoever corrects the first",
          (got, len(comp)), ([], 2))

    SHORT = {
        "A.md": "All rows are green.\n",
        "B.md": "All rows are green.\n",
    }
    got, _, _, drop = restatements(SHORT)
    check("REPEAT(word-floor): two SHORT sentences do not collide - they are "
          "dropped with their reason rather than reported",
          (got, len(drop)), ([], 2))

    NO_VERB = {
        "A.md": "Every row of the sources table, the claims table and the "
                "scorecard below.\n",
        "B.md": "Every row of the sources table, the claims table and the "
                "scorecard below.\n",
    }
    got, comp, _, _ = restatements(NO_VERB)
    check("REPEAT(no-verb): a sentence fragment with no verb of assertion is "
          "not a claim and is not compared",
          (got, comp), ([], []))

    PLAIN = {
        "A.md": "The runner reads the gate table and prints one line per gate "
                "it ran, in the order the table gives.\n",
        "B.md": "The runner reads the gate table and prints one line per gate "
                "it ran, in the order the table gives.\n",
    }
    got, _, _, _ = restatements(PLAIN)
    check("REPEAT(no-quantifier): an identical sentence with NO universal in "
          "it is out of scope - this tool checks universal claims, not "
          "duplicated prose",
          got, [])

    print()
    print(f"{BOLD}=== C. the exemptions, the waivers and the state word "
          f"==={RESET}")

    REGISTER = {
        "KNOWN-ISSUES.md":
            "It read: every one of them was run by an LLM persona rather than "
            "by a person, which was false of entry 29.\n",
        "docs/START-HERE.md":
            "The tests found what they found — every one of them was run by an "
            "LLM persona rather than by a person.\n",
    }
    got, comp, skip, _ = restatements(REGISTER)
    check("REPEAT(register): the findings register is exempt as a document "
          "class - it quotes a claim's old wording beside the correction, so "
          "the two necessarily collide",
          (got, len(comp), len(skip)), ([], 1, 1))

    PROMPT = {
        "docs/walks/walk-13-thorough-adopter.md":
            "PERSONA: you execute every command exactly as printed and you "
            "verify every checkpoint the document states.\n",
        "docs/walks/read-30-recon-secops.md":
            "PERSONA: you execute every command exactly as printed and you "
            "verify every checkpoint the document states.\n",
    }
    got, comp, skip, _ = restatements(PROMPT)
    check("REPEAT(verbatim-prompt): a published prompt page is exempt too - "
          "it is a record of what was said on a date and correcting it would "
          "falsify the record",
          (got, len(comp), len(skip)), ([], 0, 2))

    WAIVERS[("A.md", "B.md")] = "a deliberate restatement, ruled once"
    try:
        got, _, _, _ = restatements(ABSOLUTE)
        check("REPEAT(waiver): a pair a human has ruled deliberate is WAIVED, "
              "not silently dropped - it is still found and still printed",
              [(bool(f["waiver"]), f["waiver"]) for f in got],
              [(True, "a deliberate restatement, ruled once")])
        WAIVERS[("A.md", "B.md")] = "   "
        got, _, _, _ = restatements(ABSOLUTE)
        check("REPEAT(empty-waiver): an EMPTY reason is not a waiver - it is "
              "the silent case wearing a label",
              [f["waiver"] for f in got], [None])
    finally:
        WAIVERS.pop(("A.md", "B.md"), None)

    check("REPEAT(state-word): a run that skipped nothing is CLEAN",
          coverage_state(777, 0), ("CLEAN", 100.0))
    st, pc = coverage_state(760, 554)
    check("REPEAT(state-word): a run that compared 760 of 1314 - this kit at "
          "`d52f8a5` - is PARTIAL, and the percentage is printed rather than "
          "the word `clean`",
          (st, round(pc, 1)), ("PARTIAL", 57.8))

    check("REPEAT(shipped-waiver): every shipped waiver carries a non-empty "
          "reason", [k for k, v in WAIVERS.items() if not (v or "").strip()],
          [])

    check("REPEAT(unused-waiver): a waiver whose pair no longer matches is "
          "reported as UNUSED - the correction-travel tripwire - and a "
          "waiver with a live pair is not",
          unused_waivers(
              [dict(a=("A.md", 1, "s"), b=("B.md", 1, "s"))],
              {("A.md", "B.md"): "live", ("C.md", "D.md"): "dead"}),
          [("C.md", "D.md")])

    print()
    print(f"{BOLD}=== D. this tool against the kit it ships in ==={RESET}")
    root = Path(__file__).resolve().parent.parent
    paths = kit_documents(root)
    check("the kit's own documents are found", len(paths) > 10, True)
    docs = {}
    for p in paths:
        try:
            docs[p.relative_to(root).as_posix()] = p.read_text(
                encoding="utf-8")
        except OSError:
            pass
    _, comp, skip, _ = restatements(docs)
    # A pattern that matches nothing is a check that proves nothing - the same
    # assertion the citation lint's section E and the count lint's section D
    # make about themselves.
    check("...and this tool SEES universal claims in them", len(comp) > 0, True)
    check("...and the exempt classes really are populated, so neither branch "
          "of the exemption rule is untested by the tree it ships in",
          len(skip) > 0, True)

    print()
    print((GREEN if ok_all else RED)
          + f"REPEAT-LINT SELFTEST: {'PASS' if ok_all else 'FAIL'} "
            f"— {n} checks" + RESET)
    return 0 if ok_all else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Is this universal claim stated in more than one "
                    "document? A correction to one copy does not travel to "
                    "the others.",
        epilog="exit 0 clean · 1 a claim is restated · 2 abort")
    ap.add_argument("--root", default="", help="the tree to lint")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--list", action="store_true",
                    help="print every claim compared, skipped and dropped")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    root = Path(a.root).resolve() if a.root \
        else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"{RED}REPEAT LINT: ABORT — no such directory: {root}{RESET}")
        return 2
    return run(root, a.list)


if __name__ == "__main__":
    sys.exit(main())
