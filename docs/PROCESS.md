# The SentinelQA process — a walkthrough

This guide explains **what happens when you QA a ticket with SentinelQA, and why each rule exists.**
It is written for someone new to the process. The agents follow the full rulebook in
`plugins/sentinelqa/skills/qa-functional/SKILL.md`; this page is the human-readable version.

---

## 1. The idea in one paragraph

Most QA failures are not a lack of effort. They come from **skipped steps that nobody notices**:
a plan nobody approved, a "bug" that was only a guess from reading code, a report that says
"tested thoroughly" with no evidence behind it. SentinelQA fixes this with three things:

1. **Stations** — every ticket goes through the same six steps, in order.
2. **Gates** — at five points the agent **stops and a human decides**. The agent never decides
   for you whether something is a defect, whether the build is ready, or whether to ship.
3. **Proof** — every claim carries evidence (a screenshot, a `file:line`, a log), and two audit
   scripts check the work before it can be called finished.

**No proof, no pass.**

---

## 2. The big picture

```
 S0 INTAKE ──► S1 UNDERSTAND ──► S2 DESIGN ──► S3 EXECUTE ──► S4 REPORT ──► S5 RELEASE
                    │                │              │              │             │
                 GATE A           GATE B         GATE C         GATE D        GATE E
             requirements      test plan        defects       verdict &      go / no-go
              sign-off         approval        validation      filing
```

- **All five gates fire on every ticket**, however small. A trivial ticket gets *less testing*,
  never *fewer human decisions*.
- **Silence is not approval.** If you haven't answered a gate, the run waits at
  `BLOCKED — AWAITING APPROVAL`.
- **One approval covers one action.** Approving the plan does not approve posting a bug.
- Any station can send the run **back** to an earlier one. If a clarification answer changes the
  rules, the plan is redesigned and goes through Gate B again.

---

## 3. The case file — where everything lives

Every ticket gets one folder in the project repo. Every station reads it and writes to it, so
the work survives the chat session, and anyone can see months later what was tested and who
approved what.

```
qa/<TICKET-KEY>/
├── 00-intake.yml      S0  tier, risk score, capability level, run context
├── 01-requirement.md  S1  business rules, gaps, questions and answers
├── 02-plan.md         S2  the complete test suite approved at Gate B
├── 03-pass1.md        S3  predictions from reading the code   ← WRITE-ONCE
├── 04-evidence/       S3  screenshots, traces, API responses, logs
├── 05-report.md       S4  the final report and verdict (+ a .html copy)
└── 06-decisions.md    all every gate decision: who, when, which revision   ← APPEND-ONLY
```

Two files have special rules, and they are what make the record trustworthy:

- **`03-pass1.md` is write-once.** Predictions are written *before* testing and never edited.
  A prediction changed after seeing the result is not a prediction.
- **`06-decisions.md` is append-only.** A wrong decision is never deleted. A new entry supersedes it,
  so the trail stays honest.

---

## 4. Station by station

### S0 — Intake & triage: "what are we testing, and how much does it matter?"

**First, your saved profile.** `/qa-setup`, run once per machine, saves each of your projects: its environments, accounts by role, whether QA can see the source code, and where case files go. Every run reads it first, so it never asks again for what you told it.

**Then, the start-of-run check.** Before any testing, the run confirms it is open in the ticket's
project folder (if not, it tells you where to open Claude Code, or you choose to continue without the
code), reads the ticket, sends one request to the test environment (never production), finds each
role's login and logs in once per role. Everything missing or failing goes into **one** message. After
your answer it runs through to the next gate; anything that breaks mid-run is marked *Not executed*
with its reason instead of stopping the test.

**Then, a dependency check.** Every machine and project is different, so the agent first checks
what this session actually has, without asking:

| Dependency | If it is missing |
|---|---|
| Ticket access (whichever Jira connector exists; **Atlassian Rovo** is the one that works today) | You paste the ticket text. This is the only thing it can't work without |
| Ticket attachments (DB scripts, specs, screenshots) | You drop the files into the case file, or it lists them as *Not reviewed* |
| The project's source code | Once you confirm it isn't available to QA, it tests from the requirement and the live app |
| Test environment and build check | It delivers the analysis and full test design, and marks cases *Not Executed* |
| Test accounts by role | It tests what the accounts it has can reach |
| Browser tool | It tests over HTTP where it can, and marks visual cases *Not Executed* |
| Python (for the audits) | It runs the audit checks by hand and says so |

Everything it couldn't find goes into **one** message: *"Will you provide it? (yes → how / no)"*.
A "no" never stops the run; the agent continues with what exists and records the gap, so the report
says exactly what wasn't covered and why. It never asks you to log in, and it never asks the same
thing twice for the same ticket. For an in-repo case folder it writes a one-line `qa/.gitignore`, so the case file never shows up as a
change to commit; for a read-only project everything goes in an external folder and the repo is not
touched.

**Then it confirms six facts. It never assumes them:**

| # | Fact | Why |
|---|---|---|
| 1 | Ticket number | Everything traces back to it |
| 2 | Branch, and whether it is merged | Decides which code is read |
| 3 | Deployed site (environment URL) | Behaviour and test data differ between environments |
| 4 | **The build actually deployed, and how that was confirmed** | Testing the wrong build makes every result worthless |
| 5 | Test account and role | Permissions change what you can see |
| 6 | First pass or re-test | A re-test never overwrites the original report |

**Confirming the build.** A version number in the page footer is not proof. The agent checks
something only the new build does, plus a **negative control**: something that should *fail*,
to prove the check is real.

**Capability level.** The agent states honestly what it can do in this session:

| Level | Has | Can |
|---|---|---|
| 1 — Analysis | Ticket text only | Analyse and design |
| 2 — Investigation | + the code, docs, logs | Verify the code against the requirement |
| 3 — Execution | + a real browser / API / database tool | Run tests and capture evidence |

**Stakes tier.** This decides how much testing the change earns:

| Tier | Typical changes |
|---|---|
| **3 — High stakes** | Login, permissions, payments, data migration, security |
| **2 — Normal** | Business logic, new features, workflows, reports and exports |
| **1 — Trivial** | Label or text changes, styling, safe config toggles |

A tier goes **up by one** if, for example, the area has open known findings, it broke in a
recent release, or the code was mostly AI-generated. There is also a **risk score**:
likelihood × blast radius, each 1–5. A one-line change to a shared permission check scores
higher than 400 lines on one isolated screen.

**What the tier changes, and what it doesn't:**

| | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Test scope | Happy path + the change | Full design | Full design + exploratory session |
| Code review depth | Changed lines | Full, with `file:line` predictions | Full + every caller of the changed code |
| Regression | Smoke + affected area | + adjacent areas | Full regression |
| **Gates A–E** | **All fire** | **All fire** | **All fire** |

Output: `00-intake.yml`.

---

### S1 — Understand: "what exactly should this do?" → **Gate A**

- **Acceptance criteria come from the real spec**, which is often a ticket *comment*, not the
  description. They are broken down into **numbered, testable rules** (R1.1, R1.2 …) written as
  IF/THEN statements, and counted.
- **Every IF gets its unstated ELSE.** "Required for accidents" → what happens for other types?
- **The Clarification Gate:** if anything that matters is undefined, the agent stops and asks
  precise, numbered questions, each answerable in a word. It never fills a gap with a guess.
- **The interview:** five questions to the ticket owner that the documents can't answer.

**Gate A — Requirement sign-off.** *Are these the right rules, and are the gaps real?*

Output: `01-requirement.md`.

---

### S2 — Design: "what will we test?" → **Gate B**

- The agent designs the **complete** suite for the tier, never a sample: happy path, negative,
  validation, boundary, workflow, role/permission, regression.
- Each case is marked either as a **hard assertion** (machine-checkable pass/fail) or as a
  **qualitative judgment** (needs a human eye). A judgment is never dressed up as an assertion.
- The suite is **self-reviewed in a fresh context by a different model**, so the reviewer doesn't
  inherit the author's blind spots.
- What is **not** covered is listed **first**, not hidden at the end.

Before any execution, the **case-file audit** runs:
`case-file-audit.py qa/<TICKET> --pre-s3`. If an earlier station didn't actually run, it fails
and the run **stops**. A skipped station can't be back-filled later.

**Gate B — Plan approval.** *Is this the right coverage?*
- **Reject:** the agent fixes *only* what you rejected and shows you a diff.
- **Approve:** the plan is frozen. Any later change is a new revision and comes back to Gate B.
- The approved plan is posted to the ticket as a comment, **from your session, never by an agent
  on its own**.

Output: `02-plan.md` (and `test-plan/<TICKET-KEY>-test-plan.md` in the project).

---

### S3 — Execute: "what does it actually do?" → **Gate C**

**Two-pass verification**, always in this order:

1. **Pass 1 — read the code.** Predict what will happen, each prediction with a `file:line`.
   Written to `03-pass1.md` **before** testing, and never edited.
2. **Pass 2 — run it.** Execute the approved cases on the real application and record what
   actually happens, independently of Pass 1.
3. **Reconcile.** Where the two passes disagree, there's information: either the code reading
   was wrong, or the environment is different. Both are reported.

*Why this order:* Pass 1 tells you where to look and what "correct" looks like, so Pass 2 tests a
hypothesis instead of wandering.

**Before anything is called a defect:**
- The default answer is **"not a defect"** until proven otherwise.
- A **control check**: does it also fail on an unaffected flow, or on a build without the change?
  If it does, it's an environment issue, not this ticket's bug.
- A **ledger check**: is it already in the project's known-findings ledger
  (the project's known-findings ledger)? Then it's reported as **Known** and not raised again.
- Environment down or wrong build → `BLOCKED`, **never** `FAIL`. A missing permission on the test
  account → `BLOCKED` for that flow, not a defect.

**Gate C — Defect validation.** For each candidate: *is this really a defect, at this severity
and priority?* Only you decide.

Output: `03-pass1.md`, `04-evidence/`.

---

### S4 — Report: "what did we find?" → **Gate D**

The report is written from the template `templates/test-summary.md` and covers:

- **Recommendation** at the top, then scope, requirement analysis and how the build was confirmed.
- **Coverage as a ratio**: "18 of 26 rules exercised", never "tested thoroughly".
- **Every executed case**, passes included: numbered Steps / Expected / Actual / Evidence, **with a
  screenshot**, or a stated reason why a screenshot is impossible.
- Defects in **separate groups**: user-reachable · edge/validation · role/permission · system flaw ·
  known. They are never merged into one list.
- **Suspicions investigated and ruled out**, including the agent's own wrong guesses.
- **Not executed**, with the blocker named for each case.
- Regression impact, open requirement gaps, evidence index, test data left behind, corrections to
  Pass-1 predictions, what passed, colleague-reported issues, ledger check, open decisions.

Then the **closeout audit** runs: `report-audit.py <report>.md <evidence-dir>`. If it fails, the
*file* is fixed and the audit is re-run. A failure is never explained away in prose.

The report is delivered as **`.md` + a self-contained `.html`** with screenshots embedded, and
filed on the report shelf: `~/Downloads/QA-Reports/<PROJECT>/YYYY-MM-DD_<name>`.

**Gate D — Verdict & filing.** You sign the verdict. Every write to Jira (bug, comment,
transition) is authorised **one at a time**.

Output: `05-report.md` + `.html`.

---

### S5 — Release: "do we ship?" → **Gate E**

For a whole fix-version, the **`release-gate`** skill rolls up every ticket's report:

- **It lists the fix-version first and collects reports second.** A ticket with no QA report is
  **UNKNOWN, never a pass.**
- A NOT READY ticket is never upgraded during the rollup. The release can only ship over it as an
  explicit acceptance decision **with a person's name on it**.
- Coverage debt is listed ticket by ticket, never netted into "38 of 40 passed".
- It checks cross-ticket risk: several tickets touching the same module.

**Gate E — Go / no-go.** A named person decides.

---

## 5. Labels used in every report

**Evidence labels:** how sure are we?

| Label | Means |
|---|---|
| **Confirmed (reproduced)** | Seen live, repeatably, with evidence |
| **Confirmed (source)** | Proven in the code with `file:line`, but not yet seen live |
| **Observed** | Seen once, not yet reproduced |
| **Potential** | Reasoned, not verified |
| **Unknown** | Not investigated (said openly, not left out) |
| **Clarification Required** | Blocked on an unclear requirement |

A label is never upgraded without new evidence. **A bug only gets a severity once it's
`Confirmed (reproduced)`.** Source-only findings go into an "Unverified predictions" section.

**Verdicts:** the recommendation (shipping is still a human call).

| Verdict | When |
|---|---|
| **READY** | All in-scope coverage executed and passing; nothing blocking |
| **READY WITH KNOWN ISSUES** | Works for its purpose; every accepted issue is named |
| **NOT READY** | A defect blocks the intended use, or core coverage failed |
| **BLOCKED — CLARIFICATION REQUIRED** | The requirement is too unclear to judge right from wrong |

*Never READY on untested coverage.* If cases couldn't run, the verdict is READY WITH KNOWN ISSUES
(naming the gap) or BLOCKED.

---

## 6. How the agents talk to you

Anything the agent hands you to decide follows the **decision brief** format
(`references/decision-briefs.md`). Each item gives you:
- what a user would see,
- why it happens and whose it is,
- the evidence and the impact,
- a risk/undo table for anything risky,
- **one** recommendation,
- exactly what it needs from you.

It ends with a **"Your decisions"** checklist, so you can read it once and decide.

**`/qa-functional` versus the `qa-functional` agent.** `/qa-functional <KEY>` is the full run, live
testing included: it works in your own session, with the browser SentinelQA installs, and stops at
each gate for you. The `qa-functional` agent is a background helper for the analysis and test-plan
half. An agent can't wait for a person at a gate, so it stops at the first gate. Its last line always
tells you the next step: `/qa-functional <KEY>`, which continues from the same case file and runs
the tests. Automation work goes to `/qa-automate`.

Things the agents **never** do on their own: file or edit tickets, post comments, commit, push,
send messages, or touch production.

---

## 7. Keeping the process honest over time

The method is the same on every project; **how well it performs on a project depends on that
project's layer**: its QA rules, its ledger and its memory. `/qa-setup` records the basics once; the first ticket asks anything still missing, and at the end
of each run you accept what is worth keeping, so it grows with every run:


- **The known-findings ledger** (one per project: `.claude/qa/known-findings.md`, or next to the case
  files for a read-only project) records what was
  investigated and ruled out, so nobody raises the same non-bug twice. Start one from
  `templates/known-findings-ledger.md`.
- **Agent assurance** (`references/agent-assurance.md`): a ten-ticket "golden set" from your own
  ledger, re-run whenever the agents are changed, to catch the process getting worse.
- **Lessons become rules.** Most rules in this process exist because a past run failed without
  them. When you hit a new failure, propose the rule (see *Changing the process* in the README).
