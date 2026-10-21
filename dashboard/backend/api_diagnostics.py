"""Read-only checks for dashboard dependencies."""
import json
import shutil
from pathlib import Path
from fastapi import APIRouter
router = APIRouter()
ROOT = Path(__file__).resolve().parents[2]

@router.get("/diagnostics")
def diagnostics():
    config_path = ROOT / "config" / "engine.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        config = {}
    provider = config.get("writing", {}).get("provider", "unset")
    cli = shutil.which("openclaw.cmd") or shutil.which("openclaw")
    writer_ready = bool(cli) if provider == "openclaw" else None
    return {
        "server": "ok",
        "writing_provider": provider,
        "writing_cli_available": bool(cli),
        "writing_status": "missing_cli" if provider == "openclaw" and not cli else ("unverified" if writer_ready is None else "cli_found_not_authenticated"),
        "nassol_review": "available",
        "nassol_auto_research": "not_implemented",
        "nassol_auto_publish": False,
    }
