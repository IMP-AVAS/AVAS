import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QCheckBox, QMessageBox

import os

from PyQt5.QtCore import Qt, pyqtSignal
from utils.readfile import read_txt, read_dst
from user.user_qt.user_defined import treat_err, treat_err2, gray240
from api import cal_acceptance
from api import plot_acc

class PageAccept(QWidget):
    basic_signal = pyqtSignal(str)

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.decimals = 6

        self.initUI()

    def initUI(self):
        # print(self.project_path)
        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QHBoxLayout()

        # 创建一个垂直组合框
        gb_main = QGroupBox("")

        layout_main = QVBoxLayout()
        ##########################################################################
        gb_xyz = QGroupBox()

        layout_xyz = QHBoxLayout()

        self.cb_x = QCheckBox("xx'", self)
        self.cb_x.stateChanged.connect(self.cb_xyz_change)

        self.cb_y = QCheckBox("yy'", self)
        self.cb_y.stateChanged.connect(self.cb_xyz_change)

        self.cb_z = QCheckBox("zz'", self)
        self.cb_z.stateChanged.connect(self.cb_xyz_change)

        self.cb_phie = QCheckBox("phiE", self)
        self.cb_phie.stateChanged.connect(self.cb_xyz_change)

        layout_xyz.addWidget(self.cb_x)
        layout_xyz.addWidget(self.cb_y)
        layout_xyz.addWidget(self.cb_z)
        layout_xyz.addWidget(self.cb_phie)

        gb_xyz.setLayout(layout_xyz)
        ##############################################
        gb_0 = QGroupBox()

        layout_0 = QVBoxLayout()

        layout_01 = QHBoxLayout()
        self.emit_label = QLabel("Emittance")
        self.emit_line = QLineEdit()
        self.emit_unit = QLabel("\u03C0.mm.mrad")


        self.emit_norm_label = QLabel("Norm Emittance")
        self.emit_norm_line = QLineEdit()
        self.emit_norm_unit = QLabel("\u03C0.mm.mrad")

        layout_01.addWidget(self.emit_label)
        layout_01.addWidget(self.emit_line)
        layout_01.addWidget(self.emit_unit)
        layout_01.addWidget(self.emit_norm_label)
        layout_01.addWidget(self.emit_norm_line)
        layout_01.addWidget(self.emit_norm_unit)

        layout_02 = QHBoxLayout()
        self.x_label = QLabel("Min_x")
        self.x_line = QLineEdit()
        self.x_unit = QLabel("mm")

        self.y_label = QLabel("Min_y")
        self.y_line = QLineEdit()
        self.y_unit = QLabel("mrad")

        layout_02.addWidget(self.x_label)
        layout_02.addWidget(self.x_line)
        layout_02.addWidget(self.x_unit)

        layout_02.addWidget(self.y_label)
        layout_02.addWidget(self.y_line)
        layout_02.addWidget(self.y_unit)

        label_list = [self.emit_label, self.emit_norm_label, self.x_label, self.y_label]
        for i in label_list:
            i.setMinimumWidth(84)

        qline_list = [self.emit_line, self.emit_norm_line, self.x_line, self.y_line]
        for i in qline_list:
            i.setFixedWidth(84)

        layout_0.addLayout(layout_01)
        layout_0.addLayout(layout_02)
        gb_0.setLayout(layout_0)




        ##############################################
        gb_run = QGroupBox()
        run_layout = QHBoxLayout()

        self.buttonm_run = QPushButton("Run")
        self.buttonm_run.setMaximumWidth(84)
        self.buttonm_run.clicked.connect(self.button_run_click)

        self.buttonm_plot = QPushButton("Plot")
        self.buttonm_plot.setMaximumWidth(84)
        self.buttonm_plot.clicked.connect(self.button_plot_click)

        run_layout.addWidget(self.buttonm_run)
        run_layout.addWidget(self.buttonm_plot)
        gb_run.setLayout(run_layout)

        ##############################################

        layout_main.addWidget(gb_xyz)
        layout_main.addWidget(gb_0)
        layout_main.addWidget(gb_run)

        layout_main.addStretch(1)

        gb_main.setLayout(layout_main)

        layout.addWidget(gb_main)
        self.setLayout(layout)


    def cb_xyz_change(self, state):
        sender_checkbox = self.sender()  # 获取发送信号的复选框对象

        # print(sender_checkbox)
        cb_xyz = [self.cb_x, self.cb_y, self.cb_z, self.cb_phie]
        if sender_checkbox in cb_xyz:
            if sender_checkbox.isChecked():
                cb_xyz.remove(sender_checkbox)
                for i in cb_xyz:
                    i.setChecked(not sender_checkbox.isChecked())


    def inspect(self):
        if not self.step_per_period_text.text():
            e = "Missing calculation step"
            QMessageBox.warning(None, 'Error', e)
            return False
        else:
            return True

    def button_run_click(self):
        if self.cb_x.isChecked():
            all_emit, norm_emit, x_min, xx_min = cal_acceptance(self.project_path, 0)

        elif self.cb_y.isChecked():
            all_emit, norm_emit, x_min, xx_min = cal_acceptance(self.project_path, 1)

        elif self.cb_z.isChecked():
            all_emit, norm_emit, x_min, xx_min= cal_acceptance(self.project_path, 2)

        elif self.cb_phie.isChecked():
            all_emit, norm_emit, x_min, xx_min = cal_acceptance(self.project_path, 3)



        if self.cb_x.isChecked() or self.cb_y.isChecked() or self.cb_z.isChecked() \
            or self.cb_phie.isChecked():

            if norm_emit is not None:
                self.emit_line.setText(str(round(all_emit, self.decimals)))
                self.emit_norm_line.setText(str(round(norm_emit,self.decimals)))
            else:
                self.emit_line.setText("")
                self.emit_norm_line.setText(str(round(all_emit, self.decimals)))

            self.x_line.setText(str(round(x_min,self.decimals)))
            self.y_line.setText(str(round(xx_min,self.decimals)))

    def button_plot_click(self):
        if self.cb_x.isChecked():
            res = plot_acc(self.project_path, 0)

        elif self.cb_y.isChecked():
            res = plot_acc(self.project_path, 1)

        elif self.cb_z.isChecked():
            res = plot_acc(self.project_path, 2)

        elif self.cb_phie.isChecked():
            res = plot_acc(self.project_path, 3)


    def updatePath(self, new_path):
        self.project_path = new_path

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageAccept(r'C:\Users\shliu\Desktop\xiaochu')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    sys.exit(app.exec_())