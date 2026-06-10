# React Best Practices Reference

Read this when reviewing React/JSX code. Focus on the sections most relevant to the code under review.

---

## Hooks

### useEffect
- Every value used inside `useEffect` that could change over time belongs in the dependency array
- An empty `[]` dep array with logic that reads props/state is almost always a bug — it means the effect runs once with stale values
- If cleanup is needed (subscriptions, timers, event listeners, abort controllers), it must be returned from the effect
- Effects that fetch data should abort on cleanup to prevent setting state on unmounted components:
  ```tsx
  useEffect(() => {
    const controller = new AbortController();
    fetch(url, { signal: controller.signal }).then(...);
    return () => controller.abort();
  }, [url]);
  ```
- Avoid putting object/array/function literals directly in dep arrays — they create new references every render

### useState / state shape
- Don't store derived values in state — compute them from existing state
- Don't store the same data in two places — keep a single source of truth
- Initializer functions (lazy init) should be used for expensive initial state: `useState(() => computeExpensive())`

### useCallback / useMemo
- Only worth using when: (1) the value/function is a dep of another hook, (2) passed to a memoized child component, or (3) computation is genuinely expensive
- AI often adds these everywhere "for performance" — they add cost if misused
- Missing deps in `useCallback` creates stale closures

### useRef
- Correct for: DOM references, values that must persist without triggering re-renders, mutable values in event handlers that need current state
- Don't use it as a workaround for state management problems

---

## Component Design

### Props
- Avoid boolean props that encode multiple states — prefer explicit string unions: `variant="primary" | "secondary"` vs `isPrimary isSecondary`
- Spreading unknown props (`{...rest}`) onto DOM elements is fine but use `HTMLAttributes<HTMLDivElement>` to type it correctly
- Don't destructure deeply nested props — it makes the shape opaque

### Keys
- Keys must be stable and unique among siblings — never use array index as a key when the list can reorder or filter
- Keys should come from the data (IDs), not generated at render time

### Conditional rendering
- `undefined` and `null` are safe to render; `0` and `''` are not (they render as "0" or empty)
- `condition && <Component />` with a numeric condition renders 0 — use `condition ? <Component /> : null`

### Event handlers
- `onClick={(e) => handler(e, id)}` creates a new function every render — this is fine for most cases, but avoid it in tight loops or if the child is `React.memo`
- Synthetic events are pooled in old React — don't access them asynchronously without `e.persist()` (React 17+ this is no longer needed)

---

## Performance

### Re-renders
- A component re-renders when its parent re-renders, its state changes, or its context changes
- `React.memo` only prevents re-renders from parent — state/context changes still trigger
- Context consumers re-render whenever context value changes — split context if you have high-change and low-change values together

### Lists
- Large lists (>100 items) should be virtualized — `react-window` or `react-virtual`
- Avoid creating DOM nodes for hidden items — use CSS `display: none` only for truly small toggles

---

## TypeScript in React

- Prefer `React.FC` only if you need the `children` implicit prop (React 18+: children must be explicit)
- Type event handlers precisely: `React.ChangeEvent<HTMLInputElement>`, not `any`
- Use discriminated unions for complex prop shapes
- `as` casts on DOM refs should match the element: `useRef<HTMLButtonElement>(null)`, not `useRef<HTMLElement>(null)`
