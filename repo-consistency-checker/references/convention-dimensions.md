# Convention Dimensions Reference

For each dimension below: identify the dominant pattern in the EXISTING codebase first (with file:line evidence), then check whether the new/changed code follows it. Mark a dimension N/A if it doesn't apply to the files under review.

---

## 1. Naming conventions

- **File naming**: PascalCase components (`UserCard.tsx`) vs kebab-case (`user-card.tsx`) vs camelCase — does the new file match the surrounding folder?
- **Component name vs file name**: Does the exported component/function name match the filename, the way existing files do?
- **Variables/functions**: camelCase consistency, prefix conventions already in use (`handle*` for event handlers, `is*`/`has*`/`should*` for booleans, `use*` for hooks, `on*` for prop callbacks)
- **Constants**: `UPPER_SNAKE_CASE` vs camelCase for module-level constants — match what similar constants in the repo do
- **Types/interfaces**: `PascalCase`, and whether the repo suffixes prop types (`ButtonProps`) or not

## 2. File & folder structure

- Where do files of this kind live? (`components/`, `features/<feature>/`, co-located with the thing that uses them, etc.)
- Is the new file's location consistent with where similar files live?
- **Co-location**: are styles/tests/types co-located with the component (`Button.tsx`, `Button.module.css`, `Button.test.tsx` in one folder) or kept in parallel trees (`src/components/`, `src/styles/`, `__tests__/`)? Does the new file follow whichever the repo does?
- **Barrel files**: does the repo re-export via `index.ts`? If sibling modules have an `index.ts` barrel and the new module doesn't update/add one (or vice versa), note it.
- One component/export per file vs. multiple — match the surrounding convention.

## 3. Component / module structure

- Function declarations (`export function Foo()`) vs. arrow function components (`const Foo = () => {}`) — which does the repo use?
- **Default export vs named export** — be consistent with sibling files of the same kind.
- Where is the props type defined? Inline in the same file above the component, in a shared `types.ts`, or imported from elsewhere — match the existing pattern.
- Order of sections within a file (hooks first, then handlers, then derived values, then JSX) — if the repo has a consistent internal ordering, check the new file roughly follows it.

## 4. Imports

- **Path style**: absolute/aliased imports (`@/components/Button`) vs relative (`../../components/Button`) — which does the repo use, and does `tsconfig`/`jsconfig` define an alias the new file should be using but isn't (or vice versa)?
- **Import grouping/order**: external packages, then internal/aliased, then relative, then styles/assets — if the repo (or its lint config, e.g. `eslint-plugin-import`) enforces an order, check the new file matches.
- **Default vs named imports** for the same library — e.g. if the rest of the repo does `import { useQuery } from '@tanstack/react-query'`, a new file shouldn't introduce a different import shape for the same package.
- **New dependencies**: does the new code `import` from a package not present in `package.json`/lockfile, where an existing dependency already covers the same need (e.g. adding `styled-components` when the repo uses CSS Modules everywhere, or adding `lodash` for something `Array.prototype` already covers and the repo never uses lodash)?

## 5. State management

- **Local state**: `useState` vs `useReducer` — does the new code's choice match how similarly-complex state is handled elsewhere?
- **Shared/global state**: Context, Redux/Redux Toolkit, Zustand, Jotai, Recoil, MobX — is the new code introducing a *different* mechanism than what the repo already uses for cross-component state?
- **Server/remote state**: React Query / SWR / RTK Query / Apollo vs. raw `useEffect` + `fetch`/`axios` — this is one of the most common AI-introduced mismatches. If the repo has a data-fetching abstraction, new fetches should use it.
- **Derived state**: does the new code store derived values in state and sync them with `useEffect` where the rest of the repo just computes them inline (or vice versa)?

## 6. Styling

- CSS Modules, styled-components/Emotion, Tailwind utility classes, plain global CSS, or inline `style={{}}` — identify the dominant approach and flag a new approach introduced for no apparent reason.
- Class naming convention (BEM-style, utility-first, semantic) — does the new code's class names follow the same scheme?
- Theme/design tokens: if the repo references a theme object, CSS variables, or Tailwind config for colors/spacing, does the new code use those or hardcode raw values (`#fffae6`, `16px`)?

## 7. TypeScript conventions

- `interface` vs `type` for object/prop shapes — match the dominant choice.
- Use of `any`/`unknown`: does the new code introduce `any` where the rest of the repo types things precisely (or vice versa — don't penalize loose typing if the whole repo is loosely typed)?
- Event handler typing: `React.ChangeEvent<HTMLInputElement>` etc. vs `any` — match existing handler signatures for the same element types.
- Generics naming (`T`, `TData`, descriptive names) and enum vs string-union usage — match what's already established.

## 8. Async / data fetching / error handling

- Where do API calls live — inline in components, in hooks, or in a dedicated `api`/`services` layer? New fetch logic should land in the same place similar existing logic does.
- **Error handling shape**: try/catch + error state, error boundaries, toast/notification system, or thrown errors bubbling to a query library's `error` field — match the established shape.
- **Loading states**: spinner component, skeleton, boolean flag, or query-library `isLoading` — match how sibling components represent loading.
- Cleanup/cancellation: if sibling effects use `AbortController` or cleanup functions for subscriptions/timers, new effects of the same kind should too.

## 9. Testing conventions

- Test file location: co-located (`Button.test.tsx` next to `Button.tsx`) vs. a parallel `__tests__/`/`test/` tree — match the repo's choice.
- Testing library and query style: React Testing Library (`getByRole`, `getByLabelText`) vs `getByTestId`-heavy vs Enzyme — match what's used for similar components.
- Naming/structure of test files (`describe`/`it` vs `test`, naming of test cases) — match existing test files for the same kind of module.

## 10. Comments & documentation

- Comment density and style (JSDoc blocks on exported functions, inline `//` explanations, or minimal commenting) — match the surrounding code's level, don't introduce a noticeably different documentation style for the same kind of code.

## 11. Linting / formatting

- If a lint/format command is available (`npm run lint`, `eslint`, `prettier --check`) and can be run locally without side effects, run it scoped to the changed files. Distinguish **new** violations introduced by the diff from pre-existing ones in the file (for modified files, compare against `git show HEAD:<path>`).
- Note any explicit rule in `.eslintrc*`/`.prettierrc*` that the new code violates even if the linter wasn't run.

## 12. Routing / app-structure conventions (if applicable)

- Framework routing convention (Next.js file-based routes, React Router route config, etc.) — does a new page/route follow the same structure and naming as existing ones?
- Navigation: `<Link>`/router helpers vs raw `<a>`/`window.location` — match existing usage.

## 13. Constants / configuration / magic values

- Are repeated values (API base URLs, feature flags, role names, timeout durations) pulled from a shared constants/config/env-var location elsewhere in the repo? If so, new code introducing the same kind of value inline (hardcoded) is a deviation.
