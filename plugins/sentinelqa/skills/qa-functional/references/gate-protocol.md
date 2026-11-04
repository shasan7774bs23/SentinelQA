# The Five Gates — the human decides

A gate is a point where a **human decides** and the decision is **recorded in `06-decisions.md`**.
Gates are not status updates. If nothing can change as a result, it is not a gate.

**All five fire on every ticket, at every tier.** The stakes tier scales how much testing a change
earns; it never decides whether a human signs off.

| Gate | After | The question |
|---|---|---|
| **A** | S1 Understand | Are these the right business rules, and are the gaps real? |
| **B** | S2 Design | Is this the right coverage? |
| **C** | S3 Execute | Is each of these actually a defect, at this severity? |
| **D** | S4 Report | Do I sign this verdict, and what gets filed? |
| **E** | S5 Release | Knowing what was not tested, do we ship? |

---

## How to PRESENT a gate — the decision must be readable on its own

A gate asks a human to decide. **If they have to ask you what the question means, the gate has
failed.** Internal shorthand — `BR-3`, `G-1`, `Tier 3`, `S2` — is for the artifacts, never for the
question put to the person.

Every item you ask a human to rule on carries four things:

1. **What it is, in plain English.** Not `BR-2`. *"The Business Email on the form should be the
   adjuster's login email."* Give the id in brackets afterwards if it helps them find it in the file.
2. **What you did, and on what basis.** The rule you derived, the value the code uses, the source
   you took it from.
3. **What breaks if it is wrong.** A concrete scenario with a real consequence — *"an adjuster is
   promoted after the claim is created, and the form prints the old job title to the insurer"* — not
   *"behaviour may be incorrect."*
4. **What you need back.** The literal options: confirm · correct it · or a question you need
   answered before you can continue.

Two specific items are habitually under-explained. Both have an explicit rule:

### Presenting business rules and gaps

- **Never list rule ids alone.** Write the rule out. The human is confirming the *meaning*, and
  cannot confirm an identifier.
- **A gap is not a complaint — it is a decision you are handing over.** For each one, say: what the
  requirement does not state · what the implementation does instead (labelled `Confirmed (source)`
  with its citation) · and what the consequence is if that choice is wrong. Then ask whether to
  accept the implementation's choice or treat it as a clarification question.
- **Rank them.** If six gaps are presented flat, all six look equally important and none gets real
  attention. Say which one matters most and why.

### Presenting the stakes tier

Never ask "do you accept Tier 3?" — a tier number is meaningless to the person signing it off.
**Say what the tier will actually cause you to do, and what the alternative would skip.** For example:

> *Tier 3 means: full regression across the module, Pass 1 reviewing every caller of the changed
> code, an exploratory session, and a rollback criterion in the plan. Tier 2 would mean: the
> affected area plus adjacent ones, Pass 1 on the change itself, no exploratory session.
> The team estimated half a day total for this ticket — Tier 3 will cost more than that.
> Confirm Tier 3, or drop to Tier 2?*

State the cost honestly. A tier that is obviously disproportionate should be flagged as such by
you — but **only a human lowers it**, so present the trade-off rather than quietly resolving it.

## Hard rules for every gate

1. **Record the decision in `06-decisions.md` before work continues** — who, when, what was
   decided, which artifact revision it applies to, and what changed as a result.
2. **One approval authorises one action.** Approval at a gate is never approval for the next, and
   never carries forward to a changed artifact.
3. **An approval names a revision.** "Approved" with no version attached is not traceable.
4. **Rejection is specific.** A bare "no" costs a full cycle and teaches nothing.
5. **Silence is not approval.** An unanswered gate is `BLOCKED — AWAITING APPROVAL`, never a pass.
6. **Running as a subagent you cannot hold a gate open** — you get one return. Produce the
   artifact, state which gate it waits at, return. Never mark a gate passed yourself.

---

## The three autonomy modes

| Mode | Meaning |
|---|---|
| **HITL** — in the loop | Work stops. The human approves, rejects or edits before anything continues. |
| **OHOTL** — observed, on the loop | Work proceeds visibly. The human can interrupt at any moment but is not a blocker. |
| **AHOTL** — autonomous, on the loop | Success criteria agreed up front; the agent completes; the human reviews the output. |

Which mode applies at which station is set by the tier in `intake-triage.md`.

**Gates C, D and E are HITL at every tier, always.** Any judgment that leaves the team — a defect call,
a verdict, a release — is a human's. That is not configurable.

---

## GATE A — Requirement sign-off

**Are these the right business rules, and are the gaps real gaps?**

Presented from `01-requirement.md`: extracted actors and rules in IF/THEN form, the ambiguities,
numbered questions, and what the requirement is silent about. **No test cases yet** — this gate is
about whether the understanding is right, before effort is spent designing against it.

### The interview

Documents do not contain tribal knowledge. Where the developer or requirement owner is reachable,
ask these before designing. Five minutes here buys coverage no amount of document analysis produces.

1. What part of this worries you most?
2. What has broken in this area before?
3. What would a user have to do for this to go wrong?
4. What is deliberately out of scope?
5. What would a test suite plausibly miss?

Record the answers in `01-requirement.md`, **attributed**. They are evidence, not opinion — an
answer to Q2 that contradicts the ledger is itself a finding.

Optional at Tier 1 · **required** at Tier 2 · required plus a second reader at Tier 3.

**Outcome:** APPROVED → S2 · REJECTED → re-analyse · `CLARIFICATION REQUIRED` → stop; do only what
does not depend on the answer.

---

## GATE B — Plan approval

**Is this the right coverage, and are we agreed on what is pass/fail versus what needs a human eye?**

The judgment/execution boundary. After approval, S3 runs the plan and never silently re-decides it.

### What S2 produces first

**The COMPLETE suite — never a sample.** The human is approving *coverage*; coverage cannot be
approved from a representative subset. Every case the tier calls for: happy, negative, validation,
boundary, workflow, role/permission, regression, plus the test data.

Then the **self-review** — `test-case-review.md` §1–4 plus the eight-point review in
`ai-assisted-qa.md`. **Run it in a fresh context holding only the requirement and the drafted
suite, not the reasoning that produced them, and prefer a cheaper, differently-prompted model
tier.** A reviewer carrying the generator's reasoning grades to the generator's assumptions, and
the failures that matter are precisely the ones invisible from inside the generating step.

Write the result to `02-plan.md`.

### What is presented

- **Coverage summary** — counts by type
- **The full case list** — every case, with the business rule it traces to
- **Hard assertions ⟡ qualitative judgments**, marked distinctly — what is machine-checkable
  pass/fail versus what needs a human to look
- **Known traps**, tied to the individual steps they endanger
- **What is explicitly NOT covered, and why** — *blocked* separated from *out of scope*. Put it
  first; it is what a reviewer most needs and what is most easily buried.

### The decision

| Outcome | What happens |
|---|---|
| **APPROVED** | Freeze `02-plan.md` at this revision, record its hash in `06-decisions.md`, post the plan to the ticket, continue to S3. |
| **APPROVED WITH EDITS** | Apply the edits verbatim, save as a new revision, post **that** revision. Never re-draft around an edit. |
| **REJECTED** | Targeted revision — below. |

### Reject vocabulary

A rejection names **which cases** and **why**, from this fixed list — the eight-point review
categories, reused so each reason maps to one correction.

| Reason | The correction |
|---|---|
| Expected result derived from the app, not the requirement | Re-derive from the rule. If the requirement is silent, it is a clarification question, not a test — reopen Gate A. |
| Untraceable to any business rule | Delete it, or surface the undocumented rule. Never keep a case "just in case". |
| Invented expected result | Cross-check against the source; if unsupported, raise it as a question. |
| Duplicate equivalence class | Merge, and state which partition now covers it. |
| Missing dimension | Add cases for that dimension only — role, state transition, persistence after reload, pre-existing records, impacted modules. |
| Bundled assertions | Split, so each case has one reason to fail. |
| Unreal UI labels | Verify against the actual UI. Generated labels are plausible and frequently wrong. |
| Out of scope for this ticket | Move to a deferred list inside the plan. Keep it visible. |

### Revision discipline

- **Correct only what was rejected.** Regenerating the whole suite discards reviewed, accepted work
  and resets the human's context. It is the most wasteful possible response to a specific objection.
- **Re-present with a DIFF** — removed, added, changed, each against its reject reason.
- **Every round is its own entry in `06-decisions.md`.**
- **Three non-converging rounds → stop.** That is a requirement problem, not a design problem.
  Reopen Gate A and say so.

### Publishing the approved plan

On approval the plan is posted as a **comment on the ticket**.

**⛔ The agent never posts. The human's own session does.** Ticket access inside the subagent is
read-only and stays that way. An approve/reject loop needs a mid-run pause, and a subagent gets one
return — so the loop runs in conversation, where the human is, and the write belongs there too.

- **One operation:** add a comment. Never create, edit, transition, delete or log work.
- **One approval = one comment.** A further post needs a further approval.
- **Verbatim from `02-plan.md`** — never a re-summary, or there are two versions of the truth.
- **Never edit a posted comment.** A revised plan posts a *new* comment headed
  `Test Plan — Revision N (supersedes comment #<id>)`.
- **Size:** full case table up to ~50 cases; beyond that post the coverage summary, per-type counts
  and the "not covered" list, pointing to `02-plan.md`.
- **Record the comment id** in `06-decisions.md`.

**Handoff:** `lead-test-automation-engineer` builds against `02-plan.md` by TC id. A case that has
not passed Gate B is not ready to automate.

---

## GATE C — Defect validation

**Is each of these actually a defect, and is this the right severity and priority?**

Per candidate finding, after the validation gate in `defect-analysis.md` and the control check. The
default answer remains **"not a defect."**

Every ruled-out candidate goes to the known-findings ledger **with its reasoning**, so the same
non-bug is never investigated twice. Every confirmed defect carries its full anatomy on this first
pass — ticket number, severity and priority, numbered steps, labelled Expected and Actual, Evidence.

---

## GATE D — Verdict &amp; filing

**Do I sign this verdict, and which of these drafts get filed?**

The agent drafts; the human says yes; only then does anything reach the tracker. Each item is
authorised separately — approval to file one bug is not approval to file the next.

---

## GATE E — Release go/no-go

**Knowing what was not tested, do we ship?**

Owned by the `release-gate` skill; the approver is named in the report. With case files on disk the
release gate enumerates coverage from **structure** rather than from whatever reports it was handed
— which closes the failure mode it exists to guard against.

---

## Never do

- Treat presenting a draft as permission to act on it.
- Record an approval without the artifact revision it applies to.
- Carry an approval forward to a changed artifact.
- Let an unanswered gate decay into a pass.
- Post to a tracker from inside a subagent.
- Regenerate a whole suite in response to a specific rejection.
