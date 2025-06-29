from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from fsm.states import VideoEffectStates

router = Router()

EFFECTS = {
    "glasses": "🕶️ Glasses",
    "laugh": "😂 Laughing",
    "hearts": "❤️ Hearts"
}

@router.message(StateFilter(VideoEffectStates.ChoosingEffect))
async def prompt_effect_choice(message: Message):
    builder = InlineKeyboardBuilder()
    for key, name in EFFECTS.items():
        builder.button(text=name, callback_data=f"effect:{key}")
    builder.adjust(2)
    await message.answer("Оберіть ефект для накладення на відео:", reply_markup=builder.as_markup())

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

    if effect_key == "explosion":
        await state.set_state(VideoEffectStates.WaitingForExplosionTime)
        await callback.message.answer("⏱ Вкажіть секунду, з якої почати вибух (наприклад, 1.5)")
    else:
        await state.set_state(VideoEffectStates.ChoosingAddonType)
        await callback.message.answer("Чи бажаєте додати інтро або аутро до відео?")

@router.message(StateFilter(VideoEffectStates.WaitingForExplosionTime))
async def receive_explosion_time(message: Message, state: FSMContext):
    try:
        start_time = float(message.text.replace(",", "."))
        if start_time < 0:
            raise ValueError

        await state.update_data(explosion_start_time=start_time)
        await state.set_state(VideoEffectStates.ChoosingAddonType)
        await message.answer("✅ Час вибуху збережено! Чи бажаєте додати інтро або аутро до відео?")
    except ValueError:
        await message.answer("❌ Введіть коректне число — секунду, з якої почати вибух (наприклад, 1.5).")
