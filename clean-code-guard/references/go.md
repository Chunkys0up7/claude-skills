# Go — clean-code-guard reference

Go is opinionated by design — many of these patterns are non-negotiable in the community.

## Errors

- **Return errors, don't panic.** `panic` is for truly unrecoverable bugs (nil deref on a
  required dependency at startup). Libraries must not panic.
- **Wrap with context** using `%w`:
  ```go
  if err != nil {
      return fmt.Errorf("renewing session for user %s: %w", userID, err)
  }
  ```
- **`errors.Is` / `errors.As`** for inspecting wrapped errors. Don't string-compare error
  messages.
- **Sentinel errors** (`var ErrNotFound = errors.New("not found")`) for callers to match on.
- **Don't ignore errors with `_`** unless you can articulate *why* it's safe. Add a comment.

```go
// Bad
data, _ := io.ReadAll(resp.Body)

// Better
data, err := io.ReadAll(resp.Body)
if err != nil {
    return fmt.Errorf("reading response body: %w", err)
}
```

## Interfaces

- **Small interfaces** — Go's mantra: "the bigger the interface, the weaker the abstraction."
  `io.Reader` is one method. That's the bar.
- **Define interfaces at the consumer**, not the producer. If `package billing` needs to look up
  users, it defines its own `UserLookup` interface and the user package implements it
  incidentally.
- **No interface explosion** — don't define an interface for every struct "in case you mock it
  later." Add the interface when you have a second implementation or a real testing need.

## Package layout

- **Avoid `util`, `common`, `helpers`, `shared`** as package names. They're buckets, not
  abstractions. Name by capability: `retry`, `timestamps`, `currency`.
- **Package name = directory name** (with rare exceptions).
- **Internal code** in `internal/` — Go enforces that nothing outside the module can import it.
  Use this to mark genuine internals.
- **`cmd/<name>`** for binaries; the rest of the module is libraries.

## Composition over inheritance

Go forces this — embed structs and interfaces. Don't fight it.

```go
type Logger struct { ... }

type Service struct {
    Logger        // embedded — Service gets Logger's methods
    db *sql.DB
}
```

## Context

- **`ctx context.Context` is the first parameter** for anything that can block, do IO, or be
  cancelled.
- **Don't store contexts in structs.** Pass them through as function arguments.
- **Always check `ctx.Done()`** in long loops or honor cancellation via the operations you call.
- **Don't use `context.Background()` deep in the call tree** — that's a code smell. Receive a
  context from above.

## Concurrency

- **Goroutines need a clear lifecycle.** Who owns it? When does it stop? If you can't answer,
  you have a leak.
- **Channels for ownership transfer; mutexes for protecting state.** Both are tools — neither is
  always right.
- **`sync.WaitGroup`** for "wait for N things"; **`errgroup.Group`** when those things can fail
  and you want first-error semantics.
- **Don't share without synchronization** — `go test -race` should pass.

## Naming

- **`MixedCaps`** for exported identifiers; **`mixedCaps`** for unexported. No underscores.
- **Short names for short scopes** (`i`, `r`, `err`); long names for long scopes
  (`activeSessionCount`).
- **Receivers**: one or two letters; same letter across all methods on a type.
- **`Get` is rarely needed** — `user.Name` is fine; `user.GetName()` is Java-ese.

## Common smells specific to Go

- `init()` doing non-trivial work — opaque, ordering-dependent, hard to test.
- Empty interface `any` (or `interface{}`) when you mean a real type — type switches everywhere
  are a smell.
- Returning `*Foo` when `Foo` would do — only return pointers when you need mutation, identity,
  or to avoid expensive copies.
- A package depending on its caller (cyclic imports — Go won't compile, but the urge means the
  abstraction is wrong).
- Long parameter lists — Go has no named arguments, so >4 params is a real readability hit. Use
  a config struct.

## Tooling baseline

- **gofmt** / **goimports** (not optional)
- **golangci-lint** with a reasonable preset
- **`go test -race`** in CI
- **`go vet`** in CI
