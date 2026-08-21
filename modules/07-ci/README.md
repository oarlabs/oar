# Module 07 — CI

The first judgement in the system that no session can edit while it runs.

## Files

| File | What it is |
|---|---|
| `verify.yml.template` | A GitHub Actions workflow that runs the certification command on every push: checksum-pinned toolchain download, the runner's selftest before anything expensive, a warm-up dirty-tree diagnostic, artifact upload on failure, and a **contract step that asserts an exact exit code**. **UNPROVEN — see the note below.** |
| `BRANCH-PROTECTION.md` | What to enable, in value order; code ownership on judgment-bearing paths; the private-repo/paid-plan constraint with three honest dispositions; how to verify protection actually blocks; the CI-green trap. |

> **`verify.yml.template` has never been executed with real slots filled in.**
> It is modelled on a workflow that ran green in the reference build, but its
> toolchain URL, archive name, checksum and inner binary path are placeholders
> only an adopter can supply, so nothing here has been run end to end. Expect
> to debug your first push. Everything else executable in this kit is proven by
> a selftest or the adoption smoke; this file is the one exception, and
> `KNOWN-ISSUES.md` says so too.
>
> (The kit's *own* CI, `.github/workflows/kit-ci.yml`, is a different and much
> simpler file — it downloads nothing.)

## The three ideas worth stealing

### 1. Assert an exact exit code, not "not failure"

```yaml
verify exit : 3   (this job requires exactly 3)
```

Exit 0 from a subset run means the skip list silently emptied and something is
claiming a certification it cannot have. That is **news**, not success. A CI
contract that accepts "anything but red" cannot tell you when it stopped
testing — which is the failure mode CI is supposed to protect you from.

### 2. Verify the toolchain download against a published checksum

An unverified download is **a stranger's code deciding whether your tree is
green**. Check the archive before unpacking, stop the job on a mismatch (never
warn), and put the checksum *in the cache key* so repinning misses the cache
instead of letting a stale toolchain outlive its pin.

### 3. Run the runner's own selftest before anything expensive

A runner whose judges are broken cannot tell you anything about your project,
and it will take forty minutes to not tell you.

## Adopt it

1. Substitute the slots; fill in the real binary path inside the archive.
2. Replace the skip-list comment block with your real gates and **a distinct
   reason for each**. Collapsing them into "not supported yet" loses the only
   useful information — which of them can ever be lifted.
3. **If you adopted module 02, put `hooks` on that skip list.** A hosted runner
   is a second machine: the committed `.claude/settings.json` carries the
   absolute paths of the machine that wrote it, so `--armed` reports
   `UNSTARTABLE:` there, that token vetoes the gate, and CI goes red on every
   push. Skip it in the CI invocation only, with `{{CI_EXPECTED_EXIT}}` at 3.
   A permanently skipped gate reports PARTIAL and **certifies less** — it never
   says the enforcement layer is armed — so keep it in your local `RUN_ORDER`.
4. Push. Read the whole log once, deliberately, including the contract step.
5. Then read `BRANCH-PROTECTION.md` and decide, on the record, whether you have
   a gate or a tripwire.

## File contract with other modules

- **← 03-verification.** The workflow runs `{{GATE_COMMAND}}` and asserts
  `{{CI_EXPECTED_EXIT}}`. The `--skip` list and that code must agree: skip
  anything and the expected code is 3, skip nothing and it is 0.
- **→ 04-ledgers.** CI belongs in `FAILURE-FLOOR.md` as a **Zone A** row — the
  only one most projects will have for a while — with its status recorded
  honestly as tripwire or gate.
- **`kit.config`** supplies the runner OS, timeout, skip list, expected exit,
  and the toolchain URL/archive/checksum.

## What breaks if you adopt this module alone

Nothing, and it is also nearly useless alone: the workflow runs a certification
command, so without module 03 (or an equivalent one-command runner of your own)
there is nothing for it to run. Adopt 03 first, always.

## Adaptation notes

- **Not GitHub Actions?** The structure ports directly: pin and verify the
  toolchain, selftest the judges, run the gates capturing the exit code as
  *data*, upload artefacts unconditionally, then assert the exact code in a
  separate step. The separation of "run" from "judge the run" is what lets a red
  run still produce its evidence.
- **Self-hosted runners** can host more gates — screens, devices, longer
  timeouts — but they move CI back toward the blast radius. Say which in the
  ledger; a self-hosted runner that agents can reach is not Zone A.
- **Do not let CI become the certification bar** if it runs a subset. The local
  full run is the bar. The PARTIAL verdict exists to keep that distinction
  visible in a single character, and the moment people start saying "CI is
  green" to mean "it is certified", the distinction has already been lost.
