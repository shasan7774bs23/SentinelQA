# Exploratory Testing

Scripted cases check what you already thought of. Exploratory testing is a timeboxed, chartered
hunt for what you didn't. It is **structured** — a charter, a timebox, and notes — not "click
around and see."

Run it as a **complement to** scripted coverage, never as a substitute. If exploratory testing is
the only testing that happened, the report says so.

## When it earns its place

| Situation | Why |
|---|---|
| Scripted cases all pass and the feature still feels wrong | The design missed a dimension |
| Requirements are thin and clarification is slow | Findings become the clarification questions |
| A defect was fixed | The area around the fix is the likeliest place for the next one |
| A workflow crosses several modules | The seams between modules are where cases stop looking |
| Level 3 access just became available | Cheapest first look before running the formal suite |

Do **not** use it to skip design. An exploratory session on an unanalyzed requirement finds
whatever is loudest, not whatever matters.

## Charter format

One charter, one session. Keep it to a sentence:

> **Explore** the Claim approval workflow
> **With** an Adjuster account and a record already rejected once
> **To discover** state transitions the requirement doesn't define

A charter that could describe the whole product is not a charter. If you cannot name what you are
hunting, go back to `test-scenario-design.md`.

## Timebox

45–90 minutes. Stop at the timebox even mid-thread — write the thread down as the next charter.
Sessions that run until you get bored produce notes nobody can read.

## Useful tours

Pick one lens per session; mixing them turns into wandering.

| Tour | You do |
|---|---|
| **Interruption** | Refresh, back-button, close the tab, double-submit, open two tabs on the same record |
| **Sequence** | Do the steps in an order nobody designed for |
| **Data** | Push the values from `test-data-design.md` in unscripted places |
| **Role** | Repeat the same flow as every role that can reach it |
| **Landmark** | Jump straight to a deep URL without passing through the flow |
| **Money/consequence** | Follow anything that sends, charges, deletes, or notifies |
| **Configuration** | Toggle the setting or flag the feature depends on, mid-flow |

## Take notes as you go, not afterwards

Record, in this order, as it happens:

1. What you did — enough to re-walk it
2. What you observed
3. What you expected, and where that expectation came from
4. Questions raised

Reconstructed steps are how an irreproducible bug report gets written. Note it live.

## The evidence rules do not relax here

Everything in the main method still binds:

- A finding from an exploratory session is **Observed** until you reproduce it deliberately.
  Reproduce it, then it is **Confirmed (reproduced)**.
- It still goes through the validation gate in `defect-analysis.md` before it is called a defect.
  Surprise is not the same thing as wrong.
- It still gets checked against `.claude/qa/known-findings.md`.
- If the behaviour is undefined by the requirement, it is a **Requirement gap**, not a bug — and
  probably a good clarification question.

An exploratory session is a licence to look anywhere. It is not a licence to lower the bar for
what counts as proven.

## What the session produces

- **Confirmed findings** → into the normal defect flow
- **New test cases** → anything worth re-running becomes a scripted case, and the design was
  incomplete without it — say so rather than quietly adding it
- **Clarification questions** → into the gate
- **Ruled-out behaviour** → a proposed ledger entry, so nobody hunts it again
- **The next charter** → whatever the timebox cut off

## Reporting

Report sessions by charter, not by minute:

```markdown
### Session 1 — Claim approval, rejected-record path
**Charter:** … · **Timebox:** 60 min · **Level:** 3 · **Account:** adjuster-1
**Coverage:** approval, rejection, re-submission, two-tab editing
**Findings:** 2 Observed (1 reproduced → BUG-xx), 1 requirement gap (Q3)
**Not covered:** bulk approval — no test data available
```

Always state what the session did **not** reach. An exploratory report without a "not covered"
line reads as full coverage of an area that was sampled, and that is the most dangerous sentence
in a QA report.
