# The systematic debugging workflow

This is the deep version of the workflow summarized in `SKILL.md`. Read it when the bug is
non-trivial — when you've spent more than 15 minutes or attempted more than one fix.

---

## 1. Capture — write down what you know

Before touching code, capture the bug. Five things:

- **Exact error** — full message and exception class. Not paraphrased.
- **Stack trace** — full, including chained causes. Top to bottom.
- **Reproduction steps** — exact inputs, exact sequence.
- **Environment** — OS, language version, key dependency versions, prod vs local.
- **Recent changes** — git log of recent commits to the affected area; recent deploys; recent
  config or dependency changes.

If any of these are missing, get them before continuing. "I don't know exactly what error" is
the start of a 3-hour spiral.

---

## 2. Reproduce

A bug you can't reproduce is a bug you can't fix. You can only hope.

Hierarchy of reproductions, best to worst:

1. **Failing test case.** Write the test that exhibits the bug. This becomes your regression
   test later.
2. **Standalone script.** A small `repro.py` / `repro.ts` / `repro.go` that demonstrates the
   problem.
3. **Precise manual sequence.** Step 1, step 2, step 3 → bug. Same every time.
4. **Production logs from a real occurrence** — when local repro is impossible (real user data,
   real load, real infra).

If you genuinely cannot reproduce, that is the first problem to solve. Add instrumentation.
Wait for the next occurrence. Build a synthetic version that triggers the suspected path.

> If the bug is intermittent, run the repro 50 times in a loop. Failure rate gives you a signal.
> A bug that fires 1% of the time has an ordering or timing dependency — look there.

---

## 3. Read the whole error

The stack trace tells a story. Read it top to bottom — top is the latest call, bottom is the
entry point.

Things to extract:

- **Exception type AND message.** A `KeyError: 'user_id'` is different from a `KeyError: 'id'`.
- **The throw site.** Which file/line raised. (This is rarely the cause.)
- **The call path.** Who called the throw site? Who called that?
- **Chained causes** — `caused by`, `__context__`, `from e`. The chained cause is often the real
  bug; the outer exception is just the wrapper.
- **Async / generator frames** — if present, the trace can be misleading about temporal order.

> The frame that threw is where the code gave up. The frame where the bug lives is usually
> earlier in the chain.

---

## 4. Ask "what changed?"

A bug that just started has a recent cause. Look for it.

```bash
git log --since="2 days ago" --stat
git log --since="2 days ago" -- path/to/affected/area
git diff HEAD~5..HEAD -- path/to/affected/area
```

Also consider:
- Recent deploys (look at the deploy log / CI history)
- Dependency updates (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml` changes)
- Config changes (env vars, feature flags, infra)
- Data changes (schema migrations, backfills, new tenant types)

If the answer is "nothing changed," then either something *did* change and you haven't found it
yet, or this is an old bug just now being triggered. Find which.

---

## 5. Form a hypothesis

A real hypothesis has three parts:

1. **What** is happening
2. **Why** it's happening (the mechanism)
3. **Evidence** so far supporting it

Example of a real hypothesis:

> "`renew_session` is throwing `KeyError: 'token'` because the session dict no longer has a
> `token` field after the schema change in commit `abc123`. Evidence: the trace shows the
> KeyError at line 47 of `session.py`, and `git show abc123` removed the `token` field from the
> Session dataclass."

Example of a fake hypothesis (a guess in disguise):

> "Maybe the session is None."

The fake one has no mechanism and no evidence. It's a starting point, not a hypothesis. Either
upgrade it (find evidence that session is None) or reject it (verify session is not None).

---

## 6. Verify the hypothesis BEFORE changing code

This is the step people skip when they're tired. Don't.

Tools for verification, in rough order of effort:

- **Read the code** — does the source actually do what you think? Often this alone confirms or
  rejects.
- **Print / log** — add one or two targeted prints. Run. See the value. Remove the prints.
- **Breakpoint / debugger** — when the state is too complex to print. `breakpoint()` (Python),
  `debugger;` (JS), `dlv` (Go), `lldb`/`gdb` (Rust).
- **Focused test** — write a unit test that exercises the suspected path with the suspected
  input. The test failing the way you predicted = strong confirmation.
- **Production instrumentation** — when local repro isn't possible, log the relevant state
  behind a feature flag, deploy, observe, remove.

If the evidence rejects your hypothesis, you've learned something — go back to step 5 with new
data. Don't just try a different fix.

---

## 7. Plan the fix

Once the hypothesis is confirmed, plan rather than dive. Write out:

- **What change you'll make** — the specific code edit, in the right place.
- **Why this is the right level** — is the root cause here, or are you patching downstream? If
  downstream, *why* is that the right call (sometimes it is — e.g., defending an API boundary).
- **What test will catch this** — the regression test you'll write.
- **What else might break** — does this change affect other callers, other code paths, other
  data shapes?

For a non-trivial fix, surface this plan to the user before applying it.

---

## 8. Apply one change

One change. Run the repro / test. Confirm:

- The bug is gone.
- Nothing else broke (run the local test suite, at least the area you touched).
- The hypothesis predicted the result accurately.

If the bug is *not* gone after your "confirmed" fix, your hypothesis was incomplete — go back
to step 5. Don't just try another change.

---

## 9. Write the regression test

Every real bug gets one. The test should:

- **Fail on the buggy code** — verify by running it against the pre-fix version (revert briefly,
  run, confirm it fails, re-apply fix).
- **Pass on the fixed code.**
- **Be named after the bug** — `test_renew_session_handles_missing_token_field` is better than
  `test_renew_session_2`.
- **Be small** — exercise the bug, not the whole system.

If you can't write a regression test, the fix is either in the wrong place or the system is too
tightly coupled to test. Both are worth knowing.

---

## 10. Search for the pattern

Same bug shape, different file. Bugs travel in packs because they're usually a mental-model
bug, not a typo — and the same mental model got applied elsewhere.

Searches to run:

- Same function call elsewhere (`grep -rn renew_session`)
- Same anti-pattern (`grep -rn "except Exception"`)
- Same recent change (look at the commit that introduced the bug; what else did it touch?)
- Similar code paths (the team probably copy-pasted)

When you find another instance, fix it (with its own regression test) or at least flag it as a
follow-up.

---

## 11. Document the why

The fix code should be obvious. The *why* of the fix often isn't. Three places to capture it:

- **Code comment** — for the non-obvious bit. "We check `token is not None` here because the v2
  schema made this field optional (see GH-1234)."
- **Commit message** — explain the bug, the root cause, and the fix. Future-you will thank you.
- **Runbook / docs** — if this could recur in production, write a one-paragraph runbook entry.

---

## Worked example

**Bug**: nightly job `send_renewal_emails` started crashing 2 days ago with
`AttributeError: 'NoneType' object has no attribute 'email'`.

1. **Capture**: error, full trace, "started 2 days ago in nightly cron." Recent change: PR #842
   touched the user fetch.

2. **Reproduce**: write a test that calls `send_renewal_emails` with the user state from prod
   (a user with `lazy=True` profile). Test fails the same way.

3. **Read the trace**: `AttributeError` at line 23 of `mailer.py`: `user.profile.email`. The
   trace shows `user.profile` is `None`.

4. **What changed?**: PR #842 added `lazy=True` to the profile relationship. This means
   `user.profile` is no longer eagerly loaded — it requires a session.

5. **Hypothesis**: "When the cron runs, it loads users in a context where the SQLAlchemy session
   has closed by the time the email job accesses `user.profile`. `lazy=True` returns `None`
   instead of fetching, because the session is gone."

6. **Verify**: add a print before line 23. Run cron locally. Confirm `user.profile` is `None`
   and `user._sa_instance_state.session` is closed.

7. **Plan**: the right fix is to eagerly load `profile` when fetching users for the cron — not
   to null-check `user.profile` at the email site (that hides the data-loading bug).

8. **Apply one change**: `users.options(joinedload(User.profile))` in the cron query.

9. **Regression test**: simulate the closed-session condition, verify the cron doesn't crash.

10. **Search the pattern**: grep for other `lazy=True` relationships used by background jobs.
    Find two more (subscriptions, preferences). File issues / fix.

11. **Document**: comment on the `joinedload` line explaining why. Commit message describes the
    `lazy=True` change as the root cause.

Total: ~45 minutes, one fix, one test, two follow-ups. Without the workflow, this is the
3-hour version: null-check user.profile, hit the next null, null-check that, drown in nulls,
finally realize the session is the problem.
