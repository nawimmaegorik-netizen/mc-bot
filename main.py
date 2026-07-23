import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# ================= НАСТРОЙКА БОТА =================
BOT_TOKEN = "8747034188:AAFF2fVYIk8E3qr_laG5xkOKaw2OQEyQDjw"
ADMIN_GROUP_ID = -5339298513  # Сюда ID твоей группы (с минусом)
OWNER_ID = 5623311021  # Сюда твой личный Telegram ID
OWNER_USERNAME = "@BICXARZ"  # Твой юзернейм для связи
# ==================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для анкеты
class Form(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()

@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    if message.chat.id == OWNER_ID:
        await message.answer("Привет, Создатель! Ты зашел как Админ. Сюда будут приходить анкеты игроков в твою группу.")
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Подать заявку", callback_data="start_anketa")]
        ])
        await message.answer("Привет! Это бот набора администрации для нашего Minecraft Java сервера. Нажми кнопку ниже, чтобы начать заполнение анкеты.", reply_markup=kb)

@dp.callback_query(F.data == "start_anketa")
async def start_anketa(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Вопрос 1: Напиши свой ник в Майнкрафте и твой возраст.")
    await state.set_state(Form.q1)

@dp.message(Form.q1)
async def process_q1(message: Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await message.answer("Вопрос 2: Сколько времени (часов в день) ты готов уделять серверу?")
    await state.set_state(Form.q2)

@dp.message(Form.q2)
async def process_q2(message: Message, state: FSMContext):
    await state.update_data(q2=message.text)
    await message.answer("Вопрос 3: Был ли у тебя опыт администрирования? Если да, то где?")
    await state.set_state(Form.q3)

@dp.message(Form.q3)
async def process_q3(message: Message, state: FSMContext):
    await state.update_data(q3=message.text)
    data = await state.get_data()
    await state.clear()

    await message.answer("Спасибо! Твоя анкета отправлена на проверку администрации. Ожидай ответа.")

    # Проверяем, есть ли у игрока @username
    user_username = f"@{message.from_user.username}" if message.from_user.username else "Не установлен юзернейм"

    # Формируем текст анкеты для группы с юзером игрока
    anketa_text = (
        f"📝 **Новая заявка в админы!**\n\n"
        f"👤 **Игрок:** {message.from_user.mention_html()}\n"
        f"🔗 **Юзернейм для связи:** {user_username}\n"
        f"🆔 **ID игрока:** `{message.from_user.id}`\n\n"
        f"1️⃣ **Ник и возраст:** {data['q1']}\n"
        f"2️⃣ **Время на сервере:** {data['q2']}\n"
        f"3️⃣ **Опыт работы:** {data['q3']}"
    )

    # Кнопки для группы админов
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{message.from_user.id}")
        ]
    ])

    await bot.send_message(chat_id=ADMIN_GROUP_ID, text=anketa_text, reply_markup=admin_kb, parse_mode="HTML")

# Обработка кнопок Принять / Отклонить в группе
@dp.callback_query(F.data.startswith("accept_"))
async def accept_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    try:
        # Отправляем сообщение игроку со ссылкой на твой юзернейм
        await bot.send_message(chat_id=user_id, text=f"🎉 **Поздравляем!** Твоя анкета успешно одобрена. Для получения прав свяжись с создателем сервера: {OWNER_USERNAME}")
        await callback.message.edit_text(callback.message.text + "\n\n🟢 **Вердикт: ПРИНЯТ**", reply_markup=None, parse_mode="HTML")
    except Exception:
        await callback.answer("Не удалось отправить сообщение игроку (возможно, бот заблокирован).", show_alert=True)

@dp.callback_query(F.data.startswith("reject_"))
async def reject_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    try:
        await bot.send_message(chat_id=user_id, text="❌ **К сожалению**, твоя анкета была отклонена. Попробуй подать заявку позже.")
        await callback.message.edit_text(callback.message.text + "\n\n🔴 **Вердикт: ОТКЛОНЕН**", reply_markup=None, parse_mode="HTML")
    except Exception:
        await callback.answer("Не удалось отправить сообщение игроку.", show_alert=True)

async def main():
    print("Бот запущен и работает...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
      
