# 나는 SOLO/나솔사계 자동 원고 배치 (1차 구현)

## What works
- GitHub Actions manual dispatch; collects last 7 days' Korean Google News RSS candidates.
- Full-text HTTP retrieval when possible; skips inaccessible/insufficient sources.
- OpenAI API generates **up to** 20 original Korean draft articles from retrieved text, not invented to reach quota.
- Output JSON with headline, source, verified-claim candidates, human review flag.
- Stores results as a **7-day GitHub Actions artifact**. Never publishes to Naver or social media.
- Dry-run default is true, and calls no AI API.
- Repository **must be private** for non-dry runs; this is enforced at runtime.
- Drafts remain **unverified** until a human compares each claim to the actual source; retrieval and AI evaluation do not constitute independent fact-checking.
- Images are not generated or downloaded. Image rights and original broadcast content must be checked separately.
- Google News RSS redirects, paywalls, anti-bot pages and noisy HTML can cause skips or unreliable extracted text. Do not treat the batch as production-ready.
- Existing draft index can be used for duplicate detection only if persisted in the run workspace; artifacts are not automatically restored across runs. Cross-run deduplication is **not yet implemented**.

## Before running
1. Change GitHub repository `jagama90/blog-writer` visibility to **private**. It is currently public.
2. Configure repository Actions secret `OPENAI_API_KEY` (never commit the key).
3. GitHub Actions workflows generally need to exist on the repository default branch to appear in the Actions manual-dispatch UI. Merge the feature branch after reviewing.
4. Run **Editorial draft batch (review only)** via Actions → Run workflow, set dry_run=true first.
5. When ready set dry_run=false, max_drafts 1 to test costs, then scale up to 20.
6. Download the `editorial-review-drafts` artifact and verify each article before any publication.

## Limits
- No unattended schedule until API cost, privacy and quality controls are verified.
- This workflow uses OpenAI API billing, which is separate from ChatGPT subscription.
- Public repository + draft artifact publishing is explicitly blocked.
- No direct cloud studio import or mobile draft browser yet.
