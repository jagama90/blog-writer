"""Review-only NASSOL endpoints; no external publishing or paid API calls."""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from nassol_review.media import cards, video
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
        media_error = None
        paths = []
        clip = None
        try:
            paths = cards(data, folder)
            clip = video(paths, folder)
        except (RuntimeError, ValueError, OSError) as exc:
            media_error = str(exc)
        return {"success": True, "title": title, "draft": (folder / "blog_review_draft.md").read_text(encoding="utf-8"),
                "output_folder": str(folder), "job_id": folder.name,
                "cards": [f"/api/nassol/media/{folder.name}/{p.name}" for p in paths],
                "video": f"/api/nassol/media/{folder.name}/nassol_short.mp4" if clip else None,
                "media_error": media_error, "published": False}
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

@router.get("/nassol/media/{job_id}/{filename}")
def download_media(job_id: str, filename: str):
    import re
    if not re.fullmatch(r"\d{8}_\d{6}_\d{6}", job_id):
        raise HTTPException(status_code=400, detail="Invalid job")
    if filename not in {*(f"card_{i:02d}.png" for i in range(1, 6)), "nassol_short.mp4"}:
        raise HTTPException(status_code=400, detail="Invalid file")
    root = (BASE / "data" / "nassol" / "review").resolve()
    folder = (root / job_id).resolve()
    if folder.parent != root:
        raise HTTPException(status_code=400, detail="Invalid path")
    path = folder / ("cards" if filename.endswith(".png") else "") / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not generated")
    return FileResponse(path, filename=filename)
