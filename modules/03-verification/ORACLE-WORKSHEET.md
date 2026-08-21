# The Oracle Worksheet — manufacturing your first check

> **If you cannot state the check for done, you are not ready to charter the
> lane.**

An **oracle** is anything that can tell you, without a human reading the output,
whether a result is correct. Some projects get one free: a rewrite can diff
against the original; a port can compare byte-for-byte; a spec-conformant format
has a validator. Most projects get nothing free, and the honest response is not
"we'll test it manually" — it is **manufacture one**, deliberately, before you
build the thing it measures.

This worksheet is the menu, then the questions, then the traps.

---

## Part 1 — the shapes, cheapest first

### 0. Example-based tests (the one you already have — and the degenerate case)

"Call it with these inputs, assert these outputs." Unit tests, table tests, most
integration tests. **This is a real oracle** and it is where nearly everyone
starts, so it is named here rather than left implicit — a worksheet that offers
five exotic shapes and omits the obvious one reads as a demand to be clever.

- **Costs:** one case at a time, forever.
- **Catches:** exactly the cases you thought of.
- **Fails at:** everything you did not think of — which is the entire defect
  population you are actually worried about. It is degenerate in a precise
  sense: **the oracle is a list you wrote by hand, so it can only be as complete
  as your imagination on the day.** Its coverage does not grow with the system;
  it grows with your typing.

**How to upgrade, in increasing order of leverage** — each of these turns your
existing cases into something that generalises:

| From | To | Move |
|---|---|---|
| a handful of hand-written cases | **golden outputs (1)** | stop asserting fields one by one; freeze the whole output and diff it |
| assertions you wrote by hand | **differential (2)** | assert *equality with a reference* instead of equality with a literal |
| cases you invented | **record–replay (3)** | capture real traffic and replay it; your users write the cases |
| "output should be X" | **metamorphic (4)** | "output(f(x)) must relate to output(x) *this way*" — no literal needed |
| an unbounded output space | **allowed universe** | define what may legitimately appear; anything else is a defect by definition |

A good project keeps its example tests **and** manufactures one of the shapes
below. The upgrade is additive; example tests remain the best way to pin a
specific bug you just fixed so it can never come back.

### 1. Golden outputs (record once, compare forever)

Run the system on fixed inputs, eyeball the output **once, carefully**, and
freeze it. Every future run diffs against the frozen copy.

- **Costs:** an afternoon of careful eyeballing.
- **Catches:** every unintended change, including ones nobody thought to test.
- **Fails at:** legitimate change — a golden file that is updated casually is a
  golden file that certifies whatever you last did. Make updating one a
  reviewed commit with a stated reason, on a judgment-bearing path.
- **Use when:** output is deterministic and human-checkable at least once.

### 2. Differential (two implementations, same input)

Run two things that should agree: old vs new, fast path vs reference path, your
implementation vs a library's, one platform vs another.

- **Costs:** keeping the reference alive.
- **Catches:** everything the reference gets right — an enormously broad net for
  very little code.
- **Fails at:** anything both sides get wrong, and at legitimate divergence
  (which you must enumerate, not discover).
- **Use when:** a reference exists at all. This is the free oracle a rebuild
  gets, and it is worth *manufacturing* a throwaway reference to obtain it.

### 3. Record–replay (capture real usage, replay it)

Capture real inputs — requests, events, commands, an input tape — and replay
them against a candidate build, diffing the resulting state.

- **Costs:** a capture format and a replay harness; more than it looks.
- **Catches:** regressions under *real* usage rather than imagined usage. It is
  also the only shape that instruments **feel**: "sluggish" becomes
  input-to-response latency measured over a replayed tape.
- **Fails at:** anything not in the tape, and anything the recording perturbs.
- **Traps, all paid for in the reference build:**
  - **Wall-clock windows.** Any timeout, debounce, or double-click window read
    from a real clock makes replay non-deterministic. Inject the clock, or
    record the *resolved outcome* instead of the raw event.
  - **Serialisation loses precision.** Floats through JSON is the classic:
    round-trip your tape format and diff it against itself before you trust one
    byte of a replay diff.
  - **Measure the noise floor first.** Run the same input twice on the same
    build and diff. Whatever differs is noise, and any replay check that does
    not know its own noise floor will report it as signal forever.

### 4. Metamorphic properties (relations that must hold)

You cannot say what the right answer is, but you can say how the answer must
*relate* to another answer:

- same seed → same world;
- sort then filter ≡ filter then sort;
- doubling every price doubles the total;
- an idempotent operation applied twice ≡ applied once;
- a round trip (encode→decode, save→load, export→import) returns the original.

- **Costs:** thinking. Almost no code.
- **Catches:** deep logic errors no example-based test would reach.
- **Fails at:** errors that preserve the relation (both sides wrong the same
  way).
- **Use when:** you have no idea what correct output looks like. This is the
  shape people forget exists, and it is usually available.

### 5. Self-tested scorers (a judge you have judged)

When the property is fuzzy — "grounded", "readable", "no invented facts" —
write a **scorer**, then test the scorer against labelled cases the way you
would test any other code.

- **Costs:** the scorer, plus its own test set. Effectively two components.
- **Catches:** the fuzzy class nothing else reaches.
- **Fails at:** everything until proven — an unproven scorer is an opinion with
  a number attached, and a number is more persuasive than it deserves to be.
- **The rule:** a scorer's **precision is its own quality bar**. An
  over-firing flag erodes trust exactly the way a silent miss erodes safety,
  because an alarm the operator learns to skim is a dead alarm. Soft-flag for a
  human until precision is proven; only then let it block.

**The allowed-universe trick generalises across all five shapes.** Define the
closed set of things that may legitimately appear — vendors, commands, string
literals, effects, file writes, network hosts. Anything outside the set is a
defect *by definition*, detectable deterministically with no judgment call. It
turns "is this right?" (uncomputable) into "is this in the set?" (a lookup).

---

## Part 2 — the worksheet

Fill this in **before** chartering the lane. One page per check.

```
CHECK NAME            <the name that will appear in the JUDGMENT LEDGER>

THE RULING IT HOLDS   <the owner's words, verbatim>

FAILS WHEN            <one sentence: what makes it go red>

SHAPE                 golden | differential | record-replay | metamorphic |
                      scorer | allowed-universe

REQUIRED OUTPUT LINE  <the exact line a run prints when green - the line the
                      gate greps for. Write it now; if you cannot, you do not
                      yet know what this check measures.>

THE FLOOR             <the minimum count the line must carry, and WHY that
                      number. "0 of 0 passed" is a well-formed success line.>

NEGATIVE CONTROL      <the specific mutation that must make it red, and how you
                      will apply it WITHOUT editing a repo file>

RUNTIME               <seconds. A check nobody runs is not a check, and the
                      threshold is lower than you think.>

WHAT IT DOES NOT      <the honest gap. Write it down here, or discover it in
COVER                  production and call it a surprise.>

COVERAGE ESCAPE       <Read the gap you just wrote, then answer: if a human
RISK                   reports a defect that falls in it, will this check be
                       reported as "green" at the time? If yes, you have
                       PRE-DECLARED an escape - which is fine, and much cheaper
                       than a surprise, PROVIDED it goes in the judgment ledger
                       as UNCHECKED with this reason. The trap is a green suite
                       measuring the wrong SURFACE: floors that covered arrival
                       when the complaint was about the journey. Growth in check
                       COUNT never closes that; only asking "what surface is
                       this measuring?" does.>
```

---

## Part 3 — the five laws

1. **Negative controls, always.** A check that has never been red is unproven.
   Prove it red *before* you count on it, and prove it red *without editing a
   repo file* — that is what the runner's `--nc` facility is for. An edit-based
   negative control is one forgotten revert away from becoming permanent.

2. **The oracle itself must be verified against the source.** A guardrail is
   only as trustworthy as the data behind it. "Verify against the source"
   applies to your checks, not only to your outputs.

3. **Grounded is not the same as coherent.** Every part being real does not make
   the combination right. Coherence needs its own oracle, and a crude one
   over-fires. Soft-flag until precision is proven.

4. **Loud failure over silent drop, at every layer including plumbing.** A
   correct result must never die to a missing brace. Anything salvaged is
   flagged as repaired, never laundered into looking clean.

5. **Verify in the target environment.** A pass is scoped to the environment it
   ran in. Name that scope, then simulate the target's distinguishing property
   inside the gate: boot the *exported* artefact, not the development run; test
   the *deployed* encoding, not your terminal's.

---

## Part 4 — continuity, the check everyone skips

Every shape above certifies a **moment**. Somebody lives with your artefact
**across** builds.

> **State written by build N must load and run in build N+1, checked
> mechanically at certification.**

Concretely: commit a fixture produced by the last certified build; at cert
time, load it in the candidate and assert hard properties (it opens; it runs
forward; a set of invariants hold). A certifying run then mints the fixture the
*next* certification will be judged against — so the gate is self-perpetuating,
and by construction a certifying run ends with an uncommitted fixture that the
stage-close checklist has to remember to commit.

Its absence is invisible: nothing fails, nobody complains, and then one release
eats everyone's saved state at once.

**Not every project carries state across builds** — a pure function, a
stateless renderer, a build tool with no persisted artefacts genuinely has
nothing to continue. Say so explicitly rather than skipping the section, because
"we thought about it and there is nothing" and "we never thought about it" are
indistinguishable from the outside a year later:

```
CONTINUITY GATE       present | N/A

IF N/A, WHY           <the specific reason nothing survives a build boundary:
                       no persisted state, no user-authored files, no wire
                       format, no cache with a lifetime longer than a run.>

WHAT WOULD CHANGE     <the first feature that would make this section apply -
THIS                   a save file, a database, an exported document, a public
                       API response shape. Name it now; you will ship it later
                       and nobody will re-read this page unprompted.>
```

---

## Part 5 — the escape rate, the only metric that says whether this is working

For each round, count the items reported by a human that **an existing check
should have caught**. That is an **escape**.

- Escapes are your real quality metric, not the size of your test suite.
- Every escape gets a check *in the same round*, alongside the code fix.
- Publish the number every round. **If it does not fall, the loop is witnessing,
  not learning** — you are cataloguing defects rather than converting them.

Two escape shapes recur often enough to name:

- **The inversion escape.** A round improves something deliberately, and a later
  round undoes it *in equally good faith*, because nothing but prose sat under
  the original ruling. This is what the JUDGMENT LEDGER exists to prevent.
- **The coverage escape.** A green suite that measures the wrong surface — the
  checks covered arrival and the human's complaint was about the journey. The
  worksheet's COVERAGE ESCAPE RISK box (Part 2) is where you pre-declare these,
  one check at a time, *before* they escape.
