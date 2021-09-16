from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


def cancel_kb():
    btn_auto = KeyboardButton('Определить автоматически')
    btn_cancel = KeyboardButton('Отмена скачивания презентации')
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(btn_auto)
    kb.add(btn_cancel)
    return kb


def prompt_kb():
    btn_yes = KeyboardButton('Да')
    btn_no = KeyboardButton('Нет')
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(btn_yes, btn_no)
    return kb


def main_kb():
    btn_about = KeyboardButton('О боте')
    btn_ocr = KeyboardButton('Распознать презентацию')
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(btn_about)
    kb.add(btn_ocr)
    return kb
