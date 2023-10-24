import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget,\
    QMainWindow, QPlainTextEdit, QLayout, QVBoxLayout, QLabel,\
    QLineEdit
from PyQt5.QtCore import QSize, Qt
import timer
import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.time = ''
    #     self.textcontent = ''
        self.setWindowTitle('something')
        self.label = QPlainTextEdit()

        self.button = QPushButton()
        # self.input.textChanged.connect(self.label.setPlainText)
        self.button.clicked.connect(self.the_button_was_clicked)
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
    #     self.button = QPushButton('me again')
    #     self.button.setCheckable(True)
    #     self.button.clicked.connect(self.the_button_was_clicked)
    #     # self.setFixedSize(QSize(400,300))
    #     self.text = QPlainTextEdit()
    #
    #     # self.text2 = QPlainTextEdit()
    #
    #     # self.layout = QVBoxLayout()
    #     # self.layout.addWidget(self.button)
    #     # self.layout.addWidget(self.text)
    #     # self.setLayout(self.layout)
    #     self.setCentralWidget(self.button)
    #     # self.setCentralWidget(self.text2)
    def the_button_was_clicked(self):
        self.time = str(datetime.datetime.now())
        self.label.setPlainText(self.time)




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()