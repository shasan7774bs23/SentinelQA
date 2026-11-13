---
description: Add or update ONE project (the one in the current folder) in this machine's SentinelQA profile. Shortcut for /qa-setup when you only need one project. Never required.
---

Run the `/qa-setup` procedure for **only the project in the current folder**. Keep the machine
checks and the permission-rules question exactly as `/qa-setup` does them, if they are not settled yet.

Extra input (may be empty, may already hold answers, or `--yes`): $ARGUMENTS

1. Read the `/qa-setup` command's instructions (`${CLAUDE_PLUGIN_ROOT}/commands/qa-setup.md`) and
   follow them, with the questions limited to this one project (questions 4-11).
2. Inspect the folder first: git remote, recent branch names and commits (for the ticket prefix),
   manifest files (the stack), and whether its `CLAUDE.md` forbids writes (then it is `read-only`).
3. Save exactly as `/qa-setup` step 3 describes (write `~/.sentinelqa/import.json`, then `sentinelqa-setup.py import` that file),
   then `add-rules` if the rules are added. Every other saved project is kept.
4. Hand over: what was saved, and `/qa-functional <TICKET-KEY>` as the next step.

Never write a credential, never commit, never run a login command.
