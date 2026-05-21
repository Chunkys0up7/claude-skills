# Finding and parsing specs

Specs come in many flavours. The skill needs to handle all of them. This file is the playbook
for finding the canonical source and pulling structured requirements out of it.

---

## Where specs live

Common locations to look for, in roughly the order you should check them:

| Location                              | Format                          | What it usually contains                  |
| ------------------------------------- | ------------------------------- | ----------------------------------------- |
| `docs/specs/` · `specs/`              | Markdown PRDs / design docs     | Feature-level specs                       |
| `rfcs/` · `docs/rfcs/`                | Markdown RFCs                   | Proposals, design discussions             |
| `docs/adrs/` · `architecture/decisions/` | Markdown ADRs                | Architectural decisions, one per file     |
| `requirements/` · `docs/requirements/`| Markdown / Word / Confluence    | Detailed functional requirements          |
| `openapi.yaml` · `openapi/`           | OpenAPI / Swagger               | API contracts                             |
| `*.graphql` · `schema.graphql`        | GraphQL SDL                     | API contracts                             |
| `proto/` · `*.proto`                  | Protocol Buffers                | RPC / message contracts                   |
| `tests/acceptance/` · `features/`     | Gherkin (`.feature`)            | Acceptance criteria as given/when/then    |
| `README.md`                           | Markdown                        | Sometimes the only spec for small projects |
| `CHANGELOG.md`                        | Markdown                        | What's been delivered (not a spec, but useful) |
| Ticket bodies (Jira, Linear, GH)      | Plain text                      | Per-story requirements                    |
| Notion / Confluence / Coda            | External link                   | Linked from the repo or chat              |

If unsure, **ask the user**. "Where does the spec live?" beats reading the wrong document for
20 minutes.

---

## Reading order when you find one

When you have the spec in front of you:

1. **Front matter** — title, version, author, date, status (draft / approved / superseded).
2. **Goals / non-goals section** — defines what's in scope and what's deliberately *not*.
3. **Functional requirements** — the "what." Each one becomes a tracker row.
4. **Non-functional requirements** — performance, security, accessibility, observability.
   These often get skipped but they're requirements too.
5. **Acceptance criteria** — sub-bullets under each requirement, or a dedicated section.
   These become the test plan.
6. **Open questions section** — these become entries in the Open Questions table.
7. **Out-of-scope / future** — make sure these end up Deferred in the tracker, not Not Started.

Read the **whole** thing. The non-obvious requirements are in the boring sections — error
handling, edge cases, observability, rollout.

---

## Parsing into the tracker — per format

### PRD / design doc (Markdown)

A typical PRD:

```markdown
# Session API spec

## 2. Functional requirements

### 2.1 Create session
Users can create a session by POSTing to `/sessions` with credentials.

**Acceptance criteria:**
- Returns 201 with a token on success
- Token is a signed JWT
- Token expires after 24h
```

Extract:

| ID  | Requirement                | Spec ref | Acceptance criteria                        |
| --- | -------------------------- | -------- | ------------------------------------------ |
| R1  | Users can create a session | §2.1     | AC1: 201+token; AC2: JWT; AC3: 24h expiry  |

### RFC

Structured similarly to PRDs, but emphasize:
- **Status** — draft RFCs are dangerous to implement against; they change.
- **Decisions** section — these are commitments. Don't undo them silently.
- **Alternatives considered** — context, not requirements.

### ADR (Architecture Decision Record)

ADRs are *decisions*, not full requirements. They constrain how you implement other specs.

When implementing a feature, find any ADRs that touch the same area (auth, storage, observability)
and treat them as constraints — they go in the tracker's Decisions log as inherited decisions.

### OpenAPI / Swagger contract

Each path × method = a requirement. The schema definition is part of the acceptance criteria.

```yaml
/sessions:
  post:
    summary: Create a session
    responses:
      '201': { ... }
      '401': { ... }
```

Extract:

| ID  | Requirement                       | Spec ref               | Acceptance criteria                       |
| --- | --------------------------------- | ---------------------- | ----------------------------------------- |
| R1  | POST /sessions creates a session  | `openapi.yaml /sessions POST` | AC1: 201 schema; AC2: 401 if no creds |

Add separate rows for each response status code if behavior matters.

### Gherkin / acceptance criteria (`.feature` files)

Each scenario is a verifiable requirement. The Given/When/Then *is* the test plan.

```gherkin
Feature: Session creation
  Scenario: Valid credentials produce a session
    Given an existing user with email "u@example.com"
    When the user posts to /sessions with valid credentials
    Then the response status is 201
    And the response body contains a token
```

Extract:

| ID  | Requirement (the scenario)              | Spec ref | Status                          |
| --- | ---------------------------------------- | -------- | ------------------------------- |
| R1.1 | Valid creds produce a session            | `sessions.feature::Valid credentials produce a session` | Status from test run |

This is the cleanest case — the spec IS the test plan.

### Ticket bodies (Jira / Linear / GitHub issues)

Treat the ticket body as a per-story spec. If the team uses "Acceptance Criteria" as a
standard section in tickets, parse those into AC rows.

For epics with multiple stories, the epic is the top-level grouping and each story becomes a
row.

---

## When the spec is missing pieces

Most specs are incomplete. Common gaps:

| Gap                                | What to do                                                       |
| ---------------------------------- | ---------------------------------------------------------------- |
| No acceptance criteria             | Propose them; get user sign-off; add to spec or tracker          |
| No non-functional requirements     | Assume sensible defaults; surface explicitly                     |
| No error handling spec             | Surface as Open Question (per endpoint / function)               |
| No data shape / schema             | Propose the schema; get sign-off; record as decision             |
| No deployment / rollout            | Surface as Open Question; default to "behind feature flag"       |
| No observability requirements      | Propose metrics/logs; record as decision                         |
| No security requirements           | Propose (authn / authz / audit / rate limit); record as decision |

Surface every gap. Don't fill it in silently. The tracker's Decisions log is where these go.

---

## When the spec contradicts itself

Specs from real humans often have contradictions. Examples:

- §2.1 says "tokens expire after 24h"; §2.5 says "long-lived sessions persist across browser
  restarts."
- §3.1 says "audit every action"; §3.2 says "skip audit for read-only endpoints."
- §4 says "rate limit 100/min"; an inline note says "internal services exempt."

For each contradiction:

1. **Surface it immediately** — don't pick one and code.
2. **Propose a resolution** with reasoning.
3. **Get user sign-off.**
4. **Record the resolution** in the Decisions log.
5. **Recommend updating the spec** — the contradiction is a spec bug.

---

## When the spec is in chat or verbal

The most fragile spec is the one that doesn't exist as a document. If the user describes
requirements in chat:

1. **Write them down.** Either as a new spec file, or as the initial tracker rows with the
   spec ref noted as "chat 2026-05-21" (and a quote of the relevant message).
2. **Confirm with the user** that this is the canonical source.
3. **Treat chat as evidence that informs the spec, not the spec itself** — make the file the
   spec, and update the file when chat decisions happen.

Verbal-only specs lead to drift. Capture them in writing the moment you're working from them.

---

## Cross-referencing multiple specs

Real features often touch:
- A product spec (PRD)
- An API contract (OpenAPI)
- ADRs (architectural constraints)
- Acceptance criteria (Gherkin)
- Security review notes
- Style/design guidelines

These can all be source-of-truth simultaneously, for different aspects. The tracker should
note this:

```markdown
**Spec sources**:
- Product: `docs/specs/sessions.md` (rev 2026-05-15)
- API contract: `openapi.yaml` (paths /sessions and /sessions/{id})
- Architecture: `docs/adrs/0003-jwt-tokens.md` · `docs/adrs/0007-audit-log.md`
- Security: `docs/security/auth-review-2026q2.md`
```

Each tracker row notes which source the requirement came from. When sources conflict, surface
it like any contradiction.

---

## Re-reading the spec when it changes

Specs aren't static. They get amended. When you resume work:

1. **Check spec rev / git log on the spec file.** Has it changed since the tracker's recorded
   "Spec source rev"?
2. **If yes, diff it.** What did the diff add, change, remove?
3. **Reconcile**:
   - New requirements → add tracker rows (Not started).
   - Changed requirements → check whether the change invalidates work already Verified. If
     yes, that's a regression — flag and re-do.
   - Removed requirements → mark Deferred or strike through (don't delete history).
4. **Update the tracker's recorded spec rev.**

The tracker's "spec source rev" is what the rest of the tracker is consistent with. When it's
stale, the rest is stale too.
