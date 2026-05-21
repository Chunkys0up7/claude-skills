# Rust — clean-code-guard reference

Rust forces a lot of these patterns at the compiler level. This guide is about what the compiler
*doesn't* catch.

## Result and Option

- **`Result<T, E>`** for fallible operations, **`Option<T>`** for nullable. Don't use sentinel
  values.
- **`?`** for propagation. Don't manually `match` and re-return unless you're transforming the
  error.
- **`.unwrap()` and `.expect()` are for prototypes and tests.** In production code, every unwrap
  is a future panic. Use `?` or handle the case explicitly.
- **Custom error types** via `thiserror`:
  ```rust
  #[derive(Debug, thiserror::Error)]
  pub enum SessionError {
      #[error("user {0} not found")]
      UserNotFound(UserId),
      #[error("database error: {0}")]
      Db(#[from] sqlx::Error),
  }
  ```
- **`anyhow::Result`** for binaries and high-level glue where you don't care about the error
  type. Don't use it in library APIs — callers can't match on it.

## Newtypes for IDs

Same idea as TS branded types — let the compiler distinguish things that share a primitive
representation:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UserId(pub Uuid);

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct OrderId(pub Uuid);
```

Now `fn renew(id: UserId)` won't accept an `OrderId`.

## Traits

- **Traits are the abstraction unit.** Prefer composition over inheritance (Rust doesn't have
  inheritance anyway).
- **Define traits at the consumer.** Same as Go — the module that needs the behavior owns the
  trait.
- **`dyn Trait` vs generics**: generics inline at compile time (fast, larger binary); `dyn Trait`
  uses a vtable (smaller binary, dynamic dispatch). Default to generics; reach for `dyn` when you
  need a heterogeneous collection or to break a recursive type.
- **Don't over-bound generics.** `T: Clone + Send + Sync + 'static` everywhere is a smell —
  push the bounds down to where they're actually required.

## Lifetimes

- **Name lifetimes meaningfully** when there's more than one: `'src`, `'borrow`, not `'a`, `'b`.
- **`'static` is not a free pass.** It means "lives for the program's lifetime" — use it only
  when that's actually true.
- **If lifetimes get hairy**, the design is often wrong. Try: owning instead of borrowing,
  `Arc<T>` instead of references, or restructuring so borrows don't cross the boundary.

## Ownership and cloning

- **`.clone()` to satisfy the borrow checker without thinking is a smell.** Pause and ask
  whether you can borrow, restructure, or move instead.
- That said, `.clone()` is fine when it's cheap (a small struct, an `Arc`) and the alternative
  is gymnastic — pragmatism over purity.
- **Prefer `&str` over `String` in function parameters** unless you genuinely need ownership.

## Modules and crates

- **One concept per module.** `mod user`, `mod session`, not `mod utils`.
- **`pub(crate)`** for code that's internal to the crate but shared across modules. Use it
  liberally — it tightens your public surface.
- **In a workspace**, small focused crates are better than one monolith. Crate boundaries are
  also compile-time boundaries — a small crate changes don't trigger a full rebuild.
- **`mod.rs` vs `module/mod.rs`** — both work; pick one style per project.

## Concurrency

- **`Send` and `Sync` are the floor.** If your types don't satisfy them, you can't share across
  threads — and the compiler will tell you.
- **`tokio::spawn`** for async tasks. Like goroutines, they need a clear lifecycle — who awaits
  the handle?
- **`Arc<Mutex<T>>`** for shared mutable state — but ask first if you can avoid sharing.
  Channels (`tokio::sync::mpsc`) are usually cleaner.
- **Don't `block_in_place` or `block_on` inside async code** without understanding the
  consequences.

## Macros

- **Prefer functions over macros.** Macros are for cases functions genuinely can't handle —
  variadic arguments, generating boilerplate from a DSL, compile-time validation.
- **Document macro inputs and expansions.** A macro that "just works" is a debugging nightmare.

## Common smells specific to Rust

- `unwrap()` / `expect()` outside `main`, tests, or genuine "this can never fail" cases.
- `#[allow(...)]` without a follow-up comment explaining why.
- `unsafe` blocks without a safety comment (`// SAFETY: ...`) stating the invariants that make
  the unsafe code sound.
- `RefCell<T>` everywhere — usually means the design wants `&mut` discipline you're working
  around.
- `String` parameters everywhere — `&str` is usually fine.
- Generic explosion (`fn f<T, U, V, W>` where most are unused).

## Tooling baseline

- **rustfmt** (not optional)
- **clippy** with at least `-W clippy::pedantic` — push back on individual lints if they're
  noisy, don't blanket-disable
- **`cargo test`** + **`cargo nextest`** for faster runs
- **`cargo deny`** for dependency hygiene in production crates
