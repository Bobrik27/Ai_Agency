# -*- coding: utf-8 -*-
import sys
import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# --- WINDOWS FIX (ОБЯЗАТЕЛЬНО) ---
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Загрузка переменных
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояния для калькулятора
class CalcStates(StatesGroup):
    waiting_for_first_number = State()
    waiting_for_operation = State()
    waiting_for_second_number = State()

# Клавиатура операций
kb_operations = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="+"), KeyboardButton(text="-")],
        [KeyboardButton(text="*"), KeyboardButton(text="/")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Я бот-калькулятор.\nВведите первое число:")
    await state.set_state(CalcStates.waiting_for_first_number)

@dp.message(CalcStates.waiting_for_first_number)
async def process_first_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Это не число. Попробуйте еще раз.")
        return
    await state.update_data(first_number=int(message.text))
    await message.answer("Выберите действие:", reply_markup=kb_operations)
    await state.set_state(CalcStates.waiting_for_operation)

@dp.message(CalcStates.waiting_for_operation)
async def process_operation(message: types.Message, state: FSMContext):
    if message.text not in ['+', '-', '*', '/']:
        await message.answer("Выберите действие из кнопок.")
        return
    await state.update_data(operation=message.text)
    await message.answer("Введите второе число:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CalcStates.waiting_for_second_number)

@dp.message(CalcStates.waiting_for_second_number)
async def process_second_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Это не число.")
        return
    
    data = await state.get_data()
    num1 = data['first_number']
    op = data['operation']
    num2 = int(message.text)
    
    result = 0
    if op == '+': result = num1 + num2
    elif op == '-': result = num1 - num2
    elif op == '*': result = num1 * num2
    elif op == '/': 
        if num2 == 0: result = "Ошибка (деление на 0)"
        else: result = num1 / num2
        
    await message.answer(f"Результат: {result}")
    await message.answer("Введите /start чтобы начать заново.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())