---
name: release-gate
description: Release-level quality decision across a Jira fix-version. Aggregates the per-ticket QA reports, defects, coverage debt, cross-ticket regression risk and production signals for everything carrying a fix-version into one release-readiness recommendation. Use when asked whether a release, build or fix-version is ready to ship; to prepare a go/no-go; to roll up QA status across multiple tickets; or to review what a release is actually carrying. For a single ticket, use the qa-functional skill instead.
---

# Release Quality Gate

The per-ticket question is *"does this ticket work."* This is a different question:

> **What is this release actually carrying, and do we know enough about it to ship?**

You are producing a **recommendation for a human who owns the release decision.** Your job is to
give them an accurate picture — including the parts nobody looked at — not to make the call
easier.

A release gate fails in one direction far more often than the other: it aggregates the reports
it was handed, produces a confident green, and silently blesses the tickets nobody tested.
**Enumerate the fix-version first. Collect reports second. Report the difference.**

---

## Hard rules — never violate

1. **A ticket with no QA report is UNKNOWN, never a pass.** Unknown coverage blocks a clean
   READY. This is rule one because it is the failure mode that makes release gates dangerous.
2. **Never upgrade a verdict during rollup.** A ticket that is NOT READY stays NOT READY. A
   release ships over it only as an explicit, named acceptance decision made by a human — and
   that name goes in the report.
3. **Coverage debt is reported, never netted out.** "38 of 40 passed" hides which two and why.
   Blocked and Not Executed each keep their reason all the way to the release report.
4. **Never aggregate a report you have not read.** A verdict line in a spreadsheet is not a
   report. If you only have summaries, say the rollup rests on summaries.
5. **Evidence labels survive the rollup.** Something **Potential** in a ticket report is still
   Potential at release level. Aggregation is not corroboration — three weak signals do not
   make a confirmed one.
6. **Known-issue acceptance is a decision, not an observation.** Every accepted issue is named,
   with who accepted it. An unnamed "known issue" is an unresolved defect.
7. **The verdict is a recommendation.** Shipping is the user's call. Do not soften the picture
   to make that call comfortable.

### Never do
Infer a ticket passed because nobody reported a problem · merge defect classes to shorten the
list · drop a Blocked case because its reason is boring · present a per-ticket regression
section as if it covered cross-ticket interaction · report a metric you did not compute ·
invent production signals · let scope creep turn this into re-testing the tickets.

---

## Step 0 — Capability detection (first action, every run)

State plainly which level you are at:

| Level | You have | You may |
|---|---|---|
| **1** | The fix-version's ticket list only | Report what is in scope and what QA evidence is missing. Nothing more. |
| **2** | + the per-ticket QA reports | Roll up verdicts, defects, coverage debt; assess interaction risk from the reports' own regression sections |
| **3** | + repo access, CI/regression results, production signals | Verify the change surface directly; compute real pass rates and trends |

Never infer a level. At Level 1 the honest output is a **BLOCKED — QA INCOMPLETE** picture plus
a precise list of what must be produced.

## Step 0b — Establish the scope, before anything else

1. **Enumerate the fix-version from Jira**, not from the reports you were given.
   JQL: `fixVersion = "<version>"` — optionally `AND status != Cancelled`. Read through whatever
   Atlassian MCP is available. **Draft only** — never create, edit or transition a ticket.
2. **Match each ticket to a QA report.** Produce three buckets: *reported* · *no report found* ·
   *report exists but is Level 1 (analysis only, never executed)*.
3. **Confirm the build under assessment** — name and how it was confirmed. A rollup of reports
   written against different builds is not a release picture; say so if that is what you have.
4. **Load the known-findings ledger** (`.claude/qa/known-findings.md`) so previously ruled-out
   items are not re-raised as new release risk.

Buckets two and three are usually the headline finding. Lead with them.

---

## The pipeline

```
Fix-version
   → Enumerate tickets from Jira            (scope truth, not report truth)
   → Match tickets ↔ QA reports             → reported / missing / analysis-only
   → Roll up verdicts                       (never upgrading one)
   → Roll up defects by class and severity  (classes stay separate)
   → Coverage debt                          (Blocked + Not Executed, each with its reason)
   → CROSS-TICKET INTERACTION RISK          (references/interaction-risk.md)
   → Carry forward unresolved requirement gaps
   → Regression + production signals        (Level 3)
   → Ledger check
   → Release report + recommendation        (templates/release-report.md)
```

The interaction-risk stage is the one that justifies this skill existing. Everything else is
arithmetic over reports that already exist; interaction risk is the property that is **only**
visible at release level, because no per-ticket report was scoped to see it.

---

## Rolling up verdicts

Map each ticket's per-ticket verdict, then apply the worst-case rule:

| Any ticket is… | Release cannot be better than… |
|---|---|
| NOT READY | **NOT RELEASE READY** — unless explicitly accepted, named, by a human |
| BLOCKED — CLARIFICATION REQUIRED | **BLOCKED — QA INCOMPLETE** |
| No QA report / analysis-only | **BLOCKED — QA INCOMPLETE** |
| READY WITH KNOWN ISSUES | **RELEASE READY WITH ACCEPTED ISSUES** |
| All READY | **RELEASE READY** |

## The four release verdicts

| Verdict | When |
|---|---|
| **RELEASE READY** | Every ticket in the fix-version has an executed QA report and a READY verdict. No open defects above trivial. No unresolved blocking gaps. No untested interaction risk. |
| **RELEASE READY WITH ACCEPTED ISSUES** | Works for the intended use. Every open defect is listed, understood and explicitly accepted by a named person. This verdict is a decision being recorded, not an observation. |
| **NOT RELEASE READY** | One or more defects block the intended use, or core coverage failed, and nobody has accepted them. |
| **BLOCKED — QA INCOMPLETE** | Coverage is unknown for part of the release — tickets with no report, reports that were never executed, or unresolved requirement ambiguity. **The question is upstream, not in the build.** Never soften this to NOT RELEASE READY; they mean different things and lead to different actions. |

**Never mark RELEASE READY over unexecuted coverage.** If part of the release was analysed but
never run, the honest verdict is BLOCKED — QA INCOMPLETE, or ACCEPTED ISSUES naming the
untested area. Never a clean READY.

---

## Reference routing

| Stage | Reference |
|---|---|
| Cross-ticket regression the per-ticket reports could not see | `references/interaction-risk.md` |
| The deliverable | `templates/release-report.md` |

For anything about a *single* ticket — designing cases, validating a defect, judging whether
behaviour is a bug — stop and use the **`qa-functional`** skill. This skill does not re-test;
it decides what the assembled evidence supports.

## Scale to the ask

A four-ticket patch release does not need the full sectioned report — but it still needs the
scope enumeration, the missing-report check and a verdict. Those three are never skipped, at
any size.
