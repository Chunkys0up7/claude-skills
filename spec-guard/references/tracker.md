# The compliance tracker

The artifact at the centre of `spec-guard`. It records, for every requirement in the spec,
where the implementation is, what proves it, and what's left to do.

The tracker isn't optional and isn't deferred. **It's updated as work happens** — that's the
only time the information is correct.

---

## Where it lives

Pick **one** location at the start of the project and stick to it:

| Location                                | When to use                                                |
| --------------------------------------- | ---------------------------------------------------------- |
| `SPEC-COMPLIANCE.md` at repo root       | Default. Most discoverable. Survives across sessions.      |
| `docs/specs/<feature>-compliance.md`    | When the project has multiple specs each with own tracker. |
| `.specs/progress.md`                    | When the team prefers a hidden directory.                  |
| Inline in the conversation only         | One-off sessions, exploratory work, no repo to commit to.  |

If unsure, default to `SPEC-COMPLIANCE.md` at the repo root and confirm with the user once.

---

## The full template

```markdown
# Spec compliance: <feature or epic name>

**Spec source**: `docs/specs/feature-x.md` (rev 2026-05-15, commit abc123 if vendored)
**Last updated**: 2026-05-21
**Owner**: <user>
**Status**: 🟡 In progress · target ship date 2026-06-01

## Summary

- **Done**: R1, R2, R5
- **In progress**: R3, R6
- **Blocked**: R4 (pending Q1)
- **Not started**: R7, R8, R9
- **Deferred**: R10 (out of this milestone)

## Requirements

| ID | Requirement                       | Spec ref | Status     | Evidence                                       | Notes |
|----|-----------------------------------|----------|------------|------------------------------------------------|-------|
| R1 | Users can create a session        | §2.1     | 🟦 Verified | `app/api/sessions.ts` · tests: `sessions.test.ts::create_returns_201`, `::token_is_jwt` |   |
| R2 | Sessions expire after 24h         | §2.3     | 🟦 Verified | `app/services/session.ts::expire` · `tests/session_expiry.test.ts` |       |
| R3 | Audit log entry per action        | §4.2     | 🟡 In progress | `migrations/0042_audit.sql` (table created); handler wiring pending | depends on R1, R2 |
| R4 | Rate limit: 100 req/min per user  | §2.5     | ❌ Blocked  |                                                | Q1: window strategy |
| R5 | Idempotent token refresh          | §2.4     | ✅ Done    | `app/api/refresh.ts`; tests pending verification | passes manual smoke |
| R6 | Webhook on session creation       | §3.1     | 🟡 In progress | `app/events/session_created.ts` (draft) |       |
| R7 | Admin can revoke any session      | §5.1     | ⬜ Not started |                                              |       |
| R8 | Metrics emitted for each endpoint | §6.1     | ⬜ Not started |                                              |       |
| R9 | SSO via SAML                      | §7.1     | ⬜ Not started |                                              |       |
| R10| Mobile push on revoke             | §5.2     | ➖ Deferred |                                                | post-MVP, tracked GH-#123 |

## Acceptance criteria detail (for in-progress items)

### R3 — Audit log entry per action

- [x] AC1: Audit table exists with columns (user_id, action, ts, ip) → `migrations/0042_audit.sql`
- [ ] AC2: Every state-changing endpoint writes a row → handler wiring in progress
- [ ] AC3: Audit rows are immutable (no UPDATE/DELETE from app) → DB constraint pending
- [ ] AC4: Audit table queryable by user_id and date range → index pending

## Out-of-spec changes

| ID | Change                                | Justification                            | Decided by | Note                                |
|----|---------------------------------------|------------------------------------------|------------|-------------------------------------|
| X1 | Added Redis for rate-limit state      | Required prerequisite for R4             | user 5/21  | Spec needs update post-MVP          |
| X2 | Renamed `Session.token` to `Session.access_token` | Naming consistency with auth0 docs | claude 5/21 | Cosmetic; updated all callers       |

## Open questions

| ID | Question                                          | Spec ref | Status              |
|----|---------------------------------------------------|----------|---------------------|
| Q1 | What's the rate-limit window unit — 1m fixed or sliding? | §2.5     | Awaiting user input |
| Q2 | Should expired sessions emit a webhook?           | §3.1     | Resolved → no (see D2) |

## Decisions log

| ID | Decision                                          | Why                                            | When  | Resolves |
|----|---------------------------------------------------|------------------------------------------------|-------|----------|
| D1 | Use JWT for session tokens, not opaque tokens     | Existing stack uses JWT; cohesion              | 5/21  | spec silent |
| D2 | No webhook on expiry, only on creation/revocation | Avoids noise; expiry is internal               | 5/21  | Q2       |

## Change log for this tracker

- 2026-05-21: R1, R2 marked Verified. Created tracker. R4 blocked on Q1.
- 2026-05-20: Initial extraction from spec rev 2026-05-15. 10 requirements logged.
```

---

## The status taxonomy

Be strict about these — they mean specific things.

| Symbol | Status        | Meaning                                                                       |
| ------ | ------------- | ----------------------------------------------------------------------------- |
| ⬜     | Not started   | Requirement exists in spec; no code yet.                                      |
| 🟡     | In progress   | Code exists for some part; not all acceptance criteria met yet.              |
| ✅     | Done          | Implementation complete; acceptance criteria *believed* met but not verified. |
| 🟦     | Verified      | Acceptance criteria explicitly verified — tests pass, evidence in tracker.    |
| ❌     | Blocked       | Cannot proceed until a decision / dependency is resolved.                     |
| ➖     | Deferred      | Explicitly out of this milestone (with note on where it's tracked).           |

**The distinction between Done and Verified matters.** "Done" is "I wrote the code." "Verified"
is "I ran the test that proves it satisfies the acceptance criteria, and that test is recorded
in the Evidence column." Don't conflate them. Many bugs hide between these two states.

---

## Evidence — what counts

The Evidence column is the difference between "trust me" and "here's why you should trust me."

**Good evidence:**
- File path + symbol: `app/services/session.ts::renewSession`
- Test reference: `tests/session.test.ts::test_renew_returns_new_token`
- Commit/PR: `commit abc123`, `PR #842`
- Manual smoke trace if no test exists (note explicitly: "manual smoke; no automated test yet")

**Bad evidence:**
- "Implemented" (where? proved how?)
- "See the PR" (which PR? which file?)
- "Tested" (which test exercised this requirement?)
- Blank

If the evidence is "this is hard to test," that itself is a finding — record it as an open
question or a decision to accept that risk.

---

## When to update the tracker

**Always update it in the same session as the change.** Not "at the end of the day." Not "when I
have time." Right after the change lands.

Three update points:

1. **When status changes** (Not started → In progress; In progress → Done; Done → Verified;
   any → Blocked).
2. **When evidence accrues** (a new file is touched, a test is added).
3. **When an out-of-spec change is made, a decision is recorded, or a question surfaces.**

If a session ends with the tracker out of sync, that's a debt to record explicitly:
"Tracker not updated for the last commit; needs reconciliation next session."

---

## Maintaining the tracker across sessions

When you resume a session on a spec'd project:

1. **Read the tracker first.** Before reading the spec, before reading code.
2. **Reconcile against current state.** Has anything shipped that isn't recorded? Read recent
   commits for spec IDs in commit messages or PR descriptions.
3. **Re-read the spec if it's changed.** Compare `git log` on the spec file to the tracker's
   "Spec source" rev. If the spec moved, list the diffs and decide what to do for each.
4. **Update "Last updated" and add a "Change log" entry** describing what changed this session.

---

## Commit message convention

Tie each commit back to a requirement ID. This is what makes the tracker auditable later:

```
feat(R1): create-session endpoint with JWT issuance

Implements R1 (create session) acceptance criteria AC1-AC3.
- POST /sessions returns 201 with token
- Token is a signed JWT with sub=user_id, exp=24h
- Audit row written (also progresses R3)

Refs: docs/specs/auth.md §2.1
Tracker: SPEC-COMPLIANCE.md
```

When a commit covers multiple IDs, list them all. When a commit is out-of-spec, prefix with the
out-of-spec ID:

```
chore(X1): add Redis client dependency

Out-of-spec — prerequisite for R4 rate limiting. Recorded as X1 in
SPEC-COMPLIANCE.md.
```

---

## Tracker hygiene

A few rules that keep the tracker honest over time:

- **One requirement per row.** If R1 has 8 acceptance criteria, expand them in the AC detail
  section, but R1 stays one row.
- **No "done" without evidence.** Empty Evidence column + ✅ status = a lie waiting to surface.
- **Out-of-spec changes are not invisible.** Either they're in the X table or they don't
  exist.
- **Closed questions become decisions.** When Q1 resolves, move the resolution to the
  Decisions log (don't just edit Q1 to say "Done").
- **Deferred items still get tracked.** Mark them ➖ Deferred with a pointer to where they live
  now (issue link, post-MVP backlog).
