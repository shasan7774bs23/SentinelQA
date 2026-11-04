# Business Rule Analysis

Convert prose requirements into **explicit conditional rules**, then enumerate their combinations.
This is the step that prevents missed conditional logic — the single most common source of escaped
defects, because prose hides branches that a table exposes.

## Rule format

Give every rule an ID. Traceability depends on it.

```
BR-001: IF Claim Type = Accident THEN Incident Reference is required.
BR-002: IF Claim Type = Inquiry    THEN Incident Reference is not validated.
BR-003: IF Inspection = ON                      THEN Inspector ID must be present and checked.
```

Rules must be **atomic** (one condition → one behaviour) and **decidable** (you can tell by looking
whether it held).

Rewrite vague prose into testable form:

| Prose | Rule |
|---|---|
| "validated appropriately" | *Undecidable.* → Clarification Required |
| "the field is mandatory for accidents" | `BR-n: IF Type = Accident THEN Field is required` |
| "admins can override" | `BR-n: IF Role has Override THEN <what exactly> is permitted` |

## Find the unstated ELSE

For every stated IF, ask what happens otherwise. Requirements state the interesting branch and
leave the other implied.

```
Stated:   IF Type = Accident THEN Incident Reference required
Implied:  IF Type ≠ Accident THEN ?     ← optional, hidden, or ignored? Not the same thing.
```

An unstated ELSE is either an obvious default (record it as an assumption) or a genuine gap
(raise it). Deciding which is your judgment — but never leave it unrecorded.

## Decision table

List each condition and its full value set, then enumerate combinations.

| # | Claim Type | Inspection | Incident Ref. | Expected |
|---|---|---|---|---|
| 1 | Accident | ON | Present | Saves; inspector ID checked |
| 2 | Accident | ON | Empty | Blocked — required-field error |
| 3 | Accident | OFF | Present | Saves; no inspector check |
| 4 | Accident | OFF | Empty | Blocked — required-field error |
| 5 | Inquiry | ON | Present | Saves; inspector ID checked |
| 6 | Inquiry | ON | Empty | Saves — not validated |
| … | | | | |

The table makes gaps obvious. **Any row you cannot fill in the Expected column is a requirement
gap**, not a decision for you to make.

## Managing combination explosion

Conditions multiply fast — 4 conditions with 3 values each is 81 combinations. Reduce deliberately,
and say that you did:

1. **Always test in full**: rules governing money, legal documents, permissions, or data deletion.
2. **Pairwise** for the rest — every *pair* of values appears together at least once. Catches the
   large majority of combination defects at a fraction of the cost.
3. **Drop impossible combinations**, and say why they're impossible.
4. **Never silently truncate.** If you tested 12 of 81, state that and state the selection rule.

## Watch for

| Problem | Why it matters |
|---|---|
| **Overlapping rules** | Two rules match the same input — which wins? Usually undefined. |
| **Contradictory rules** | Two rules demand opposite outcomes. Always a clarification. |
| **Undefined boundaries** | "large amounts" — where exactly? See `boundary-testing.md`. |
| **Implicit ordering** | Does validation run before or after save? Changes the observable result. |
| **Time-dependent rules** | Anything involving "current", "expired", "recent". |
| **Role-conditional rules** | The same rule behaving differently per role is really several rules. |

## Implicit rules

Some rules are never written but always expected. Confirm rather than assume:

- Required fields block save and say which field.
- Saved data survives a reload.
- A rejected action leaves state unchanged.
- An action a role can't perform isn't offered.
- Dates cannot be set in an impossible order (end before start).

If the system violates one of these, it's a defect even unstated — but verify the expectation with
the requirement owner before filing, because a few of them are deliberate.

## Output

- A numbered rule list `BR-001…n`
- A decision table per rule cluster, with every Expected cell filled or flagged
- A list of unstated ELSE branches with your assumption or a question
- Rules flagged `Clarification Required`

Every rule must reach at least one test scenario. A rule with no scenario is untested coverage.
