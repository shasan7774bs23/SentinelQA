---
description: Open or resume a QA case file for a ticket and run the V2 method (S0 triage → gates → report)
---

Load the **`qa-functional`** skill and run the V2 method for the ticket below, working inside its
case file at `qa/<TICKET-KEY>/` in the current repo.

Ticket: $ARGUMENTS

If no ticket key is given, list the case files already present under `qa/` with the gate each one is
waiting at, and ask which to resume. Do not start a new one.

## How to run it

**If the case file does not exist**, create it and start at S0:
`00-intake.yml` (use `templates/intake.yml`) → stakes tier, risk = likelihood × blast radius,
capability level, autonomy modes. Triage *before* analysis — the tier decides how much of the
method runs.

**If it already exists**, read every file in it first — including `06-decisions.md` — and resume at
the station after the last recorded gate decision. Never redo a gate that has already been passed,
and never reintroduce something I rejected.

## Non-negotiables for this run

- **Load the project's `CLAUDE.md` and `.claude/qa/known-findings.md` before analysis.** Check every
  candidate finding against the ledger; a match is reported as **Known** and not re-raised.
- **`03-pass1.md` is write-once.** Record codebase predictions with `file:line` before any live
  execution, and never edit them afterwards.
- **`06-decisions.md` is append-only.** Every gate decision goes in with who, when, and which
  artifact revision it applies to.
- **Gate B:** design the **complete** suite for the tier — never a sample. Self-review it in a fresh
  context before presenting. Present coverage, hard assertions ⟡ qualitative judgments, rule→case
  traceability, and what is **not** covered. Then stop and wait for me.
- **On reject:** correct only what I rejected, show a diff, re-present. Three non-converging rounds
  means the requirement is unclear — reopen Gate A and say so.
- **On approve:** freeze the revision, then post the plan to the ticket as a comment — *you* post it
  from this session after my approval; never from a subagent, never as anything but an added comment,
  and a revised plan is a new comment that supersedes the old one.
- **Gates C, D and E are mine at every tier.** Draft the defect calls, the verdict and any ticket
  content, then wait. Nothing reaches Jira without my explicit yes, per item.
- Never mark a test Pass or Fail without execution evidence. Unexecuted is `Not Executed`.

Tell me at the end which gate we are at and what you need from me to move.
