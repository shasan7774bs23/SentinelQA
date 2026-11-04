# QA Test Plan — `<TICKET-KEY>`

> `qa/<TICKET-KEY>/02-plan.md` — the artifact approved at **Gate B** (end of station S2) and posted
> to the ticket on approval. Once approved it is frozen; execution runs it and does not re-decide
> its scope. A change after approval is a **new revision** and goes back through Gate B.
> See `references/gate-protocol.md`.

| Field | Value |
|---|---|
| Ticket | `<KEY>` — `<title>` |
| Revision | `<N>` |
| Status | `DRAFT` · `AWAITING APPROVAL` · `APPROVED` · `SUPERSEDED BY REV <N>` |
| Tier / risk | Tier `<1–3>` · risk `<1–25>` *(from `00-intake.yml`)* |
| Capability level | `<1 Analysis | 2 Investigation | 3 Execution>` |
| Build under test | `<build>` — *how confirmed:* `<how>` |
| Self-review | run in a fresh context at `<model tier>` on `<date>` |
| Approved by / on | `<name>` / `<date>` |

---

## 1. ⛔ NOT covered — read this first

Separate *blocked* (could not test) from *out of scope* (chose not to). They are different
decisions with different owners. If this section is empty, say so explicitly.

| Area | Blocked or out of scope? | Reason |
|---|---|---|
| `<area>` | `<blocked / out of scope>` | `<why>` |

## 2. Coverage summary

| Type | Cases |
|---|---|
| Happy path | `<n>` |
| Negative / invalid input | `<n>` |
| Validation | `<n>` |
| Boundary | `<n>` |
| Workflow / state transition | `<n>` |
| Role / permission | `<n>` |
| Regression | `<n>` |
| **Total** | **`<n>`** |

## 3. Business rules under test

Every case traces to a rule. A case with no rule is padding or an undocumented rule — raise it,
do not keep it.

| Rule | IF / THEN | Source | Cases |
|---|---|---|---|
| BR-1 | `<IF … THEN …>` | `<AC ref / requirement line>` | TC-1, TC-4 |

## 4. Test cases

The **complete** set — not a sample. One reason to fail per case. Status stays `Not Executed`
until genuinely executed. Full field list in `templates/test-case.md`.

### TC-`<n>` — `<title>`

| Field | Value |
|---|---|
| Traces to | `<BR-n>` |
| Type | `<happy / negative / validation / boundary / workflow / role / regression>` |
| **Assertion kind** | **`HARD`** (machine-checkable pass/fail) · **`JUDGMENT`** (needs a human eye) |
| Priority | `<P0–P3>` |
| Preconditions | `<state, data, role>` |
| Test data | `<values — never a secret, never production data>` |

**Steps**
1. `<one UI action per step, plain language a non-technical reader can follow>`

**Expected:** `<behaviour>` — *derived from:* `<BR-n / AC ref>`
> Derived from the requirement, never from watching the app. A result taken from the app
> documents the bug instead of finding it.

**Status:** `Not Executed`

---

## 5. Hard assertions ⟡ qualitative judgments

Stated separately so the executor knows which is which — and so the report can too. A `JUDGMENT`
case must never be converted into a machine assertion; that turns "someone should look at this"
into a green tick.

**Hard assertions** — pass/fail without interpretation:
- `<TC-n: the assertion>`

**Qualitative judgments** — require a human to look and decide, against what standard:
- `<TC-n: what a human must judge, and the standard>`

## 6. Known traps

Tied to the individual steps they endanger, not listed generically.

| Trap | Which step it endangers | Source |
|---|---|---|
| `<e.g. grid default sort uses an unsafe CAST>` | `<TC-7 step 3>` | `<ledger entry / interview / Pass 1>` |

## 7. Test data

| Data | How obtained | Cleanup | Expires? |
|---|---|---|---|
| `<item>` | `<reuse approved / create unique>` | `<how>` | `<yes/no>` |

## 8. Regression scope

| Area | Why it is in scope |
|---|---|
| `<module>` | `<shared schema / shared permission surface / direct caller>` |

## 9. Execution plan

| Layer | Cases | Who runs it |
|---|---|---|
| Existing automated suite | `<TC refs>` | `lead-test-automation-engineer` |
| New automation (build only after approval) | `<TC refs>` | `lead-test-automation-engineer` |
| Manual | `<TC refs>` | `<name>` |

---

## 10. Rollback criterion *(Tier 3)*

| Field | Value |
|---|---|
| Signal to watch after release | `<named metric, log, or error signature>` | 
| Threshold that triggers rollback | `<value>` |
| Watch window | `<e.g. 24h>` |
| Who watches | `<name>` |

---

## Approval record

| Revision | Decision | By | Date | Posted to ticket |
|---|---|---|---|---|
| 1 | `<APPROVED / REJECTED>` | `<name>` | `<date>` | `<comment id or —>` |

**If rejected:** record which cases and why, using the reject vocabulary in
`references/gate-protocol.md`. Correct only what was rejected, note what changed, and present the
next revision.
