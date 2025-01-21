from VoiceRecognitionThread import voiceRecognitionThread

from PyQt5.QtWidgets import QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSignal

class CustomToolButton(QToolButton):
    # Добавляем собственный сигнал clicked
    custom_clicked = pyqtSignal()

    def __init__(self, in_thread=None, parent=None):
        super().__init__(parent)

        self.voiceRecognitionThread = in_thread
        self.init_ui()

    def init_ui(self):
        # Устанавливаем иконку на кнопку
        icon = QIcon("microphone.png")
        self.setIcon(icon)

        # Устанавливаем размер иконки (по желанию)
        self.setIconSize(icon.actualSize(QSize(40, 40)))

        # Устанавливаем стиль для круглой кнопки
        self.setStyleSheet("QToolButton { border-radius: 20px; }")

    def enterEvent(self, event):
        # Изменение иконки при наведении
        if not self.voiceRecognitionThread.is_active:
            icon = QIcon("microphoneOn.png")
            self.setIcon(icon)
        else:
            icon = QIcon("microphoneActive.png")
            self.setIcon(icon)

    def leaveEvent(self, event):
        # Возврат к иконке по умолчанию при выходе мыши
        if not self.voiceRecognitionThread.is_active:
            icon = QIcon("microphone.png")
            self.setIcon(icon)
        else:
            icon = QIcon("microphoneActive.png")
            self.setIcon(icon)

    def mousePressEvent(self, event):
        # Изменение иконки при нажатии
        icon = QIcon("microphonePress.png")
        self.setIcon(icon)

    def mouseReleaseEvent(self, event):
        # Возврат к иконке по умолчанию после отпускания кнопки
        #if self.voiceRecognitionThread.isRunning():
        if not self.voiceRecognitionThread.is_active:
            icon = QIcon("microphoneOn.png")
            self.setIcon(icon)
        else:
            icon = QIcon("microphoneActive.png")
            self.setIcon(icon)

        self.custom_clicked.emit()