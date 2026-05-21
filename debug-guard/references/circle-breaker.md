# The circle breaker

What to do when you've been debugging the same thing for too long and you're going round in
circles.

**Activation criterion:** 3+ failed fix attempts on the same bug, or > ~60 minutes spent without
clear progress. Either one triggers the circle breaker.

---

## Why you're stuck (almost always)

When debugging spirals, the failure mode is almost always one of these:

1. **You haven't actually reproduced reliably.** The bug "kind of" happens. Without reliable
   repro, every fix attempt is a coin flip about whether it worked.
2. **You're patching symptoms, not finding the cause.** The first error led you to a fix; that
   fix uncovered the next error; you've been moving the bug, not fixing it.
3. **You have a hypothesis you never actually tested.** You assumed X is the cause and started
   fixing. The fix doesn't work because X wasn't actually it.
4. **You're missing context.** There's something about the system — an invariant, an env var, a
   race, a piece of history — that you don't know. No fix will work until you find it.
5. **The bug is in a different layer than you're looking.** You're in the app layer and the
   bug is in the framework, the OS, a dependency, or the data.

More attempts won't fix any of these. More *evidence* will.

---

## The protocol

Run through these steps in order. Don't skip; the order matters.

### Step 1: List what you've tried and what happened

Open a scratch file or section in your response. For each attempt:

- What was the hypothesis?
- What did you change?
- What was the result?

This often surfaces things immediately:

- Three "different" attempts that were really the same conceptual change in different words.
- A clue from an earlier failure you noticed but didn't act on.
- The realization that you've been testing against an unreliable repro.

### Step 2: Re-check the cardinal rules — honestly

For each, answer yes or no:

- Did you reproduce the bug *reliably*? Not "I saw it happen once" — "I can make it happen on
  command."
- Did you read the *whole* stack trace, including chained causes?
- Did you form a *specific* hypothesis with a mechanism and supporting evidence — or just a
  guess?
- Did you *verify* the hypothesis with evidence before changing code?
- Did you make *one* change at a time?

A "no" on any of these is where to restart. Most spirals have a "no" on the first two.

### Step 3: Build (or rebuild) a minimal reproducer

Strip the failing code path down until the bug stops, then add back one piece at a time until
it returns.

This is the single most powerful debugging technique. It does multiple things at once:

- Forces reliable repro
- Isolates the minimum surface that triggers the bug
- Often makes the cause obvious in the act of stripping

The piece you add that brings the bug back is your suspect. Now you have an actual hypothesis.

### Step 4: Bisect — when did this break?

If the bug is something that worked before, find the commit that broke it:

```bash
git bisect start
git bisect bad                 # current state has the bug
git bisect good <known-good>   # this commit didn't have it
# git will check out a middle commit; test, then:
git bisect good   # or 'bad'
# repeat until git tells you the breaking commit
```

You can script the test: `git bisect run ./my_test.sh` will run automatically.

Once you have the breaking commit, read it. The bug is almost certainly there.

If the bug has been around forever, bisection won't help — go to step 5.

### Step 5: Read the surrounding code

You may be missing context the code knows but you don't:

- **Callers** — how is this function actually called? What invariants do they assume?
- **Tests** — how was this code expected to behave? Tests document intent.
- **Comments** — especially `# noqa`, `# TODO`, `# HACK` comments. These flag known weirdness.
- **Recent changes** — `git log -p path/to/file` for the last 5-10 commits. What did they
  touch?
- **Issue tracker / PR history** — has this code been fought with before?

### Step 6: Rubber-duck the problem

Explain the bug from scratch, as if to someone with zero context. Out loud, in writing, doesn't
matter — what matters is the act of building the explanation.

Half the time, the act of explaining surfaces the missing piece. The other half, having a clean
written explanation makes the next step (asking for help) much faster.

Useful structure:

> "I'm trying to do X. I expected Y to happen. Instead, Z happens. I think it's because A, and
> the evidence for A is B. I've tried C, D, and E, with results F, G, H. The piece I don't
> understand is I."

### Step 7: Ask for context you don't have

Some bugs aren't solvable from the code alone. Ask the user (or team):

- What does this service / job / endpoint actually do? (Sometimes the function name lies.)
- What environment are we in? What's different vs. dev?
- What other systems interact with this?
- Has this been broken before? What was it?
- What have you already tried, and what happened?

This is cheap and often instantly unblocks you. The hesitation to ask ("they'll think I'm
stuck") is misplaced — you *are* stuck, and asking is faster than another hour of solo
spiraling.

### Step 8: Change tactics, not just variations

If you've tried three variations of "add a null-check," the *approach* is wrong, not the
variation. Try a different shape:

- Looking downstream → look upstream
- Looking at the code → look at the data
- Looking at this process → look at the process that produced the input
- Looking at the runtime → look at the build / install / config
- Looking at the app → look at the framework / dependency / OS

The bug is in a layer you haven't considered.

---

## When to give up and ask for help

When the circle breaker itself doesn't break the circle in another 30-60 minutes, that's the
signal to escalate:

- Ask the original author of the code (if findable via git blame).
- Ask in your team's debugging channel.
- File the issue with everything you've tried and where you're stuck.
- Sleep on it. Genuinely. Some bugs solve themselves between 11pm and 7am.

**Asking for help with a clean writeup of what you've tried is not failure — it's the
professional move.** It saves the next person from re-treading your path and gives you a fresh
perspective that you've now closed off from yourself.

---

## After the bug is fixed

When you finally crack a spiraled bug, do two things:

1. **Write a short post-mortem** — even 5 lines is enough. What was the root cause? What threw
   you off the scent? What would have surfaced it faster?
2. **Update the skill / runbook / docs** if the lesson generalizes. The next time this class of
   bug appears, you (or the next person) should hit it faster.

The most expensive thing about a 3-hour debug isn't the 3 hours. It's the next 3 hours when
something similar happens and the lesson hasn't been captured.
