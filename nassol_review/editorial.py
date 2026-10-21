"""Local-only NASSOL editorial draft generator. No publishing, paid API, or invented verification."""
from __future__ import annotations
import argparse
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build(data: dict) -> tuple[str, str]:
    person = str(data.get("person", "")).strip()
    sources = data.get("sources", [])
    opinion = data.get("editorial", {})
    if not person or not sources:
        raise ValueError("person and at least one source are required")
    if any(not s.get("url") or not s.get("claim") for s in sources):
        raise ValueError("Each source requires a URL and a factual claim")
    title = str(data.get("title", "")).strip()
    if not title:
        title = f"나는솔로 {person}, {str(sources[0]['claim']).strip()[:38]}"
    for prefix in ("[지니지구 생각]", "[은행원 생각]"):
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
    if not title:
        raise ValueError("final title is empty")
    parts = [f"# {title}", "", "지니지구에요 ㅎㅇㅎㅇ", ""]
    hook = str(opinion.get("hook", "")).strip()
    if hook:
        parts.extend([hook, ""])
    for index, source in enumerate(sources):
        date = source.get("date", "날짜 미확인")
        parts.extend([f"{source['claim']}", "", f"({date} 보도 기준)", ""])
        if index == 0:
            parts.extend(["[관련 사진 1: 사용 권한 확인 후 삽입]", ""])
        if index == len(sources) - 1:
            parts.extend(["[관련 사진 2: 사용 권한 확인 후 삽입]", ""])
    take = str(opinion.get("take", "")).strip()
    ending = str(opinion.get("ending", "")).strip()
    if not take or not ending:
        raise ValueError("editorial.take and editorial.ending are required; never invent a personal opinion")
    parts.extend([take, "", ending, "", f"## {person} 프로필", ""])
    profile = data.get("profile", {})
    for key, value in profile.items():
        if value:
            parts.append(f"- {key}: {value}")
    parts.extend(["", "## 참고 기사", ""])
    for source in sources:
        parts.append(f"- {source.get('date','날짜 미확인')} | {source['url']}")
    parts.extend(["", "> 이 글은 수동 검수용 초안입니다. 기사 본문을 복제하지 않았으며, 입력된 사실·SNS·사진 사용권을 자동 검증하지 않았습니다.", ""])
    return title, "\n".join(parts)

def run(input_path: Path, output_root: Path) -> Path:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    title, body = build(data)
    output_root.mkdir(parents=True, exist_ok=True)
    folder = output_root / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    folder.mkdir()
    (folder / "final_title.txt").write_text(title + "\n", encoding="utf-8")
    (folder / "blog_review_draft.md").write_text(body, encoding="utf-8")
    (folder / "source_audit.json").write_text(json.dumps({
        "verification": "NOT independently verified",
        "publication": "manual review only",
        "sources": data["sources"],
        "profile": data.get("profile", {}),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    print(run(args.input, args.out))
