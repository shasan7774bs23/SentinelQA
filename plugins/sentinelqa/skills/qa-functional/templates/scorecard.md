# QA Process Scorecard — `<MONTH YYYY>`

> Derived from the case files under `qa/` plus the known-findings ledger. One page, monthly.
> **Never put line coverage or raw pass rate on this scorecard** — they are the vanity metrics the
> method deliberately rejects.

| Field | Value |
|---|---|
| Period | `<YYYY-MM-01>` → `<YYYY-MM-31>` |
| Releases shipped | `<n>` |
| Tickets QA'd | `<n>` (Tier 1 `<n>` · Tier 2 `<n>` · Tier 3 `<n>`) |
| Compiled by / on | `<name>` / `<date>` |

---

## The two that matter most

| Metric | This month | Last month | Direction | Target |
|---|---|---|---|---|
| **Escaped defect rate** — UAT/prod defects ÷ total found | `<n%>` | `<n%>` | ↓ | `<n%>` |
| **Mutation score on changed code** — Stryker, PR-scoped | `<n%>` | `<n%>` | ↑ | `<n%>` |

> Escaped defect rate is the north star: passing tests prove nothing if bugs still reach users.
> Mutation score is the only honest answer to *do these tests detect anything*.

## Process health

| Metric | This month | Last month | Direction | Note |
|---|---|---|---|---|
| **Gate B rework rate** — % of plans materially changed at approval | `<n%>` | `<n%>` | ↓ | The trust metric. Falling = the agent is earning autonomy. A jump right after an agent edit means the edit regressed it. |
| Gate B rounds to approval (median) | `<n>` | `<n>` | ↓ | 3+ repeatedly = requirements are unclear, not design |
| Mean time to detect — commit → defect found | `<n>` days | `<n>` | ↓ | Measures shift-left, not volume |
| **Human minutes per ticket** | `<n>` | `<n>` | ↓ | The efficiency number. Climbing without escape rate falling = ceremony, not quality |
| Ledger hit rate — candidate findings matched to an existing entry | `<n%>` | `<n%>` | ↑ | Is institutional memory actually being reused? |
| Assurance gap — % of acceptance criteria that could not be verified | `<n%>` | `<n%>` | ↓ | The honest version of coverage |

## Suite health

| Metric | This month | Last month | Note |
|---|---|---|---|
| Flake rate — flake-adjusted pass rate | `<n%>` | `<n%>` | Never the raw pass rate |
| Tests quarantined | `<n>` | `<n>` | Quarantined tests **do not count as coverage** |
| Oldest quarantine | `<n>` days — `<test>` — owner `<name>` | | A quarantine with no owner or date is a deleted test with extra steps |

## Agent assurance

| Field | Value |
|---|---|
| Last golden-set run | `<date>` · score `<n>/100` · previous `<n>/100` |
| Triggered by | `<which agent/skill edit>` |
| Weakest axis | `<axis>` — `<what to fix>` |
| Autonomy changes this month | `<station: HITL → OHOTL, with the evidence>` or `none` |

## Coverage of the period

| Bucket | Count | Note |
|---|---|---|
| Tickets with an executed QA report | `<n>` | |
| Tickets with analysis only (never executed) | `<n>` | Counts as **unknown**, never as a pass |
| Tickets with **no** QA report | `<n>` | The headline number if it is not zero |
| Blocked, with reason | `<n>` | Each reason carried forward, never netted out |

---

## What changed, and what to do about it

**Moved in the right direction:** `<metric — why, if known>`

**Moved in the wrong direction:** `<metric — suspected cause>`

**Actions for next month:**
1. `<action>` — owner `<name>`

**Decisions needed from leadership:** `<or "none">`

---

## Not on this scorecard, deliberately

Line coverage · raw pass rate · test count · number of test cases written · automation percentage.
Every one of them can improve while quality gets worse. If someone asks for them, give them the
escape rate instead and explain why.
