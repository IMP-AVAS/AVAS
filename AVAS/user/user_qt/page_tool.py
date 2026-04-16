from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGridLayout, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QCheckBox, QMessageBox
from user.user_qt.page_plophase import PagePlotphase
class PageTool(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        group_box1 = QGroupBox("")
        group_box2 = QGroupBox("")
        group_box3 = QGroupBox("")
############################
        #第一列
        layout_box1 = QVBoxLayout()

        btn_avasplot = QPushButton("AVASPlot")
        btn_avasplot.clicked.connect(self.btn_avasplot_start)

        layout_box1.addWidget(btn_avasplot)
        layout_box1.addStretch(1)

        group_box1.setLayout(layout_box1)


######################
        layout.addWidget(group_box1)
        layout.addWidget(group_box2)
        layout.addWidget(group_box3)
        self.setLayout(layout)

    def updatePath(self, new_path):
        self.project_path = new_path

    def btn_avasplot_start(self):
        self.avasplot_window = PagePlotphase(self.project_path)
        self.avasplot_window.show()

import sys
from PyQt5.QtWidgets import QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    project_path = None
    win = ToolPage(project_path)

    win.resize(700, 500)
    win.show()
    sys.exit(app.exec_())