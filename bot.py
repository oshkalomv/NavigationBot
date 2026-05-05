import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import re

TOKEN = "your-bot-token"

bot = Bot(token=TOKEN)
dp = Dispatcher()

teachers = [
    'Актовый зал', 'Андреева ГС (ИНЯЗ)', 'Антипова ДЛ (МАТ)', 'Ахадова ТЕ (ИНЯЗ)', 'Библиотека',
    'Болотова АВ (советник)', 'Большой спортивный зал', 'Булычева АМ (ИНФ)', 'Вагапова НР (МАТ)', 'Ваньков АА (ХИМ)',
    'Ганичева ЕШ (ИНЯЗ)', 'Гридина ЕГ (МАТ)', 'Дианова ИВ (РУССЯЗ)', 'Дмитриева ВЕ (ФИЗ)', 'Ермолаева АЕ (педорг)',
    'Иванова ИА (соц.педорг)', 'Ивашкова НД (секретарь)', 'Коваленко МИ (ТЕХ)', 'Королева ЮА (БИО)', 'Кудинова АВ (ИНЯЗ)',
    'Малый спортивный зал', 'Медицинский кабинет', 'Огородова АЮ (МАТ)', 'Оленева АЮ (РУССЯЗ)',
    'Ответственный по питанию и картам', 'Петрова  ВА (ИНФ)', 'Петрушина МН (РУССЯЗ)', 'Сергеева АВ (МАТ)', 'Соколова НВ (директор)',
    'Соловьева АЛ (РУССЯЗ)', 'Стешенок ИГ (ИНЯЗ)', 'Столовая', 'Суркова ИА (ИСТ)', 'Тищенко АВ (ИНФ)', 'Турина НС (ИНЯЗ)', 'Филина ЕА(РУССЯЗ)',
    'Хаперскова ЮН (ИЗО)', 'Шукшина ЕИ (ИСТ)', 'Бородкин АО (ИСТ)', 'Маматкулов АХ (ГЕОГР)'
]

START_PHOTO = "start_photo.png"
NO_PHOTO = "no_photo.png"


lessons = [
    "Математика", "Русский язык/литература", "Физика", "География", "Информатика",
    "Иностранный язык", "Химия", "Биология", "История/Обществознание", "Технология", "ИЗО", "Другое"
]


lesson_teacher_map = {

    "Математика": [2, 8, 11, 22, 27],
    "Русский язык/литература": [12, 23, 26, 29, 35],
    "Физика": [13],
    "География": [39],
    "Информатика": [7, 25, 33],
    "Иностранный язык": [1, 3, 10, 19, 30, 34],
    "Химия": [9],
    "История/Обществознание": [32, 37, 38],
    "Технология": [17],
    "ИЗО": [36],
    "Биология": [18],
    "Другое": [0, 4, 5, 6, 14, 15, 16, 20, 21, 24, 28, 31]


}


def build_lessons_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for lesson in lessons:
        kb.button(text=lesson, callback_data=f"lesson_{lesson}")
    kb.adjust(2)
    return kb.as_markup()

def build_teachers_kb_for_lesson(lesson: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    teacher_indexes = lesson_teacher_map.get(lesson, [])
    for idx in teacher_indexes:
        if 0 <= idx < len(teachers):
            kb.button(text=teachers[idx], callback_data=f"teacher_{idx}")
    kb.button(text="Назад", callback_data="back_to_lessons")
    kb.adjust(2)
    return kb.as_markup()


@dp.message(Command("start"))
async def start_handler(message: Message):
    photo = FSInputFile(START_PHOTO)
    await message.answer_photo(photo=photo, caption="Выберите урок:", reply_markup=build_lessons_kb())

@dp.callback_query(F.data.startswith("lesson_"))
async def lesson_handler(callback: CallbackQuery):
    lesson = callback.data[len("lesson_"):]
    await callback.message.edit_caption(
        caption=f"Учителя, ведущие: {lesson}",
        reply_markup=build_teachers_kb_for_lesson(lesson)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("teacher_"))
async def teacher_handler(callback: CallbackQuery):
    index = int(callback.data.split("_")[1])
    name = teachers[index]

    photo_path = NO_PHOTO
    for ext in (".png", ".jpg", ".jpeg"):
        candidate = f"{name}{ext}"
        if os.path.exists(candidate):
            photo_path = candidate
            break

    photo = FSInputFile(photo_path)

    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_to_lessons")
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo, caption=name),
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_lessons")
async def back_to_lessons_handler(callback: CallbackQuery):
    photo = FSInputFile(START_PHOTO)
    await callback.message.edit_media(
        media=InputMediaPhoto(media=photo),
        reply_markup=build_lessons_kb()
    )
    await callback.answer()


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
