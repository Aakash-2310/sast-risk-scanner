import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


def ensure_reports_dir(report_dir: str) -> None:
    os.makedirs(report_dir, exist_ok=True)


def generate_report_name(name: Optional[str] = None) -> str:
    if name:
        return name if name.endswith(".json") else name + ".json"
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"sast_report_{ts}.json"


def load_latest_report(report_dir: str) -> Optional[Dict[str, Any]]:
    if not os.path.isdir(report_dir):
        return None

    files = [f for f in os.listdir(report_dir) if f.endswith(".json")]
    if not files:
        return None

    files.sort(key=lambda x: os.path.getmtime(os.path.join(report_dir, x)), reverse=True)
    latest = os.path.join(report_dir, files[0])

    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)