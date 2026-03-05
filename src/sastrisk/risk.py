from collections import Counter
from typing import Dict, List, Tuple


def count_by_severity(findings: List[Dict]) -> Dict[str, int]:
    c = Counter(f.get("severity") for f in findings)
    return {
        "HIGH": int(c.get("HIGH", 0)),
        "MEDIUM": int(c.get("MEDIUM", 0)),
        "LOW": int(c.get("LOW", 0)),
    }


def compute_risk_score(findings: List[Dict], severity_weight: Dict[str, int]) -> int:
    """
    EXACT internship formula:

    Risk Score =
      (severity_weight × count) +
      (exploitability × exposure)

    Interpreted as:
    - severity_weight × count => sum over severities (weight[sev] * count_of_sev)
    - exploitability × exposure => sum over findings (finding.exploitability * finding.exposure)
    """
    sev_counts = count_by_severity(findings)

    severity_part = 0
    for sev, cnt in sev_counts.items():
        severity_part += int(severity_weight.get(sev, 0)) * int(cnt)

    ee_part = 0
    for f in findings:
        ee_part += int(f.get("exploitability", 0)) * int(f.get("exposure", 0))

    return int(severity_part + ee_part)


def decide_action(findings: List[Dict]) -> Tuple[str, int]:
    """
    Block Rules:
    - High severity => Block merge (exit 2)
    - Medium severity => Warning (exit 0)
    - Low severity => Log only (exit 0)
    - No findings => Pass (exit 0)
    """
    sev = count_by_severity(findings)

    if sev["HIGH"] > 0:
        return "BLOCK", 2
    if sev["MEDIUM"] > 0:
        return "WARN", 0
    if sev["LOW"] > 0:
        return "LOG", 0

    return "PASS", 0