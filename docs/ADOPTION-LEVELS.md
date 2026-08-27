# Three adoption levels

## Level 1 — documents only (30–45 minutes) — the path is `LEVEL-1.md`

Take **04-ledgers** and **08-collaboration**. Run the seed interview, or
schedule it when the owner is someone else. Start the four ledgers empty. Add
**01-governance** as prose if you have agents.

`LEVEL-1.md` walks it step by step and ends in a check you can run.
`kit_doctor.py --level1` reads the documents you installed. It prints what it
certifies, what it does **not** certify, and what removing the level costs.

No harness assumptions, and **no code installed into your repository**. The two
tools that path uses run from the kit clone against your repo. This level
changes what your project records about itself, which is most of the value, and
it is the reversible one. Start here unless you have a specific reason not to.

## Level 2 — partial (a day)

Add **03-verification**: one command, one exit code, real floors, and a real
[negative control](../GLOSSARY.md). Add **02-enforcement** after a governance
rule has failed at least once. The failure tells you which rule to promote
first. Promoting rules that have never failed grows the rule set until people
route around it.

## Level 3 — full (a week, mostly spent on your own gates)

Add **07-ci** for the first control outside the blast radius, then **05** and
**06** for ambient state and bounded detours. Spend the remaining time writing
the gates specific to your project. The kit provides the frame; the checks are
yours.
