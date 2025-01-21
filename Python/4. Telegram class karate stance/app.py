import telebot
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Загрузка модели ResNet
model = load_model('ResNet-Conv2D.ver-23.01.24.qipc-2000_errors-4_224x224x3.h5')

# Определение классов в данной задаче
classes = ['Дзенкуцу Дачи (Zenkutsu Dachi)',
           'Киба Дачи (Kiba Dachi)',
           'Кокутсу Дачи (Kokutsu Dachi)',
           'Мусуби дачи (Musubi Dachi)',
           'Неко Аши Дачи (Neko Ashi Dachi)',
           'Санчин дачи (Sanchin Dachi)',
           'Тсуру Аши Дачи (Tsuru Ashi Dachi)',
           'Хачиджи Дачи (SotoHachiji, Hachiji Dachi)',
           'Хэйко дачи (Heiko Dachi)',
           'Хэйсоку дачи (Heisoku Dachi)',
           'Шико Дачи (Shiko Dachi)']

# Токен Telegram бота
# Инициализация переменных, которые будут хранить значения ключей
TELEGRAM_TOKEN = None
try:
    # Чтение данных из файла
    with open('keys.txt', 'r') as file:
        for line in file:
            # Удаление пробелов и перевод строки
            line = line.strip()
            # Разделение строки на имя ключа и значение
            if line:
                key, value = line.split('=', 1)
                if key == "TELEGRAM_TOKEN":
                    TELEGRAM_TOKEN = value
finally:
    # Проверка, что ключи были прочитаны
    if TELEGRAM_TOKEN: # and OPENAI_API_KEY:
        print("Ключ был успешно прочитан.")
    else:
        print("Ошибка: Не удалось прочитать ключ из файла.")

# Создание объекта бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Этот бот классифицирует изображения с помощью модели ResNet. Пожалуйста, отправь мне изображение.')


# Обработка всех присланных изображений
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        # Получаем информацию о фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Сохраняем фото
        with open("image.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Загружаем и обрабатываем изображение для модели
        img = image.load_img("image.jpg", target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x *= (1.0 / 127.5 - 1.0)
#        x = preprocess_input(x)

        # Предсказываем класс изображения
        preds = model.predict(x)
#       #decoded_preds = decode_predictions(preds, top=3)[0]

        # Отправляем результаты обратно пользователю
        response = "Предсказание:\n"


#        for pred in decoded_preds:
#            response += f"{pred[1]}: {pred[2] * 100:.2f}%\n"

        response += classes[np.argmax(preds)]

        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")


# Запуск бота
bot.polling()