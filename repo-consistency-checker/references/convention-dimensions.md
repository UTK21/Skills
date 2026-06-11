# Convention Dimensions Reference

For each dimension below: identify the dominant pattern in the EXISTING codebase first (with file:line evidence), then check whether the new/changed code follows it. Mark a dimension N/A if it doesn't apply to the files under review.

Each dimension lists what to look for generally, plus specifics for the three "starter" stacks this skill ships with: **JS/TS/React**, **Python**, and **Java**. The same underlying questions apply to other languages too — adapt using the same logic (what does *this* repo already do for *this* concern?).

---

## 1. Naming conventions

> **This dimension is mandatory and must always be reported on, even when everything else scores well.** Casing mismatches are cheap to introduce, cheap to fix, and the single most common AI-introduced inconsistency. List every instance found with a file:line citation.

- **JS/TS/React**:
  - File naming: PascalCase components (`UserCard.tsx`) vs kebab-case (`user-card.tsx`) vs camelCase
  - Component name vs file name should match
  - Variables/functions: camelCase, with prefix conventions already in use (`handle*` for event handlers, `is*`/`has*`/`should*` for booleans, `use*` for hooks, `on*` for prop callbacks)
  - Constants: `UPPER_SNAKE_CASE` vs camelCase for module-level constants
  - Types/interfaces: `PascalCase`, and whether the repo suffixes prop types (`ButtonProps`)

- **Python** (PEP 8 baseline — confirm against actual repo usage):
  - Modules/files and functions/variables: `snake_case`
  - Classes and exceptions: `PascalCase` (e.g. `UserService`, `UserNotFoundError`)
  - Constants: `UPPER_SNAKE_CASE`
  - "Private"/internal attributes and methods: leading underscore (`_repository`, `_helper`)
  - A `camelCase` method, parameter, or variable in an otherwise `snake_case` module is a clear deviation — flag it explicitly.

- **Java**:
  - Classes, interfaces, enums, records: `PascalCase`
  - Methods, fields, local variables, parameters: `camelCase`
  - Constants (`static final`): `UPPER_SNAKE_CASE`
  - Packages: all lowercase, no underscores, dot-separated
  - A `PascalCase` method name (`GetOrder`) or `snake_case` parameter (`order_id`) in an otherwise camelCase Java file is a clear deviation — flag it explicitly.

## 2. File & folder structure

- **JS/TS/React**:
  - Where do files of this kind live? (`components/`, `features/<feature>/`, co-located with the thing that uses them, etc.)
  - **Co-location**: are styles/tests/types co-located with the component (`Button.tsx`, `Button.module.css`, `Button.test.tsx` in one folder) or kept in parallel trees (`src/components/`, `src/styles/`, `__tests__/`)?
  - **Barrel files**: does the repo re-export via `index.ts`? Is the new module included consistently?
  - One component/export per file vs. multiple — match the surrounding convention.

- **Python**:
  - Package layout: `src/<package>/` vs flat `<package>/` at repo root
  - `__init__.py` usage — does the repo re-export the public API there, or import directly from submodules?
  - One class/concern per module vs grouped modules (e.g. all exceptions in `exceptions.py` vs co-located with the class that raises them)
  - Does `tests/` mirror the package structure (`tests/services/test_order_service.py` for `app/services/order_service.py`)?

- **Java**:
  - Standard Maven/Gradle layout: `src/main/java/<package>/...` and `src/test/java/<package>/...` mirroring each other
  - Package-by-layer (`controller/`, `service/`, `repository/`, `model/`, `exception/`) vs package-by-feature — match whichever the repo uses
  - Is the new class in the package that mirrors where similar classes (other services, other repositories) live?

## 3. Code / module / class structure

- **JS/TS/React**:
  - Function declarations (`export function Foo()`) vs. arrow function components (`const Foo = () => {}`)
  - Default export vs named export — match sibling files of the same kind
  - Where is the props type defined — inline above the component, in a shared `types.ts`, or imported?
  - File section ordering (hooks, then handlers, then derived values, then JSX) — does the new file roughly follow it?

- **Python**:
  - Class-based vs functional/module-level design for similar concerns
  - `@dataclass` / Pydantic models / `TypedDict` vs plain classes with manual `__init__` for data carriers — match the dominant choice
  - Member ordering within a class (`__init__`, properties, public methods, private `_methods`) — does the new class follow the same shape as sibling classes?
  - Decorator usage (`@staticmethod`, `@classmethod`, `@property`) — consistent with similar classes?

- **Java**:
  - Member ordering (fields → constructor(s) → public methods → private helper methods) — match sibling classes
  - Constructor injection vs field/setter injection (see also Dimension 5) reflected in class structure
  - Builder pattern, fluent setters, or plain constructors — match what similar classes do
  - Records vs classes for simple data carriers (DTOs) — match the dominant choice
  - Interface-first design (service implements an interface) vs concrete classes only — match the repo's pattern

## 4. Imports & dependencies

- **JS/TS/React**:
  - Absolute/aliased imports (`@/components/Button`) vs relative (`../../components/Button`) — does `tsconfig`/`jsconfig` define an alias the new file should use but isn't (or vice versa)?
  - Import grouping/order (external, then internal/aliased, then relative, then styles/assets) if enforced by lint config
  - Default vs named imports for the same library, used consistently
  - **New dependencies**: does the new code import a package not in `package.json`/lockfile where an existing dependency already covers the need (e.g. adding `styled-components` when the repo uses CSS Modules everywhere, or `lodash` for something the repo never uses lodash for)?

- **Python**:
  - Import order/grouping per PEP 8 / isort: standard library, then third-party, then local/first-party — separated by blank lines
  - Absolute imports (`from app.services.user_service import UserService`) vs relative (`from .user_service import UserService`) within the package — match the dominant style
  - `from x import *` — flag if the repo otherwise avoids it
  - **New dependencies**: does the new code import a package not declared in `pyproject.toml`/`requirements*.txt` where an existing dependency already covers the need?

- **Java**:
  - Import grouping/order (`java.*`, `javax.*`, third-party, then project packages) — match what existing files do
  - Wildcard imports (`import com.example.app.model.*`) — flag if the repo otherwise uses explicit imports
  - Static imports — used consistently with how the repo does (or doesn't) use them
  - **New dependencies**: does the new code use a library not declared in `pom.xml`/`build.gradle*` where an existing dependency already covers the need?

## 5. State / dependency & resource management

- **JS/TS/React**:
  - **Local state**: `useState` vs `useReducer` — does the new code's choice match how similarly-complex state is handled elsewhere?
  - **Shared/global state**: Context, Redux/Redux Toolkit, Zustand, Jotai, Recoil, MobX — is the new code introducing a *different* mechanism than the repo already uses for cross-component state?
  - **Server/remote state**: React Query / SWR / RTK Query / Apollo vs. raw `useEffect` + `fetch`/`axios` — one of the most common AI-introduced mismatches.
  - **Derived state**: does the new code store derived values in state and sync via `useEffect` where the rest of the repo just computes them inline?

- **Python**:
  - Dependency injection style — constructor parameters (manual DI) vs a framework mechanism (`fastapi.Depends`, `dependency_injector`, Django apps registry) — match what sibling classes/handlers do.
  - Configuration/settings management — `pydantic.BaseSettings`/`os.environ`/a central `config.py` — does new code read config the same way, or hardcode/read env vars ad hoc?
  - Resource lifecycle — context managers (`with open(...)`, `with session_scope()`) for files/DB sessions/locks — match existing usage.

- **Java**:
  - Dependency injection style — constructor injection (preferred in most modern Spring code) vs field injection (`@Autowired` on a field) vs setter injection — match what sibling `@Service`/`@Component` classes do. Introducing field injection where the rest of the repo uses constructor injection is a notable deviation.
  - Bean scope / singleton conventions — match existing `@Service`/`@Component`/`@Configuration` usage.
  - Transaction/session management — `@Transactional` placement, `EntityManager`/`Session` handling — match existing repository/service patterns.

Mark N/A for code where this doesn't apply (e.g. a pure algorithm/utility module with no shared state or dependencies).

## 6. Styling / presentation layer (UI-specific)

- **JS/TS/React**: CSS Modules, styled-components/Emotion, Tailwind utility classes, plain global CSS, or inline `style={{}}` — identify the dominant approach and flag a new approach introduced without justification. Check class naming convention (BEM-style, utility-first, semantic) and whether design tokens (theme object, CSS variables, Tailwind config) are used vs hardcoded raw values (`#fffae6`, `16px`).
- **Python / Java**: mark **N/A** for non-UI services. If the repo renders templates (Jinja2, Django templates, Thymeleaf, JSP), check that new templates follow the same templating conventions, layout/inheritance structure, and naming as existing ones.

## 7. Type system conventions

- **JS/TS/React**:
  - `interface` vs `type` for object/prop shapes — match the dominant choice
  - Use of `any`/`unknown` — does new code introduce `any` where the rest of the repo types precisely (or vice versa)?
  - Event handler typing (`React.ChangeEvent<HTMLInputElement>`) vs `any`
  - Generics naming (`T`, `TData`, descriptive names) and enum vs string-union usage

- **Python**:
  - Type hint coverage — is the rest of the codebase fully type-hinted (params + return types)? New code with no type hints next to fully-hinted siblings is a deviation.
  - `Optional[X]` vs `X | None` (PEP 604) — match whichever style the repo's Python version and existing code uses
  - Data shape conventions — `@dataclass`, Pydantic `BaseModel`, `TypedDict`, or plain dict — match the dominant choice for similar data
  - mypy/pyright strictness implied by config (`mypy.ini`, `pyproject.toml [tool.mypy]`) — does new code violate it (e.g. untyped defs when `disallow_untyped_defs = true`)?

- **Java**:
  - Generics usage and naming (`T`, `K`, `V` vs descriptive type parameter names) — match existing generic classes/methods
  - `Optional<T>` vs returning `null` for "may be absent" values — match the dominant pattern (e.g. repository methods returning `Optional<User>`)
  - Nullability annotations (`@Nullable`/`@NonNull`) if used elsewhere
  - Records vs Lombok-annotated POJOs vs manual getters/setters for data carriers — match the dominant choice

## 8. Async / error handling

- **JS/TS/React**:
  - Where do API calls live — inline in components, in hooks, or a dedicated `api`/`services` layer? New fetch logic should land in the same place similar existing logic does.
  - Error handling shape — try/catch + error state, error boundaries, toast/notification system, or a query library's `error` field — match the established shape.
  - Loading states — spinner, skeleton, boolean flag, or `isLoading` from a query library — match sibling components.
  - Cleanup/cancellation — `AbortController` or cleanup functions for subscriptions/timers, if siblings use them.

- **Python**:
  - Exception strategy — does the repo define custom exception classes (e.g. `UserNotFoundError(Exception)`) for domain errors? New code raising a bare `Exception("...")` or using a broad `except:`/`except Exception:` where siblings raise/catch specific custom exceptions is a deviation.
  - Comparisons — `is None`/`is not None` vs `== None` (PEP 8): a new `== None` next to existing `is None` checks is a deviation.
  - Context managers (`with`) for files, DB sessions, locks — match existing resource-cleanup patterns.
  - `async`/`await` with `asyncio` vs synchronous code — don't introduce async in an otherwise-sync module (or vice versa) without it being the established pattern for that layer.
  - Logging vs raising vs silently swallowing — match how sibling modules surface errors.

- **Java**:
  - Checked vs unchecked exceptions — does the repo have a custom exception hierarchy (e.g. `UserNotFoundException extends RuntimeException`)? New code throwing a generic `RuntimeException("...")` where siblings throw a specific domain exception is a deviation.
  - `Optional.get()`/`.orElseThrow(...)` — if siblings use `.orElseThrow(() -> new XyzNotFoundException(...))`, new code calling `.get()` directly (which throws an unchecked `NoSuchElementException` with no useful message) is a deviation.
  - `try-with-resources` for `AutoCloseable` resources — match existing usage.
  - Logging framework (SLF4J/Log4j via `private static final Logger log = ...`) vs `System.out.println`/`printStackTrace` — match existing usage.

## 9. Testing conventions

- **JS/TS/React**:
  - Test file location: co-located (`Button.test.tsx` next to `Button.tsx`) vs. a parallel `__tests__/`/`test/` tree
  - Testing library and query style: React Testing Library (`getByRole`, `getByLabelText`) vs `getByTestId`-heavy vs Enzyme
  - `describe`/`it` vs `test`, naming of test cases — match existing test files for the same kind of module

- **Python**:
  - pytest vs `unittest.TestCase` — match the dominant style
  - File naming (`test_*.py` or `*_test.py`) and location (`tests/` mirroring `app/`, or co-located)
  - Fixtures (`@pytest.fixture`) vs `setUp`/`tearDown` — match existing tests
  - Mocking style (`unittest.mock`, `pytest-mock`'s `mocker`) — match existing tests
  - Does a new module have a corresponding test module, the way sibling modules do?

- **Java**:
  - JUnit 4 (`org.junit.Test`) vs JUnit 5 (`org.junit.jupiter.api.Test`) — match the dominant version
  - `*Test.java` naming in `src/test/java/<mirrored package>` — does a new class have a corresponding test class the way siblings do?
  - `@BeforeEach`/`@Mock`/Mockito usage and Arrange-Act-Assert structure — match existing tests

## 10. Comments & documentation

- General: match the surrounding code's comment density and style — don't introduce a noticeably different documentation style for the same kind of code.
- **Python**: if public functions/classes elsewhere have docstrings (Google/NumPy/reST style), new public functions/classes should too.
- **Java**: if public classes/methods elsewhere have Javadoc (`/** ... */`), new public classes/methods should too.

## 11. Linting / formatting

- **JS/TS/React**: `eslint`/`prettier` — if `npm run lint`/`npx eslint <files>` can be run without side effects, run it on the changed files.
- **Python**: `black`/`ruff`/`flake8`/`isort`/`mypy`/`pylint` — check `pyproject.toml`/`setup.cfg`/`.flake8`/`ruff.toml` for the configured tools and run them on changed files if possible.
- **Java**: `checkstyle`/`spotless`/`google-java-format`/`PMD`/`SpotBugs` — check the build file for configured plugins and run them on changed files if possible.

In all cases: distinguish **new** violations introduced by the diff from pre-existing ones in modified files (compare against `git show HEAD:<path>`). Note any explicit config rule the new code violates even if the linter wasn't run.

## 12. Framework & architectural conventions

- **JS/TS/React**: routing convention (Next.js file-based routes, React Router route config) — does a new page/route follow the same structure and naming as existing ones? Navigation via `<Link>`/router helpers vs raw `<a>`/`window.location` — match existing usage.
- **Python**: web framework conventions — Django URLconf/views/serializers, FastAPI routers + `Depends` + Pydantic schemas, Flask blueprints. Does a new endpoint/view register and layer the same way existing ones do (same router/blueprint structure, same request/response model conventions)?
- **Java**: Spring (or similar) annotations and layering — `@RestController`, `@RequestMapping`/`@GetMapping`/`@PostMapping`, `@Service`, `@Repository`, `@Component`. Does a new controller/service/repository follow the same annotation usage and layering as existing ones?

## 13. Constants / configuration / magic values

- General: are repeated values (API base URLs, feature flags, role names, timeout durations, status strings) pulled from a shared constants/config/env-var location elsewhere in the repo? New code introducing the same kind of value inline (hardcoded) is a deviation.
- **JS/TS/React**: `.env` + `process.env`, dedicated `constants.ts`/`config.ts`
- **Python**: `.env` + `python-dotenv`/`os.environ`, `pydantic.BaseSettings`, `constants.py`
- **Java**: `application.properties`/`application.yml` + `@Value`/`@ConfigurationProperties`, constants interfaces/classes
