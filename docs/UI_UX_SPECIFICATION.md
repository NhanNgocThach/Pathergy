# Pathergy Web Application UI/UX Specification

Status: Product design baseline  
Scope: UI/UX planning only  
Backend baseline: Pathergy API 6.1.0 with authentication and authorization  
Audience: future frontend developers, product designers, and accessibility reviewers

> Pathergy is an educational prototype. It is not medical software, does not
> provide medical advice, and must never describe a medication as safe,
> approved, recommended, suitable, or free of allergy risk.

## 1. Product scope and principles

Pathergy helps an individual maintain a basic personal health profile, record
allergies, inspect standardized RxNorm medication ingredients, run a conservative
recorded-allergy comparison, review screening history, and participate in one or
more family groups.

The design must follow these principles:

1. **Personal ownership first.** A user owns one personal patient profile.
2. **Family role is not health-data ownership.** OWNER and ADMIN manage a family
   group but do not automatically receive access to another member's health data.
3. **Permission is explicit.** Family health access is controlled by the target
   member's permission settings for each family membership.
4. **Medical wording is conservative.** Results communicate what was and was not
   found in recorded data; they do not make safety decisions.
5. **Important states are visible in words and symbols.** Color is supportive,
   never the only signal.
6. **Small-screen workflows remain complete.** Medication checking and profile
   selection must not require a desktop viewport.
7. **The UI reflects the current API.** Unsupported actions are not shown as
   active controls.

### 1.1 Implemented now

- Registration, email verification, login, refresh, logout, password reset, and
  password change.
- Active-session listing, one-session revocation, and all-session revocation.
- One personal patient profile created during authenticated registration.
- Authorized patient profile viewing and editing.
- Authorized allergy CRUD.
- Public RxNorm medication lookup.
- Authorized medication allergy screening and persisted screening history.
- Family groups, memberships, roles, relationships, statuses, leave/remove
  behavior, and final-owner protection.
- Per-membership family permission storage and authorization for
  `BASIC_PROFILE`, `ALLERGIES`, and `SCREENING_HISTORY`.
- Membership in multiple family groups.

### 1.2 Planned or unavailable

- Frontend implementation, native mobile applications, and dark mode.
- Email or QR family invitations, user search/directory, invitation acceptance,
  and owner approval workflows.
- Editing account email or display name.
- OAuth, social login, MFA, phone/SMS login, passkeys, Face ID, or fingerprints.
- Current medication management, medical documents, emergency information,
  clinician workflows, prescriptions, interaction checking, or AI features.
- Server-side screening-history filtering, pagination, or a history-detail API.
- Verified guardianship, consent, or legal family relationships.
- Production email delivery for verification and reset links.

## 2. Sitemap and information architecture

```text
Public
├── Login
├── Register (includes personal profile creation)
├── Verify email
├── Forgot password
├── Reset password
└── Medication reference search (optional public entry)

Authenticated application
├── Dashboard
├── My Health
│   ├── Health Profile
│   ├── Allergies
│   ├── Medication Check
│   └── Screening History
├── Families
│   ├── Family list
│   ├── Family detail
│   ├── Member detail
│   └── My sharing permissions
├── Sessions & Security
│   ├── Active sessions
│   └── Change password
└── Account Settings
    ├── Account summary
    └── Logout
```

### 2.1 Desktop navigation

Use a persistent left sidebar at widths of 1024 px and above:

1. Dashboard
2. My Health
   - Profile
   - Allergies
   - Medication Check
   - Screening History
3. Families
4. Sessions & Security
5. Account Settings

The sidebar header contains the Pathergy wordmark and an “Educational prototype”
label. The footer contains the current user's display name, email, and an account
menu. Do not show a family role globally because a user can have a different role
in each family.

### 2.2 Tablet navigation

At 768–1023 px, use a collapsible navigation rail. Labels appear when expanded.
The page title and profile selector remain in the content header, not inside the
rail.

### 2.3 Mobile navigation

At less than 768 px, use five bottom navigation destinations:

- Home
- Health
- Check
- Families
- More

“More” opens Screening History, Sessions & Security, Account Settings, and
Logout. Keep the medication Check destination directly reachable because it is a
primary task. Use page-level back navigation for family and history details.

## 3. User types and journeys

### 3.1 Individual user

Primary goal: maintain their own profile and allergies, check a medication, and
review history.

Journey:

1. Register with account and patient-profile information.
2. Verify email and log in.
3. Review the dashboard and profile.
4. Add known allergies.
5. Search for or check a medication.
6. Read a conservative result and educational disclaimer.
7. Review prior checks and manage device sessions.

### 3.2 Family group owner

Primary goal: create and organize a family group without implying ownership of
members' health information.

Journey:

1. Create a group and become ACTIVE OWNER.
2. Add an existing user by numeric user ID using the current backend behavior.
3. Assign relationship and initial role; membership begins PENDING.
4. Activate or decline the pending membership through membership update.
5. Manage roles and remove members when permitted.
6. View only health data that each target member explicitly shares.
7. Transfer/add another OWNER before attempting to leave or remove the final
   owner.

### 3.3 Family group admin

Primary goal: assist with group and membership management.

An ACTIVE ADMIN can update the group and perform the same currently implemented
membership-management calls as an OWNER. The UI must still hide or disable health
data that the target member has not shared. “Admin” must never be described as
“full health access.”

### 3.4 Family group member

Primary goal: participate in the group and choose what their own membership
shares.

An ACTIVE MEMBER can view group and membership information, update only their own
family data permissions, and leave voluntarily. They cannot add, update, or
remove other members. PENDING, LEFT, REMOVED, and DECLINED memberships have no
normal family access.

### 3.5 User in multiple family groups

Primary goal: understand which role and permissions apply to which family.

The Families page groups entries by family and displays role, relationship, and
status on each card. Permission settings are edited within one selected family;
the UI states that changes apply only to that family membership. Never provide a
single global “share with all families” switch.

## 4. Screen inventory and screen requirements

### 4.1 Authentication screens

#### Login

- Fields: email, password.
- Optional device metadata is supplied by the frontend as a friendly device name
  and device type; it is not required from the user.
- Primary action: “Log in.”
- Secondary actions: “Forgot password?” and “Create account.”
- Show `EMAIL_NOT_VERIFIED` as a specific next-step message.
- Show `ACCOUNT_LOCKED` without exposing internal security details.
- After success, establish the frontend session and navigate to Dashboard.
- Do not offer “Continue with Google/Apple,” biometric login, or MFA.

#### Register

- Account section: display name, email, password, confirm password.
- Personal profile section: first name, last name, date of birth.
- Explain before submit: “Registration creates your personal health profile.”
- Password help is visible before error: at least 10 characters, uppercase,
  lowercase, number, and special character.
- Date of birth cannot be in the future.
- Success routes to “Check your email” rather than directly into the app.
- In development mode only, a returned verification URL may be presented as a
  clearly labeled developer shortcut. Never present it as production behavior.

#### Verify email

- Read the single-use token from the frontend route and submit it to the API.
- Loading copy: “Verifying your email…”
- Success: “Email verified. You can now log in.”
- Invalid, expired, or reused token: explain that the link is no longer valid.
- The backend currently has no resend-verification endpoint; do not show a
  functional resend button. Link to support/help text or registration guidance.

#### Forgot password

- One email field and “Send reset instructions.”
- Always show the same success message, whether or not the account exists.
- In development mode only, the API may return a developer reset URL.

#### Reset password

- Read token from the frontend route.
- Fields: new password and confirmation.
- On success, state that all sessions were revoked, then return to Login.
- Invalid/expired/reused token gets a non-destructive error panel.

#### Change password

- Fields: current password, new password, confirmation.
- Confirm that a successful change signs out every device, including this one.
- After success, clear frontend credentials and navigate to Login.

#### Active sessions

- List device name/type, approximate IP, user agent fallback, created time, last
  used time, expiry, and a “Current session” badge.
- Provide “Revoke” for each session and “Revoke all sessions.”
- Revoking the current session or all sessions returns the user to Login.
- Use a confirmation dialog for revoke-all; one-session revocation may use a
  lighter confirmation unless it is the current session.

### 4.2 Dashboard

Dashboard modules:

1. **Personal summary:** name and date of birth from the personal patient profile.
2. **Known allergies:** count and up to three allergy rows, with “View all.”
3. **Recent checks:** up to five client-selected rows from screening history.
4. **Families:** active family count plus role/status per membership.
5. **Quick actions:** Add allergy, Check medication, View history, Create family.
6. **Security notice:** session or verification-related information only when
   actionable; do not create an alarm-style notice by default.

There is no dashboard aggregate API. Load `/auth/me`, the personal profile,
allergies, history, and family memberships in parallel. Each module needs its own
loading and retry state so one failed request does not blank the entire page.

### 4.3 Personal Health Profile

#### View profile

- Show first name, last name, date of birth, and ownership/sharing explanation.
- Label the current user's record “My profile.”
- A permitted family profile is labeled “Shared profile,” never “My dependent”
  unless that legal relationship is established in a future phase.
- Hide Edit if the request is known to be view-only. Because the API does not
  return capability metadata with a patient, the UI may discover edit denial on
  submit and must handle `FAMILY_PERMISSION_DENIED` gracefully.

#### Edit profile

- Editable fields: first name, last name, date of birth.
- Submit the complete patient payload because the backend update schema is not
  partial.
- Confirm success inline and preserve focus context.
- Do not provide personal-profile deletion. A linked personal profile cannot be
  deleted through current patient CRUD.

#### Privacy explanation

Use concise copy:

> Your health profile belongs to your account. Family roles manage the group;
> your sharing permissions control access to your health information.

### 4.4 Allergies

#### Allergy list

- Profile selector at top, limited to profiles the API makes discoverable.
- Columns/cards: substance, optional RxCUI, reaction, severity, actions.
- Desktop uses a table; mobile uses stacked cards.
- Sort client-side by substance or severity; no server sorting exists.

#### Add/Edit allergy

- Fields: substance, optional numeric RxCUI, optional reaction, severity.
- Explain RxCUI as an optional standardized RxNorm identifier; do not require a
  beginner to know one.
- Severity options: Mild, Moderate, Severe.
- Reaction is the only current notes-like field and is limited to 200 characters.
- The edit request sends all allergy fields.
- If edit permission is unavailable, render read-only detail and no mutation
  controls.

#### Delete allergy

- Confirmation title: “Delete allergy record?”
- Include the substance name and explain that deletion removes the recorded item,
  not a medical diagnosis.
- Primary destructive action: “Delete record.”

#### Empty state

> No allergy records have been added for this profile.

Do not change this to “No allergies” because the database may be incomplete.

### 4.5 Medication search and screening

Use one guided workspace with two related actions:

1. Standardized medication search (`GET /medications/search`).
2. Patient-specific recorded-allergy check
   (`POST /patients/{patient_id}/medication-check`).

#### Input area

- Profile selector: “Check for” with “My profile” first and permitted profiles
  after it.
- Medication name, 2–100 characters.
- Primary action: “Check recorded allergies.”
- Secondary action: “View medication ingredients” when using reference-search
  mode.
- Do not auto-run on every keystroke; submit deliberately to avoid unnecessary
  external calls and history records.

#### Loading

- Keep the submitted medication and profile visible.
- Announce “Checking standardized ingredients and recorded allergies…” through a
  polite live region.
- Disable duplicate submission but leave Cancel/Back navigation available.

#### Medication information

- User query.
- Normalized RxNorm name.
- Medication RxCUI.
- Active ingredient list with ingredient name and RxCUI.
- If ingredient data is incomplete, show that limitation before any result copy.

#### Result presentation

**POTENTIAL_ALLERGY_MATCH**

- Heading: “Potential allergy match.”
- Supporting icon: warning triangle with accessible label.
- Show every returned match: recorded substance, standardized ingredient,
  optional identifiers, and match method in a technical disclosure.
- Action: “Review with a qualified healthcare professional.”
- Never offer “Take medication” or a positive safety action.

**NO_RECORDED_MATCH_FOUND**

- Heading: “No recorded match found.”
- Use neutral blue/gray, not success green.
- Copy: “The listed active ingredients did not match the allergy records
  currently stored for this profile. This does not mean the medication is safe.”

**UNABLE_TO_VERIFY**

- Heading: “Unable to verify ingredients.”
- Copy: “Pathergy could not confirm the medication and its active ingredients.
  No safety conclusion can be made.”
- Offer Retry and a professional-review reminder.

Every screening result includes the API disclaimer:

> Educational prototype only. This result is not medical advice. Consult a
> qualified healthcare professional.

#### External service error

Standalone medication search may return 502 or 504. Show “Medication information
is temporarily unavailable” with Retry. A patient medication check converts
RxNorm failures into `UNABLE_TO_VERIFY` and stores that result, so render the
returned result rather than a generic network failure when HTTP 200 is received.

### 4.6 Screening History

#### History list

- Profile selector.
- Rows: searched medication, normalized name when available, RxCUI when
  available, result badge, date/time.
- Default order is newest first, matching the backend.
- Client-side filters only: medication text, result, and date range.
- Clearly label filters “On loaded history”; the API has no server-side filter or
  pagination.

#### History detail

The current history response does not contain active ingredients, match records,
or the original result message. Therefore detail may show only fields returned by
the list API. The complete immediate screening result may be shown directly after
a check, but must not be reconstructed later from missing data.

#### Empty and denied states

- Empty: “No medication checks have been recorded for this profile.”
- Permission denied: “This profile has not shared screening history with you.”
- Do not suggest changing another user's permission. Link to the user's own
  family permission settings only when relevant.

### 4.7 Families

#### Family group list

- Active family cards first, then historical/inactive membership cards.
- Show family name, the user's role, relationship, membership status, and joined
  or left date when available.
- Provide “Create family group.”
- For multiple groups, permission summaries are shown per card, never merged.

#### Create family group

- One required group-name field.
- Explain that the creator becomes ACTIVE OWNER.
- After success, navigate to group detail.

#### Family group detail

- Header: family name, current user's role and status.
- Sections: Members, My sharing permissions, and management actions.
- OWNER/ADMIN see Rename group and membership management.
- MEMBER sees group information, their own permissions, and Leave family.
- Do not expose group deactivation in the first frontend implementation. Although
  `is_active` is writable, current backend access checks do not define a complete
  inactive-group UX contract.

#### Member list and detail

- Display role, relationship, status, joined/left dates, and user ID.
- Current API membership responses do not include member names or emails. Until
  the backend supplies safe display data, use “User #123” rather than guessing.
- Status badges: Pending, Active, Left, Removed, Declined.
- Historical rows are read-only.

#### Add existing member

- Current input: numeric user ID, role, relationship.
- Label honestly: “Existing Pathergy user ID.”
- Helper text: “The current prototype cannot search by name or email.”
- Success state explains that the membership is PENDING.
- There is no invitation delivery or member self-accept endpoint. Activation is a
  manager action in the current backend.

#### Update role, relationship, and status

- OWNER/ADMIN can edit an open membership.
- Role options: OWNER, ADMIN, MEMBER.
- Relationship options: SELF, SPOUSE, CHILD, PARENT, SIBLING, RELATIVE,
  CAREGIVER, OTHER.
- PENDING can remain pending, become ACTIVE, or become DECLINED.
- ACTIVE membership status is not changed to LEFT/REMOVED through this form; use
  the dedicated leave/remove actions.
- Describe roles as group-management authority, not health access.

#### Leave family

- Available only for the current user's ACTIVE membership.
- Explain that leaving keeps the account, personal profile, allergies, and
  screening history.
- If the user is the final ACTIVE OWNER, explain that another OWNER must be made
  active first.

#### Remove member

- OWNER/ADMIN only.
- Confirmation states that removal changes membership status to REMOVED and does
  not delete personal health information.
- Final-owner restriction must be surfaced from the 409 response.

### 4.8 Family permission UX

Place a permanent explanation above the controls:

> Your family role controls group management. These settings control which health
> information you share through this family. An OWNER or ADMIN does not receive
> health access automatically.

Only the authenticated user may read or update permissions for their own ACTIVE
membership. Render one permission page per family.

| Permission | View control | Edit control | Current effect |
| --- | --- | --- | --- |
| Basic profile | Yes | Yes | View or update first name, last name, date of birth |
| Allergies | Yes | Yes | View or create/update/delete allergy records |
| Screening history | Yes | Yes | View history; edit permits medication checks that create history |

The backend also stores CURRENT_MEDICATIONS, MEDICAL_DOCUMENTS, and
EMERGENCY_INFORMATION. Show these only in a disabled “Not available yet” section,
or omit them. Do not imply that enabling them exposes a working feature.

Control pattern:

- Each row has two labeled switches or checkboxes: “Allow viewing” and “Allow
  changes.”
- Do not assume edit implies view; send both explicit booleans.
- Save changes with one deliberate “Save sharing settings” action.
- After success, announce “Sharing settings updated for [family name].”
- Warn that settings apply only to this family.

### 4.9 Account and Security

#### Account Settings

- Display name, email, verification status, account status, and user ID from
  `/auth/me` or the self account endpoint.
- There is no account-update endpoint. Display name and email are read-only.
- Link to Health Profile for editable patient information.
- Do not show account deletion.

#### Sessions & Security

- Change password card.
- Active sessions card.
- Logout action.
- Privacy note explaining that sessions may include IP address and user-agent
  information.

## 5. Wireframe descriptions

### 5.1 Application shell

Desktop: sidebar on the left; top content bar with page title, optional profile
selector, and contextual action; centered content column up to 1200 px. Mobile:
single top bar, full-width content cards, sticky bottom navigation.

### 5.2 Dashboard wireframe

Top row contains greeting and primary “Check medication” button. Second row uses
two equal cards for Personal Summary and Known Allergies. Third row uses a wide
Recent Checks card and a narrower Families card. On mobile all cards stack in
that order, with quick actions directly under the greeting.

### 5.3 Medication Check wireframe

Step 1 card: profile selector and medication input. Step 2 card: normalized
medication and active ingredients. Step 3 full-width result panel with icon,
explicit result heading, details, disclaimer, and professional-review copy. On
mobile, keep all three in one vertical flow; never place result and disclaimer in
side-by-side columns.

### 5.4 Allergies wireframe

Header with profile selector and Add Allergy. Desktop table below; mobile card
list. Add/Edit uses a focused dialog on desktop and a full-screen form on mobile.
Delete uses a compact confirmation dialog.

### 5.5 Family detail wireframe

Header card contains group name, current role, and status. Tab/section order:
Members, My Sharing, About Membership. Management actions appear in a contextual
menu only for OWNER/ADMIN. Mobile uses stacked sections rather than horizontal
tabs when tab labels would wrap.

### 5.6 Sessions wireframe

Page header and revoke-all secondary destructive action. Each session card shows
device icon, friendly name, Current badge, last activity, and expandable technical
details. Revoke is aligned consistently at the end of each row/card.

## 6. Required user flows

### 6.1 Register and verify email

1. User opens Register.
2. User completes account and profile fields.
3. Frontend validates required fields and password rules.
4. Submit `POST /auth/register`.
5. Show verification-required confirmation.
6. User follows verification link containing a token.
7. Submit `POST /auth/verify-email` with the token.
8. On success, navigate to Login.

### 6.2 Log in

1. User enters email and password.
2. Frontend adds friendly device metadata.
3. Submit `POST /auth/login`.
4. Store/use the returned token pair according to the future frontend security
   decision.
5. Load `GET /auth/me` and navigate to Dashboard.
6. Rotate refresh token through `POST /auth/refresh` when necessary.

### 6.3 Create personal profile

Personal profile creation is not a separate authenticated onboarding step. It is
part of `POST /auth/register`. After verification/login, the user reviews the
created profile through `GET /patients/{patient_id}` and may edit it with PUT.
Do not call development-only `POST /patients` from the production frontend.

### 6.4 Add an allergy

1. Open Allergies for the personal or permitted profile.
2. Load current list.
3. Select Add Allergy if edit access is available.
4. Complete substance, optional RxCUI/reaction, and severity.
5. Submit POST.
6. Insert returned record and announce success.
7. On duplicate 409, keep form data and focus the substance error.

### 6.5 Search for a medication

1. Enter medication name.
2. Submit `GET /medications/search?name=...`.
3. Show normalized name, RxCUI, ingredients, and RxNorm disclaimer.
4. Handle not found, incomplete response, unavailable service, and timeout.

### 6.6 Run an allergy screening

1. Select an accessible profile.
2. Enter medication name.
3. Submit medication-check POST once.
4. Render returned ingredients and one of the three exact result states.
5. Show matches when present and always show the educational disclaimer.
6. The returned `history_id` confirms the result was stored.

For another family member, backend access requires the target membership to grant
`ALLERGIES.can_view` and `SCREENING_HISTORY.can_edit` in one shared ACTIVE family.

### 6.7 Review screening history

1. Select an accessible profile.
2. Load screening history.
3. Filter loaded rows client-side.
4. Select a row for a limited detail view using only returned history fields.

### 6.8 Create a family group

1. Open Families and select Create.
2. Enter group name.
3. Submit group POST.
4. Navigate to detail; show ACTIVE OWNER badge for the creator.

### 6.9 Add an existing user

1. OWNER/ADMIN opens Add member.
2. Enter existing numeric user ID, role, and relationship.
3. Submit membership POST.
4. Show PENDING status.
5. If appropriate, manager later updates status to ACTIVE.

No search, invitation, email delivery, or self-acceptance step exists yet.

### 6.10 Update family role

1. OWNER/ADMIN opens an open member record.
2. Select OWNER, ADMIN, or MEMBER.
3. Submit membership PUT.
4. Refresh member row.
5. If final-owner protection triggers, explain the required ownership transfer.

### 6.11 Update family permissions

1. ACTIVE user opens My Sharing inside one family.
2. Load their own membership permissions.
3. Adjust explicit view/edit values for implemented data types.
4. Submit permission PUT.
5. Refresh and announce success.

### 6.12 Leave a family group

1. ACTIVE user selects Leave family.
2. Confirm personal data remains intact.
3. Submit leave POST using their own user ID in the path.
4. Show LEFT status and remove normal family actions.
5. Handle final-owner conflict without changing local state.

### 6.13 Revoke a device session

1. Open Active Sessions.
2. Select Revoke on a session.
3. Confirm when needed.
4. Submit session DELETE.
5. Remove the row. If current session was revoked, clear credentials and go to
   Login.

### 6.14 Reset password

1. Submit email through Forgot Password.
2. Always show generic confirmation.
3. User follows reset link.
4. Submit token and new password pair.
5. On success, all sessions are revoked; navigate to Login.

## 7. UI state standards

| State | Required behavior |
| --- | --- |
| Loading | Use skeletons for stable layouts and a text status for screen readers |
| Empty | Explain what is absent without making a medical conclusion; offer an authorized next action |
| Success | Confirm near the action; do not rely only on a disappearing toast |
| Validation | Show field errors plus a top error summary; focus the summary after submit |
| Authentication required | Attempt refresh once when appropriate; otherwise clear tokens and route to Login with a return path |
| Permission denied | Explain the missing access without exposing private details or implying OWNER override |
| Not found | Use a neutral “Record not available” page; do not confirm an unrelated patient's existence |
| External API unavailable | Preserve medication input, offer Retry, and make no medical conclusion |
| Unexpected error | Show a request-safe reference if available, Retry, and contact/help guidance |
| Offline/connection | Use “Connection unavailable”; preserve unsent non-sensitive form values in memory only |

Screen-specific rules:

- A 401 invalid/expired access token is an authentication state, not a permission
  alert.
- A 403 family permission error stays on the page and replaces sensitive content
  with the denied state.
- A privacy-protecting 404 for another patient's record must not be rewritten as
  “Patient exists but is private.”
- A screening HTTP 200 with `UNABLE_TO_VERIFY` is a completed conservative result,
  not a transport error.

## 8. Component inventory

- Application shell, desktop sidebar, tablet rail, mobile bottom navigation.
- Page header, breadcrumb, profile selector, family selector.
- Buttons: primary, secondary, tertiary, destructive, icon-only.
- Text, email, password, date, numeric ID, and medication-search inputs.
- Select, radio group, checkbox/switch, textarea-like reaction input.
- Form field, hint, inline error, and error summary.
- Patient summary card, allergy card/row, family card, membership row, session
  card, history row.
- Role, relationship, membership-status, severity, result, and Current Session
  badges.
- Medical result panel, informational alert, warning alert, error alert.
- Data table with mobile card transformation.
- Empty state, skeleton, spinner, retry block, permission-denied block.
- Confirmation modal, full-screen mobile form, disclosure panel.
- Toast/live-region announcement that supplements persistent feedback.

## 9. Design system and tokens

### 9.1 Color palette — light mode

| Token | Value | Use |
| --- | --- | --- |
| `color.brand.700` | `#0B5D59` | Primary actions and active navigation |
| `color.brand.600` | `#0B6E69` | Links and interactive accents on light surfaces |
| `color.brand.050` | `#EAF7F5` | Selected and informational surfaces |
| `color.ink.900` | `#17212B` | Primary text |
| `color.ink.700` | `#344454` | Secondary text |
| `color.ink.500` | `#607080` | Metadata |
| `color.surface` | `#FFFFFF` | Main surface |
| `color.canvas` | `#F6F8FA` | Page background |
| `color.border` | `#CBD5DF` | Borders and dividers |
| `color.info.700` | `#175CD3` | Neutral informational status |
| `color.warning.800` | `#854A0E` | Unable-to-verify text/icon |
| `color.warning.100` | `#FEF0C7` | Warning surface |
| `color.danger.700` | `#B42318` | Potential-match and destructive emphasis |
| `color.danger.050` | `#FEF3F2` | Potential-match surface |
| `color.success.700` | `#067647` | Administrative success only, never medication safety |

Verify all final text/background combinations against WCAG AA. Do not place white
text on a token until its contrast has been measured in the implemented design.

### 9.2 Typography

- Font family: Inter when bundled, otherwise system UI (`Segoe UI`, Roboto,
  Helvetica, Arial, sans-serif).
- Base size: 16 px; body line height: 1.5.
- Page title: 32/40, weight 700 desktop; 28/36 mobile.
- Section title: 24/32, weight 650–700.
- Card title: 18/26, weight 650.
- Body: 16/24, weight 400.
- Supporting text: 14/20; never smaller than 14 px for health information.
- Labels: 14/20, weight 600.

### 9.3 Spacing and sizing

Use a 4 px base scale: `4, 8, 12, 16, 24, 32, 40, 48, 64`.

- Card padding: 24 px desktop, 16 px mobile.
- Form field gap: 16 px.
- Section gap: 32–48 px.
- Minimum pointer target: 44 × 44 px.
- Content maximum width: 1200 px; focused forms: 640 px.
- Border radius: 8 px controls, 12 px cards, 16 px prominent result panels.

### 9.4 Interaction tokens

- Focus ring: 3 px `#175CD3` with 2 px surface offset.
- Disabled controls retain readable text and include a programmatic disabled
  state; they are not merely faded.
- Hover changes background/border in addition to cursor.
- Motion duration: 120–200 ms; respect `prefers-reduced-motion`.
- Avoid medical-result animations and celebratory success effects.

### 9.5 Badge semantics

- Role badges use neutral/brand styling.
- Membership status always includes text.
- Severity uses label + icon/pattern: Mild, Moderate, Severe.
- `NO_RECORDED_MATCH_FOUND` uses informational styling, not a green success badge.
- `POTENTIAL_ALLERGY_MATCH` uses warning icon + explicit text.
- `UNABLE_TO_VERIFY` uses question/warning icon + explicit text.

### 9.6 Component and icon standards

| Component | Standard |
| --- | --- |
| Primary button | One primary action per form region; brand fill, clear verb label, loading label that preserves width |
| Secondary button | Bordered or neutral fill for safe alternate actions |
| Destructive button | Danger styling and explicit object/action label; confirmation for irreversible or session-ending scope |
| Inputs | Label above control, hint below label, error below control, 44 px minimum height |
| Password input | Show/hide control with an accessible name; requirements visible before submit |
| Cards | Use a heading and semantic region when independently meaningful; avoid nested cards deeper than one level |
| Tables | Real table semantics on desktop; caption or accessible name; mobile card version preserves every field label |
| Alerts | Icon, heading, message, and optional action; warning/error is not communicated by color alone |
| Modal dialogs | Labeled dialog, initial focus, focus containment, Escape close when safe, focus returned to trigger |
| Navigation | Current destination exposed with `aria-current`; labels remain available to assistive technology in collapsed modes |

Use one consistent outline icon family such as Lucide, with 20 px icons in
controls and 24 px icons in status panels. Decorative icons are hidden from
assistive technology; meaningful stand-alone icons receive an accessible name.
Pair medical and status icons with text. Do not use a checkmark to represent
`NO_RECORDED_MATCH_FOUND`, because it could be interpreted as a safety approval.

## 10. API-to-screen mapping

| API | Auth | Screen/use |
| --- | --- | --- |
| `GET /` | Public | Operational health only; not a user-facing feature |
| `POST /auth/register` | Public | Register and create personal profile |
| `POST /auth/verify-email` | Public | Verify Email |
| `POST /auth/login` | Public | Login |
| `POST /auth/refresh` | Refresh token | Frontend session renewal |
| `POST /auth/logout` | Bearer | Logout |
| `POST /auth/forgot-password` | Public | Forgot Password |
| `POST /auth/reset-password` | Public token | Reset Password |
| `POST /auth/change-password` | Bearer | Change Password |
| `GET /auth/me` | Bearer | App bootstrap and Account Settings |
| `GET /auth/sessions` | Bearer | Active Sessions |
| `DELETE /auth/sessions/{session_id}` | Bearer/self | Revoke one session |
| `DELETE /auth/sessions` | Bearer/self | Revoke all sessions |
| `GET /patients` | Bearer | Discover own and BASIC_PROFILE-viewable profiles |
| `GET /patients/{patient_id}` | Bearer + ownership/permission | Profile view |
| `PUT /patients/{patient_id}` | Bearer + ownership/`BASIC_PROFILE.can_edit` | Profile edit |
| `DELETE /patients/{patient_id}` | Bearer + authorization | Do not expose for linked personal profiles |
| `POST /patients` | Bearer + development mode | Development tooling only; never production UI |
| `GET /patients/{patient_id}/allergies` | Bearer + ownership/`ALLERGIES.can_view` | Allergy list |
| `POST /patients/{patient_id}/allergies` | Bearer + ownership/`ALLERGIES.can_edit` | Add allergy |
| `GET /patients/{patient_id}/allergies/{allergy_id}` | Bearer + view | Allergy detail |
| `PUT /patients/{patient_id}/allergies/{allergy_id}` | Bearer + edit | Edit allergy |
| `DELETE /patients/{patient_id}/allergies/{allergy_id}` | Bearer + edit | Delete allergy |
| `GET /medications/search` | Public | Standardized medication reference search |
| `POST /patients/{patient_id}/medication-check` | Bearer + screening rule | Medication Check |
| `GET /patients/{patient_id}/screening-history` | Bearer + ownership/`SCREENING_HISTORY.can_view` | History |
| `GET /users/{user_id}` | Bearer/self | Account summary; self only |
| `GET /users/{user_id}/profile` | Bearer + profile authorization | Alternate profile view path |
| `GET /users/{user_id}/family-groups` | Bearer/self | Family list/history |
| `POST /users` | Bearer + development mode | Development tooling only; never production UI |
| `POST /family-groups` | Bearer | Create family |
| `GET /family-groups/{group_id}` | Bearer + ACTIVE membership | Family detail |
| `PUT /family-groups/{group_id}` | Bearer + OWNER/ADMIN | Rename/update group |
| `POST /family-groups/{group_id}/members` | Bearer + OWNER/ADMIN | Add existing user as PENDING |
| `GET /family-groups/{group_id}/members` | Bearer + ACTIVE membership | Member list/history |
| `GET /family-groups/{group_id}/members/{user_id}` | Bearer + ACTIVE membership | Member detail |
| `PUT /family-groups/{group_id}/members/{user_id}` | Bearer + OWNER/ADMIN | Role/relationship/status update |
| `POST /family-groups/{group_id}/members/{user_id}/leave` | Bearer/self | Leave family |
| `DELETE /family-groups/{group_id}/members/{user_id}` | Bearer + OWNER/ADMIN | Remove member |
| `GET /family-groups/{group_id}/members/{user_id}/permissions` | Bearer + same ACTIVE user | My Sharing |
| `PUT /family-groups/{group_id}/members/{user_id}/permissions` | Bearer + same ACTIVE user | Save sharing settings |

## 11. Error and status mapping

Service errors use `detail.code` and `detail.message`. Plain FastAPI errors from
some medication/allergy routes may use a string `detail`; the frontend API layer
must normalize both shapes.

| HTTP/code | UI response |
| --- | --- |
| `401 AUTHENTICATION_REQUIRED` | Route to Login; preserve safe return path |
| `401 INVALID_ACCESS_TOKEN` | Try one refresh; otherwise sign out |
| `401 ACCESS_TOKEN_EXPIRED` | Try one refresh; otherwise sign out |
| `401 INVALID_CREDENTIALS` | Inline login/current-password error |
| `403 EMAIL_NOT_VERIFIED` | Verification-required panel |
| `423 ACCOUNT_LOCKED` | Locked-account alert with retry-later wording |
| `429 RATE_LIMIT_EXCEEDED` | Disable repeated submit for Retry-After duration |
| `409 EMAIL_ALREADY_REGISTERED` | Email field error; link to Login |
| `422 PASSWORD_TOO_WEAK` | Password requirements + field error |
| `422 PASSWORD_MISMATCH` | Confirmation field error |
| `400 INVALID_VERIFICATION_TOKEN` | Invalid verification-link page |
| `400 VERIFICATION_TOKEN_EXPIRED` | Expired verification-link page |
| `400 INVALID_RESET_TOKEN` | Invalid reset-link page |
| `400 RESET_TOKEN_EXPIRED` | Expired reset-link page |
| `404 PATIENT_NOT_FOUND` | Record not available |
| `404 PATIENT_ACCESS_DENIED` | Record not available; do not disclose existence |
| `403 FAMILY_PERMISSION_DENIED` | Permission-denied state for requested health feature |
| `404 USER_ACCESS_DENIED` | Account not available |
| `403 FAMILY_ACCESS_DENIED` | Active-membership-required state |
| `403/409 MEMBERSHIP_NOT_ACTIVE` | Membership inactive or no longer open for the requested action |
| `403 INSUFFICIENT_ROLE` | Management action not permitted |
| `403 PERMISSION_ACCESS_DENIED` | Only own sharing settings can be managed |
| `404 FAMILY_GROUP_NOT_FOUND` | Family not found |
| `404 FAMILY_MEMBERSHIP_NOT_FOUND` | Member not found |
| `409 DUPLICATE_ACTIVE_MEMBERSHIP` | User already pending/active in family |
| `409 LAST_OWNER_CANNOT_LEAVE` | Require another active OWNER first |
| `409 PERSONAL_PROFILE_DELETE_FORBIDDEN` | Explain personal profile cannot be deleted here |
| `422 INVALID_FAMILY_ROLE` | Role field error |
| `422 INVALID_FAMILY_RELATIONSHIP` | Relationship field error |
| `422 INVALID_MEMBERSHIP_STATUS` | Status field error |
| `422 INVALID_PERMISSION_TYPE` | Refresh permission configuration; do not save unknown type |
| Medication search `404` | No standardized RxNorm medication found |
| Medication search `502` | Medication information unavailable/incomplete |
| Medication search `504` | Medication service timeout |
| Allergy duplicate `409` | Substance already recorded for this profile |
| Generic `422` | Field mapping plus top error summary |
| Generic `5xx` | Unexpected error panel with Retry |

## 12. Responsive behavior

### Desktop (1024 px and above)

- Persistent sidebar and multi-column dashboard.
- Tables for allergies, history, members, and sessions where appropriate.
- Dialogs max 560–640 px for add/edit actions.
- Medication result uses full content width but keeps text lines readable.

### Tablet (768–1023 px)

- Collapsible rail.
- Dashboard changes to one or two columns based on available width.
- Tables hide low-priority technical columns behind row expansion.
- Profile selector remains visible above health content.

### Mobile (below 768 px)

- Bottom navigation and single-column pages.
- Convert tables to cards; do not require horizontal scrolling for primary data.
- Add/edit forms use full-screen sheets/pages.
- Sticky bottom action may be used for Save or Check, but must not cover error or
  disclaimer content.
- Profile selector uses a labeled full-width select or bottom sheet with “My
  profile” and “Shared profile” grouping.
- Medication ingredients and matches stack vertically; identifiers may be placed
  in expandable technical details.
- Modal confirmations remain keyboard and screen-reader accessible and fit a
  320 px viewport.

## 13. Accessibility requirements

- Target WCAG 2.2 AA.
- Every control has a persistent visible label; placeholders are examples only.
- Full keyboard access with logical focus order and no keyboard traps.
- Focus moves to page heading after navigation, error summary after failed submit,
  and dialog heading when opened.
- Visible 3 px focus indicator with sufficient contrast.
- Use semantic headings, lists, tables, buttons, dialogs, and form elements.
- Associate help and error text with fields using programmatic descriptions.
- Provide an error summary linking to invalid fields.
- Announce async search/screening status and mutation success through appropriate
  live regions without repeatedly interrupting screen readers.
- Medical result panels use heading, icon with text alternative, explicit result
  text, and supporting description—not color alone.
- Severity and membership statuses always include words.
- Minimum 44 × 44 px touch targets and adequate spacing between destructive and
  non-destructive actions.
- Dates use localized display plus an unambiguous accessible value. Preserve API
  UTC timestamps and convert for display.
- Password visibility controls have accessible names and do not alter tab order.
- Respect zoom to 200%, text reflow, reduced motion, high contrast, and browser
  font scaling.
- Keep disclaimers in normal document flow; never hide them in tooltips.

## 14. Current limitations affecting frontend design

1. **Family member discovery:** add-member accepts only a numeric `user_id`.
   There is no name/email search or invitation flow.
2. **Member display:** membership responses contain IDs, roles, relationships,
   statuses, and timestamps, but no safe member display name.
3. **Shared-profile discovery:** `GET /patients` discovers the user's profile and
   profiles shared through `BASIC_PROFILE.can_view`. A target could share
   ALLERGIES or SCREENING_HISTORY without BASIC_PROFILE, leaving no reliable
   friendly profile-selection path in the current API.
4. **Capability metadata:** patient responses do not say whether the requester has
   view/edit rights. The UI must infer from context or handle 403 on mutation.
5. **History detail:** stored history does not include ingredient or match detail;
   no detail endpoint exists.
6. **History scale:** no pagination, filtering, or date query parameters.
7. **Account editing:** email and display name are read-only because no update
   endpoint exists.
8. **Profile deletion:** linked personal profiles cannot be deleted through the
   current API.
9. **Email delivery:** production verification/reset delivery is not implemented;
   development URLs must not define production UX.
10. **Browser token storage:** the API returns access and refresh tokens in JSON,
    not secure HttpOnly cookies. The frontend security architecture must decide
    storage and refresh behavior before implementation; avoid casual localStorage
    use for sensitive sessions.
11. **Permission types:** three future data types are stored but have no health
    feature endpoints.
12. **Group inactive semantics:** `is_active` exists, but the current family
    authorization flow is based primarily on membership status. Do not expose a
    deactivation workflow until behavior is explicitly defined and tested.
13. **No verified relationships:** family relationship labels are user-provided
    and do not prove guardianship or consent.
14. **Educational status:** the system is not production medical software and
    must use fictional information only.

## 15. Future UI features out of scope

- Dark mode after light-mode accessibility is validated.
- Email/QR invitations, invitation expiration/revocation, and invitation inbox.
- User search with privacy-preserving results.
- Phone authentication, passkeys, biometrics, OAuth, and MFA.
- Medical documents, doctor portal, notifications, FHIR, AI assistant, analytics,
  enterprise administration, and native mobile applications.
- Medication interactions, prescribing, dosing advice, adherence, or safety
  recommendations.
- Current medication, emergency information, and document permission screens.
- Legal consent, guardianship verification, audit-log UI, and compliance claims.

## Frontend Implementation Baseline

The future frontend must build an accessible, responsive authenticated application
with public authentication screens; a dashboard; personal profile and allergy
management; RxNorm medication reference search; conservative medication allergy
screening; screening history; family group, membership, role, relationship,
status, leave/remove, and self-controlled permission experiences; account summary;
password change; active-session management; and logout.

It must use the current `/auth`, `/patients`, nested `/allergies`,
`/medications/search`, `/medication-check`, `/screening-history`, `/users`, and
`/family-groups` APIs exactly as mapped above. It must derive application identity
from `/auth/me` and the Bearer token—not client-supplied requester IDs—and must
respect ownership, ACTIVE membership, group role, and target-member family data
permissions.

The first frontend must not call development-only `POST /users` or
`POST /patients`, must not present unsupported family invitations or account
editing, and must not claim that a medication is safe, approved, recommended,
suitable, or free of allergy risk. The backend limitations in Section 14 are
explicit integration constraints, not details for the frontend to guess around.
