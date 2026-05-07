import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFrame, QLabel, QCheckBox, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt


class AccordionItem(QWidget):
    def __init__(self, title, content_widget):
        super().__init__()

        self.title = title

        self.button = QPushButton(title)
        self.button.setCheckable(True)
        self.button.setChecked(False)
        self.button.setStyleSheet("""
            QPushButton {
                text-align: left;
                font-size: 18px;
                padding: 4px;
                border: 1px solid gray;
                background-color: #f5f5f5;
            }
            QPushButton:checked {
                background-color: #e8e8e8;
            }
        """)

        self.content = QFrame()
        self.content.setFrameShape(QFrame.StyledPanel)
        self.content.setVisible(False)

        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(20, 10, 10, 10)
        content_layout.addWidget(content_widget)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.button)
        layout.addWidget(self.content)

    def set_expanded(self, expanded: bool):
        self.button.setChecked(expanded)
        self.content.setVisible(expanded)

    def is_expanded(self):
        return self.button.isChecked()


class Accordion(QWidget):
    def __init__(self):
        super().__init__()

        self.items = []

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_item(self, title, content_widget):
        item = AccordionItem(title, content_widget)
        self.items.append(item)
        self.layout.addWidget(item)

        item.button.clicked.connect(lambda checked, current=item: self.on_item_clicked(current))

    def on_item_clicked(self, clicked_item):
        for item in self.items:
            if item is clicked_item:
                item.set_expanded(True)
            else:
                item.set_expanded(False)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Accordion Example")
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        accordion = Accordion()

        # 第一项内容
        content1 = QWidget()
        layout1 = QVBoxLayout(content1)

        layout1.addWidget(QLabel("Use 'Gas' command in your structure file"))

        cb1 = QCheckBox("Gas stripping")
        cb2 = QCheckBox("Gas scattering")
        cb3 = QCheckBox("Magnetic stripping")

        layout1.addWidget(cb1)
        layout1.addWidget(cb2)
        layout1.addWidget(cb3)
        layout1.addStretch()

        accordion.add_item("Partran Scattering and Stripping", content1)

        # 第二项内容
        content2 = QWidget()
        layout2 = QVBoxLayout(content2)
        layout2.addWidget(QLabel("这里放 Energy and Phase limits 的设置内容"))
        layout2.addWidget(QCheckBox("Enable energy limit"))
        layout2.addWidget(QCheckBox("Enable phase limit"))
        accordion.add_item("Partran Energy and Phase limits for ( Emittances, losses, Density file )", content2)

        # 第三项内容
        content3 = QWidget()
        layout3 = QVBoxLayout(content3)
        layout3.addWidget(QLabel("这里放输出文件设置"))
        accordion.add_item("Distribution output file (PLT) and Losses file (losses_PAR.dat)", content3)

        # 第四项内容
        content4 = QWidget()
        layout4 = QVBoxLayout(content4)
        layout4.addWidget(QLabel("这里放 Partran options 设置"))
        accordion.add_item("Partran options", content4)

        # 第五项内容
        content5 = QWidget()
        layout5 = QVBoxLayout(content5)
        layout5.addWidget(QLabel("这里放 Toutatis Options 设置"))
        accordion.add_item("Toutatis Options", content5)

        # 第六项内容
        content6 = QWidget()
        layout6 = QVBoxLayout(content6)
        layout6.addWidget(QLabel("这里放 Multi-Threading 设置"))
        accordion.add_item("Multi-Threading", content6)

        accordion.layout.addStretch()

        scroll.setWidget(accordion)
        main_layout.addWidget(scroll)

        # 默认展开第一项
        accordion.items[0].set_expanded(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())