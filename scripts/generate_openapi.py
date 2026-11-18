import json
from pathlib import Path

from api.app import app

ROOT = Path(__file__).resolve().parents[1]

(ROOT / "openapi.json").write_text(
    json.dumps(app.openapi(), indent=2) + "\n",
    encoding="utf-8",
)
