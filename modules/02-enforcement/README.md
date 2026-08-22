# Module 02 — Enforcement

The layer that makes a rule fire instead of merely being written down.

## Files

| File | What it is |
|---|---|
| `hook_model_gate.py` | A PreToolUse gate with four enforcement points: model tier on workflow `agent()` calls, model tier on agent spawns (plus a ban on naming the orchestrator tier), blanket-staging denial (`git add`/`stage` with `-A`, `-u`, `.`, `:/`, `*`, `git commit -a`, behind `git -C`, or indented in a block), and an optional protected-path tripwire with cert-green pre-authorisation. Three of the four are string heuristics with both error directions disclosed in the source. **Reads everything from `kit.config`; needs no editing.** |
| `hook_fixtures.py` | The harness that judges the gate. Synthesised stdin payloads, an "is it armed?" settings check, the dead-man clause, and `--make-deadman` so you can prove the clause fires before you trust it. |
| `settings.json.template` | The harness wiring: `permissions.ask` for the protected path, one hook file at three PreToolUse matcher blocks (seven tool names), and the status-line command. Valid JSON with the slots inside strings, so `--armed` works on it unsubstituted. |

## Adopt it — the commands, in a working order

Run these from your own repository root. They are ordered so each one can run
when you reach it: the directories exist before the copies, and the config is
in place before anything reads it. One directory per `mkdir` line — `mkdir -p
a b` is a positional-parameter error in pwsh.

```bash
mkdir -p tools
mkdir -p .claude
cp /path/to/kit/modules/02-enforcement/hook_model_gate.py tools/
cp /path/to/kit/modules/02-enforcement/hook_fixtures.py   tools/
cp /path/to/kit/kit.config.example                        kit.config
# then fill four keys in kit.config: PROJECT_NAME, LANE_TIER, SWEEP_TIER and
# FORBIDDEN_SPAWN_TIER (usually the same value as your orchestrator tier)
# now substitute the slots in the kit's
#   modules/02-enforcement/settings.json.template
# into .claude/settings.json
# ... and DELETE the permissions.ask block unless you are enabling the
# protected-path tripwire: left in with the shipped defaults it lands
# Edit(NONE/**)/Write(NONE/**) as live harness rules. The proof command
# below is green either way, so it will not catch this for you.
python tools/hook_fixtures.py --strict --armed .claude/settings.json
```

**Copy the config AND fill those four keys.** Skipping either step fails
silently. The kit reads placeholder-shaped values (`your-top-tier-model`) as
UNSET on purpose, so keys left at their shipped example values behave like
missing keys. `FORBIDDEN_SPAWN_TIER` is the one people skip because it looks
like a duplicate of the orchestrator tier; skip it and the rule it names is
simply not enforced, while the non-strict run still exits 0. Without a config
the hook still runs and still denies undeclared spawns — but
`FORBIDDEN_SPAWN_TIER`, `MODEL_EXEMPT_TYPES` and the protected path *do not
exist*, and the fixtures that cover them downgrade to `SKIP`. `--strict` fails
on that, and the run prints `CONFIG WARNING:`.

Then, before you believe any of it:

```bash
python tools/hook_fixtures.py --make-deadman <scratch-dir>
python tools/hook_fixtures.py --hook <scratch-dir>/hook_model_gate.py   # must go RED
```

`<scratch-dir>` is any writable directory: `/tmp/dead` on Unix,
`$env:TEMP/dead` in pwsh. `--make-deadman` creates it.

And judge the harness itself:

```bash
python tools/hook_fixtures.py --selftest
```

A gate that has never been seen red is unproven — that is this module's
doctrine in one line. The corpse-hook facility exists so proving it costs
thirty seconds instead of an afternoon.

## THREE of the four points are HEURISTICS, and here is what defeats each

Point 2 — the tier declared on an agent spawn — is exact: it reads a structured
field out of the tool input. Points 1, 3 and 4 are string matchers over text a
human wrote, and each of them has both error directions written into its own
source. This section is the summary; the source is the authority.

**Point 1 — counting `agent(` against `model:`.** The scanner blanks comment
text and string-literal *contents* in one pass, then counts. One pass rather
than two, because comments and literals hide each other's delimiters: masking
strings first would make `// don't` open a literal at the apostrophe and blank
the rest of the file. What still defeats it:

- a `model:` in a data structure that is not a spawn argument counts as a
  declaration → a **false allow** for one undeclared `agent(` (silent);
- a JS regex literal with escaped slashes (`/https:\/\//`) reads as a `//`
  comment and blanks the rest of its line; `#` outside a string does the same
  → a **false deny** (loud, immediate, fixable).

Comments are blanked because the un-blanked version had a much easier defeat:
one commented-out `model:` anywhere in a file satisfied the rule for an
entirely different, undeclared call. Trading a rare loud error for a trivial
silent one is the right direction. **The real answer is a parser.** If your
workflow scripts are complex enough for this to matter, lint them with
something that has an AST and let this gate keep the floor.

**Point 3 — blanket staging.** It denies `git add` and `git stage` carrying
`-A`, `--all` (or any unambiguous prefix of it, so `--al` and `--a` too), `-u`,
`--update`, a combined short-flag cluster containing `A` or `u`, `.`, `./`,
`:/`, `*`, or `:(top)` — quoted or bare; `git commit` with an `a`-bearing flag
cluster; all of those behind git's global options (`git -C <path> add -A`),
behind an assignment or wrapper prefix (`FOO=1`, `env`, `sudo`, `time`,
`nohup`), inside `$( … )`, and indented inside a block, which is where one
leading space used to defeat the whole rule. `git add --dry-run` is
deliberately **not** denied: it stages nothing, and it is the command an
operator reaches for after a deny.

**No completeness is claimed.** That covered list grew twice in one week —
three independent persona reads found one set, and a fourth read found ten
more forms in a single session after them. What still defeats it, all measured:

- a nested shell (`sh -c 'git add -A'`, `bash -lc "…"`), a backslash line
  continuation, backtick command substitution, `xargs git add`, a shell alias,
  a command built at runtime (`V=git; $V add -A`), a blanket flag placed after
  a quoted argument (`git commit -m "x" -a`), or any script the command merely
  invokes → **false allow, and it is SILENT**: the gate says nothing and the
  files are staged. Backticks are excluded deliberately — a backtick code span
  inside a commit message is far more common than the legacy substitution form,
  and matching it would deny ordinary prose.
- an indented occurrence inside a heredoc or a multi-line commit message →
  **false deny** (loud, immediate, fixable). Taken deliberately: the indented
  form is too common in real shell blocks to leave uncovered.

The scan never leaves the line it started on. An earlier version of the widened
pattern used `\s` between tokens, `\s` matches newline, and five ordinary
two-line blocks were measured denying — `git commit -F msg.txt` followed by
`ls -la` among them. Fixtures `ae`, `af` and `an` hold that line.

**The durable answer is to judge the index, not the string** — every bypass
above ends in the same index state — and a PreToolUse hook cannot do it,
because it runs *before* the command, when `git diff --cached` still describes
the world as it was. That judgement belongs in a git `pre-commit` hook. Until
you install one, the compensating pair is this pattern plus the sweep list the
gate prints when it denies (read from `git status --porcelain` at that moment),
and `python tools/kit_doctor.py`, whose dirty-paths check names the same files
on demand. Neither stages anything.

**Point 4 — the protected path.** A substring match on a normalised string.
Backslashes are folded; nothing else is. What defeats it silently: a
differently-cased spelling on a case-insensitive filesystem (Windows, and macOS
by default), a `cd` followed by a relative path, and a symlink or junction into
the location — all **false allow**. Case is deliberately *not* folded, because
on Linux the two spellings are genuinely different files and a tripwire that
asks about a path the owner did not protect is the false positive that gets
gates deleted. The other direction is **false ask**, which is loud and resolves
toward the human: a substring match also fires on a longer path that merely
contains the configured one (`/build` asks about `/buildings/`), and on any
command that mentions the path in prose. `python tools/kit_doctor.py` probes
the filesystem you are on and says what the case mismatch costs there.

**None of the four is a security control.** They are Zone B: useful friction,
honestly labeled, running with the same privileges as the thing they govern,
from a file that thing can edit. See `Security scope` in the kit README.

## The two claims, and why the first one is the one people miss

Fixtures prove what the hook **decides**. They say nothing about whether the
harness ever **calls** it. A settings file whose matchers were deleted or
rewired leaves every fixture green and every rule unenforced — the exact shape
of a gate that has silently stopped guarding. `--armed` parses the settings
read-only and asserts the hook is referenced for Workflow, Agent, Bash and
Edit.

It is deliberately loose about shape and strict about presence: harnesses
differ in how hooks are declared, so a schema assertion here would rot, but
"the string naming this hook appears under a matcher covering the tools it
governs" will not.

## The dead-man clause

Silence is a real verdict from this hook — *"I have no opinion, let the
permission system decide"* — which creates the failure mode the clause closes:

- a fixture expecting a **decision** passes when the decision is *delivered*,
  whatever the process wrote to stderr (a hook that prints a deprecation
  warning and then correctly denies has guarded; failing it would be a false
  red, and false reds are how a suite gets ignored);
- a fixture expecting **silence** passes only if the process also exited 0.
  Silence from a corpse is not consent.

## Where the config comes from — four steps, and the loud failure

Both tools search in **exactly** this order. Exactness matters: a harness
whose config search differs from the gate it is testing can load a config the
gate would never see, and is then measuring a different program. One list,
both tools:

1. `$KIT_CONFIG`
2. `./kit.config` — the current working directory
3. `<the tool's own directory>/kit.config`
4. **the nearest `kit.config` walking UP** from the tool's directory

Step 4 is what lets `<repo>/tools/hook_model_gate.py` find `<repo>/kit.config`,
which is the layout QUICKSTART produces. Whatever is found is then overlaid
with **`kit.config.local`** from the same directory:

| File | Committed? | Holds |
|---|---|---|
| `kit.config` | **yes** | repo-relative, shareable values |
| `kit.config.local` | **no** (gitignored) | absolute paths, the protected location |

The split resolves a real contradiction. The config must travel with the repo,
because a rule the hook cannot find does not fail — it silently stops
existing. But a config carrying one machine's absolute paths is wrong for
everyone else who clones, and publishes a small map of your infrastructure
besides.

**When no config is found**, `hook_fixtures.py` prints `CONFIG WARNING:` lines
and `--strict` fails. Without that warning, a config-less run prints greens
plus skips and reads as success while the forbidden-tier rule, the exempt
types and the protected path do not exist at all — the skips carry the whole
story. This failure was found by adopting the kit into a scratch project.

## Conditional fixtures

Four fixtures only mean something once `kit.config` configures the feature
they test (exempt agent types, the forbidden tier, the protected path).
Unconfigured, they print `[SKIP]` with the reason and are counted separately —
never silently passed. `--strict` turns a skip into a failure; use it in CI
once your config is complete. Skipped-as-passed is the single easiest way to
build a suite that reports green about nothing.

## File contract with other modules

- **← 01-governance.** The rules document declares these rules in prose; this
  module fires them. They must agree on `{{MODEL_EXEMPT_TYPES}}`,
  `{{FORBIDDEN_SPAWN_TIER}}`, `{{PROTECTED_PATH}}` and `{{CERT_TOKEN_FILE}}` —
  all read from `kit.config` by the hook, all quoted by the prose.
- **→ 03-verification.** The verify runner **ships a `hooks` gate** that shells
  out to `hook_fixtures.py --strict --armed <settings>`, so certification
  includes "the enforcement layer is armed, alive, and decides correctly". Its
  required line carries three counts — `HOOK FIXTURES: N/N passed, S skipped,
  A n/a` — with a floor on N, a ceiling of 0 on S, and A left free (the
  two-count form without `n/a` no longer satisfies the pattern; the runner's
  selftest asserts that). The full veto list is `UNARMED:` · `UNSTARTABLE:` ·
  `DEAD-MAN` · `HOOK NOT ARMED` · `CONFIG WARNING`. Point `HOOK_FIXTURES` and
  `HOOK_SETTINGS` at your copies, or `--skip hooks` if you did not adopt this
  module.
- **→ 05-statusboard.** `settings.json.template` carries the `statusLine`
  command. Delete that block if you skip module 05.
- **`kit.config` is the only coupling surface, and here is all of it** — the
  hook reads nine keys, in six rows (three rows carry two keys each):

  | Key | What the hook does with it |
  |---|---|
  | `MODEL_EXEMPT_TYPES` | agent types allowed to spawn with no tier |
  | `FORBIDDEN_SPAWN_TIER` | the tier no spawn may request by name |
  | `LANE_TIER`, `SWEEP_TIER` | rendered **into the deny message** as the tiers to use instead |
  | `PROTECTED_PATH_ENABLED`, `PROTECTED_PATH` | the tripwire, and what it guards |
  | `PROJECT_ROOT`, `CERT_PATHS` | how cert-green is evaluated — without both, pre-authorisation can never fire, and the harness says so |
  | `CERT_TOKEN_FILE` | where the token lives |

  **The cert-green token is a CONVENIENCE, not an authorization.** It is an
  ordinary unsigned JSON file, so anything that can write a file can mint one,
  including the agents the tripwire governs. There is deliberately no
  signature: an HMAC needs a key, and where the agent runs shell commands as
  the owner there is nowhere to put a key the agent cannot read, so a signature
  would raise forgery from "write a file" to "read a file, then write a file"
  while making the token read as an attestation it is not. What the token
  genuinely buys is that a certified, unchanged tree stops prompting the owner
  over and over for touches already approved in general. Mint it with
  `python <your verify runner> --mint-cert-token`, which writes it only from
  the runner's single `PASS` return; the honest label ships inside the file.

  **`NONE` and empty both mean UNSET**, in the hook and in the harness alike.
  A placeholder that behaves like a value is worse than a missing key: with
  `PROTECTED_PATH = NONE` treated as a value, the gate would substring-match
  the literal word and ask about `src/NONESUCH/`, and an unconfigured tripwire
  would produce a *fuller* green than a correctly-disabled one.

  No path, tier or protected location is hard-coded in the hook.

## What breaks if you adopt this module alone

Nothing breaks; the gate enforces the subset you have configured. With no
`kit.config` at all it still denies undeclared spawns, and still denies the
common forms of blanket staging — a heuristic that raises the cost of the
mistake rather than making it impossible, with its gaps listed above — which is
most of its day-to-day value.

**Be precise about the tripwire.** `PROTECTED_PATH_ENABLED=false` (or absent)
does not mean the tripwire "degrades to always ask" — it means the tripwire
**does not exist**: the hook never looks at a path, and nothing prompts.
"Always ask" is what happens one level in, when the tripwire IS enabled but
cert-green cannot be evaluated (no `PROJECT_ROOT`, no `CERT_PATHS`, no token,
or a dirty certified tree). That is the safe failure direction, and it is a
different state. Off and safe-when-uncertain are not the same thing, and a
document that blurs them teaches people that a feature they never switched on
is protecting them.

The fixture harness reports the difference explicitly:

| State | Fixtures l/m report | Counts as a gap? |
|---|---|---|
| tripwire enabled and configured | PASS/FAIL, verdict `ask` or `allow` | — |
| `PROTECTED_PATH_ENABLED = false` | **`n/a` (disabled by config)** | **no** — off on purpose |
| key absent, or enabled with no path | `SKIP` | **yes** — `--strict` fails |

## What this module gives you ALONE, and what it does not

**M-7.** Adopted on its own, module 02 gives you a live gate — undeclared
spawns denied exactly, the common forms of blanket staging denied
heuristically, an optional protected-path tripwire that is also a heuristic —
plus a fixture harness that can prove the gate decides correctly, is armed in
your settings, and is not a corpse. That is real, and for many projects it is the
single highest-value hour in the kit.

What it does **not** give you is any of that *at certification time*. Nothing
runs the fixtures unless you run them; nothing notices when someone edits the
hook; nothing invalidates a green because the config changed. Those are module
03's `hooks` and `judges` gates, and until you have them the honest
description of this module is **"a gate you must remember to test"** — not
"an enforcement layer".

Two cheap steps narrow the gap today: put
`python tools/hook_fixtures.py --strict --armed .claude/settings.json` in
whatever CI you already have, and re-run `--make-deadman` after any change to
the hook. Neither is as good as a gate you cannot forget.

## Honest scope: this is Zone B

The hook runs in the operator's own session, out of a file every implementer
in the repo can write. It is real — it fires, it blocks, it has caught
things — but it is enforced by the same hands it governs. An agent that edits
the hook has walked through it.

The Zone A controls (outside the agents' blast radius) are: a human at a gate,
server-side required checks on a protected branch, and code ownership on
judgment-bearing paths. Module 07 gets you the second one. Until then, the
honest minimum is what this module ships: fixtures inside your certification,
a dead-man clause, and a dirty-judge check at cert time (module 03's
`judge-paths-clean` gate) so an uncommitted edit to the hook invalidates the
run.

## Adaptation notes

- **Different harness?** The decision protocol is a JSON object on stdout with
  a `permissionDecision`. If yours differs, change `out()` — one function —
  and the fixture judge's parse in `judge()`. Everything else is
  harness-agnostic.
- **No workflow scripts?** Delete point 1; keep the Agent branch.
- **Adding a rule?** Add its fixture in the same commit. A rule without a
  fixture is a rule you will one day discover was broken, with no way to say
  when it broke.
- **The anchored `git add` pattern is load-bearing.** An unanchored version
  fires on prose that merely mentions the banned form — the reference gate
  blocked its own documentation minutes after birth. Precision matters as much
  as loudness: an alarm the operator learns to skim is a dead alarm.
