import os
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from config import TEMP_DIR, MAX_VIDEO_SIZE_MB, MAX_VIDEO_NOTE_DURATION_SEC
from fsm.states import VideoEffectStates

router = Router()

@router.message(StateFilter(VideoEffectStates.WaitingForVideo))
async def receive_video_note(message: Message, state: FSMContext):
    """
    Приймає video_note, перевіряє обмеження, зберігає і переходить до ChoosingEffect.
    """
    # Перевірка, чи це video_note
    if not message.video_note:
        await message.answer("Будь ласка, надішліть відеоповідомлення (кружечок).")
        return

    # Перевіримо розмір файлу
    file_size = message.video_note.file_size or 0
    size_mb = file_size / (1024 * 1024)
    if size_mb > MAX_VIDEO_SIZE_MB:
        await message.answer(f"Файл замалий/завеликий ({size_mb:.1f} MB). Макс — {MAX_VIDEO_SIZE_MB} MB.")
        return

    # Перевіримо тривалість (секунди)
    duration = message.video_note.duration or 0
    if duration > MAX_VIDEO_NOTE_DURATION_SEC:
        await message.answer(f"Занадто довге відеоповідомлення ({duration}s). Макс — {MAX_VIDEO_NOTE_DURATION_SEC}s.")
        return

    # Завантажуємо файл
    file_id = message.video_note.file_id
    tg_file = await message.bot.get_file(file_id)
    os.makedirs(TEMP_DIR, exist_ok=True)
    save_path = os.path.join(TEMP_DIR, f"{file_id}.mp4")
    await message.bot.download_file(tg_file.file_path, save_path)

    # Зберігаємо шлях до оригіналу в FSM
    await state.update_data(original_video_path=save_path)

    # Переходимо до вибору ефекту
    await message.answer("✅ Відео отримано! Тепер оберіть ефект.")
    await state.set_state(VideoEffectStates.ChoosingEffect)


def register(dp):
    dp.include_router(router)
