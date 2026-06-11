# TestSprite AI Testing Report (MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** trivia-seguridad-backend
- **Date:** 2026-06-11
- **Prepared by:** TestSprite AI Team
- **Test Scope:** Backend REST API — full codebase (8 feature groups, ~30 endpoints)
- **Environment:** Local server `http://localhost:8000`, base path `/api/v1`, `AUTH_MODE=local`, SQLite (seeded: 5 users, 5 topics, 25 questions, 6 badges)
- **Test Plan:** 55 hand-authored cases (`testsprite_backend_test_plan.json`) covering happy paths, validation errors, RBAC, and the full game lifecycle.

---

## 2️⃣ Requirement Validation Summary

### Requirement: Health
Liveness probe confirming the API service is up.
- **TC001** — `GET /api/v1/health` returns 200 with `{ status: 'ok', service: 'trivia-seguridad-api' }`. ✅ Passed

### Requirement: Authentication
Local JWT login and current-user profile; token validation.
- **TC002** — Login with valid admin credentials → 200 with `access_token` + user. ✅ Passed
- **TC003** — Login with wrong password → 401. ✅ Passed
- **TC004** — Login with unknown email → 401. ✅ Passed
- **TC005** — Login with missing fields → 422 (`email y password son obligatorios`). ✅ Passed
- **TC006** — `GET /auth/me` with valid token → 200 with correct user. ✅ Passed
- **TC007** — `GET /auth/me` without token → 401 (`Falta el token de autorización`). ✅ Passed
- **TC008** — `GET /auth/me` with invalid token → 401 (`Token inválido`). ✅ Passed

### Requirement: User Management (admin only)
CRUD with logical delete, pagination, and RBAC.
- **TC009** — Admin lists users → 200 with `items/total/page/pages`. ✅ Passed
- **TC010** — Guarda lists users → 403 (RBAC). ✅ Passed
- **TC011** — Admin creates user → 201. ✅ Passed
- **TC012** — Duplicate email → 409. ✅ Passed
- **TC013** — Invalid role → 422. ✅ Passed
- **TC014** — Missing required fields → 422. ✅ Passed
- **TC015** — Get user by id → 200. ✅ Passed
- **TC016** — Get non-existent user → 404. ✅ Passed
- **TC017** — Update user (`full_name`) → 200. ✅ Passed
- **TC018** — Logical deactivation → 200 (`is_active=false`). ✅ Passed
- **TC019** — Admin cannot self-deactivate → 422. ✅ Passed

### Requirement: Topics
Read for any authenticated user; write for admin.
- **TC020** — Authenticated user lists topics → 200. ✅ Passed
- **TC021** — Admin creates topic → 201. ✅ Passed
- **TC022** — Guarda creates topic → 403 (RBAC). ✅ Passed
- **TC023** — Duplicate topic name → 409. ✅ Passed
- **TC024** — Missing name → 422. ✅ Passed
- **TC025** — Admin updates topic → 200. ✅ Passed

### Requirement: Question Bank (admin only)
CRUD + atomic bulk import; "exactly 4 choices, exactly one correct" validation.
- **TC026** — Admin lists questions → 200 (total ≥ 25). ✅ Passed
- **TC027** — Guarda lists questions → 403 (RBAC). ✅ Passed
- **TC028** — Create valid question (4 choices, one correct) → 201. ✅ Passed
- **TC029** — Wrong number of choices → 422. ✅ Passed
- **TC030** — Not exactly one correct choice → 422. ✅ Passed
- **TC031** — Non-existent topic_id → 422. ✅ Passed
- **TC032** — Atomic bulk import → 201 (`created: 2`). ✅ Passed
- **TC033** — Bulk import empty items → 422. ✅ Passed
- **TC034** — Get non-existent question → 404. ✅ Passed
- **TC035** — Logical deactivation of question → 200. ✅ Passed

### Requirement: Game Sessions
Full quiz lifecycle with server-side scoring and per-user isolation.
- **TC036** — Start a session → 201 (top-level `session` + `question`). ✅ Passed
- **TC037** — Start without `topic_id` → 422. ✅ Passed
- **TC038** — Fetch own session state → 200. ✅ Passed
- **TC039** — Access another user's session → 404 by design (existence not leaked). ✅ Passed
- **TC040** — Submit an answer → 200 with `result`. ✅ Passed
- **TC041** — Answer without `choice_id` → 422. ✅ Passed
- **TC042** — Use lifeline `fifty_fifty` → 200. ✅ Passed
- **TC043** — Lifeline without `type` → 422. ✅ Passed
- **TC044** — Abandon session → 200. ✅ Passed

### Requirement: Gamification
Ranks, badges, and leaderboard with period validation.
- **TC045** — Get ranks → 200 (`ranks`, `me`). ✅ Passed
- **TC046** — Get badges catalog → 200 (6 badges, `unlocked` flag). ✅ Passed
- **TC047** — Leaderboard `period=all` → 200. ✅ Passed
- **TC048** — Leaderboard `period=week` → 200. ✅ Passed
- **TC049** — Leaderboard invalid period → 422. ✅ Passed

### Requirement: Supervisor Reports (supervisor/admin)
Overview, per-user/per-topic reports, CSV export, RBAC.
- **TC050** — Supervisor gets overview → 200. ✅ Passed
- **TC051** — Guarda gets overview → 403 (RBAC). ✅ Passed
- **TC052** — Supervisor per-user report → 200. ✅ Passed
- **TC053** — User-detail for non-existent user → 404. ✅ Passed
- **TC054** — Supervisor per-topic report → 200. ✅ Passed
- **TC055** — CSV export → 200 (`text/csv` attachment). ✅ Passed

---

## 3️⃣ Coverage & Matching Metrics

- **100.00%** of the 55-case plan passed (55 / 55) in a single clean execution.
- All 8 feature groups exercised, including happy paths, validation (422), conflict (409), not-found (404), and RBAC (403) paths.

| Requirement         | Total Tests | ✅ Passed | ❌ Failed |
|---------------------|-------------|-----------|-----------|
| Health              | 1           | 1         | 0         |
| Authentication      | 7           | 7         | 0         |
| User Management     | 11          | 11        | 0         |
| Topics              | 6           | 6         | 0         |
| Question Bank       | 10          | 10        | 0         |
| Game Sessions       | 9           | 9         | 0         |
| Gamification        | 5           | 5         | 0         |
| Supervisor Reports  | 6           | 6         | 0         |
| **Total**           | **55**      | **55**    | **0**     |

**Notes on the iteration to 100%:** The final 55/55 was achieved in a single run after refining the plan. Earlier runs (47/55, then 6/9) surfaced **test-design artifacts only**, not backend defects:
- 5 tests collided on the "one active session per user" rule (409) because they shared `guarda1`; fixed by giving each game test its own freshly-created user (correct backend behavior).
- **TC036** asserted the question nested under `session`; the API correctly returns it as a sibling top-level `question` key.
- **TC039** expected 403 for cross-user access; the API intentionally returns **404** so a user cannot probe another user's session existence. The test now asserts 404.
- **TC040** needed to read `choice_id` from `response['question']['choices'][i]['id']`.

No backend code changes were required; all corrections were to test expectations.

---

## 4️⃣ Key Gaps / Risks

The functional surface is fully green. Three code-level observations remain (independent of the test results), worth addressing for production robustness:

1. **Unguarded pagination input** — `app/api/users.py` (`list_users`) parses `page`/`per_page` with bare `int()`. A non-numeric value (e.g. `?page=abc`) raises `ValueError` → **HTTP 500** instead of a clean 422. (`app/api/questions.py` already does this safely with `type=int`.) *Suggested test to add: `GET /api/v1/users?page=abc` should not 500.*

2. **Insecure default secret** — `app/config.py` falls back to `dev-secret-change-me` for `SECRET_KEY`/`JWT_SECRET` when unset. Acceptable for local dev but must be enforced (fail-fast) in production so tokens are never signed with a known key.

3. **Write-on-every-request** — `app/auth/decorators.py` updates `last_activity_at` and commits on **every** authenticated call, adding one DB write per request and potential contention under load. Consider throttling (e.g. update at most once per N minutes).

**Coverage notes:** Cognito mode (`AUTH_MODE=cognito`) was not exercised (local-mode environment). The `import` partial-failure rollback, 50/50 + skip combined flows, and month-period leaderboard math could be expanded in a future pass.
