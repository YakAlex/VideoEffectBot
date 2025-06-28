from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from fsm.states import VideoEffectStates

router = Router()

# Кнопки з простими ефектами
EFFECTS = {
    "glasses": "🕶️ Glasses",
    "explosion": "💥 Explosion",
    "laugh": "😂 Laughing",
    "hearts": "❤️ Hearts"
}

@router.message(StateFilter(VideoEffectStates.ChoosingEffect))
async def prompt_effect_choice(message: Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(text=name, callback_data=f"effect:{key}") for key, name in EFFECTS.items()]
    keyboard.add(*buttons)
    await message.answer("Оберіть ефект для накладення на відео:", reply_markup=keyboard)


@router.callback_query(StateFilter(VideoEffectStates.ChoosingEffect))
async def handle_effect_choice(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("effect:"):
        return

    effect_key = callback.data.split(":", 1)[1]
    if effect_key not in EFFECTS:
        await callback.answer("Невідомий ефект", show_alert=True)
        return

    await state.update_data(chosen_effect=effect_key)
    await callback.answer(f"Обрано ефект: {EFFECTS[effect_key]}")

    # Переходимо до вибору інтро/аутро
    await state.set_state(VideoEffectStates.ChoosingAddonType)
    await callback.message.answer("Чи бажаєте додати інтро або аутро до відео?")
