# Bug Report Template

## Title formula (mandatory)

```
[Module] – [Condition/Action] – [Incorrect behaviour]
```

Good:
> [Claims] – Saving an Accident claim without an Incident Reference does not show required-field validation

Bad:
> Validation not working · Bug in claim screen · Incident reference issue

The title must let a reader who was not in the room know **where**, **when**, and **what's wrong**
without opening the ticket.

---

## Body

```markdown
**Class:** Bug — user-reachable | Bug — edge/validation | Finding — role/permission | Finding — system flaw
**Status:** Confirmed | Observed | Potential
**Severity:** S1–S4        **Priority:** P0–P3
**Environment:** <name + URL + build/branch, and how the build was confirmed>
**Module / Area:**
**Requirement / Ticket:**
**Frequency:** Always | Intermittent (x of y attempts) | Once

### What's wrong
<Two or three sentences, plain English, no jargon. What a user experiences and why it matters.
A non-technical reader must understand this paragraph.>

### Preconditions
<State that must exist first: data, roles, configuration, feature flags.>

### Test data
<Exact values used. Accounts by label, not password.>

### Steps to reproduce
1. <One action per step. Name the real screen, tab, button and field labels.>
2. …

<Never shorten these. Completeness beats brevity.>

### Expected result
<Exact expected behaviour, and where it comes from — the requirement, AC, or documented rule.>

### Actual result
<Exactly what happened. No interpretation here.>

### Evidence
<Screenshot / log / API response / video / reproducible steps. If none, say so — do not invent any.>

### Control check
<Does it also fail on a flow the change didn't touch, or on a build without the change?
This is what separates a real regression from an environment difference.>

### Business impact
<Who is affected and what it costs them.>

### Regression impact
<What else could be affected and should be retested.>

### Attachments
<List, or "None">

---
> **Technical note (for dev):** <file:line, query, root cause, suspected fix. Keep ALL jargon here.>
```

---

## Compact bug block (for consolidated / release / multi-bug reports)

When a report lists many defects, use the full body above where space allows, but **never drop below this compact block** — every one of the five core elements is still mandatory for each bug. Use this exact shape:

```markdown
### BUG-<n> · <TICKET-KEY> — [Module] – [Condition/Action] – [Incorrect behaviour] · S<n> · P<n> · [Confirmed | Observed | Potential]

**Steps to reproduce:**
1. <one UI action per step — real screen/tab/button/field names>
2. …

**Expected:** <what should happen, and where it comes from — AC/requirement>
**Actual:** <exactly what happened>
**Evidence:** <screenshot filename / API response / file:line — or explicit "none">
```

Rules for the compact block:
- The **ticket key** is in the heading of every bug (a findings table alone does not satisfy this).
- **Steps, Expected, Actual, Evidence are all present for every bug** — even S4 cosmetic ones. No summary sentence replaces them.
- Keep dev-only jargon (file:line, root cause) on the Evidence line or a trailing note, not in the Steps.
- If several bugs share one ticket (e.g. sub-requirements a/b/c or multiple gaps in one feature), give each its own block (BUG-15-A, 15-B, …), each with its own Steps/Expected/Actual/Evidence.

---

## Severity vs Priority — they are different axes

**Severity = impact if it happens.**

| | |
|---|---|
| **S1** | Data loss/corruption, security exposure, core workflow blocked, no workaround |
| **S2** | Major function broken or wrong result; painful workaround exists |
| **S3** | Minor function wrong; easy workaround |
| **S4** | Cosmetic, wording, alignment |

**Priority = how soon it must be fixed.**

| | |
|---|---|
| **P0** | Fix now — blocks release or is live in production |
| **P1** | Fix this sprint |
| **P2** | Scheduled backlog |
| **P3** | Fix if convenient |

They genuinely diverge. A typo in a customer-facing legal document is **S4 severity / P0 priority**.
A crash in a screen nobody uses this quarter is **S1 / P2**. Never derive one from the other.

## Before you write the report

- The defect validation gate in `references/defect-analysis.md` has been passed.
- The known-findings ledger has been checked.
- Every claim is labelled Confirmed / Observed / Potential.
- No evidence is invented.
