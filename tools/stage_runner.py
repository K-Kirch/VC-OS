"""
Stage runner — spawns one headless `claude -p` per IC-prep stage.

Owns:
  - prompt template loading + variable interpolation
  - subprocess invocation with scoped permissions
  - per-run log capture under IC-prep/_pipeline/runs/<slug>/

Does not own:
  - state machine logic (orchestrator.py reads deal.md after the run)
  - Notion I/O (orchestrator.py only)
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
HEADLESS_SETTINGS_PATH = Path(__file__).resolve().parent / "headless-settings.json"


class StageRunError(RuntimeError):
    pass


def _claude_executable():
    """Resolve the claude CLI on PATH. Returns the path string or raises."""
    # On Windows, shutil.which finds claude.cmd / claude.exe automatically.
    exe = shutil.which("claude")
    if not exe:
        raise StageRunError(
            "claude CLI not found on PATH. Install Claude Code and ensure `claude` is callable."
        )
    return exe


def render_prompt(stage_number, slug):
    """Load the stage prompt template and interpolate variables."""
    candidates = list(PROMPTS_DIR.glob(f"stage-{stage_number}-*.txt"))
    if not candidates:
        raise StageRunError(f"No prompt template for stage {stage_number} in {PROMPTS_DIR}")
    if len(candidates) > 1:
        raise StageRunError(f"Multiple prompts match stage {stage_number}: {candidates}")
    template = candidates[0].read_text(encoding="utf-8")
    return template.format(slug=slug)


def _log_path(slug, stage_number):
    runs_dir = WORKSPACE_ROOT / "IC-prep" / "_pipeline" / "runs" / slug
    runs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return runs_dir / f"{ts}-stage-{stage_number}.log"


def run_stage(slug, stage_number, deal_path, timeout_seconds=1800, dry_run=False):
    """
    Spawn headless claude for one stage. Returns dict with keys:
      exit_code, log_path, stdout_tail, stderr_tail
    The caller (orchestrator) is responsible for reading deal.md afterward
    to confirm state transition.
    """
    prompt = render_prompt(stage_number, slug)
    log_file = _log_path(slug, stage_number)

    cmd = [
        _claude_executable(),
        "-p", prompt,
        "--dangerously-skip-permissions",
    ]

    if dry_run:
        log_file.write_text(
            f"DRY RUN — command would be:\n{' '.join(repr(c) for c in cmd)}\n\n"
            f"--- PROMPT ---\n{prompt}\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "log_path": log_file,
            "stdout_tail": "(dry run)",
            "stderr_tail": "",
            "dry_run": True,
        }

    # Strip parent Claude Code env vars so the child does not detect nested
    # execution and silently downgrade permissions.
    child_env = {
        k: v for k, v in os.environ.items()
        if not (k.startswith("CLAUDECODE") or k.startswith("CLAUDE_CODE_"))
    }

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            encoding="utf-8",
            errors="replace",
            env=child_env,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as e:
        log_file.write_text(
            f"TIMEOUT after {timeout_seconds}s\n\n"
            f"--- PROMPT ---\n{prompt}\n\n"
            f"--- PARTIAL STDOUT ---\n{(e.stdout or '')}\n\n"
            f"--- PARTIAL STDERR ---\n{(e.stderr or '')}\n",
            encoding="utf-8",
        )
        raise StageRunError(f"Stage {stage_number} for {slug} timed out after {timeout_seconds}s") from e

    log_file.write_text(
        f"exit_code={proc.returncode}\n\n"
        f"--- PROMPT ---\n{prompt}\n\n"
        f"--- STDOUT ---\n{proc.stdout}\n\n"
        f"--- STDERR ---\n{proc.stderr}\n",
        encoding="utf-8",
    )

    return {
        "exit_code": proc.returncode,
        "log_path": log_file,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-1000:],
        "dry_run": False,
    }


def parse_stage_result_line(stdout_text):
    """Pull the final 'STAGE_RESULT: ...' line, if present."""
    for line in reversed(stdout_text.splitlines()):
        if line.startswith("STAGE_RESULT:"):
            return line.strip()
    return None


def detect_usage_limit(stdout_text):
    """Return a friendly message if the child claude hit a usage cap, else None."""
    if not stdout_text:
        return None
    lowered = stdout_text.lower()
    if "you've hit your limit" in lowered or "you have hit your limit" in lowered:
        # Surface the first non-empty line for the actual reset time string.
        for line in stdout_text.splitlines():
            if line.strip():
                return line.strip()
        return "Claude usage limit hit."
    return None
