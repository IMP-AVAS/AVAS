import os.path
import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QDialog, QCheckBox, QButtonGroup, QMessageBox

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from apis.basic_api.api import plot_error_out, plot_error_emit_loss, plot_density, plot_density_level, plot_density_process
from user.user_qt.user_defined import treat_err

from user.user_qt.page_utils.picture_dialog import PictureDialog1
from user.user_qt.user_defined import MyQLineEdit
from utils.iniconfig import IniConfig
from aftertreat.picture.ploterror import PlotErrout, PlotErr_emit_loss
from functools import partial






########################################################

class PageError(QWidget):
    error_signal = pyqtSignal(dict)
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.lattice_path = self.project_path + r"\inputFile" + r'\lattice.txt'

        self.error_par_file_path = None
        self.density_file_path = None
        # 相移meter和oeriod
        self.pahse_advance_mp = ''
        self.output_plot_type = 'average'

        self.density_plane_choose = None
        self.density_picture_type = None

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        group_box = QGroupBox("")
        group_box_layout = QVBoxLayout()

        ##############################################

        err_type_group_box = QGroupBox("")
        hbox_error_type = QHBoxLayout()

        self.cb_stat_error = QCheckBox("Static error")
        self.cb_stat_error.stateChanged.connect(self.cb_error_change)

        self.cb_dyn_error = QCheckBox("Dynamic error")
        self.cb_dyn_error.stateChanged.connect(self.cb_error_change)

        self.cb_stat_dyn_error = QCheckBox("Static error & Dynamic error")
        self.cb_stat_dyn_error.stateChanged.connect(self.cb_error_change)

        hbox_error_type.addWidget(self.cb_stat_error)
        hbox_error_type.addWidget(self.cb_dyn_error)
        hbox_error_type.addWidget(self.cb_stat_dyn_error)

        err_type_group_box.setLayout(hbox_error_type)
        ##############################################
        group_box_seed = QGroupBox("")
        layout_seed = QHBoxLayout()
        label_seed = QLabel("seed")
        label_seed.setFixedSize(180, 12)  # 设置宽度和高度
        # label_charge.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_seed = MyQLineEdit("50")

        self.text_seed.textChanged.connect(self.text_seed_change)

        layout_seed.addWidget(label_seed)
        layout_seed.addWidget(self.text_seed)
        group_box_seed.setLayout(layout_seed)

        ##############################################
        group_box_output = QGroupBox("")
        layout1 = QVBoxLayout()

        layout10 = QHBoxLayout()
        self.button_select_error_par = QPushButton(QApplication.style().standardIcon(32),"")
        self.button_select_error_par.clicked.connect(self.select_error_par)
        self.text_error_par  = MyQLineEdit(" ")

        layout10.addWidget(self.button_select_error_par)
        layout10.addWidget(self.text_error_par)



        layout11 = QHBoxLayout()
        self.button_emit_loss = QPushButton("Emit growth && Loss")
        self.button_emit_loss.clicked.connect(self.plot_error_emit_loss_this)

        self.cb_average = QCheckBox('average', self)
        self.cb_average.stateChanged.connect(self.cb_average_change)

        self.cb_rms = QCheckBox('rms', self)
        # self.cb_period.setChecked(True)  # 将 cb_period 设置为选中状态
        self.cb_rms.stateChanged.connect(self.cb_rms_change)

        # 创建一个按钮组
        button_group_1 = QButtonGroup(self)
        button_group_1.addButton(self.cb_average)
        button_group_1.addButton(self.cb_rms)

        layout11.addWidget(self.button_emit_loss)
        layout11.addWidget(self.cb_average)
        layout11.addWidget(self.cb_rms)

        layout12 = QHBoxLayout()
        self.button_output_xy = QPushButton("X && Y")
        self.button_output_xy.clicked.connect(partial(self.plot_error_out, "xy"))

        self.button_output_x1y1 = QPushButton("X' && Y'")
        self.button_output_x1y1.clicked.connect(partial(self.plot_error_out, "x1y1"))

        self.button_output_rmsxy = QPushButton("rms(X) && rms(Y)")
        self.button_output_rmsxy.clicked.connect(partial(self.plot_error_out, "rms_xy"))

        self.button_output_rmsx1y1 = QPushButton("rms(X') && rms(Y')")
        self.button_output_rmsx1y1.clicked.connect(partial(self.plot_error_out, "rms_x1y1"))

        self.button_output_energy = QPushButton("Energy change")
        self.button_output_energy.clicked.connect(partial(self.plot_error_out, "ek"))


        layout12.addWidget(self.button_output_xy)
        layout12.addWidget(self.button_output_x1y1)
        layout12.addWidget(self.button_output_rmsxy)
        layout12.addWidget(self.button_output_rmsx1y1)
        layout12.addWidget(self.button_output_energy)

        layout1.addLayout(layout10)
        layout1.addLayout(layout11)
        layout1.addLayout(layout12)

        group_box_output.setLayout(layout1)

        #############################################################
        group_box_density = QGroupBox("")
        layout_density = QVBoxLayout()

        layout_density_0 = QHBoxLayout()
        self.button_select_density_file = QPushButton(QApplication.style().standardIcon(32),"")
        self.button_select_density_file.clicked.connect(self.select_density_file)
        self.text_density_file = MyQLineEdit(" ")

        layout_density_0.addWidget(self.button_select_density_file)
        layout_density_0.addWidget(self.text_density_file)

        group_box_density_plane_choose = QGroupBox("")
        layout_density_plane_choose = QHBoxLayout()

        self.cb_plane_x = QCheckBox("X")
        self.cb_plane_x.stateChanged.connect(self.cb_density_plane_change)

        self.cb_plane_y = QCheckBox("Y")
        self.cb_plane_y.stateChanged.connect(self.cb_density_plane_change)

        self.cb_plane_r = QCheckBox("R")
        self.cb_plane_r.stateChanged.connect(self.cb_density_plane_change)

        self.cb_plane_z = QCheckBox("Z")
        self.cb_plane_z.stateChanged.connect(self.cb_density_plane_change)

        button_group_plane = QButtonGroup(self)
        button_group_plane.addButton(self.cb_plane_x)
        button_group_plane.addButton(self.cb_plane_y)
        button_group_plane.addButton(self.cb_plane_r)
        button_group_plane.addButton(self.cb_plane_z)


        layout_density_plane_choose.addWidget(self.cb_plane_x)
        layout_density_plane_choose.addWidget(self.cb_plane_y)
        layout_density_plane_choose.addWidget(self.cb_plane_r)
        layout_density_plane_choose.addWidget(self.cb_plane_z)
        group_box_density_plane_choose.setLayout(layout_density_plane_choose)

        group_box_density_picture_type = QGroupBox("")
        layout_density_picture_type = QVBoxLayout()

        self.cb_density = QCheckBox("Density")
        self.cb_density_level = QCheckBox("Density level")
        self.cb_density_centroid = QCheckBox("Centroid")
        self.cb_density_emittance = QCheckBox("Emittance")
        self.cb_density_rms_size = QCheckBox("Rms size") #包络
        self.cb_density_rms_size_max = QCheckBox("Rms size max")

        self.cb_density.clicked.connect(self.cb_density_picture_type_change)
        self.cb_density_level.clicked.connect(self.cb_density_picture_type_change)
        self.cb_density_centroid.clicked.connect(self.cb_density_picture_type_change)
        self.cb_density_emittance.clicked.connect(self.cb_density_picture_type_change)
        self.cb_density_rms_size.clicked.connect(self.cb_density_picture_type_change)
        self.cb_density_rms_size_max.clicked.connect(self.cb_density_picture_type_change)






        layout_density_picture_type_1 = QHBoxLayout()
        layout_density_picture_type_1.addWidget(self.cb_density)
        layout_density_picture_type_1.addWidget(self.cb_density_level)

        layout_density_picture_type_2 = QHBoxLayout()
        layout_density_picture_type_2.addWidget(self.cb_density_centroid)
        layout_density_picture_type_2.addWidget(self.cb_density_emittance)
        layout_density_picture_type_2.addWidget(self.cb_density_rms_size)
        layout_density_picture_type_2.addWidget(self.cb_density_rms_size_max)

        button_group_density_picture_type = QButtonGroup(self)
        button_group_density_picture_type.addButton(self.cb_density)
        button_group_density_picture_type.addButton(self.cb_density_level)
        button_group_density_picture_type.addButton(self.cb_density_centroid)
        button_group_density_picture_type.addButton(self.cb_density_emittance)
        button_group_density_picture_type.addButton(self.cb_density_rms_size)
        button_group_density_picture_type.addButton(self.cb_density_rms_size_max)


        layout_density_picture_type.addLayout(layout_density_picture_type_1)
        layout_density_picture_type.addLayout(layout_density_picture_type_2)

        group_box_density_picture_type.setLayout(layout_density_picture_type)
    ###############################################
        button_density_picture_plot = QPushButton("Plot")
        button_density_picture_plot.clicked.connect(self.plot_density_process_this)

        button_density_picture_plot.setFixedSize(100, 30)  # 设置固定大小


        layout_density.addLayout(layout_density_0)
        layout_density.addWidget(group_box_density_plane_choose)
        layout_density.addWidget(group_box_density_picture_type)
        layout_density.addWidget(button_density_picture_plot)


        group_box_density.setLayout(layout_density)

#####################################################################################

        group_box_layout.addWidget(err_type_group_box)
        group_box_layout.addWidget(group_box_seed)
        group_box_layout.addWidget(group_box_output)
        group_box_layout.addWidget(group_box_density)


        group_box_layout.addStretch(1)

        group_box.setLayout(group_box_layout)

        layout.addWidget(group_box)
        self.setLayout(layout)

    # @treat_err
    # ###########errr
    # def error_ek_dialog(self):
    #     func = plot_error
    #     self.dialog = ErrorEnergyDialog(self.project_path, func, self.plot_error_type)
    #     self.dialog.initUI()
    #     self.dialog.plot_image()
    #     self.dialog.show()
    #
    # @treat_err
    # def error_envelope_dialog(self, ):
    #     func = plot_error
    #     self.dialog = ErrorEnvelopeDialog(self.project_path, func, self.plot_error_type)
    #     self.dialog.initUI()
    #     self.dialog.show()


    def plot_error_emit_loss_this(self, ):
        func = plot_error_emit_loss
        # self.dialog = EmitLossDialog(self.project_path, func, 'par')

        self.xy_dialog = PictureDialog1()

        self.xy_dialog.initUI()
        item = {"filePath": self.error_par_file_path, "pictureType": "par"}

        self.xy_dialog.plot_image1(item, plot_error_emit_loss)
        self.xy_dialog.show()


    def text_seed_change(self):
        if self.text_seed.text():
            seed_value = int(self.text_seed.text())
        else:
            seed_value = 0

        error_dic = self.get_state_dict()
        self.error_signal.emit(error_dic)



    def plot_error_out(self, message):

        self.xy_dialog = PictureDialog1()

        self.xy_dialog.initUI()
        item = {"filePath": self.error_par_file_path,
                    "statMethod": self.output_plot_type,
                    "pictureType": message,
                    "show_": 0,
        }
        self.xy_dialog.plot_image1(item, plot_error_out,)
        self.xy_dialog.show()

    def plot_density_process_this(self):
        # print(self.density_file_path)
        # print(self.density_picture_type)
        diaglog = None

        # plot_density(self.density_file_path, self.density_plane_choose, show_=1, fig=None, platform="qt")
        item = {"filePath": self.density_file_path, "desnityPlane": self.density_plane_choose,
                "sampleInterval": 1}

        if self.density_picture_type == "density":
            self.density_dialog = PictureDialog1()
            self.density_dialog.initUI()

            self.density_dialog.plot_image1(item, plot_density, )
            self.density_dialog.show()

        elif self.density_picture_type == "density_level":
            self.density_level_dialog = PictureDialog1()
            self.density_level_dialog.initUI()
            self.density_level_dialog.plot_image1(item, plot_density_level,)
            self.density_level_dialog.show()

        elif self.density_picture_type == "centroid":
            self.density_centroid_dialog = PictureDialog1()
            self.density_centroid_dialog.initUI()
            item.update({"pictureType":"centroid"})
            self.density_centroid_dialog.plot_image1(item, plot_density_process)
            self.density_centroid_dialog.show()

        elif self.density_picture_type == "emit":
            self.density_emit_dialog = PictureDialog1()
            self.density_emit_dialog.initUI()
            item.update({"pictureType":"emit"})
            self.density_emit_dialog.plot_image1(item, plot_density_process)
            self.density_emit_dialog.show()

        elif self.density_picture_type == "rms_size":
            self.density_rms_size_dialog = PictureDialog1()
            self.density_rms_size_dialog.initUI()
            item.update({"pictureType":"rms_size"})
            self.density_rms_size_dialog.plot_image1(item, plot_density_process)
            self.density_rms_size_dialog.show()

        elif self.density_picture_type == "rms_size_max":
            self.density_rms_size_max_dialog = PictureDialog1()
            self.density_rms_size_max_dialog.initUI()
            item.update({"pictureType":"rms_size_max"})
            self.density_rms_size_max_dialog.plot_image1(item, plot_density_process)
            self.density_rms_size_max_dialog.show()



    def cb_average_change(self, state):
        if state == Qt.Checked:
            self.output_plot_type = 'average'

    def cb_rms_change(self, state):
        if state == Qt.Checked:
            self.output_plot_type = 'rms'

    def updatePath(self, new_path):
        self.project_path = new_path
        self.ini_path = os.path.join(self.project_path, "InputFile", 'ini.ini')
        self.ini_obj = IniConfig()

    def cb_error_change(self, state):
        sender_checkbox = self.sender()  # 获取发送信号的复选框对象

        if sender_checkbox == self.cb_stat_error:
            if sender_checkbox.isChecked():
                self.cb_dyn_error.setChecked(False)
                self.cb_stat_dyn_error.setChecked(False)

        elif sender_checkbox == self.cb_dyn_error:
            if sender_checkbox.isChecked():
                self.cb_stat_error.setChecked(False)
                self.cb_stat_dyn_error.setChecked(False)

        elif sender_checkbox == self.cb_stat_dyn_error:
            if sender_checkbox.isChecked():
                self.cb_stat_error.setChecked(False)
                self.cb_dyn_error.setChecked(False)


        error_dic = self.get_state_dict()
        self.error_signal.emit(error_dic)

    def cb_density_plane_change(self, state):
        sender_checkbox = self.sender()  # 获取发送信号的复选框对象
        if sender_checkbox == self.cb_plane_x:
            print("找到了x")
        # if sender_checkbox == self.cb_stat_error:

    # 根据复选框状态更新 density_plane_choose
        if self.cb_plane_x.isChecked():
            self.density_plane_choose = "x"
        if self.cb_plane_y.isChecked():
            self.density_plane_choose = "y"
        if self.cb_plane_r.isChecked():
            self.density_plane_choose = "r"
        if self.cb_plane_z.isChecked():
            self.density_plane_choose = "z"


    def cb_density_picture_type_change(self, state):
        if self.cb_density.isChecked():
            self.density_picture_type = "density"
        elif self.cb_density_level.isChecked():
            self.density_picture_type = "density_level"
        elif self.cb_density_centroid.isChecked():
            self.density_picture_type = "centroid"
        elif self.cb_density_emittance.isChecked():
            self.density_picture_type = "emit"
        elif self.cb_density_rms_size.isChecked():
            self.density_picture_type = "rms_size"
        elif self.cb_density_rms_size_max.isChecked():
            self.density_picture_type = "rms_size_max"
        # print(self.density_picture_type)



    def fill_parameter(self):
        item = {"projectPath": self.project_path}
        ini_dict = self.ini_obj.create_from_file(item)
        if ini_dict['code'] == -1:
            raise Exception(ini_dict['data']['msg'])

        ini_dict = ini_dict["data"]['iniParams']

        if ini_dict['error']['error_type'] == 'stat':
            self.cb_stat_error.setChecked(True)
        elif ini_dict['error']['error_type'] == 'dyn':
            self.cb_dyn_error.setChecked(True)
        elif ini_dict['error']['error_type'] == 'stat_dyn':
            self.cb_stat_error.setChecked(True)

        self.text_seed.setText(str(ini_dict['error']['seed']))

    def get_state_dict(self):
        dic = {"error_type": "undefined", "seed": 0, "if_normal": 1}
        if self.cb_stat_error.isChecked():
            dic['error_type'] = 'stat'
        elif self.cb_dyn_error.isChecked():
            dic['error_type'] = 'dyn'
        elif self.cb_stat_dyn_error.isChecked():
            dic['error_type'] = 'stat_dyn'
        else:
            dic['error_type'] = ""

        dic["seed"] = int(self.text_seed.text())
        return dic
    def select_error_par(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        default_directory = os.path.join(self.project_path, "OutputFile")
        error_par_path, _ = QFileDialog.getOpenFileName(self, "Select  File", directory=default_directory,
                                                       options=options)

        if error_par_path:
            self.text_error_par.setText(error_par_path)
        self.error_par_file_path = error_par_path

    def select_density_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        default_directory = os.path.join(self.project_path, "OutputFile")
        error_par_path, _ = QFileDialog.getOpenFileName(self, "Select  File", directory=default_directory,
                                                       options=options)

        if error_par_path:
            self.text_density_file.setText(error_par_path)
        self.density_file_path = error_par_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageError(r'C:\Users\anxin\Desktop\test_err')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    main_window.updatePath(r'C:\Users\anxin\Desktop\test_err')
    sys.exit(app.exec_())


# app = QApplication(sys.argv)
# main_window = CavityVoltageDialog(r'C:\Users\anxin\Desktop\00000', plot_cavity_voltage )
# main_window.initUI()
# main_window.setGeometry(800, 500, 600, 650)
# main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
# main_window.show()
# sys.exit(app.exec_())