#!/usr/bin/env node
/**
 * PreToolUse hook — gates git write/remote operations and gh write commands
 * behind an approve/deny prompt.
 *
 * Enforces the standing rule: never commit, push, or take an outward action
 * without explicit confirmation. Returns permissionDecision "ask", so each
 * matched command surfaces a prompt rather than a hard block — approval is
 * per-action and never carries forward. Read-only git (status/log/diff/show/
 * blame/merge-base/branch --list) stays allowed so investigation works.
 *
 * Escape hatch: deny the prompt and run it yourself with a leading `!`.
 *
 * Opt-in: see README "Optional: git-write guard" for the settings.json entry.
 * Matcher "Bash|PowerShell" — BOTH shells must be covered; matching only Bash
 * left git writes reachable through the PowerShell tool.
 */

const RULES = [
  // --- git: history / remote / index writes -------------------------------
  // NOTE: `merge\b(?!-)` so read-only `git merge-base` (needed for diff analysis) is NOT blocked.
  [/\bgit\b(?:\s+(?:-[a-zA-Z]\s+\S+|--?[\w-]+(?:=\S+)?))*\s+(commit|push|rebase|cherry-pick|revert|merge\b(?!-)|am|apply|filter-branch|filter-repo|update-ref|fast-import|commit-tree|replace)\b/i,
    'git history/remote write'],
  [/\bgit\b(?:\s+(?:-[a-zA-Z]\s+\S+|--?[\w-]+(?:=\S+)?))*\s+add\b/i,
    'git add (staging)'],
  [/\bgit\b[^;&|]*\breset\b[^;&|]*--(hard|soft|mixed|merge|keep)\b/i,
    'git reset (moves HEAD / discards work)'],
  [/\bgit\b[^;&|]*\bclean\b[^;&|]*\s-[a-zA-Z]*[fdx]/i,
    'git clean (deletes untracked files)'],
  [/\bgit\b[^;&|]*\bremote\b[^;&|]*\b(add|remove|rm|set-url|rename|prune|set-head|set-branches)\b/i,
    'git remote modification'],
  [/\bgit\b[^;&|]*\bbranch\b[^;&|]*\s-(d|D|m|M|c|C)\b/i,
    'git branch create/delete/rename'],
  [/\bgit\b[^;&|]*\b(checkout\s+(-b|--orphan)|switch\s+(-c|--create))\b/i,
    'git branch creation'],
  [/\bgit\b[^;&|]*\btag\b(?![^;&|]*(--list|--contains|--points-at|\s-l\b|\s-n))/i,
    'git tag creation/deletion'],
  [/\bgit\b[^;&|]*\bstash\b[^;&|]*\b(push|pop|drop|clear|save|apply|store)\b/i,
    'git stash write'],
  [/\bgit\b[^;&|]*\breflog\b[^;&|]*\b(delete|expire)\b/i,
    'git reflog rewrite'],
  [/\bgit\b[^;&|]*\bworktree\b[^;&|]*\b(add|remove|move|prune)\b/i,
    'git worktree modification'],
  [/\bgit\b[^;&|]*\bsubmodule\b[^;&|]*\b(add|update|deinit|set-url)\b/i,
    'git submodule modification'],
  [/\bgit\b[^;&|]*\bconfig\b(?![^;&|]*(--get|--list|\s-l\b))/i,
    'git config write'],

  // --- gh: anything that writes to GitHub ---------------------------------
  [/\bgh\s+(pr|issue|release|repo|secret|variable|workflow|gist|label|ruleset|cache|run|project|codespace)\s+[\w-]*\s*\b(create|delete|edit|merge|close|reopen|comment|review|ready|rename|transfer|archive|lock|unlock|pin|unpin|approve|set|upload|run|dispatch|enable|disable|sync|restore)\b/i,
    'gh write command (creates/changes something on GitHub)'],
  [/\bgh\s+api\b[^;&|]*(-X|--method)\s*(POST|PUT|PATCH|DELETE)\b/i,
    'gh api write request'],
];

let raw = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { raw += chunk; });
process.stdin.on('end', () => {
  let command = '';
  try {
    command = ((JSON.parse(raw) || {}).tool_input || {}).command || '';
  } catch {
    process.exit(0); // unparseable input -> never block
  }
  if (!command) process.exit(0);

  const hit = RULES.find(([pattern]) => pattern.test(command));
  if (!hit) process.exit(0);

  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'ask',
      permissionDecisionReason:
        `CONFIRM — ${hit[1]}.\n\n` +
        `Nothing is committed, pushed, or sent outward without your explicit ` +
        `confirmation. Approve to run it, or deny to stop.\n\n` +
        `Approval covers THIS action only — a yes never carries to the next one. ` +
        `To run it yourself instead, deny and use a leading "!" in the input box.`,
    },
  }));
  process.exit(0);
});
