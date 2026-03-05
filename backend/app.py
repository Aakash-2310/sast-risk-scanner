import os
import json
import subprocess
from fastapi import FastAPI, HTTPException

from backend.config import REPORT_DIR, SCANNER_FILE
from backend.models import ScanRequest, ScanResponse
from backend.storage import ensure_reports_dir, generate_report_name, load_latest_report

app = FastAPI(title="SAST Backend", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResponse)
def scan(req: ScanRequest):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if not os.path.exists(os.path.join(repo_root, ".git")):
        raise HTTPException(status_code=400, detail="Not a git repo. Run from project root.")

    ensure_reports_dir(REPORT_DIR)
    report_name = generate_report_name(req.report_name)
    report_path = os.path.join(REPORT_DIR, report_name)

    cmd = ["python", SCANNER_FILE, "--report", report_path]
    if req.base:
        cmd += ["--base", req.base]
    if req.head:
        cmd += ["--head", req.head]
    if req.verbose:
        cmd += ["--verbose"]

    proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
    exit_code = proc.returncode

    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            result = json.load(f)
    else:
        result = {
            "action": "ERROR",
            "risk_score": -1,
            "summary": {},
            "findings": [],
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }

    return ScanResponse(ok=True, exit_code=exit_code, report_path=report_path, result=result)


@app.get("/reports/latest")
def reports_latest():
    data = load_latest_report(REPORT_DIR)
    if not data:
        raise HTTPException(status_code=404, detail="No reports found.")
    return data
@app.get("/")
def home():
    return {"message": "SAST Backend running. "}