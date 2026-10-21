-- Execute ONLY in a new, dedicated Supabase project.
create table if not exists public.editorial_drafts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null check (char_length(title) between 1 and 300),
  body text not null default '',
  status text not null default 'draft' check (status in ('draft','reviewed')),
  updated_at timestamptz not null default now()
);
create index if not exists editorial_drafts_user_updated on public.editorial_drafts(user_id,updated_at desc);
alter table public.editorial_drafts enable row level security;
revoke all on public.editorial_drafts from anon;
grant select,insert,update on public.editorial_drafts to authenticated;
create policy "owner read" on public.editorial_drafts for select to authenticated using ((select auth.uid())=user_id);
create policy "owner insert" on public.editorial_drafts for insert to authenticated with check ((select auth.uid())=user_id);
create policy "owner update" on public.editorial_drafts for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
