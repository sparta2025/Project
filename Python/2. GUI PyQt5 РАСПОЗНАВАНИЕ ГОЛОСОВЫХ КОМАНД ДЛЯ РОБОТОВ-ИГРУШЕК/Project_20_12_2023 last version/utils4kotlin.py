import MapOfCommands 

# Преобразуем часть числа или все число в целое представление
def words_to_int(aWords):
        # Словарь числовый представлений прописи числа до 999
        NUMERIC = {
            'ноль': 0, 'один': 1,  'два': 2,  'три': 3,
            'четыре': 4,  'пять': 5,  'шесть': 6,
            'семь': 7,  'восемь': 8,  'девять': 9,
            'десять': 10,  'одиннадцать': 11,  'двенадцать': 12,
            'тринадцать': 13,  'четырнадцать': 14,  'пятнадцать': 15,
            'шестнадцать': 16,  'семнадцать': 17,  'восемнадцать': 18,
            'девятнадцать': 19,  'двадцать': 20,  'тридцать': 30,
            'сорок': 40,  'пятьдесят': 50,  'шестьдесят': 60,
            'семьдесят': 70,  'восемьдесят': 80,  'девяносто': 90,
            'сто': 100,  'двести': 200,  'триста': 300,
            'четыреста': 400,  'пятьсот': 500,  'шестьсот': 600,
            'семьсот': 700,  'восемьсот': 800,  'девятьсот': 900
            }

        words_lower = aWords.lower()
        words_list = words_lower.split()

        total_number = 0
        current_number = 0
        # Флаг до числа, чтобы определять, что писать перфикс или суфикс
        pref_digit = 1
        pref_digit_str = ""
        suf_digit_str = ""

        for word in words_list:
            if word in NUMERIC:
                current_number += NUMERIC[word]
                pref_digit = 0
            else:
                total_number += current_number
                current_number = 0

                # Возвращаем начало и окончание строки
                if pref_digit == 1:
                    pref_digit_str = pref_digit_str + " " + word
                else:
                    suf_digit_str = suf_digit_str + " " + word

        total_number += current_number
        # Возвращаем число, начало и конец строки без концевыз пробелов
        return total_number, pref_digit_str.strip(), suf_digit_str.strip()

# Преобразуем число прописью в цифровое представление, разделяя на части
def words_to_number(words):
    # Разделяем число на целую и дробную часть
    words_lower = words.lower()
    words_list = words_lower #.split()

    if 'целых' in words_list:
        index_cel = words_list.index('целых')
        integer_part_words = words_list[:index_cel]
        decimal_part_words = words_list[index_cel + 1:]
    else:
        decimal_multiplier = 0
        integer_part_words = words_list
        decimal_part_words = ""

    # Получаем целую и дробную часть числа
    decimal_part = 0
    # Если точка есть, то используем дробную часть, если нет, то просто возвращаем результат
    integer_part, pref_part, suf_part = words_to_int(integer_part_words)
    decimal_part, _, suf_part_end = words_to_int(decimal_part_words)
    
    if (suf_part_end != ""): suf_part = suf_part_end
    return integer_part, decimal_part, pref_part, suf_part
        
        
    
# Преобразуем число прописью в цифровое представление
def russian_words_to_number(words):
    integer_part, decimal_part, pref_part, suf_part = words_to_number(words)
    
    if (decimal_part != 0):
        return pref_part + " " + str(integer_part) + '.' + str(decimal_part) + " " + suf_part
    else:
        if (integer_part != 0):
            return pref_part + " " + str(integer_part) + " " + suf_part
        else:
            return pref_part

        
# Кодируем - обрамляем цифру в коды BB00 ... B00B        
def russian_words_to_number_code(words):
    integer_part, decimal_part, pref_part, suf_part = words_to_number(words)
    
    digit_mapping = MapOfCommands.selectDigit
        
    if (decimal_part != 0):
        return pref_part + " " + digit_mapping[0] + " " + str(integer_part) + '.' + str(decimal_part) + " " + digit_mapping[1] + " " + suf_part
    else:
        if (integer_part != 0):
            return pref_part + " " + digit_mapping[0] + " " + str(integer_part) + " " + digit_mapping[1] + " " + suf_part
        else:
            return pref_part

# Выделяем из строки команду
def get_current_command(text):
    start_words = MapOfCommands.StartWords #["робот", "бот", "тетработ", "тэтработ"]  # Список начала команды роботу
    stop_words = MapOfCommands.StopWords #["стоп", "стой", "отставить", "прекратить"]  # Список стоп слов

    in_command = False  # Флаг, указывающий, что мы находимся внутри команды
    current_command = []  # Список для хранения текущей команды

    # Пройдемся по словам в тексте
    words = text.split(" ")
    for word in words:
        # Если слово является стартовым словом
        if word in start_words:
            in_command = True
            current_command = [word]
        # Если слово является стоп-словом и мы находимся внутри команды
        elif in_command and word in stop_words:
            current_command.append(word)
            in_command = False
            return " ".join(current_command)
        # Если мы находимся внутри команды
        elif in_command:
            current_command.append(word)

    # Если команда не закончена стоп-словом, добавим стоп-слово в конец текущей команды
    if in_command:
        current_command.append(stop_words[0])
        return " ".join(current_command)

    # Если не было найдено ни одного стартового слова, вернем пустую строку
    return ""   

# Вывод команд в виде списка
def get_list_commands(text):
    commands = []  # Инициализируем список для хранения команд
    
    in_command = False  # Флаг, указывающий, что мы находимся внутри команды
    current_command = []  # Список для хранения текущей команды

    # Пройдемся по словам в тексте
    words = text.split()
    for word in words:
        # Если слово является стартовым словом
        if word in StartWords:
            in_command = True
            current_command = [word]
        # Если слово является стоп-словом и мы находимся внутри команды
        elif in_command and word in StopWords:
            current_command.append(word)
            in_command = False
            commands.append(current_command)
        # Если мы находимся внутри команды
        elif in_command:
            current_command.append(word)
    
    # Если не было найдено ни одного стартового слова, вернем пустой список
    if in_command:
        # Если команда не заканчивается стоп-словом, добавим стоп-слово
        current_command.append(StopWords[0])
        commands.append(current_command)
   
    return commands
    # Окончание функции преобразования в список

# Функция для форматирования команды в виде кодов
def replace_commands(input_str):
    command_mapping = MapOfCommands.command_mapping # Словарь команд
    digit_mapping = MapOfCommands.selectDigit # Команды, ограничивающие цифру
    
    words = input_str.split()
    replaced_words = [command_mapping.get(word, word) for word in words if ((word in command_mapping) or (word in [digit_mapping[0], digit_mapping[1]]) or (word.isdigit()))]
    return " ".join(replaced_words)