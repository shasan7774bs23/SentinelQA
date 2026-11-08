---
description: Same as /qa-functional — open or resume a QA case file for a ticket and run the full method, including live testing
---

*(`/qa-functional <TICKET-KEY>` is the main way to start a run; this command is the same thing with the
run instructions spelled out.)*

Load the **`sentinelqa:qa-functional`** skill (Skill tool, exactly that name) and run the method for
the ticket below, working inside its case file at `qa/<TICKET-KEY>/` in the current folder.

Ticket: $ARGUMENTS

If no ticket key is given, list the case files already present under `qa/` with the gate each one is
waiting at, and ask which to resume. Do not start a new one.

## How to run it

**If the case file does not exist**, create it and start at S0.

**If it already exists**, read every file in it first, including `00-intake.yml` and
`06-decisions.md`. It may have been started by the `qa-functional` subagent. Resume at the station
after the last recorded gate decision. Never redo a gate that has already been passed, never
reintroduce something I rejected, and **never re-ask anything already answered in `00-intake.yml`**.

## Start of the run: one message from you, then work

1. **Dependency check (the skill's Step 00), silently first.**
   - **Ticket:** use whichever Jira tool exists (Atlassian Rovo, Atlassian, or a local Atlassian
     server). Fetch the description, **all comments**, linked tickets and the attachment list.
   - **Attachments:** download them with `jira-attachments.py` if Jira credentials are set.
   - **Everything else:** look for the source code, the environment, the accounts, a browser tool
     and Python. Use the project layer from `/qa-init` where it exists.
2. **Then ONE batched message** holding:
   - every missing dependency, as *"Will you provide it? (yes → how / no)"*;
   - the run-context facts still unknown;
   - the up-front inputs.
   Nothing that was found goes in it. If nothing is missing, say so in one line and continue.
3. **After my answer, continue with what exists.** A "no" is never a stop. Record each answer in
   `00-intake.yml` → `dependencies` and work around the gap as the skill's Step 00 table says.
4. **Source code not available to QA:** once I confirm it, continue without it. Pass 1 is
   requirement-based and write-once; Pass 2 tests everything reachable live (UI through the
   browser, HTTP and API, roles, boundaries, neighbouring features).
5. **Everything available:** run the whole method.

Never ask me to log in or re-authenticate, and never run a login command. A connector that needs
authentication counts as missing.

## Non-negotiables for this run

- **Load the project's `CLAUDE.md` / `CLAUDE.local.md` and `.claude/qa/known-findings.md` before
  analysis.** Check every candidate finding against the ledger; a match is reported as **Known** and
  not re-raised.
- **Keep `qa/` out of git:** write `qa/.gitignore` and `.playwright-mcp/.gitignore`, each containing
  `*`. Skip this only if the project layer says QA files are committed.
- **`03-pass1.md` is write-once.** Record predictions before any live execution, and never edit them
  afterwards. Use `file:line` when you have the code; with no code, base them on the requirement and
  label the basis.
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
- Never mark a test Pass or Fail without execution evidence. Unexecuted is `Not Executed`, with the
  blocker named.

Tell me at the end which gate we are at and what you need from me to move.
