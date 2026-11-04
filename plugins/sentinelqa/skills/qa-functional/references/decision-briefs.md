# Decision briefs — how anything needing a human decision is presented

Applies to every QA agent and the main session alike — whenever you hand the human something to
**read, decide, confirm or approve** (open findings, tickets to file, risky runs, clarification
questions, release calls). Goal: they can read it once and decide without asking a follow-up.

**Order:** status first (what is done and verified) → corrections to your own earlier claims →
one block per item → a closing **"Your decisions"** checklist, one line per decision.

**Each item carries:**
1. **Plain-English title** naming the problem as a user would notice it (the internal ID goes after, not instead).
2. **What a user sees** — the symptom, in steps.
3. **Why, and whose it is** — app / environment / test / data, with the reasoning. File:line and code detail go in a developer row or footnote, never in the main text.
4. **Evidence** — dates, how many times reproduced, by whom (hand / suite), screenshot names.
5. **Impact** — who is blocked, what is red.
6. **Owner + what they need** — and when someone else must act, a **ready-to-paste message** for them.
7. **For any risky action, a table:** what it does · side effects (emails, permanent data, locks, accounts touched) · can it be undone.
8. **Your recommendation and why** — one recommendation, not a menu with no opinion.
9. **What you need from the human** — exact fields/answers, so nothing has to be asked twice.

**Style:** plain English, no unexplained jargon; tables when comparing options; concise — detail
earns its place by changing the decision. Never act on an item before the human's explicit answer to it.
