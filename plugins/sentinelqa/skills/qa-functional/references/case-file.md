# The QA Case File — the spine

One folder per ticket, committed to the repo. **Every station reads it. Every station writes to it.
Every gate stamps who decided what, and when.**

It is what makes the run durable: the two agents share state through it, the release gate reads it,
and a human can reconstruct months later what was tested, what was approved, and by whom. A finding
that exists only in a chat session is lost the moment the session ends.

```
qa/<TICKET-KEY>/
├── 00-intake.yml        tier · risk score · capability level · run context   (S0)
├── 01-requirement.md    rules · gaps · ambiguities · interview notes         (S1)
├── 02-plan.md           the test suite approved at Gate B                    (S2)
├── 03-pass1.md          codebase predictions — WRITE-ONCE                    (S3)
├── 04-evidence/         screenshots · traces · API responses · logs          (S3)
├── 05-report.md         the consolidated report and verdict                  (S4)
└── 06-decisions.md      APPEND-ONLY — every gate decision                    (all gates)
```

---

## The three rules that make it trustworthy

1. **`03-pass1.md` is WRITE-ONCE.** Codebase predictions are recorded with `file:line` citations
   *before* any live execution, timestamped, and never edited afterwards. A prediction edited after
   seeing the result is not a prediction — it is a rationalisation, and it destroys the entire value
   of the two-pass model.
2. **`06-decisions.md` is APPEND-ONLY.** A decision that turned out wrong is never deleted or
   rewritten; it is superseded by a new entry that says so. The trail is the point.
3. **The folder is committed.** Uncommitted, it is one disk failure from gone and invisible to
   everyone else. If the project forbids commits, say so in the report — the artifacts are weaker
   for it and the human should know.

## Per-file contract

| File | Written at | Template | Rule |
|---|---|---|---|
| `00-intake.yml` | S0 | `templates/intake.yml` | Tier and risk recorded with their reason. No tier = no run. |
| `01-requirement.md` | S1 | — | Rules in IF/THEN form, gaps named, interview notes attributed. |
| `02-plan.md` | S2 | `templates/qa-plan.md` | The complete suite. Frozen on Gate B approval; a change after approval is a **new revision** and goes back through the gate. |
| `03-pass1.md` | S3 | — | **Write-once.** Timestamped. Every prediction carries `file:line`. |
| `04-evidence/` | S3 | — | Real artifacts only. Never fabricated, never "attached" when it is not. |
| `05-report.md` | S4 | `templates/test-summary.md` | Plus the rendered `.html` — see the reporting standards. |
| `06-decisions.md` | every gate | `templates/decisions-log.md` | Append-only. Who, when, which artifact revision. |

## If the repo already has a convention

**Look first and match it.** Some repos keep per-ticket plans in `test-plan/` and QA
reports at the repo root as `<TICKET>-QA-Report.html`. Where a convention exists, follow it and note
in `00-intake.yml` where the artifacts actually live. The case file is a structure, not a demand
that you reorganise someone's repository.

## Resuming a run

Read **every** file in the folder before continuing, `06-decisions.md` included. Resume at the
station after the last recorded gate decision. **Never redo a gate that already passed, and never
reintroduce something the human rejected** — that is what the decisions log is for.
