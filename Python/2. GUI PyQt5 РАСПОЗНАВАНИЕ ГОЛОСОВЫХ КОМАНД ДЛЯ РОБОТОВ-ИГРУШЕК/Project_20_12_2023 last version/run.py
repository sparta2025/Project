# Импорт необходимых модулей и библиотек
import sys
from VoiceRecognitionThread import voiceRecognitionThread
from CustomToolButton import CustomToolButton
from utils4kotlin import russian_words_to_number, russian_words_to_number_code
from utils4kotlin import replace_commands, get_current_command
import MapOfCommands
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSplitter, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Определение класса окна приложения
class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация переменных и параметров
        self.thread = None
        self.model_name = "model-ru"
        self.startWords = MapOfCommands.StartWords
        self.stopWords = MapOfCommands.StopWords

        # Создание экземпляра потока распознавания и подключение сигнала к обработчику
        self.thread = voiceRecognitionThread(model_name=self.model_name, start_words=self.startWords,
                                             stop_words=self.stopWords)
        self.thread.recognition_complete.connect(self.on_recognition_complete)

        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self):
        # Настройка внешнего вида окна
        self.setWindowTitle("Пример интерфейса")

        # Создание вертикального расположения виджетов
        layout = QVBoxLayout()

        # Создание сплиттера
        splitter = QSplitter()
        splitter.setOrientation(Qt.Vertical)

        # Создание текстовых полей
        self.text_edit1 = QTextEdit()
        self.text_edit2 = QTextEdit()

        # Добавление текстовых полей в сплиттер
        splitter.addWidget(self.text_edit1)
        splitter.addWidget(self.text_edit2)

        # Установка начальных размеров текстовых полей
        splitter.setSizes([200, 200])

        # Добавление сплиттера в расположение
        layout.addWidget(splitter)

        # Создание кнопки с пользовательским изображением
        self.tool_button = CustomToolButton(in_thread=self.thread)

        # Подключение функции обработки события к сигналу clicked кнопки
        self.tool_button.custom_clicked.connect(self.on_button_clicked)

        # Добавление кнопки в расположение с выравниванием по центру
        layout.addWidget(self.tool_button, alignment=Qt.AlignCenter)

        # Добавление пустого пространства снизу для размещения кнопки посередине
        layout.addStretch()

        # Установка созданного расположения виджета
        self.setLayout(layout)

    def on_recognition_complete(self, text):
        # Обработка завершения распознавания речи
        if text.lower() in self.stopWords:
            self.text_edit1.append("Прерываемся и идем курить и думу думать...")
            icon = QIcon("microphone.png")
            self.tool_button.setIcon(icon)
            self.thread.is_active = False
            self.thread.stop()  # Остановка потока после распознавания стоп-слова
        elif text.lower() in self.startWords:
            self.text_edit1.append("Приготовимся слушать...")
        else:
            text_ = russian_words_to_number(text)
            text_code = russian_words_to_number_code(text)
            result = get_current_command(text_)
            result_code = get_current_command(text_code)
            result_code = replace_commands(result_code)
            if result != "":
                self.text_edit1.append(result)
                self.text_edit2.append(result_code)

    def on_button_clicked(self):
        # Обработка нажатия пользовательской кнопки
        if self.thread is None or not self.thread.is_active:
            if self.thread is None:
                # Создание нового потока, если он еще не существует
                self.thread = voiceRecognitionThread(model_name=self.model_name, start_words=self.startWords,
                                                     stop_words=self.stopWords)
                self.thread.recognition_complete.connect(self.on_recognition_complete)

            self.text_edit1.append("Приготовимся слушать...")
            self.thread.is_active = True
            self.thread.start()
        else:
            self.text_edit1.append("Прерываемся и идем курить и думу думать...")
            self.thread.is_active = False
            self.thread.stop()  # Остановка существующего потока