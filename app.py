import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram import F

import logging
import sys
import os

from admin import check_admin
from data_handlers import create_excel_file
from database import create_appeal, session, get_all_appeal
from texts import ABOUT_TEXT, DESCRIPTION, NEXT_MESSAGE, TO_MESSAGES, NULL_STATE
from tools import generate_filename, generate_short_filename
from config import API_TOKEN


MAIN_CALLBACK_DATA = ['button_idea', 'button_claim', 'button_news']

PATH_TO_DATA = 'data/'

# Инициализация бота и диспетчера
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=API_TOKEN)


# Функция временно депрекейтнута
def main_keyboard_dep():
    button1 = InlineKeyboardButton(text="Идея",
                                   callback_data="button_idea")
    button2 = InlineKeyboardButton(text="Жалоба",
                                   callback_data="button_claim")
    button3 = InlineKeyboardButton(text="Новость",
                                   callback_data="button_news")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button1],
            [button2],
            [button3]
        ]
    )
    return keyboard


def main_keyboard():
    button = InlineKeyboardButton(text='Начать направлять новости',
                                  callback_data='get_text')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button]
        ]
    )
    return keyboard

def admin_keyboard():
    button = InlineKeyboardButton(text='Получить все записи в excel',
                                  callback_data='get_all_appeals')
    button2 = InlineKeyboardButton(text='Добавить админа',
                                   callback_data='add_admin')
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [button],
            [button2]
        ]
    )
    return keyboard

# Состояния
class Form(StatesGroup):
    get_text = State()


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        DESCRIPTION,
        reply_markup=main_keyboard(),
    )

@dp.message(Command('about'))
async def command_about(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        ABOUT_TEXT
    )

@dp.message(Command('admin'))
@check_admin
async def command_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Админ может:',
        reply_markup=admin_keyboard()
    )


@dp.callback_query(lambda c: c.data == 'get_text')
async def save_state_and_data(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.answer(TO_MESSAGES)
    await state.set_state(Form.get_text)


@dp.callback_query(lambda c: c.data == 'get_all_appeals')
async def get_all_appeals(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    appeals = await get_all_appeal(session)
    filename = await generate_filename(callback_query.from_user.id,
                                       callback_query.from_user.username)
    short_filename = await generate_short_filename(
        callback_query.from_user.username)
    path_to_file = f'{PATH_TO_DATA}{filename}'
    await create_excel_file(appeals, path_to_file)
    file = FSInputFile(path_to_file, filename=short_filename)
    await callback_query.bot.send_document(callback_query.from_user.id, file)
    os.remove(path_to_file)


@dp.message(StateFilter(Form.get_text))
async def add_appeal(message: Message, state: FSMContext) -> None:
    await create_appeal(session,
                        message.from_user.id,
                        message.from_user.username,
                        message.text
                        )
    await message.answer(NEXT_MESSAGE)

@dp.message()
async def null_state(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(NULL_STATE)

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
