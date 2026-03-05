import os
import subprocess
from typing import List, Optional, Tuple


def _run_git(args: List[str]) -> str:
    """
    Runs a git command and returns stdout (stripped).
    Raises RuntimeError with stderr when git fails.
    """
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def in_git_repo() -> bool:
    try:
        _run_git(["rev-parse", "--is-inside-work-tree"])
        return True
    except Exception:
        return False


def ensure_fetch(ref: str) -> None:
    """
    In CI, origin/<branch> might not exist locally.
    This tries to fetch the branch. If it fails, we ignore.
    """
    try:
        if ref and ref.startswith("origin/"):
            branch = ref.split("origin/")[-1]
            subprocess.run(
                ["git", "fetch", "origin", branch, "--depth=1"],
                capture_output=True,
                text=True,
            )
    except Exception:
        pass


def guess_refs_from_env() -> Tuple[Optional[str], Optional[str]]:
    """
    GitHub PR:
      GITHUB_BASE_REF, GITHUB_HEAD_REF
    GitLab MR:
      CI_MERGE_REQUEST_TARGET_BRANCH_NAME, CI_COMMIT_REF_NAME
    """
    gh_base = os.getenv("GITHUB_BASE_REF")
    gh_head = os.getenv("GITHUB_HEAD_REF")
    if gh_base and gh_head:
        return f"origin/{gh_base}", f"origin/{gh_head}"

    gl_base = os.getenv("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    gl_head = os.getenv("CI_COMMIT_REF_NAME")
    if gl_base and gl_head:
        return f"origin/{gl_base}", f"origin/{gl_head}"

    return None, None


def _split_lines(output: str) -> List[str]:
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_changed_files(base: Optional[str], head: Optional[str]) -> List[str]:
    """
    Diff-based changed files list.

    Priority:
    1) If base+head are provided: diff base...head (PR/MR)
    2) Else:
       a) If commit_count >= 2: diff HEAD~1...HEAD
       b) If commit_count == 1: try staged diff (--cached), else scan all tracked files
       c) If commit_count == 0 (rare): scan all tracked files

    This avoids the common "ambiguous argument HEAD~1" error in new repos.
    """

    # Case 1: PR/MR diff
    if base and head:
        diff_range = f"{base}...{head}"
        out = _run_git(["diff", "--name-only", diff_range])
        return _split_lines(out)

    # Determine commit count
    commit_count = 0
    try:
        commit_count = int(_run_git(["rev-list", "--count", "HEAD"]))
    except Exception:
        commit_count = 0

    # Case 2a: normal repo (2+ commits)
    if commit_count >= 2:
        out = _run_git(["diff", "--name-only", "HEAD~1...HEAD"])
        return _split_lines(out)

    # Case 2b: first commit repo
    # Try staged changes (useful before first commit, or right after initial commit)
    try:
        out = _run_git(["diff", "--name-only", "--cached"])
        staged = _split_lines(out)
        if staged:
            return staged
    except Exception:
        pass

    # Fallback: scan all tracked files
    try:
        out = _run_git(["ls-files"])
        return _split_lines(out)
    except Exception:
        return []