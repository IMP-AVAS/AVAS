import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QCheckBox, QButtonGroup, QTreeWidget, QTreeWidgetItem, QSpacerItem, QSizePolicy, QMessageBox

import os

from PyQt5.QtCore import QStandardPaths, QCoreApplication, pyqtSignal, QTimer
from api import change_particle_number

from user.user_qt.user_defined import treat_err
import multiprocessing


class PageMatch (QWidget):
    match_signal = pyqtSignal(dict)

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.match_choose = ''
        self.use_initial_value = 0
        self.initUI()

    def initUI(self):
        # print(self.project_path)
        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QHBoxLayout()

        # 创建一个垂直组合框
        vertical_group_box_main = QGroupBox("Function")

        vertical_layout_main = QVBoxLayout()

        ##########################################################################


        group_box_match = QGroupBox('Match')
        group_box_match.setFixedHeight(150)  # 设置高度为200像素

        hbox_match = QVBoxLayout()

        self.cb_input_twiss = QCheckBox('Calculate input twiss parameter', self)
        self.cb_input_twiss.stateChanged.connect(self.cb_match_change)

        self.cb_match_twiss = QCheckBox('Match with twiss command', self)

        self.cb_match_twiss.stateChanged.connect(self.cb_match_change)

        # 创建一个包装布局
        wrapper_layout = QHBoxLayout()

        self.cb_use_initial_value = QCheckBox('Use initial value')
        self.cb_use_initial_value.stateChanged.connect(self.cb_match_change)

        # 添加一个占位符小部件到包装布局以增加左边距
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        wrapper_layout.addItem(spacer)

        wrapper_layout.addWidget(self.cb_use_initial_value)
        # self.cb_use_initial_value.setVisible(False)

        # 创建一个按钮组

        # 添加包装布局到 hbox_match_2 布局
        hbox_match.addWidget(self.cb_input_twiss)
        hbox_match.addWidget(self.cb_match_twiss)
        hbox_match.addLayout(wrapper_layout)

        group_box_match.setLayout(hbox_match)

        self.cb_use_initial_value.setEnabled(False)



        vertical_layout_main.addWidget(group_box_match)
        vertical_layout_main.addStretch(1)

        vertical_group_box_main.setLayout(vertical_layout_main)
        #########################################################################################

        layout.addWidget(vertical_group_box_main)

        self.setLayout(layout)

        self.change_num_process = None

        # 创建一个定时器，每隔一段时间检查self.match_process的状态
        self.match_timer = QTimer(self)
        # self.match_timer.timeout.connect(self.check_match_process_status)

        self.simulation_timer = QTimer(self)
        # self.simulation_timer.timeout.connect(self.check_simulation_process_status)

    def updatePath(self, new_path):
        self.project_path = new_path

    @treat_err
    def refreshUI(self):
        self.initUI()  # Call initUI to refresh the UI


    def cb_match_change(self, ):
        sender_checkbox = self.sender()  # 获取发送信号的复选框对象

        if sender_checkbox == self.cb_input_twiss:
            if sender_checkbox.isChecked():
                self.cb_match_twiss.setChecked(False)
                self.cb_use_initial_value.setEnabled(False)
                self.cb_use_initial_value.setChecked(False)

        elif sender_checkbox == self.cb_match_twiss:
            if sender_checkbox.isChecked():
                self.cb_use_initial_value.setEnabled(True)
                self.cb_input_twiss.setChecked(False)

            if not sender_checkbox.isChecked():
                self.cb_use_initial_value.setEnabled(False)


        dic = self.get_state_dict()
        self.match_signal.emit(dic)

    def fill_parameter(self):

        ini_dict = self.ini_obj.creat_from_file(self.ini_path)
        if ini_dict['code'] == -1:
            raise Exception(ini_dict['data']['msg'])
        ini_dict = ini_dict["data"]['ini_params']


        if ini_dict['match']['cal_input_twiss'] == 1:
            self.cb_input_twiss.setChecked(True)

        if ini_dict['match']['match_with_twiss'] == 1:
            self.cb_match_twiss.setChecked(True)
        if ini_dict['match']['use_initial_value'] == 1:
            self.cb_use_initial_value.setChecked(True)


    def get_state_dict(self):
        dic = {"cal_input_twiss": 0, "match_with_twiss": 0, "use_initial_value": 0}

        if self.cb_input_twiss.isChecked():
            dic["cal_input_twiss"] = 1

        if self.cb_match_twiss.isChecked():
            dic["match_with_twiss"] = 1

        if self.cb_use_initial_value.isChecked():
            dic["use_initial_value"] = 1

        return dic


    def inspect(self):
        pass
        return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageMatch(r'C:\Users\anxin\Desktop\comparison\avas_test')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    sys.exit(app.exec_())