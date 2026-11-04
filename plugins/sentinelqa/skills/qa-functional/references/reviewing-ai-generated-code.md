# Reviewing AI-Generated Application Code

Not the same job as `ai-assisted-qa.md`. That file reviews AI-drafted **test cases**. This one
reviews AI-drafted **production code** — the PR that arrived from Copilot, Claude or Cursor and
now needs a QA read before anything it does earns a passing suite.

Use it during **PASS 1 — codebase verification** whenever the code under test was AI-generated.

The distinction that makes this a QA job at all:

> A developer reviews AI code to confirm it works. QA reviews it to prove it doesn't — and
> approves only after failing to.

## The six checks

### 1. What does it do when the input isn't clean?
Models are trained on the happy path far more than on chaos. Generated parsing and validation
code handles the well-formed case and quietly ignores the empty cell, the wrong encoding, the
40,000-row upload where 40 were expected.

Ask of every function: *what is the ugliest input a real user could deliver here?* Then check
whether the code even considers it, let alone handles it.

### 2. Trace every error path, not only the main one
Trace what happens when the function **cannot** do its job. Does it fail loudly, fail silently,
or fail in a way that corrupts something downstream?

The tell-tale is a generic `try/catch` that swallows the exception and logs `"an error
occurred"` with no context about what broke. That looks like error handling and is not error
handling. Flag it every time.

### 3. Hunt the assumptions nobody stated out loud
Generated code assumes quietly — the list is never empty, the date is always in the future, the
ID already exists in the database by the time this runs. None of these are wrong *most* of the
time, which is exactly what makes them dangerous. They ship, work for three weeks, and take a
feature down the day someone reaches the one edge nobody coded for.

Read the diff once hunting only for your own thought *"well, that'll always be true."* Every
occurrence of that thought is a flag.

### 4. Write the breaking test before you approve
Do not merely imagine the edge case — write the short test that settles it. Not a suite; just
enough to prove whether the thing you suspect is broken actually is.

Reviewing a generated validation routine means running it against empty, whitespace-only, emoji
and 10,000-character input **now**, not discovering it in production.

This is the check that separates a QA review from a developer review. At Level 1 or 2, say
plainly that the breaking test was designed but not executed.

### 5. Technically correct, contextually wrong
Where the ticket was ambiguous, a human developer pauses and asks. The model picks an
interpretation, commits to it confidently, and flags nothing.

So review against the **original requirement**, never against the code alone: *is this what we
meant, or merely what was easiest to generate from the words we used?* An unflagged
interpretation is a **Requirement gap**, not a bug — classify it that way and raise it.

### 6. Do not accept generated tests as evidence of coverage
When the AI wrote tests alongside the code, read the **assertions**, never the pass/fail
summary. Generated suites routinely test the happy path five different ways and never once test
a failure case. A fully green AI-written suite means the tests pass — not that they ask anything
worth asking.

If every test is a variation of "does it work when everything is fine", that is not coverage.
Say so in the report rather than counting it.

## Classifying what this review finds

Use the standard classes in `SKILL.md`. This review does not get its own vocabulary:

| What you found | Class |
|---|---|
| Unhandled input a real user can supply | **Bug — edge/validation** |
| Swallowed exception that corrupts downstream state | **Bug — user-reachable**, if a user can reach the corruption |
| Unstated assumption that happens to hold today | **Potential** — until you can demonstrate the input that breaks it |
| Unflagged interpretation of an ambiguous requirement | **Requirement gap** |
| Green generated suite with no failure cases | Not a defect — a **coverage claim to reject**; report it as such |

The evidence taxonomy still governs. Reading a suspicious branch is **Confirmed (source)** only
with a `file:line` citation and a control check; anything you merely reasoned about stays
**Potential**.

## Before finishing

- Every function reviewed against its ugliest realistic input, not only its intended one.
- Every error path traced, not just the success path.
- The diff read once purely for unstated assumptions.
- At least one breaking test written and run for the behaviour you most doubted — or an
  explicit note that execution was unavailable.
- Generated tests judged on their assertions, never on their green.
- Nothing upgraded from **Potential** to a defect without the input that demonstrates it.
