# Decisions log — `<TICKET-KEY>`

> Save as `qa/<TICKET-KEY>/06-decisions.md`. **APPEND-ONLY.** Never edit or delete an entry.
> A correction is a new entry that supersedes an earlier one and says so.
>
> This file is the audit trail of every human decision in the QA run. It is what makes
> "a human verified this" a checkable fact rather than a claim.

---

## Entry format

Every entry carries: **which gate · which round · when · who · what was decided · what changed · what
it applies to.** An approval with no artifact revision attached is not traceable and does not count.

---

## Gate A — Requirement sign-off

### Round 1 — `<YYYY-MM-DD HH:MM>` — `<APPROVED | REJECTED | CLARIFICATION REQUIRED>`
- **Reviewer:** `<name>`
- **Applies to:** `01-requirement.md` @ rev `<n>`
- **Interview:** `<conducted with <name> | not applicable (Tier 1) | owner unreachable>`
- **Decision / reason:** `<what was decided and why>`
- **Changed as a result:** `<rules added, removed, corrected — or "nothing">`
- **Open questions carried forward:** `<numbered, or "none">`

---

## Gate B — Plan approval

> One entry per round. On rejection, the agent corrects **only what was rejected** and re-presents with
> a diff. If three rounds do not converge, stop and reopen Gate A — that is a requirement problem, not
> a design problem.

### Round 1 — `<YYYY-MM-DD HH:MM>` — `REJECTED`
- **Reviewer:** `<name>`
- **Applies to:** `02-plan.md` @ rev 1 — `<n>` cases
- **Reject reasons** *(from the fixed vocabulary in `references/gate-protocol.md`)*:
  - `<TC-14..TC-19>` — duplicate equivalence class
  - missing dimension (state transition) — no case for `<scenario>`
- **Action taken:** `<removed 5 cases, added 3 workflow cases>` — diff presented `<yes/no>`

### Round 2 — `<YYYY-MM-DD HH:MM>` — `APPROVED`
- **Reviewer:** `<name>`
- **Applies to:** `02-plan.md` @ rev 2 — `<n>` cases, `<n>` marked JUDGMENT
- **Edits applied by reviewer:** `<verbatim list, or "none">`
- **Posted to ticket:** `<KEY>` comment id `<id>` — `<timestamp>`
- **Supersedes comment:** `<id, or "n/a — first post">`
- **Next:** S3 Execute. Plan is frozen; execution does not re-decide scope.

---

## Gate C — Defect validation

> One entry per candidate finding. The default answer is **not a defect**.

### `<finding short name>` — `<YYYY-MM-DD HH:MM>` — `<CONFIRMED DEFECT | NOT A DEFECT | NEEDS MORE EVIDENCE>`
- **Reviewer:** `<name>`
- **Evidence label:** `<Confirmed (reproduced) | Confirmed (source) | Observed | Potential>`
- **Control check:** `<does it also fail on an unaffected flow / a build without the change?>`
- **Class:** `<user-reachable | edge/validation | role-permission | system flaw | requirement gap | enhancement>`
- **Severity / Priority:** `<S1–S4>` / `<P0–P3>` — *set by:* `<name>`
- **Ledger:** `<new entry added | matched existing entry "<name>" — not re-raised>`
- **Reason:** `<why this verdict>`

---

## Gate D — Verdict &amp; filing

### `<YYYY-MM-DD HH:MM>` — Verdict `<READY | READY WITH KNOWN ISSUES | NOT READY | BLOCKED — CLARIFICATION REQUIRED>`
- **Signed by:** `<name>`
- **Applies to:** `05-report.md` @ rev `<n>`
- **Build:** `<build>` — *how confirmed:* `<how>`
- **Justification:** `<why this verdict and not the adjacent one>`
- **Filed to tracker** *(each item separately authorised)*:
  | Draft | Authorised by | Filed as |
  |---|---|---|
  | `<bug title>` | `<name>` | `<KEY or "not filed — reason">` |
- **Known issues accepted:** `<issue — accepted by <name>, or "none">`

---

## Autonomy changes

> Log any deviation from the tier's default autonomy modes, in either direction.
> Raising autonomy needs evidence across varied conditions. Lowering it needs no justification at all.

### `<YYYY-MM-DD>` — `<station>`: `<OHOTL → HITL>`
- **Set by:** `<name>`
- **Reason:** `<why>`
- **Evidence** *(required only when raising)*: `<golden-set score, Gate B rework rate, run history>`

---

## Corrections

> An earlier entry that turned out to be wrong is never edited. It is superseded here.

### `<YYYY-MM-DD>` — supersedes `<gate, round, date>`
- **What was wrong:** `<statement>`
- **What is correct:** `<statement>`
- **How established:** `<evidence>`
