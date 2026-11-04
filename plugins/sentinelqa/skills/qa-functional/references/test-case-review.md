# Test Case Review

Reviewing an existing suite — someone else's cases, an inherited test plan, or automated tests
offered as evidence of coverage.

Judge two things separately: **is the coverage right**, and **are the cases any good**. A suite can
be immaculate and cover the wrong things.

## 1. Coverage — what's missing

Build the trace both ways (`traceability.md`):

- **Forward** — every requirement, AC and business rule → is there at least one case?
  Anything unmatched is **uncovered**, and that's the headline finding of most reviews.
- **Backward** — every case → does it serve a requirement? Unmatched cases are either an
  **undocumented rule** (valuable — surface it) or **padding** (remove it).

Then check the coverage dimensions from `test-scenario-design.md`. In practice the recurring gaps are:

| Usually missing | Why |
|---|---|
| Negative paths | Suite written from the happy-path spec |
| Boundary values | Requires reading three separate limits |
| Role/permission and data scope | Needs multiple provisioned accounts |
| Invalid state transitions | Only the forward path was drawn |
| Existing records created before the change | Nobody thinks about old data |
| Impacted modules / regression | Scope stops at the feature edge |
| Notifications and emails | Silent when absent — no error to notice |
| Persistence after reload | "It saved" ≠ "it's still there" |

## 2. Quality — case by case

| Check | Fails when |
|---|---|
| **Executable by a stranger** | Implied knowledge, invented labels, "navigate to the usual screen" |
| **Specific expected result** | "Works correctly", "validation happens", "data is correct" |
| **Traceable** | Points at no requirement or rule |
| **One reason to fail** | Compound assertions bundling three checks |
| **Independent** | Depends on a record a previous case created |
| **Realistic** | Tests the framework, or a path no user can reach |
| **Honest status** | Marked Pass with no evidence of execution |
| **Achievable preconditions** | Needs setup nobody can perform, not marked Blocked |

## 3. The dangerous ones

Three failure modes that are worse than a missing test, because they actively mislead:

**Expected result copied from observed behaviour.** Someone ran the app, saw what it did, and wrote
that down as "expected". The case now guarantees the current behaviour forever, including any bug in
it. Tell-tale: expected results phrased with implementation detail, or oddly specific values with no
requirement behind them.

**Tests pinning a known defect.** An assertion that encodes wrong behaviour. When the bug is fixed,
this test fails and someone "fixes" the test. Cross-check any suspicious assertion against the
requirement and the known-findings ledger.

**Passes that never ran.** A suite of green results with no evidence, no timestamps, no environment
recorded. Treat unevidenced Pass as **Not Executed** and say so — this is a coverage claim, not
coverage.

## 4. Redundancy

Cases differing only in an irrelevant value, or several failing for the same reason. Merge or delete.

Be careful: two cases exercising the same *rule* through different *paths* (grid vs detail page,
UI vs export) are not redundant — they fail independently and both are worth keeping.

The commonest hidden duplicate is **same-partition** duplication: several cases feeding
different values from one input class (`31`, `44`, `57` into a field valid for 18–65). They
fail together and pass together, so they are one case in three costumes. Collapse them —
see `test-data-design.md`.

If the suite was AI-drafted, run the eight-point review in `ai-assisted-qa.md` as well —
generated suites duplicate by class and invent expected results more than hand-written ones.

## 5. Staleness

- Does the case reference screens, fields or flows that no longer exist?
- Has the requirement changed since it was written?
- Do the test accounts and data still exist and hold the assumed state?
- Does it target an environment still in use?

## Output

```markdown
## Test case review — <suite / ticket>

**Reviewed:** <n> cases against <n> requirements / business rules

### Coverage gaps          ← uncovered requirements, highest priority first
| Requirement | Gap | Suggested case | Priority |

### Incorrect expected results   ← the dangerous ones
| Case | States | Should state | Source |

### Quality issues
| Case | Issue | Fix |

### Redundant
| Cases | Reason | Recommendation |

### Undocumented rules found
<Behaviour asserted by tests but absent from the requirements — raise these, don't just accept them>

### Assessment
<Is this suite trustworthy as evidence of coverage? Say plainly yes or no, and why.>
```

That final line is the point of the review. A polished suite covering 40% of the rules should be
described as covering 40% of the rules.
