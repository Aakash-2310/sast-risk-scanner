import os

REPORT_DIR = os.getenv("SAST_REPORT_DIR", "reports")
SCANNER_FILE = os.getenv("SAST_SCANNER_FILE", "sast_scan.py")