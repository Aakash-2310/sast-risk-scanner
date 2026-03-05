import json
from datetime import datetime
from typing import Dict, List, Any


def build_report(
    *,
    changed_files: List[str],
    findings: List[Dict],
    severity_counts: Dict[str, int],
    severity_weight: Dict[str, int],
    risk_score: int,
    action: str,
) -> Dict[str, Any]:
    """
    Risk analytics report (JSON):
    - counts by severity
    - risk score breakdown
    - decision/action
    - findings list
    """
    severity_part = (
        severity_weight.get("HIGH", 0) * severity_counts.get("HIGH", 0)
        + severity_weight.get("MEDIUM", 0) * severity_counts.get("MEDIUM", 0)
        + severity_weight.get("LOW", 0) * severity_counts.get("LOW", 0)
    )

    ee_part = sum(int(f.get("exploitability", 0)) * int(f.get("exposure", 0)) for f in findings)

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "risk_score": risk_score,
        "changed_files": changed_files,
        "summary": {
            "total_findings": len(findings),
            "high": severity_counts.get("HIGH", 0),
            "medium": severity_counts.get("MEDIUM", 0),
            "low": severity_counts.get("LOW", 0),
        },
        "risk_breakdown": {
            "severity_weight_x_count": severity_part,
            "exploitability_x_exposure": ee_part,
            "formula": "Risk Score = (severity_weight × count) + (exploitability × exposure)",
        },
        "findings": findings,
    }


def write_report(path: str, report: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)