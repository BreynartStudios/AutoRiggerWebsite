import asyncio
import logging
from pathlib import Path

from app.config import BLENDER_PATH, BLENDER_SCRIPTS_DIR, JOB_TIMEOUT

logger = logging.getLogger(__name__)


class BlenderError(Exception):
    """Raised when a Blender script fails."""
    pass


async def run_blender_script(script_name: str, args: list[str]) -> str:
    """
    Run a Blender Python script headlessly.

    Args:
        script_name: Name of the script in blender_scripts/
        args: Arguments to pass after "--"

    Returns:
        stdout output from Blender

    Raises:
        BlenderError: If the script fails
    """
    script_path = BLENDER_SCRIPTS_DIR / script_name
    if not script_path.exists():
        raise BlenderError(f"Script not found: {script_name}")

    cmd = [
        BLENDER_PATH,
        "--background",
        "--python", str(script_path),
        "--",
        *args,
    ]

    logger.info("Running Blender: %s", " ".join(cmd))

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=JOB_TIMEOUT,
        )

        stdout_text = stdout.decode("utf-8", errors="replace")
        stderr_text = stderr.decode("utf-8", errors="replace")

        if process.returncode != 0:
            logger.error(
                "Blender script failed (exit %d):\nstdout: %s\nstderr: %s",
                process.returncode, stdout_text, stderr_text,
            )
            raise BlenderError(
                f"Blender exited with code {process.returncode}: {stderr_text[:500]}"
            )

        logger.info("Blender script completed successfully")
        return stdout_text

    except asyncio.TimeoutError:
        process.kill()
        raise BlenderError(f"Blender script timed out after {JOB_TIMEOUT}s")
    except FileNotFoundError:
        raise BlenderError(
            f"Blender not found at '{BLENDER_PATH}'. "
            "Install Blender or set BLENDER_PATH environment variable."
        )
