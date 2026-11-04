# Test Scenario Design

A **scenario** is a situation worth verifying. A **test case** is the executable steps that verify it.
Design scenarios first — otherwise you write cases for whatever comes to mind and discover the gaps
after release.

## Derive systematically, not by brainstorming

Generate scenarios from each source in turn. Brainstorming finds the obvious; enumeration finds the rest.

| Source | Yields |
|---|---|
| **Each business rule** (`BR-nnn`) | One scenario per rule outcome, both branches |
| **Each decision-table row** | One scenario per meaningful combination |
| **Each state transition** | Valid, invalid, unauthorized, repeated — see `workflow-testing.md` |
| **Each role** | Permitted and denied behaviour — see `role-permission-testing.md` |
| **Each bounded input** | Limits and just-outside — see `boundary-testing.md` |
| **Each error path** | What the user sees and can do next — see `negative-testing.md` |
| **Each dependency** | Behaviour when it's slow, down, or returns nothing |
| **Each impacted module** | Regression on things that were already working |

## Coverage dimensions

Consider every dimension, then explicitly rule out the ones that don't apply — with a reason.
"Not applicable" recorded is coverage; silence is a gap.

**Functional** — happy path · alternate paths · business rules · workflow
**Negative** — empty, invalid, malformed, invalid combinations, unauthorized, unexpected actions
**Validation** — field rules, cross-field rules, the exact message text, and whether the server enforces it too
**Boundary** — min, max, just inside, just outside, character and numeric limits, dates
**User behaviour** — back, refresh, double-click, duplicate submit, multiple tabs, navigate away, cancel, retry
**System behaviour** — session expiry, API failure, timeout, missing data, invalid state, dependency failure
**Data** — persistence after reload, defaults, existing records created before the change
**Impact** — related modules, existing workflows, existing records, reports and exports

## Impacted-module analysis

The most under-tested area, and where regressions actually escape. For the feature under test, ask:

- What **shares** the data it writes? Reports, exports, integrations, downstream jobs.
- What **reads** the state it changes? Grids, dashboards, notifications, search.
- What **calls the same code path**? Other screens using the same service or component.
- What **existing records** does it affect? Data created before this change.
- What **notifications or emails** fire, and did their content or recipients change?

At Level 2 this is answered from the code, not guessed — see `two-pass-verification.md`.

## Risk-based priority

Assign a priority to every scenario. Priority drives what gets run when time is short.

| | Applies to |
|---|---|
| **P0** | Core business flow, data integrity, security/permissions, money, legal documents, anything irreversible |
| **P1** | Major functionality, primary user journeys, main business rules |
| **P2** | Standard functional coverage, secondary paths, common errors |
| **P3** | Cosmetic, rare edge cases, low-impact convenience behaviour |

Weigh **likelihood × impact × detectability**. A rare failure nobody notices for months can
outrank a common one that's obvious immediately.

Explain the reasoning whenever a priority would surprise someone — especially a P0 on something
that looks trivial, like wording on a legal document.

## Deduplicate before writing cases

Merge scenarios that fail for the same reason. Ten scenarios that each catch something distinct
beat forty restating one rule.

Delete a scenario if:
- Another scenario fails for the identical reason.
- It tests the framework rather than the feature (that a dropdown drops down).
- It traces to no requirement or rule — unless it exposes an *undocumented* rule, in which case
  raise the rule instead of quietly writing the test.

## Output

| ID | Scenario | Source (`BR-nnn` / AC / state / role) | Category | Priority |
|----|----------|---------------------------------------|----------|----------|

Then confirm: **every business rule and every acceptance criterion appears at least once** in the
Source column. Anything missing is uncovered — see `traceability.md`.
