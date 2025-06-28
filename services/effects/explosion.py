import os
import asyncio
from config import MEDIA_DIR
from services.effects.base import BaseEffect

EXPLOSION_DURATION = 3.553  # тривалість ефекту в секундах

class ExplosionEffect(BaseEffect):
    def __init__(self, start_time: float = 0.0):
        self.overlay_path = os.path.join(MEDIA_DIR, "overlays", "explosion.mp4")
        self.overlay_duration = EXPLOSION_DURATION
        self.start_time = start_time  # час початку накладення ефекту

    async def apply(self, input_path: str, output_path: str) -> None:
        video_duration = await self._get_video_duration(input_path)

        start_time = self.start_time
        if start_time < 0:
            start_time = 0.0
        if start_time + self.overlay_duration > video_duration:
            start_time = max(0.0, video_duration - self.overlay_duration)

        filter_complex = (
            f"[1:v]format=yuva420p,"
            f"fade=t=in:st=0:d=0.3:alpha=1,"
            f"fade=t=out:st={self.overlay_duration - 0.3}:d=0.3:alpha=1[ol];"
            f"[0:v][ol]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:"
            f"enable='between(t,{start_time},{start_time + self.overlay_duration})'[v];"
            f"[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-i", self.overlay_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            output_path
        ]

        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.communicate()

    async def _get_video_duration(self, path: str) -> float:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        return float(stdout.decode().strip())
