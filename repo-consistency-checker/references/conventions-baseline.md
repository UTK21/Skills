# Generating & Refreshing `.claude/CONVENTIONS.md`

This reference covers **Step 0** of `SKILL.md`: how to profile a repo for the first time (or refresh an existing profile) and write `.claude/CONVENTIONS.md`.

---

## Sampling strategy (don't read the whole repo)

The goal is a representative sample, not exhaustive coverage. For a typical repo this should be on the order of **15-30 files total**, even for large codebases.

1. **Always read project-level config first** — these files alone establish a lot with very little reading:
   - JS/TS/React: `package.json`, `tsconfig.json`, `.eslintrc*`, `.prettierrc*`
   - Python: `pyproject.toml`/`setup.cfg`/`requirements*.txt`, `.flake8`/`ruff.toml`/`mypy.ini`/`pylintrc`
   - Java: `pom.xml`/`build.gradle*`, `checkstyle.xml`
   - Any repo: `.editorconfig`, `CONTRIBUTING.md`/`STYLE_GUIDE.md` if present (treat as context on intent, not ground truth — see SKILL.md edge cases)

2. **Use `git log` to bias toward "actively maintained" patterns.** Files changed recently/frequently are more likely to reflect the *current* convention than old, untouched files. `git log --diff-filter=AM --name-only -20` (or similar) gives a quick signal of what's actively being worked on.

3. **For each major file-kind in the repo, sample 2-4 files.** Use `Glob` to enumerate by pattern, then read a handful — prefer ones that look canonical (not the smallest/oddest). Examples of "kinds" to look for (only the ones that actually exist in this repo):
   - JS/TS/React: components (`**/*.tsx`), hooks (`**/hooks/*.ts`), pages/routes, API/service layer, tests, shared types/utils
   - Python: service/business-logic modules, models/schemas, API routes/views, tests, utility modules
   - Java: controllers, services, repositories, models/DTOs/entities, exceptions, tests

4. **For monorepos / multiple sub-projects**, identify top-level packages first (e.g. via workspace config, multiple `package.json`/`pyproject.toml`/`pom.xml` files). If their conventions clearly differ, profile each separately and write a `.claude/CONVENTIONS.md` per sub-project (see SKILL.md edge cases). If they share conventions, one root-level file is fine.

5. **Stop once you have evidence for most of the 13 dimensions** in `references/convention-dimensions.md`. It's fine — and expected — for some dimensions to come back "insufficient evidence" on a small or early-stage repo. Don't pad the doc to force coverage.

---

## Resolving genuinely ambiguous dimensions

Most dimensions will have a clear dominant pattern even from a small sample (e.g. 8 of 10 sampled components use the same data-fetching approach) — write that down, note the minority usage under "Known Mixed/Conflicting Patterns", and move on. Don't ask the user about these.

A dimension is **genuinely ambiguous** only when, after sampling:
- two (or more) patterns show up in roughly similar numbers, **and**
- both appear in actively-maintained files (not "one pattern only in old/legacy-looking code that the other has clearly replaced").

For each genuinely ambiguous dimension, ask the user which pattern should be treated as canonical going forward — a wrong silent guess here gets enforced on every future consistency check, so it's worth a quick question. Use `AskUserQuestion`:

- One question per ambiguous dimension, batched into as few calls as possible (max 4 questions per call; if there are more than 4, see below).
- `header`: short dimension name (e.g. "State mgmt", "Error handling", "Naming").
- `question`: state both patterns with a citation each, e.g. "This repo has two state-management approaches in active use — Context API (`UserProvider.tsx:1-20`) and Zustand (`useCartStore.ts`). Which should new code follow?"
- `options`: each pattern as an option, with its citation in the `description`, plus (where it makes sense) an option like "Both are fine — don't pick one" for dimensions where coexistence is reasonable (e.g. two acceptable test-assertion styles).

Use the chosen pattern as the **Dominant pattern** for that dimension in `.claude/CONVENTIONS.md`. Record the non-chosen pattern under "Known Mixed/Conflicting Patterns" as the secondary/legacy pattern — existing usages of it aren't wrong, but new code should follow the chosen one.

If there are more than ~4 genuinely ambiguous dimensions, ask about the highest-impact ones first (naming, state management, error handling, testing) in one batch, and resolve the rest with the tiebreaker from `SKILL.md` Step 0/2 (more recently-touched pattern wins) — note those under "Known Mixed/Conflicting Patterns" so the user can revisit them later if they disagree.

**On refresh**, only ask about dimensions that are newly ambiguous or were never resolved — don't re-ask about ones the user already settled. If a new sample suggests the user's earlier choice has since fallen out of use entirely, tell them what you found and ask whether to update the baseline rather than silently changing it.

---

## Target Conventions (aspirational patterns)

Sometimes the convention the team *wants* isn't the one the code *has* — they're starting a migration, tightening standards, or adopting a new library, and they want the checker to push new code toward the target rather than the status quo.

**When to offer it:** as the last step of baseline generation (after ambiguity resolution, before writing the file), ask once via `AskUserQuestion`:

- `header`: "New patterns"
- `question`: e.g. "The baseline above describes what the code currently does. Do you want to declare any *target* conventions — patterns new code should follow even though the existing code doesn't yet?"
- `options`: "No — current code is the standard (Recommended)" first (most repos just want the status quo enforced), plus an option like "Yes — I'll describe them", letting the user type specifics via the built-in "Other"/notes input.

**When the user volunteers one** ("add a new pattern: all new API calls go through `api/client.ts`"), at any time — not just during generation — confirm before recording it, via `AskUserQuestion` if anything is unclear:
1. The exact rule (what new code must do, what it must stop doing).
2. The scope (which dimension(s) it affects; new code only, or also flagging old code when touched?).
3. Whether it *replaces* an existing baseline entry (a migration) or is *net-new* (no existing pattern for this concern).

Then append it to the **Target Conventions** section of `.claude/CONVENTIONS.md` — a targeted edit, not a full regeneration.

**How checks treat target conventions (Step 3 / scoring):**
- New/changed code is scored against the **target**, not the legacy pattern it replaces. Code following the target pattern is *consistent*, even if 90% of the repo still does it the old way.
- New code that follows the *legacy* pattern instead of the target is a deviation — usually ⚠️ Minor ("repo is mid-migration; new code should use X per Target Conventions") unless the team marked the rule as strict, then 🔴 Major.
- Cite the Target Conventions entry as the baseline evidence (there may be no file:line in the code yet — that's expected; cite `.claude/CONVENTIONS.md § Target Conventions` and note it's user-declared).
- Don't retroactively penalize untouched legacy code, and don't suggest drive-by migrations beyond the diff under review.

**On refresh:** preserve the Target Conventions section verbatim — it's user-declared intent, not sampled fact, so resampling can't invalidate it. If sampling shows a target has now become the dominant actual pattern, tell the user and offer to "graduate" it into the main baseline section for that dimension.

---

## House Rules (always-enforced, lint-style rules)

Target Conventions describe *pattern migrations* ("new code uses X instead of Y"). **House Rules** are different: specific, checkable rules the team wants enforced on all new/changed code regardless of what existing code does — closer to a lint rule than a pattern. Examples:

- "`useEffect` that sets up a subscription, timer, or event listener must return a cleanup function."
- "`useCallback`/`useMemo` dependency arrays must include every prop/state value referenced inside — no artificially empty `[]`."
- "No `console.log` outside `src/dev/`."
- "Every exported function in `src/api/` must have an explicit return type."

How they work:

- **Capture:** users declare them ("add a house rule: ...") at any time, or during baseline generation alongside the Target Conventions question. Before recording one, restate it precisely and confirm — vague rules produce noisy checks. If a stated rule has legitimate exceptions (e.g. an empty deps array is *correct* for a callback that references no props/state), encode the precise version and note the exception in the rule text.
- **Prefer the linter when possible:** if a rule is mechanically checkable by the repo's existing tooling (e.g. `react-hooks/exhaustive-deps` covers dependency arrays), recommend enabling that rule too and record in the House Rule that the linter is the primary enforcer — the skill then just reports violations under Dimension 11. Rules the linter can't express (judgment-based ones) are checked by the skill directly.
- **Checking:** during Step 3, evaluate each House Rule against the changed files only, under whichever dimension it belongs to (note the rule ID/text in the finding). Violations score like an explicit enforced convention — 0-3 on that dimension per the rubric — and land in 🔴 Major Inconsistencies unless the rule declares a lower strictness.
- **No retroactive sweeps:** like everything else in this skill, House Rules apply to the diff under review, not untouched legacy code.
- **On refresh:** preserve the House Rules section verbatim, same as Target Conventions.

---

## `.claude/CONVENTIONS.md` template

Write the file using this structure. Keep each dimension's entry short — a stated pattern plus 1-3 citations, not a full essay.

```markdown
# Repo Conventions Baseline

> Generated by repo-consistency-checker on YYYY-MM-DD from N sampled files.
> This is the baseline `repo-consistency-checker` compares new/changed code
> against. It's a normal markdown file — edit it directly if these
> descriptions are wrong or conventions change, or ask the skill to
> "refresh the conventions baseline" to regenerate it from the current code.

## Stack
- [Languages, frameworks, and key libraries detected, with the config file(s) they came from]

## 1. Naming Conventions
- [Dominant pattern per identifier kind — files, functions/methods, variables, constants, types/classes — with citations]

## 2. File & Folder Structure
- [Where each kind of file lives, co-location vs parallel trees, citations]

## 3. Code / Module / Class Structure
- [Dominant shape — exports, member ordering, data-carrier style, citations]

## 4. Imports & Dependencies
- [Import style/ordering/aliasing conventions, citations]

## 5. State / Dependency & Resource Management
- [Dominant approach(es) — state mgmt / DI style / resource handling, citations]

## 6. Styling / Presentation Layer
- [Dominant approach, or "N/A — no UI layer in this repo"]

## 7. Type System Conventions
- [Type-hinting/typing conventions, citations]

## 8. Async / Error Handling
- [Exception/error-handling shape, citations]

## 9. Testing Conventions
- [Framework, file naming/location, structure, citations]

## 10. Comments & Documentation
- [Docstring/Javadoc/JSDoc conventions if any, or "minimal — no enforced doc style observed"]

## 11. Linting / Formatting
- [Configured tools and key enforced rules]

## 12. Framework & Architectural Conventions
- [Routing/layering/annotation conventions, citations]

## 13. Constants / Configuration
- [Where config/constants live, citations]

## Known Mixed/Conflicting Patterns
- [Any dimension where the repo isn't internally consistent — note both patterns, which is treated as dominant, and how that was decided (user-confirmed via AskUserQuestion / auto-detected majority / recency tiebreaker). Omit section if none found.]

## Target Conventions (aspirational)
- [User-declared patterns that new code must follow even though existing code doesn't yet. For each: the rule, the dimension(s) it affects, what it replaces (if a migration), strictness (minor vs major deviation if not followed), and date declared. Omit section if none.]

## House Rules (always enforced)
- [User-declared lint-style rules checked on every diff regardless of existing code. For each: precise rule text (including legitimate exceptions), the dimension it's checked under, primary enforcer (this skill, or a named lint rule), strictness, and date declared. Omit section if none.]

## Not Yet Covered
- [Dimensions/file-kinds with too little evidence to establish a pattern yet. Omit section if none.]
```

---

## Refreshing an existing baseline

When the user asks to refresh/regenerate, or you've found `.claude/CONVENTIONS.md` to be stale:

1. Re-run the sampling strategy above against the current codebase.
2. Read the existing `.claude/CONVENTIONS.md` first and diff your new findings against it mentally — don't silently overwrite manual edits without comment.
3. When you write the refreshed file, summarize for the user what changed (e.g. "State management: was Context API, now mostly Zustand — updated. Naming conventions: unchanged.").
4. If a section in the old file looks hand-edited and still matches reality, preserve it as-is rather than rewording for no reason.
