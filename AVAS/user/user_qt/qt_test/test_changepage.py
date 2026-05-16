#该文件为切换页面

# self.tabs = QTabWidget()
# self.tabs.tabBar().hide()

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLabel, QStackedLayout
)
import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.btn1 = QPushButton("页面 1")
        self.btn2 = QPushButton("页面 2")

        page1 = QLabel("这是页面 1")
        page2 = QLabel("这是页面 2")

        self.stack_layout = QStackedLayout()
        self.stack_layout.addWidget(page1)
        self.stack_layout.addWidget(page2)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.btn1)
        main_layout.addWidget(self.btn2)
        main_layout.addLayout(self.stack_layout)

        self.btn1.clicked.connect(lambda: self.stack_layout.setCurrentIndex(0))
        self.btn2.clicked.connect(lambda: self.stack_layout.setCurrentIndex(1))


app = QApplication(sys.argv)
w = Window()
w.show()
sys.exit(app.exec_())