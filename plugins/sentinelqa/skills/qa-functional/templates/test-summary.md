# QA Test Summary Report Template

The deliverable. Every section below appears — if one doesn't apply, say "None" rather than
dropping it. A silently omitted section reads as "nothing to report" when it may mean "not checked".

---

```markdown
# QA Report — <TICKET> <Feature>

**Ticket:** <key + title>
**Feature:** <one line>
**Environment:** <name, URL, build/branch — and how the build was confirmed>
**Capability level:** 1 Analysis | 2 Investigation | 3 Execution
**Date:** <absolute date>

## QA Recommendation

> **READY** | **READY WITH KNOWN ISSUES** | **NOT READY** | **BLOCKED — CLARIFICATION REQUIRED**

<Two or three sentences of justification. What drove the verdict, and what would change it.>

---

## 1. Scope

**Tested:** <areas>
**Not tested:** <areas, each with a reason — out of scope / blocked / not provisioned>
**Requirement sources:** <ticket · BRD/FRD/SRS · API spec · mockup · AC only · verbal — and which were unavailable>

## 2. Requirement analysis

**Understood as:** <the requirement in your own words — this is where a misunderstanding surfaces>

**Business rules derived:**
| ID | Rule | Source |
|----|------|--------|

**Assumptions made:** <any "assume X and continue" you were given, or state None>

## 2b. How the deployed build was confirmed

**Never the footer. Never the branch.** Identify the running binary by SERVER BEHAVIOUR, and show
the control that makes the probe meaningful.

| Probe | Result | What it proves |
|---|---|---|
| `<a route that exists ONLY in the candidate build>` | `<status + body>` | the new code is in the running assembly |
| **Negative control** — `<a bogus action on the SAME controller>` | `404` | the positive results are not a catch-all |

<A probe with no control has tested nothing. State the probe in the report, not just the conclusion.>

## 3. Verification summary

**Pass 1 — codebase:** <n> areas examined, <n> predictions recorded
**Pass 2 — execution:** <n> cases executed, or "not performed — <reason>"

| # | Finding | Pass 1 (code) | Pass 2 (live) | Verdict | Class |
|---|---------|---------------|---------------|---------|-------|

### Disagreements between passes
<Every quadrant where code and app disagreed, what was checked, what remains open.
If there were none, say so explicitly.>

## 4. Coverage

| | Total | Covered | Gap |
|---|---|---|---|
| Acceptance criteria | | | |
| Business rules | | | |
| Roles in scope | | | |
| Impacted modules | | | |

**Categories exercised:** happy path · negative · validation · boundary · edge/corner · workflow · role/permission · data persistence · regression
**Input classes covered:** <per key input — classes tested vs classes that exist>
**Data combinations deliberately not tested:** <trimmed matrix entries and the reason>
**Deliberately excluded:** <what and why>

## 5. Test results

| ID | Scenario | Category | Priority | Status | Defect |
|----|----------|----------|----------|--------|--------|

**Totals:** Pass <n> · Fail <n> · Blocked <n> · Not Executed <n>

<Blocked and Not Executed each need a reason. Never let them pass without one.>

### Exploratory sessions

| Charter | Timebox | Level | Findings | Not covered |
|---------|---------|-------|----------|-------------|

<Omit this block if no exploratory session was run. Never leave a session unreported —
an area that was sampled must not read as an area that was covered.>

## 6. Defects

### User-reachable bugs
<Full reports per templates/bug-report.md>

### Edge / validation bugs
<Same format, kept separate>

### Role / permission findings
<Same format, kept separate>

### System-flaw findings
<Same format, kept separate — not user-facing, different fix path>

### Known — not re-raised
| KF ID | Symptom | Verdict | Why it's not being re-reported |

## 6b. Suspicions investigated and **ruled out** — do not re-raise

| Suspicion | Why it is NOT a defect |
|---|---|

**This section is mandatory and "None" is a valid answer only if you genuinely chased nothing down.**
Every theory you formed and then disproved goes here — including your own. It is what stops the next
run rediscovering it, and it is the evidence that findings were filtered rather than accumulated.
A run that produces zero ruled-out items usually means suspicions were filed instead of tested.

## 6c. Not executed — with the blocker named for each

| TC | Rule | Why not executed |
|---|---|---|

**Name the blocker per item: a human decision, a missing permission/account, a missing fixture, or a
tool/environment outage.** "Blocked by a tool" is not "awaiting a human". A blocked case is **not**
evidence the feature works, and **not** evidence it is broken — say so.

## 7. Regression impact

<What else could be affected and should be retested, and why. Derived from the codebase pass
where available — not guessed.>

## 8. Requirement gaps — unresolved

| # | Question | Why it matters | Blocking? |

<Anything still Clarification Required. If any is marked Blocking, the recommendation
above cannot be READY.>

### How every executed case is written (passes included)

```markdown
#### TC-01 · Apply SAVE10 to a $100.00 order

**Steps to reproduce**:

1. Open the checkout page.
2. Enter 100.00 in **Order total** and SAVE10 in **Discount code**.
3. Press **Apply**.

**Expected:** Amount to pay $90.00 (AC1)
**Actual:** Amount to pay $90.00. **Pass.** Confirmed (reproduced).
**Evidence:** `TC-01.png`

![TC-01](04-evidence/TC-01.png)
```

The backticked file name is what the audit counts. The image line is what `report-html.py` embeds.
A case with no screenshot states why in its own body (for example "Not Executed - blocked by …").

## 9. Evidence

<What exists and where: screenshots, logs, responses. If execution didn't happen, say
"No execution evidence — analysis only." Never imply evidence you don't have.>

**AI-drafted artifacts:** <which parts were AI-drafted and reviewed by a human, or None>

### 9b. Evidence index

| File | Shows | Case |
|---|---|---|

<Every file in the evidence directory appears here. An unreferenced artifact is either an untold
finding or dead weight — resolve it, don't leave it. Flag anything that must NOT be cited as
evidence (e.g. captured during a broken-selector or transient-failure window).>

**Captured as data rather than images:** <raw HTTP responses, DOM probes, query output>

## 10. Test data left behind

| Item | State | Action needed |
|---|---|---|

<Every record created, every state transitioned, every permission granted. Say which are cleaned up
and VERIFIED clean, and which are not. An irreversible change is disclosed here, never buried.>

## 11. Corrections to my own Pass-1 predictions

| Rule | Pass 1 predicted | Pass 2 found | Why the prediction was wrong |
|---|---|---|---|

<If Pass 1 predicted PASS everywhere and Pass 2 agreed everywhere, say so explicitly — that is a
meaningful result, not an empty section. Where they disagreed, the prediction being wrong is the
point of two-pass verification: record WHY, because the faulty assumption usually generalises.>

## 12. What passed — do not re-test without cause

<The rules verified live and passing, grouped by acceptance criterion, in enough detail that someone
else can see what is already covered and need not repeat it.>

## 12b. Colleague-reported issues and prior reports on this ticket

<Anything a teammate, developer or earlier QA report already raised on this ticket: what they
claimed, whether this run reproduced it, and the evidence. Write "None" if there were none.>

## 13. Ledger check

<State that `.claude/qa/known-findings.md` was read BEFORE reporting, and what matched. Then any
proposed new entries, quoted verbatim and marked NOT YET WRITTEN.>

## 14. Open decisions

| # | Decision | Recommendation |
|---|---|---|

<Gate D sign-off, anything needing a permission or account you do not have, anything you drafted but
did not post. Close with an explicit line stating that nothing was written to any tracker.>
```

---

## Choosing the recommendation

| Verdict | When |
|---|---|
| **READY** | All in-scope coverage executed and passing. No open defects above trivial. No blocking gaps. |
| **READY WITH KNOWN ISSUES** | Works for the intended use; open defects are understood, accepted and listed. Name every issue being accepted — this verdict is a decision, not an observation. |
| **NOT READY** | One or more defects block the intended use, or core coverage failed. |
| **BLOCKED — CLARIFICATION REQUIRED** | Requirement ambiguity prevents deciding whether behaviour is correct. Not a soft "NOT READY" — it means the question is upstream, not in the build. |

Two rules on the verdict:

- **Never mark READY on unexecuted coverage.** If cases could not be run, the honest verdict is
  READY WITH KNOWN ISSUES (naming the untested area) or BLOCKED — never a clean READY.
- **The verdict is a recommendation, not a decision.** Shipping is the user's call. Give them an
  accurate picture and the reasoning; don't soften the picture to make the call easier.
