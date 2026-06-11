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
