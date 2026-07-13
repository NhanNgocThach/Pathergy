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
- Swagger documentation and automated tests

This phase does not add passwords, login sessions, JWT, OAuth, QR invitations,
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
  services/
    rxnorm.py
    screening.py
    accounts.py
    families.py
migrations/
  env.py                     Alembic environment
  versions/
    0001_phase3_baseline.py
    0002_accounts_and_families.py
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

## Family workflow examples

There is no authentication system yet. Endpoints use an explicit
`requesting_user_id` in the request body or query string for development ownership
checks. IDs are still verified against database relationships; they are not trusted
automatically.

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

## Security limitations

- `requesting_user_id` is not authentication and can be impersonated by a caller.
- There are no passwords, tokens, login sessions, OAuth, verified emails, or audit
  identity guarantees.
- Family relationship labels are user-provided and are not legal proof.
- This phase does not verify guardianship or consent.
- Do not deploy this educational prototype with real health information.

A family membership grants limited access. It does not transfer ownership of the
personal health profile. Leaving a family group does not delete personal health
data. This phase does not include real authentication or verified legal
guardianship.

## Deliberately out of scope

QR and email invitations, passwords, JWT, OAuth, real authentication, doctor
accounts, prescriptions, document uploads, frontend work, multilingual support,
AI, AWS, Docker, FHIR, openFDA, DailyMed, drug interactions, food recommendations,
and allergy-screening changes are not included.

RxNorm documentation: <https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html>
