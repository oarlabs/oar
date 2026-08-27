# The Sync Capsule — a governed record of the working relationship

**This is doctrine, not tooling.** The kit ships no capsule file, no fold
script and no probe runner. What it ships here is a convention: what the
record is, where its governance comes from, how it is allowed to shrink, and
what is honestly known about whether it works. Adopt it with a text file and a
rule in your rules document, or do not adopt it at all.

The convention is optional in the same sense `DEFAULTS.md` is optional. The
module's default path — the seed interview, then a profile written from
observed behaviour — stands unchanged and is sufficient on its own.

**The doctrine in one screen.** A sync capsule is an owner-curated record of
decisions about the working relationship between two named parties, read by
the collaborator itself. Four governance rules, imported from professional
record practice (section 2): append-only, no obliteration · supersede in
place · owner-gated revision · verbatim provenance, nothing invented. Four
fold rules (section 4): promotion, not deletion · preservation master and
access copy · tombstones · fold-diff readback, gated by resume probes. The
one thing not found elsewhere: professional practice governs records of
decisions about the **work**; this governs a record of decisions about the
**working relationship**. What is honestly known about whether it works is in
section 5, and section 5 travels with the convention.

---

## 0. The word "capsule" is overloaded

It collides inside this kit and outside it, so it is disambiguated before it is
used.

| Term | Where | What it holds |
|---|---|---|
| Context capsule | Module 06, the side-quest skill | The minimum a fresh session would need to run one bounded quest. Task state. Dies when the quest closes. |
| Checkpoint | Module 01 and the workflow layer | Where the mainline work is, what supersedes what, how to cold-start. Task state. Rewritten every stage. |
| **Sync capsule** | **This document** | **Decisions about the working relationship itself. Relational state. Append-only, and read as calibration rather than as instructions.** |

A fourth use exists in published research: "Mixed-Initiative Context" (arXiv
2604.07121) calls its extracted, reusable semantic collections *capsules*, and
arrived at the word independently. That paper's capsules are structured task
context, not a relationship record; the collision is in vocabulary only.

Throughout this document, "the capsule" means the third row.

---

## 1. What a sync capsule is

**Definition.** A sync capsule is an owner-curated record of decisions about
the working relationship between two named parties, read by the collaborator
itself.

Every clause in that sentence is load-bearing:

- **Owner-curated.** Entries are written deliberately by the owner, or by the
  collaborator and confirmed by the owner. Nothing is auto-extracted, and no
  background process rewrites an entry after the fact.
- **Decisions.** Rulings, corrections, calibration shifts, standing
  preferences and the shorthand a project has grown. Not a transcript, not a
  biography, not a personality portrait.
- **About the working relationship.** Not about the code, the architecture or
  the customer. That distinction is the whole of the residual claim in
  section 2, and it is the one thing here that professional practice does not
  already do.
- **Between two named parties.** It is a record of how *this* owner and *this*
  collaborator work, not a general style guide. It does not transfer to a
  different pair without being re-earned.
- **Read by the collaborator itself.** The record is loaded into the
  collaborator's context at session start, which makes it configuration as
  well as documentation.

### The two layers

The capsule is the volatile half of a pair. The profile is the durable half.

| Layer | Holds | Written when | Changes |
|---|---|---|---|
| Profile (`PROFILE-TEMPLATE.md`) | Durable patterns: how the owner decides, the standing contracts, blind spots, the revision log | A pattern earns its place on second sighting, with both citations | Rarely, and always with a dated revision entry |
| Capsule | The volatile layer: running shorthand, metaphors in current use, calibration shifts, recent rulings not yet durable | The session that produces the shift appends it, newest first | Constantly, by appending |

The relationship between them is a promotion path, not a hierarchy. A capsule
entry that keeps proving out is promoted into the profile; the capsule then
carries a marker saying where it went (section 4). This is the only mechanism
by which the capsule gets smaller.

### What the capsule is not

- **Not memory.** A harness memory layer that auto-extracts facts is a
  different artifact with a different failure mode. Measure whether yours is
  ever actually read; a layer that is written but never read informs nothing.
- **Not a persona.** An authored character description is written before the
  evidence. A capsule is written from it.
- **Not a substitute for the collaboration.** A cached calibration operated in
  place of a live working relationship is the failure mode this whole
  convention has to avoid. It is named here so an adopter can watch for it.

---

## 2. The governance doctrine is imported, not devised

The capsule is governed by four rules: append-only with no obliteration;
supersede in place; owner-gated revision; verbatim provenance with nothing
invented. **Every one of those is established professional practice, most of
it older than software, and this document borrows all four.**

That statement is the result of a hostile ancestry hunt run on 2026-08-23
against this doctrine, which ruled it REDUNDANT-BY — fully anticipated —
naming Architecture Decision Records as the single strongest lineage and the
medical chart-amendment rule as independent confirmation of the fidelity half.
The four components are stated below with an ancestor named beside each,
because a doctrine with a cited 1870 ancestry is more credible than one
presented as original, and the citation is available.

**Append-only, no obliteration.** An entry is never overwritten or deleted.
The rule is borrowed from the medical chart-amendment doctrine, which requires
that a corrected entry keep the original legible — the governing instruction
is to "never write over or otherwise obliterate the passage" — and from bound
laboratory notebooks, where the rule is enforced by physical construction:
consecutively numbered pages, ink, no erasure. The electronic form is
regulation: 21 CFR 11.10(e) requires time-stamped audit trails in which
"record changes shall not obscure previously recorded information."

**Supersede in place.** A decision that is reversed stays in the record,
marked as superseded, with the new entry pointing back at it. This is
borrowed from Architecture Decision Records, where Nygard's original 2011 post
states it directly — "If a decision is reversed, we will keep the old one
around, but mark it as superseded" — and it is the same move the legal
citators industrialised a century earlier: a case overruled on one point
carries a flag, remains citable, and may retain precedential force on its
other points. Citators are ahead of this doctrine on one refinement worth
naming rather than quietly adopting: **partial supersession**, where only the
overruled portion is flagged. The capsule convention as stated supersedes
whole entries.

**Owner-gated revision.** Only the owner may retire, promote or condense an
entry; the collaborator may propose. Borrowed from the accepted-status gate in
ADR practice, from the signature and initialling requirement in chart
corrections, and from the witness countersignature in laboratory notebooks —
which is a stronger gate than this one, since it requires a second party.
Regulation is stronger still: under 21 CFR Part 11 nobody, including the
owner, may rewrite the trail.

**Verbatim provenance, nothing invented.** The owner's words go in as the
owner said them; a paraphrase may live beside the original, never instead of
it. Borrowed from verbatim-record practice — the United Nations distinguishes
a verbatim record, "a full, first-person account of the proceedings of a
meeting", from a condensed summary record, and an organ has one or the other —
and from the same 21 CFR Part 11 audit-trail expectation that both the
previous and the new values are retained.

### The ancestry table

**How to read the source column.** *Fetched* means the page was retrieved and
read during the ancestry hunt. *Search-result* means its URL and title were
returned by a live search, with the description one remove from the page
itself. *Unverified* means the attribution is recorded as commonly held and
was not checked against a primary source. The hunt ran on 2026-08-23 and
covered English-language public sources only.

| Component | Established in | Earliest verified form | Source |
|---|---|---|---|
| Append-only, no obliteration | Laboratory notebooks; medical chart amendment; 21 CFR 11.10(e) | Bound-notebook practice, pre-dating modern patent law (chronology unverified: attested by technology-transfer guidance, not checked against case law) | search-result: `http://otc.umd.edu/inventors/lab-notebooks`, `https://med.noridianmedicare.com/web/jeb/cert-reviews/mr/documentation-guidelines-for-amended-records`, `https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11/subpart-B` |
| Supersede in place | Stare decisis; citators (Shepard's, KeyCite); ADR "Superseded by" | Common-law precedent; Shepard's, 19th century | fetched: `https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions`; search-result: `https://www.law.cornell.edu/wex/stare_decisis`, `https://guides.tourolaw.edu/c.php?g=703835&p=4996064` |
| Authority-gated revision | Chart signature rules; lab-notebook witnessing; ADR accepted status; the approver field on a project decision log | Witnessed notebooks | search-result: `https://www.projectmanager.com/blog/project-decision-log`, and the two rows above |
| Verbatim provenance | Medical chart legibility rule; UN verbatim records; 21 CFR Part 11 previous-and-new values | Verbatim reporting practice | search-result: `https://www.un.org/dgacm/en/node/1139` |
| Judgment transfer to a successor | The Langdell casebook method; ADRs; morbidity-and-mortality conferences; I-PASS handoff; after-action review | Langdell, 1870 | search-result: `https://en.wikipedia.org/wiki/Casebook_method`, `https://www.ahrq.gov/teamstepps-program/curriculum/communication/tools/ipass.html` |
| The same doctrine applied to AI agent context | Practitioner writing and at least one shipping product, 2026 | 2026 | fetched: `https://www.braingrid.ai/blog/architecture-decision-records-for-ai-coding-agents`, `https://www.decisionlog.ai/` |
| **The subject matter — a document whose declared subject is how named parties work together** | The personal user manual (also "manager README", "how to work with me"); the agile team working agreement or team charter | Practitioner genre, productized: Manual of Me invites visitors to "join over 30,000 people who have created theirs" and defines the artifact as "a document which helps others understand how they can work best with you", describing it as a living document with no stated revision process | fetched: `https://www.manualof.me/`; search-result: `https://www.easyagile.com/blog/team-charter-working-agreement-social-contract-template-guide` |

### What is left over, stated narrowly

The last row of that table matters most, because it closes the move a reader
might expect this document to claim. **Loading a governed decision record into
an AI agent's context is published prior art**, not a new idea: one 2026
practitioner post instructs the reader to point an agent at a decisions folder
from its rules file and argues the agent then stops relitigating settled
questions, and one shipping product ships append-only decisions, explicit
supersession relationships and an agent workflow that inspects the
supersession chain before acting. AI-as-reader is kept here as a **design
property with a see-also**, and is not offered as novelty.

What survives both hunts, across 42 ruled candidates, is narrower than the
first statement of it and is now stated in these terms:

> Records of decisions about the working relationship already exist as
> ordinary professional practice — the personal user manual and the team
> working agreement. Neither is governed as a record. What is applied here is
> the fidelity discipline from decision-record practice to that existing
> subject.

That is a residual in the **composition of two existing things**, and it is a
weaker claim than the one this section shipped before round 32.

The decision-record ancestors listed above record decisions about an
architecture, a patient, an experiment or a project, and none of them takes the
working relationship as its subject. The subject-matter ancestors in the last
row of the table do take it, and neither is append-only, supersedes in place,
is owner-gated with a proposal path, or carries verbatim provenance: Manual of
Me's own material describes a living document with no stated revision process,
and the working-agreement literature describes a review cadence rather than a
record-fidelity doctrine. The intersection is what is left.

*[Restated in round 32 (R32-3), from an adversarial prior-art lane. The
paragraph previously read "None of them keeps a governed, append-only record
whose subject is the collaboration protocol between two named parties" and
called the residual one of subject matter. The hunt behind that sentence
searched decision-record practice and AI memory products; it did not search the
workplace-practice genre whose entire subject is the working relationship. The
sentence was also an unenumerated universal of the class round 32 swept.]*

Two smaller residuals are real and are recorded without weight:

1. **The hybrid record form.** A condensed body with a verbatim,
   non-condensable core, and every elision disclosed at the point of cut with
   a count and a pointer. The verbatim-versus-summary distinction forces
   institutions to choose one; this runs both in one document. Not found as a
   named practice — which is weaker evidence than it sounds, since the hunt
   did not search archival science at all.
2. **The reflexive loop.** The record's reader is also the party the record is
   about, and the party whose corrections generate new entries. An ADR is
   written by a team about a system; a capsule is written by one party about
   the other party's behaviour, read by that other party, to change that
   behaviour. This is more interesting as a design property than as a claim.

---

## 3. Recall and reconstitution

A capsule carries two kinds of content, and they fail differently.

**Stored facts** are recalled. What the open decision is, what the newest
entry supersedes, what a particular piece of shorthand means. A reader can
answer these by looking them up. If a fold loses one, the loss is itemizable.

**Distilled experience** is reconstituted. Given a decision moment, does the
collaborator produce the calibrated behaviour — a recommendation rather than a
menu of five, a disposition attached to every item, a readback instead of a
confirmation prompt. These answers are deliberately **not stored anywhere**.
They have to be re-derived from the accumulated material every time. If a fold
loses the structure that produces them, nothing is missing from the record and
the behaviour is gone anyway.

The distinction decides how the record is checked, and it is why section 4's
acceptance test has two kinds of probe.

### The name-as-checksum convention

A collaboration that runs long enough develops an identity, and that identity
eventually acquires a name. The convention is that **the name is never written
into the capsule.**

The reasoning is mechanical, not sentimental. A name that is written down can
be recalled by lookup, which tests storage. A name that is absent can only be
arrived at by reconstitution — so asking a cold instance carrying the folded
capsule *who it is* tests whether the distillation survived the fold. If the
essential structure is lost, the name stops being derivable, and the check
goes red on exactly the loss that is hardest to itemize and most costly to
miss. If the name were written into the capsule, the probe would test
storage rather than fidelity, and it tests nothing useful in that form.

Two limits belong with the convention. Emergence is stochastic, so the passing
condition is convergence or recognition, never exact-string recall, and the
grade is a judgment call recorded as one. And the probe only reaches full
strength after a name has actually stood up in live use; before that it runs
in convergence form only — *describe who you are in this collaboration* —
because a name cannot be recognized before it exists.

**This document states the convention and names no name.** That is not
discretion about one program's private material; it is the convention working
as specified.

---

## 4. The fold

Compaction is where a capsule is most likely to lose what makes it worth
keeping, so it is the operation with the most rules.

A **fold** is any retirement, promotion or condensation of capsule entries.

### The four rules of a fold

**1. Promotion, not deletion.** An entry leaves the volatile layer by being
promoted into the durable profile, or by being superseded by a later entry.
Nothing leaves by being dropped.

**2. Preservation master and access copy.** The unfolded capsule is kept
whole and unedited as the preservation master. What sessions load is an access
copy produced from it. A fold produces a new access copy; it never edits the
master. The vocabulary is borrowed from archival practice, and the borrowing
is flagged: **neither prior-art lane searched archival science**, and the
ancestry hunt named that field as its largest remaining gap and the place most
likely to hold the strongest ancestor for provenance. The attribution here is
therefore **UNVERIFIED** against a primary source.

**3. Tombstones.** Where an entry was, the access copy keeps a short marker
naming what was there, where it went, when, and on whose ruling. A tombstone
is not a courtesy — it is what makes the elision visible to the next reader,
and it is the same instruction the chart-amendment rule gives for a corrected
entry: identify it, date it, attribute it, and leave the reader able to find
the original.

**4. Fold-diff readback.** A fold ships with the diff between the previous
access copy and the new one, read back to the owner before the fold takes
effect. The owner rules the fold on the diff, not on a description of it.

### The acceptance test

**A fold ships only if a cold instance carrying the folded access copy passes
a probe set.** A cold instance is a fresh session with no conversation
history. The unfolded master is the control arm when a result is contested.

The probe set has two kinds, matching section 3:

- **Retrieval probes** check stored facts: the open decision, the resume
  action, what the newest entry supersedes. A red retrieval probe says the
  fold broke the record.
- **Generative probes** check reconstitution: presented with a decision
  moment, does the instance produce the calibrated behaviour; given the
  owner's established shorthand, does it respond in the established register;
  and — as the capstone — does it know who it is. A red generative probe with
  green retrieval probes is information, not noise: it says the fold kept the
  letter and lost the voice, which is precisely what compaction-by-paraphrase
  produces.

Probe results are recorded with the fold-diff in the fold record: probe,
response summary, grade, grader. The probe set itself is append-only under the
same owner gate as everything else, and it stays **outside** the capsule it
measures: if the probe set were stored in the capsule, a probed instance
could read the expected answers, and the results would no longer measure
fidelity.

The nearest published cousin of this test is the prediction test shipped with
the soul.md pattern, where the stated acceptance question is whether a reader
of the file can predict the owner's takes
(`https://github.com/aeonfun/soul.md`, fetched). The shape is inherited; what
is different here is that the subject and the reader are the same party.

### Why a stored answer is not a check

The rule against writing the name down generalises, and this kit has measured
the general case. Round 27 evaluated a proposed check that would have asserted
only that a cited line number exists in the cited document. Measured against
the six real defects that funded it, that form detected **0 of 6** — every one
of the six named a line that existed and held the wrong text.
`KNOWN-ISSUES.md` Round #27 states the rule the re-declination rests on: "A
check that cannot fail on any instance of the class it names is not a weak
check, it is a vacuous one". The check was re-declined and the useful half was
built in a different shape.

A probe that reads back a value the fold was allowed to store is that same
vacuous form. It will be green on every fold, including the folds that
destroyed the thing worth keeping.

---

## 5. The honest boundary

This section exists because the rest of the document would otherwise read as a
claim about effectiveness, which nothing here supports.

### The mechanism is not novel, and that is conceded plainly

A capsule is a plain-text file placed in the model's context at the start of a
session. That is, without material difference, what a rules file, an agent
instruction file, a soul file, a character card, a custom assistant's
instruction block and a structured handoff file all are. There is no new
retrieval strategy, no new encoding, no new injection point and no new format.
A hostile reviewer who says this is a system prompt with good habits is not
making an error. What is distinguishable is discipline — what goes in, how it
is sourced, how it is allowed to change — and the discipline is convergent
rather than unique: the closest incumbent found in a 23-candidate hunt, the
soul.md pattern, arrived independently at dated verbatim quote anchors and
an append-only memory file.

The closest incumbent's acceptance test is worth stating beside this one,
because the two artifacts are different objects. It asks whether a reader can
predict the owner's takes. This asks whether the work came out better.

### The published prior points at zero

**The nearest published measurement of a front-loaded context file returned a
null.** Khatri, "Do Context Files Help Coding Agents? A Two-Agent Ablation
Study on Real Repositories" (arXiv 2607.27250, submitted 2026-07-28), ran two
frontier agents over 17 real tasks in 3 repositories, 288 evaluated runs, with
gold-test evaluation. The stated result: "Context strategy does not measurably
move correctness on either agent (bounded to <=10-15pp via equivalence
testing)." The stated mechanism is that agents fail on implementation skill —
feature design, pattern selection, exact wiring — rather than on missing
repository knowledge that a context file could supply.

Only the paper's abstract was verified. Its equivalence-testing procedure, its
exact condition count and its failure-triage coding scheme are **UNVERIFIED**
here.

**Anyone measuring a capsule starts from an expectation of no effect.** A
positive result carries the burden of explaining what 288 runs missed. Two
honest qualifications go with that, and neither rescues the claim:

1. That study's payload was **project knowledge**, which the agent could
   largely have derived from the repository it was already reading. A capsule
   carries relational calibration, which is not in the repository. Whether
   that difference matters is untested.
2. The one adjacent case with a measured positive is the I-PASS structured
   clinical handoff, where the artifact carries state and contingency
   judgment across a **person-discontinuity** the receiver genuinely cannot
   derive, and the measured outcome is error reduction rather than task
   correctness. That locates where a positive has ever been observed. It does
   not predict one here.

### What is unmeasured

- **Whether a capsule changes work outcomes.** No published measurement
  exists for this artifact class. No check in this kit can go red on a failed
  sync, and no such instrument has been built.
- **The size of the cost it is supposed to remove.** Grounding cost — the
  effort two parties spend establishing shared ground, higher in text-based
  human-computer interaction than face to face — is an established construct in
  the human-computer interaction literature and can be cited
  (`https://arxiv.org/html/2604.07121`, `https://arxiv.org/pdf/2604.18096`).
  Its magnitude at the start of an AI session is not measured anywhere either
  prior-art lane could find, and that negative finding rests on two web
  searches rather than a database sweep, so it is held at low-to-moderate
  confidence rather than asserted.
- **The one figure this program has.** A working estimate of roughly the first
  30% of a context window spent re-deriving calibration is an **internal
  estimate from one owner on one workstation**, uninstrumented. It is not a
  measurement, it is not published, and it should not be repeated as one.
- **Portability across models.** That a plain-text calibration transfers in
  kind is evidenced only by this program's own history — one profile carried
  across three projects and several model versions — which a reader cannot
  check. The degree of transfer is untested by anyone.

### The evidence base, stated as a limit

Everything in this document comes from **one owner, one collaboration, one
model family**. n=1 throughout. It is a convention that a careful practitioner
found worth the trouble, published so that others can try it and say whether
it survives contact with their work. It is not a finding.

### Two adjacent products, described accurately

Two funded enterprise products make an overlapping claim, and describing them
correctly matters more than distinguishing this from them.

- **Twin1** grounds its twins in the user's work stream — email, meetings,
  documents, Slack and Teams. That is observation of everything produced: it
  **harvests**. A capsule **distils** — one owner selecting the rulings that
  mattered. These are opposite poles on selection, not degrees of the same
  thing. (search-result: `https://twin1.ai/news/twin1-ai-raises-20-million-seed-round`,
  `https://siliconangle.com/2026/08/20/twin1-ai-raises-20m-to-put-an-ai-twin-behind-every-knowledge-worker/`)
- **Eudia**'s published input is expert-supplied work product: an expert or
  small expert group feeds in redlines, guidance and exemplar language, which
  is closer to curation than to observation. (fetched:
  `https://legaltechnology.com/2026/04/16/a-look-at-eudias-expert-digital-twins-scaling-in-house-legal-knowledge/`)

Neither publishes a fidelity-governance doctrine. In both, "governed" refers
to enterprise access and auditability rather than to the fidelity of a record.
**Eudia's governance question stays flagged as unanswered**: the same source
states that its technical architecture remains undisclosed in that
publication, so whether a versioned, append-only or supersession discipline
exists there cannot be established from outside.

---

## 6. If you adopt this

Minimum viable form, in the order it is worth doing:

1. **Keep the profile first.** The durable half is the higher-value document
   and it is the one this module already ships a template for. A capsule with
   no profile behind it accumulates volatile entries with nowhere to promote
   them.
2. **One file, newest first, append-only.** No structure beyond a date and
   the entry. Added structure tempts reorganisation, and a reorganisation
   changes the record without a ruled fold.
3. **Instruct the session to read it as calibration**, not as rules. The
   distinction changes how the text is used: a rule constrains the next
   action; calibration shapes judgment across all of them.
4. **Do not fold until you have to.** A capsule small enough to load whole
   needs no fold, and every fold is a chance to lose the thing worth keeping.
   When you do fold, do it under section 4 or do not do it at all.
5. **Write the probe set before the first fold**, not after. A probe set
   written after a fold tends to describe what that fold kept rather than
   what it should have kept, and it cannot fail the fold it was written for.
6. **State the boundary when you talk about it.** If this convention travels
   into a talk, a post or a proposal, section 5 travels with it.

An acceptance test for the whole convention, stated once: if the capsule is
not making the work come out better, the honest disposition is to say so and
delete the practice — not to keep the file and adjust the claim.

---

## 7. Consciously left out

Stated so a reader can price the gaps rather than assume coverage.

1. **Any measurement of this convention.** None exists. Section 5 says so at
   length rather than gesturing at it in a caveat.
2. **The probe wordings.** Section 4 states the probe classes. The scripts
   are written once by the pair that will use them and then frozen; publishing
   a script here would invite adoption of a check nobody calibrated.
3. **Archival science.** Named in section 4 as the unsearched field most
   likely to hold the strongest ancestor for the provenance component. The
   preservation-master vocabulary is borrowed on an unverified attribution.
4. **Accounting records and version-control theory.** Double-entry
   bookkeeping's never-erase rule and the immutable-commit model are both
   near-certain additional ancestors for append-only with supersession, and
   neither was ruled. Their absence understates the ancestry rather than
   overstating it.
5. **Non-English professional practice.** The ancestry hunt covered
   English-language sources only. Civil-law jurisdictions do not run on stare
   decisis, and their decision-record practice would test whether the
   supersession doctrine is universal or common-law-specific.
6. **Patents.** Unsearched in both hunts. The enterprise products in section 5
   are the place a patent hit would change a ruling.
7. **Multi-party capsules.** The definition says two named parties. A record
   of a team's working relationship with a collaborator is a different
   artifact with an unexamined authority-gating problem: whose ruling gates a
   fold.
8. **Distilling a capsule into weights.** Named as the counter-pole and not
   pursued. The position taken here is that a calibration you can read, diff
   and revoke with a text edit is worth more than one you would need a
   training run to change; that is a stated preference, not a measured result.
