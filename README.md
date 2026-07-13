# Pathergy

Pathergy is a beginner-friendly educational backend about medication safety and
personal health-data sharing. It uses FastAPI, SQLAlchemy, SQLite, Pydantic,
Alembic, and Pytest.

> Use fictional information only. Pathergy is not medical software, does not
> provide medical advice, and does not determine whether a medication is safe.

## Current features

- Patient and allergy CRUD
- RxNorm medication and active-ingredient lookup
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
- Swagger documentation and automated tests

This phase does not add OAuth, social login, passkeys, biometric login, QR or
email invitations, or verified legal guardianship.

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

Some listed data types are not implemented yet. This phase stores their permission
settings for future compatibility; it does not add family health-data viewing
endpoints.

## Project structure

```text
app/
  main.py                    FastAPI setup and error handlers
  database.py                SQLite engine and request sessions
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
migrations/
  env.py                     Alembic environment
  versions/
    0001_phase3_baseline.py
    0002_accounts_and_families.py
    0003_authentication.py
tests/                       Unit, API, migration, and regression tests
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

## Development account examples

`POST /users` remains available for the earlier development workflows. Accounts
created through that endpoint do not have a password and cannot log in. New
authenticated accounts should use `POST /auth/register`. Authenticated
registration always creates a new personal profile; it cannot claim an existing
standalone patient by ID. Existing-profile linking remains a development-only
`POST /users` behavior.

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
minutes. The included rate limiter is an in-memory development hook; it is not a
shared production rate limiter.

### Production considerations

Production must disable `AUTH_DEVELOPMENT_MODE`, deliver verification/reset links
through a trusted email provider, use HTTPS, store secrets in a managed secret
store, rotate secrets deliberately, and replace the in-memory limiter with a
shared rate-limit backend. Existing health and family routes must not be exposed
until authenticated-user authorization replaces their development ID inputs.
Session/IP/user-agent retention and security audit logging also require an explicit
privacy policy before real deployment.

## Family workflow examples

Authentication now exists for the `/auth` account and session workflows. Existing
family endpoints intentionally retain the explicit `requesting_user_id` in the
request body or query string for backward-compatible development ownership checks.
They do not yet derive that ID from the JWT. IDs are checked against database
relationships, but callers can still impersonate another ID on those routes.

Create a group. User `1` becomes its ACTIVE OWNER:

```http
POST /family-groups
```

```json
{
  "requesting_user_id": 1,
  "name": "Fictional Household"
}
```

Add existing user `2` as PENDING:

```http
POST /family-groups/1/members
```

```json
{
  "requesting_user_id": 1,
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
  "requesting_user_id": 1,
  "status": "ACTIVE"
}
```

Set user `2`'s sharing choices for this membership:

```http
PUT /family-groups/1/members/2/permissions
```

```json
{
  "requesting_user_id": 2,
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

```json
{
  "requesting_user_id": 2
}
```

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
| `GET` | `/medications/search?name={name}` | Search RxNorm ingredients |
| `POST` | `/patients/{patient_id}/medication-check` | Check recorded allergies and store history |

### Development accounts

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/users` | Create an account and create/link one profile |
| `GET` | `/users/{user_id}` | Retrieve an account |
| `GET` | `/users/{user_id}/profile` | Retrieve its personal patient profile |
| `GET` | `/users/{user_id}/family-groups` | List that user's membership history |

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

## Security limitations

- Authentication is implemented for `/auth` workflows, but existing patient,
  allergy, medication-check, development-account, and family routes are not yet
  protected by JWT dependencies.
- `requesting_user_id` on family routes is not authenticated and can be
  impersonated by a caller.
- There is no OAuth, MFA, verified family consent, or production audit identity.
- The in-memory rate limiter is per process and is unsuitable for multiple server
  instances.
- Development verification/reset URLs expose bearer-like single-use tokens in API
  responses and must be disabled in production.
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
document uploads, frontend work, multilingual support, AI, AWS, Docker, FHIR,
openFDA, DailyMed, drug interactions, food recommendations, and allergy-screening
changes are not included.

RxNorm documentation: <https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html>
