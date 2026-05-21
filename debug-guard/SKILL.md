---
name: debug-guard
description: |
  Systematic debugging discipline — prevents whack-a-mole fixing, surface-level patches, and the
  3-hour spiral on a 20-minute bug. Fires whenever code is broken, throwing errors, producing wrong
  output, behaving intermittently, or running slow — and when a previous fix attempt didn't work.
  Across all languages and stacks.
  Triggers on phrases like: "this is broken", "X isn't working", "I'm getting this error", "why is
  this failing", "debug this", "fix this bug", "the test is failing", "it crashes when", "I keep
  getting", "I've tried X but it still", "it's still not working", "this should work but doesn't",
  "the output is wrong", "this is flaky", "intermittent failure", "race condition", "deadlock",
  "memory leak", "too slow", "performance regression". Also fires when the user pastes a stack
  trace, a traceback, an exception message, a failed test output, or a log excerpt with errors.
  ALSO triggers strongly on UI / browser / network / proxy / connectivity bugs: "CORS error",
  "blocked by CORS", "preflight failing", "Failed to fetch", "TypeError: Failed to fetch", "fetch
  is failing", "401 in the browser but works in Postman / curl", "cookies aren't being sent",
  "SameSite", "credentials: include", "mixed content", "self-signed certificate",
  "ERR_CERT_AUTHORITY_INVALID", "ERR_CONNECTION_REFUSED", "ERR_TUNNEL_CONNECTION_FAILED", "the
  dev proxy isn't working", "Next.js rewrites", "Vite proxy", "nginx 502", "X-Forwarded-For",
  "WebSocket won't connect", "WebSocket 200 instead of 101", "SSE messages arrive in bursts",
  "service worker serving stale code", "CSP refused to connect", "behind a corporate proxy", "npm
  install fails with SSL", "NODE_EXTRA_CA_CERTS", and any UI bug where the user has DevTools open
  and is staring at the Network tab.
  ENFORCES (this is the whole point): reproduce before fixing, read the FULL stack trace, form a
  written hypothesis with evidence, change ONE thing at a time, find the root cause (not the
  symptom), write a regression test, and check whether the same pattern exists elsewhere in the
  codebase. Activates the "circle breaker" if 3+ fix attempts haven't worked — stop, reassess, and
  go back to repro and hypothesis before trying anything else.
  Distinct from `clean-code-guard` (writing new code with quality bars), `simplify` (post-hoc
  cleanup of working code), `security-review` (security audit), and `review` (PR review of an
  already-written change). This skill is specifically for **broken code that needs investigation
  and a fix**.
  Skip only for: trivial obvious typos with no investigation needed (single char fix), pure
  syntax-lookup questions, or when the user explicitly says "I know what's wrong, just change X
  to Y".
---

# debug-guard

The difference between a 20-minute fix and a 3-hour rabbit hole is almost always **discipline,
not skill**. This skill enforces the discipline.

It's the antidote to vibe-debugging — that pattern where you patch the first error you see, hit
a new error, patch that, hit another, and three hours later you've changed 15 things and still
don't understand the bug.

## Core principle: investigate before you change

**No fix without a hypothesis. No hypothesis without evidence. No evidence without a
reproduction.**

Most bad debugging happens because someone skipped the first step and started changing code
based on intuition. Intuition is fine *after* you have a reproduction — it's a disaster before.

> The first error you see is almost never the cause. It's a downstream symptom of an upstream
> mistake. Patching where it surfaces hides the bug; it doesn't fix it.

---

## The seven cardinal rules

These are the rules. Break one and you're guessing.

### 1. Reproduce first

If you can't make the bug happen on demand, you can't fix it — only hope. Before changing any
code, get to "I can trigger this reliably." That might mean:

- A failing test case
- A precise sequence of inputs / clicks / commands
- A small script that demonstrates the bug
- Server logs from a real occurrence (when local repro isn't possible)

**No repro = no fix, only guessing.** If you genuinely cannot reproduce, that *itself* is the
first thing to solve.

### 2. Read the whole error

The full stack trace, top to bottom. The exception type AND the message. The chained `cause` /
`__context__` if there is one. The surrounding logs. Recent commits. The frame that threw is
rarely where the bug lives — it's just where the code stopped being able to cope.

### 3. Hypothesize, then verify

Write down — out loud, in the response — what you think is happening AND why:

> "I think `X` returns `None` here because the cache lookup in `Y` is missing the key. I'll
> confirm by logging the cache state before this call."

If you can't write a hypothesis like that, you don't know enough yet. Go find more evidence —
don't change code.

**Confirm the hypothesis with evidence before changing anything.** A log line, a debugger break,
a test that fails the way you predict. Otherwise your "fix" is also a guess.

### 4. One change at a time

Each change is motivated by evidence and verified independently. If you change two things at
once and the bug goes away, you don't know which one fixed it — and you've now silently
introduced a second change you may not have needed. Shotgun fixes are the #1 source of
re-emerging bugs.

### 5. Root cause, not symptom

When you find the bug, ask "why" until you hit something that *explains* the behavior:

- "It crashes because `user.email` is `None`."
  → Why? "Because we didn't fetch it from the DB."
  → Why? "Because the new `lazy=True` flag in the schema."
  → Why? "Because we added it for the admin page but didn't update the email job."

The fix lives at the third or fourth "why," not the first. Adding `if user.email is None: return`
at the crash site hides this bug; it doesn't fix it.

### 6. Regression test

Every real bug gets a test that would have caught it. If you can't write that test, your fix is
either fragile, unverifiable, or in the wrong place — investigate one more level.

### 7. Look for the pattern

Once you find the root cause, search the codebase for the same shape elsewhere. Bugs travel in
packs — the same anti-pattern usually got copy-pasted to two or three other places. Search
broadly (the call site, similar functions, recent commits touching this area) before declaring
the work done.

---

## The systematic workflow

When invoked on a real debugging task, follow this. Steps in **bold** are non-negotiable.

1. **Capture** — exact error message, exception class, full stack trace, repro steps,
   environment, recent changes.
2. **Reproduce** — confirm you can trigger it. Failing test > script > manual sequence > prod
   logs.
3. **Read the trace top-to-bottom.** Note the actual exception type and message, all chained
   causes, and the call path. The cause is upstream of the throw site more often than not.
4. **Ask "what changed?"** — `git log --since="N days ago"`, recent deploys, dependency updates,
   config changes, infra changes.
5. **Form a hypothesis.** State it explicitly: "I think X is happening because Y, evidenced
   by Z."
6. **Test the hypothesis** — log, print, breakpoint, or write a focused unit test. Confirm OR
   reject before changing production code.
7. **If rejected** → form a new hypothesis with the new evidence. Don't just try a different
   fix.
8. **Once confirmed** → plan the fix. What changes; what tests; what side effects.
9. **Apply one change** → verify the bug goes away AND nothing else broke.
10. **Write the regression test.**
11. **Search for the pattern** elsewhere in the codebase.
12. **Document the why** — code comment for the non-obvious bit; commit message for the
    history; runbook/notes if it could recur in production.

Steps 1–7 are the part people skip when in a hurry. Skipping them is what causes the 3-hour
spiral.

---

## The circle breaker

**If you've made 3 or more fix attempts and the error is still happening (even in different
forms), STOP. Do not try a 4th variation of the same approach.**

When you're spiralling, the failure mode is almost always *insufficient investigation*, not
*insufficient fix attempts*. More attempts won't help; more evidence will.

When the circle breaker fires, do these things in order:

1. **List everything you've tried and what each result was.** Often surfaces what you haven't
   tried — and reveals that you've been making the same conceptual change three different ways.
2. **Re-check the cardinal rules.** Did you actually reproduce reliably? Did you confirm a
   hypothesis with evidence, or just guess? Did you read the *whole* stack trace, including
   chained causes?
3. **Find a minimal reproducer.** Strip the failing code path down until the bug stops, then add
   back one piece at a time until it returns. The piece that brings it back is your suspect.
4. **Bisect.** When did this start? `git bisect`, or read commits in the affected area. A bug
   that's "always been there" usually was introduced in a specific commit you can find.
5. **Read the surrounding code.** You may be missing context — invariants the caller assumes,
   side effects of another function, ordering constraints.
6. **Rubber-duck it.** Explain the bug from scratch as if to someone with zero context. Half the
   time the act of explanation reveals what you missed.
7. **Ask the user.** Sometimes the missing piece is a fact only they have — what this service
   does, which environment, what other systems are involved, what they've already tried. Cheap
   move, often unblocks instantly.

See [`references/circle-breaker.md`](./references/circle-breaker.md) for the full playbook.

---

## The 15 anti-patterns of vibe debugging

Spot these in yourself and stop. Full catalog with examples in
[`references/anti-patterns.md`](./references/anti-patterns.md).

1. **The shotgun** — changing 5 things at once "to be safe."
2. **The downstream patch** — adding `if x is None: return` at the crash site without finding
   why `x` is `None`.
3. **The cargo cult fix** — pasting a Stack Overflow snippet without understanding what it does.
4. **The "just restart it"** — making the symptom disappear without finding the cause.
5. **The cache blame** — "must be a stale cache" without verifying.
6. **The "works on my machine" punt** — suspecting an environment difference without
   investigating it.
7. **The big try/except** — wrapping the stack trace in `except Exception: pass` so the error
   stops being visible.
8. **The revert-and-retry** — undoing the failing change and trying a slightly different
   approach instead of forming a new hypothesis.
9. **The AI-in-a-loop** — pasting the error to an LLM, applying the suggestion, getting a new
   error, repeating without building a mental model.
10. **The cosmetic fix** — fixing what the error *says* without checking whether the error
    message is accurate. Errors lie.
11. **The fix-without-repro** — changing code based on "it should work this way" without ever
    seeing the bug fire after the change.
12. **The dependency upgrade hope** — bumping a library because a similar issue was fixed in
    v2, without confirming this is the same bug.
13. **The "weird, working now"** — declaring victory after a fix you don't understand. It comes
    back in production at 2 AM.
14. **The print-everywhere flood** — adding 50 print statements with no plan, drowning in
    noise.
15. **The infinite spiral** — 4+ failed attempts without stepping back. Circle breaker time.

---

## Bug types need different approaches

The workflow above is the default. Some bug types want adjustments. Quick guide; deep dive in
[`references/by-bug-type.md`](./references/by-bug-type.md).

| Bug type                       | Key adjustments                                          |
| ------------------------------ | -------------------------------------------------------- |
| Crash / exception              | Default workflow. Stack trace is your friend.            |
| Wrong output, no error         | Add assertions for expected invariants; bisect inputs.   |
| Flaky / intermittent           | Run repeatedly; add instrumentation; look at ordering.   |
| Performance                    | Profile FIRST, then fix. Don't guess hotspots.           |
| Concurrency (race, deadlock)   | Tiny repro is hard. Reason about ordering systematically. Race detectors. |
| Integration / "works locally"  | Diff configs, env vars, versions. Reproduce the env.     |
| Memory leak                    | Heap snapshots. Look for growing collections.            |
| Build / install failure        | Read the FIRST error in the log, not the last.           |
| **UI / browser / network**     | **Network tab IS the truth. Reproduce with DevTools open. Cross the wire boundary deliberately.** → [`references/ui-debugging.md`](./references/ui-debugging.md) |
| **CORS / cookies / proxy**     | **Find the OPTIONS preflight; isolate which hop loses the request.** → [`references/ui-debugging.md`](./references/ui-debugging.md) |
| **Corporate proxy / SSL**      | **Install the corporate root CA properly — never disable TLS verification.** → [`references/ui-debugging.md`](./references/ui-debugging.md) |

---

## Tools per language

Tools matter less than discipline, but a few essentials per language in
[`references/tools.md`](./references/tools.md):

- **Python** — `pdb` / `ipdb` / `breakpoint()`, `pytest -x --pdb`, `logging` not `print`
- **TypeScript/JavaScript** — `debugger;`, Chrome devtools, Node `--inspect-brk`, `console.dir`
  with depth
- **Go** — `dlv`, `go test -run=TestName -v`, race detector with `-race`
- **Rust** — `dbg!()`, `rust-gdb` / `rust-lldb`, `RUST_LOG=trace`, `cargo test -- --nocapture`

---

## Output format when debugging

When this skill is active, structure the response like this:

```
**Diagnosis: <one-line statement of what's broken>**

What I know
- <fact from error / log / stack trace>
- <fact from code / recent changes>
- <fact from environment>

Hypothesis
- <what I think is happening, and WHY>

To verify (do this BEFORE changing code)
- <specific evidence I'll gather — log, print, test, breakpoint>

Fix plan (only after hypothesis confirmed)
- <single change, with rationale>
- <regression test that would have caught this>
- <pattern check: search for similar shape elsewhere>
```

When the user gives you a stack trace or error message, this format is your default. Don't jump
straight to a code change.

When you're past the verification step, write the fix. When you're not yet at the verification
step, **ask for whatever you need to verify** — log output, surrounding code, repro steps.

---

## What this skill is NOT

- **Not a replacement for thinking.** It's scaffolding for thinking. The skill structures the
  process; the user (and Claude) still does the diagnosis.
- **Not a delay tactic.** When the fix is genuinely obvious (a clear typo, a missing import, an
  off-by-one with a single test that catches it), do the fix. The discipline applies to bugs
  that are NOT one-line obvious.
- **Not a blocker for trivial bugs.** A one-character typo doesn't need a hypothesis section.
  Use judgment.
- **Not the same as `clean-code-guard`.** That one is for *writing* code well; this one is for
  *fixing* code that's already broken. Both can apply during a refactor that's fixing bugs.

---

## See also

- [`references/workflow.md`](./references/workflow.md) — deep workflow with worked examples
- [`references/anti-patterns.md`](./references/anti-patterns.md) — the 15 vibe-debugging
  pathologies with concrete examples
- [`references/by-bug-type.md`](./references/by-bug-type.md) — type-specific guidance
- [`references/circle-breaker.md`](./references/circle-breaker.md) — what to do when you're
  spiralling
- [`references/tools.md`](./references/tools.md) — per-language debugging tools and idioms
- [`references/ui-debugging.md`](./references/ui-debugging.md) — UI / browser / network / proxy /
  CORS / cookies / dev proxies / reverse proxies / corporate MITM / WebSocket / SSE / caching /
  CSP. Read this whenever the bug crosses the browser-to-server wire.
