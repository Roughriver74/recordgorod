from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Установка окна
        self.setWindowTitle('Recorder')
        self.setStyleSheet("background-color: #1e1e1e;")
        self.setFixedSize(300, 400)

        # Лейбл с названием приложения
        label = QLabel('Recorder', self)
        label.setFont(QFont('Arial', 20))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignCenter)

        # Кнопка записи
        record_button = QPushButton('●', self)
        record_button.setFont(QFont('Arial', 36))
        record_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #ff5555;
                border-radius: 50px;
                width: 100px;
                height: 100px;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        record_button.setFixedSize(100, 100)
        record_button.setCursor(Qt.PointingHandCursor)

        # Основной макет
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(record_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
