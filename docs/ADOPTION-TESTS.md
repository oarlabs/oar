# Adoption-test status

Relocated from `README.md` in round 30, intact.

---

Partial-adoption tests have been run against three modules by LLM personas.
`KNOWN-ISSUES.md` is the authority; this table is a summary of it.

| Walked alone | Result as shipped | Now |
|---|---|---|
| module 05 | TRUE | unchanged |
| module 03 | **FALSE** — 3 findings, 1 silent | fixed, and re-walked clean by the release audit |
| module 02 | **FALSE** — its own README's adoption recipe did not run as written | **TRUE** — the release walk confirmed the recipe produces a working harness file; its proof command is green once the recipe's fill list is followed: `HOOK FIXTURES: 38/38 passed, 0 skipped, 2 n/a`, exit 0 *[the walk measured `15/15` on 2026-08-20. Twenty-one fixtures landed in round #17 — the measured blanket-staging bypasses, the false-deny class the widening created, and the string-literal defects — and the count moved; the number here is this kit's own run of the same command against the same filled key list, not a re-walk. The `0 skipped` and the exit code are what the walk was proving.]* |

The pattern in both failures: the contracts held; the adoption instructions
did not. "Separately adoptable" is a claim about documentation as much as
about code, and only someone else's hands can check the documentation half.
The hands that checked it here belonged to an LLM persona following a written
charter, which is a weaker instrument than a person and is labelled as one.
The unqualified claim returns when a re-test passes, not when the fixes land.
