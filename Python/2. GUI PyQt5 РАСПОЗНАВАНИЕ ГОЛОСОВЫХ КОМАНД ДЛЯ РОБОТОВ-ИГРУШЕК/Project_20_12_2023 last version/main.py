__version__ = "0.0.1"

import sys
from run import MyWindow
from PyQt5.QtWidgets import QApplication

# Запуск приложения при выполнении скрипта
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())