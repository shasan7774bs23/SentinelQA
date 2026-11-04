# Test Case Design

Turn each scenario into steps another person can execute without asking you anything.
Format and field definitions live in `templates/test-case.md`.

## The bar

A test case is finished when a competent colleague who has never seen the feature can run it,
and would reach the same verdict you would.

That means: real screen names, real field labels, real button text, exact data, and an expected
result specific enough to be wrong.

## Getting the real UI labels

Invented labels are the fastest way to make a test case unusable. Get them from:

- **Level 2** — the view/template source. This is the reliable path; see `two-pass-verification.md`.
- **Level 3** — the running application.
- **Level 1** — you don't have them. Write the case with a placeholder and **say so**:
  `<field: the Incident Reference input — label unverified>`. Never invent one and present it as fact.

## Writing steps

One action per step. A step containing "and" is usually two steps.

**Weak**
```
1. Log in and go to claims and create a new one with type accident
2. Leave stuff blank and save
3. Verify validation works
```

**Strong**
```
1. Log in as an Adjuster (account: adjuster-1).
2. Open Policy POL-1042 → Claims tab.
3. Click "Add Claim".
4. Set Claim Type = "Accident".
5. Leave Incident Reference empty.
6. Complete all other required fields (see Test Data).
7. Click "Save".
```

Rules:
- Name the starting point. Never assume the reader is already on the screen.
- Name the role and account, by label — never a password.
- Specify data values; don't say "enter valid data".
- Include the action that triggers evaluation (Save, Submit, blur) — it's often the step that matters.

## Writing expected results

The expected result must be **specific, observable, and traceable**.

| Weak | Strong |
|---|---|
| "Validation works" | "Save is blocked. Inline message under Incident Reference: 'Incident Reference is required.' No record is created." |
| "The record saves" | "Record saves, page returns to the Claims list, and the new row appears with Status = Draft." |
| "Correct data shows" | "Incident Date shows 08/12/2026 14:30 — the value entered in step 5." |

Every expected result should trace to a requirement, AC, or business rule. If you can't point at
one, you're asserting a personal preference — either find the rule or raise it as undocumented.

**Include the negative half** where it matters: what should *not* happen. No record created, no
email sent, no state change. Absence is frequently the actual requirement.

## One reason to fail

A case should fail for exactly one reason. If it can fail three ways, a failure tells you nothing
and you'll spend the triage time you saved writing it.

Split compound assertions into separate cases, or make the extra checks explicitly secondary.

## Preconditions and test data

**Preconditions** — everything that must be true before step 1: data existing, role assigned,
configuration set, feature flag on. If a case needs setup nobody can perform, mark it **Blocked**
and say what's needed; don't quietly drop it.

**Test data** — exact values. Accounts by label. Note data that must be *fresh* (a case that only
works on an unused record needs to say so, or it'll pass once and fail forever after).

## Independence

Cases must not depend on each other's side effects. If case B needs the record case A created,
either fold them into one case or make B create its own.

Chained cases fail as a block, and the first failure hides everything behind it.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| "Verify the feature works correctly" | State the specific observable outcome |
| Implied knowledge ("navigate to the usual screen") | Name it |
| Ten cases differing only in an irrelevant value | One case, or a data-driven table |
| Testing the framework | Delete it |
| Steps that assume the previous case ran | Make it self-contained |
| Expected result copied from observed behaviour | Derive it from the requirement, not the app |

That last one matters most: if you write the expected result by looking at what the app currently
does, you have documented the bug rather than found it.

## Before finishing

- Status is **Not Executed** unless you actually executed it.
- Every case traces to a scenario, and through it to a rule or AC.
- No padding — every case can fail for a real, distinct reason.
- Preconditions are achievable, or the case is marked Blocked with the reason.
