# EYES — a screenshot instrument and a look-quality loop, level 1

Agents ship views nobody has seen. `eyes.py` renders a page with an isolated,
headless Chromium and prints a fixed catalog of ten questions for a reader
(a person or an agent with a file-reading tool) to answer against the PNG.
The mechanical half — does a PNG exist, is it fresh, is it the right size,
is it not blank — runs first and needs no model. The catalog does need one:
a pixel check cannot find cut-off text, and this page says so rather than
implying a fuller net than the tool casts.

**Lineage.** Nearest published ancestors: Chromium headless screenshot (the
render mechanism itself); pixel-diff visual regression (the shape of gating
a render — compare against a stored image, fail on change). What is new
here: the ten-question catalog as the judged content, answered by a reader
rather than a pixel diff, with the mechanical existence/freshness/dimension/
blank checks running first and needing no model. See
`checks-registry.json`'s `gate:eyes` and `selftest:eyes` rows for the
seen-red dates.

Level 1 only. Level 2 (a caged, interactive browser with fixed verbs — open,
click, type, read, shot) is held, planned but not built, per a private
design record ("EYES — a screenshot instrument and a look-quality loop,"
2026-09-15, section 3). This module does not need it and does not build
toward it.

## The three verbs, plus the gate

```
python eyes.py shot --src <file-or-url> --out <dir> [--viewports W1xH1,...]
python eyes.py ears --src <file-or-url> --out <dir>   # shot + console capture
python eyes.py look --out <dir>                        # print the catalog
python eyes.py look --fixture                          # calibration only
python eyes.py gate <out-dir>                           # the verify.py gate
python eyes.py --selftest
```

**`shot`** finds a Chromium (Edge, Chrome or Chromium — on PATH, then the
standard per-OS program folders, then `kit.config`'s `BROWSER_PATH`, then an
explicit `--browser` override), renders the source at each named viewport
(default `1280x720`, `1920x1080`, and `400x850` for a phone), and writes one
PNG per viewport plus `manifest.json`: the source (repository-relative, or
the URL as given — never a workstation path), the source's sha256 (local
files only), the render clock, the browser's version, and the per-viewport
dimensions and filenames.

**`ears`** is `shot` plus a console capture: Chromium's own
`--enable-logging=stderr --v=1` output, filtered down to lines Chromium
tags `CONSOLE:` (its own marker for a page's `console.error`,
`console.warn` and uncaught-exception output) whose `source:` is not a
`chrome-extension://` origin. See "What this does not prove" below for the
residual that filter leaves.

**`look`** prints the ten-question catalog as a fixed report shape, one row
per question per viewport, with the evidence column naming the PNG. It does
not judge the image — it has no vision — it prints the template a reader
fills in and saves as `look-report.json` beside the manifest:

```json
{"answers": {"<viewport>": {"<item#>": "yes"|"no", ...}, ...}}
```

`look --fixture` instead prints the shipped fixture's known calibration
answers (see "The fixture," below) so a reader can check their own reading
against a known instance before trusting their reading of a real page.

**`gate`** is what `verify.py`'s `eyes` entry shells out to. It reads
`manifest.json` and `look-report.json` from a `shot`/`ears` output directory
and prints exactly one line:

```
EYES: state SEEN; shots 2; viewports 1280x720,1920x1080; catalog 20/20 answered; yes 0
```

## Decision 5 — the profile and the network

Every render gets a fresh `--user-data-dir` under the output folder: no
extensions, no sync, no history from any other run. The network is blocked
by default (`--host-resolver-rules=MAP * 0.0.0.0`, resolving nothing);
`--allow-hosts <host> [<host> ...]` punches named exceptions and the
manifest records which hosts were allowed. A page under test that cannot
render from the box alone is a finding worth reading, not a reason to widen
the default.

## Decision 6 — the ask before the local browser

This tool never opens the owner's own browser or the owner's own profile.
Every command it issues to a Chromium binary carries `--headless=new` and
an absolute, fresh `--user-data-dir` under the output folder — unconditionally,
including the tool's internal version read (which, per the finding below,
does not launch the browser at all). There is no flag, anywhere in the CLI
or in the functions that build a browser command, that removes either one;
`--selftest` section E reads that guarantee back out of the actual argument
list the tool builds and out of the command-builder functions' own
signatures, so the claim is checked, not merely stated.

When the isolated path cannot do the job — a page behind a login, a session
only the owner's own profile holds, a render the isolated path genuinely
cannot produce — `shot` does not fall back. It stops: exit 2, on the
source itself not being reachable at all, and exit 2 again, with the same
three-part ask, on any render that comes back non-zero (a timeout, a
crash, a viewport that never wrote its PNG) — never a bare exit 1 with
"see logs." Either way the ask names the page, why the isolated render
failed, and what the local browser would expose, to the owner, at his own
prompt, by a person. There is no
`--use-local-profile` flag and there will not be one.

## The catalog

| # | Question |
|---|---|
| 1 | Cut-off text: an ellipsis, a clipped glyph at an edge, a first or last character missing. |
| 2 | Overflow: a scrollbar where the design has none; content past the viewport edge. |
| 3 | Overlap: one element drawn over another. |
| 4 | Alignment: a row whose items do not share a baseline; a grid with a ragged column; a control block that does not line up with its label. |
| 5 | Reflow on state change: rendered twice (idle and lit, empty and full), elements that moved between the two. |
| 6 | Contrast: text or a state color unreadable against its ground. |
| 7 | Indistinguishable labels: two elements that read the same after truncation. |
| 8 | Empty regions: a panel with nothing in it; a blank render. |
| 9 | The wrong state rendered: a lamp color that disagrees with the data the page claims. |
| 10 | The ears: any JavaScript error, failed fetch or warning in the log. |

The same ten questions are now a standard section of module 01's
`PUNCH-LIST-TEMPLATE.md`, so every drive and every lane answers the same
list.

## The fixture

`examples/eyes-fixture/before-1280.png` is a real "before" screenshot from
an earlier UI pass, copied in — not rendered by this tool, since it
predates it. Its documented, known answers are **yes on items 1, 2, 5 and
7** (a clipped readout line, tell-tales cut at the panel's bottom, a grid
reflow, and nine plates reading the same word) — `look --fixture` prints
exactly this set. A reader whose own reading of the fixture misses one of
these four is miscalibrated before they ever look at a real page.

## The example render

`examples/eyes-page/index.html` is the module's own render target for the
`eyes` gate in `verify.py`, committed alongside its rendered output in
`examples/eyes-render/` (PNGs, manifest, console captures, and a
hand-answered `look-report.json`) — the same shape `example_unit` and
`example_lint` use their own committed scripts for. The page is
deliberately defect-free, so the committed render's `yes` count is honestly
`0`. Point the gate's `cmd` in `verify.py` at your own rendered output on
adoption.

## What this does not prove

- **A pixel check cannot find cut-off text.** The mechanical half (exists,
  fresh, right dimensions, not blank) is necessary and is not sufficient;
  every catalog question past "is there a render at all" needs a reader.
- **Staleness is only checked for a local file source.** A URL source
  carries no sha in the manifest — re-checking it would mean a second
  fetch, which is a second render, not a freshness check, so the gate
  cannot detect a URL's page having changed since the shot.
- **`ears` reliably catches `console.error`, `console.warn` and uncaught
  exceptions, and only those.** Measured against a planted probe page on
  this workstation: a bare failed resource load (a missing image, a
  blocked fetch) for a `file://` source did not produce a `CONSOLE:` line
  on its own — only what the page's own script explicitly routes to
  console is guaranteed to surface. Item 10 of the catalog is scoped to
  what Chromium actually reports, not to every possible resource failure.
- **The browser's version is read from the binary's own file metadata, not
  from a live probe.** Measured on this workstation: `--headless=new`
  combined with any exit-and-print flag (`--version`, `--product-version`)
  does not return — confirmed to 90 seconds, and it is not specific to
  `--version`: headless mode with no `--screenshot`/`--dump-dom` (nothing
  telling it to do one thing and exit) simply does not exit on this box's
  installed Edge (153.0.4234.32). `file_version()` reads the Windows PE
  VERSIONINFO resource via `ctypes` (stock, no dependency) instead, with a
  version-looking sibling-directory fallback on other platforms. The
  isolated command-builder for a live probe (`build_version_cmd`) still
  exists and is still proven isolated by `--selftest`, for a caller who
  wants one and can bound it; the render path does not call it.
- **The blank check is sampled, not exhaustive**, for cost on large images —
  a pathological one-pixel defect surrounded by a uniform field could read
  as blank. The catalog's own questions are the check for content that
  matters; the blank check exists to catch the failure mode a render
  producing nothing at all would otherwise pass silently.

## Failure and maintenance

- **No browser on the box:** `shot` writes a manifest recording it, prints
  `EYES: state NO-BROWSER`, and exits 3 — no render attempted. The `eyes`
  gate reads that state and vetoes it; NO-BROWSER never reads as green.
- **Chromium changes a flag:** every flag lives in `build_shot_cmd` /
  `build_version_cmd`, two pure functions; `--selftest` asserts their
  output directly, with no subprocess, so a broken flag list reds the
  selftest rather than a lane's render.
- **A page stops being re-shot:** the manifest's source sha goes stale
  against the source file, the gate reports `STALE`, and `STALE` is
  vetoed — a rotted look never certifies as current.
- **A checkout changes a source page's line endings:** `source_sha256` is
  computed with CRLF normalized to LF at both write and check, so
  `core.autocrlf` (on by default for Git for Windows) does not turn a
  clean checkout into a false `STALE`. `.gitattributes` also pins every
  file under `examples/**` to `text eol=lf`, so the committed example's
  own bytes stop moving across checkouts in the first place.
- **A render fails outright:** any non-zero render (a timeout, a crash, a
  viewport whose PNG never gets written) exits 2 with the same three-part
  ask decision 6 names — never a bare exit 1 with "see logs."
- **A source is given outside the repository:** `shot` refuses before
  writing anything — `EYES: state NOT-RUN; source outside the
  repository; copy it under the repository and run again`, exit 2 — so a
  public-kit manifest can never carry a workstation absolute path for the
  source. The same class, for `ears`' console capture: a kept `CONSOLE`
  line has the source's own directory replaced with `<source>`, and any
  line that still matches a drive-letter or `/Users/`/`/home/` pattern
  after that is withheld outright.
- **Model drift on the catalog:** the fixture with its four known yes-rows
  is the calibration instrument, available on demand via `look --fixture`,
  and `--selftest` section I judges a reader's answers against it rather
  than comparing a constant to itself.
