# Repo Consistency Report

*(This is a SAMPLE report for the fictional "shopfront" repo — the diff under review adds an order-history feature: `OrderHistory.tsx`, `orderApi.ts`, and a modified `routes.tsx`. It pairs with `sample-conventions.md`.)*

**Scope:** 2 new files (`src/components/OrderHistory.tsx`, `src/orderApi.ts`), 1 modified (`src/routes.tsx`) — uncommitted changes vs `HEAD`
**Baseline source:** `.claude/CONVENTIONS.md` (existing)
**Gaps filled via live sampling:** None

## Overall Consistency Score: 58/100 — Noticeable Drift

The component itself is well-shaped and typed, but the change introduces a second data-fetching pattern (raw `axios` in the component instead of react-query + `src/api/`), puts the API file in the wrong layer, and has several naming deviations. It would not pass as "written by the same team" without changes.

| Dimension | Score | N/A? | Notes |
|---|---|---|---|
| Naming conventions | 5/10 | | snake_case props, `I`-prefixed interface (see Minor Deviations) |
| File & folder structure | 4/10 | | `orderApi.ts` placed in `src/` root instead of `src/api/` |
| Code/module/class structure | 7/10 | | Arrow-fn + default export vs. baseline function declaration + named export |
| Imports & dependencies | 5/10 | | Relative `../..` imports instead of `@/` alias; new `axios` dep duplicates existing client |
| State / dependency & resource management | 3/10 | | Raw axios + `useEffect`/`useState` instead of react-query hook over `src/api/` |
| Styling / presentation (UI only) | 8/10 | | CSS Modules used correctly; two inline styles for static values |
| Type system conventions | 7/10 | | Types defined inline in component instead of `src/types/` |
| Async / error handling | 4/10 | | try/catch + local error string in component vs. `ApiError` + react-query error state |
| Testing conventions | 2/10 | | No test file — violates Target Convention "all new components must have a co-located test" |
| Comments & docs | 10/10 | | Sparse `//` comments, matches repo style |
| Linting / formatting | 6/10 | | Double quotes and semicolons vs. Prettier config (run `npm run lint -- --fix`) |
| Framework & architectural conventions | 8/10 | | Route added in `src/routes.tsx` correctly; page-level fetching logic lives in the component, acceptable per baseline |
| Constants / config values | 6/10 | | Hardcoded `"/api/v2/orders"` string; baseline lifts endpoints to `src/constants/api.ts` |

## ✅ Consistent With Existing Patterns
- CSS Modules co-located and imported as `styles` (`OrderHistory.tsx:4` ↔ baseline §6)
- Route registration centralized in `src/routes.tsx:31`, matching `ProductsPage` precedent (baseline §12)
- PascalCase component file/export name `OrderHistory` (baseline §1)

## ⚠️ Minor Deviations
- `interface IOrderHistoryProps` (`OrderHistory.tsx:9`) — baseline uses no `I` prefix and `type XxxProps` (`CheckoutForm.tsx:8`, baseline §1, §3)
- snake_case prop `user_id` (`OrderHistory.tsx:10`) — baseline props are camelCase (`ProductCard.tsx:9`)
- Default export of arrow function (`OrderHistory.tsx:14`) — baseline uses named function declarations (`ProductCard.tsx:12`)
- Relative `../../` imports (`OrderHistory.tsx:1-2`) — baseline uses `@/` alias (baseline §4)
- Double quotes + semicolons throughout both new files — repo Prettier config is single quotes, no semicolons (`.prettierrc:1-4`)
- Hardcoded endpoint string `"/api/v2/orders"` (`orderApi.ts:6`) — baseline lifts these to `src/constants/api.ts`
- Missing test file for `OrderHistory` — flagged per `.claude/CONVENTIONS.md § Target Conventions` (user-declared, strictness: minor)

## 🔴 Major Inconsistencies
- **Second data-fetching pattern.** `OrderHistory.tsx:18-29` uses `axios.get` inside a `useEffect` with local `useState` for data/loading/error. The repo's established pattern is a react-query hook in `src/hooks/` over a fetcher in `src/api/` using the shared `ApiError`-throwing client (`useProducts.ts:6-10`, `api/products.ts:4-9`, baseline §5, §8). This also adds `axios` as a new dependency duplicating the existing `src/api/client.ts`.
- **Wrong layer for the API module.** `src/orderApi.ts` sits in `src/` root; every other fetcher lives in `src/api/` (baseline §2).

## Recommendations
1. Replace the axios/`useEffect` block with a `useOrders` hook in `src/hooks/` wrapping a fetcher in `src/api/orders.ts`, following `useProducts.ts:6-10` — and drop the `axios` dependency.
2. Move `orderApi.ts` → `src/api/orders.ts`; move the `Order` type to `src/types/order.ts`.
3. Rename `IOrderHistoryProps` → `OrderHistoryProps` (as `type`), `user_id` → `userId`; switch to a named function declaration.
4. Lift `"/api/v2/orders"` into `src/constants/api.ts`; replace `../../` imports with `@/`.
5. Add `OrderHistory.test.tsx` (Target Convention); run `npm run lint -- --fix` for quotes/semicolons.

## Baseline Maintenance
None — `.claude/CONVENTIONS.md` covered every dimension; no contradictions with current code observed.
