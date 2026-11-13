---
description: Hand a task to the Lead Test Automation Engineer subagent (bootstrap a repo, plan/build/run tests, investigate failures, draft bug reports)
---

Use the **lead-test-automation-engineer** subagent for the request below, honoring all of its rules — happy-path + full end-to-end first; propose negative/edge cases but confirm with me before automating them; real execution with evidence only (never claim a pass without it); investigate failures app-vs-test before calling anything a bug; and never create/file a ticket or push anything without my explicit confirmation.

Request:
$ARGUMENTS

**Before handing over (you, in this session, so the person is asked once and the subagent is never
blocked):** load the `sentinelqa:qa-functional` skill's start-of-run check and run it for this request:
`python <skill dir>/scripts/sentinelqa-setup.py match --cwd .` (with `--ticket <KEY>` if a ticket is
named), then `sentinelqa-setup.py preflight --cwd . [--ticket <KEY>] --env <ENV> --roles <roles the
tests need>`. If the session is not open in the project's folder (situation B), say where to open
Claude Code and stop. Put every `ask` item in ONE message, wait for the answers, save new facts to the
profile, then hand the subagent the project facts and answers. Never print a credential.
Before starting more than one subagent, give the one-line cost check from the skill's standing rules.

If no request is given above, bootstrap the current project — inspect its stack, test framework, existing tests, environments, and version-control rules — and report what you found plus a recommended next step, without changing anything.
