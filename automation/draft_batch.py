#!/usr/bin/env python3
"""Conservative, review-only article batch generator. Python standard library only."""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "drafts" / "generated"
USER_AGENT = "JinijiguEditorialResearch/1.0 (review-only)"
QUERIES = ['"나는 SOLO" 방송', '"나솔사계" 방송', '"나는 솔로" 출연자']
MAX_ITEMS = 20

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml,text/html,application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(800_000).decode("utf-8", errors="replace")

def collect(limit=90):
    found = {}
    for q in QUERIES:
        rss = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q + " when:7d", "hl": "ko", "gl": "KR", "ceid": "KR:ko"})
        try:
            root = ET.fromstring(fetch(rss))
        except Exception as e:
            print("RSS unavailable:", str(e), file=sys.stderr)
            continue
        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            url = (item.findtext("link") or "").strip()
            published = (item.findtext("pubDate") or "").strip()
            if title and url and url.startswith("https://"):
                key = re.sub(r"\W+", "", title.split(" - ")[0]).lower()
                found.setdefault(key, {"headline": title, "url": url, "published": published})
            if len(found) >= limit:
                break
    return list(found.values())[:limit]

def call_model(api_key, model, payload):
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": "당신은 한국 방송 콘텐츠 검증 편집자다. 주어진 기사 제목만으로 방송 내용, 대사, 사실을 지어내지 않는다. 확인되지 않은 사실은 제외한다. JSON 객체만 반환한다."},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
    ], "response_format": {"type": "json_object"}}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body, method="POST",
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as response:
        data = json.load(response)
    return json.loads(data["choices"][0]["message"]["content"])

def normalized_title(s):
    return re.sub(r"[^가-힣a-z0-9]+", "", s.lower())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max-drafts", type=int, default=20)
    p.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    p.add_argument("--dry-run", action="store_true", help="Discover candidates only; do not call AI or save drafts")
    args = p.parse_args()
    max_drafts = max(1, min(args.max_drafts, MAX_ITEMS))
    candidates = collect()
    print("Discovered candidates:", len(candidates))
    if args.dry_run:
        print(json.dumps(candidates[:max_drafts], ensure_ascii=False, indent=2))
        return
    if os.getenv("REPO_PRIVATE") != "true":
        sys.exit("Refusing to generate drafts: repository privacy not verified.")
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        sys.exit("OPENAI_API_KEY secret is required.")
    OUT.mkdir(parents=True, exist_ok=True)
    index_file = OUT / "index.json"
    try:
        old = json.loads(index_file.read_text(encoding="utf-8")) if index_file.exists() else []
    except (ValueError, OSError):
        old = []
    used = {normalized_title(x.get("headline", "")) for x in old}
    batch = []
    for c in candidates:
        if len(batch) >= max_drafts:
            break
        key_title = normalized_title(c["headline"])
        if key_title in used:
            continue
        # RSS headlines are leads, NOT verified article evidence. Never present them as validated.
        # The model receives a URL for attribution but cannot independently open it here.
        # Require verified full-text evidence before publication-ready generation.
        try:
            page = fetch(c["url"])
            text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", page, flags=re.I | re.S)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 1000 or len(text) > 500000:
                continue
            evidence = text[:11000]
            result = call_model(key, args.model, {
                "instruction": "아래 제공된 기사 텍스트에 명시된 사실만 사용. 7~8문단의 독창적 네이버 블로그 초안 작성. 근거 부족하거나 방송 결과를 검증할 수 없으면 publishable=false. 기사 전체를 재현하거나 긴 인용 금지. 출력 JSON 키: title, body, facts(문자열 배열), angle, publishable(불리언), reason. 사실과 해석을 구분. 각 주장에 대한 근거를 제공된 본문에서만 찾을 것.",
                "headline": c["headline"], "source_url": c["url"], "published": c["published"], "article_text": evidence
            })
        except Exception as e:
            print("Skipped source:", c["url"], type(e).__name__, file=sys.stderr)
            continue
        if not isinstance(result, dict) or not result.get("publishable") or not isinstance(result.get("facts"), list):
            continue
        title, body = result.get("title"), result.get("body")
        if not isinstance(title, str) or not isinstance(body, str) or len(body) < 650:
            continue
        if normalized_title(title) in used:
            continue
        doc = {"title": title, "body": body, "facts": result["facts"], "angle": result.get("angle", ""),
               "sources": [c["url"]], "source_headline": c["headline"], "source_published": c["published"],
               "review_status": "needs_human_fact_check", "image_status": "not_created",
               "created_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        digest = hashlib.sha256((title + c["url"]).encode()).hexdigest()[:12]
        (OUT / (digest + ".json")).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        batch.append({"id": digest, "headline": c["headline"], "title": title, "source": c["url"]})
        used.add(key_title)
        used.add(normalized_title(title))
        print("Draft generated:", digest)
        time.sleep(0.2)
    index_file.write_text(json.dumps(old + batch, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved drafts:", len(batch), "of requested", max_drafts)
    if not batch:
        print("No sufficiently supported drafts; no content fabricated.")

if __name__ == "__main__":
    main()
