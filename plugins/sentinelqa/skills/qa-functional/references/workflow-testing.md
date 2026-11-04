# Workflow / State Testing

Anything that moves through states — Draft → Submitted → Review → Approved → Completed — needs
testing as a **state machine**, not as a sequence of screens. Most workflow defects are transitions
nobody drew on the diagram.

## Build the transition matrix first

Rows = current state. Columns = attempted action. Each cell = expected outcome.

|  | Submit | Approve | Reject | Edit | Delete |
|---|---|---|---|---|---|
| **Draft** | → Submitted | ✗ blocked | ✗ blocked | ✓ allowed | ✓ allowed |
| **Submitted** | ✗ already | → Approved | → Rejected | ? | ? |
| **Approved** | ✗ | ✗ already | ? | ✗ | ✗ |
| **Rejected** | → Submitted? | ✗ | ✗ | ✓ ? | ? |
| **Completed** | ✗ | ✗ | ✗ | ✗ | ✗ |

**Every `?` is a requirement gap.** Requirements describe the forward path and go quiet about the
rest. Fill the matrix, then take the blanks to the requirement owner — this single artifact usually
surfaces more gaps than the rest of the analysis combined.

## What to test

### Valid transitions
Each forward move works, by the right role, and everything that should follow does: status updates,
timestamps recorded, actor recorded, notifications fired, next actor able to act, audit row written.

### Invalid transitions
Skipping a state · going backwards · acting on a terminal state. Must be blocked with a clear
message, and must leave state unchanged.

### Unauthorized transitions
The right action by the wrong role — see `role-permission-testing.md`. Blocked at the server, not
only hidden in the UI.

### Repeated transitions
Approve something already approved. Double-click Submit. Two reviewers approving simultaneously.
Watch for: duplicate side effects, duplicate emails, a second audit row, or a counter advanced twice.

### Backward transitions
Rejection → resubmission is the common one. Verify: what's editable after rejection · whether the
resubmitted item returns to the same reviewer · whether the rejection reason persists or clears ·
whether history shows both cycles.

### Editing after transition
Which fields stay editable in each state, and by whom. Editing an approved record is either
forbidden or must trigger re-approval — silently allowing it invalidates the approval.

### Interruption mid-transition
Refresh, navigate away, or lose the session while a transition is in flight. The record must land
in exactly one state — never half-transitioned.

## Concurrency

Two people acting on the same record at once. Routinely untested, and the failures are severe:

- Two approvers approve simultaneously → double advance? two notifications?
- One edits while another approves → is the approval against the old or new content?
- One deletes while another is mid-edit → clean error or crash?

At minimum, know whether the system detects the conflict or silently applies last-write-wins.
Silent last-write-wins on an approval workflow is worth reporting even if "working as designed".

## Routing and assignment

Where a workflow routes between actors (owner → reviewer → approver):

- Correct next actor per configuration
- What happens when the next actor is unset, inactive, or deleted
- What happens when the same person occupies two roles
- Whether the item appears in the right person's queue **and disappears from the previous one**
- Whether the previous actor can still act after handing off
- Delegation or substitute-approver paths, if any

## State visibility

For each state, confirm across the UI:

- Which fields are visible, editable, read-only
- Which actions are offered
- Which grid, tab, or queue the record appears in
- What the status label reads — and that it matches everywhere it's shown

A record showing "Submitted" in the list and "Draft" on the detail page is a real defect and an
easy one to miss, because each screen looks fine alone.

## Side effects per transition

Track for every transition, not just the final one:

| Transition | Status | Timestamp | Actor | Notification | Audit | Downstream |
|---|---|---|---|---|---|---|

Notifications are the usual casualty — fired twice, fired to the wrong person, or silently not
fired at all. An absent email produces no error anywhere; only an explicit test catches it.
