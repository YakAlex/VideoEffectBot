import os
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from config import TEMP_DIR, INTROS_DIR, OUTROS_DIR
from fsm.states import VideoEffectStates

router = Router()


@router.message(StateFilter(VideoEffectStates.ChoosingAddonType))
async def prompt_addon_type(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Інтро", callback_data="addon:intro"),
         InlineKeyboardButton(text="➕ Аутро", callback_data="addon:outro")],
        [InlineKeyboardButton(text="🚫 Пропустити", callback_data="addon:none")]
    ])
    await message.answer("Чи бажаєте додати інтро або аутро до відео?", reply_markup=keyboard)


@router.callback_query(StateFilter(VideoEffectStates.ChoosingAddonType))
async def handle_addon_type(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("addon:"):
        return
    addon = callback.data.split(":")[1]
    await state.update_data(addon_type=addon)
    await callback.answer(f"Обрано: {addon}")

    if addon == "none":
        await state.set_state(VideoEffectStates.Processing)
        await callback.message.answer("Обробляю відео без інтро або аутро...")
    else:
        await state.set_state(VideoEffectStates.ChoosingAddonSource)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📁 Бібліотека", callback_data="source:library"),
             InlineKeyboardButton(text="📤 Моє відео", callback_data="source:custom")]
        ])
        await callback.message.answer("Оберіть джерело для інтро/аутро:", reply_markup=keyboard)


@router.callback_query(StateFilter(VideoEffectStates.ChoosingAddonSource))
async def handle_addon_source(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("source:"):
        return
    source = callback.data.split(":")[1]
    await state.update_data(addon_source=source)
    await callback.answer(f"Джерело: {source}")

    if source == "custom":
        await state.set_state(VideoEffectStates.WaitingForAddonVideo)
        await callback.message.answer("Надішліть своє відео (до 10 сек, MP4, 1:1)...")
    else:
        # Показати список файлів з бібліотеки
        data = await state.get_data()
        addon_type = data.get("addon_type")
        folder = INTROS_DIR if addon_type == "intro" else OUTROS_DIR
        video_files = [f for f in os.listdir(folder) if f.lower().endswith(".mp4")]

        if not video_files:
            await callback.message.answer("У бібліотеці наразі немає доступних відео.")
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=video.split("_", 1)[-1].replace(".mp4", "").capitalize(),
                callback_data=f"lib:{video}"
            )] for video in video_files
        ])

        await state.set_state(VideoEffectStates.ChoosingAddonFromLibrary)
        await callback.message.answer("Оберіть інтро/аутро з бібліотеки:", reply_markup=keyboard)


@router.callback_query(StateFilter(VideoEffectStates.ChoosingAddonFromLibrary))
async def choose_library_addon(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("lib:"):
        return
    filename = callback.data.split(":", 1)[1]

    data = await state.get_data()
    addon_type = data.get("addon_type")
    folder = INTROS_DIR if addon_type == "intro" else OUTROS_DIR

    full_path = os.path.join(folder, filename)
    if not os.path.exists(full_path):
        await callback.message.answer("Помилка: файл не знайдено.")
        return

    await state.update_data(addon_path=full_path)
    await state.set_state(VideoEffectStates.Processing)
    await callback.answer("Відео з бібліотеки обрано.")
    await callback.message.answer("Обробляю відео з вибраним додатком...")


@router.message(StateFilter(VideoEffectStates.WaitingForAddonVideo))
async def receive_custom_addon(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("Надішліть відео у форматі MP4 (до 10 сек, 1:1)...")
        return

    file_id = message.video.file_id
    tg_file = await message.bot.get_file(file_id)
    os.makedirs(TEMP_DIR, exist_ok=True)
    save_path = os.path.join(TEMP_DIR, f"addon_{file_id}.mp4")
    await message.bot.download_file(tg_file.file_path, save_path)

    await state.update_data(addon_path=save_path)
    await state.set_state(VideoEffectStates.Processing)
    await message.answer("✅ Додаткове відео отримано. Починаю обробку...")
