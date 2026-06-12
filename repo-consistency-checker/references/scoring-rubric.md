# Scoring Rubric

## Per-dimension score (0-10)

For each dimension in `convention-dimensions.md` that applies to the files under review, assign a score:

| Score | Meaning |
|---|---|
| **10** | Fully consistent — uses the exact same pattern, naming, and structure as the baseline. |
| **7-9** | Mostly consistent — same underlying pattern/approach, only superficial differences (e.g. slightly different variable name style on one line). |
| **4-6** | Mixed/partial — uses a pattern that exists *somewhere* in the repo but not the dominant/baseline one for this kind of file, OR a single notable but isolated deviation in an otherwise-matching file. |
| **1-3** | Inconsistent — introduces an approach, library, or structure not used elsewhere in the repo for this kind of problem, with no clear justification. |
| **0** | Directly contradicts an explicit, enforced convention (lint rule, config, or documented style guide). |
| **N/A** | Dimension doesn't apply to these files (e.g. styling dimension for a pure data-utility module). Exclude from the average — do not count as 0. |

Mark a dimension N/A rather than guessing — an inflated or deflated overall score from forcing irrelevant dimensions is worse than a shorter table.

### Scoring against Target Conventions

When `.claude/CONVENTIONS.md` declares a target convention for a dimension (a user-declared pattern the existing code doesn't follow yet — see `references/conventions-baseline.md`), the **target replaces the sampled baseline** for that dimension:

- New code that follows the **target** scores as consistent (7-10) — do not dock points because most of the repo still does it the old way.
- New code that follows the **legacy** pattern instead scores **4-6** by default (it matches code that exists, but not the declared direction), or **1-3** if the team marked the rule as strict.
- Cite `.claude/CONVENTIONS.md § Target Conventions` as the baseline evidence — a code citation may not exist yet, and that's expected.

### Scoring House Rules violations

A violation of a **House Rule** (always-enforced lint-style rule — see `references/conventions-baseline.md`) counts as contradicting an explicit, enforced convention: score the affected dimension **0-3** regardless of what surrounding code does, unless the rule itself declares a lower strictness. Cite both the rule text in `.claude/CONVENTIONS.md § House Rules` and the violating line.

## Overall score

```
Overall = round( (sum of scores for applicable dimensions) / (number of applicable dimensions * 10) * 100 )
```

i.e. average the applicable per-dimension scores (0-10) and scale to 0-100.

If fewer than 3 dimensions are applicable, or there's no real baseline to compare against (see Edge Cases in SKILL.md), do not present a single overall number as if it were a full assessment — say so and present whatever dimension-level findings you do have.

## Score bands / labels

| Range | Label | Meaning |
|---|---|---|
| 90-100 | **Excellent — fits seamlessly** | Indistinguishable from code written by someone steeped in this codebase's conventions. |
| 75-89 | **Good — minor nits** | Clearly follows the established patterns; a few small stylistic tweaks would make it indistinguishable. |
| 60-74 | **Fair — some deviations** | Core approach is compatible but several details (naming, location, imports, typing, etc.) diverge and are worth fixing before merge. |
| 40-59 | **Inconsistent — notable pattern mismatches** | One or more dimensions show a parallel/competing pattern to something the repo already does (e.g. a second state-management approach, a new styling method). Should be addressed before merge in most cases. |
| 0-39 | **Major drift — looks like a different codebase** | Multiple major inconsistencies, likely including new dependencies or architectural approaches that duplicate existing solutions. |

## Weighting notes

- All applicable dimensions are weighted equally by default — simplicity keeps the score interpretable and arguable from the evidence.
- If one dimension is overwhelmingly the dominant concern (e.g. the only issue is a brand-new state-management library introduced for state the repo already manages elsewhere), still compute the even-weighted average, but make sure the prose summary and "Major Inconsistencies" section make clear that this single issue is the headline finding — a numeric average can understate a single severe architectural mismatch.
- A high score does not mean "no findings" — always populate the Consistent / Minor / Major sections honestly, even if Minor and Major are empty ("None found.").
