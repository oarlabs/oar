# Module 05 — Status board

Ambient state, always visible, costing no tokens and no attention.

## Files

| File | What it is |
|---|---|
| **`tools/statusline.py`** (at the kit root) | The **portable** board. Stock Python, runs anywhere, `--selftest` renders all four banner states, `--demo` renders a sample. **Start here.** |
| `statusline.ps1.template` | The **Windows-optimised** variant of the same contract. Richer live-agent detection; requires pwsh. |
| `CONTRACT.md` | The `sidequest.json` file contract: schema, lifecycle, reader behaviour, and how to adopt either side alone. |

**Pick one.** Both satisfy `CONTRACT.md`; running both means two boards
disagreeing about the same session.

The Python board exists because every other executable in the kit is stock
Python: a kit that claims to be host-agnostic cannot have one component that
refuses to start on Linux.

## Wire it — the JSON, inlined for each variant

You do **not** need module 02 for this. Paste the block straight into your
harness settings file (for Claude Code: `.claude/settings.json`). If you *did*
adopt module 02, merge this key into the settings you already substituted from
its template rather than keeping two files.

> **The escaped `\"` below is correct on THIS route and forbidden on the other
> one.** Here you are hand-writing JSON, where `\"` is the legal way to quote a
> path inside a string. Module 02's route substitutes `kit.config`'s
> `STATUSLINE_CMD` value into an already-quoted JSON string — its settings
> template reads `"command": "<the STATUSLINE_CMD slot>"` — so a double quote in
> *that* value closes the string and the settings file stops parsing, and
> unparseable settings mean no hooks either. If you adopt module 02 later, do
> not carry these quotes into
> `STATUSLINE_CMD`: use an unquoted path, or single quotes if it contains
> spaces. QUICKSTART Step 4 and `kit.config.local.example` state the rule for
> that route; `KNOWN-ISSUES.md`'s **SB-B** is the failure it prevents, which has
> already happened once.

**Portable (recommended):**

```json
{
  "statusLine": {
    "type": "command",
    "command": "python \"/ABSOLUTE/PATH/TO/YOUR/REPO/tools/statusline.py\"",
    "padding": 0
  }
}
```

**Windows / pwsh variant:**

```json
{
  "statusLine": {
    "type": "command",
    "command": "pwsh -NoProfile -ExecutionPolicy Bypass -File \"C:/ABSOLUTE/PATH/TO/YOUR/REPO/tools/statusline.ps1\"",
    "padding": 0
  }
}
```

**Use an absolute path.** The harness does not promise you a working directory,
and a relative command that fails to start produces *no board at all* — which
reads exactly like "nothing is happening".

## What the harness sends it — the stdin schema

The board reads **one JSON object on stdin** and writes **one ANSI line** (plus
one line per live agent) on stdout. Every field is optional; each drives one
segment, and a field the harness does not send simply drops that segment.

```json
{
  "session_id": "abc123",
  "model":          { "display_name": "lane-tier" },
  "context_window": { "used_percentage": 82,
                      "total_input_tokens": 410000,
                      "context_window_size": 500000 },
  "cost":           { "total_cost_usd": 3.45,
                      "total_duration_ms": 5400000,
                      "total_lines_added": 120,
                      "total_lines_removed": 30 }
}
```

| Field | Segment | If absent |
|---|---|---|
| `session_id` | live-agent lines | segment dropped (also needs `AGENT_TRANSCRIPT_DIR`) |
| `model.display_name` | `⚡ lane-tier` | dropped |
| `context_window.used_percentage` | the context bar | **`ctx ?` placeholder — see below** |
| `context_window.context_window_size` + `total_input_tokens` | fallback percentage | used only when `used_percentage` is missing |
| `cost.*` | spend, wall clock, ±lines | each dropped individually |

**The one field that never drops silently is the context bar.** A missing or
differently-named context key renders a dim **`ctx ?`** instead of removing
the segment, because an absent bar reads as *"plenty of room left"* — the most
dangerous thing this board could imply — while `ctx ?` says *"I do not know"*,
which is the true statement. Same rule as the sidequest banner, applied to the
other segment that carries a warning.

**If your harness sends a different shape**, map it in `render()` — that
function is the entire adapter, and `--selftest` will tell you when you have
broken something.

Nothing else is read from stdin. The board makes no network calls, writes no
files, and runs one short `git` invocation for the branch segment.

## Configuration, and the defaults that mean you can skip it

`tools/statusline.py` reads `kit.config` (the same four-step search every tool
here uses) but **every key has an in-module default**, so the board renders
before you have configured anything:

| Key | Default | What it does |
|---|---|---|
| `SIDEQUEST_FLAG` | `.claude/sidequest.json` | the flag file whose existence is the banner |
| `SIDEQUEST_STALE_DAYS` | `3` | past this, the banner turns amber and says `STALE` |
| `STATUS_BAR_CELLS` | `16` | width of the context bar |
| `STATUS_CLEAR_MARK_PCT` | `75` | where the clear mark sits |
| `STATUS_BOARD_LINE_FILE` | `NONE` | optional hand-maintained stage line |
| `AGENT_TRANSCRIPT_DIR` | `NONE` | harness-specific; `NONE` drops the live-agent segment |
| `STATUS_ESCAPE_LEDGER` | `NONE` | opt-in escape-rate segment; see below |
| `PROJECT_ROOT` | *(empty)* | see below |

### `PROJECT_ROOT` must be absolute — or the board says so out loud

A relative or missing `PROJECT_ROOT` resolves against wherever the harness
happened to launch the board. On a foreign working directory the flag file is
not found, and **an open side quest silently vanishes from the board** — which
is precisely the silent degradation `CONTRACT.md` forbids.

So the portable board resolves the root as: absolute `PROJECT_ROOT` → nearest
`.git` ancestor → give up **and print a visible amber warning segment**. It
never simply drops the banner. Set an absolute `PROJECT_ROOT` in
`kit.config.local` and the question never arises.

### The escape-rate segment — opt-in, and off until you name a ledger

**The portable Python board only.** `statusline.ps1.template` does not carry
this segment. The "one contract" both implementations satisfy is `CONTRACT.md`,
the `sidequest.json` file contract, which is untouched and unaffected either
way — but a reader should not have to work that out, so it is stated here and
in the root README's module row.

Set `STATUS_ESCAPE_LEDGER` to the ledger carrying your escape-rate table — the
same file module 03's `escapes` gate reads — and the board grows one segment:

```
esc 19.3% █▄▄▇▃▄▁▁█▄█▁▃ +1 uncounted RISING
```

The percentage is the overall rate. Each tick is one counted round, oldest
first, **scaled against the ceiling**: a round at or over the ceiling is a full
tick, and the last sixteen rounds are drawn. Scaling to the ceiling rather than
to the highest round in the series is deliberate — series-relative scaling makes
1%, 2%, 1% look like a mountain range and makes every project's picture look
equally dramatic, while the ceiling is the line the number is actually judged
against.

**This module's own advice is "resist adding segments", and it still stands.**
That is why this one is off by default. An adopter who never names a ledger
pays nothing: no segment, no marker, no file read, not even the import of the
tool. The argument for offering it at all is that the escape rate is the one
project number whose *trend* is the signal — a rate that stops falling means
the loop is witnessing rather than learning — and a trend nobody looks at
between certifications is a trend nobody acts on.

**The numbers are not computed here.** The board imports
`modules/04-ledgers/escape_rate.py` and calls it. A ledger parser living in the
status board would be a second reader of one table, drifting from the tool the
gate runs, and the two would publish different numbers from the same file with
both runs green. The board looks for the tool beside itself in `tools/` first,
then in the kit's `modules/04-ledgers/` layout.

| Situation | Segment |
|---|---|
| `STATUS_ESCAPE_LEDGER` unset | **Nothing at all.** The one state that asserts nothing, so it is the one state allowed to be silent. |
| Configured, `escape_rate.py` not found | `esc UNAVAILABLE (escape_rate.py not found)` on amber — the wiring is wrong, not the project. |
| Ledger missing, unreadable, or malformed | `esc LEDGER ABORT: <the tool's own sentence>` on the loud red field. **Never dropped** — an aborting instrument that renders as no segment reads as a good score. |
| No rounds recorded yet | `esc NO-ROUNDS-RECORDED` — the tool's state word, verbatim. **Never `esc 0.0%`**, which is the same flattering lie the tool's exit-code contract exists to prevent. |
| Measured | the rate, the sparkline, `+N uncounted` when rounds were excluded from the denominator, and `RISING` (amber) or `OVER` (red) when either applies. |
| Latest round under the gate's denominator floor | the rate and sparkline as above, with the literal `SMALL-N` suffix on amber (plus `RISING` when the trend also rises). The cumulative number is still fully measured, so the board keeps it — only the per-round ceiling was not armed (the floor is `ceil(100/ceiling)`, derived in `escape_rate.py`). |

**Cost, measured rather than assumed.** On the kit's own 1071-line ledger,
averaged over 20 renders: **5.8 ms one-off to import the tool, 1.4 ms per
render to read and parse**. A whole render is about 54 ms with the segment on
against about 45 ms with it off — the difference is the segment, on a render
dominated by the `git` subprocess. With the key unset nothing is read and the
tool is never imported.

**There is no cache**, and adding one would not help: the harness starts a
fresh process per render, so an in-memory cache would never hit, and a cache
*file* would break a load-bearing property of this module — the board reads
state and writes none.

**The tick characters are derived, not hard-coded.** A pipe gets the block
ramp: `main()` reconfigures the stream to UTF-8 before writing, and the reader
decodes it. A *console* is asked whether its own code page can carry the blocks,
and gets an eight-step ASCII ramp (`_.:-=+*#`) when it cannot. The operating
system is not consulted, because it is the wrong question in both directions —
a Windows terminal set to UTF-8 draws the blocks, and a POSIX host under
`LANG=C` does not. Residual, stated: a console that misreports its code page is
not visible from inside the process, and the board's other segments draw block
and box characters unconditionally — that predates this segment and is
unchanged by it.

## What the board is for

The two facts you most need mid-session are the two your transcript cannot show
you:

1. **What is running right now, and at what tier.** An agent silently inheriting
   the orchestrator tier is invisible everywhere else, and the cost compounds
   for the length of the session.
2. **How close the context window is to the point where clearing beats
   continuing.** The mark encodes a property of **your documentation**, not of
   the model. Move it if your resumes are expensive. `STATUS_CLEAR_MARK_PCT`
   and module 01's `CHECKPOINT_GLOB` are two halves of one contract: the mark
   sits where clearing beats continuing, and what makes clearing cheap is the
   newest checkpoint. If your checkpoints rot, move the mark right — or better,
   fix the checkpoints. (Doctrine: BLUEPRINT §7.)

The bar is coloured by **position**, not by fill, so it shows the terrain ahead
rather than only where you are.

## Verify it before you wire it

A status line that throws is a status line that gets removed within the day, and
then you have no board at all.

```bash
python tools/statusline.py --selftest    # all four banner states, rendered
python tools/statusline.py --demo        # what it looks like with real data
```

<details><summary>PowerShell variant</summary>

```powershell
$errs = $null
[System.Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path tools\statusline.ps1), [ref]$null, [ref]$errs)
$errs.Count    # must be 0

'{"session_id":"s1","model":{"display_name":"lane"},
  "context_window":{"used_percentage":82,"total_input_tokens":410000}}' |
  pwsh -NoProfile -File tools\statusline.ps1
```
</details>

Exercise all four sidequest states: no flag, a fresh flag, one older than
`SIDEQUEST_STALE_DAYS`, and a corrupt one. All four must produce a *defined*
rendering, and the corrupt one must be loud. `--selftest` does exactly that and
prints each banner so you can see it.

## The one design rule

**Every segment is guarded.** A missing field, an unreadable file, an absent git
repo: the segment disappears and the board still renders. The exceptions are the
segments where silence would assert something false:

- a corrupt sidequest flag renders a loud `SIDEQUEST (state file unreadable)`;
- an unresolvable `PROJECT_ROOT` renders a loud warning segment;
- a missing or misnamed context key renders `ctx ?`;
- a configured escape-rate ledger that cannot be read or parsed renders the
  abort. With no ledger configured the segment does not exist, which is the one
  state that asserts nothing.

## File contract with other modules

- **↔ 06-sidequest** via `CONTRACT.md`. The skill **writes and deletes** the
  flag; the board **only reads** it. Neither imports the other.
- **→ 03-verification, and this one is easy to miss.** `sidequest.json` must be
  **gitignored**. It is session state, not tree state — and if it lands inside
  your `JUDGE_PATHS` or `CERT_PATHS` (both of which commonly include `.claude/`),
  then merely *opening a side quest* turns the `judges` gate red and
  certification becomes impossible until the quest closes. Add the ignore rule
  at the same moment you adopt either module. `CONTRACT.md` states the same
  coupling from the other side.
- **→ 04-ledgers, and only when you opt in.** Setting `STATUS_ESCAPE_LEDGER`
  makes the board import `escape_rate.py` and render its numbers. The board
  never parses the ledger itself; if the tool is not present the segment says
  `UNAVAILABLE`. Leave the key `NONE` and the two modules do not touch.
- **← 02-enforcement.** Its `settings.json.template` carries a `statusLine`
  block for convenience. If you skipped module 02, use the inlined JSON above —
  you do not need that template.
- **`kit.config`** supplies every path and threshold, and every one has a
  default.

## What breaks if you adopt this module alone

Nothing. Without module 06 the sidequest banner never appears (or you write the
flag by hand). Without module 02 you paste the `statusLine` JSON above yourself.
Without module 04 you leave `STATUS_ESCAPE_LEDGER` at `NONE` and that segment
never exists. The board reads state; it never writes any.

## Adaptation notes

- **Extend the live-agent block** to your harness's transcript layout, or leave
  `AGENT_TRANSCRIPT_DIR = NONE` and lose only that segment.
- **Resist adding segments.** Every one competes with the two facts above. The
  hand-maintained board line exists precisely so stage state can change without
  the board growing another parser to go stale.
