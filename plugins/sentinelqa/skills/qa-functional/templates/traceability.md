# Traceability Matrix Template

Method and ID conventions: `references/traceability.md`.

---

## Master matrix

One row per test case. The full chain on a single line.

```markdown
| REQ / AC | BR | Scenario | Test Case | Category | Priority | Status | Defect |
|----------|-----|----------|-----------|----------|----------|--------|--------|
| AC-1 | BR-001 | SC-001 | TC-123-001 | Happy path | P1 | Not Executed | — |
| AC-1 | BR-002 | SC-002 | TC-123-002 | Negative | P1 | Not Executed | — |
| AC-2 | BR-003 | SC-004 | — | — | — | **UNCOVERED** | — |
```

Mark uncovered rows visibly. They are the reason the matrix exists.

---

## Forward coverage — every requirement reaches a test

```markdown
| REQ / AC | Business rules | Scenarios | Cases | Covered |
|----------|----------------|-----------|-------|---------|
| AC-1 | BR-001, BR-002 | SC-001, SC-002 | TC-001, TC-002 | ✅ |
| AC-2 | BR-003 | SC-004 | — | ❌ no case |
| AC-3 | — | — | — | ❌ not analyzed |
```

Distinguish the two failures — *no case written* vs *never analyzed*. The second is worse.

## Backward coverage — every test serves a requirement

```markdown
| Test Case | Traces to | Verdict |
|-----------|-----------|---------|
| TC-123-019 | — | Orphan → undocumented rule? padding? |
```

Resolve each orphan as: undocumented rule (raise it) · padding (delete) · framework test (delete).
Never invent a requirement to justify an orphan.

## Defect trace — impact of each failure

```markdown
| Defect | Case | Scenario | Rule | REQ / AC | AC met? |
|--------|------|----------|------|----------|---------|
| D-1 | TC-123-018 | SC-012 | BR-004 | AC-2 | ❌ |
```

The last column is what the release decision reads.

## Coverage summary

```markdown
| | Total | Covered | Executed | Passed | Gap |
|---|---|---|---|---|---|
| Acceptance criteria | | | | | |
| Business rules | | | | | |
| Roles in scope | | | | | |
| Impacted modules | | | | | |
```

**Covered ≠ Executed ≠ Passed.** Keep the three columns separate — collapsing them is how a plan
gets reported as a result.

## Blocked vs missed

```markdown
| Item | Not covered because | Owner |
|------|--------------------|-------|
| Judge role matrix | Account not provisioned | <who can provision> |
| AC-7 | Missed in analysis | QA |
```

A blocked gap needs someone else to act; a missed gap is yours to close. Reporting them in one
undifferentiated list hides both.
