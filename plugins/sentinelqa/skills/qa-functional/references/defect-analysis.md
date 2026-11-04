# Defect Analysis

**The default answer is "not a defect."** Make the evidence argue you out of that position.

A false bug report costs more than a missed one. A miss costs a retest; a false report costs a
developer's afternoon, and after two or three of them the whole QA report stops being read.

---

## The validation gate

Run every candidate through this, in order. Stop at the first exit.

```
1. Is the requirement clear on this behaviour?
      NO  → Requirement gap. Ask a precise question. NOT a defect (yet).
      YES ↓

2. Does the actual behaviour violate that requirement?
      NO  → Works as specified. Possibly an Enhancement. NOT a defect.
      YES ↓

3. Is it in the known-findings ledger?
      YES → Report as Known, cite the entry, do not re-raise.
      NO  ↓

4. Is it reproducible?
      NO  → Observed. Investigate further before reporting. Say how many attempts.
      YES ↓

5. Does the control check hold? (see below)
      NO  → Environment or data difference, not a defect. Verify before claiming.
      YES ↓

6. Is the build under test actually the build containing the change?
      NO  → Cannot conclude anything. Confirm the deployment first.
      YES ↓

                        → DEFECT. Classify, then report.
```

## The control check

The single most useful question, and the one most often skipped:

> **Does this also fail somewhere the change didn't touch, or on a build without the change?**

- Fails **only** on the changed flow / changed build → genuine regression.
- Fails **everywhere**, including untouched flows → pre-existing behaviour, not this ticket's defect.
  Still worth reporting, but as a separate pre-existing issue.
- Fails on **one environment only** → environment or data difference until proven otherwise.
  Never file an environment difference as a product defect without confirming it on a second environment.

## Classification

Once it passes the gate, assign exactly one class:

| Class | Test |
|---|---|
| **Bug — user-reachable** | A real user, using normal UI affordances, hits it in ordinary work |
| **Bug — edge/validation** | Needs unusual but legitimate input, ordering, or timing |
| **Finding — role/permission** | Wrong data or actions exposed to a role; RBAC gap |
| **Finding — system flaw** | Architectural, config or security issue with no user action that triggers it |
| **Requirement gap** | Behaviour genuinely undefined |
| **Enhancement** | Matches spec; spec is weak |
| **Not a defect** | Matches spec |

Report every class. Keep role/permission and system-flaw findings **visually separate** from the
user-facing bug list — they have a different audience and a different fix path. The decision to
file any of them belongs to the user.

## Accidental defect vs deliberate deferral

Before reporting, check whether the behaviour was **chosen**:

- Search the diff and surrounding code for comments like `deferred`, `not migrated`, `TODO`, `known gap`.
- Check the commit message and PR description for intent.
- Check whether a test asserts the current behaviour — if so, it is intended, and *your* reading is
  the thing in question.

Both still get reported, but differently:

- **Accidental** → a bug. Someone made a mistake; here is the fix.
- **Deliberate deferral** → a scope gap. Someone decided this; the question is whether the decision
  is acceptable and whether it is tracked. Say so plainly, and say who decided it if the code shows it.

Presenting a deliberate deferral as a careless bug reads as sloppy analysis and puts dev on the defensive.

## Common false positives

Check each before reporting:

| Pattern | What it looks like |
|---|---|
| **Environment difference** | Fails on one env; different build, config, feature flag or seed data |
| **Stale build** | The deployed build predates the change |
| **Masked / restricted data** | Field reads empty because a PII or permission rule blanked it — working as designed |
| **Test data artefact** | Seeded record missing a field a real record would have |
| **Permission-by-design** | The role genuinely should not see it |
| **Already-known** | Sitting in the ledger from a previous cycle |
| **Own misreading** | The requirement says something different on a second read |

## Reproducibility

State it explicitly and honestly:

- **Always** — reproduced on every attempt (say how many)
- **Intermittent** — `x of y` attempts, with any pattern you noticed
- **Once** — could not reproduce; report as **Observed**, never as Confirmed

Never round an intermittent failure up to "always."

## Evidence

Every defect needs at least one of: observed behaviour with exact steps · screenshot · log ·
API response · video · a source citation (`file:line`) proving the behaviour.

If you have none, you have a hypothesis. Label it **Potential** and say what evidence would settle it.

**Never invent evidence.** Not a sample log, not a plausible API response, not a described
screenshot. If you did not see it, it does not exist.

## Severity and priority

Assign both, independently — see `templates/bug-report.md` for the scales.

Ask separately:
- *If this happens, how bad is it?* → Severity
- *How soon must it be fixed?* → Priority

Then sanity-check: would the business agree? A wording error on a customer-facing legal document is
low severity and top priority. Say why when the two diverge, so nobody "corrects" it later.

## Writing it up

Plain English in the body, numbered UI steps anyone can follow, all technical detail in a closing
footnote. Never shorten reproduction steps to look concise.
