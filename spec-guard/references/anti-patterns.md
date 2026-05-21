# Anti-patterns of vibe-spec work

The 10 most common ways spec-driven work goes wrong. Each one shows up in real codebases;
each one is preventable.

---

## 1. Spec drift

**Smell**: Implementing what feels natural instead of what the spec says.

> Spec says "tokens expire after 24 hours." You implement 24-hour idle timeout (refreshed on
> use). They're not the same. Users with long sessions never get logged out.

**Why it's bad**: You've built something the spec didn't ask for. Sometimes it's better — but
usually it's a quiet bug that ships because nobody noticed the divergence.

**The fix**: When you read a requirement, restate it in your own words and check that your
implementation plan matches the restatement. Then implement.

---

## 2. Silent scope creep

**Smell**: Adding things not in the spec because they "obviously" need to exist.

> Spec says "create a session endpoint." You add session list, session detail, and session
> revoke endpoints too — "they'll need them eventually."

**Why it's bad**: Three more endpoints to test, document, maintain, and secure. The user
hasn't agreed to the surface area. The spec didn't require them. Now they exist and someone
will integrate against them.

**The fix**: If you think "we'll probably need X too," **surface it explicitly**: "Spec
doesn't include list / detail / revoke. Want me to add them now or defer?" Record the answer.
Either path is fine; what's not fine is doing it silently.

---

## 3. The "I'll track it later" lie

**Smell**: "I'll update the compliance tracker at the end."

**Why it's bad**: You won't. Or if you do, you won't remember the details. Or the next
session you'll re-discover what you already built but can't prove.

**The fix**: Update the tracker **as work happens**. Each completed thing → one tracker
update. It's a 10-second cost that saves hours of "wait, was R3 done?" later.

---

## 4. The vague acceptance

**Smell**: A tracker row marked ✅ Done with empty Evidence column.

> R3 (Audit log entry per action) ✅ Done

**Why it's bad**: You can't prove this. Maybe it's done; maybe it's half-done; maybe the
acceptance criteria are partially met. Without evidence, "Done" is a feeling.

**The fix**: No Done without an evidence link. Either a file:line, a test name, or a commit
hash. If you can't produce one, the status isn't Done — it's In Progress with a "needs
verification" note.

---

## 5. The verbal spec

**Smell**: "We discussed this in chat last Tuesday — the requirement is X."

**Why it's bad**: Chat history is fragile. Six weeks later, no one will remember Tuesday's
conversation. The new team member won't have it. The auditor won't find it.

**The fix**: When a decision is made in chat (or a meeting, or a Slack thread), **write it
down in the canonical spec doc or the tracker's Decisions log**. The canonical source is the
written file, not the conversation.

---

## 6. The implicit decision

**Smell**: The spec is silent on something (error format, retry policy, log format, key
rotation interval). You picked something reasonable and shipped.

**Why it's bad**: Reasonable to you, in this context, today, may not match what the team
wants. And there's no record of why you picked what you picked, so when someone questions it
later, "I don't remember" is the only answer.

**The fix**: When the spec is silent and you need to decide, **propose the decision and record
it**. Decisions log row: "Used exponential backoff with 1s base, 5 retries — spec silent;
matches existing pattern in `app/services/email.ts`."

The recording is what matters. The decision itself can be quick.

---

## 7. The cherry-pick

**Smell**: Implementing the easy 80% of the spec and quietly skipping the hard 20%.

> Built create, renew, expire. Skipped revoke and admin-revoke because they were "complex."
> Marked the feature ✅ Done.

**Why it's bad**: The user thinks the feature is done; it isn't. Production users hit the
unimplemented paths and get 500s or silent failures.

**The fix**: A feature is done when **all** its acceptance criteria are met. If you're
skipping any, that's a feature with an explicit Deferred section, not a Done feature. Mark
unfinished items 🟡 In progress or ➖ Deferred (with a pointer to where they're tracked).

---

## 8. The ahead-of-spec

**Smell**: Coding ahead of where the spec is settled.

> Spec is in draft. You start implementing. Spec changes mid-implementation. Now your code
> doesn't match the new spec, and the work to reconcile is bigger than waiting would have
> been.

**Why it's bad**: Compounding waste. Code based on a draft is bet against the spec changing.
You're going to lose that bet some of the time.

**The fix**: Don't build against draft specs unless the user explicitly accepts the risk
("yes, build it, we'll fix-up later"). When the spec moves to approved, then build. If you
must build ahead, isolate the speculative parts behind a flag so the rework is cheap.

---

## 9. The plan-as-narration

**Smell**: Writing the integration plan **after** implementing, as a description of what
you did.

**Why it's bad**: The plan exists to catch design issues before they're in code. After-the-fact
plans don't catch anything — they just describe the choices you already made (with all their
flaws baked in).

**The fix**: Plan first, even if briefly. If the plan reveals a problem, you save the
implementation time. If it doesn't, the cost was 30 seconds.

When you skip the plan, you're betting "this is simple, no design issues to surface." That bet
is fine when it's true and expensive when it's wrong. The plan is cheap insurance.

---

## 10. The spec-vs-code drift

**Smell**: Code evolves over months; the spec doesn't get updated.

> Spec says `POST /sessions` returns `{token, expires_at}`. Code now returns
> `{access_token, refresh_token, expires_in}`. Nobody touched the spec.

**Why it's bad**: The spec is no longer the source of truth — but it's still presented as one.
New team members read the spec, write code against it, get bugs. Auditors find compliance
gaps. The next refactor pulls the spec back, breaking existing clients.

**The fix**: When code intentionally diverges from the spec, **update the spec in the same
PR**, or record the divergence as an out-of-spec change with a follow-up to amend the spec.
Specs are documents that need maintenance, not artifacts that get written once.

---

## The meta-pattern

Eight of these ten have a common root cause: **information made in one moment doesn't get
written down before the moment ends.** A decision in chat that doesn't reach the spec. A
divergence from the plan that doesn't reach the tracker. A skipped acceptance criterion that
doesn't reach the Deferred section. A reasoning step that lives only in your head.

The discipline `spec-guard` enforces is, fundamentally, **write it down at the time, not
later.** The tracker is the place; the integration plan is the format; the commit message is
the trail.

Everything else falls out of that.
