# The integration plan

The plan that comes **before** code — the cheapest refactor you can possibly do.

The point isn't bureaucracy. It's that ~30 seconds of thinking about how a change fits into the
codebase catches the design issues that would otherwise become 2-hour rewrites mid-PR.

---

## When you need a plan

Plans aren't required for everything. Use judgment.

**Plan required:**
- Any change > ~20 lines of new code
- Any change touching > 1 file (other than a trivial rename)
- Any new abstraction (new class, new module, new service, new endpoint)
- Any change that affects a public surface (API, exported symbol, schema)
- Any change to security, auth, data integrity, or payments code

**Plan optional (use judgment):**
- Pure refactors with no behavior change (the diff itself is the plan)
- One-file additions of new internal helpers under 50 lines

**Plan not needed:**
- Typo fixes
- Comment / docstring updates
- Single-line bug fixes (still cite the spec/bug ID though)
- Rename a variable / move a constant

When in doubt, write a one-paragraph plan. It's faster than realizing mid-implementation that
you need to back out.

---

## The template

```markdown
**Change**: <one-line summary — what's the user-visible delta?>

**Spec items addressed**: R1, R3 (and X1 if out-of-spec)

**Existing code surfaces touched**
- `<path>` — <what changes here, briefly>
- `<path>` — <what changes here>

**New abstractions**
- `<Name>` — <one-line purpose>. Lives in `<path>`. Owns: <one-line>. Used by: <one-line>.

**Dependencies (must exist first)**
- R0 (X) — ✅ Done
- DB migration for `<table>` — needs writing as part of this change
- External: `<service>` must be reachable from the env

**Risks / conflicts**
- Conflicts with in-flight work on <other branch/file>
- Backward compat: <does this break existing callers / clients / persisted data?>
- Migration / rollout: <can we deploy without coordinating clients?>

**Test plan (tied to acceptance criteria)**
- R1 AC1 (<what>) → `tests/<path>::<test_name>`
- R1 AC2 (<what>) → same file::<test_name>
- R3 AC1 (<what>) → `tests/<path>::<test_name>`

**Rollout / migration** (if applicable)
- Feature flag: yes/no, default <value>
- Migration order: 1. deploy code with flag off, 2. run migration, 3. enable flag
- Rollback: <how — flag off? revert migration?>

**Out of scope (explicitly)**
- <thing the user might expect but isn't part of this change>
```

Not every section applies to every change. Skip sections that don't — the plan exists to
capture decisions, not to fill a form.

---

## Worked example 1 — adding an endpoint

**Change**: Add `POST /sessions` endpoint that creates a session for an authenticated user
and returns a JWT.

**Spec items addressed**: R1 (create session), partially R3 (audit log)

**Existing code surfaces touched**
- `app/api/index.ts` — register new route
- `app/models/user.py` — add `last_session_at: datetime | None` field
- `migrations/` — new migration for `sessions` table

**New abstractions**
- `SessionService` (`app/services/session.ts`) — owns session lifecycle (create, renew,
  expire, revoke). Used by all `/sessions` endpoints. Wraps DB access; consumers don't touch
  the table directly.
- `Session` model (`app/models/session.py`) — value object with id, user_id, token, expires_at.

**Dependencies (must exist first)**
- R0 (User model) — ✅ Done
- JWT signing key in env — already present (`AUTH_JWT_SECRET`)
- DB migration for `sessions` — created as part of this change (`migrations/0042_sessions.sql`)

**Risks / conflicts**
- None with current main; coordinate with frontend team — they need to start sending
  Authorization header after this lands
- Backward compat: no existing endpoint to break
- Rollout: backend ships before frontend cutover

**Test plan**
- R1 AC1 (201 with token on success) → `tests/api/sessions.test.ts::test_create_returns_201`
- R1 AC2 (token is JWT) → same file::`test_token_is_jwt`
- R1 AC3 (token has sub=user_id, exp=24h) → same file::`test_token_claims`
- R1 AC4 (401 if unauthenticated) → same file::`test_unauth_returns_401`
- R3 AC1 (audit row written) → `tests/audit/sessions.test.ts::test_create_writes_audit`

**Out of scope (explicitly)**
- Token refresh (R5) — separate endpoint, separate change
- Rate limiting on this endpoint (R4) — blocked on Q1

---

## Worked example 2 — refactor with no behavior change

**Change**: Extract `app/utils/cache.ts` into `app/services/cache/` with a proper interface,
two implementations (in-memory, Redis), and tests.

**Spec items addressed**: None directly — this is enabling infrastructure. Tracker entry as
**X3** (out-of-spec refactor; rationale: required to support R4 cleanly).

**Existing code surfaces touched**
- `app/utils/cache.ts` (deleted; functionality moved)
- All 8 importers of `cache.ts` — updated to import from `services/cache`

**New abstractions**
- `CacheStore` interface — get/set/del with TTL. Lives in `app/services/cache/types.ts`.
- `MemoryCacheStore` — for dev / tests.
- `RedisCacheStore` — for prod.

**Dependencies (must exist first)**
- None. Redis is already in `package.json`.

**Risks / conflicts**
- All 8 call sites need to be updated atomically — won't compile otherwise. Mitigation:
  single PR, hold the merge.
- Behavior change: none expected. Existing tests should pass unchanged.

**Test plan**
- Behavior tests for existing cache callers must pass unchanged (regression).
- New unit tests for `MemoryCacheStore` and `RedisCacheStore` against the `CacheStore`
  interface contract.

**Out of scope**
- Migrating other ad-hoc caches in the codebase (there are 3) — track as follow-up.

---

## Worked example 3 — small change (still gets a one-paragraph plan)

**Change**: Default `User.role` to `"member"` instead of `null` when creating a user.

**Spec items addressed**: R8 AC2 (every user has a role).

**Plan**: One-line change in `app/models/user.py` (default value). Add migration to backfill
existing nulls to `"member"`. Add a NOT NULL constraint in the same migration. Test: extend
`tests/users.test.ts::test_create_user` to assert role default. Rollback: migration is
reversible. Risk: any code reading role and not handling null is now exercising a new code
path — grep for `\.role` to confirm no special-casing.

---

## How to use the plan in the response

When this skill is active, the plan goes in the conversation **before** the implementation.
Pattern:

1. Surface the plan
2. Pause for user nod (especially on the first significant change in a session — after that,
   trust grows)
3. Implement
4. Update the tracker with results

If the user says "just go," fine — but the plan still gets written. It takes 30 seconds and
the act of writing it catches issues that the act of "just going" wouldn't.

---

## The plan is not the design doc

A common misconception: "the plan should fully design the system." No. The plan answers six
questions:

1. What's changing (one line)?
2. What does it satisfy in the spec?
3. What code does it touch?
4. What's new?
5. How do I know it works (the test plan)?
6. What could go wrong (risks, conflicts, rollout)?

Each answer is a sentence or a bullet, not a paragraph. If the plan is longer than the
implementation, the plan is wrong — either it's overspecifying, or the change should be
broken into smaller ones.

---

## What changes when the plan is wrong

The plan is a snapshot of what you *thought* before writing code. The act of writing code will
sometimes reveal that part of the plan was wrong (a surface you thought you'd touch turned out
not to need touching, or a new abstraction turned out to be unnecessary).

That's expected and good. When it happens:

1. **Don't silently abandon the plan.** Update it.
2. **Note the divergence in the tracker.** "Plan said X; actual implementation Y because Z."
3. **If the divergence is large**, that's a signal to stop, redo the plan, and proceed.

The plan isn't a contract; it's a record of intent. When intent changes, the record changes
with it.
