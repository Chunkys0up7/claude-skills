# Bug-type-specific guidance

The default workflow in `SKILL.md` and `workflow.md` works for most bugs. These types want
adjustments.

---

## Crashes and exceptions

The default workflow is built for this.

**Specific tips:**

- **The thrown exception type is usually accurate.** The *message* sometimes lies. Trust
  `KeyError` over the dictionary key it names.
- **Chained exceptions matter.** Python's `__cause__` / `from e`, Java's `caused by`, Rust's
  `source()` chain. The original exception is usually closer to the root cause than the
  outer wrapper.
- **Async stack traces lie about temporal order.** Frames may be from where the coroutine was
  scheduled, not where it was awaited. Use async-aware debuggers when available.

---

## Wrong output, no error

Hardest of the common categories. The code runs to completion but the answer is wrong. There's
no stack trace, no clear failure point.

**Workflow adjustments:**

1. **Find the smallest input that produces wrong output.** A 10-row CSV that exhibits the bug
   is gold.
2. **Build the expected-vs-actual diff.** What should the output be? What is it? Where do they
   first diverge?
3. **Add assertions for invariants.** `assert len(out) == len(in)`. `assert all(x >= 0 for x
   in totals)`. Run the code. Assertions failing tells you *where* the divergence starts.
4. **Bisect inputs.** Cut the input in half. Does the bug still appear? Cut again. Eventually
   you have a 1-2 record input that triggers it.
5. **Bisect history.** When did the output start being wrong? `git bisect` with a script that
   returns 0 for correct output, 1 for wrong.

**Common causes:**

- Off-by-one (loops, slice indices, boundary values)
- Wrong default (`{}`, `[]`, `0`, `None`) when the absent case should be handled differently
- Floating point comparison (`==` on floats; use tolerances)
- Sorting / ordering assumptions that don't hold (dict iteration order across versions, hash
  randomization)
- Integer overflow / underflow
- Encoding issues (UTF-8 vs latin-1, bytes vs str)
- Timezone bugs (naive vs aware datetimes; UTC vs local)

---

## Flaky / intermittent bugs

The bug fires sometimes but not always. Same input, same code.

**Workflow adjustments:**

1. **Run the repro in a loop.** 50, 100, 500 times. Failure rate is your signal — 1% rate
   suggests timing/ordering; 50% rate suggests boolean flip.
2. **Instrument heavily, on the failing path only.** Log timestamps, thread IDs, order of
   operations. Save logs from a successful run AND a failing run; diff them.
3. **Think about ordering.** What runs concurrently? What runs in random order (dict
   iteration, async task scheduling, parallel test runners)?
4. **Think about external state.** Files, DB rows, env vars, system clock, network. What might
   be different between runs?

**Common causes:**

- Race conditions (read/write without synchronization)
- Test isolation failures (test A leaves state that affects test B; run order matters)
- Time-dependent code (DST, midnight, leap seconds)
- Memory or resource exhaustion at high load
- Network flakiness (real upstream timeout vs your code's behavior under timeout)
- Random initialization (uninitialized memory, random seed)

---

## Performance bugs

Code works, just too slowly.

**The cardinal rule for performance: PROFILE FIRST. Don't guess.**

Most "obvious" performance bottlenecks are wrong — the actual hotspot is somewhere else. Guessing
wastes hours optimizing the wrong loop.

**Workflow:**

1. **Establish a baseline** — measure current performance with a repeatable workload.
2. **Profile** — use the language's profiler.
   - Python: `cProfile`, `py-spy`, `scalene`
   - JS/Node: Chrome devtools profiler, `--prof`
   - Go: `pprof` (CPU, alloc, block, mutex profiles)
   - Rust: `cargo flamegraph`, `perf`
3. **Find the actual hotspot.** Look at exclusive time (just this function) and inclusive time
   (this function + everything it calls). They tell different stories.
4. **Form a hypothesis** about why it's slow — algorithm (O(n²) where O(n) is possible),
   allocations, IO, contention, syscalls.
5. **Make one change. Re-measure.** If it didn't help, your hypothesis was wrong — back to
   profiling.
6. **Stop when you've hit the goal.** Don't keep optimizing past the requirement; that's how
   you make code unreadable for no gain.

**Common causes:**

- N+1 queries (ORM lazy loading; calling the DB inside a loop)
- O(n²) inside what looked like O(n) (e.g., `in` on a list instead of a set)
- Repeated computation (function called inside a loop when the result is constant)
- Unnecessary allocations (string concatenation in a hot loop)
- Lock contention (mutex held longer than needed)
- IO without batching or async

---

## Concurrency bugs (race conditions, deadlocks)

Hardest category. Code is correct for any single thread; wrong with multiple.

**Workflow adjustments:**

1. **Tiny repro is hard but worth the effort.** Strip everything until you have the minimum
   code that races. Often this exposes the bug in plain sight.
2. **Reason about all interleavings.** For shared state, what happens if thread A pauses at
   line 5 and thread B runs? What if both are at line 10?
3. **Use the race detector.**
   - Go: `go test -race` / `go run -race`
   - Rust: `RUSTFLAGS=-Z sanitizer=thread cargo +nightly test` (nightly)
   - C/C++: ThreadSanitizer
4. **Look at synchronization primitives.** Mutexes, channels, atomics — is each shared piece of
   state actually protected on every access?
5. **Think about happens-before relationships.** Memory ordering matters in low-level code.

**Common causes:**

- Read-modify-write without a lock
- Two locks acquired in different orders by different code paths → deadlock
- Async tasks awaiting each other in a cycle
- Shared mutable state via global / module variable
- Closure capturing a loop variable (especially in Go pre-1.22, JS `var`)
- Background tasks outliving the context they assumed

---

## Integration bugs ("works locally")

Code works on your machine; fails in CI / staging / prod. Same code, different environment.

**Workflow:**

1. **Diff the environments** — OS, language version, dependency versions, env vars, file
   system layout, network, available resources.
2. **Reproduce the production environment locally** — Docker, devcontainer, the same exact
   image CI runs.
3. **Diff the data** — production has data shapes that don't exist in local fixtures (longer
   strings, null fields you thought were always set, multi-byte characters, larger numbers).
4. **Diff the load** — production has concurrency you didn't test for.

**Common causes:**

- Dependency version drift (lock file ignored, or platform-specific binary)
- Missing env var with a silent default in dev
- File system case sensitivity (Mac vs Linux)
- Time zone differences (local TZ vs UTC)
- Network: DNS, certs, proxies, firewalls
- Data: nulls, encoding, sizes, edge values
- Permissions / users / file ownership

---

## Memory leaks

Process memory grows unboundedly over time.

**Workflow:**

1. **Confirm it's a leak**, not just baseline growth. Memory should plateau eventually if it's
   not a leak.
2. **Take heap snapshots at intervals.** Diff them. What's growing?
3. **Look for growing collections** — caches without eviction, lists you append to forever,
   event listeners not removed, closures holding references.
4. **Look for resources not freed** — file handles, DB connections, sockets, subprocess
   handles.

**Tools:**
- Python: `tracemalloc`, `objgraph`, `memray`
- JS/Node: Chrome devtools heap snapshots, `--inspect`
- Go: `pprof` heap profile
- Rust: usually compiler-prevented; if leak, look at `Rc`/`Arc` cycles

---

## UI, browser, network, proxy, and connectivity bugs

These are split across browser + network + dev proxy + reverse proxy + server, and each layer
has its own visibility tools. They want a dedicated approach.

**See [`ui-debugging.md`](./ui-debugging.md)** for the deep playbook covering:
- The Network-tab-first mindset and the triage workflow
- CORS, cookies, and `credentials: 'include'`
- Dev proxies (Next.js rewrites, Vite, webpack-dev-server, CRA)
- Production reverse proxies (nginx, traefik, cloud LBs) — header forwarding, path rewriting,
  WebSocket upgrade, timeouts, buffer sizes
- Corporate proxies and MITM cert pain — `HTTP_PROXY` / `HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`,
  `REQUESTS_CA_BUNDLE`, system trust stores
- WebSocket and SSE failure modes
- Browser / CDN / service worker caching
- CSP debugging
- A quick-reference table mapping browser errors → likely causes

**Top-of-mind rules** (the rest is in the playbook):

1. **The Network tab is the truth.** Console errors are summaries — read the actual request
   and response.
2. **Open DevTools BEFORE you reproduce.** Network doesn't record what happened before it was
   open (unless "Preserve log" + reload).
3. **Cross the wire boundary deliberately.** Check what the browser sent vs what the server
   received vs what the server sent vs what the browser saw — any mismatch tells you which
   layer has the bug.
4. **"Works in Postman" is not a useful comparison** — Postman doesn't enforce CORS, doesn't
   send your browser cookies, and sends whatever headers you tell it.
5. **Isolate which hop loses the request** when there's a proxy pile-up. Don't change the
   topmost layer first.
6. **Never `Access-Control-Allow-Origin: *`** in production, and never combine `*` with
   `Allow-Credentials: true` (browsers reject the combination).
7. **Never disable TLS verification** to make a cert error go away. Install the right cert.

---

## Build / install failures

Compile errors, dependency resolution failures, install scripts crashing.

**The most important rule: READ THE FIRST ERROR, NOT THE LAST.**

The first error is usually the cause; everything after it is the build system flailing because
the first thing didn't produce expected output. People reflexively scroll to the bottom of the
log and miss the actual problem.

**Workflow:**

1. **Find the first error in the log.** Scroll up. Or `grep -i error` and look at the earliest
   match.
2. **Reproduce locally** — `pnpm install --frozen-lockfile`, `pip install -r
   requirements.txt`, etc.
3. **Check version compatibility** — does the locked version actually exist? Did the registry
   yank a release?
4. **Check the lock file** — is it committed? Is it up to date with the manifest?
5. **Clean state test** — `rm -rf node_modules; pnpm install`. Does it work from scratch?

**Common causes:**

- Lock file out of sync with manifest
- Yanked / removed version
- Native binary missing for the platform (Python wheels, Node native modules)
- Conflicting transitive dependencies
- Cached corrupt download (`.npm`, `~/.cache/pip`)
- Auth failure to a private registry
