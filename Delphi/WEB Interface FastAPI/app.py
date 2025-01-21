import io
import base64
from numpy import argmax
from PIL import Image
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model

from flask import Flask, request, jsonify, abort, render_template


# Определение словаря classes
classes = [
      "Дзенкуцу Дачи (Zenkutsu Dachi)",
      "Киба Дачи (Kiba Dachi)",
      "Кокутсу Дачи (Kokutsu Dachi)",
      "Мусуби дачи (Musubi Dachi)",
      "Неко Аши Дачи (Neko Ashi Dachi)",
      "Санчин дачи (Sanchin Dachi)",
      "Тсуру Аши Дачи (Tsuru Ashi Dachi)",
      "Хачиджи Дачи (SotoHachiji, Hachiji Dachi)",
      "Хэйко дачи (Heiko Dachi)",
      "Хэйсоку дачи (Heisoku Dachi)",
      "Шико Дачи (Shiko Dachi)"
      ]

app = Flask(__name__)

model = None

# Распознаем класс входящей картинки img
def predict_class_image(img):
  try:
    # Создать временную папку

    # Получаем текущую директорию, где находится скрипт
    current_directory = os.getcwd()

    # Имя новой папки
    folder_name = "temp"
    folder_class = "temp"

    # Полный путь к новой папке
    temp_dir = os.path.join(current_directory, folder_name)
    temp_dir_img = os.path.join(current_directory, folder_name, folder_class)

    # Создаем папку, если она еще не существует
    if not os.path.exists(temp_dir_img):
            os.makedirs(temp_dir_img)

    # Входящее изображение перемещаем во временную папку
    # Полный путь к целевому месту перемещения изображения
    target_path = os.path.join(temp_dir_img, 'temp_img.jpg')

    try:
        img.save(target_path)
    except Exception as e:
        return 'Ошибка при сохранение изображения: ' + str(e) 

    # Распознаем класс изображения
    test_datagen = ImageDataGenerator(rescale = 1.0/255.0)  # Предполагая, что вы использовали нормализацию [0, 1] во время обучения

    test_generator = test_datagen.flow_from_directory(
      directory = temp_dir,
      target_size = (227, 227),
      batch_size = 1,  # Укажите 1, так как у вас одиночное изображение
      color_mode = "rgb",
      class_mode = None,  # Используйте None для классификации
      shuffle = False  # Не перемешивать данные
      )

    try:
        # Выполнение предсказания на CPU
        with tf.device('/CPU:0'):
          predictions = model.predict(test_generator, verbose = 1)
    except Exception as e:
        return 'Ошибка при распознавании класса: ' + str(e)         

    predicted_class_idx = argmax(predictions[0])
    predicted_label = classes[predicted_class_idx]

    return predicted_label
  except request.exceptions.RequestException as e:    
    return 'Ошибка метода predict_class_image()' + ' ' + e 

# Рендерим файл index.html
@app.route("/", methods=['GET', 'POST'])
def render_index():
  try:
    return render_template('index.html')
  except Exception as e:
    # Здесь можно залогировать исключение для отладки
    print(str(e))
    return "Internal Server Error", 500

# Обрабатываем из WEB-интерфейса
@app.route("/predict_html", methods=['POST'])
def predict_html_method():
    try:
        if not request.json or 'image' not in request.json:
            abort(400)               

        # Получаем изображение из запроса
        #img_bytes = request.files['image'] #.read()

        # get the base64 encoded string
        im_b64 = request.json['image']

        # convert it into bytes
        img_bytes = base64.b64decode(im_b64.encode('utf-8'))

        # Преобразуем байты изображения в объект PIL Image
        try:
            img = Image.open(io.BytesIO(img_bytes))
        except Exception as e:
            return 'Ошибка при открытии изображения: ' + str(e) 
    
    except request.exceptions.RequestException as e:    
        return 'Ошибка метода predict_html_method()' + ' ' + e
    
    return predict_class_image(img)

# Обрабатываем из локального интерфейса Delphi + python4delphi
@app.route("/predict", methods=['POST'])
def predict_method():
    try:
        if not request.json or 'image' not in request.json:
            abort(400)

        # get the base64 encoded string
        im_b64 = request.json['image']

        # convert it into bytes
        img_bytes = base64.b64decode(im_b64.encode('utf-8'))

        # convert bytes data to PIL Image object
        try:
            img = Image.open(io.BytesIO(img_bytes))
        except Exception as e:
            return 'Ошибка при открытии изображения: ' + str(e)
    except request.exceptions.RequestException as e:    
        return 'Ошибка метода predict_method()' + ' ' + e

    return predict_class_image(img)

# Загрузка модели при старте VM
def load_model_start(load_path):
    global model
    try:
        model = tf.keras.models.load_model(load_path)
    except Exception as e:
      model = None

    return model

# Запуск сервера Flask либо на предустановленном порту, либо на адресе 8000
def run_server_api():
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port, debug = False)


if __name__ == "__main__":    
    load_path = "ResNet-Conv2D.ver-16.2.4.qipc-562_errors-1.h5"
    model = load_model_start(load_path) # Загрузка модели при инициализации контейнера

    run_server_api()