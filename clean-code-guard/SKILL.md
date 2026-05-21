---
name: clean-code-guard
description: |
  Preventative cross-language code-quality guardrail. Fires BEFORE and DURING any task that will
  produce more than ~20 lines of new code, refactor existing code, design a module, or review code
  — across TypeScript, JavaScript, Python, Go, Rust, Java, and C#. Catches "vibe coding"
  pathologies as they happen: sprawl (files/classes/functions exceeding sane limits), god objects
  mixing IO + business logic + presentation, mixed abstraction levels, deep nesting, magic values,
  boolean-parameter hell, hidden coupling via deep/private imports, missing type annotations or
  docstrings, premature abstraction, dead code, stale TODOs, and comments that restate code
  instead of explaining why.
  Triggers on phrases like: "build a feature", "add a class", "write a function", "implement X",
  "refactor this", "design a module", "review my code", "is this clean?", "this file is getting
  big", "should I split this", "structure this project", "tidy this up", "clean up the
  architecture", "what's the right abstraction", and any request that will produce a non-trivial
  amount of new code.
  Use this skill in THREE moments: at the start of a code-writing task to set quality goals,
  mid-stream as a check on progress, and at the end as a final review pass.
  Distinct from `simplify` (post-hoc cleanup of changes already made) and `python-quality-guard`
  (Python-specific style and tooling) — clean-code-guard is the broader, earlier, cross-language
  discipline layer. When all three apply, run them together; they reinforce each other.
  Skip only for: pure syntax lookups ("what's the syntax for X?"), reading-only tasks, trivial
  one-liners (rename a variable, add a print statement), or tasks where the user explicitly says
  "just hack it in, I'll clean it up later."
---

# clean-code-guard

A preventative quality bar for code Claude writes or reviews. Stops the slow drift toward
800-line god classes, 12-arg functions, magic-number soup, and comments that lie.

This is the **discipline layer**: broader than `python-quality-guard` (Python-specific) and
earlier in the lifecycle than `simplify` (post-hoc cleanup). The three skills are complementary.

## Core principle: flag and discuss, not block

When you spot something in this skill, **surface it, propose the fix, then continue** — don't
grind the work to a halt for a borderline call. Quality bars are heuristics, not laws.

> A 410-line file with one clear purpose is fine.
> A 380-line file doing five unrelated things is not.

Judgment beats line counts. The thresholds below exist so you have a *reason to look* — not a
reason to refactor automatically.

## When to invoke this skill

Three moments. Don't skip the first one.

### 1. Pre-flight — before writing

Before writing more than ~20 lines, answer these in your head (or out loud, for non-trivial work):

- **One job**: What's the single responsibility of the thing I'm about to write? Can I name it in
  one sentence without using "and"?
- **Location**: Existing file or new one? If new, what module/package — and why there?
- **Dependencies**: Will I need to import from another module's internals or private symbols?
  (If yes → restructure first, don't reach through.)
- **Public surface**: Which symbols are exported; which are private?
- **Error contract**: What can fail? Does this layer handle errors, propagate them, or never fail?

For anything non-trivial, **surface this as a 3–5 line plan and get a nod** before writing. This
is the cheapest possible refactor.

### 2. Mid-stream check — every ~100 lines or 5–10 minutes

Quick scan:

- File crossed 400 LOC? Class crossed 200? Function crossed 50?
- Just wrote the same logic for the third time? Extract.
- Added a boolean parameter? Could it be an enum or two functions?
- Nesting deeper than 3 levels? Guard clause it.

### 3. Final pass — before declaring done

Run the 15 checks below. Flag anything borderline in the response to the user.

---

## The 15 vibe-coding pathologies

For each: the smell, why it hurts, the threshold, the standard move. Explanations matter more
than thresholds — pick up the *intent*, then judge.

### 1. Size sprawl

- **Thresholds**: file > 400 LOC · class > 200 LOC · function > 50 LOC · module > ~10 top-level
  exports.
- **Why it hurts**: cognitive load grows worse than linearly with length — when readers can't fit
  it in their head, they stop reasoning and start pattern-matching, which is how bugs ship.
- **Move**: Extract Function / Extract Class / Extract Module. Split by *responsibility*, not by
  line count — a 50-line group of tightly cohesive helpers is one unit, not five.

### 2. God objects (no single responsibility)

- **Smell**: a class doing IO + business logic + formatting. Names like `Manager`, `Handler`,
  `Processor`, `Service`, `Helper` with no qualifier — these are usually buckets, not abstractions.
- **Why it hurts**: every reason to change the system becomes a reason to change this one class.
  Diffs collide. Tests need a dozen mocks.
- **Move**: Separate by *axis of change*. IO layer ← domain layer ← presentation layer. Each in
  its own file with a name that says what it owns.

### 3. Mixed abstraction levels

- **Smell**: a function with high-level orchestration sitting next to byte-fiddling.
  ```python
  def ship_orders():
      orders = fetch_orders()
      for o in orders:
          o.items.sort(key=lambda i: i.price * 1.08)  # ← what is 1.08?
          send_to_carrier(o)
  ```
- **Why it hurts**: the reader context-switches between strategy and tactics on every line.
- **Move**: extract the low-level bit with a name that explains it.
  `tax_inclusive_price(item)`, `sort_by_tax_inclusive_price(items)`. The orchestrator now reads
  as a story.

### 4. Duplication — the Rule of Three

- **Threshold**: the same 5+ lines of logic appearing **three or more** times.
- **Why it hurts**: bug fixes get applied to one copy and forgotten in the others.
- **Move**: Extract Function. **But**: don't extract on the *second* occurrence — wait for the
  third. Two is coincidence; three is a pattern. And resist extracting things that *look*
  similar today but will diverge tomorrow (e.g., two validators with the same shape but
  different rules incoming).

### 5. Missing annotations

Type information is the first layer of documentation; docstrings are the second.

- **Python**: type hints on every public signature; return types; dataclass fields. Docstrings on
  public classes and non-trivial functions, explaining *why* the thing exists.
- **TypeScript**: `strict: true`. `any` is a smell — use `unknown` and narrow. JSDoc on exported
  APIs.
- **JavaScript (no TS)**: JSDoc `@param {type}` and `@returns {type}` on exported functions.
- **Go**: doc comment on every exported identifier (`// Foo does X.` — the comment starts with
  the name).
- **Rust**: `///` doc comments on every `pub` item.

See language-specific guides under `references/` for details.

### 6. Naming

- **Smells**: `data`, `info`, `helper`, `util`, `manager`, `temp`, `result`, `obj` as standalone
  names. Abbreviations not from the domain (`usrCtxMgr`). Inconsistent verbs (`getUser` in one
  file, `fetchUser` in another, `loadUser` in a third).
- **Move**: Name by what it **is** (`UserSession`) or what it **does** (`renewSession`). Pick one
  verb per concept and stick to it codebase-wide — `get` / `fetch` / `load` / `find` each mean
  different things, choose deliberately:
  - `get*` — in-memory, fast, no IO
  - `fetch*` — over the network
  - `load*` — from disk or DB
  - `find*` — may return nothing (null/Option)

### 7. Magic values

- **Smell**: `if retries < 5`, `time.sleep(0.250)`, `headers["X-API-Key"]`, `status == "ACTIVE"`.
- **Move**: Promote to a named constant near the top of the module (or a `config` module).
  Comment *why* the value (`# matches upstream's 5s timeout`). Strings used as enum values →
  actual enums.

### 8. Deep nesting

- **Threshold**: > 3 levels of `if` / `for` / `while` / `try`.
- **Move**: Guard clauses (return early on the error or empty case). Extract Function. Replace
  Conditional with Lookup Table or Strategy. If the nesting reflects a real state machine,
  *name* the states and write it as one.

### 9. Boolean parameter hell

- **Smell**: `do_thing(true, false, true)` at the call site — readers can't tell what the bools
  mean without jumping to the definition. Easy to swap by mistake.
- **Move**: Replace with an enum (`Mode.DRY_RUN`), a tagged union, or — often best — split into
  two functions: `do_thing_dry()` and `do_thing_live()`.

### 10. Dead code and stale TODOs

- **Smell**: commented-out blocks "in case we need them"; unreferenced exports; TODOs older than
  ~6 months with no owner.
- **Move**: **Delete it.** Git remembers. If a TODO is real, file an issue and put the link in
  the comment: `// TODO(GH-1234): switch to v2 API once available`.

### 11. Hidden coupling

- **Smell**: importing from another module's `_private` symbols, deeply-nested paths
  (`from foo.bar.baz.qux.internal import X`), or reaching through getters to mutate fields.
- **Why it hurts**: you've coupled to the *refactor-ability* of someone else's internals — when
  they reorganize, you break.
- **Move**: Ask the upstream module to export it properly, or wrap it in a local adapter so the
  coupling is in one place you can later patch.

### 12. Error handling consistency

- **Smell**: bare `except:` / `catch (e) {}` swallowing everything; mixing return-error-codes
  with throw-exceptions in the same module; "silent fallback" that hides bugs.
- **Rule**: every layer must either **handle** an error (do something specific) or **propagate**
  it. Never catch-and-log-and-continue without an explicit, documented decision.
- **Move**: catch specific exception types; wrap and re-raise with context
  (`raise FooError("during X") from e`); use a `Result` type in languages that have one.

### 13. Premature abstraction (the opposite trap)

- **Smell**: an interface with one implementation; a Factory creating exactly one concrete type;
  a 4-level inheritance chain on plain-data classes; layers added "in case we need to swap it
  later."
- **Why it hurts**: every layer of indirection is a layer the reader has to traverse to
  understand a 3-line operation.
- **Move**: **Inline the abstraction.** Replace inheritance with composition. Add the abstraction
  back the *day* you need the second implementation, not before. This is dual to #1 — too many
  small things is as bad as one huge thing.

### 14. State mutation discipline

- **Smell**: shared module-level mutable state; functions that silently mutate their arguments;
  long-lived objects passed by reference and mutated by multiple callers.
- **Move**: prefer immutability where reasonable — `@dataclass(frozen=True)`, `readonly`,
  `const`, `Readonly<T>`. When mutation is genuinely the right call, **localize it**: one owner
  per piece of state, document it, expose mutation through named methods rather than direct
  field access.

### 15. Comments that lie or repeat

- **Smell**: `// increment counter` next to `counter++`. `# returns the user` on
  `def get_user(...) -> User:`. Outdated comments that contradict the code beneath them.
- **Rule**: **Comments explain *why*, not *what*.** Why this algorithm and not the obvious one?
  Why this constant? What invariant must hold? What did we try that didn't work and why?
- **Move**: Delete the noise. Write the *why* the next reader will thank you for. The code
  itself should explain *what* — if it doesn't, rename or refactor, don't comment.

---

## The refactor menu

When you flag something, the first-line move is usually one of these. Full worked examples in
[`references/refactor-menu.md`](./references/refactor-menu.md).

| Smell                          | First-line move                                |
| ------------------------------ | ---------------------------------------------- |
| Long function                  | Extract Function                               |
| Long class                     | Extract Class — split by responsibility        |
| Long file                      | Extract Module                                 |
| Too many params (>5)           | Introduce Parameter Object                     |
| Boolean params                 | Replace with Enum / split into two functions   |
| Deep nesting                   | Guard clauses → Extract Function               |
| Repeated logic (≥3 occurrences)| Extract Function                               |
| Conditional chain on type tag  | Replace with Polymorphism or Lookup Table      |
| Magic number / string          | Introduce Named Constant                       |
| Function in wrong class/module | Move Function / Move Field                    |
| God class                      | Split by axis of change                        |
| Over-abstracted                | Inline Function / Collapse Hierarchy           |
| Mutable shared state           | Make immutable, or localize ownership          |
| Mixed abstraction              | Extract lower-level helper with a clear name   |
| Comment restates code          | Delete comment; rename code to be self-evident |

---

## Language-specific guidance

Read the relevant file before substantive code review or design work in that language:

- **Python** → [`references/python.md`](./references/python.md)
- **TypeScript / JavaScript** → [`references/typescript-javascript.md`](./references/typescript-javascript.md)
- **Go** → [`references/go.md`](./references/go.md)
- **Rust** → [`references/rust.md`](./references/rust.md)
- **Java / C#** — many of the same principles; cross-reference the TypeScript guide for
  type-system idioms and the Python guide for class design.

---

## What this skill is NOT

- **Not a linter.** Real linters (ruff, eslint, gofmt, clippy) catch syntactic and style issues;
  this skill catches *design* issues. Run both — they don't overlap.
- **Not a blocker.** If a heuristic conflicts with a real reason, the real reason wins. Surface
  the tradeoff explicitly and proceed.
- **Not a replacement** for `simplify` (post-hoc cleanup) or `python-quality-guard` (Python style
  and tooling). When they overlap, run them together.
- **Not a style guide.** No position on tabs vs spaces, snake_case vs camelCase (defer to
  language convention), or import ordering. That's lint territory.

---

## Output format when reviewing existing code

When using this skill to review code (not to write it), structure the response as:

```
**Quality pass: <file or scope>**

✓ Clean
- <what's good — be specific, this teaches by reinforcement>

⚠ Flags
- [must-fix] <issue>: <one-line explanation> → <proposed move>
- [should-fix] <issue>: <explanation> → <move>
- [nit] <issue>: <explanation> → <move>

? Discuss
- <borderline calls where the right answer depends on intent — ask before changing>
```

Severities:
- **must-fix** — will bite the team (broken contract, silent error swallowing, deep coupling).
- **should-fix** — will accumulate (long file, missing types, magic values).
- **nit** — preference (naming style, comment phrasing).

When using this skill while *writing* code, you don't need the formal output — just write the
clean version and call out the non-obvious decisions in the response.
