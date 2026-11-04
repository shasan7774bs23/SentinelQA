# Known-Findings Ledger

**Location:** `.claude/qa/known-findings.md` in each project.
**Purpose:** stop the agent re-raising something already investigated and ruled out.

This is the memory that prevents the worst QA failure mode — reporting the same non-bug every cycle
until nobody reads the report. Consult it before reporting **any** finding; append to it after
**every** run.

---

## Schema

| Column | Meaning |
|---|---|
| **ID** | `KF-nnn`, never reused |
| **Date** | When the verdict was reached (absolute date, not "last sprint") |
| **Area** | Module / screen / feature |
| **Symptom** | One line — what someone would *observe*. Write it the way a person would re-report it. |
| **Verdict** | See below |
| **Why** | The reasoning that settled it. This is the most important column. |
| **Ref** | Ticket, commit, or `file:line` |

### Verdicts

| Verdict | Meaning |
|---|---|
| `NOT A DEFECT` | Investigated; behaves correctly. Do not re-raise. |
| `BY DESIGN` | Surprising but intended. Do not re-raise. |
| `ENV DIFFERENCE` | Environment/config/data artefact, not the product. |
| `KNOWN — OPEN` | Real defect, already filed. Reference the ticket; do not duplicate. |
| `KNOWN — DEFERRED` | Real, consciously accepted for now. Reference the decision. |
| `FIXED` | Was real, now resolved. Kept so a regression is recognisable. |

---

## Table

```markdown
| ID | Date | Area | Symptom | Verdict | Why | Ref |
|----|------|------|---------|---------|-----|-----|
| KF-001 | 2026-01-01 | Profile | Phone number reads back empty for a non-owner | NOT A DEFECT | PII masking blanks it for non-owners; data saves correctly | XYZ-101 |
| KF-002 | 2026-01-01 | Checkout | Full-form POST appears to no-op | NOT A DEFECT | Every field auto-saves individually; no user-visible symptom. Tech debt, not a bug | XYZ-102 |
```

*(Rows above are examples of the format — replace with the project's real entries.)*

---

## Rules

**Before reporting anything**, match candidates against this ledger by *symptom*, not by wording.
The same defect gets described differently every time — match on what was observed.

A match → report it as **Known**, cite the ID, and move on. Do not re-argue a settled verdict
unless you have **new** evidence, in which case say explicitly what changed.

**After every run**, propose new rows for anything you ruled out. A finding investigated and
dismissed without a ledger row will be investigated again next cycle by someone else.

**Never delete a row.** If a verdict changes, add a new row and mark the old one superseded —
the history is what makes the ledger trustworthy.

**Keep `Why` substantive.** "Checked, not a bug" is useless in three months. Write the reasoning
that would stop a competent colleague reopening it.

---

## Starter file

```markdown
# Known Findings — <project>

Consulted before reporting any QA finding. See the qa-functional skill.

| ID | Date | Area | Symptom | Verdict | Why | Ref |
|----|------|------|---------|---------|-----|-----|
```
