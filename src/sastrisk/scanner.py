from typing import Dict, List
from .rules import Rule, is_scannable_file


def scan_file(path: str, rules: List[Rule]) -> List[Dict]:
    if not is_scannable_file(path):
        return []

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception:
        return []

    findings: List[Dict] = []

    for line_no, line in enumerate(lines, start=1):
        for rule in rules:
            if rule.pattern.search(line):
                findings.append(
                    {
                        "rule_id": rule.rule_id,
                        "title": rule.title,
                        "severity": rule.severity,
                        "file": path,
                        "line": line_no,
                        "snippet": line.strip()[:200],
                        "exploitability": rule.exploitability,
                        "exposure": rule.exposure,
                    }
                )

    return findings


def scan_files(files: List[str], rules: List[Rule]) -> List[Dict]:
    all_findings: List[Dict] = []
    for f in files:
        all_findings.extend(scan_file(f, rules))
    return all_findings