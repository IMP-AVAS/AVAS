from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTabWidget
import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.btn1 = QPushButton("页面 1")
        self.btn2 = QPushButton("页面 2")

        self.tabs = QTabWidget()
        self.tabs.tabBar().hide()

        self.tabs.addTab(QLabel("这是页面 1"), "page1")
        self.tabs.addTab(QLabel("这是页面 2"), "page2")

        layout = QVBoxLayout(self)
        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.tabs)

        self.btn1.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        self.btn2.clicked.connect(lambda: self.tabs.setCurrentIndex(1))


app = QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec_())