# Branch protection — the first control your agents cannot edit

Everything else in this kit runs **inside the blast radius**. Hooks, gates,
charters, ledgers, the standing rules — all of them live in files that every
agent in the repository can write. They are real controls: they fire, they
block, they have caught things. They are simply enforced by the same hands they
govern.

CI on a protected branch is different in kind. The runner is somebody else's
machine, executing a workflow definition the push is *judged by*, not
*authored by* in the moment. That is the bright line, and it is worth crossing
as early as your project can afford.

## The honest distinction: tripwire versus gate

| | **Tripwire** | **Gate** |
|---|---|---|
| What it is | CI runs on push and reports red | A **required status check** on a protected branch |
| What it stops | Nothing | The merge |
| What it gives you | A loud, unignorable, session-external signal | Actual prevention |
| Cost | A workflow file | Branch protection, and possibly a paid plan |

**A red tripwire arrives after the push has already landed.** That is still
enormously valuable — it is the only judgement in the system that no session
can talk itself out of — but calling it a gate is the kind of overstatement
this kit exists to prevent. Write down which one you have.

## What to enable, in order of value

1. **Require the `verify` status check to pass before merging.** This is the
   whole point. Everything else on this list is supporting structure.
2. **Require a pull request before merging.** Without it, protection is
   trivially bypassed by pushing straight to the branch.
3. **Dismiss stale approvals when new commits are pushed.** Otherwise "approved"
   describes a diff nobody is looking at any more.
4. **Require branches to be up to date before merging.** Closes the semantic
   merge conflict: two PRs each green alone, red together.
5. **Include administrators.** A rule you can personally bypass is a rule you
   will personally bypass, at 11pm, on the change that turns out to matter.
6. **Require review from a code owner on judgment-bearing paths** — see below.
7. **Block force pushes and deletions** on the protected branch.

## Code ownership on judgment-bearing paths (the highest-value item people skip)

The paths that decide *what green means* deserve stronger protection than the
paths that are *being judged*:

```
# CODEOWNERS - judgment-bearing paths
/tools/verify.py          @you
/tools/hook_*.py          @you
/.github/workflows/       @you
/tests/fixtures/          @you
/kit.config               @you
```

**A hook can never protect itself** — the process can rewrite the hook before it
next runs. Code ownership is the control that stops an agent authoring its own
judge, and it is the one Zone A control that costs nothing but configuration.

The same list should be your verify runner's `JUDGE_PATHS`, so an uncommitted
edit to any of them also invalidates a local certification. Two different
mechanisms, one list.

## The private-repository constraint (be honest about it)

On several hosts, branch protection on a **private** repository requires a paid
plan. On GitHub specifically, protected branches on private repos need Pro or
above; rulesets have their own availability rules that change over time — check
current documentation rather than trusting this paragraph.

Three honest dispositions when you hit it, in preference order:

1. **Pay.** It is usually the price of a coffee per month, and it converts your
   only Zone A control from advisory to binding. If the project matters, this is
   not a real decision.
2. **Go public**, if the code can be public. Protection on public repositories
   is generally free.
3. **Run the tripwire and write down that it is a tripwire.** Put it in the
   failure-floor table, in the Zone column, with the residual named: *"reports
   red loudly; cannot block; a push lands before the red arrives."* Recording
   the gap is what stops it being forgotten and later described as a gate.

**Do not** simulate protection with a hook that refuses to push. That control
lives inside the blast radius, which is exactly what you were trying to escape,
and it produces the worst outcome available: the feeling of a gate without one.

## Verifying the protection actually works

Protection is configuration, and configuration drifts. Prove it once, then
re-prove it after any repository settings change:

1. Open a PR whose only change makes a gate red on purpose.
2. Confirm the merge button is **blocked**, not merely decorated with a red X.
3. Close the PR.

If the merge button is available, you have a tripwire. Say so in the ledger.

## The CI-green trap

A green tick on a PR is read by humans as "this is fine". If your CI runs a
subset — and it almost certainly does — then that tick means "every check that a
hosted runner can host is green", which is a much smaller claim.

Two defences, and you want both:

- Make the workflow **print the distinction in its own output**, every run, in
  the contract step. Anyone who clicks through sees it.
- Assert the **exact expected exit code**, so a silently-emptied skip list fails
  the job instead of quietly upgrading a partial run into a full one.
