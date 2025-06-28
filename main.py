import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import video_note, effects, addons, finalize

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from fsm.states import VideoEffectStates

# Увімкнемо логування
logging.basicConfig(level=logging.INFO)

router = Router()

async def set_default_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запуск"),
    ]
    await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    @dp.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("👋 Привіт! Надішли відеоповідомлення (кружечок), щоб почати обробку.")
        await state.set_state(VideoEffectStates.WaitingForVideo)

    # Реєструємо всі модулі
    dp.include_router(video_note.router)
    dp.include_router(effects.router)
    dp.include_router(addons.router)
    dp.include_router(finalize.router)

    await set_default_commands(bot)
    print("Бот запущено")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
