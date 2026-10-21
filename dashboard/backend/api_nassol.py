"""Review-only NASSOL endpoints; no external publishing or paid API calls."""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from nassol_review.editorial import build, run

router = APIRouter()
BASE = Path(__file__).resolve().parents[2]

class DraftRequest(BaseModel):
    person: str
    title: str = ""
    sources: list[dict]
    editorial: dict
    profile: dict = {}

@router.post("/nassol/draft")
def create_nassol_draft(request: DraftRequest):
    data = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    try:
        title, _ = build(data)
        folder = run_data(data)
        return {"success": True, "title": title, "draft": (folder / "blog_review_draft.md").read_text(encoding="utf-8"), "output_folder": str(folder), "published": False}
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))

def run_data(data: dict) -> Path:
    """Persist a review draft without accepting filesystem paths from HTTP input."""
    import json
    from datetime import datetime
    output = BASE / "data" / "nassol" / "review"
    output.mkdir(parents=True, exist_ok=True)
    folder = output / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    folder.mkdir()
    title, body = build(data)
    (folder / "final_title.txt").write_text(title + "\n", encoding="utf-8")
    (folder / "blog_review_draft.md").write_text(body, encoding="utf-8")
    (folder / "source_audit.json").write_text(json.dumps({"verified": False, "sources": data["sources"]}, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder
