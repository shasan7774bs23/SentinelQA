# AI-Assisted QA

AI is useful for the **generative** half of this method — drafting, enumerating, extracting,
restructuring. It is worthless, and actively dangerous, for the **evidential** half: what actually
happened when the test ran, and whether a finding is a real defect.

Every hard rule in `SKILL.md` still applies when AI produced the artifact. An AI-drafted test case
that was never executed is `Not Executed`, exactly like a hand-written one.

## Where it genuinely helps, and where it must not be trusted

| Stage | AI can | AI must not |
|---|---|---|
| Requirement analysis | Extract actors, inputs, rules; list what is *not* stated | Decide what an ambiguous requirement means |
| Business rules | Convert prose to IF/THEN, build a decision table | Invent the missing ELSE branch |
| Test data | Enumerate input classes and boundary sets | Assert a range the requirement never gave |
| Scenario + case design | Draft cases, restructure, spot missing dimensions | Judge which risks matter here — that is domain knowledge |
| Codebase pass (Level 2) | Locate logic, summarise a flow, cite `file:line` | Conclude "works correctly" without you reading the citation |
| Execution | Nothing, unless a real browser/API/DB tool is driving it | **Ever report a Pass, a Fail, a log, or a screenshot it did not produce** |
| Defect validation | Argue both sides of the validation gate | Confirm a defect; that needs reproduction + a control check |
| Reporting | Draft the report, keep the traceability consistent | Sign off. The recommendation is a human's. |

The dividing line is simple: **AI may propose anything and confirm nothing.**

## Review protocol for AI-generated test cases

The poster-level advice "review and refine AI generated test cases" is only real if the review has
a checklist. Run this one on every AI-drafted suite — yours or a team member's:

1. **Does each case trace to a requirement or rule?** Untraceable cases are padding or an
   undocumented rule. Delete or raise — never keep "just in case".
2. **Was any expected result derived from the app instead of the requirement?** That documents the
   bug rather than finding it. It is the single most common failure in generated cases.
3. **Is any expected result invented?** Cross-check every one against the source. If the
   requirement is silent, the case is a clarification question, not a test.
4. **One reason to fail per case?** Generated cases habitually bundle two assertions.
5. **Are the UI labels real?** Generated labels are plausible and frequently wrong — see
   `test-case-design.md`.
6. **Are the cases distinct, or the same class of input restated?** See `test-data-design.md`.
7. **Is anything missing that the generator never thinks of unprompted?** Role/permission
   behaviour, workflow state transitions, persistence after reload, existing records created
   before the change, impacted modules.
8. **Does any case assume execution already happened?** Status must be `Not Executed`.

Cases that survive all eight are worth running. In practice a generated suite loses a third of its
volume here and gets better for it.

## Prompting that produces usable QA output

- Paste the requirement **verbatim**. Summarising it is where the requirement gap disappears.
- Ask for **gaps and ambiguities first**, test cases second. Reverse that order and the model
  quietly fills every gap with an assumption.
- State the format explicitly — the fields in `templates/test-case.md`.
- Forbid invention out loud: *"Where the requirement is silent, write 'Not stated' and raise a
  question. Do not infer the behaviour."*
- Give it the code, or the spec, or say plainly that it has neither. A model with no source is at
  Level 1 whatever it claims.
- Ask it to mark each expected result with the rule it came from. Anything unmarked is suspect.

## Tools

Chat assistants (Claude, ChatGPT, Gemini), IDE agents (Claude Code, Copilot), custom RAG agents
over your BRD/SRS corpus, and AI-native test tools (TestRigor, Functionize and similar) differ in
convenience, context size, and how much of your requirement they can hold at once.

None of them changes anything above. A more capable tool produces a better *draft*, faster — it
does not upgrade a prediction into evidence. Judge any tool on one question: **can it show you
what it based each claim on?**

## What stays human, always

Severity and priority · the READY / NOT READY recommendation · whether a finding is a real defect ·
what gets filed as a ticket · what gets released. AI drafts these. It does not decide them, and it
does not sign them.

## Before finishing

- Every AI-drafted case has been through the eight-point review.
- No expected result came from watching the app.
- Nothing is labelled Pass or Fail that was not genuinely executed.
- The report says which artifacts were AI-drafted and that a human reviewed them.
