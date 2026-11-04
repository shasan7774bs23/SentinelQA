# Cross-Ticket Interaction Risk

The risk that only exists at release level: **two changes that are each individually correct,
and together are not.**

Every per-ticket QA report assessed its own blast radius. None of them was scoped to see the
other tickets in the release. So a module touched by three tickets was reviewed three times, by
three people, each assuming theirs was the only change to it. That assumption is the gap.

This is the one stage of the release gate that produces findings nobody has produced before.
Everything else in the gate is arithmetic over existing reports.

## Build the matrix first

From each ticket's **Regression impact** section and its Pass 1 `file:line` citations, list the
modules, services, tables, endpoints and shared components it touched.

| Module / surface | Tickets touching it | Any ticket assess the combination? |
|---|---|---|
| `PaymentService` | ABC-101, ABC-118 | No |
| `users` table | ABC-104, ABC-118, ABC-127 | No |

**Anything touched by two or more tickets is an interaction candidate.** Anything touched by one
is already covered by that ticket's own regression section — do not re-litigate it here.

At Level 3, build the matrix from the actual diff across the release rather than from what the
reports happened to mention. Reports under-report their own blast radius routinely.

## The five interactions worth checking

**Shared state or schema.** Two tickets writing the same table, cache or document. Check for a
column one widens and another validates, a default one sets and another assumes, a row one
soft-deletes and another counts.

**Ordering and migration.** One ticket's migration against another's read path. The failure is
deploy-order dependent, so it reproduces in one environment and not another — which is exactly
the shape that gets dismissed as "an environment issue."

**Contract drift.** One ticket changes a response shape, header, status code or error body that
another consumes. Each side is internally consistent; the seam is not. Especially likely when
the two tickets sit with different developers.

**Configuration and feature flags.** Two tickets adding flags that are individually tested on,
never tested in the four combinations. Ask which combination production will actually be in on
release day — often it is one nobody ran.

**Permission surface.** Two tickets each altering role checks. Role/permission findings are kept
separate in the per-ticket reports for good reason; at release level, the union of two
independently-correct permission changes can open a path neither ticket created alone.

## What a finding here looks like

Name the **specific combined scenario**, not the abstract risk:

> `ABC-118` widens `users.status` to accept `SUSPENDED`. `ABC-104` counts active users with
> `status != 'INACTIVE'`. A suspended user is now counted as active on the dashboard. Neither
> ticket's report covers this; `ABC-104` was tested before `ABC-118` merged.

Then say plainly whether anyone tested it. Usually nobody has — which makes it a **coverage
gap**, not a defect. Recommend the specific test, and let the human decide whether it runs
before release or the risk is accepted.

## Honest limits

- Without repo access this is Level 1 reasoning over what the reports chose to mention.
  Everything found here is **Potential** — never Confirmed — until someone reproduces it.
- The matrix is only as good as the regression sections feeding it. If several reports left
  "Regression impact" thin, say that the interaction analysis is correspondingly weak rather
  than presenting a short list as a clean bill of health.
- Do not manufacture interactions to look thorough. Two tickets touching the same module with
  no plausible shared failure mode is a fine finding to report as "no interaction identified."

## Before finishing

- Matrix built from every ticket in the fix-version, not only the ones with rich reports.
- Every module with 2+ tickets either produced a named scenario or an explicit "no interaction
  identified."
- Every scenario states whether it was tested, and by whom, or that it was not.
- Nothing labelled above **Potential** without reproduction.
- The weakness of the input reports is stated if the matrix rests on thin regression sections.
