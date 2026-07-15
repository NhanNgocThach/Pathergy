# Pathergy portfolio deployment

This guide prepares the educational Pathergy prototype for this architecture:

```text
GitHub main branch
  |-- frontend/ -> Vercel (Next.js)
  |-- repository root -> Render (FastAPI)
  `-- Render -> Neon (PostgreSQL)
```

This is a portfolio and development deployment. It is not production-ready,
HIPAA-compliant, or approved for real patient information. Use fictional data
only.

## What GitHub does

GitHub remains the source of truth. `.github/workflows/ci.yml` runs the backend
tests and all frontend checks for pushes and pull requests to `main`. Vercel and
Render connect to the same repository and deploy automatically. GitHub stores
code and runs CI; Vercel and Render run the applications.

Never commit `.env`, `.env.local`, a Neon connection string, JWT secrets, token
hash secrets, or SQLite database files. The repository `.gitignore` excludes
those local files.

## 1. Create the Neon PostgreSQL database

1. Create a Neon project and database.
2. In Neon's **Connect** dialog, enable **Connection pooling**.
3. Copy the pooled connection string. Its hostname contains `-pooler` and the
   URL normally begins with `postgresql://`.
4. Save that complete value as Render's `DATABASE_URL`. Do not put it in a
   repository file.

Pathergy converts a standard `postgresql://` URL to SQLAlchemy's Psycopg 3
dialect. The engine uses a small pool, connection pre-ping, and connection
recycling. Local tests continue to use SQLite.

Run migrations from a trusted environment with the same `DATABASE_URL`:

```powershell
$env:DATABASE_URL="postgresql://..."
python -m alembic upgrade head
```

`render.yaml` also runs `python -m alembic upgrade head` before Uvicorn starts.
Render's dedicated pre-deploy command is preferable if the service is later
upgraded to a plan that supports it; for the free service the idempotent Alembic
upgrade is part of the start command.

## 2. Deploy FastAPI to Render

1. In Render, create a new **Blueprint** and connect the Pathergy GitHub
   repository.
2. Render reads `render.yaml` from the repository root. The backend root
   directory is the repository root, not `frontend/`.
3. Confirm the branch is `main` and the service name is `pathergy-api`.
4. Enter the prompted environment variables listed below.
5. Deploy and wait for `/health` to report `{"status":"ok"}`.

Render supplies `PORT`. The service starts without development reload:

```text
python -m alembic upgrade head &&
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Swagger remains available at `/docs` for this portfolio deployment. The API
health probe is `/health`.

### Render environment variables

| Variable | Value/source |
| --- | --- |
| `PYTHON_VERSION` | `3.12.11`; pins a version with prebuilt dependency wheels |
| `DATABASE_URL` | Neon pooled PostgreSQL URL; secret |
| `AUTH_JWT_SECRET` | Render-generated random secret, at least 32 characters |
| `AUTH_TOKEN_HASH_SECRET` | Different Render-generated random secret |
| `CORS_ALLOWED_ORIGINS` | Exact Vercel origin, such as `https://pathergy.vercel.app` |
| `AUTH_DEVELOPMENT_MODE` | `false` for an internet-accessible deployment |
| `AUTH_DEVELOPMENT_BASE_URL` | Exact Vercel origin |
| `AUTH_RATE_LIMIT_PER_MINUTE` | `30` |

Do not add wildcard CORS. The backend rejects `*` and sends no credentialed CORS
headers because the current API does not authenticate with cookies.

## 3. Deploy Next.js to Vercel

1. In Vercel, select **Add New Project** and import the Pathergy GitHub
   repository.
2. Set **Root Directory** to `frontend`.
3. Keep the detected Next.js build settings. No `vercel.json` is required.
4. Add this Production environment variable:

   ```text
   NEXT_PUBLIC_API_BASE_URL=https://your-render-service.onrender.com
   ```

5. Deploy, then copy the final Vercel origin into Render's
   `CORS_ALLOWED_ORIGINS` and `AUTH_DEVELOPMENT_BASE_URL`.
6. Redeploy Render after changing those variables.

`NEXT_PUBLIC_API_BASE_URL` is embedded into browser JavaScript during the Vercel
build. It is intentionally public and must contain only the public API origin,
never a database URL or secret. Changing it requires a new Vercel deployment.

Vercel creates preview deployments for branches and production deployments from
`main`. A preview URL is a different browser origin; add it explicitly to
`CORS_ALLOWED_ORIGINS` only when you intend to test that exact preview.

## Authentication across Vercel and Render

The current backend does not issue cookies. Login returns both tokens as JSON:

- the JWT access token is held only in frontend memory;
- the opaque refresh token is held in the browser tab's `sessionStorage`;
- protected requests send the access token in the `Authorization` header;
- refresh requests send the refresh token in JSON.

Therefore `Secure`, `HttpOnly`, and `SameSite` cookie settings do not apply to
the current implementation, and CORS remains `allow_credentials=false`. HTTPS
is still required. Storing a refresh token in browser storage remains vulnerable
to token theft if an XSS flaw exists; this is a documented limitation, not a
production token design.

`AUTH_DEVELOPMENT_MODE` must remain `false` on a public deployment. Pathergy does
not yet have an email provider, so a newly registered cloud account will not
receive its verification or password-reset link. Do not expose development
links publicly to work around this: the forgot-password response could expose a
reset token. Email delivery is separate future work.

## Free-tier limitations

- A free Render service can sleep after inactivity, so its first request can be
  slow while the service starts.
- Neon can suspend an idle compute and add latency to the first database query.
- Provider limits and free-tier terms can change; check each dashboard before
  relying on them.
- The in-memory authentication rate limiter is per Render process and is not a
  distributed production control.
- There is no production email delivery, audit program, verified consent,
  compliance program, or healthcare privacy certification.

## Automatic deployment after `main`

1. Push a commit to `main`.
2. GitHub Actions runs backend and frontend checks.
3. Render's `commit` trigger rebuilds and deploys the backend from that commit.
4. Vercel builds and deploys the `frontend` project from the same commit.
5. Render runs Alembic before starting the new API process.

The current portfolio setup deploys immediately from `main`; GitHub Actions
reports test failures separately and does not gate the Render deployment. Use a
pull request and wait for its checks before merging when a deployment must be
test-gated.

## Return to local development

Backend PowerShell:

```powershell
cd D:\Workspace\Pathergy
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Frontend PowerShell:

```powershell
cd D:\Workspace\Pathergy\frontend
Copy-Item .env.example .env.local
npm run dev
```

The local `.env.example` keeps SQLite and localhost values. Cloud values belong
only in Neon, Render, and Vercel dashboards.
