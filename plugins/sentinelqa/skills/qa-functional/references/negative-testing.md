# Negative Testing

Verify the system behaves correctly when things go **wrong** — bad input, wrong order, wrong person,
failing dependency.

The point is not that the action is rejected. The point is **how**: the right thing is blocked, the
user is told clearly, state is unchanged, and they can recover. A rejection that corrupts data or
leaves a dead-end screen is still a defect.

## Input

| Case | Check |
|---|---|
| **Empty** | Required field left blank — blocked, named, no partial save |
| **Whitespace only** | Spaces should not satisfy a required field |
| **Wrong type** | Letters in a numeric field; text where a date is expected |
| **Wrong format** | `13/45/2026`, `not-an-email`, malformed phone or ID |
| **Out of range** | See `boundary-testing.md` |
| **Special characters** | `' " < > & \ / % _ ; --` and unicode/emoji |
| **Very long input** | Well past the limit — truncated silently, rejected, or error? |
| **Leading/trailing spaces** | Trimmed or preserved? Affects matching and duplicates |
| **Duplicate value** | Where uniqueness is required |
| **Invalid combination** | Each field valid alone, invalid together (end date before start) |

Two specifics worth always checking, because they're common and quiet:

- **Silent truncation** — input longer than the limit saved as a shortened value with no warning.
  A truncated case number or name is corrupted data that looks fine.
- **Client-only validation** — if the rule exists only in JavaScript, the server accepts anything
  that bypasses the form. Verify at Level 2 whether the server enforces it too. Classify a
  server-side gap as `Finding — system flaw`, not a user-facing bug.

## Unauthorized and unexpected actions

- Action attempted by a role that shouldn't have it → see `role-permission-testing.md`
- Action on a record the user doesn't own
- Action on a record in the wrong state (approve something already approved)
- Action on a deleted or archived record
- Direct navigation to a screen the user can't reach through the menu

## Real user behaviour

Not edge cases — this is what people actually do. Each deserves a case where it plausibly breaks:

| Behaviour | Failure it exposes |
|---|---|
| **Double-click Submit** | Duplicate records, duplicate emails, double-charged actions |
| **Browser Back after submit** | Stale form, resubmission, inconsistent state |
| **Refresh mid-action** | Lost input, half-saved record |
| **Two tabs, same record** | Last-write-wins silently overwriting the other tab |
| **Navigate away with unsaved changes** | Silent data loss, or a warning that doesn't appear |
| **Cancel** | Partial save left behind; state not rolled back |
| **Retry after an error** | Duplicate side effects from the first attempt |
| **Bookmark / direct URL** | Screen loads without required context, or leaks data |
| **Long idle, then submit** | Session expired mid-form — is input preserved? |

## System-level failure

| Condition | Expected |
|---|---|
| **Session expired** | Clean redirect to login; ideally input preserved; never a raw error |
| **API / integration failure** | Handled message, no data corruption, retryable |
| **Timeout** | User informed; no silently half-completed operation |
| **Missing dependent data** | Graceful message, not a crash or a blank screen |
| **Invalid state reached** | Blocked with an explanation |
| **Concurrent modification** | Detected, or last-write-wins — either way, know which and confirm it's intended |

## What a good error must do

Check all four for each negative case:

1. **Blocks the action** — nothing partial persisted.
2. **Names the problem** — which field, what's wrong, in plain language. Not "an error occurred".
3. **Is visible** — near the field or somewhere the user actually looks; not only in the console.
4. **Is recoverable** — they can fix it and continue without losing the rest of their input.

Losing an entire form because one field was wrong is a defect even when the rejection was correct.

## What a good error must *not* do — leak

A message can be clear, helpful, and still be a defect, because it answers a question the
user was not entitled to ask.

The classic: password reset with an unregistered email. "Email not found" is helpful and
wrong — it turns the reset form into a tool for discovering which addresses hold accounts.
The correct behaviour is an identical response either way: "If an account exists for this
address, a reset link has been sent." Same message, same timing, same status code.

Check the same way anywhere identity or ownership is involved:

| Message that leaks | What it reveals |
|---|---|
| "Email not found" on reset or login | Which addresses are registered |
| "Incorrect password" vs "user does not exist" | Valid usernames, one guess at a time |
| "Record 4471 belongs to another branch" | That the record exists, and whose it is |
| A stack trace, SQL text, or internal path | Implementation detail to an attacker |
| Noticeably faster failure for unknown users | The same answer, by timing |

Classify these as `Finding — system flaw` unless the requirement explicitly specifies the
message, in which case the requirement is what needs raising.

## Don't over-generate

Negative testing multiplies fast. Prioritise where failure actually costs something:
required fields on core flows, anything touching money, legal documents, permissions, or deletion.

Do **not** write forty cases proving the same validator rejects forty different bad strings.
One case per distinct rule and per distinct handling path.
