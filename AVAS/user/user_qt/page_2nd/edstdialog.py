#dst文件的可视化页面

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QDialog, QCheckBox, QButtonGroup, QMessageBox

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from functools import partial
from PyQt5.QtCore import Qt


from PyQt5.QtCore import pyqtSignal
import sys
from dataprovision.beamparameter import DstParameter
from apis.basic_api.api import plot_edst

from aftertreat.dataanalysis.out_percentemitt import cla_twiss_output_standard
import time

import logging
from logger.logger_config import setup_logger
from user.user_qt.page_utils.dstemitdialog import DstEmitDialog
from conf.contants import dst_picture_title_dict, edst_option_type_dict

logger = logging.getLogger(__name__)


class CustomToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.actions = {}  # 存储按钮的名称和 QAction 对象



    def add_tool_button(self, name, callback):
        """
        添加一个工具栏按钮
        :param name: 按钮名称
        :param callback: 按钮点击后的回调函数
        """
        action = QAction(name, self)
        action.triggered.connect(callback)  # 绑定点击事件
        self.addAction(action)
        self.actions[name] = action  # 记录按钮
        return action

    def remove_tool_button(self, name):
        """移除指定的按钮"""
        if name in self.actions:
            action = self.actions.pop(name)
            self.removeAction(action)

    def clear_toolbar(self):
        """清空工具栏"""
        self.actions.clear()
        self.clear()



class EdstPlotDialog(QDialog):
    resize_signal = pyqtSignal()  # 正确初始化自定义信号
    def __init__(self, edst_path):
        super().__init__()
        self.edst_path = edst_path
        self.field_num = 0
        self.fig = Figure(figsize=(6.4,6))  # 创建figure对象
        # self.setGeometry(800, 500, 360*3, 320*2)
        self.option_type_dict = edst_option_type_dict
        self.picture_type = [
            ["x", "x1"],
            ["y", "y1"],
            ["phi", "w"],
            # ["z", "z1"],
            ["phi", "y"]
        ]
        self.emit_ratio = 1

        # if edst_path is not None:
        #     self.edst_dict = self.get_dst_dict()

        self.initUI()



    def get_dst_dict(self):
        t0 = time.time()
        dst_obj = DstParameter(self.dst_path)
        dst_dict = dst_obj.get_parameter()
        t1 = time.time()
        logger.info(f"计算dst所用的时间 {t1-t0}")
        return dst_dict

    def initUI(self):
        winflags = Qt.Dialog
        # 添加最小化按钮
        winflags |= Qt.WindowMinimizeButtonHint
        # 添加最大化按钮
        winflags |= Qt.WindowMaximizeButtonHint
        # 添加关闭按钮
        winflags |= Qt.WindowCloseButtonHint
        # 设置到窗体上
        self.setWindowFlags(winflags)
        # 创建一个容纳工具栏和图像的 QWidget
        self.setWindowTitle('弹出窗口')

################################

        self.canvas = FigureCanvas(self.fig)  # 创建figure画布
        self.figtoolbar = NavigationToolbar(self.canvas, self)  # 创建figure工具栏
###############################

        self.ratio_dialog = None
        container_widget = QWidget(self)

        layout = QVBoxLayout()
        container_widget.setLayout(layout)

        self.toolbar = CustomToolBar(self)

        # 添加多个按钮，每个按钮绑定不同的槽函数
        self.toolbar.add_tool_button("refresh", self.refresh)
        self.toolbar.add_tool_button("open", self.open_file)
        self.toolbar.add_tool_button("save", self.save_file)
        self.toolbar.add_tool_button("ε", self.emit_info)

        #############
        layout.addWidget(self.toolbar)

########################################
        grit_picture_type = QGridLayout()

        axis_options = ["X", "Y", "Z", "X'", "Y'", "Z'", "Φ", "W", "dp/p"]

        grit_picture_type.setContentsMargins(0, 0, 0, 0)
        grit_picture_type.setHorizontalSpacing(8)
        grit_picture_type.setVerticalSpacing(0)

        self.axis_selectors = []
        print(141, self.picture_type)
        defaults = [
            ("X", "X'"),
            ("Y", "Y'"),
            ("Φ", "W"),
            ("Φ", "Y")
        ]

        for i in range(4):
            label = QLabel(f"P{i + 1}")

            combo_x = QComboBox()
            combo_y = QComboBox()

            combo_x.addItems(axis_options)
            combo_y.addItems(axis_options)

            combo_x.setCurrentText(defaults[i][0])
            combo_y.setCurrentText(defaults[i][1])

            self.axis_selectors.append((combo_x, combo_y))

            col = i * 4
            grit_picture_type.addWidget(label, 0, col, Qt.AlignVCenter)
            grit_picture_type.addWidget(combo_x, 0, col + 1)
            grit_picture_type.addWidget(QLabel("-"), 0, col + 2, Qt.AlignCenter)
            grit_picture_type.addWidget(combo_y, 0, col + 3)

        grid_container = QWidget()
        grid_container.setLayout(grit_picture_type)

        grid_container.setMaximumHeight(50)  # 关键：限制最大高度
        print(173, self.picture_type)

        for i, (combo_x, combo_y) in enumerate(self.axis_selectors):
            combo_x.currentTextChanged.connect(partial(self._update_axis_options, i))
            combo_y.currentTextChanged.connect(partial(self._update_axis_options, i))
        print(178, self.picture_type)

        for i in range(len(self.axis_selectors)):
            self._update_axis_options(i)

        # for combo_x, combo_y in self.axis_selectors:
        #     combo_x.currentTextChanged.connect(self.update_plots)
        #     combo_y.currentTextChanged.connect(self.update_plots)

        #############################
        layout.addWidget(self.figtoolbar)  # 工具栏添加到窗口布局中
        # layout.addWidget(grid_container)
        layout.addWidget(self.canvas)  # 画布添加到窗口布局中
        print(191, self.picture_type)

################################################
        self.dst_emit_obj = DstEmitDialog(self)
        self.dst_emit_obj.emit_ratio_signal.connect(self.get_emit_ratio)


        self.setLayout(layout)
        # self._update_axis_options()

    def _update_axis_options(self, idx):
        combo_x, combo_y = self.axis_selectors[idx]

        x = combo_x.currentText()
        y = combo_y.currentText()

        # 更新 combo_x 中是否禁用 y
        for i in range(combo_x.count()):
            item = combo_x.model().item(i)
            item.setEnabled(combo_x.itemText(i) != y)

        # 更新 combo_y 中是否禁用 x
        for i in range(combo_y.count()):
            item = combo_y.model().item(i)
            item.setEnabled(combo_y.itemText(i) != x)

        # 再刷新图
        self.update_plots()

    def update_plots(self):
        # logger.info("Axis changed")


        # axis_options = ["X", "Y", "Z", "X'", "Y'", "Z'", "phi", "W", "dp_p"]



        for i, (cx, cy) in enumerate(self.axis_selectors):
            x_axis = cx.currentText()
            y_axis = cy.currentText()
            self.picture_type[i] = [self.option_type_dict[x_axis], self.option_type_dict[y_axis]]

        # logger.info(self.picture_type)
        # 在这里刷新你的图像
        # 比如：self.redraw_all()



    def plot_image(self):
        self.fig.clear()
        t0 =time.time()


        # item = {
        #     "ratio": 1,
        #     "picture_type":self.picture_type,
        #     "dst_path": None,
        #     "dst_dict": self.dst_dict ,
        #     "ratio": self.emit_ratio,
        #
        # }
        # twiss_dict, twiss_text = cla_twiss_output_standard(item)
        print(self.picture_type)
        item = {"edst_path": self.edst_path, "picture_type": self.picture_type, "show_": 0, "fig": self.fig, "platform": "qt",
                "sampleInterval": 1, "needData": False, "projectPath": None, "location": "out", }


        plot_edst(item)

        self.canvas.draw()

        # emit_page_text = {
        #     "twiss_text": twiss_text,
        #     "certer_text": None,
        #     "size_text": None,
        #     "fwhm_text": None,
        # }
        #
        # self.dst_emit_obj.update_pages(emit_page_text
        # )

    def closeEvent(self, event):
        event.accept()


    def refresh(self):
        self.plot_image()
        # label_edit_widgets = {}
        # for i in range(0, self.field_name):
        #     label_name = f"label_{i}"
        #     edit_name = f"edit_{i}"
        #
        #     label = self.findChild(QLabel, label_name)
        #     edit = self.findChild(QLineEdit, edit_name)
        #
        #     if label and edit:
        #         label_edit_widgets[label.text()] =float(edit.text())
        #
        # # 现在 label_edit_widgets 包含了每个 label 对应的 edit
        # self.ratio = label_edit_widgets
        # self.plot_image()

    def open_file(self):
        pass

    def save_file(self):
        pass
    def emit_info(self):

        self.dst_emit_obj.show()

    def get_emit_ratio(self, emit_ratio):
        self.emit_ratio = emit_ratio
        self.plot_image()


if __name__ == '__main__':
    setup_logger(
        level=logging.INFO,
    )

    app = QApplication(sys.argv)
    w = EdstPlotDialog(r"C:\Users\wangh\Desktop\qx\2beam\OutputFile\outData_6.992532.edst")
    w.plot_image()
    w.show()
    sys.exit(app.exec_())