# Boundary Testing

Defects cluster at edges. `>` written where `>=` was meant is invisible everywhere except at exactly
one value — so test exactly that value.

Boundaries are the edges of the input classes you drew in `test-data-design.md`. Derive both from
the same partition set — done independently, they duplicate each other.

## The standard set

For any bounded input, test six points:

```
min-1    min    min+1    ...    max-1    max    max+1
  ✗       ✓       ✓               ✓       ✓      ✗
```

If time is tight, `min`, `max`, `max+1` catch most of it. `max+1` is the highest-value single test
in this whole reference.

## Where boundaries come from — and why they disagree

A field usually has **three independent limits**, and they are frequently different:

1. The **UI** control's `maxlength`
2. The **server** validator
3. The **database** column width

They should agree. When they don't, you get one of these:

| Mismatch | Symptom |
|---|---|
| UI limit > DB width | Save fails with a raw database error, or the value is silently truncated |
| UI limit < server limit | Client blocks something the server would accept — inconsistent, and bypassable |
| No server limit | Anything bypassing the form corrupts data → `Finding — system flaw` |

At Level 2, read all three and compare them directly. This is one of the highest-yield checks in
the codebase pass, and it's invisible from the UI alone.

## What to test per type

**Text** — empty · 1 char · exactly the limit · limit+1 · whitespace only · leading/trailing spaces ·
unicode and emoji (do they count as 1 char or more?) · a very long paste

**Numeric** — 0 · negative · min · max · min-1 · max+1 · decimals where integers are expected ·
precision and rounding (does 0.005 round to 0.01 or 0.00?) · thousands separators · scientific notation

**Date/time** — today · yesterday/tomorrow at the boundary of "past"/"future" rules · start = end ·
end before start · 29 Feb in leap and non-leap years · month ends (28/29/30/31) · year boundaries ·
DST transition days · midnight exactly · **timezone** (stored UTC, displayed local — does the date
shift?) · far past and far future

**Selection/list** — none selected · exactly one · all · maximum allowed · one over the maximum

**File** — 0 bytes · 1 byte · exactly the size limit · limit+1 · allowed and disallowed extensions ·
correct extension with wrong content

**Collections/pagination** — 0 records · 1 · exactly one page · one over a page · exactly the export
limit · one over it

## Off-by-one hotspots

Check these specifically — they're where `>` vs `>=` hides:

- "Must be at least N" — is N itself accepted?
- "Up to N characters" — is N accepted, or only N-1?
- "Within the last 30 days" — is day 30 included? Day 0?
- "Older than X" — is exactly X included?
- Page size N — does the Nth record appear on page 1 or page 2?
- Age or duration thresholds — is the boundary day inside or outside?

The requirement is usually silent on inclusivity. That silence is a **requirement gap**, not a
decision for you to make — raise it, then test whichever answer you're given.

## Empty is not one thing

`null`, empty string, whitespace, zero, and "not provided" are five different states, and systems
routinely conflate them. Where it matters — especially numeric fields where 0 is meaningful —
test them separately:

> Is a Deductible Amount of `0.00` stored and displayed as zero, or treated as "not recorded"?

The two have completely different legal meaning. That kind of conflation is a real defect.

## Report boundary defects precisely

State the exact value that fails and the nearest value that works:

> Accepted at 50 characters; at 51 the value saves truncated to 50 with no warning.
> Server validator allows 255; the database column is `varchar(50)`.

A boundary defect reported without the exact failing value is a defect report the developer
has to reproduce from scratch.
