# Two-Pass Verification — Codebase First, Then Execution

Verify from the **codebase first**, then execute, then **reconcile the two**. Never run the
application first and reason backwards from what you happened to see on screen.

Pass 1 tells you *where to look* and *what a correct result would even be*. With it, Pass 2 tests a
hypothesis. Without it, Pass 2 is wandering around a UI hoping something looks wrong.

---

## Pass 1 — Codebase verification

Work **bottom-up from the user interface outward**, not top-down from tests or module names. Tests
tell you what someone already thought of; the view tells you what a user can actually touch.

Read in this order:

1. **The view / template** — every control, one by one. Real labels, real field names.
   **Hunt for conditionally rendered sections** — anything behind a toggle, role check, feature flag
   or tab. These are where coverage is lost, because they are invisible until something enables them.
2. **Client-side script** — validation, request shape, how the response is consumed.
   A changed response shape with unchanged JS is a classic silent break.
3. **Entry point** — controller / route / handler. Permissions and guards attached to it.
4. **Business logic** — rules, branches, state transitions, defaults.
5. **Data layer** — what persists, constraints, what happens on reload.
6. **Existing tests** — what behaviour is already pinned. An assertion on current behaviour means
   it is intended, and your reading is the thing in doubt.
7. **The diff and commit intent** — what actually changed, and what the author meant to change.
8. **Config and feature flags** — what gates any of the above.

### Output of Pass 1 — record it before executing

| # | Area | Predicted behaviour | Predicted finding | Citation | Confidence |
|---|------|--------------------|-------------------|----------|------------|
| P1 | | What the code says will happen | Defect / correct / uncertain | `file:line` | High/Med/Low |

**Write this list down before Pass 2 begins, and do not revise it afterwards.** A prediction edited
after seeing the result is not a prediction — it is a rationalisation, and it destroys the entire
value of running two passes.

---

## Pass 2 — Live execution

Level 3 only. Execute the designed test cases and record what was **actually observed**, described
independently of Pass 1. Do not annotate observations with "as predicted" while capturing them —
capture first, compare second.

Capture real evidence: screenshots, responses, logs. Never invent any of it.

---

## Reconciliation

|  | **Pass 2: fails** | **Pass 2: passes** |
|---|---|---|
| **Pass 1 predicts defect** | ✅ **CONFIRMED** — strongest evidence available | ⚠️ **LATENT or MISREAD** — investigate |
| **Pass 1 predicts correct** | ⚠️ **BLIND SPOT or ENVIRONMENT** — investigate | ✅ **PASS** |

The two ⚠️ quadrants are the most valuable output of the whole exercise. Never quietly drop them.

### ✅ Both say broken — Confirmed
Highest confidence there is. Pass 1 hands you the root cause and the fix location for free — put
them in the technical footnote so dev starts from the answer, not from the symptom.

### ⚠️ Code says broken, app says fine
Do **not** discard it. Work through, in order:

1. **Is the path unreachable from the UI?** Dead code — report as tech debt, not a user bug.
2. **Is something upstream masking it?** e.g. client-side validation hiding a missing server check.
   Real, lower severity, and fragile — anything bypassing the client re-exposes it. Say that.
3. **Did I misread the code?** The most common answer. Re-read before concluding anything else.
4. **Is it conditional on data, role or config I didn't have?** State the condition that would fire it.

Report as **Potential (latent)** with the triggering condition. A defect that only fires on
production data is precisely what this pass exists to catch.

### ⚠️ Code says fine, app says broken
Do **not** jump to "environment issue". Work through, in order:

1. **Did I read the whole path?** A missed branch, override, filter, interceptor, or base class.
   This quadrant usually means Pass 1 was incomplete — not that the product is fine.
2. **Is the deployed build the build I read?** Check this early; it is the single most common cause.
3. **Data, config or environment specific?** Confirm on a second environment before saying so.
4. **A genuine source-vs-runtime gap?** Caching, stale artefact, unapplied migration, hand-edited config.

Only after all four may it be classified as an environment difference.

### ✅ Both say fine — Pass
Record that both passes agree. That is meaningfully stronger than either alone, and worth stating.

---

## Bias guards

- **Pre-register.** Pass 1 written down before Pass 2 runs. No retroactive edits.
- **Capture before comparing.** Record what you observed before checking it against the prediction.
- **A prediction is not a confirmation.** If you expected a failure and something merely looks odd,
  that is not evidence. Reproduce it properly or label it Observed.
- **Disagreements get reported, not resolved by preference.** Neither pass automatically wins.
- **Treat ⚠️ quadrants as open questions**, not resolved ones. If you cannot resolve one, say so.

---

## Degraded modes

| Situation | What to do |
|---|---|
| **No repo access** | Single-pass, execution only. State that no code verification was possible and that findings lack root-cause backing. |
| **No execution capability** | Single-pass, code only. Findings cap at **Confirmed (source)** — say plainly that live reproduction has not happened, and list the exact cases a human must run to close each one. |
| **Neither** | Design and analysis only. No findings may be reported as verified. |

Never present a single-pass result as if both passes agreed.

---

## Consolidated report section

```markdown
## Verification summary

**Pass 1 — codebase:** <n> areas examined, <n> predicted findings   (Level 2)
**Pass 2 — execution:** <n> cases executed on <env / build>          (Level 3)

| # | Finding | Pass 1 (code) | Pass 2 (live) | Verdict | Class |
|---|---------|---------------|---------------|---------|-------|
| 1 | | Defect predicted `file:line` | Reproduced 3/3 | CONFIRMED | Bug — user-reachable |
| 2 | | Defect predicted `file:line` | Not reproduced | POTENTIAL (latent) | needs <condition> |
| 3 | | No issue predicted | Failed | INVESTIGATE | build/env unconfirmed |

### Disagreements
<Every ⚠️ row, with what was checked and what remains open. Never omit this section —
if there were no disagreements, say so explicitly.>
```
