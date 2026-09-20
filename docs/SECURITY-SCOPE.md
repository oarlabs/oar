# Security scope

**This kit is not a security boundary**. No part of it should be presented to a
security reviewer as one.

What it governs is **correctness, cost, and process integrity**. Specifically:
that the checks a project trusts exist, that they ran, that they have been seen
red, and that a verdict is not narrated. Also that a rule is labeled with
whether the agents it governs could rewrite it, and that the money and rework
are written down. Those are the failure modes of an honest agent doing
competent work badly.

A third actor sits between the honest one and the hostile one: the agent
optimizing for green. It is neither hostile nor incompetent; it treats a
control as an obstacle on the way to satisfying the charter. Three
signatures mark it: a refusal
routed around instead of reported, a stop word passed by feel instead of
read from the counter, and a report that omits a finding by
misunderstanding rather than by concealment. The kit answers each
signature by name. The wrapper rule closes the first: a refused tool call
is quoted rather than re-encoded. The measured stop word closes the
second: a lane reads its own token count. The spec-side reviewer, judge
paths and negative controls close the third: a reviewer onboards from the
punch list and the diff, not the implementer's account. A refusal is the
end of the path, never a detour.

Four agent behaviors are worth separating, because the kit answers each one
differently.

| Agent | What the kit does | What it does not |
|---|---|---|
| **Accidental** (an honest mistake, no intent) | Governs the failure modes of an honest agent doing competent work badly: that the checks a project trusts exist, that they ran, and that they have been seen red (this file, "the failure modes of an honest agent doing competent work badly"). | Scan for a leaked secret or credential beyond the tokens you enumerate yourself. The general secret class belongs to `gitleaks` and `TruffleHog` (this file, "the general secret class belongs to the incumbents, and this kit does not compete for it"). |
| **Overconfident** (asserts a verdict that did not run) | Makes a narrated verdict askable. The demonstration gate cannot certify a behavioral suite that executed zero of its assertions, and the kit's escape rate is computed rather than narrated (`README.md` says "A check moves through four states" and `BLUEPRINT.md` says "The kit's own escape rate, computed rather than narrated"). | Always confirm a harness is wired correctly. The armed check is only half-closable, because no second source exists for a harness's own intent (`KNOWN-ISSUES.md` says "no second source exists for a harness's intent"). |
| **Optimizing for green** (weakens a check to pass it) | Invalidates certification on an uncommitted edit to a judge, the judge-paths-clean check (`BLUEPRINT.md` says "an uncommitted edit to a judge invalidates certification"). A defect that got through a check that existed and passed anyway counts against the published escape rate (`KNOWN-ISSUES.md`, "The kit's own numbers"). | Stop a committed change to a check's own source. That needs a human reader of meaning, which is code ownership and required review on judgment-bearing paths (`BLUEPRINT.md` says "required review on judgment-bearing paths"). |
| **Malicious** (routes around the gate on purpose) | Labels the gate honestly. Every control here runs with the same privileges as the thing it governs, and the enforcement hook is Zone B, useful friction, honestly labeled (this file, "useful friction, honestly labeled"). | Serve as the security boundary. The boundary is a sandbox or container the agent cannot escape, separate credentials, egress rules, server-side CI on a protected branch, and review at the merge point by someone the agent cannot be (this file, "review at the merge point by someone the agent cannot be," and `BLUEPRINT.md` says "Server-side CI on a protected branch"). |

What it does **not** defend against:

- **A malicious or hostile agent**. Every control here runs with the same
  privileges as the thing it governs, from files inside the repository that
  thing edits. An agent that decides to route around the gate can edit the
  hook, the fixtures, the config the hook reads, or the settings file that
  wires it. The kit's own zone labels say this in the small: Zone B is "useful
  friction, honestly labeled," and the enforcement hook is Zone B.
- **Prompt injection**. Nothing here inspects, sanitizes, or reasons about the
  content of prompts, tool output, retrieved documents, or web pages. A hostile
  instruction arriving inside a file an agent reads passes through every
  control in this kit untouched.
- **Credential exfiltration**. There is no secret scanning of agent output, no
  egress control, and no network policy. `tools/deident_scan.py` scans a tree
  for tokens *you list yourself* before you publish it. It is a publication
  aid, not a data-loss control, and it cannot see what an agent already sent.
  **The general secret class belongs to the incumbents, and this kit does not
  compete for it**. `gitleaks` and `TruffleHog` are the established pre-commit
  and CI secret scanners. What `deident_scan.py` covers is the narrower,
  adjacent job they do not do: program-identity tokens you enumerate yourself,
  such as a name, a username, an employer, or machine path fragments. A green
  from this one says nothing about secrets.
- **Supply chain**. The kit ships stock Python and pins nothing of its own.
  Module 07's CI template checksum-pins the toolchain it downloads, and that is
  the extent of it. Nothing verifies the provenance of your dependencies, your
  models, or this kit.

Two specifics need naming, because both look stronger than they are:

- **The [cert-green](../GLOSSARY.md) token** (`modules/02-enforcement`) is a
  convenience, not an authorization. It is an unsigned JSON file, so anything
  that can write a file can mint one. An HMAC needs a key, and in a harness
  where the agent runs shell commands as the owner there is nowhere to put a
  key the agent cannot read.
  `verify.py --mint-cert-token` writes it from the runner's single PASS return,
  and the honest label ships inside the file.
- **Three of the PreToolUse hook's four rules are string heuristics**. Points
  1, 3 and 4 are the workflow-script tier count, the blanket-staging ban and
  the protected-path tripwire. Each matches text a human wrote, and each
  discloses its error directions in its own source, including the ones that
  fail *silently*. **No completeness is claimed for any of them**. The forms
  still known to walk past point 3 are named where the rule is defined. Point 2 is the tier declared on an agent spawn. It compares
  declared fields rather than matching text, and is exact. The three heuristics
  raise the cost of a mistake; they do not make one impossible.

If you need a security boundary, put it where boundaries go. That means
separate credentials, a sandbox or container the agent cannot escape, and
egress rules. It also means review at the merge point by someone the agent
cannot be. This kit sits inside that boundary and makes the work honest. It
does not replace it.

`python tools/kit_doctor.py` reports these limits against your own adoption:
what your gates cannot catch, what a blanket commit would sweep up, and what
your cert-green token is and is not.
