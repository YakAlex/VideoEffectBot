import os
import asyncio
from typing import Literal
from config import MAX_VIDEO_SIZE_MB, MAX_INTRO_DURATION_SEC, INTROS_DIR, OUTROS_DIR

AddonType = Literal["intro", "outro"]

ADDON_DIRS = {
    "intro": INTROS_DIR,
    "outro": OUTROS_DIR
}

def get_available_addons(kind: AddonType) -> list[str]:
    folder = ADDON_DIRS.get(kind)
    if not folder or not os.path.isdir(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith(".mp4")]

def get_addon_path(kind: AddonType, filename: str) -> str:
    return os.path.abspath(os.path.join(ADDON_DIRS[kind], filename))

async def validate_user_video(path: str) -> bool:
    if not path.endswith(".mp4"):
        return False

    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > MAX_VIDEO_SIZE_MB:
        return False

    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    stdout, _ = await proc.communicate()

    try:
        width, height, duration = stdout.decode().strip().split("\n")
        width = int(width)
        height = int(height)
        duration = float(duration)

        aspect_ratio = round(width / height, 2)
        if duration > MAX_INTRO_DURATION_SEC:
            return False
        if not 0.95 <= aspect_ratio <= 1.05:
            return False

    except Exception:
        return False

    return True
