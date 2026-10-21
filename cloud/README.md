# Free mobile review dashboard (separate from local Python backend)

This is a **static cloud review MVP**, not the existing local FastAPI dashboard. It edits and stores text drafts on mobile; it does **not** generate images/video, connect social accounts, or publish.

## Architecture / free limits
- Cloudflare Pages: free static HTTPS hosting, no continuously running Python server.
- A **new, dedicated** Supabase Free project: email/password Auth + Postgres with per-user RLS.
- Supabase Free may pause after 7 days of inactivity; storage/egress quotas apply. Free does not guarantee uninterrupted production uptime.
- Existing local video rendering remains on the PC until a separate job runner is configured.

## Setup
1. Create a new Supabase project (do **not** reuse an unrelated existing project).
2. In Supabase SQL Editor, run `cloud/schema.sql`.
3. In Authentication, disable public signups after creating your single admin account (or invite the admin). Use a strong password and enable MFA where available.
4. Deploy `cloud/` as static assets to Cloudflare Pages (Direct Upload). Use `cloud` as the uploaded directory; there is no build command.
5. Visit the Pages HTTPS URL, enter the dedicated Supabase project URL and **publishable/anon** key. Never enter service_role, secret keys, or social platform tokens.
6. Sign in with your admin email/password. Create, edit, and review drafts. Verify data stays after refreshing or opening on another device.

Security: Only publishable/anon key is saved to browser localStorage; access tokens stay in page memory, and are discarded on refresh. This deliberately requires re-login after refresh. RLS restricts rows to the signed-in user. Never put content or credentials in a public GitHub repository. This UI does not contain any privileged admin actions.

## Scope boundary
The existing FastAPI / FFmpeg generator is not deployed here. Cloudflare Pages cannot execute that local Python stack as-is. The next milestone is an authenticated cloud job service / platform OAuth connectors, with explicit manual approval before any publication.
