

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
from utils.readfile import read_lattice_mulp_with_name
import os

#最普通的，只有一张图片

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

class PictureDialog1(QDialog):
    resize_signal = pyqtSignal()  # 正确初始化自定义信号
    def __init__(self, ):
        super().__init__()
        self.fig_size = (6.4, 4.6)

        self.fig = Figure(figsize=self.fig_size)  # 创建figure对象

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
        # self.setGeometry(200, 200, 640, 480)

################################
        self.canvas = FigureCanvas(self.fig)  # 创建figure画布
        self.figtoolbar = NavigationToolbar(self.canvas, self)  # 创建figure工具栏
###############################
        # container_widget = QWidget(self)

        layout = QVBoxLayout()

##############################
        self.toolbar = CustomToolBar(self)

        # 添加多个按钮，每个按钮绑定不同的槽函数
        self.toolbar.add_tool_button("刷新", self.refresh)
        self.toolbar.add_tool_button("打开", self.open_file)
        self.toolbar.add_tool_button("保存", self.save_file)
        #############




        layout.addWidget(self.toolbar)
        layout.addWidget(self.figtoolbar)  # 工具栏添加到窗口布局中
        layout.addWidget(self.canvas)  # 画布添加到窗口布局中
        # layout.addWidget(self.image_label)

        self.setLayout(layout)
        self.resize_signal.connect(self.on_resize)  # 连接信号和槽

    def resizeEvent(self, event):
        # 当窗口被拉伸时，发出自定义信号
        self.resize_signal.emit()
        return super().resizeEvent(event)


    def on_resize(self):
        self.fig.tight_layout()
        # self.fig.subplots_adjust(left=0.5 )

    def closeEvent(self, event):
        event.accept()


    # 只有一张图，接收参数为文件路径， 函数， 图片类型1
    def plot_image1(self, item, func):

        item.update({"fig": self.fig})
        func(**item)

    def plot_image2(self, file_path, func, picture_type1=None, picture_type2=None):
        func(file_path, picture_type1, picture_type2, show_=0, fig=self.fig)

    def refresh(self):
        print("刷新按钮被点击！")

    def open_file(self):
        print("打开文件！")

    def save_file(self):
        print("保存文件！")


#这是一个带有右键的组件
class Picturewidgetrightkey(QWidget):
    resize_signal = pyqtSignal()  # 正确初始化自定义信号
    def __init__(self):
        super().__init__()

        self.fig_size = (6.4, 4.6)
        self.fig = Figure(figsize=self.fig_size)  # 创建figure对象

    def initUI(self):
        # self.setGeometry(200, 200, 400, 300)
################################
        self.canvas = FigureCanvas(self.fig)  # 创建figure画布
        self.figtoolbar = NavigationToolbar(self.canvas, self)  # 创建figure工具栏
###############################
        layout = QVBoxLayout()

        # 创建一个容纳工具栏和图像的 QWidget
        container_widget = QWidget(self)
        # 将右键上下文菜单与 self.image_label 绑定
        container_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        container_widget.customContextMenuRequested.connect(self.contextMenuEvent)

        layout_container = QVBoxLayout(container_widget)  # 让 container_widget 成为布局容器
        layout_container.addWidget(self.figtoolbar)
        layout_container.addWidget(self.canvas)



        self.setLayout(layout_container)
        self.plot_image()

    def resizeEvent(self, event):
        # 当窗口被拉伸时，发出自定义信号
        self.resize_signal.emit()
        return super().resizeEvent(event)


    def on_resize(self):
        self.fig.tight_layout()
        # plt.subplots_adjust(top=0.8 )

    def plot_image(self):
        # self.fig.clf()
        # self.func(self.project_path, self.picture_type, show_=0, fig=self.fig)
        # self.canvas.draw()
        pass

    def contextMenuEvent(self, pos):
        pass


#用来处理只有一张图片，但是需要右键
class OnePicyureRightkeys(QDialog):
    def __init__(self, project_path, func):
        super().__init__()
        self.project_path = project_path
        self.func = func
        self.picture_widget = Picturewidgetrightkey()

    def initUI(self):
        self.setWindowTitle("Envelope Dialog")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.toolbar = CustomToolBar()
        # 添加多个按钮，每个按钮绑定不同的槽函数
        self.toolbar.add_tool_button("刷新", self.refresh)
        self.toolbar.add_tool_button("打开", self.open_file)
        self.toolbar.add_tool_button("保存", self.save_file)
        #############

        self.layout.addWidget(self.toolbar)

        # 添加到布局
        self.layout.addWidget(self.picture_widget)
        self.picture_widget.initUI()

        self.setLayout(self.layout)

    def refresh(self):
        print("刷新按钮被点击！")

    def open_file(self):
        print("打开文件！")

    def save_file(self):
        print("保存文件！")


#多粒子中的包络
class MulpEnvelopeDialog(OnePicyureRightkeys):
    def __init__(self, project_path, func):
        super().__init__(project_path, func)

        self.picture_widget = Picturewidgetrightkey()
        self.picture_widget.contextMenuEvent = self.contextMenuEvent
        self.picture_widget.plot_image = self.plot_image
        self.picture_type = "rms_x"

    def plot_image(self):
        item = {"projectPath": self.project_path, "pictureType": self.picture_type, "show_": 0,
                "fig": self.picture_widget.fig, "platform": "qt", "sampleInterval": 1}

        self.func(**item)
        self.picture_widget.canvas.draw()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        menu_items = {
            "rms_x": cmenu.addAction("rms_x"),
            "rms_y": cmenu.addAction("rms_y"),
            "phi": cmenu.addAction("phi"),
            "rms_xy": cmenu.addAction("rms_xy"),
            "max_x": cmenu.addAction("max_x"),
            "max_y": cmenu.addAction("max_y"),
            "max_xy": cmenu.addAction("max_xy"),
            "beta_x": cmenu.addAction("beta_x"),
            "beta_y": cmenu.addAction("beta_y"),
            "beta_z": cmenu.addAction("beta_z"),
            "beta_xyz": cmenu.addAction("beta_xyz"),
        }

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        for item_name, menu_item in menu_items.items():
            if action == menu_item:
                self.picture_type = item_name
                break
        self.picture_widget.fig.clf()
        self.picture_widget.plot_image()


class MulpEmittanceDialog(OnePicyureRightkeys):
    def __init__(self, project_path, func):
        super().__init__(project_path, func)
        self.picture_widget = Picturewidgetrightkey()
        self.picture_widget.contextMenuEvent = self.contextMenuEvent
        self.picture_widget.plot_image = self.plot_image
        self.picture_type = "emittance_x"

    def plot_image(self):
        item = {"projectPath": self.project_path, "pictureType": self.picture_type, "show_": 0,
                "fig": self.picture_widget.fig, "platform": "qt", "sampleInterval": 1}

        self.func(**item)
        self.picture_widget.canvas.draw()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        menu_items = {
            "emittance_x": cmenu.addAction("emittance_x"),
            "emittance_y": cmenu.addAction("emittance_y"),
            "emittance_z": cmenu.addAction("emittance_z"),
        }

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        for item_name, menu_item in menu_items.items():
            if action == menu_item:
                self.picture_type = item_name
                break
        self.picture_widget.fig.clf()
        self.picture_widget.plot_image()


class BeamPahseAdvance(OnePicyureRightkeys):
    def __init__(self, project_path, func):
        super().__init__(project_path, func)
        self.picture_widget = Picturewidgetrightkey()
        self.picture_widget.contextMenuEvent = self.contextMenuEvent
        self.picture_widget.plot_image = self.plot_image
        self.picture_type = "meter"


    def plot_image(self):
        print(self.picture_type)
        item = {
            "projectPath": self.project_path, "pictureType": self.picture_type, "show_": 0, "fig": self.picture_widget.fig, "platform": "qt"}

        self.func(**item)
        self.picture_widget.canvas.draw()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        menu_items = {
            "meter": cmenu.addAction("Meter"),
            "period": cmenu.addAction("Period"),
        }

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        for item_name, menu_item in menu_items.items():
            if action == menu_item:
                self.picture_type = item_name
                break
        self.picture_widget.fig.clf()

        self.picture_widget.plot_image()


class CavityVoltageDialog(QDialog):
    resize_signal = pyqtSignal()  # 正确初始化自定义信号
    def __init__(self, project_path, func):
        super().__init__()
        self.project_path = project_path
        self.func = func
        self.ratio = {}
        self.field_num = 0
        self.fig = Figure(figsize=(6.4, 4.6))  # 创建figure对象
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
        self.toolbar.add_tool_button("刷新", self.refresh)
        self.toolbar.add_tool_button("打开", self.open_file)
        self.toolbar.add_tool_button("保存", self.save_file)
        #############
        layout.addWidget(self.toolbar)

########################################
        self.get_feld()
        vbox_field = QVBoxLayout()
        i = 0
        for k, v in self.ratio.items():
            label = QLabel(k)
            edit = QLineEdit(str(v))
            label.setObjectName(f"label_{i}")
            edit.setObjectName(f"edit_{i}")
            vbox_field.addWidget(label)
            vbox_field.addWidget(edit)
            i = i + 1

        self.field_name = i


        field_group_box = QGroupBox()
        field_layout = QVBoxLayout()
        field_layout.addLayout(vbox_field)
        field_group_box.setLayout(field_layout)



##############################################
        hbox_field_image = QHBoxLayout()
        hbox_field_image.addWidget(field_group_box)
        hbox_field_image.addWidget(self.canvas)

        field_image_group_box = QGroupBox()

        field_image_group_box.setLayout(hbox_field_image)
################################################

        layout.addWidget(self.figtoolbar)

        layout.addWidget(field_image_group_box)

        self.setLayout(layout)


    def plot_image(self):
        self.fig.clear()
        self.func(self.project_path, self.ratio, show_=0, fig=self.fig)

        # print(self.ratio)
        # obj = self.cls(self.project_path, self.ratio)
        # obj.get_x_y()
        # obj.run(show_=0, fig=self.fig)
        self.canvas.draw()


    def closeEvent(self, event):
        event.accept()

    def get_feld(self):
        lattice_path = os.path.join(self.project_path, "InputFile", "lattice_mulp.txt")
        all_info, _ = read_lattice_mulp_with_name(lattice_path)

        for i in all_info:
            if i[0] == 'field' and float(i[4]) == 1:
                self.ratio[i[9]] = 1

    def refresh(self):
        label_edit_widgets = {}
        for i in range(0, self.field_name):
            label_name = f"label_{i}"
            edit_name = f"edit_{i}"

            label = self.findChild(QLabel, label_name)
            edit = self.findChild(QLineEdit, edit_name)

            if label and edit:
                label_edit_widgets[label.text()] =float(edit.text())

        # 现在 label_edit_widgets 包含了每个 label 对应的 edit
        self.ratio = label_edit_widgets
        self.plot_image()

    def open_file(self):
        pass

    def save_file(self):
        pass



if __name__ == "__main__":
    obj = PictureDialog1()
    obj.initUI()
    obj.exec_()