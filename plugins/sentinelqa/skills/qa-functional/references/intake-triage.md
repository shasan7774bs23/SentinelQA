# S0 — Intake &amp; Triage

The first station. Two minutes. It answers: **what are we testing, where, as whom — and how much
QA does this change deserve?**

Output: `qa/<TICKET-KEY>/00-intake.yml` (see `templates/intake.yml`).

> **The tier scales rigor, never gates.** All five gates fire on every ticket — a human signs off
> the rules, the plan, each defect, the verdict, and the release, regardless of tier. What the tier
> changes is how much *testing* the change earns, not how much *human judgement* it gets.

---

## Hard rules

1. **Triage before analysis.** The tier decides how much of the pipeline runs. Deciding it afterwards is
   just rationalising the effort you already spent.
2. **Tier up on doubt, never down.** If a change sits between two tiers, it is the higher one.
3. **The tier is recorded, with its reason**, in `00-intake.md`. An unrecorded tier is not a decision.
4. **Only a human lowers a tier.** The agent may raise one on new evidence at any point; lowering is a
   human decision and is logged in `06-decisions.md`.
5. **A Tier 3 signal outranks a low risk score.** The score is a guide; the signals below are a floor.

---

## Step 1 — Confirm the run context (ask if missing)

Six facts, confirmed before anything else. Never assumed, never inferred.

| # | Fact | Why it is not optional |
|---|---|---|
| 1 | **Ticket number** | Every case, defect and report line traces to it |
| 2 | **Branch**, and whether it is merged | Tells you which source Pass 1 reads |
| 3 | **Deployed site** — the environment URL under test | There is more than one; behaviour and fixtures do not transfer |
| 4 | **The build actually deployed there, and how you confirmed it** | **The most expensive assumption in this process.** A branch containing the fix does not mean the environment runs it. |
| 5 | **Test account and role** for the flows in scope | A missing permission is a blocked flow, not a defect |
| 6 | **First pass or re-test** — if a re-test, the fix commit/PR | A re-test verifies a specific change |

**If any is missing, ask — one short numbered list — before testing.** As a subagent, do whatever
does not depend on the missing fact and return `BLOCKED — CLARIFICATION REQUIRED`.

- **Never infer the deployed build from the branch.** Confirm from the running application and
  record how.
- **Environment down or wrong build → `BLOCKED`, never `FAIL`.**
- **Permission the account lacks → `BLOCKED` for that flow**, with the permission named.

## Step 2 — Stakes tier

Highest matching signal wins. These are a floor, not a suggestion.

| Tier | Signals |
|---|---|
| **3 — High stakes** | Authentication / authorization / SSO · payments or financial calculation · data migration or schema change · permissions and role surfaces · deletion or irreversible transitions · production data · security-relevant configuration · anything that cannot be rolled back within one release cycle |
| **2 — Normal** | Business logic · new feature or endpoint · workflow or state-machine change · report or export content · anything with an observable acceptance criterion |
| **1 — Trivial** | Label, copy or translation text · styling with no layout logic · config toggle with an obvious revert · dependency bump with no API change · test-only change |

**Escalators — any one raises the tier by one, max 3:**

- The change touches a module with an open entry in the known-findings ledger
- The same area produced a defect in the last two releases
- The requirement needed the Gate A interview to become clear
- More than one ticket in this release touches the same module
- The implementation was substantially AI-generated

## Step 3 — Risk score

Both axes 1–5. `risk = likelihood × blast radius` (1–25). Used to rank effort across a release.

**Likelihood** — 1: one-line change in well-covered code · 3: new logic or thin coverage ·
5: no clear requirement, no coverage, or a pattern that has failed here before.

**Blast radius** — 1: one screen, visibly wrong and instantly fixable · 3: a module several
features depend on · 5: everyone, silently — data corruption, authorization bypass, financial error.

**Blast radius matters more than file count.** A one-line change to a shared authorization helper
is a 5. A 400-line change to one isolated screen is a 2. Trace the callers, not the diff.

## Step 4 — What the tier changes

| | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Gate A interview | Optional | **Required** | **Required** + a second reader |
| Suite scope | Happy path + the changed behaviour | Full design: happy, negative, boundary, workflow, role, regression | Full design + exploratory session |
| Pass 1 depth | The changed lines | Full, with `file:line` predictions | Full, plus every caller of the changed symbol |
| Regression set | Smoke + the directly affected area | + adjacent areas | Full regression |
| Rollback criterion in the plan | — | — | **Required** |
| **Gates A · B · C · D · E** | **All fire** | **All fire** | **All fire** |

The bottom row is the point. Rigor scales; **the gates never do.** The defect call, the verdict and
the release decision stay human at every tier, with no exception and no "it was only a Tier 1" argument.

## Step 5 — Capability level

State it plainly: **1** Analysis (ticket text only) · **2** Investigation (+ repo, code, logs) ·
**3** Execution (+ a real browser / API / DB tool, named). Never infer a capability you cannot name.

---

## Step 6 — Autonomy mode per station

Record the mode alongside the tier. See `gate-protocol.md` for what each mode means in practice.

| Station | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| S0 Intake &amp; triage | AHOTL | OHOTL | HITL |
| S1 Understand &rarr; Gate A | OHOTL | HITL | HITL + second reader |
| S2 Design &rarr; Gate B | OHOTL | HITL | HITL, named approver |
| S3 Execute | AHOTL | OHOTL | OHOTL + human exploratory |
| S3 Defect validation &rarr; Gate C | **HITL** | **HITL** | **HITL** |
| S4 Verdict &amp; filing &rarr; Gate D | **HITL** | **HITL** | **HITL** |
| S5 Release go/no-go &rarr; Gate E | **HITL** | **HITL** | **HITL**, named in report |

**This table is a default, not a law.** The human may set any cell to HITL at any time, for any reason,
including "I want to watch this one." Raising a cell's autonomy needs the opposite: evidence that it has
been safe across varied conditions, including ambiguous and partially-failing cases. One good run is not
evidence. Lowering autonomy again is normal, not a failure.

---

## Never do

- Assign a tier without recording the reason in `00-intake.yml`.
- Lower a tier because the work looks like a lot. Only a human lowers a tier, and it is logged.
- Use the risk score to override a Tier 3 signal — the signals are a floor.
- Skip a gate because the tier is low. **The tier never gates the gates.**
- Treat "the developer said it's a small change" as a tier. Developers size effort, not blast radius.

## Output

Write `qa/<TICKET>/00-intake.md` using `templates/intake.md`, then continue to S1.

