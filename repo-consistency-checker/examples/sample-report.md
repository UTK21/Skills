# Repo Consistency Report

*(SAMPLE — a diff touching two files in a fictional React/TS app. Shows the expected per-file structure, citation density, and tone.)*

**Scope:** 2 changed files vs `main`

## Overall: 55/100 — Inconsistent — notable pattern mismatches

`OrderList.tsx` blends in structurally but fetches data its own way; `order_utils.ts` has naming drift throughout. Neither would read as written by the same hands as their neighbors.

## src/components/OrderList.tsx — 4/10
**Baseline:** its own unchanged code + `UserList.tsx`, `ProductList.tsx` (same folder, recently touched)
- 🔴 Fetches with raw `useEffect` + `fetch` and local `useState` for data/loading (`OrderList.tsx:8-16`); both siblings fetch via `useQuery` over a function in `src/api/` (`UserList.tsx:5-9`, `src/api/users.ts:1-6`). This introduces a second data-fetching pattern for a problem the repo already solves.
- ⚠️ No error state — siblings render an error branch from the query result (`UserList.tsx:12`).
- ⚠️ List keys use array index (`OrderList.tsx:21`); siblings key by `id` (`UserList.tsx:17`).
- ✅ Named export, PascalCase file/component, props typed via `OrderListProps` — all match siblings.

## src/utils/order_utils.ts — 7/10
**Baseline:** its own unchanged code + `formatPrice.ts`, `dateHelpers.ts` (`src/utils/`)
- ⚠️ File name `order_utils.ts` is snake_case; every other util file is camelCase (`formatPrice.ts`, `dateHelpers.ts`).
- ⚠️ New function `Get_Total` (`order_utils.ts:14`) — siblings and this file's own existing functions are camelCase (`order_utils.ts:3`, `formatPrice.ts:2`).
- ⚠️ Hardcoded `0.18` tax rate (`order_utils.ts:17`) — sibling utils pull such values from `src/constants/` (`formatPrice.ts:1`, `src/constants/pricing.ts:2`).
- ✅ Pure named-export functions with explicit return types, matching the utils folder.

## Recommendations
1. Rewrite the fetch in `OrderList.tsx` as a `useQuery` over a new `src/api/orders.ts`, imitating `UserList.tsx:5-9` — and add its error branch.
2. 🔧 Rename `order_utils.ts` → `orderUtils.ts` and `Get_Total` → `getTotal`.
3. 🔧 Lift `0.18` into `src/constants/pricing.ts` alongside the existing pricing values.
4. 🔧 Key the order list by `order.id` as in `UserList.tsx:17`.

*Items marked 🔧 are mechanical — say "apply the fixes" and they'll be applied to your working tree (unstaged, review via `git diff`). Item 1 is architectural and stays manual.*
