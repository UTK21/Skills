---
name: repo-consistency-checker
description: >
  Evaluates whether new or changed code matches the existing coding conventions, patterns, and architecture already established in this repository, and produces a consistency score. Use this skill whenever the user wants to check if their changes "fit" the codebase, asks for a "consistency score", "pattern consistency check", "does this match our conventions/style", "how consistent is this with the rest of the repo", or wants a diff, PR, or staged/uncommitted changes reviewed for adherence to existing patterns (naming, file structure, state management, styling, imports, TypeScript conventions, error handling, testing, etc.) rather than generic best practices. Especially useful for React/TypeScript/JS repos but applies to any codebase with established conventions.
---

# Repo Consistency Checker

You are a senior engineer who has read every file in this codebase and knows its unwritten conventions cold. Your job is to take new or changed code and answer one question: **does this look like it was written by the same team, following the same patterns, as the rest of the repo?**

This is NOT the same as a best-practices review. A change can be "good code" in the abstract and still score poorly here if it solves a problem the codebase already has a pattern for, but in a different way (a second state-management library, a different file layout, a different naming scheme, a different data-fetching approach, etc.).

> **Related skill:** `ai-code-reviewer` checks for bugs, best practices, and accessibility issues. This skill checks for *fit with the existing codebase*. They're complementary — run both for a full picture, but don't conflate their findings.

## Why this matters

- Two correct-but-different ways of doing the same thing increase cognitive load for every future reader.
- AI-assisted and fast-moving changes commonly introduce a *new* pattern instead of reusing the one that already exists for the same problem (a new state-management approach, a new styling method, a different file layout, different naming, different import style, an extra dependency that duplicates one already in `package.json`).
- Catching pattern drift early keeps the codebase coherent and keeps diffs small and reviewable.

---

## Process

### Step 1 — Determine the scope of "new code"

Figure out what's being evaluated:

- If the user says "my changes", "this diff", "uncommitted", "staged" → run `git status` and `git diff` (and `git diff --staged`) to see what changed.
- If they reference a branch/PR → use `git diff <base>...<head>` (e.g. `git diff main...HEAD`) and `git log <base>..HEAD` for the commit list.
- If they paste code directly with no repo context → ask which directory/module it would live in, or ask for 1-2 example files of the same kind (component/hook/route/etc.) to use as the baseline.

Build a list of changed files. Separate **new files** from **modified files** from **deleted files**, and drop anything that isn't hand-written source (lockfiles, build output, snapshots, generated types, `.min.js`, etc.) — those don't carry conventions.

### Step 2 — Build a baseline profile of the EXISTING codebase

This is the most important step, and the one it's tempting to skip. Do not judge the new code against generic "best practices" — judge it against what THIS repo already does.

1. **Read project-level config first** — it tells you what's even possible and what's enforced:
   - `package.json` — framework, UI library, state management, data-fetching, styling, test runner
   - `tsconfig.json` — strictness, path aliases (`@/...`)
   - `.eslintrc*`, `.prettierrc*`, `.editorconfig` — enforced style rules
2. **For each changed file, find 2-4 sibling files of the same kind** that were NOT changed in this diff:
   - New component → find other components in the same folder or `components/`
   - New hook → find other hooks in `hooks/`
   - New API call/route → find other files in the API/services layer
   - New test → find other test files
   - For **modified** files, also check `git show HEAD:<path>` (or the base ref) to see the file's own prior conventions
3. Read those sibling files and note, per dimension in `references/convention-dimensions.md`, what the *dominant* pattern is. If the repo is inconsistent with itself (legacy vs. new pattern), note both and use the more common / more recently-touched one as the baseline — and say so in the report.

Keep this baseline tight and evidence-based: every convention you claim is "the repo's pattern" should be backed by at least one file:line citation from an existing file.

### Step 3 — Compare each changed file against the baseline

Walk through `references/convention-dimensions.md`. For each dimension that applies to the file(s) under review, compare the new/changed code to the baseline from Step 2. Be specific — cite both sides:

> "New code uses `axios.get()` directly inside the component (`OrderList.tsx:14`), but the baseline (`UserList.tsx:6-9`, `api/users.ts:1-4`) fetches via a `useQuery` hook backed by a function in `api/`."

Skip dimensions that genuinely don't apply (e.g. styling conventions for a pure utility module) and say so briefly rather than padding the report.

### Step 4 — Score

Use `references/scoring-rubric.md` to score each applicable dimension and compute the overall consistency score.

### Step 5 — Write the report

Use the **Output Format** below.

---

## Dimensions to evaluate

See `references/convention-dimensions.md` for the full checklist (naming, file/folder layout, component structure, imports, state management, styling, TypeScript conventions, async/error handling, testing, comments, and linting).

## Scoring

See `references/scoring-rubric.md` for the per-dimension scoring scale, weighting, and how to roll it up into the overall score and label.

---

## Output Format

```
# Repo Consistency Report

**Scope:** [files analyzed, and against what base/ref]
**Baseline derived from:** [sibling files / config used to determine conventions]

## Overall Consistency Score: XX/100 — [Label]

[1-3 sentence summary: does this look like it belongs in this repo?]

| Dimension | Score | N/A? | Notes |
|---|---|---|---|
| Naming conventions | x/10 | | ... |
| File & folder structure | x/10 | | ... |
| Component/module structure | x/10 | | ... |
| Imports | x/10 | | ... |
| State management | x/10 | | ... |
| Styling | x/10 | | ... |
| TypeScript conventions | x/10 | | ... |
| Async / error handling | x/10 | | ... |
| Testing conventions | x/10 | | ... |
| Comments & docs | x/10 | | ... |

## ✅ Consistent With Existing Patterns
- [What the new code does the same way as the rest of the repo, with citations]

## ⚠️ Minor Deviations
- [Small stylistic differences — cite new code vs. baseline]

## 🔴 Major Inconsistencies
- [New patterns/approaches/dependencies not used elsewhere for the same purpose — cite new code vs. baseline]

## Recommendations
1. [Concrete, actionable — "use `useQuery` from `@tanstack/react-query` as in `UserList.tsx` instead of a raw `useEffect`/`fetch`"]
2. ...
```

---

## Edge cases

- **No prior code to compare against (new/empty repo or new module):** Say so explicitly. Fall back to an *internal consistency* check — do the new files follow a single coherent pattern among themselves? Don't compute a misleading overall score; instead note "no baseline available — internal consistency only."
- **Repo has multiple conflicting conventions already (e.g. mid-migration):** Identify both patterns, state which one is dominant/newer, and evaluate against that one. Don't penalize the new code twice for a pre-existing inconsistency.
- **The "new code" is actually a refactor that intentionally changes the pattern repo-wide:** If the diff touches many files to migrate a pattern (e.g. CSS Modules → Tailwind across the board), don't score it as "inconsistent" — note that it appears to be an intentional, repo-wide migration and evaluate internal consistency of the new pattern instead.
- **Generated/scaffolded files (e.g. from `create-react-app`, codegen):** Exclude from scoring, note them separately.

## Tone and approach

- Cite real file:line evidence on both sides of every claim — this report is only useful if it's verifiable.
- Don't penalize the new code for not following a "best practice" the rest of the repo also doesn't follow — that's out of scope for this skill.
- Be proportionate: a single new helper function with a slightly different naming style is a minor deviation, not a major one. Reserve "Major Inconsistency" for things that introduce a parallel pattern/dependency for something the repo already has a way of doing.
- If the code is highly consistent, say so briefly and confidently — don't manufacture nitpicks to fill out the report.
