
1. Исследуется задача классификации.
	Тип классификации – по каталогам.
	В исследовательских целях используются смешанные данные – картинки и фотографии:
		Рассматриваются различные архитектуры рукописных сетей, а также рассмотрены предобученные сети для примера.
		11 классов по 2000 фотографий и картинок размером 224х224х3 - 22 000 исходных данных для обучения.

2. Использование фреймворка GUI PyQt5 в вопросах интеграции модели Speech-to-Text vosk проекта 
	Стажировка: РАСПОЗНАВАНИЕ ГОЛОСОВЫХ КОМАНД ДЛЯ РОБОТОВ-ИГРУШЕК 

3. Интеграция Rest API разворачивание синхронного сервера Flask на сервисе Yandex Cloud.

4. Интеграция модели нейронной сети с социальной сетью Telegram. Рассматривается задача классификации стоек карате - 11 классов.
	В качестве модели использовалась рукописная модель с архитектурой ResNet. DataSet содержит 2000 картинок на класс - 
	всего 22 000 картинок размером 224х224x3 пикселей.
	
5. Фреймворк PyTorch. Object Detection пример на синтетических данных:
	Пример использования фреймворка PyTorch. Используются синтетические данные - 4 класса: фон, треугольник, квадрат, круг. 
	Используемый метод Object Detection на предобученной модели fasterrcnn_resnet50_fpn, дообучение модели на синтетических данных.

6. Фреймворк PyTorch. Классификация музыкальных жанров:
	Фреймворк PyTorch. Классификация музыкальных жанров. Всего десять жанров. Создание DataSet по жанрам на основе 
	Мэл спектрограмм, создание классификатора (модели), обучение и оценка.
	
7. WEB интерфейс, использование FastAPI, работа с сервисом ACRCloud, моделью ИИ GigaChat, сервисом Yandex TTS:
	Основная идея - загружаем звуковой трек через WEB интерфейс, загружаем на сервис ACRCloud и получаем информацию о треке 
	(исполнитель, жанр, альбом и т.д.), используя модель ИИ GigaChat генерируем историю, 
	используя сервис Yandex TTS преобразуем текст в речь. Написано на языке Python с использованием фреймворка FastAPI, 
	асинхронной модели передачи данных, связи с сервисами и моделями по API.