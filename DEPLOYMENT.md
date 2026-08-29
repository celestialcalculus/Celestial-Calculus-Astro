# Celestial Calculus — Cross-device deployment

## Architecture

- **GitHub Pages:** static responsive/PWA frontend.
- **Supabase:** authentication + encrypted-in-transit PostgreSQL sync store with Row Level Security.
- **Calculation API:** the Python service containing Swiss Ephemeris. Deploy it privately to a Docker-capable host such as Render, Railway, Fly.io, or a private VPS. GitHub does not execute Python API code for GitHub Pages.
- **Offline:** localStorage keeps a device cache; when the network is unavailable the UI remains usable for locally cached profiles. Cloud synchronization resumes after login/network recovery.

## 1. Create Supabase project

Create a project, then run `supabase_schema.sql` in the SQL Editor.
Enable Email authentication (or another provider if desired).

## 2. Deploy calculation API

Build and run the Docker image:

```bash
docker build -t celestial-calculus-api .
docker run -p 8765:8765 -e CC_CORS_ORIGIN=https://YOUR-USER.github.io celestial-calculus-api
```

Use the resulting HTTPS API URL as `API_BASE_URL`. For production, do not expose the development HTTP service directly to the public internet without TLS/authentication. The next hardening step is to put the API behind HTTPS and add authenticated API access.

## 3. GitHub Pages

Push this repository to GitHub. In repository Settings → Secrets and variables → Actions, add:

- `CC_API_BASE_URL` — HTTPS URL of the calculation API
- `CC_SUPABASE_URL` — Supabase project URL
- `CC_SUPABASE_ANON_KEY` — Supabase publishable/anon key

The workflow `.github/workflows/pages.yml` generates `web/config.js` and publishes `web/`.

## 4. Android

Open the GitHub Pages URL in Chrome → menu → **Add to Home screen / Install app**. It behaves as a PWA. The same Supabase account is used for synchronization.

## 5. Windows

Open the same URL in Edge/Chrome. Use the browser's **Install this site as an app** option for an app-like desktop window.

## Privacy

Birth data is synchronized only when cloud sync is enabled and the user signs in. RLS restricts database rows to the authenticated owner. The calculation API receives birth details when a chart is calculated. If strict privacy is required, deploy the calculation API privately and restrict access with an authenticated gateway/VPN.
