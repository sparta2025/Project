import json
import pyaudio
from vosk import Model, KaldiRecognizer
from PyQt5.QtCore import pyqtSignal, QThread

class voiceRecognitionThread(QThread):
    recognition_complete = pyqtSignal(str)

    def __init__(self, model_name=None, start_words=None, stop_words=None, parent=None):
        super().__init__(parent)

        # Инициализация параметров потока распознавания речи
        self.model_name = model_name
        self.startWords = start_words
        self.stopWords = stop_words
        self.is_active = False

    def run(self):
        # Инициализация модели распознавания и аудиозаписи
        model = Model(self.model_name)
        rec = KaldiRecognizer(model, 16000)
        p = pyaudio.PyAudio()

        # Открытие аудиопотока для записи
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()
        self.is_active = True

        # Цикл записи и распознавания аудиоданных
        while self.is_active:
            data = stream.read(4000, exception_on_overflow=False)
            if (rec.AcceptWaveform(data)) and (len(data) > 0):
                answer = json.loads(rec.Result())
                if answer['text']:
                    # Эмитирование сигнала с распознанным текстом
                    self.recognition_complete.emit(answer['text'])
        else:
            # Остановка и закрытие аудиопотока после завершения цикла
            stream.stop_stream()
            stream.close()

    def stop(self):
        # Метод для остановки потока
        self.is_active = False
        self.wait()  # Ожидание завершения потока перед возвратом