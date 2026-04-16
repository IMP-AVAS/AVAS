from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QDialog, QCheckBox, QButtonGroup, QMessageBox

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtCore import pyqtSignal
from utils.readfile import read_lattice_mulp
import os
from user.user_qt.page_utils.picture_dialog import Picturewidgetrightkey
from apis.basic_api.api import plot_dataset, plot_phase_ellipse
import sys

from PyQt5.QtCore import pyqtSignal

class PhaseEllipseWidgetbase(Picturewidgetrightkey):
    resize_signal = pyqtSignal()  # 正确初始化自定义信号
    def __init__(self,  ):
        super().__init__()

        self.fig_size = (6.4, 4.6)
        self.fig = Figure(figsize=self.fig_size)  # 创建figure对象
        self.picture_type = "xx1"

    def plot_image(self):
        pass
    def plot_image2(self):

        if not self.twiss_parameter:
            pass
        else:
            if self.picture_type == "xx1":
                parameter_item = {
                    "alpha": self.twiss_parameter["alpha_x"],
                    "beta": self.twiss_parameter["beta_x"],
                    "rms_emit": self.twiss_parameter["rms_emit_x"],

                }

            elif self.picture_type == "yy1":
                parameter_item = {
                    "alpha": self.twiss_parameter["alpha_y"],
                    "beta": self.twiss_parameter["beta_y"],
                    "rms_emit": self.twiss_parameter["rms_emit_y"],

                }


            elif self.picture_type == "zz1":
                parameter_item = {
                    "alpha": self.twiss_parameter["alpha_z"],
                    "beta": self.twiss_parameter["beta_z"],
                    "rms_emit": self.twiss_parameter["rms_emit_z"],
                }


            plot_phase_ellipse(parameter_item, self.picture_type, show_=0, fig=self.fig)


            self.canvas.draw()


    def change_twiss_parameter(self, new_twiss_parameter):
        self.twiss_parameter = new_twiss_parameter
        self.plot_image2()


    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        menu_items = {

            "xx1": cmenu.addAction("X-X'"),
            "yy1": cmenu.addAction("Y-Y'"),
            "zz1": cmenu.addAction("Z-Z'"),
            "xy": cmenu.addAction("X-Y"),
            "phiw": cmenu.addAction("Φ-W"),


        }

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        for item_name, menu_item in menu_items.items():
            if action == menu_item:
                self.picture_type = item_name
                break
        self.fig.clf()
        self.plot_image2()



class PhaseEllipseWidget(QDialog):
    closed = pyqtSignal()
    def __init__(self, ):
        super().__init__()


        # 创建 4 个 Picturewidgetrightkey 实例
        self.widgets = [
            PhaseEllipseWidgetbase(),
            PhaseEllipseWidgetbase(),
            PhaseEllipseWidgetbase(),
            PhaseEllipseWidgetbase(),
        ]
        self.widgets[0].picture_type = "xx1"
        self.widgets[1].picture_type = "yy1"
        self.widgets[2].picture_type = "zz1"
        self.widgets[3].picture_type = "xx1"

    def initUI(self):
        layout = QGridLayout()

        # 在网格布局中添加 4 个 Picturewidgetrightkey
        layout.addWidget(self.widgets[0], 0, 0)  # 第一行第一列
        layout.addWidget(self.widgets[1], 0, 1)  # 第一行第二列
        layout.addWidget(self.widgets[2], 1, 0)  # 第二行第一列
        layout.addWidget(self.widgets[3], 1, 1)  # 第二行第二列

        # 初始化所有 widget
        for widget in self.widgets:
            widget.initUI()
        self.setLayout(layout)

    def parameter_changed(self, new_twiss_parameter):
        for i in self.widgets:
            i.change_twiss_parameter(new_twiss_parameter)


    def closeEvent(self, event):
        self.closed.emit()
        event.accept()



if __name__ == "__main__":
    project_path = r"C:\Users\shliu\Desktop\maxi\test_m"

    app = QApplication(sys.argv)

    # 传入 project_path 和 func 作为参数
    dialog = PhaseEllipseWidget()

    dialog.initUI()
    twiss_parameter = {
        "alpha_x": -0.46109213,
        "beta_x": 0.38656878,
        "rms_emit_x": 0.2001403,

        "alpha_y": -0.46109213,
        "beta_y": 0.38656878,
        "rms_emit_y": 0.2001403,

        "alpha_z": -0.46109213,
        "beta_z": 0.38656878,
        "rms_emit_z": 0.2001403,

    }

    dialog.parameter_changed(twiss_parameter)
    dialog.exec_()