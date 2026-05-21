# Python — clean-code-guard reference

Python-specific patterns and gotchas. Pairs with the cross-language guidance in `SKILL.md` and
overlaps with `python-quality-guard` (which goes deeper on tooling and style). Read both when
working on substantial Python code.

## Type hints

- **Every public function signature gets types.** Internal helpers too, unless they're trivial
  one-liners.
- **Modern syntax** (Python 3.10+): `list[int]`, `dict[str, User]`, `X | None`.
- `Optional[X]` is fine but `X | None` is now idiomatic.
- Use `TypedDict` for dict-shaped data crossing a boundary; use `@dataclass` for in-process
  values; use `pydantic` for validated I/O at the edge.
- Generics with `TypeVar` (PEP 695 syntax `def f[T](x: T) -> T:` if 3.12+).
- `Final` for module-level constants: `MAX_RETRIES: Final[int] = 5`.

```python
# Good
def renew_session(user_id: UserId, *, ttl: timedelta = DEFAULT_TTL) -> Session:
    ...

# Smell — no signal about what's in or out
def renew(u, ttl=None):
    ...
```

## Dataclasses vs classes vs pydantic

- **`@dataclass(frozen=True, slots=True)`** for value objects — immutable, comparable, cheap.
- **Plain class** when there's real behavior (methods that mutate or compute over state) and
  identity matters.
- **`pydantic.BaseModel`** at trust boundaries: HTTP request/response, config files, queue
  messages. Don't use pydantic for every internal model — it's runtime validation overhead and
  couples your domain to a framework.

## Async

- **Don't mix sync and async naively.** A blocking call inside `async def` stalls the event
  loop. Wrap blocking IO with `asyncio.to_thread()` or use the async client.
- **Always `await`** coroutines. A bare `coro()` in async code is a silent bug.
- **`asyncio.gather()`** for parallel; **`asyncio.TaskGroup`** (3.11+) when you want exception
  semantics that match a `try` block.
- **Name** async functions the same as sync ones — `fetch_user`, not `fetch_user_async`. The
  `async def` already says so.

## Exceptions

- **Define a base exception per package**: `class FooError(Exception): ...`. Subclass it for
  specific failure modes. Callers can then `except FooError` to catch anything from your library.
- **Wrap and re-raise with context**: `raise FooError("during step X") from e`. The `from e`
  chains the cause so tracebacks stay useful.
- **Never `except:` bare.** `except Exception:` is also a smell unless you immediately re-raise
  or log-and-reraise. Catch specifically.
- **No silent swallowing.** If you really want to ignore an error, write a one-line comment
  explaining why.

```python
# Bad
try:
    do_thing()
except:
    pass

# Better
try:
    do_thing()
except TransientNetworkError:
    pass  # safe to drop — caller will retry on next tick
```

## Module layout

- `__init__.py` defines the **public surface** with `__all__` or explicit re-exports. Anything
  not re-exported is considered private even without the underscore.
- One concept per module. Don't make `utils.py` — name the module by what it provides
  (`retry.py`, `currency.py`, `timestamps.py`).
- Internal helpers prefixed `_`. Internal modules prefixed `_` too (`_internal.py`).

## Mutable default arguments

Classic Python footgun:

```python
# BUG
def append_item(x, items=[]):
    items.append(x)
    return items

# Fix
def append_item(x, items=None):
    items = items if items is not None else []
    items.append(x)
    return items
```

## Comprehensions and pipelines

- List/dict/set comprehensions for *transformations*; loops for *side effects*.
- Stop nesting comprehensions past two levels — it's unreadable. Break into named generators.
- For multi-step transforms, prefer named intermediate variables over a long chained
  comprehension. Readers can debug a sequence; they can't debug a one-liner.

## Tooling baseline

Assume these unless told otherwise:

- **ruff** for lint + format (replaces black, isort, flake8, pyupgrade)
- **mypy** or **pyright** for type checking
- **pytest** for tests
- **uv** or **poetry** for dependency management

If `pyproject.toml` exists, respect what's configured. Don't add a competing config.

## Common smells specific to Python

- `from foo import *` — pulls in everything, breaks tooling, makes provenance opaque.
- `eval` / `exec` on user input — security hole and unreadable.
- `globals()` / `setattr()` to "be dynamic" — almost always wrong outside metaprogramming
  libraries.
- Decorators that change a function's signature without `@functools.wraps` — breaks
  introspection and tracebacks.
- `print()` in library code — use `logging`.
- `assert` for production checks — `python -O` strips them. Use real exceptions.
