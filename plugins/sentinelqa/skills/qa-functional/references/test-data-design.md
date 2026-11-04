# Test Data Design

Boundaries are in `boundary-testing.md`. This file is about everything between them: which values
to pick, how many, and which ones quietly stop working after the first run.

Pick values *before* writing steps. A case written first and given data afterwards ends up with
"enter a valid email" — which is not a test, it's a hope.

## Partition every input first

For each input, list its **valid classes** and its **invalid classes**. A class is a set of values
the system is supposed to treat identically. Test one representative per class — not three.

Three values from the same class are one test wearing three hats. They fail together, they pass
together, and they cost triage time on every run forever.

**Worked example — Age, required, accepted range 18–65:**

| Class | Kind | Representative |
|---|---|---|
| Below range | Invalid | 17 |
| In range | Valid | 34 |
| Above range | Invalid | 66 |
| Non-numeric | Invalid | `abc` |
| Empty | Invalid | (blank) |
| Negative | Invalid | -5 |

Six cases. Not forty. Then `boundary-testing.md` adds 17/18/19 and 64/65/66 at the edges of the
partitions you just drew — **derive both from the same partition set**. Doing boundaries and
partitions independently is how a suite ends up with the same value tested four times.

## Where classes come from

| Source | Gives you |
|---|---|
| Business rules | The classes that actually change behaviour — see `business-rule-analysis.md` |
| Validation rules | Format, length, type, required-ness |
| Database schema (Level 2) | Real column types and lengths, which often disagree with the UI |
| Requirement silence | A **gap**, not a class you get to invent. Raise it. |

If the requirement never states the accepted range, you cannot partition it. That is a
clarification question, not a guess.

## Combining inputs — the data-condition matrix

Once each input is partitioned, you still have to decide which *combinations* to test. Full
cross-product is almost always padding.

Rows = inputs. Columns = the classes you care about. Test a combination only when a business rule
actually distinguishes it. Everything else is one representative.

```
              | Role: Admin | Role: Adjuster | Role: Read-only
Status: Draft |     R1      |      R1       |      R2
Status: Final |     R3      |      R2       |      R2
```

Four rules → four cases, not six. Combinations that land on the same rule are duplicates.

For rule-heavy features use a decision table or pairwise selection — both in
`business-rule-analysis.md`. Say in the report which combinations you deliberately did not test
and why. A silently trimmed matrix reads as full coverage.

## Realistic beats merely valid

Valid data proves the field accepts what the developer expected. Realistic data proves it survives
actual users. Include at least one of each where the field takes free text:

- Names with an apostrophe or hyphen — `O'Brien`, `Smith-Jones`
- Non-ASCII characters, if the product has any international reach
- Leading and trailing whitespace — is it trimmed, rejected, or stored?
- A value at realistic maximum length, not the schema maximum
- Two records differing only by case — `test@x.com` vs `TEST@x.com`

These are not edge cases. They are Tuesday.

## Data that expires

Flag every value that only works once. This is the single most common reason a suite passes on
day one and fails forever after.

| Kind | Example | What the case must state |
|---|---|---|
| Single-use | Reset token, OTP, invite link | How to generate a fresh one |
| Unique-constrained | Email, username, reference number | The uniquifying pattern, e.g. `qa+<timestamp>@…` |
| State-consuming | A Draft record the case submits | That it needs an unused record, and how to create one |
| Time-sensitive | A date that must be in the future | Relative, never hardcoded — "today + 7", not "25/12/2026" |

A hardcoded future date is a test that is scheduled to fail.

## Data that must *not* exist

Half of negative testing depends on absence. State it as a precondition explicitly — an
unregistered email only tests "unregistered" if nobody registered it last sprint.

## Handling and safety

- **Accounts by label, never passwords.** Same rule as `templates/test-case.md`.
- **Never real customer data.** No production PII in a test case, a ticket, or a screenshot.
  Mask it, or generate it.
- **Never real payment details**, including your own.
- Note anything that leaves a trace — a case that fires a real email or a real webhook says so in
  its preconditions.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| "Enter valid data" | Name the value |
| Ten cases differing only by an in-class value | One case, or a data-driven table |
| Hardcoded dates | Express relative to today |
| Shared fixture record every case mutates | Each case creates its own |
| Data invented to match observed app behaviour | Derive it from the rule, not the screen |
| Password or PII pasted into a case or ticket | Label the account; mask the data |

## Before finishing

- Every input has its classes listed, valid and invalid.
- One representative per class, and the boundaries come from the same partitions.
- Every combination tested maps to a distinct business rule; trimmed ones are named in the report.
- Expiring, unique, and time-sensitive values are flagged with a refresh procedure.
- Absence preconditions are stated where a negative case depends on them.
- No production PII, no passwords, no real payment data.
