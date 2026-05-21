# Debugging tools per language

Discipline matters more than tools, but knowing the right tool for each language saves real
time. Quick reference.

---

## Universal

- **Git bisect** — find the commit that introduced a bug.
  ```bash
  git bisect start && git bisect bad && git bisect good <known-good-sha>
  # test each commit git checks out, mark good/bad
  git bisect run ./repro.sh   # or fully automated
  ```
- **`grep`/`rg`** — find every occurrence of a function, variable, error message, or anti-pattern.
- **`strace` / `dtruss` / `procmon`** — see every syscall a process makes. Useful for "what
  file is it actually opening?" or "why is it slow on this machine?"
- **`tcpdump` / Wireshark** — see what's actually going over the network.

---

## Python

**Breakpoints:**
- `breakpoint()` — built-in since 3.7. Drops into pdb (or whatever `PYTHONBREAKPOINT` points
  at — set it to `ipdb.set_trace` for a nicer experience).
- `pytest --pdb` / `pytest -x --pdb` — drop into debugger on first test failure.

**Profilers:**
- `cProfile` — built-in, deterministic, function-level.
  ```bash
  python -m cProfile -o profile.out script.py
  python -m pstats profile.out
  ```
- `py-spy` — sampling profiler, can attach to a running process without modifying it.
  ```bash
  py-spy record -o flame.svg --pid <pid>
  ```
- `scalene` — CPU + memory + GPU profiling with line-level granularity.

**Memory:**
- `tracemalloc` — built-in, snapshot-based.
- `memray` — modern, low overhead.
- `objgraph` — visualize object reference cycles.

**Logging over print:**
- `logging` module — set up once, use everywhere. `logger.exception(...)` inside `except`
  blocks captures the stack trace automatically.

**Async:**
- `asyncio.run(main(), debug=True)` — enables slow-callback warnings and unhandled-task-result
  reporting.
- `PYTHONASYNCIODEBUG=1` — same, via env var.

---

## TypeScript / JavaScript / Node

**Breakpoints:**
- `debugger;` statement — pause when devtools (browser) or `--inspect` (Node) is attached.
- `node --inspect-brk script.js` — break on first line; connect via chrome://inspect or VS
  Code.
- VS Code debug configs work out of the box for Node and Chrome.

**Profilers:**
- Chrome devtools Performance tab — for browser code.
- `node --prof script.js` → `node --prof-process isolate-*.log` for CLI.
- `0x` — flame graphs for Node.

**Memory:**
- Chrome devtools Memory tab — heap snapshots, allocation timeline.
- `node --inspect` + Chrome Memory panel for Node heap snapshots.

**Logging:**
- `console.dir(obj, { depth: null })` — print nested objects without `[Object]` truncation.
- Pino / Winston / Bunyan for structured logging in Node.

**Async:**
- `--async-stack-traces` (default in modern Node) — async functions show through in stack
  traces.
- `--unhandled-rejections=strict` — crash on unhandled promise rejection (default in newer
  Node).

---

## Go

**Breakpoints:**
- `dlv` (Delve) — the Go debugger.
  ```bash
  dlv debug ./cmd/myapp
  dlv test ./pkg/foo
  dlv attach <pid>
  ```
- VS Code Go extension wires dlv automatically.

**Race detector:**
- `go test -race ./...`
- `go run -race main.go`
- Catches read/write data races. Slow at runtime; use in CI.

**Profilers:**
- `pprof` — built-in via `net/http/pprof` or `runtime/pprof`.
  ```go
  import _ "net/http/pprof"  // enables /debug/pprof/ endpoints
  ```
  ```bash
  go tool pprof http://localhost:8080/debug/pprof/profile?seconds=30
  ```
- CPU, heap, goroutine, block (mutex contention), mutex profiles all available.

**Logging:**
- `log/slog` (1.21+) — structured logging built in.
- `zap` / `zerolog` for high-performance structured logging.

**Tests:**
- `go test -run TestName -v` — single test with verbose output.
- `go test -count=10` — run repeatedly (flake detection).

---

## Rust

**Breakpoints:**
- `rust-gdb` / `rust-lldb` — wrappers around gdb/lldb that load Rust pretty-printers.
- `dbg!(expr)` — built-in macro that prints file/line + value and returns it. Better than
  `println!` for ad-hoc debugging.

**Logging:**
- `tracing` ecosystem (`tracing` + `tracing-subscriber`) — structured, async-aware logs.
- `env_logger` + `RUST_LOG=debug` for quick setup.
- `RUST_BACKTRACE=1` (or `full`) — show backtraces on panic.

**Profilers:**
- `cargo flamegraph` — flame graphs via perf.
- `samply` — modern sampling profiler.
- `cargo-instruments` — macOS, wraps Xcode Instruments.

**Tests:**
- `cargo test -- --nocapture` — show prints from passing tests.
- `cargo test -- --test-threads=1` — serialize tests (find isolation bugs).
- `cargo nextest run` — faster, better output than built-in.

**Concurrency:**
- ThreadSanitizer: `RUSTFLAGS="-Z sanitizer=thread" cargo +nightly test`.
- Loom — model-checking for concurrent code: `loom = "0.7"` in dev-deps.

---

## Browser

- **Sources panel** — set breakpoints, conditional breakpoints, log points.
- **Network panel** — see every request, response, timing. Filter by type.
- **Performance panel** — record interaction, see flame graph.
- **Memory panel** — heap snapshots and allocation timeline.
- **Console**:
  - `monitor(fn)` — log every call to `fn`.
  - `monitorEvents(elem)` — log every event on `elem`.
  - `$0` — the element currently selected in Elements panel.
  - `copy(obj)` — copy a deeply-nested object to clipboard.

---

## Databases

- **`EXPLAIN ANALYZE`** (Postgres) / **`EXPLAIN`** (MySQL) — see the actual query plan.
- **Slow query log** — every DB has one. Enable for prod debugging.
- **`pg_stat_statements`** — Postgres extension; the cheapest way to find your N+1 queries.

---

## When to reach for these vs. just printing

- **Print / log** when you need to see a few values from a specific code path.
- **Debugger** when the state is too complex to print, or you need to step through ordering.
- **Profiler** when you're debugging performance — never guess.
- **Race detector** when concurrency is suspected — even if you don't think you have a race.
- **Bisection** when you know it worked before but doesn't now.

A few targeted print statements often beat firing up a debugger. A debugger beats 50 print
statements. Use the right tool for the right kind of question.
