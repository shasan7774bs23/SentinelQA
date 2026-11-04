# Traceability

Every link in this chain must hold, in both directions:

```
Requirement → Business Rule → Scenario → Test Case → Result → Defect
```

Traceability is what lets you answer the two questions that decide a release:
**"is everything covered?"** and **"what does this failure actually threaten?"**

## ID scheme

| Artifact | ID | Example |
|---|---|---|
| Requirement / AC | `REQ-<ticket>-<n>` or the AC number | `AC-3` |
| Business rule | `BR-<n>` | `BR-004` |
| Scenario | `SC-<n>` | `SC-012` |
| Test case | `TC-<ticket>-<n>` | `TC-123-018` |
| Defect | Tracker key, or `D-<n>` before filing | `D-2` |
| Known finding | `KF-<n>` | `KF-007` |

IDs are never reused, even after deletion. A reused ID silently rewrites history in every report
that already cited it.

## Forward trace — is everything covered?

Start at requirements, walk to test cases. Anything that doesn't reach one is **uncovered**.

| REQ / AC | Business rules | Scenarios | Cases | Covered? |
|---|---|---|---|---|
| AC-1 | BR-001, BR-002 | SC-001…003 | TC-001…004 | ✅ |
| AC-2 | BR-003 | SC-004 | — | ❌ **uncovered** |
| AC-3 | — | — | — | ❌ **no rules derived** |

Two distinct failures, and both matter:
- **No case** — the rule was identified, nobody tested it.
- **No rule derived** — the requirement was never analyzed. Worse, because nobody knows it's missing.

## Backward trace — does everything serve a purpose?

Start at test cases, walk back to requirements. An orphan case is one of:

1. **An undocumented business rule** — the most valuable thing a review finds. Surface it and get it
   written down; don't just accept the test.
2. **Padding** — delete it.
3. **A test of the framework** — delete it.

Never resolve an orphan by inventing a requirement to justify it.

## Defect trace — what does this failure threaten?

Every defect traces back up the chain. This is what turns "a test failed" into an impact statement:

```
D-1  ← TC-123-018  ← SC-012  ← BR-004  ← AC-2
```

Read upward, it tells you which acceptance criterion is not met — which is what the release decision
actually depends on. A defect that can't be traced to a requirement needs the classification check
in `defect-analysis.md`: it may be an undocumented-rule violation or not a defect at all.

## Coverage summary

Report coverage against **requirements**, never against test count. "84 test cases" says nothing.
"9 of 11 acceptance criteria covered" is a release decision.

```markdown
| | Total | Covered | Gap |
|---|---|---|---|
| Acceptance criteria | 11 | 9 | AC-2, AC-7 |
| Business rules | 14 | 12 | BR-006, BR-011 |
| Roles in scope | 4 | 3 | Judge (not provisioned) |
| Impacted modules | 5 | 5 | — |
```

Always distinguish **not covered because it was missed** from **not covered because it's blocked**.
The first is a QA gap you own; the second is an environment or provisioning problem someone else
must clear. Conflating them hides both.

## Keeping it honest

- A requirement with no rule is unanalyzed, not covered.
- A scenario with no case is designed, not tested.
- A case not executed is planned, not verified.
- A case marked Pass without evidence is not a result.

Each of those degradations is easy to let slide, and each turns a coverage report into a fiction.
State the real level at each stage.
