import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QCheckBox, QMessageBox, QButtonGroup

import os
from user.user_qt.user_defined import MyQLineEdit

from PyQt5.QtCore import Qt, pyqtSignal
from utils.readfile import read_txt, read_dst
from user.user_qt.user_defined import treat_err, treat_err2, gray240
from utils.inputconfig import InputConfig
from apis.qt_api.api import create_from_file_input_ini, write_to_file_input_ini
from utils.tool import safe_float, safe_int, safe_str
from utils.tool import safe_str

class PageInput(QWidget):
    input_signal = pyqtSignal(dict)

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        # self.multithreading_num = -1
        self.field_source_path = None
        self.longlimits_start_num = 0

        self.default_grid_param = {
            "FFT" :
                {
                    "grid_numofgrid": [64,64,64],
                    "grid_meshrms": [6.5,6.5,6.5]
                },
            "SPICNIC":
                {
                    "grid_numofgrid": [18, 18, 18],
                    "grid_meshrms": [3.5, 3.5, 3.5]
                }
        }

        self.initUI()

    def initUI(self):
        # print(self.project_path)
        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QHBoxLayout()

        # 创建一个垂直组合框
        vertical_group_box_main = QGroupBox("Operation setting")

        vertical_layout_main = QVBoxLayout()
##########################################################################
        group_box_mulp_env = QGroupBox()

        hbox_mulp_env = QHBoxLayout()

        self.cb_mulp = QCheckBox('Multi_particles', self)
        self.cb_mulp.stateChanged.connect(self.cb_basic_change)

        self.cb_env = QCheckBox('Envelope', self)
        self.cb_env.stateChanged.connect(self.cb_basic_change)



        hbox_mulp_env.addWidget(self.cb_mulp)
        hbox_mulp_env.addWidget(self.cb_env)

        group_box_mulp_env.setLayout(hbox_mulp_env)


##########################################################
        group_box_sc_method = QGroupBox()
        sc_method_layout = QHBoxLayout()

        #111
        self.cb_fft = QCheckBox('FFT', self)
        self.cb_fft.setFixedWidth(70)

        self.cb_picnic = QCheckBox('SPICNIC', self)
        self.cb_picnic.setFixedWidth(70)

        self.cb_fft.stateChanged.connect(self.cb_sc_method_change)
        self.cb_picnic.stateChanged.connect(self.cb_sc_method_change)

        sc_method_layout.addWidget(self.cb_fft)
        sc_method_layout.addStretch(1)
        sc_method_layout.addWidget(self.cb_picnic)
        sc_method_layout.addStretch(1)
        group_box_sc_method.setLayout(sc_method_layout)

#############################################


        sc_grid_group_box = QGroupBox()

        sc_grid_layout = QVBoxLayout()

        # -----------------------------
        # 网格数模式选择：自适应 / 手动
        # -----------------------------
        sc_grid_mode_layout = QHBoxLayout()

        self.cb_adaptive_grid = QCheckBox("Adaptive grid", self)
        self.cb_manual_grid = QCheckBox("Manual grid", self)

        # 创建按钮组
        self.grid_mode_group = QButtonGroup(self)

        # 设置互斥
        self.grid_mode_group.setExclusive(True)

        # 加入两个 checkbox
        self.grid_mode_group.addButton(self.cb_adaptive_grid)
        self.grid_mode_group.addButton(self.cb_manual_grid)

        # 设置默认选中
        self.cb_adaptive_grid.setChecked(True)
        self.cb_adaptive_grid.setFixedWidth(120)
        self.cb_manual_grid.setFixedWidth(120)



        self.cb_adaptive_grid.stateChanged.connect(self.cb_grid_mode_change)
        self.cb_manual_grid.stateChanged.connect(self.cb_grid_mode_change)

        sc_grid_mode_layout.addWidget(self.cb_adaptive_grid)
        sc_grid_mode_layout.addStretch(1)
        sc_grid_mode_layout.addWidget(self.cb_manual_grid)
        sc_grid_mode_layout.addStretch(1)



        # -----------------------------
        # Numofgrid
        # -----------------------------

        sc_grid_numofgrid_layout = QHBoxLayout()
        sc_grid_numofgrid_label = QLabel("Numofgrid")
        sc_grid_numofgrid_label.setMinimumWidth(84)
        self.sc_grid_numofgrid_x_text = QLineEdit()
        self.sc_grid_numofgrid_y_text = QLineEdit()
        self.sc_grid_numofgrid_z_text = QLineEdit()

        sc_grid_numofgrid_layout.addWidget(sc_grid_numofgrid_label)
        sc_grid_numofgrid_layout.addWidget(self.sc_grid_numofgrid_x_text)
        sc_grid_numofgrid_layout.addWidget(self.sc_grid_numofgrid_y_text)
        sc_grid_numofgrid_layout.addWidget(self.sc_grid_numofgrid_z_text)


        #############
        sc_grid_meshrms_layout = QHBoxLayout()
        sc_grid_meshrms_label = QLabel("MeshRms")
        sc_grid_meshrms_label.setMinimumWidth(84)
        self.sc_grid_meshrms_x_text = QLineEdit()
        self.sc_grid_meshrms_y_text = QLineEdit()
        self.sc_grid_meshrms_z_text = QLineEdit()

        sc_grid_meshrms_layout.addWidget(sc_grid_meshrms_label)
        sc_grid_meshrms_layout.addWidget(self.sc_grid_meshrms_x_text)
        sc_grid_meshrms_layout.addWidget(self.sc_grid_meshrms_y_text)
        sc_grid_meshrms_layout.addWidget(self.sc_grid_meshrms_z_text)

        grid_param_edits = [
            self.sc_grid_numofgrid_x_text,
            self.sc_grid_numofgrid_y_text,
            self.sc_grid_numofgrid_z_text,
            self.sc_grid_meshrms_x_text,
            self.sc_grid_meshrms_y_text,
            self.sc_grid_meshrms_z_text,
        ]

        for edit in grid_param_edits:
            edit.editingFinished.connect(self.update_default_grid_param_from_ui)

        sc_grid_layout.addLayout(sc_grid_mode_layout)
        sc_grid_layout.addLayout(sc_grid_numofgrid_layout)
        sc_grid_layout.addLayout(sc_grid_meshrms_layout)

        sc_grid_group_box.setLayout(sc_grid_layout)
###############fft
        # fft_layout = QHBoxLayout()
        #
        # self.cb_fft = QCheckBox('FFT', self)
        # self.cb_fft.setFixedWidth(70)
        #
        # fft_grid_layout = QVBoxLayout()
        #
        # fft_numofgrid_layout = QHBoxLayout()
        # fft_numofgrid_label = QLabel("Numofgrid")
        # fft_numofgrid_label.setMinimumWidth(84)
        # self.fft_numofgrid_x_text = QLineEdit('64')
        # self.fft_numofgrid_y_text = QLineEdit('64')
        # self.fft_numofgrid_z_text = QLineEdit('64')
        #
        # fft_numofgrid_layout.addWidget(fft_numofgrid_label)
        # fft_numofgrid_layout.addWidget(self.fft_numofgrid_x_text)
        # fft_numofgrid_layout.addWidget(self.fft_numofgrid_y_text)
        # fft_numofgrid_layout.addWidget(self.fft_numofgrid_z_text)
        #
        #
        # #############
        # fft_meshrms_layout = QHBoxLayout()
        # fft_meshrms_label = QLabel("MeshRms")
        # fft_meshrms_label.setMinimumWidth(84)
        # self.fft_meshrms_x_text = QLineEdit('6.5')
        # self.fft_meshrms_y_text = QLineEdit('6.5')
        # self.fft_meshrms_z_text = QLineEdit('6.5')
        #
        # fft_meshrms_layout.addWidget(fft_meshrms_label)
        # fft_meshrms_layout.addWidget(self.fft_meshrms_x_text)
        # fft_meshrms_layout.addWidget(self.fft_meshrms_y_text)
        # fft_meshrms_layout.addWidget(self.fft_meshrms_z_text)
        #
        #
        # fft_grid_layout.addLayout(fft_numofgrid_layout)
        # fft_grid_layout.addLayout(fft_meshrms_layout)
        #
        # fft_layout.addWidget(self.cb_fft)
        # fft_layout.addLayout(fft_grid_layout)
########################
        # picnic_layout = QHBoxLayout()

        # self.cb_picnic = QCheckBox('PICNIC', self)
        # self.cb_picnic.setFixedWidth(70)
        # picnic_grid_layout = QVBoxLayout()

        # picnic_numofgrid_layout = QHBoxLayout()
        # picnic_numofgrid_label = QLabel("Numofgrid")
        # picnic_numofgrid_label.setMinimumWidth(84)
        # self.picnic_numofgrid_x_text = QLineEdit("18")
        # self.picnic_numofgrid_y_text = QLineEdit("18")
        # self.picnic_numofgrid_z_text = QLineEdit("18")
        #
        # picnic_numofgrid_layout.addWidget(picnic_numofgrid_label)
        # picnic_numofgrid_layout.addWidget(self.picnic_numofgrid_x_text)
        # picnic_numofgrid_layout.addWidget(self.picnic_numofgrid_y_text)
        # picnic_numofgrid_layout.addWidget(self.picnic_numofgrid_z_text)

        #############
        # picnic_meshrms_layout = QHBoxLayout()
        # picnic_meshrms_label = QLabel("MeshRms")
        # picnic_meshrms_label.setMinimumWidth(84)
        # self.picnic_meshrms_x_text = QLineEdit("3.5")
        # self.picnic_meshrms_y_text = QLineEdit("3.5")
        # self.picnic_meshrms_z_text = QLineEdit("3.5")

        # picnic_meshrms_layout.addWidget(picnic_meshrms_label)
        # picnic_meshrms_layout.addWidget(self.picnic_meshrms_x_text)
        # picnic_meshrms_layout.addWidget(self.picnic_meshrms_y_text)
        # picnic_meshrms_layout.addWidget(self.picnic_meshrms_z_text)

        # picnic_grid_layout.addLayout(picnic_numofgrid_layout)
        # picnic_grid_layout.addLayout(picnic_meshrms_layout)

        # picnic_layout.addWidget(self.cb_picnic)
        # picnic_layout.addLayout(picnic_grid_layout)

        # line = QFrame(self)
        # line.setFrameShape(QFrame.HLine)
        # line.setFrameShadow(QFrame.Sunken)
        #
        # label_sc_method = QLabel("SCMethod")
        #
        # sc_method_layout.addWidget(label_sc_method)
        # sc_method_layout.addLayout(fft_layout)
        # sc_method_layout.addWidget(line)
        # sc_method_layout.addLayout(picnic_layout)
        #
        #
        # group_box_sc_method.setLayout(sc_method_layout)
        #
        # self.cb_fft.stateChanged.connect(self.cb_sc_method_change)
        # self.cb_picnic.stateChanged.connect(self.cb_sc_method_change)

 ##########################################################
        # # group_box_multithreading = QGroupBox()
        #
        # hbox_multithreading = QHBoxLayout()
        #
        # multithreading_label = QLabel("MultiThreading")
        # # default_size = multithreading_label.sizeHint()
        # # print("Default Size:", default_size) #72 12
        # # self.multithreading_x_text = QLineEdit()
        #
        # self.multithreading_checkbox = QCheckBox('Using Multithreading', self)
        # self.multithreading_checkbox.stateChanged.connect(self.multithreading_change)
        #
        # hbox_multithreading.addWidget(multithreading_label)
        # # hbox_multithreading.addWidget(self.multithreading_x_text)
        # hbox_multithreading.addWidget(self.multithreading_checkbox)
        # group_box_multithreading.setLayout(hbox_multithreading)
        ##########################################################
        group_box_scan_phase = QGroupBox()

        hbox_scan_phase = QHBoxLayout()

        scan_phase_label = QLabel("Scan Phase")
        scan_phase_label.setMinimumWidth(84)

        # self.scan_phase_text = QLineEdit()
        self.scan_phase_combo = QComboBox(self)
        self.scan_phase_combo.addItem("Not Scan Phase")
        self.scan_phase_combo.addItem("Scan Phase")
        self.scan_phase_combo.addItem("Read Phase")

        self.scan_phase_combo.currentIndexChanged.connect(self.scan_phase_selection)

        hbox_scan_phase.addWidget(scan_phase_label)
        hbox_scan_phase.addWidget(self.scan_phase_combo)
        # hbox_scan_phase.addWidget(self.scan_phase_text)
        group_box_scan_phase.setLayout(hbox_scan_phase)

        ##########################################################
        group_box_sc_use = QGroupBox()
        hbox_sc_use = QHBoxLayout()

        sc_use_label = QLabel("Space Charge")
        sc_use_label.setMinimumWidth(84)

        self.sc_use_checkbox = QCheckBox('Calculate Space Charge', self)
        self.sc_use_checkbox.stateChanged.connect(self.sc_use_change)

        hbox_sc_use.addWidget(sc_use_label)
        hbox_sc_use.addWidget(self.sc_use_checkbox)
        group_box_sc_use.setLayout(hbox_sc_use)

        #####################################################
        group_box_field_source = QGroupBox()

        layout_field_source = QVBoxLayout()

        label_field_source = QLabel("Field Source")

        layout_field_source_choose = QHBoxLayout()
        self.button_select_field_source = QPushButton(QApplication.style().standardIcon(32),"")
        self.button_select_field_source.clicked.connect(self.select_field_source)
        self.text_field_source = MyQLineEdit(" ")

        layout_field_source_choose.addWidget(self.button_select_field_source)
        layout_field_source_choose.addWidget(self.text_field_source)

        layout_field_source.addWidget(label_field_source)
        layout_field_source.addLayout(layout_field_source_choose)

        group_box_field_source.setLayout(layout_field_source)



        ###################################

        group_box_sc_step = QGroupBox()
        vbox_sc_step = QVBoxLayout()

        hbox_sc_step1 = QHBoxLayout()

        sc_step_label = QLabel('Space-charge step')
        self.sc_step_text = QLineEdit()

        hbox_sc_step2 = QHBoxLayout()
        self.sc_step_meter_checkbox = QCheckBox('meter', self)
        self.sc_step_beta_checkbox = QCheckBox('\u03B2\u03BB', self)

        self.sc_step_meter_checkbox.stateChanged.connect(self.sc_step_meter_change)
        self.sc_step_beta_checkbox.stateChanged.connect(self.sc_step_beta_change)

        hbox_sc_step1.addWidget(sc_step_label)
        hbox_sc_step1.addWidget(self.sc_step_text)

        hbox_sc_step1.addWidget(self.sc_step_meter_checkbox)
        hbox_sc_step1.addWidget(self.sc_step_beta_checkbox)

        vbox_sc_step.addLayout(hbox_sc_step1)

        group_box_sc_step.setLayout(vbox_sc_step)
        #
        ##########################################################
        group_box_step_per_period = QGroupBox()
        vbox_step_per_period = QVBoxLayout()

        step_per_period_label = QLabel("Calsulation step(\u03B2\u03BB)")
        step_per_period_label.setMinimumWidth(100)

        self.step_per_period_text = QLineEdit()


        vbox_step_per_period.addWidget(step_per_period_label)
        vbox_step_per_period.addWidget(self.step_per_period_text)
        group_box_step_per_period.setLayout(vbox_step_per_period)
        ########################################################

        group_box_dumpPeriodicity = QGroupBox()
        vbox_dumpPeriodicity= QVBoxLayout()

        dumpPeriodicity_label = QLabel("Output step in plt")
        dumpPeriodicity_label.setMinimumWidth(100)

        self.dumpPeriodicity_text = QLineEdit()


        vbox_dumpPeriodicity.addWidget(dumpPeriodicity_label)
        vbox_dumpPeriodicity.addWidget(self.dumpPeriodicity_text)
        group_box_dumpPeriodicity.setLayout(vbox_dumpPeriodicity)
        ###################################################

        #density 控制

        group_box_density_control = QGroupBox()

        layout_density_control= QHBoxLayout()

        #111
        self.cb_generate_density = QCheckBox('Generate density file', self)
        # self.cb_generate_density.setFixedWidth(70)
        self.cb_generate_density.stateChanged.connect(self.cd_genenrate_density_file_change)

        self.label_density_grid = QLabel('Denity grid')
        self.label_density_grid.setMinimumWidth(70)

        self.text_density_grid = QLineEdit("")
        self.text_density_grid.setMinimumWidth(70)

        layout_density_control.addWidget(self.cb_generate_density)
        layout_density_control.addStretch(1)
        layout_density_control.addWidget(self.label_density_grid)
        layout_density_control.addWidget(self.text_density_grid)
        layout_density_control.addStretch(1)
        group_box_density_control.setLayout(layout_density_control)

        #############################################################
        group_box_longlimits = QGroupBox()

        layout_longlimits= QHBoxLayout()

        #111
        self.cb_longlimits_start = QCheckBox('Longlimits', self)
        # self.cb_generate_density.setFixedWidth(70)
        # self.cb_Longlimits_start.stateChanged.connect(self.cd_longlimits_start_change)

        self.label_longlimits_phase = QLabel('Phase')
        # self.label_longlimits_phase.setMinimumWidth(70)
        self.text_longlimits_phase = QLineEdit("")
        self.text_longlimits_phase.setMinimumWidth(70)
        self.label_longlimits_phase_unit = QLabel('deg')


        self.label_longlimits_energy = QLabel('Energy')
        # self.label_longlimits_energy.setMinimumWidth(70)
        self.text_longlimits_energy = QLineEdit("")
        self.text_longlimits_energy.setMinimumWidth(70)
        self.label_longlimits_energy_unit = QLabel('MeV')

        layout_longlimits.addWidget(self.cb_longlimits_start)
        layout_longlimits.addStretch(2)
        layout_longlimits.addWidget(self.label_longlimits_phase)
        layout_longlimits.addWidget(self.text_longlimits_phase)
        layout_longlimits.addWidget(self.label_longlimits_phase_unit)
        layout_longlimits.addStretch(2)
        layout_longlimits.addWidget(self.label_longlimits_energy)
        layout_longlimits.addWidget(self.text_longlimits_energy)
        layout_longlimits.addWidget(self.label_longlimits_energy_unit)

        layout_longlimits.addStretch(1)
        group_box_longlimits.setLayout(layout_longlimits)

########################################################################
        group_box_boundary = QGroupBox()
        layout_boundary= QHBoxLayout()
        self.cb_boundary_start = QCheckBox('Boundary', self)

        layout_boundary.addWidget(self.cb_boundary_start)
        group_box_boundary.setLayout(layout_boundary)

########################################################################
        group_box_randomseed = QGroupBox()
        layout_randomseed= QHBoxLayout()

        label_randomseed = QLabel("Random seed of input beam")
        self.text_randomseed = QLineEdit()
        self.text_randomseed.setMinimumWidth(70)

        layout_randomseed.addWidget(label_randomseed)
        layout_randomseed.addStretch(1)
        layout_randomseed.addWidget(self.text_randomseed)
        layout_randomseed.addStretch(1)

        group_box_randomseed.setLayout(layout_randomseed)



##########################################################################

        vertical_layout_main.addWidget(group_box_mulp_env)
        vertical_layout_main.addWidget(group_box_sc_method)
        vertical_layout_main.addWidget(sc_grid_group_box)
        # vertical_layout_main.addWidget(group_box_multithreading)
        # vertical_layout_main.addWidget(group_box_scan_phase)
        vertical_layout_main.addWidget(group_box_step_per_period)
        vertical_layout_main.addWidget(group_box_dumpPeriodicity)
        vertical_layout_main.addWidget(group_box_sc_use)
        vertical_layout_main.addWidget(group_box_field_source)
        vertical_layout_main.addWidget(group_box_density_control)
        vertical_layout_main.addWidget(group_box_longlimits)
        vertical_layout_main.addWidget(group_box_boundary)
        vertical_layout_main.addWidget(group_box_randomseed)

        vertical_layout_main.addWidget(group_box_sc_step)


        vertical_group_box_main.setLayout(vertical_layout_main)
        #########################################################################################

        layout.addWidget(vertical_group_box_main)
        self.setLayout(layout)

    def select_field_source(self):
        # options = QFileDialog.Options()
        # options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        # default_directory = self.project_path
        # field_source_path, _ = QFileDialog.getOpenFileName(self, "Select  File", directory=default_directory,
        #                                                options=options)
        #
        # if field_source_path:
        #     self.text_field_source.setText(field_source_path)
        # self.field_source_path = field_source_path
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        default_directory = self.project_path
        field_source_path = QFileDialog.getExistingDirectory(self, "Select Directory", directory=default_directory,options=options)
        field_source_path = os.path.normpath(field_source_path)

        if field_source_path:
            self.text_field_source.setText(field_source_path)
        self.field_source_path = field_source_path

    def cb_basic_change(self, state):
        sender_checkbox = self.sender()  # 获取发送信号的复选框对象
        if sender_checkbox == self.cb_mulp:  # 如果发送信号的对象是 cb_mulp 复选框
            self.cb_env.setChecked(not sender_checkbox.isChecked())  # 设置 cb_env 与 cb_mulp 相反的状态
        elif sender_checkbox == self.cb_env:  # 如果发送信号的对象是 cb_env 复选框
            self.cb_mulp.setChecked(not sender_checkbox.isChecked())  # 设置 cb_mulp 与 cb_env 相反的状态

        dic = {}

        if self.cb_mulp.isChecked():
            dic["sim_type"] = 'mulp'
            self.input_signal.emit(dic)
        elif self.cb_env.isChecked():
            dic["sim_type"] = 'env'
            self.input_signal.emit(dic)
        else:
            dic["sim_type"] = None
            self.input_signal.emit(dic)
        self.mulp_env_behavior()

    def cb_sc_method_change(self, state):
        sender_checkbox = self.sender()  # 获取发送信号的复选框对象
        if sender_checkbox == self.cb_fft:
            self.cb_picnic.setChecked(not sender_checkbox.isChecked())
        elif sender_checkbox == self.cb_picnic:
            self.cb_fft.setChecked(not sender_checkbox.isChecked())

        self.cb_grid_mode_change()



    def updatePath(self, new_path):
        self.project_path = new_path


    def fill_parameter(self):

        item = {"projectPath": self.project_path}
        input_ini_res = create_from_file_input_ini(item)


        input_ini_res = input_ini_res['data']["inputiniParams"]


        if input_ini_res.get('sim_type') == "mulp":
            self.cb_mulp.setChecked(True)
        elif input_ini_res.get('sim_type') == "env":
            self.cb_env.setChecked(True)


        if input_ini_res.get('scmethod') == "FFT":
            self.cb_fft.setChecked(True)
        elif input_ini_res.get('scmethod') == "SPICNIC":
            self.cb_picnic.setChecked(True)
        ##############################
        sc_method_v1 = input_ini_res.get('scmethod')
        if input_ini_res.get("adaptive_grid") == 0:
            self.default_grid_param[sc_method_v1]["grid_numofgrid"] = [input_ini_res.get("numofgrid_x"),
                                                                       input_ini_res.get("numofgrid_y"), input_ini_res.get("numofgrid_z")]
            self.default_grid_param[sc_method_v1]["grid_meshrms"] = [input_ini_res.get("meshrms_x"),
                                                                       input_ini_res.get("meshrms_y"), input_ini_res.get("meshrms_z")]


        if input_ini_res.get("adaptive_grid") == 1:
            self.sc_adaptive_grid_checkbox.setChecked(True)
        elif input_ini_res.get("adaptive_grid") == 0:
            self.sc_adaptive_grid_checkbox.setChecked(False)
    #####################################


        # self.scan_phase_num = safe_int(input_ini_res.get('scanphase'), 1)
        # self.scan_phase_combo.setCurrentIndex(self.scan_phase_num)

        self.sc_use_num = safe_int(input_ini_res.get('spacecharge'), 1)
        if self.sc_use_num == 0:
            self.sc_use_checkbox.setChecked(False)
        elif self.sc_use_num == 1:
            self.sc_use_checkbox.setChecked(True)

        self.step_per_period_text.setText(safe_str(input_ini_res.get('steppercycle'), "100"))

        self.dumpPeriodicity_text.setText(safe_str(input_ini_res.get('dumpperiodicity'), "0"))

        longlimits_start = safe_int(input_ini_res.get('longlimits_start', 0))
        longlimits_phase = safe_str(input_ini_res.get('longlimits_phase', 0))
        longlimits_energy = safe_str(input_ini_res.get('longlimits_energy', 0))

        if longlimits_start == 0:
            self.cb_longlimits_start.setChecked(False)
        elif longlimits_start == 1:
            self.cb_longlimits_start.setChecked(True)

        self.text_longlimits_phase.setText(longlimits_phase)
        self.text_longlimits_energy.setText(longlimits_energy)

        boundary_start = safe_int(input_ini_res.get('boundary', 0))

        if boundary_start == 0:
            self.cb_boundary_start.setChecked(False)
        elif boundary_start == 1:
            self.cb_boundary_start.setChecked(True)

        # 对于包络模型的输入
        self.text_field_source.setText(safe_str(input_ini_res["fieldSource"]))


        self.pchistogram_start_num = safe_int(input_ini_res.get('pchistogram_start'), 0)

        if self.pchistogram_start_num == 0:
            self.cb_generate_density.setChecked(False)
        elif self.pchistogram_start_num == 1:
            self.cb_generate_density.setChecked(True)


        self.text_density_grid.setText(safe_str(input_ini_res["pchistogram_grid"], "300"))

        self.text_randomseed.setText(safe_str(input_ini_res["randomseed"], "0"))
        # 对于包络模型的输入
        if input_ini_res.get('spacechargelong') is not None:
            self.sc_step_text.setText(input_ini_res.get('spacechargelong'))

        sc_step_type = input_ini_res.get('scsteptype')
        if sc_step_type is not None:
            if int(sc_step_type) == 0:
                self.sc_step_meter_checkbox.setChecked(True)
            elif int(sc_step_type) == 1:
                self.sc_step_beta_checkbox.setChecked(True)





# if input_ini_res.get('scmethod') == "FFT":
#     self.cb_fft.setChecked(True)
#     # if isinstance(input_res.get("numofgrid"), list) and len(input_res.get("numofgrid")) == 3:
#     #     self.fft_numofgrid_x_text.setText(input_res.get("numofgrid")[0])
#     #     self.fft_numofgrid_y_text.setText(input_res.get("numofgrid")[1])
#     #     self.fft_numofgrid_z_text.setText(input_res.get("numofgrid")[2])
#     #
#     # if isinstance(input_res.get('meshrms'), list) and len(input_res.get('meshrms')) == 3:
#     #     self.fft_meshrms_x_text.setText(input_res.get('meshrms')[0])
#     #     self.fft_meshrms_y_text.setText(input_res.get('meshrms')[1])
#     #     self.fft_meshrms_z_text.setText(input_res.get('meshrms')[2])
#
#
# elif input_ini_res.get('scmethod') == "SPICNIC":
#     self.cb_picnic.setChecked(True)
#     # if isinstance(input_res.get("numofgrid"), list) and len(input_res.get("numofgrid")) == 3:
#     #     self.picnic_numofgrid_x_text.setText(input_res.get("numofgrid")[0])
#     #     self.picnic_numofgrid_y_text.setText(input_res.get("numofgrid")[1])
#     #     self.picnic_numofgrid_z_text.setText(input_res.get("numofgrid")[2])
#     #
#     # if isinstance(input_res.get('meshrms'), list) and len(input_res.get('meshrms')) == 3:
#     #     self.picnic_meshrms_x_text.setText(input_res.get('meshrms')[0])
#     #     self.picnic_meshrms_y_text.setText(input_res.get('meshrms')[1])
#     #     self.picnic_meshrms_z_text.setText(input_res.get('meshrms')[2])
#
#
# # self.multithreading_num = int(input_res.get('multithreading', 0))
#
# # if self.multithreading_num == 0:
# #     self.multithreading_checkbox.setChecked(False)
# #
# # elif self.multithreading_num == 1:
# #     self.multithreading_checkbox.setChecked(True)


    def generate_input_list(self, ):

        res = {}
        if self.cb_mulp.isChecked():
            res["sim_type"] = "mulp"
        elif self.cb_env.isChecked():
            # res.append(["!simtype",  "env"])
            res["sim_type"] = "env"



        if self.cb_fft.isChecked():
            res["scmethod"] = "FFT"
        elif self.cb_picnic.isChecked():
            res["scmethod"] = "SPICNIC"

        # res["scanphase"] =self.scan_phase_combo.currentIndex()

        if self.sc_use_checkbox.isChecked():
            res["spacecharge"] = 1
        else:
            res["spacecharge"] = 0

        res['steppercycle'] = safe_int(self.step_per_period_text.text(), 10)

        if self.dumpPeriodicity_text.text():
            res["dumpperiodicity"] = safe_int(self.dumpPeriodicity_text.text(), 0)

        res["pchistogram_start"] = self.pchistogram_start_num
        res["pchistogram_grid"] = self.text_density_grid.text()

        res["fieldSource"] = self.text_field_source.text()

        if self.cb_longlimits_start.isChecked():
            res["longlimits_start"] = 1
        else:
            res["longlimits_start"] = 0

        res["longlimits_phase"] =safe_float( self.text_longlimits_phase.text() )
        res["longlimits_energy"] =safe_float( self.text_longlimits_energy.text() )

        if self.cb_boundary_start.isChecked():
            res["boundary"] = 1
        else:
            res["boundary"] = 0

        res["randomseed"] = safe_int(self.text_randomseed.text())

        if self.sc_step_text.text():
            res['spacechargelong'] = safe_int(self.sc_step_text.text(), 1)
        else:
            res['spacechargelong'] = None



        if self.sc_step_meter_checkbox.isChecked():
            res['spacechargetype'] == 0
        elif self.sc_step_beta_checkbox.isChecked():
            res['spacechargetype'] == 1

        ###########################
        if  self.cb_adaptive_grid.isChecked():
            adaptive_grid = 1
        else:
            adaptive_grid = 0
        res["adaptive_grid"] = adaptive_grid
        res['numofgrid'] = [
                    safe_int(self.sc_grid_numofgrid_x_text.text()), safe_int(self.sc_grid_numofgrid_y_text.text()),
                    safe_int(self.sc_grid_numofgrid_z_text.text())]

        res['meshrms'] = [safe_float(self.sc_grid_meshrms_x_text.text()), safe_float(self.sc_grid_meshrms_y_text.text()),
                          safe_float(self.sc_grid_meshrms_z_text.text())]
        return res


    #     # res.append(['SCMethod', "FFT"])
    #     res["scmethod"] = "FFT"
    #     # res.append(['numofgrid', self.fft_numofgrid_x_text.text(), self.fft_numofgrid_y_text.text(),
    #     #             self.fft_numofgrid_z_text.text()])
    #     # res.append(['MeshRms', self.fft_meshrms_x_text.text(), self.fft_meshrms_y_text.text(),
    #     #             self.fft_meshrms_z_text.text()])
    #
    # elif self.cb_picnic.isChecked():
    # # res.append(['SCMethod', "PICNIC"])
    # res["scmethod"] = "SPICNIC"
    #
    # # res.append(['numofgrid', self.picnic_numofgrid_x_text.text(), self.picnic_numofgrid_y_text.text(),
    # #             self.picnic_numofgrid_z_text.text()])
    # # res.append(['MeshRms', self.picnic_meshrms_x_text.text(), self.picnic_meshrms_y_text.text(),
    # #             self.picnic_meshrms_z_text.text()])
    #
    # # if self.multithreading_checkbox.isChecked():
    # #     res.append(['MultiThreading', '1'])
    # # elif not self.multithreading_checkbox.isChecked():
    # #     res.append(['MultiThreading', '0'])
    def save_input(self, ):
        input_ini_dic = self.generate_input_list()
        item = {"projectPath": self.project_path}

        res = write_to_file_input_ini(item, input_ini_dic)
        if res["code"] == -1:
            raise Exception(res['data']['msg'])


        # # 打开文件以写入数据
        # with open(input_path, 'w', encoding='utf-8') as file:
        #     # 遍历嵌套列表的每个子列表
        #     for sublist in input_list:
        #         # 将子列表中的元素转换为字符串，并使用逗号分隔
        #         line = '   '.join(map(str, sublist))
        #         # 将每个子列表的字符串写入文件
        #         file.write(line + '\n')

    # def multithreading_change(self, state):
    #     if state == Qt.Checked:
    #         self.multithreading_num = 1
    #     else:
    #         self.multithreading_num = 0

    def sc_use_change(self, state):
        if state == Qt.Checked:
            self.sc_use_num = 1
        else:
            self.sc_use_num = 0

    def cd_genenrate_density_file_change(self, state):
        if state == Qt.Checked:
            self.pchistogram_start_num = 1
        else:
            self.pchistogram_start_num = 0

    def scan_phase_selection(self, index):
        # 处理用户的选择
        selected_option = self.sender().currentText()

    def sc_step_meter_change(self, state):
        # 获取发送信号的复选框
        if state == Qt.Checked:
            self.sc_step_beta_checkbox.setChecked(False)


    def sc_step_beta_change(self, state):
        # 获取发送信号的复选框
        if state == Qt.Checked:
            self.sc_step_meter_checkbox.setChecked(False)

    def inspect(self):
        if not self.step_per_period_text.text():
            e = "Missing calculation step"
            QMessageBox.warning(None, 'Error', e)
            return False
        else:
            return True

    def mulp_env_behavior(self):
        # mulp_box = [self.cb_fft, self.cb_picnic, self.multithreading_checkbox]
        mulp_box = [self.cb_fft, self.cb_picnic]

        # self.fft_numofgrid_x_text, self.fft_numofgrid_y_text, self.fft_numofgrid_z_text,
        # self.fft_meshrms_x_text, self.fft_meshrms_y_text, self.fft_meshrms_z_text,
        # self.picnic_numofgrid_x_text, self.picnic_numofgrid_y_text, self.picnic_numofgrid_z_text,
        # self.picnic_meshrms_x_text, self.picnic_meshrms_y_text, self.picnic_meshrms_z_text,
        mulp_line = [self.step_per_period_text, self.dumpPeriodicity_text
                     ]

        env_line = [self.sc_step_text]
        env_box = [self.sc_step_meter_checkbox, self.sc_step_beta_checkbox]

        #如果是多粒子模式
        if self.cb_mulp.isChecked():
            for line_edit in env_line:
                line_edit.setEnabled(False)
            for box in env_box:
                box.setEnabled(False)


            for line_edit in mulp_line:
                line_edit.setEnabled(True)

            for box in mulp_box:
                box.setEnabled(True)

            # self.scan_phase_combo.setEnabled(True)
            # self.scan_phase_combo.setStyleSheet(f"")

        elif self.cb_env.isChecked():
            for line_edit in env_line:
                line_edit.setEnabled(True)
            for box in env_box:
                box.setEnabled(True)

            for line_edit in mulp_line:
                line_edit.setEnabled(False)
            for box in mulp_box:
                box.setEnabled(False)


            self.scan_phase_combo.setEnabled(False)
            self.scan_phase_combo.setStyleSheet(f"QComboBox {{ background-color:  {gray240} }}")
    def cb_grid_mode_change(self):
        sender = self.sender()

        numofgrid_element = [self.sc_grid_numofgrid_x_text, self.sc_grid_numofgrid_y_text,
                             self.sc_grid_numofgrid_z_text]

        meshrms_element= [self.sc_grid_meshrms_x_text, self.sc_grid_meshrms_y_text,
                          self.sc_grid_meshrms_z_text
        ]


        sc_method = None
        if self.cb_fft.isChecked():
            sc_method = 'FFT'
        elif self.cb_picnic.isChecked():
            sc_method = 'SPICNIC'

        if self.cb_adaptive_grid.isChecked():
            print("选择 Adaptive grid")
            # Numofgrid 自适应时不允许手动输入
            for i in range(3):
                numofgrid_element[i].setEnabled(False)
                meshrms_element[i].setEnabled(False)

        elif self.cb_manual_grid.isChecked():
            print("选择 Manual grid")
            for i in range(3):
                numofgrid_element[i].setEnabled(True)
                meshrms_element[i].setEnabled(True)
                numofgrid_element[i].setText(safe_str(self.default_grid_param[sc_method]["grid_numofgrid"][i]))
                meshrms_element[i].setText(safe_str(self.default_grid_param[sc_method]["grid_meshrms"][i]))

    def update_default_grid_param_from_ui(self):
        if getattr(self, "_updating_grid_ui", False):
            return

        sc_method = None
        if self.cb_fft.isChecked():
            sc_method = 'FFT'
        elif self.cb_picnic.isChecked():
            sc_method = 'SPICNIC'

        try:
            numofgrid = [
                safe_int(self.sc_grid_numofgrid_x_text.text()),
                safe_int(self.sc_grid_numofgrid_y_text.text()),
                safe_int(self.sc_grid_numofgrid_z_text.text()),
            ]

            meshrms = [
                safe_float(self.sc_grid_meshrms_x_text.text()),
                safe_float(self.sc_grid_meshrms_y_text.text()),
                safe_float(self.sc_grid_meshrms_z_text.text()),
            ]

        except ValueError:
            print("网格参数输入格式错误")
            return

        self.default_grid_param[sc_method]["grid_numofgrid"] = numofgrid
        self.default_grid_param[sc_method]["grid_meshrms"] = meshrms

        print("已同步修改：", sc_method, self.default_grid_param[sc_method])
# sec_sc = CollapsibleSection("空间电荷")
# chk_sc = QtWidgets.QCheckBox("启用空间电荷计算")
# sec_sc.form.addRow(chk_sc)
# grid = QtWidgets.QSpinBox();
# grid.setRange(16, 2048);
# grid.setValue(300)
# step = QtWidgets.QDoubleSpinBox();
# step.setRange(0.0, 10.0);
# step.setDecimals(4);
# step.setSuffix(" m")
# sec_sc.form.addRow("Density grid：", grid)
# sec_sc.form.addRow("Space-charge step：", step)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageInput(r'F:\using\test_avas_qt\cafe_avas')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.fill_parameter()
    main_window.show()
    sys.exit(app.exec_())