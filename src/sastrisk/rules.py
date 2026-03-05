import re
from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    rule_id: str
    title: str
    severity: str  # HIGH / MEDIUM / LOW
    pattern: re.Pattern
    exploitability: int
    exposure: int


def default_rules() -> List[Rule]:
    """
    Simple regex starter rules (internship level).
    Each rule includes exploitability + exposure for risk scoring.
    """
    return [
        Rule(
            rule_id="SQLI_001",
            title="Possible SQL Injection (query string building)",
            severity="HIGH",
            pattern=re.compile(r"(SELECT|UPDATE|DELETE|INSERT).*(\+|format\(|%s)", re.IGNORECASE),
            exploitability=9,
            exposure=8,
        ),
        Rule(
            rule_id="SECRET_001",
            title="Hardcoded secret (password/api key/token)",
            severity="HIGH",
            pattern=re.compile(r"(password|api[_-]?key|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE),
            exploitability=8,
            exposure=9,
        ),
        Rule(
            rule_id="CMD_001",
            title="Potential command injection (shell=True)",
            severity="HIGH",
            pattern=re.compile(r"subprocess\.(run|Popen)\(.*shell\s*=\s*True", re.IGNORECASE),
            exploitability=8,
            exposure=7,
        ),
        Rule(
            rule_id="DEBUG_001",
            title="Debug mode enabled",
            severity="MEDIUM",
            pattern=re.compile(r"\bdebug\s*=\s*True\b", re.IGNORECASE),
            exploitability=4,
            exposure=6,
        ),
        Rule(
            rule_id="WEAK_HASH_001",
            title="Weak hash algorithm (md5/sha1)",
            severity="LOW",
            pattern=re.compile(r"\b(md5|sha1)\b", re.IGNORECASE),
            exploitability=2,
            exposure=4,
        ),
    ]


def is_scannable_file(path: str) -> bool:
    allowed = (
        ".py", ".js", ".ts", ".java", ".c", ".cpp", ".cs",
        ".go", ".php", ".rb", ".rs",
        ".html", ".css", ".sql", ".yaml", ".yml", ".json"
    )
    return path.lower().endswith(allowed)