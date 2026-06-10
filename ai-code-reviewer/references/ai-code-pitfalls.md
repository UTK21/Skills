# AI Code Pitfalls Reference

Patterns that AI coding assistants (Copilot, ChatGPT, Cursor) reliably get wrong or miss. Use this to guide your review focus.

---

## Pattern 1: Optimistic Completion (Missing Error/Loading States)

AI writes the happy path and stops. The generated code assumes every fetch succeeds, every operation returns data, every async call resolves.

**What to look for:**
- `fetch()` or `axios.get()` with no `.catch()` or try/catch
- State set directly from response with no null check
- No loading indicator, spinner, or skeleton
- No empty state ("no results found")

**Why it matters:** Users see broken UIs or silent failures in production.

---

## Pattern 2: Leaked Subscriptions / Missing Cleanup

AI writes `useEffect` with subscriptions, intervals, or event listeners and forgets to clean them up.

**What to look for:**
```tsx
// BAD - no cleanup
useEffect(() => {
  window.addEventListener('resize', handleResize);
}, []);

// BAD - interval leaks
useEffect(() => {
  const id = setInterval(poll, 5000);
}, []);
```

**Why it matters:** Memory leaks, ghost event handlers, state updates on unmounted components (React warning).

---

## Pattern 3: Stale Closure in useEffect

AI puts a function call or state read inside `useEffect` without including it in deps.

```tsx
// BAD
useEffect(() => {
  doSomethingWith(userId); // userId captured at mount time, never updates
}, []); // missing userId

// BAD - callback defined outside, captures old state
useEffect(() => {
  socket.on('message', onMessage); // onMessage closes over stale state
  return () => socket.off('message', onMessage);
}, []); // onMessage not in deps
```

---

## Pattern 4: Premature Abstraction

AI introduces generic wrappers, factory functions, or configurable systems before they're needed. This is one of the most common AI signatures.

**Red flags:**
- A component that accepts 15 props to make it "reusable"
- A custom hook that wraps a single `useState`
- A `createXFactory()` function for a one-time use case
- Generic types like `T extends Record<string, unknown>` for a type that's always the same shape

**Why it matters:** Adds complexity without benefit. Future engineers (and future AI) will over-respect the abstraction and extend it instead of simplifying.

---

## Pattern 5: Accessibility Blindness

AI almost never adds accessibility attributes unprompted.

**Reliable gaps:**
- `<div onClick={...}>` instead of `<button>`
- Images without `alt`
- Inputs without `<label>` or `aria-label`
- Modals without focus trap and `role="dialog"` / `aria-modal="true"`
- Icon-only buttons with no accessible label
- `onKeyDown` missing alongside `onClick` on non-button elements

---

## Pattern 6: Any-Typed TypeScript

AI falls back to `any` under pressure — complex generics, external API responses, event types.

**Common sites:**
```ts
const data: any = await response.json();  // should be typed or unknown + narrowed
const handler = (e: any) => ...;          // should be React.ChangeEvent<HTMLInputElement>
```

`any` silently disables type checking for everything downstream. Prefer `unknown` + type narrowing, or explicit interfaces.

---

## Pattern 7: useEffect for Derived State

AI often uses `useEffect` to keep a second state value in sync with a first. This is almost always wrong.

```tsx
// BAD - AI pattern
const [items, setItems] = useState([]);
const [count, setCount] = useState(0);
useEffect(() => {
  setCount(items.length); // unnecessary, causes extra render
}, [items]);

// GOOD
const count = items.length; // just derive it
```

---

## Pattern 8: Index as Key

When AI generates list rendering, it often uses array index as key.

```tsx
// BAD
items.map((item, i) => <Item key={i} {...item} />)

// GOOD
items.map((item) => <Item key={item.id} {...item} />)
```

Index keys break when items are added, removed, or reordered — React can't tell which DOM node corresponds to which item.

---

## Pattern 9: Hardcoded Configuration

AI bakes in values that should come from environment variables, constants files, or props.

**What to look for:**
- API URLs hardcoded as strings instead of `process.env.REACT_APP_API_URL`
- Magic timeout values (3000ms)
- Hardcoded user roles, feature flags, or color values
- Repeated string literals that should be constants

---

## Pattern 10: Over-fetching / No Caching

AI writes `useEffect` data fetches with no consideration for:
- De-duplication (same data fetched by multiple components)
- Stale-while-revalidate patterns
- Cache invalidation

In most React codebases this is handled by React Query, SWR, RTK Query, or Apollo. If the codebase uses one of these, AI-generated raw `fetch` in `useEffect` is a pattern mismatch.

---

## Pattern 11: dangerouslySetInnerHTML Without Sanitization

AI sometimes uses `dangerouslySetInnerHTML` to render user-provided or API-returned HTML content without sanitizing first. This is a direct XSS vector.

```tsx
// BAD
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// GOOD
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
```

---

## Pattern 12: Implicit Prop Mutation

AI occasionally mutates props or the objects/arrays passed as props. In React this causes subtle bugs since React doesn't re-render on mutations.

```tsx
// BAD
props.items.push(newItem); // mutates parent's array
props.user.name = 'Updated'; // mutates parent's object

// GOOD
setItems([...items, newItem]);
```
