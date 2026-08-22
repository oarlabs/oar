# Golden pytest suites — the fixtures behind `gate_line.py --selftest`

Six deliberately tiny pytest suites. Each one produces one of the six outcome
shapes a real suite can hand a gate, and `gate_line.py --capture-golden` runs
all six for real and writes what pytest actually reported into
`../pytest-golden.json`.

| Directory | What it produces | Why it is here |
|---|---|---|
| `all_pass/` | 3 passed | the ordinary green |
| `with_skips/` | 3 passed, 2 skipped | a legitimate skip set, and the ceiling that bounds it |
| `failures/` | 2 passed, 1 failed | the veto line for a failing test |
| `errors/` | 2 passed, 1 errored | setup errors are not failures and are counted apart |
| `collapsed/` | 0 collected | **the silent-green class.** A suite that stopped running |
| `subset/` | 2 selected of 4, via `-k` | the honesty suffix a partial run must carry |

These are fixtures, not examples to copy. The file to copy into your project is
`../../gate_line.py`; `../../GATE-LINE.md` says how.

Nothing outside `gate_line.py --selftest` and `--capture-golden` runs them, and
they are not part of any adopting project.
