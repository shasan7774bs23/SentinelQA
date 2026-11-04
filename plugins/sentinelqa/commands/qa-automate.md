---
description: Hand a task to the Lead Test Automation Engineer subagent (bootstrap a repo, plan/build/run tests, investigate failures, draft bug reports)
---

Use the **lead-test-automation-engineer** subagent for the request below, honoring all of its rules — happy-path + full end-to-end first; propose negative/edge cases but confirm with me before automating them; real execution with evidence only (never claim a pass without it); investigate failures app-vs-test before calling anything a bug; and never create/file a ticket or push anything without my explicit confirmation.

Request:
$ARGUMENTS

If no request is given above, bootstrap the current project — inspect its stack, test framework, existing tests, environments, and version-control rules — and report what you found plus a recommended next step, without changing anything.
