import pandas
import asyncio
import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import access

import DLink_data

BOTNAME = access.BOTNAME
BOTID = access.BOTID

bot = Bot(token=BOTID)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class you_name(StatesGroup):
    username = State()

def get_trafic(user):
    if user == "Василич":
        data1 = pandas.read_csv("Василич_мобила.log")
        data2 = pandas.read_csv("Василич_ноут.log")
        data = data1.append(data2)
    else:
        filename = user + ".log"
        data = pandas.read_csv(filename)
    summa = data["bytes"].sum()
    if summa >= 1048576:
        if summa >= 1073741824:
            summa = str(round(summa / 1073741824, 2)) + " Гб"
        else:
            summa = str(round(summa / 1048576, 2)) + " Мб"
    else:
        summa = str(round(summa / 1024, 2)) + "Кб"
    times = data["attime"].sum()
    times = datetime.datetime.fromtimestamp(times)
    times = str(times.day - 1) + " д., " + str(times.hour) + " ч., " + str(times.minute) + " мин."
    return {"sum": summa, "time": times}
    pass

@dp.message_handler(commands="start", state='*')
async def start(message: types.Message, state: FSMContext):
    start_buttons = ["Валерич", "Василич", "Романыч"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    asyncio.create_task(main())
    await message.answer("Ты кто?", reply_markup=keyboard)
    await state.set_state(you_name.username.state)




@dp.message_handler(Text(equals="трафик", ignore_case=True), state="*")
async def get_info(message: types.Message, state: FSMContext):
    user = await state.get_data()
    if not user == {}:
        text = get_trafic(user['username'])
        await message.answer(f"потрачено: {text['sum']}\nза {text['time']}")


@dp.message_handler(state=you_name.username)
async def get_user(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(username=name)
    start_buttons = ["трафик"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer(f"жми \"трафик\", {name}", reply_markup=keyboard)


async def main():
    while True:
        await asyncio.sleep(20)
        DLink_data.main()


def main_start():
    executor.start_polling(dp)

