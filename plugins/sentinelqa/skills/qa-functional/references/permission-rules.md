# SentinelQA permission rules — set once per machine, apply to every project

Without these, Claude Code (in its default permission mode) asks before nearly every step of a QA
run: reading SentinelQA's own templates, saving each case-file file, running each audit script, each
browser action. These rules allow only what a QA run needs. Everything else still asks: every Jira
write, `git commit` / `git push`, the browser's `browser_run_code_unsafe`, and any other command.

**Where they go:** the `permissions.allow` list of the user settings file `~/.claude/settings.json`,
so they apply to every project. Merge them in and keep every existing entry. Never remove or change
anything else in that file. Only add them after the user says yes. Users of Claude Code's *auto*
permission mode do not need them.

`Edit(...)` rules cover creating files as well as editing them. Claude Code ignores `Write(...)` rules.
Relative paths such as `qa/**` are relative to the project you are working in, so one rule covers
every project.

```json
[
  "Read(~/.claude/plugins/cache/sentinelqa/**)",
  "Read(~/.claude/plugins/marketplaces/sentinelqa/**)",
  "Read(~/.claude/settings.json)", "Read(~/.sentinelqa/**)", "Edit(~/.sentinelqa/**)",
  "Edit(qa/**)", "Edit(.playwright-mcp/**)", "Bash(mkdir -p qa/*)",
  "Bash(python *sentinelqa*)", "Bash(py -3 *sentinelqa*)", "Bash(python3 *sentinelqa*)",
  "Bash(git status*)", "Bash(git log *)", "Bash(git diff *)", "Bash(git show *)",
  "Bash(git branch *)", "Bash(git ls-files*)", "Bash(git check-ignore *)", "Bash(git rev-parse *)",
  "mcp__claude_ai_Atlassian_Rovo__getJiraIssue", "mcp__claude_ai_Atlassian_Rovo__searchJiraIssuesUsingJql",
  "mcp__claude_ai_Atlassian_Rovo__getConfluencePage", "mcp__claude_ai_Atlassian_Rovo__getAccessibleAtlassianResources",
  "mcp__claude_ai_Atlassian_Rovo__searchConfluenceUsingCql",
  "mcp__claude_ai_Atlassian__getJiraIssue", "mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql",
  "mcp__claude_ai_Atlassian__getConfluencePage", "mcp__claude_ai_Atlassian__getAccessibleAtlassianResources",
  "mcp__claude_ai_Atlassian__searchConfluenceUsingCql",
  "mcp__atlassian__getJiraIssue", "mcp__atlassian__searchJiraIssuesUsingJql",
  "mcp__atlassian__getConfluencePage", "mcp__atlassian__getAccessibleAtlassianResources",
  "mcp__atlassian__searchConfluenceUsingCql",
  "mcp__plugin_sentinelqa_playwright__browser_navigate", "mcp__plugin_sentinelqa_playwright__browser_snapshot",
  "mcp__plugin_sentinelqa_playwright__browser_take_screenshot", "mcp__plugin_sentinelqa_playwright__browser_click",
  "mcp__plugin_sentinelqa_playwright__browser_type", "mcp__plugin_sentinelqa_playwright__browser_fill_form",
  "mcp__plugin_sentinelqa_playwright__browser_select_option", "mcp__plugin_sentinelqa_playwright__browser_press_key",
  "mcp__plugin_sentinelqa_playwright__browser_hover", "mcp__plugin_sentinelqa_playwright__browser_wait_for",
  "mcp__plugin_sentinelqa_playwright__browser_navigate_back", "mcp__plugin_sentinelqa_playwright__browser_tabs",
  "mcp__plugin_sentinelqa_playwright__browser_console_messages", "mcp__plugin_sentinelqa_playwright__browser_network_requests",
  "mcp__plugin_sentinelqa_playwright__browser_network_request", "mcp__plugin_sentinelqa_playwright__browser_handle_dialog",
  "mcp__plugin_sentinelqa_playwright__browser_resize", "mcp__plugin_sentinelqa_playwright__browser_close",
  "mcp__playwright__browser_navigate", "mcp__playwright__browser_snapshot",
  "mcp__playwright__browser_take_screenshot", "mcp__playwright__browser_click",
  "mcp__playwright__browser_type", "mcp__playwright__browser_fill_form",
  "mcp__playwright__browser_select_option", "mcp__playwright__browser_press_key",
  "mcp__playwright__browser_hover", "mcp__playwright__browser_wait_for",
  "mcp__playwright__browser_navigate_back", "mcp__playwright__browser_tabs",
  "mcp__playwright__browser_console_messages", "mcp__playwright__browser_network_requests",
  "mcp__playwright__browser_network_request", "mcp__playwright__browser_handle_dialog",
  "mcp__playwright__browser_resize", "mcp__playwright__browser_close"
]
```

HTTP checks against a test environment (`curl`) still ask the first time in each session. A rule
like `"Bash(curl *qa.example.com*)"` for your own test host removes that. Never add a production host.
