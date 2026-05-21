# Anti-patterns of vibe debugging

The 15 most common ways to spend 3 hours not fixing a 20-minute bug. Spot them in yourself; spot
them in code review.

---

## 1. The shotgun

**Smell**: changing 5 things at once "to be safe."

```python
# Three changes in one commit "in case any of them is the bug"
- if user.profile:
+ if user is not None and user.profile is not None:
      send_email(user.profile.email)
+     time.sleep(0.1)  # maybe race condition?
+ retry_count = max(retry_count, 3)
```

**Why it's bad**: when the bug goes away (or doesn't), you don't know which change mattered.
You've silently introduced 2-4 untested changes. The bug *will* come back because you didn't
find the root cause.

**The fix**: one change at a time, each motivated by evidence, each verified independently.

---

## 2. The downstream patch

**Smell**: adding a null-check / try-except / default value at the crash site.

```python
def send_renewal_email(user):
-    email = user.profile.email
+    if user is None or user.profile is None:
+        return  # skip — investigate later
+    email = user.profile.email
```

**Why it's bad**: you've hidden the bug, not fixed it. `user.profile` should not be `None` here.
By returning silently you've made the failure invisible — now the bug shows up two weeks later
as "users complaining they don't get renewal emails" with no log line to grep for.

**The fix**: trace upstream to find why `user.profile` is `None`. Either fix it there, or — if
this layer genuinely is an API boundary that should defend itself — handle it explicitly with a
log, metric, or raised exception that surfaces the problem.

---

## 3. The cargo cult fix

**Smell**: pasting code from Stack Overflow / docs / an LLM without understanding it.

```python
# Found this on SO, seems to fix it
import gc
gc.collect()
asyncio.set_event_loop(asyncio.new_event_loop())
```

**Why it's bad**: you don't know what those three lines do. If the bug "goes away," you don't
know why; if it doesn't, you don't know what to remove. The fix probably has side effects you
haven't considered.

**The fix**: understand any code before applying it. Read the docs for each function. Explain it
in your own words. *Then* decide whether it actually addresses your hypothesis.

---

## 4. The "just restart it"

**Smell**: making the symptom disappear without finding the cause.

> "Restart the service" — and it works. Until tomorrow.

**Why it's bad**: the bug is still there. You've shifted the failure from "happens whenever" to
"happens periodically." The next person to hit it has no logs from the original failure, just
the side effects.

**The fix**: when a restart fixes something, that *is* the signal — it usually means state
accumulated incorrectly. Find what (memory leak, stale connection pool, zombie task) and fix
it. Restart is a workaround, not a fix.

---

## 5. The cache blame

**Smell**: "must be a stale cache" — without verifying.

> Tried `npm run clean && npm install`, restart, fresh build — still broken. "Weird, must be a
> cache somewhere."

**Why it's bad**: usually it's not the cache. Blaming the cache is a way to avoid investigating.
And when it *is* the cache, you should know *which* cache and *why* it became stale.

**The fix**: identify the specific cache (browser, build, CDN, DB query, ORM session). Verify
its state. If it's stale, find why it didn't invalidate.

---

## 6. The "works on my machine" punt

**Smell**: "it works locally for me" — without investigating the environment difference.

**Why it's bad**: there's a real reason it works for you and not for them. Until you find it,
neither of you knows whether the bug also affects every other environment.

**The fix**: diff the environments. Same OS? Same language version? Same dependency versions
(`pip freeze`, `pnpm list`)? Same env vars? Same data? The diff is the bug.

---

## 7. The big try/except

**Smell**: wrapping the failing code in `except Exception: pass` (or `catch (e) { /* ignore */ }`).

```python
try:
    process_batch(items)
except Exception:
    pass  # was failing in prod, this stops it
```

**Why it's bad**: the bug is now invisible. The "fix" doesn't fix anything — it just stops the
log line. Side effects of the half-executed code path are still happening (partial writes,
corrupted state, missed records).

**The fix**: catch the *specific* exception you're handling. Handle it specifically (log it,
metric it, retry it, surface it). Never `except Exception: pass` without an explicit comment
explaining why this is genuinely safe (and it usually isn't).

---

## 8. The revert-and-retry

**Smell**: undoing the failing change and trying a slightly different version of the same
approach.

> Fix didn't work. Revert it. Try a slightly different version of the same fix. Doesn't work.
> Revert. Try a third variation.

**Why it's bad**: you're not learning from the failures, you're flailing. If three variations
of the same approach all fail, the *approach* is wrong, not the variation.

**The fix**: after a failed fix, go back to **hypothesis**. What did the failure tell you? Form
a new hypothesis based on the new information. Then try.

---

## 9. The AI-in-a-loop

**Smell**: pasting the error to an LLM, applying the suggested fix, getting a new error,
pasting that to the LLM, repeating.

**Why it's bad**: each suggestion is a local patch. The LLM doesn't have the full system
context, doesn't see the chain of attempts, and tends to suggest reasonable-looking changes
that move the error around rather than fix it. You end up with 8 unrelated edits and no model
of what's wrong.

**The fix**: build your own model first. Reproduce, hypothesize, gather evidence. Use the LLM
for *understanding* (what does this stack trace mean? what does this function do?), not for
*choosing the fix*. Once you understand the bug, the fix is usually obvious.

---

## 10. The cosmetic fix

**Smell**: fixing what the error *says* without checking whether the message is accurate.

> Error says `KeyError: 'user_id'`. Add `'user_id'` to the dict. Now error says
> `KeyError: 'user_name'`. Add that. Now error says... and so on.

**Why it's bad**: you're playing whack-a-mole against the symptom. The real bug is that
something upstream is producing a dict missing the fields a downstream consumer needs — the
*set* of missing fields is a clue to the upstream cause.

**The fix**: when an error tells you a key is missing, ask *who was supposed to put it there*
and *why didn't they*. Don't just add the key at the consumer.

---

## 11. The fix-without-repro

**Smell**: changing code based on "it should work this way" without ever seeing the bug fire
post-change.

**Why it's bad**: you don't actually know whether your change fixed the bug. You're betting on
intuition. Half the time the bug is something else entirely; the other half, your fix doesn't
work the way you expected.

**The fix**: every fix is followed by re-running the repro. If you don't have a repro, get one
before you change code. If you genuinely can't repro, write the test that would catch the bug
*and verify it fails against the current code*, then fix, then verify it passes.

---

## 12. The dependency upgrade hope

**Smell**: bumping a library version because a similar bug was fixed in v2, without confirming
this is the same bug.

```
# Updating axios to 1.6 -- there's a fix in the release notes that maybe is this
- "axios": "^1.4.0"
+ "axios": "^1.6.0"
```

**Why it's bad**: the upgrade might not address your bug. You've now introduced an
unrelated version bump with its own potential breaking changes. If the bug appears to be fixed,
you don't know if it's actually fixed or just lurking behind a different code path now
exercised by the new version.

**The fix**: read the actual changelog / fix commit. Confirm it addresses *this specific bug*.
If it does, upgrade — and verify your repro is fixed. If it doesn't, the upgrade is unrelated;
keep investigating.

---

## 13. The "weird, working now"

**Smell**: the bug stopped happening but nobody knows why. Declared victory.

**Why it's bad**: it'll be back. In production. At 2am. Without the logs you'd want.

**The fix**: don't declare victory without explaining the mechanism. "I don't know why it's
working now" means you haven't found the bug — you've just stopped triggering it. Either keep
investigating (intermittent timing, dependency caches, state accumulation) or document
honestly: "Bug stopped reproducing; possible cause is X but unverified. If it recurs, look
here."

---

## 14. The print-everywhere flood

**Smell**: 50 print statements added with no plan, drowning in noise.

```python
print("here 1")
print("got user", user)
print("got profile", user.profile)
print("here 2")
print("about to send")
# ... 45 more
```

**Why it's bad**: you can't see the signal in the noise. And you've now coupled the bug
investigation to a brittle pile of debug output you'll have to clean up.

**The fix**: think before printing. What specific state do you need to see to confirm or reject
the hypothesis? Add 1-3 targeted prints (or better, a single structured log line). Read the
output. Remove or commit them.

---

## 15. The infinite spiral

**Smell**: 4+ failed fix attempts and you're still going.

**Why it's bad**: every additional attempt is more code churn, more potential for new bugs, and
deeper conviction that you're "almost there." You're not. You're flailing.

**The fix**: the circle breaker. Stop after attempt 3. Step back to the cardinal rules. Find
the missing piece — usually it's "I never actually reproduced reliably" or "I never confirmed a
hypothesis with evidence." See [`circle-breaker.md`](./circle-breaker.md).

---

## The meta-pattern

Most of these share a single root cause: **changing code based on guesses, not evidence.**

The discipline that prevents all of them is the same: **reproduce, hypothesize, verify, change
one thing, test.** When you find yourself reaching for any pattern on this page, that's your
signal you've stopped following the discipline. Go back to the workflow.
