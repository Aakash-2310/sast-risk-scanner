import argparse
import json

from .git_utils import in_git_repo, guess_refs_from_env, ensure_fetch, get_changed_files
from .rules import default_rules
from .scanner import scan_files
from .risk import count_by_severity, compute_risk_score, decide_action
from .report import build_report, write_report


def load_weights(weights_path: str) -> dict:
    try:
        with open(weights_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "severity_weight": {"HIGH": 10, "MEDIUM": 5, "LOW": 2},
            "default_exposure": 6,
            "default_exploitability": {"HIGH": 8, "MEDIUM": 5, "LOW": 2},
        }


def main():
    parser = argparse.ArgumentParser(description="Diff-based SAST scanner with risk-based merge control")
    parser.add_argument("--base", help="Base ref (branch or SHA)")
    parser.add_argument("--head", help="Head ref (branch or SHA)")
    parser.add_argument("--weights", default="config/weights.json", help="Weights config JSON")
    parser.add_argument("--report", required=True, help="Output report JSON path")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not in_git_repo():
        print("Not inside a git repository.")
        raise SystemExit(1)

    base = args.base
    head = args.head

    # ✅ Only infer from CI env if user did NOT pass base/head
    if not base and not head:
        base, head = guess_refs_from_env()

    # fetch only when it is origin/<branch> format
    if base:
        ensure_fetch(base)
    if head:
        ensure_fetch(head)

    changed_files = get_changed_files(base, head)

    rules = default_rules()
    findings = scan_files(changed_files, rules)

    weights_cfg = load_weights(args.weights)
    severity_weight = weights_cfg.get("severity_weight", {"HIGH": 10, "MEDIUM": 5, "LOW": 2})

    sev_counts = count_by_severity(findings)
    risk_score = compute_risk_score(findings, severity_weight=severity_weight)
    action, exit_code = decide_action(findings)

    report = build_report(
        changed_files=changed_files,
        findings=findings,
        severity_counts=sev_counts,
        severity_weight=severity_weight,
        risk_score=risk_score,
        action=action,
    )
    write_report(args.report, report)

    print("\n=== SAST Risk Scan ===")
    print(f"Base: {base}")
    print(f"Head: {head}")
    print(f"Changed files: {len(changed_files)}")
    print(f"Findings: total={len(findings)} high={sev_counts['HIGH']} medium={sev_counts['MEDIUM']} low={sev_counts['LOW']}")
    print(f"Risk Score: {risk_score}")
    print(f"Decision: {action}")
    print(f"Report: {args.report}")

    raise SystemExit(exit_code)