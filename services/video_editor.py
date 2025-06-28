import os
import asyncio
import uuid
from config import TEMP_DIR
#from services.effects.glasses import GlassesEffect
from services.effects.explosion import ExplosionEffect
#from services.effects.hearts import HeartsEffect

async def process_video(original_video_path: str, effect: str, addon_path: str = None, explosion_start_time: float = 0.0) -> str:
    """
    Основна функція обробки відео:
    - застосовує ефект
    - додає інтро/аутро (якщо є)
    - конвертує у video_note
    """

    working_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_processed.mp4")

    # 1. Накладаємо ефект
    effect_output = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_effect.mp4")

    if effect == "glasses":
        #await GlassesEffect().apply(original_video_path, effect_output)
        pass # !!!!!!!
    elif effect == "hearts":
        #await HeartsEffect().apply(original_video_path, effect_output)
        pass # !!!!!!!
    elif effect == "explosion":
        await ExplosionEffect(start_time=explosion_start_time).apply(original_video_path, effect_output)

    else:
        # Якщо ефект не реалізований — копіюємо без змін
        effect_output = original_video_path

    # 2. Додаємо інтро/аутро, якщо є
    if addon_path and os.path.exists(addon_path):
        concat_output = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_concat.mp4")
        await concatenate_videos([addon_path, effect_output], concat_output)
        processed_path = concat_output
    else:
        processed_path = effect_output

    # 3. Приводимо до квадратного формату (1:1), готуємо до відправки як кружечок
    await convert_to_square(processed_path, working_path)

    return working_path


async def concatenate_videos(input_paths: list[str], output_path: str):
    """
    Об'єднує відео з допомогою FFmpeg.
    """
    # Створюємо тимчасовий текстовий файл зі списком
    list_file_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_list.txt")
    with open(list_file_path, "w", encoding="utf-8") as f:
        for path in input_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file_path,
        "-c", "copy",
        output_path
    ]

    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()

    os.remove(list_file_path)


async def convert_to_square(input_path: str, output_path: str):
    """
    Приводить відео до формату 1:1, оптимізованого під video_note.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "scale=min(iw\\,ih):min(iw\\,ih),pad=ceil(iw/2)*2:ceil(ih/2)*2:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "fast",
        output_path
    ]

    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()

