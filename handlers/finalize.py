# handlers/finalize.py

import os
from aiogram import Router
from aiogram.types import Message, InputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from config import TEMP_DIR
from fsm.states import VideoEffectStates
from services.video_editor import process_video

router = Router()

@router.message(StateFilter(VideoEffectStates.Processing))
async def finalize_processing(message: Message, state: FSMContext):
    data = await state.get_data()
    original_path = data.get("original_video_path")
    chosen_effect = data.get("chosen_effect")
    addon_path = data.get("addon_path")  # інтро/аутро (або None)

    if not original_path or not os.path.exists(original_path):
        await message.answer("Помилка: оригінальне відео не знайдено. Спробуйте ще раз.")
        await state.clear()
        return

    await message.answer("Обробляю відео, будь ласка, зачекайте...")

    try:
        output_path = await process_video(
            original_video_path=original_path,
            effect=chosen_effect,
            addon_path=addon_path
        )
    except Exception as e:
        await message.answer(f"Сталася помилка при обробці відео:\n{e}")
        await state.clear()
        return

    if not output_path or not os.path.exists(output_path):
        await message.answer("Не вдалося створити оброблене відео.")
        await state.clear()
        return

    # Відправляємо готове відео у форматі video_note (кружечок)
    await message.answer_video_note(InputFile(output_path))

    # Чистимо тимчасові файли (оригінал і результат)
    try:
        os.remove(original_path)
        os.remove(output_path)
        if addon_path and os.path.exists(addon_path) and addon_path.startswith(TEMP_DIR):
            os.remove(addon_path)
    except Exception:
        pass  # Ігноруємо помилки під час видалення

    await state.clear()
