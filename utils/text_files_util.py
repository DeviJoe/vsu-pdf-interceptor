def read_text_file(file_path):
    try:
        f = open(file_path, 'r', encoding='utf-8')
        text = f.read()
        f.close()
        return text
    except FileNotFoundError:
        print("Файл не найден")
    except:
        print("Ошибка при чтении файла!")