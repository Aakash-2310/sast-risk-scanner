# SAST Risk Scanner

This project implements a CI/CD integrated Static Application Security Testing (SAST) scanner with risk-based merge control.

## Features
- Diff based scanning
- Runs on Pull Requests
- Risk score calculation
- Blocks merge for high severity vulnerabilities

## Run locally
python sast_scan.py --report reports/local_report.json --verbose

## Install git hook
bash scripts/install_hook.sh

## Run backend (optional)
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000