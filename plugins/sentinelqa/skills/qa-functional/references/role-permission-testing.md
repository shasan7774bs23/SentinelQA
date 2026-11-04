# Role & Permission Testing

Two independent questions, and conflating them is the classic mistake:

1. **Action permission** — *may this role perform this action at all?*
2. **Data scope** — *on which records?* Own · team · organisation · all

A user may be allowed to edit cases (action) but only their own (scope). Testing only the first
misses the entire second category, which is where the serious defects live.

> Findings here are class **`Finding — role/permission`**. Report them separately from the
> user-facing bug list — different audience, different fix path. Filing is the user's decision.

## Action matrix

Rows = role. Columns = action. Build it and fill every cell.

|  | View | Create | Edit | Delete | Submit | Approve | Reject | Export |
|---|---|---|---|---|---|---|---|---|
| Role A | | | | | | | | |
| Role B | | | | | | | | |

Each cell: **allowed** / **denied** / **conditional** (state the condition).
Blank cells are requirement gaps — requirements rarely enumerate the full matrix.

## Data-scope matrix

Then, for every *allowed* cell, establish the scope:

| Scope | Meaning |
|---|---|
| **Own** | Records they created or are assigned |
| **Team / department** | Their unit's records |
| **Organisation** | Everything in their org |
| **Associated** | Records of linked accounts or partner orgs |
| **All** | System-wide |

Test each scope with a record **just outside** it — the neighbouring department, the other
organisation, another user's record. Inside-scope access working proves nothing about the boundary.

## How denial should manifest

Confirm which of these the requirement intends, then verify it's consistent:

| Manifestation | Appropriate when |
|---|---|
| **Control hidden** | The role never has it — cleanest |
| **Control visible but disabled** | Contextually unavailable; a tooltip should say why |
| **Error on attempt** | Discovered only at submit |
| **Record not listed** | Out of data scope |
| **404 / not found** | Out of scope, and existence itself is sensitive |

Inconsistency is itself a finding: hidden on one screen, an error on another, and silently
permitted on a third means the rule lives in three places and one of them will drift.

## Beyond the UI

Hiding a button is presentation, not enforcement. Where it matters, verify the rule holds underneath:

- Is the action gated on the **server**, or only in the view?
- Does a **direct URL** to the record work for someone out of scope?
- Are records filtered in the **query**, or fetched and hidden in the browser?
- Do **exports, reports and downloads** apply the same scope as the screen they're launched from?

At Level 2 this is read from the code — check the handler's authorization attribute and the query's
filter, not just the template. A UI-only gate is `Finding — system flaw`.

Export and download endpoints are the most frequent gap: the grid filters correctly, and the export
button next to it returns everything.

## Special cases

| Case | Check |
|---|---|
| **Own record vs others'** | Often the only difference that matters |
| **Multi-role users** | Which wins — most permissive, or most restrictive? Verify the intent |
| **Admin / superuser** | Does an override bypass rules it shouldn't (PII masking, audit)? |
| **Inactive or locked user** | Access revoked immediately, or on next login? |
| **Role changed mid-session** | Does the existing session keep the old permissions? |
| **Delegation / impersonation** | Whose permissions apply, and whose name lands in the audit trail? |
| **Unauthenticated** | Redirect to login — never a partial render or a data leak |

## Data masking vs absence

Distinguish carefully, because they look identical on screen:

- **Masked** — the record is visible, a sensitive field is blanked or redacted **by design**
- **Absent** — the data was never saved, or was lost

A field reading empty is *not* evidence of a data defect until you've confirmed masking isn't the
cause. Mistaking a working privacy rule for a persistence bug is a classic false report — check the
underlying value at Level 2 before concluding anything.

## Test accounts

Use real accounts for each role, by label, never passwords. Where a role can't be provisioned,
mark those cases **Blocked** with the exact provisioning needed — don't quietly drop the row and
present the matrix as complete.
