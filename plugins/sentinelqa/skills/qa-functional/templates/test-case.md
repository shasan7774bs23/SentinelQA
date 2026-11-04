# Test Case Template

## Fields

| Field | Description |
|---|---|
| Test Case ID | Unique — `TC-<TICKET>-<nnn>` |
| Requirement ID | Traceability back to requirement / AC / business rule |
| Scenario | What is being tested, in one line |
| Category | Happy path · Negative · Validation · Boundary · Edge/corner · Workflow/State · Role/Permission · Data persistence · Error handling · Navigation · Regression |
| Priority | P0–P3 |
| Preconditions | Data, role, configuration that must exist first |
| Test Data | Exact values. Accounts by label, never passwords |
| Steps | Numbered, one action each, real UI labels |
| Expected Result | Exact expected behaviour, traceable to a requirement |
| Actual Result | Filled only during real execution |
| Status | Pass · Fail · Blocked · **Not Executed** |
| Defect ID | If one was raised |

## The status rule — absolute

**If you did not execute it, Status is `Not Executed`.**

Never write Pass or Fail without real execution evidence. An unexecuted case with a confident
"Pass" is worse than no test at all — it manufactures false assurance and it is the fastest way
to lose the reader's trust in every other row.

---

## Long form

```markdown
### TC-<TICKET>-<nnn> — <Scenario>

| | |
|---|---|
| **Requirement** | |
| **Category** | |
| **Priority** | |
| **Status** | Not Executed |

**Preconditions**
- …

**Test data**
- …

**Steps**
1. …
2. …

**Expected result**
…

**Actual result**
_Not executed_

**Defect** — none
```

## Table form (for a suite)

```markdown
| ID | Scenario | Category | Priority | Precondition | Steps | Expected | Status | Defect |
|----|----------|----------|----------|--------------|-------|----------|--------|--------|
```

Use the table when presenting coverage across many cases; use the long form when a case has
real setup complexity or will be handed to someone else to run.

---

## Export form — Zephyr Scale (Jira)

For handing a designed suite to Zephyr Scale Cloud without retyping it. Emit one object per
case. Field names below match the Zephyr Scale **v2** API exactly — do not rename them.

```json
{
  "projectKey": "ABC",
  "name": "TC-ABC-001 — Reset password with an unregistered email",
  "objective": "Traces to: AC-3 / BR-07. Category: Negative.",
  "precondition": "No account exists for the address under test.",
  "priorityName": "High",
  "statusName": "Draft",
  "folderId": null,
  "labels": ["negative", "authentication", "ai-drafted"],
  "customFields": {},
  "_teststeps": {
    "mode": "OVERWRITE",
    "items": [
      {
        "inline": {
          "description": "Open the Forgot Password screen.",
          "testData": "",
          "expectedResult": "The email entry field is displayed."
        }
      },
      {
        "inline": {
          "description": "Enter an unregistered address and select Send.",
          "testData": "no-such-user@example.com",
          "expectedResult": "A neutral confirmation is shown. No account-existence hint is leaked."
        }
      }
    ]
  }
}
```

### Mapping rules — read before using this

**`statusName` is NOT a test result.** In Zephyr Scale it is the case's *lifecycle* status —
`Draft`, `Approved`, `Deprecated`. Pass/Fail/Not Executed belong to a **test execution**, which
is a different object created against a test cycle. Never map this template's `Status` field
into `statusName`, and never write `Pass` anywhere in an export. A designed-but-unrun case is
`"statusName": "Draft"` and simply has no execution yet — which is the correct representation of
**Not Executed**.

**Steps are a second API call.** `POST /testcases` creates the case; steps go to
`POST /testcases/{testCaseKey}/teststeps` afterwards, using the returned key. The `_teststeps`
block above is a local carrier for that second call — the leading underscore marks it as not
part of the create payload. Strip it before POSTing the case.

| This template | Zephyr field | Note |
|---|---|---|
| Test Case ID | prefix of `name` | Zephyr assigns its own key (`ABC-T12`); keep yours in the name for traceability |
| Requirement ID | `objective`, or a custom field | Better as a custom field if one exists — then it is filterable |
| Scenario | `name` | |
| Category | `labels[]`, or a custom field | |
| Priority | `priorityName` | By name, not ID — e.g. `"High"` |
| Preconditions | `precondition` | |
| Test Data | per-step `testData` | Belongs on the step, not the case |
| Steps | `_teststeps.items[].inline.description` | Order is array order — there is no index field |
| Expected Result | `_teststeps.items[].inline.expectedResult` | Per step |
| Actual Result / Status / Defect ID | — | Execution-side. Not part of a test case. |

Other constraints: `projectKey` and `name` are the only required fields · `estimatedTime` is in
**milliseconds** · every key in `customFields` must already exist in the Zephyr project or the
call is rejected · multi-line custom field values use `<br>` for newlines · dates use
`yyyy-MM-dd`.

Verified against the Zephyr Scale Cloud v2 API schema on 2026-09-22. Confirm the base URL and
the `/teststeps` path against your own tenant's API docs before wiring up a script.

---

## Quality bar

Every case must be:

- **Executable by someone else** — no implied knowledge, real screen and field labels.
- **Independently meaningful** — it fails for exactly one reason.
- **Traceable** — points at a requirement or business rule. A case that traces to nothing is
  either an undocumented rule (raise it) or padding (delete it).
- **Realistic** — reflects how a user actually behaves, not how the form is coded.

Do not pad a suite. Ten cases that each catch something beat forty that restate one rule.

## Coverage checklist

Before declaring a design complete, confirm each is considered — or explicitly ruled out with a reason:

Happy path · alternate paths · negative input · input classes (one per partition) ·
boundary values · business-rule combinations · role/permission behaviour ·
workflow state transitions · data persistence after reload · error handling ·
navigation (back, refresh, cancel, multiple tabs) · duplicate submission ·
session expiry · impacted modules · regression.
