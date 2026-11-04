# Requirement Analysis

Goal: understand what is being asked **precisely enough to test it**, and find everything that isn't
stated. What's missing matters more than what's written.

## First: what kind of requirement were you handed?

The reading order below assumes a ticket. Requirements arrive in other shapes, and each shape has
its own blind spot. Identify the source before you start extracting.

| Source | Read it for | Its usual blind spot |
|---|---|---|
| **Jira / ADO ticket** | Description, AC, comments, attachments, links, history | Scope that lives only in comments |
| **BRD / FRD / SRS** | Numbered requirements, business context, referenced annexes | Written for sign-off, not for testing — validation rules and error behaviour are usually absent |
| **API spec** (Swagger/OpenAPI, Postman collection) | Endpoints, required fields, types, enums, response codes | Documents the contract, never the business rule behind it — and error responses are often aspirational |
| **Figma / mockup / screenshot** | Field labels, states, empty and error states shown | Silent on rules, permissions and persistence; a mockup shows one state of many |
| **Acceptance criteria alone** | The contractual definition of done | No context — you cannot tell what it deliberately excludes |
| **Verbal / chat instruction** | Whatever was said | Nothing is written down. This is the weakest source there is. |

Two rules that follow from this:

1. **Name your sources in the report.** "Tested against the ticket and the Figma; no written
   validation rules existed" tells the reader exactly how much to trust the result.
2. **If the only source is verbal, a screenshot, or a chat message, say so** — you are at Level 1
   with an undocumented requirement, and the first deliverable is the written requirement, not a
   test suite. Write what you understood, get it confirmed, then test against that.

When several sources exist they will disagree. Record the disagreement as a clarification
question — do not silently pick the one that is easiest to test.

## For a ticket, read everything in this order

1. **Ticket description** — the nominal requirement.
2. **Acceptance criteria** — the contractual definition of done.
3. **Comments** — frequently where the *real* scope lives. Scope changes, decisions, and explicit
   QA instructions are usually added in comments long after the description was written.
4. **Attachments** — mockups, specs, and **DB scripts**. An attached SQL script is often the most
   accurate statement of what actually changes, and it can differ from the copy in the repo.
5. **Linked tickets** — parents, blockers, and anything this supersedes or reopens.
6. **Change history** — what was edited, when, and by whom. A late edit to AC is a risk signal.

Never analyze from the title alone.

## Extraction table

Fill this for every ticket. Write **"Not stated"** where the requirement is silent — never fill a
blank with your own reasonable guess. Each "Not stated" is a candidate clarification.

| Area | What to extract |
|---|---|
| **Feature** | What is changing, in one sentence |
| **Actor** | Who performs the action — every role that can |
| **Preconditions** | What must exist first: data, state, configuration |
| **Inputs** | User and system inputs, with types and sources |
| **Business rules** | Conditional logic — see `business-rule-analysis.md` |
| **Outputs** | Expected result, including what the user sees |
| **Validation** | Field and cross-field rules, and the exact messages |
| **Workflow** | Process and state changes triggered |
| **Permissions** | Role-specific behaviour and data scoping |
| **Dependencies** | Related systems, modules, integrations, jobs |
| **Data** | Data required, created, changed, or deleted |
| **Error handling** | What happens when it fails |
| **Acceptance criteria** | Explicit, testable criteria |
| **Ambiguities** | Everything undefined, contradictory, or vague |

## Gap analysis

Scan for each category:

| Gap type | Looks like |
|---|---|
| **Missing** | An obvious behaviour simply not mentioned |
| **Contradictory** | Description and AC disagree; a comment reverses the description |
| **Ambiguous** | "appropriate", "as needed", "properly", "handle gracefully", "etc." |
| **Undefined behaviour** | Rule states the IF, never the ELSE |
| **Missing validation** | A field with no stated constraint, format, or limit |
| **Missing role behaviour** | Only one role described where several can reach the feature |
| **Missing error behaviour** | Happy path only; nothing about failure |
| **Unstated scope** | Silent on whether existing records are affected |

### Silent killers — always check explicitly

These are almost never written down and almost always matter:

- What happens to **existing records** created before this change?
- Is the change **retroactive** or forward-only?
- What does a **user without the permission** see — hidden, disabled, or an error?
- What happens on **re-submit / double-click / refresh mid-action**?
- Are **notifications or emails** triggered, and to whom?
- Is anything **cached**, and when does it invalidate?
- Does this affect any **report, export, or downstream integration**?

## Writing clarification questions

A bad question makes the reader do your thinking. A good one is answerable in a word.

**Bad:** "Please clarify the Incident Reference behaviour."

**Good:**
> **Q1 — Incident Reference on Inquiry claims.** The AC requires it for Accident but is
> silent for Inquiry. Should Inquiry (a) require it, (b) accept it optionally, or (c) hide the
> field entirely? This changes whether saving a Inquiry claim without it is a defect or correct.

Every question states: what is undefined · the plausible readings · why the answer changes the test outcome.

Number them. Group them. Put them where they can't be missed.

## Done when

- Every row of the extraction table is filled or explicitly marked "Not stated".
- Every gap has a numbered question.
- You could hand this to another QA engineer and they would test the same thing you would.
