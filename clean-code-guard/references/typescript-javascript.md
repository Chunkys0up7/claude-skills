# TypeScript / JavaScript — clean-code-guard reference

Patterns and gotchas for TS and JS code. TS is the default — if a project is plain JS, treat it
as TS-without-the-types and use JSDoc to compensate.

## tsconfig — non-negotiable settings

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

- `strict: true` is the floor. Anything less and the type system is lying to you.
- `noUncheckedIndexedAccess` — `arr[i]` becomes `T | undefined`. Saves real bugs.
- `noImplicitOverride` — catches drift when a parent class renames a method.
- `exactOptionalPropertyTypes` — distinguishes `{ x?: string }` from `{ x: string | undefined }`.

## `any` is a smell

- `any` opts out of the type system. If you reach for it, you've given up on the proof.
- Use `unknown` when you don't know the type; narrow with type guards before use.
- `as` casts are a yellow flag — you're overriding the compiler. Comment *why*.
- `as unknown as Foo` is a red flag — you're forcing it through. Almost always a missing model.

```ts
// Bad
const data: any = JSON.parse(raw);
console.log(data.user.name);

// Better
const data: unknown = JSON.parse(raw);
if (isUserPayload(data)) {
  console.log(data.user.name); // narrowed
}
```

## Discriminated unions over enums

For type-safe state, prefer tagged unions:

```ts
type FetchState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };
```

The compiler now forces you to handle every case. Switch on `.status` and get exhaustiveness
checking with `satisfies never`.

Plain TS `enum` has runtime quirks (string vs numeric, bidirectional maps). Prefer `as const`
objects:

```ts
const Status = { Active: "active", Pending: "pending" } as const;
type Status = (typeof Status)[keyof typeof Status];
```

## Branded types for IDs

Plain `string` for IDs lets you swap a `UserId` for an `OrderId` silently. Brand them:

```ts
type Brand<T, B> = T & { readonly __brand: B };
type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;
```

Now the compiler catches accidental mix-ups.

## Module exports

- Prefer **named exports** over `export default`. Default exports rename freely across the
  codebase, lose autocomplete on import, and break tooling refactors.
- **One responsibility per module.** Same rule as Python — no `utils.ts`.
- Public surface is what's exported from a `package`'s `index.ts`. Avoid deep imports from
  outside (`import { X } from 'pkg/dist/internal/x'`) — that's reaching past the public surface.

## Immutability

- `readonly` on object properties when the field shouldn't change.
- `ReadonlyArray<T>` (or `readonly T[]`) for parameters you won't mutate.
- `Readonly<T>` to wrap a whole type.
- `const` by default; `let` only when you genuinely re-bind.
- Don't mutate function arguments. If you need a modified copy, return one.

## async / await

- **Don't mix `.then()` chains with `await`** in the same function. Pick one.
- **Always handle rejection.** A floating Promise that rejects unhandledly will crash modern
  Node.
- `Promise.all` for parallel; `Promise.allSettled` when you need partial success;
  `Promise.race` rarely.
- `for await (const x of stream)` for async iteration; don't reach into the stream manually.

## Error handling

Two valid patterns — pick one per layer and stick to it:

1. **Throw** — idiomatic JS. Use custom error classes (`class FooError extends Error`). Wrap
   with cause: `throw new FooError("during X", { cause: e })`.
2. **Tagged result** — Rust-style. Useful at boundaries with strict contracts:
   ```ts
   type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
   ```

What you must NOT do: `try { ... } catch (e) {}`. Empty catch is silent failure.

## React / Next-specific (when applicable)

- Don't put a `useEffect` in to do what derived state can do. If a value is computed from props
  or state, just compute it.
- Don't pass setters down 4 levels — that's coupling. Lift state to the closest common parent,
  or use context for genuinely shared state, or a state library.
- `'use client'` only on components that genuinely need browser APIs or interactivity. Default
  to server components.
- `key` on lists: stable IDs, not array indices.

## Common smells specific to TS/JS

- `// @ts-ignore` without a follow-up comment explaining *why* and *when to remove*.
- `Object.assign(this, opts)` constructor — opaque, untyped, breaks autocomplete.
- Truthiness checks on numbers (`if (count)` misses `0`).
- `==` instead of `===`.
- Mutating React state directly (`state.items.push(x)`).
- `Array.prototype.forEach` when you want a transformation — use `map` and capture the result.
- `console.log` left in production code — use a real logger.

## Tooling baseline

- **eslint** with `@typescript-eslint`
- **prettier** for formatting
- **tsc --noEmit** in CI
- **vitest** / **jest** for tests
- **pnpm** for package management (or whatever the project uses; don't fight it)
