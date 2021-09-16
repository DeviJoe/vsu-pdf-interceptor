import os
import dotenv
import random
import string
import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode, ContentType, ReplyKeyboardRemove
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils import text_files_util
from service import interceptor
import logging
import keyboards

dotenv.load_dotenv()


class PresData(StatesGroup):
    name = State()
    ocr = State()


logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.environ['API_TOKEN'])
states = MemoryStorage()
dp = Dispatcher(bot, storage=states)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    text = text_files_util.read_text_file("./markdown_text/start.md")
    await msg.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.main_kb())


@dp.message_handler(commands=['about'])
async def about(msg: types.Message):
    text = text_files_util.read_text_file("./markdown_text/about.md")
    await msg.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboards.main_kb())


@dp.message_handler(regexp='https://bbb')
async def gen_pdf(msg: types.Message, state: FSMContext):
    res = requests.get(msg.text)
    if res.status_code != 200:
        await msg.answer('Ссылка недействительна! Проверьте корректность введенной ссылки')
        return
    async with state.proxy() as data:
        data['url'] = msg.text.lower()
    await PresData.name.set()
    await msg.answer('Пожалуйста, введите название для презентации или нажмите кнопку отмены, '
                     'чтобы название было сгенерировано автоматически', reply_markup=keyboards.cancel_kb())


def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for _ in range(length))
    return rand_string


@dp.message_handler(state=PresData.name)
async def get_name(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'определить автоматически':
        name = generate_random_string(16)
    elif msg.text.lower() == 'отмена скачивания презентации':
        await state.finish()
        await msg.answer('Работа с презентацией отменена', reply_markup=ReplyKeyboardRemove())
        return
    else:
        name = msg.text
    async with state.proxy() as data:
        data['name'] = name
        await msg.answer('Требуется ли распознать текст в pdf?', reply_markup=keyboards.prompt_kb())
        await PresData.ocr.set()


@dp.message_handler(lambda message: message.text in ['Да', 'Нет'], state=PresData.ocr)
async def get_ocr(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if msg.text.lower() == 'да':
            data['ocr'] = True
        elif msg.text.lower() == 'нет':
            data['ocr'] = False

    await msg.answer("Начато скачивание презентации с серверов "
                     "Moodle VSU, ожидайте", reply_markup=ReplyKeyboardRemove())
    interceptor.get_pdf_from_moodle(data['url'], data['name'])
    await msg.answer('Скачивание презентации завершено! Презентация формируется, ожидайте')
    await msg.answer_document(open('./generated_pdf/' + data['name'] + '.pdf', 'rb'))

    if data['ocr']:
        try:
            await msg.answer(
                'Начато распознавние текста в презентации, ожидайте, процесс может занять длительное время')
            interceptor.ocr_pdf('./generated_pdf/' + data['name'] + '.pdf',
                                './generated_pdf/' + data['name'] + '_ocr.pdf')
            await msg.answer('Завершено! Ожидайте получение файла')
            await msg.answer_document(open('./generated_pdf/' + data['name'] + '_ocr.pdf', 'rb'))
        except:
            await msg.answer('Непредвиденная ошибка при распознавании презентации, попробуйте еще раз')
    await msg.answer('Завершено!', reply_markup=keyboards.main_kb())
    await state.finish()


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def ocr_pdf(msg: types.Message):
    doc = msg.document
    doc_name = doc.file_name
    if doc_name[-3:] != 'pdf':
        await msg.answer('Переданный файл не является pdf файлом')
        return
    url = await doc.get_url()
    res = requests.get(url)
    content = res.content
    f = open('./generated_pdf/' + doc_name, 'wb')
    f.write(content)
    try:
        await msg.answer('Начато распознавние текста в презентации, ожидайте, процесс может занять длительное время')
        interceptor.ocr_pdf('./generated_pdf/' + doc_name, './generated_pdf/ocr_' + doc_name)
        await msg.answer('Завершено! Ожидайте получение файла')
        await msg.answer_document(open('./generated_pdf/ocr_' + doc_name, 'rb'))
        await msg.answer('Завершено!', reply_markup=keyboards.main_kb())
    except:
        await msg.answer('Непредвиденная ошибка при распознавании презентации, попробуйте еще раз')
    f.close()


@dp.message_handler(commands=['/clear'])
async def clear(msg: types.Message):
    os.system("sudo rm -r ./generated_pdf")
    await msg.answer("Папка очищена!")


@dp.message_handler(content_types=ContentType.TEXT)
async def handler(msg: types.Message):
    if msg.text.lower() == 'о боте':
        await about(msg)
    else:
        await msg.answer('Ссылка недействительна :(')


if __name__ == '__main__':
    executor.start_polling(dp)
