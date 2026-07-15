# Pathergy

Pathergy is a beginner-friendly educational application about medication safety
and personal health-data sharing. Its backend uses FastAPI, SQLAlchemy, SQLite
locally, PostgreSQL for cloud deployment, Pydantic, Alembic, and Pytest. The web application adds a Next.js and TypeScript
frontend for all currently implemented user-facing APIs.

> Use fictional information only. Pathergy is not medical software, does not
> provide medical advice, and does not determine whether a medication is safe.

## Current features

- Patient and allergy CRUD
- RxNorm medication and active-ingredient lookup
- Debounced RxNorm medication-name autocomplete with keyboard navigation
- Conservative medication/allergy screening
- Persisted medication screening history
- Development-only personal user accounts
- One personal patient profile per user
- Family groups with multiple memberships per user
- OWNER, ADMIN, and MEMBER roles
- Soft leave/removal with membership history retained
- Separate data-sharing permissions for every family membership
- Argon2id password hashing and email verification
- JWT access tokens with 15-minute expiration
- Hashed 30-day refresh tokens with rotation and replay detection
- Per-device session management, logout, and session revocation
- Password reset, password change, account lockout, and rate-limit hooks
- JWT authorization for patient, allergy, screening, account, and family APIs
- Ownership and family data-permission enforcement
- Responsive authentication pages and protected application shell
- Automatic access-token refresh with single-use refresh-token rotation
- Frontend form validation, accessible error states, and mocked component tests
- Dashboard, personal health-profile viewing/editing, and allergy management UI
- RxNorm medication search, conservative allergy screening, and history UI
- Family groups, memberships, roles, enforced sharing permissions, and profiles
- Responsive desktop/mobile navigation and accessible status handling
- English, Vietnamese, and Simplified Chinese language selection for the shared
  shell, authentication, dashboard, and account-settings experience
- Browser security headers, a 64 KiB request-body limit, and separate abuse
  throttling for public RxNorm endpoints
- Swagger documentation and automated tests

This phase does not add OAuth, social login, passkeys, biometric login, QR or
email invitations, verified legal guardianship, or unsupported backend features.

## Personal ownership versus family access

The central design is:

```text
UserAccount
  └── Personal Patient Profile
        ├── Allergies
        └── Screening History

UserAccount
  └── FamilyMemberships
        ├── Family Group A + its permissions
        ├── Family Group B + its permissions
        └── Family Group C + its permissions
```

The `Patient` profile owns the health information. A `FamilyMembership` grants
limited access settings for one family group; it does not transfer ownership of
the patient profile.

Leaving or being removed from a family group changes the membership status. It
does not delete the user account, patient profile, allergies, or screening
history. Historical membership rows remain in the database for audit purposes.

## Data model

### UserAccount

Each development account contains an email, display name, active flag, and a
unique `patient_id`. The unique database constraint guarantees that one patient
profile cannot belong to two user accounts.

Existing standalone patients remain valid. A new user can either create a new
profile or link an existing unowned patient profile.

### FamilyGroup

A user can create multiple groups. The creator automatically receives an ACTIVE
OWNER membership.

### FamilyMembership

This is the many-to-many connection between users and family groups. One user may
have memberships in several groups.

Roles:

- `OWNER`
- `ADMIN`
- `MEMBER`

Relationships:

- `SELF`
- `SPOUSE`
- `CHILD`
- `PARENT`
- `SIBLING`
- `RELATIVE`
- `CAREGIVER`
- `OTHER`

Statuses:

- `PENDING`
- `ACTIVE`
- `LEFT`
- `REMOVED`
- `DECLINED`

Only an ACTIVE membership receives normal family-group access. The final ACTIVE
OWNER cannot leave, be removed, or be demoted until another OWNER is active.

### FamilyDataPermission

Each membership has its own permission rows for:

- `BASIC_PROFILE`
- `ALLERGIES`
- `CURRENT_MEDICATIONS`
- `SCREENING_HISTORY`
- `MEDICAL_DOCUMENTS`
- `EMERGENCY_INFORMATION`

All permissions default to `can_view: false` and `can_edit: false`. A user controls
the permissions for their own ACTIVE membership. Group ownership does not grant
automatic access to another adult member's health records.

Implemented authorization mappings:

- `BASIC_PROFILE`: view or edit a family member's patient profile.
- `ALLERGIES`: view or edit a family member's allergy records.
- `SCREENING_HISTORY`: view screening history; `can_edit` permits creating a
  history row through a medication check.

A family medication check requires both `ALLERGIES.can_view` and
`SCREENING_HISTORY.can_edit` on the target member's membership in the same ACTIVE
family group. Other permission types remain stored for future compatibility and
do not grant access to unimplemented features.

## Project structure

```text
app/
  main.py                    FastAPI setup and error handlers
  database.py                SQLite/PostgreSQL engine and request sessions
  models.py                  All SQLAlchemy database models
  schemas.py                 Patient, allergy, medication schemas
  auth_schemas.py            Authentication request and response schemas
  auth_config.py             Environment-based authentication settings
  family_schemas.py          Account, family, membership, permission schemas
  errors.py                  Stable service error response handling
  crud.py                    Existing patient/allergy/history operations
  routes/
    patients.py
    allergies.py
    medications.py
    medication_checks.py
    users.py
    family_groups.py
    auth.py
  services/
    rxnorm.py
    screening.py
    accounts.py
    families.py
    auth.py
    auth_security.py
    authorization.py          Ownership and family health-data access checks
migrations/
  env.py                     Alembic environment
  versions/
    0001_phase3_baseline.py
    0002_accounts_and_families.py
    0003_authentication.py
tests/                       Unit, API, migration, and regression tests
frontend/                    Complete Next.js frontend for implemented APIs
docs/UI_UX_SPECIFICATION.md  Product design and accessibility specification
alembic.ini
requirements.txt
README.md
```

## Setup

Python 3.11 or newer is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env

# Generate two different secrets and copy them into .env:
python -c "import secrets; print(secrets.token_urlsafe(48))"
python -c "import secrets; print(secrets.token_urlsafe(48))"

python -m alembic upgrade head
```

Alembic creates a new database or upgrades an older Pathergy SQLite database
without recreating existing health tables. Run migrations before starting the API.

## Run the API

```powershell
python -m uvicorn app.main:app --reload
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/>
- Deployment health check: <http://127.0.0.1:8000/health>

## Run the web frontend

The backend `.env` must allow the browser origin:

```dotenv
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
AUTH_DEVELOPMENT_BASE_URL=http://localhost:3000
```

In a second PowerShell window:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open <http://localhost:3000>. See [frontend/README.md](frontend/README.md) for
the implemented routes, authentication flow, test commands, token-storage
decision, and current frontend security limitations.

## Development account examples

`POST /users` and `POST /patients` remain available only when
`AUTH_DEVELOPMENT_MODE=true`, and both require a valid access token. Accounts
created through `POST /users` do not have a password and cannot log in. New
authenticated accounts should use `POST /auth/register`. Authenticated
registration always creates a new personal profile; it cannot claim an existing
standalone patient by ID. Existing-profile linking remains a development-only
`POST /users` behavior.

Send the authenticated development actor's token with these requests:

```http
Authorization: Bearer <access_token>
```

Create a user and a new personal profile:

```http
POST /users
```

```json
{
  "email": "fictional.person@example.com",
  "display_name": "Fictional Person",
  "profile": {
    "first_name": "Fictional",
    "last_name": "Person",
    "date_of_birth": "1990-01-01"
  }
}
```

Alternatively, replace `profile` with an existing unowned `patient_id`.

Retrieve the account and profile:

```http
GET /users/1
GET /users/1/profile
```

## Authentication

Authentication extends the existing `UserAccount`; it does not create a second
account type. An authenticated user still owns exactly one personal `Patient`
profile.

```text
Register -> verify email -> login
         -> 15-minute JWT access token
         -> 30-day opaque refresh token
         -> rotate refresh token on every refresh
         -> revoke the session on logout, reset, or replay
```

### Environment variables

Authentication secrets are required only when an authentication endpoint is used:

- `AUTH_JWT_SECRET`: signs access tokens; use at least 32 random characters.
- `AUTH_TOKEN_HASH_SECRET`: HMAC-hashes verification, reset, and refresh tokens;
  use a different value with at least 32 random characters.
- `AUTH_DEVELOPMENT_MODE`: when `true`, registration and forgot-password
  responses include development URLs containing their single-use tokens.
- `AUTH_DEVELOPMENT_BASE_URL`: base URL used for those development links.
- `AUTH_RATE_LIMIT_PER_MINUTE`: per-process authentication request limit.
- `CORS_ALLOWED_ORIGINS`: comma-separated browser origins permitted to call the
  API; local defaults are shown in `.env.example`.
- `DATABASE_URL`: local SQLite URL or a deployed Neon PostgreSQL URL. Standard
  PostgreSQL URLs use the included Psycopg 3 driver.

Do not commit real secret values. Changing either secret invalidates the tokens
that depend on it.

### Registration and email verification

```http
POST /auth/register
```

```json
{
  "email": "fictional.auth@example.com",
  "display_name": "Fictional Auth Person",
  "password": "Fictional1!Pass",
  "confirm_password": "Fictional1!Pass",
  "profile": {
    "first_name": "Fictional",
    "last_name": "Auth",
    "date_of_birth": "1990-01-01"
  }
}
```

Passwords require at least 10 characters with uppercase, lowercase, number, and
special characters. Only an Argon2id hash is stored.

In development mode, copy the `token` value from the query string in the returned
`verification_url`, then submit it in the request body:

```http
POST /auth/verify-email
```

```json
{"token": "single-use-token-from-development-url"}
```

Verification tokens expire after 24 hours and are stored only as keyed hashes.
Production mode does not return the URL; a future email-provider integration must
deliver the same token.

### Login, access tokens, and refresh rotation

Only active, verified accounts with a password may log in:

```http
POST /auth/login
```

```json
{
  "email": "fictional.auth@example.com",
  "password": "Fictional1!Pass",
  "device_name": "Fictional laptop",
  "device_type": "desktop"
}
```

The response contains a 15-minute JWT `access_token` and a 30-day opaque
`refresh_token`. Send the access token as:

```http
Authorization: Bearer <access_token>
```

Use `POST /auth/refresh` with the refresh token. Every successful refresh stores
the old token hash as used, returns a new refresh token, and invalidates the old
one. Reusing an old token is treated as replay and revokes the entire session.
No plaintext refresh token is stored.

Access-token validation also checks the database session, so logout, password
reset, password change, or replay revocation takes effect before the JWT's normal
expiration.

### Sessions and logout

Each login creates one session containing device metadata, IP address, user agent,
timestamps, expiration, and revocation state. `GET /auth/sessions` returns only
active sessions and identifies the current one.

- `POST /auth/logout` revokes the current session.
- `DELETE /auth/sessions/{session_id}` revokes one session owned by the user.
- `DELETE /auth/sessions` revokes all of the user's sessions, including the current
  session.

### Password recovery and change

`POST /auth/forgot-password` always returns the same general message to avoid
revealing whether an email exists. Development mode includes a reset URL for a
registered password account. Reset tokens expire after one hour, are single-use,
and are stored only as keyed hashes.

`POST /auth/reset-password` changes the password and revokes all sessions.
`POST /auth/change-password` requires a valid access token and the current
password, then changes the password and revokes all sessions. Both flows require
the same password-strength rules as registration.

Five consecutive invalid password attempts temporarily lock the account for 15
minutes. Authentication and public RxNorm requests have separate in-memory rate
limits. The included limiters are per process and are not a shared production
rate-limit or large-scale DDoS solution.

API responses add browser security headers that prevent framing and MIME
sniffing, restrict browser capabilities, and disable caching on authenticated or
health-data routes. JSON request bodies are capped at 64 KiB by default. The
Next.js production build adds its own framing, MIME, referrer, permissions, CSP,
and HTTPS transport headers. These controls are defense in depth; Vercel/Render
edge protection is still the first line of defense against distributed traffic.

### Production considerations

Production must disable `AUTH_DEVELOPMENT_MODE`, deliver verification/reset links
through a trusted email provider, use HTTPS, store secrets in a managed secret
store, rotate secrets deliberately, and replace the in-memory limiter with a
shared rate-limit backend. Session/IP/user-agent retention, consent records, and
security audit logging also require an explicit privacy policy before real
deployment.

## Authorization

All patient, allergy, medication-check, screening-history, account/profile, and
family endpoints require `Authorization: Bearer <access_token>`. FastAPI validates
the JWT and its database session, then derives the requester from the token's
subject. Patient IDs, user IDs, group IDs, and membership IDs identify resources;
they never establish the requester's identity.

The owner of a personal patient profile may use its implemented health APIs. For
another person's profile, both users must have ACTIVE memberships in the same
family group and the target member must have enabled the relevant permission.
OWNER and ADMIN roles control group management only; they do not bypass another
member's health-data choices.

Authorization failures use stable service errors:

- `401 AUTHENTICATION_REQUIRED` when the Bearer token is missing.
- `401 INVALID_ACCESS_TOKEN` or `ACCESS_TOKEN_EXPIRED` for an unusable token.
- `403 FAMILY_ACCESS_DENIED`, `MEMBERSHIP_NOT_ACTIVE`, or `INSUFFICIENT_ROLE`
  for family-management denial.
- `403 FAMILY_PERMISSION_DENIED` when active family members lack the target's
  required data permission.
- `404 PATIENT_ACCESS_DENIED` for an unrelated or unowned patient, which avoids
  confirming that another person's record exists.

## Family workflow examples

Every family request uses the user derived from the access token. Do not send
`requesting_user_id`; it is rejected in request bodies and ignored as identity in
query strings.

Create a group. User `1` becomes its ACTIVE OWNER:

```http
POST /family-groups
```

```json
{
  "name": "Fictional Household"
}
```

Add existing user `2` as PENDING:

```http
POST /family-groups/1/members
```

```json
{
  "user_id": 2,
  "role": "MEMBER",
  "relationship": "RELATIVE"
}
```

Activate the membership:

```http
PUT /family-groups/1/members/2
```

```json
{
  "status": "ACTIVE"
}
```

Set user `2`'s sharing choices for this membership:

```http
PUT /family-groups/1/members/2/permissions
```

```json
{
  "permissions": [
    {"data_type": "ALLERGIES", "can_view": true, "can_edit": false},
    {
      "data_type": "SCREENING_HISTORY",
      "can_view": true,
      "can_edit": false
    }
  ]
}
```

The same user can select different values for a membership in another group.
Changes in Family Group A do not affect Family Group B.

Leave without deleting personal data:

```http
POST /family-groups/1/members/2/leave
```

No request body is required. The route verifies that the path's user ID is the
authenticated user.

The response membership has `status: "LEFT"` and a `left_at` timestamp.

## Endpoints

### Existing health and medication endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/patients` | Create a patient |
| `GET` | `/patients` | List patients |
| `GET` | `/patients/{patient_id}` | Retrieve a patient |
| `PUT` | `/patients/{patient_id}` | Update a patient |
| `DELETE` | `/patients/{patient_id}` | Delete a patient and owned health rows |
| `POST` | `/patients/{patient_id}/allergies` | Create an allergy |
| `GET` | `/patients/{patient_id}/allergies` | List allergies |
| `GET` | `/patients/{patient_id}/allergies/{allergy_id}` | Retrieve an allergy |
| `PUT` | `/patients/{patient_id}/allergies/{allergy_id}` | Update an allergy |
| `DELETE` | `/patients/{patient_id}/allergies/{allergy_id}` | Delete an allergy |
| `GET` | `/medications/suggestions?q={prefix}&limit=8` | Suggest unique RxNorm names and RxCUIs for autocomplete |
| `GET` | `/medications/search?name={name}` | Search RxNorm ingredients |
| `POST` | `/patients/{patient_id}/medication-check` | Check recorded allergies and store history |
| `GET` | `/patients/{patient_id}/screening-history` | List authorized screening history |

All rows in this table except `/`, `/health`, medication suggestions, and medication search require a Bearer access
token. `POST /patients` is additionally development-only.

### Development accounts

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/users` | Create an account and create/link one profile |
| `GET` | `/users/{user_id}` | Retrieve an account |
| `GET` | `/users/{user_id}/profile` | Retrieve its personal patient profile |
| `GET` | `/users/{user_id}/family-groups` | List that user's membership history |

All development-account endpoints require a Bearer token. `POST /users` is also
disabled when `AUTH_DEVELOPMENT_MODE=false`; account and membership-history reads
are self-only. Profile reads may use `BASIC_PROFILE.can_view` family access.

### Authentication

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Register an account and personal profile |
| `POST` | `/auth/verify-email` | Consume a single-use verification token |
| `POST` | `/auth/login` | Create a session and access/refresh tokens |
| `POST` | `/auth/refresh` | Rotate a refresh token and issue a new pair |
| `POST` | `/auth/logout` | Revoke the current session |
| `POST` | `/auth/forgot-password` | Start password recovery without email enumeration |
| `POST` | `/auth/reset-password` | Consume a reset token and revoke sessions |
| `POST` | `/auth/change-password` | Change password and revoke sessions |
| `GET` | `/auth/me` | Retrieve the authenticated account |
| `GET` | `/auth/sessions` | List active sessions |
| `DELETE` | `/auth/sessions/{session_id}` | Revoke one owned session |
| `DELETE` | `/auth/sessions` | Revoke all sessions |

### Family groups and memberships

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/family-groups` | Create a group and OWNER membership |
| `GET` | `/family-groups/{family_group_id}` | Retrieve a group as an ACTIVE member |
| `PUT` | `/family-groups/{family_group_id}` | Update a group as OWNER or ADMIN |
| `POST` | `/family-groups/{family_group_id}/members` | Add an existing user as PENDING |
| `GET` | `/family-groups/{family_group_id}/members` | List current and historical memberships |
| `GET` | `/family-groups/{family_group_id}/members/{user_id}` | Retrieve active/latest membership |
| `PUT` | `/family-groups/{family_group_id}/members/{user_id}` | Activate or update membership |
| `POST` | `/family-groups/{family_group_id}/members/{user_id}/leave` | Leave voluntarily |
| `DELETE` | `/family-groups/{family_group_id}/members/{user_id}` | Soft-remove a member |

### Permissions

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/family-groups/{family_group_id}/members/{user_id}/permissions` | Read own ACTIVE membership permissions |
| `PUT` | `/family-groups/{family_group_id}/members/{user_id}/permissions` | Update own ACTIVE membership permissions |

## Stable service errors

Account and family service errors have this structure:

```json
{
  "detail": {
    "code": "FAMILY_ACCESS_DENIED",
    "message": "An active family membership is required"
  }
}
```

Typical status codes:

- `403` for denied family or permission access
- `404` for missing users, profiles, groups, or memberships
- `409` for duplicate membership and final-owner conflicts
- `422` for unsupported roles, relationships, statuses, or permission types

## Run tests

```powershell
python -m pytest -v
```

Tests use isolated temporary or in-memory SQLite databases. RxNorm calls are
mocked, so the test suite does not require live internet access.

Authentication tests cover registration, duplicate email, Argon2id hashing,
verification, login, JWT validation, refresh rotation, replay detection, logout,
session management, password reset/change, lockout, and expired/invalid tokens.

Authorization tests cover missing and invalid tokens, own-profile access,
unrelated-patient isolation, independent `can_view`/`can_edit` enforcement,
family health permissions, medication-check permissions, role checks, inactive
memberships, final-owner protection, and requester-ID impersonation attempts.

## Security limitations

- There is no OAuth, MFA, verified family consent, or production audit identity.
- The in-memory rate limiter is per process and is unsuitable for multiple server
  instances.
- A free single-instance application cannot guarantee availability during a
  large distributed denial-of-service attack. App limits reduce ordinary abuse;
  provider edge controls must absorb distributed traffic.
- Development verification/reset URLs expose bearer-like single-use tokens in API
  responses and must be disabled in production.
- The browser client holds its access token in memory and refresh token
  in `sessionStorage` because the current backend does not issue HttpOnly cookies.
  This is vulnerable to token theft if an XSS flaw is introduced and is not a
  final production token-storage design.
- Family relationship labels are user-provided and are not legal proof.
- This phase does not verify guardianship or consent.
- Do not deploy this educational prototype with real health information.

A family membership grants limited access. It does not transfer ownership of the
personal health profile. Leaving a family group does not delete personal health
data. Authentication does not yet establish verified family relationships,
guardianship, or consent.

## Deliberately out of scope

QR and email invitations, phone/SMS authentication, passkeys, Face ID,
fingerprints, Google/Apple login, OAuth, MFA, doctor accounts, prescriptions,
document uploads, full translation of every backend validation message, AI, AWS,
Docker, FHIR, openFDA, DailyMed,
drug interactions, food recommendations, and unsupported backend/frontend
features are not included.

RxNorm documentation: <https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html>

## Portfolio cloud deployment

Pathergy is prepared for a GitHub-connected Vercel frontend, Render FastAPI
backend, and Neon PostgreSQL database. See
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the exact environment variables,
Alembic command, automatic deployment flow, authentication limitations, free
tier cold starts, and steps for returning to local development.

- Live web application: <https://pathergy.vercel.app>
- Live API documentation: <https://pathergy-api.onrender.com/docs>
- Live API health check: <https://pathergy-api.onrender.com/health>

This configuration is for fictional portfolio data only. It is not described as
production-ready or HIPAA-compliant.
