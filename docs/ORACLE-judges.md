# ORACLE — judges

**What this gate catches, in one paragraph.** `judges` is a computed gate: it
asks git, not a subprocess, whether every file in `JUDGE_PATHS`/`CERT_PATHS`
is committed and clean. Certification is a property of a TREE, not of a
commit — if a judged file (a hook, the verify runner, `.claude/settings.json`,
`kit.config` itself) differs from HEAD, every other gate below it would be
enforcing rules that exist only in one working copy, so this gate runs first
and, on red, stops the other five from running at all.

**What it looked like red, observed in this worktree.** While this lane's
item 1 edit to `kit.config` (a `JUDGE_PATHS` entry itself) was uncommitted,
`python modules/03-verification/verify.py --only judges` printed:

```
RED   judges judges 1 dirty, tree clean  (0.0s)
line: judge-paths 1 dirty; cert-paths clean
THE JUDGE SURFACE is NOT COMMITTED. Certification is a property of a TREE, not of a commit: these files change what the gates mean, and they exist only in this working copy.
      M kit.config
```

Observed 2026-09-16. Restore: nothing to revert by hand — the edit is the
lane's own item 1 change, folded into this lane's single commit, at which
point `judges` reads green again because the judged surface is committed.

**Lineage.** Nearest named ancestor in the kit's own §12 Lineage table
(`BLUEPRINT.md`): "Certification is a property of a tree, proven by a cold
clone" — software supply-chain provenance (SLSA, in-toto), fetched
`https://slsa.dev/spec/v1.0/distributing-provenance`. This gate is the
narrower, git-status form of the same claim: a tree whose judge surface is
dirty attests nothing, the same way a build not taken from a cold clone
attests nothing.

**Residual.** `judges` proves the judge surface is *committed*, not that it
is *correct* — a bad rule that is checked in passes this gate exactly the way
a good one does. It also cannot see a judged path excluded by `.gitignore`
(that is `doctor:judge-paths-ignored`'s question, a separate check).
