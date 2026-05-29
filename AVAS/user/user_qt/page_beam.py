import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget,QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QGroupBox,\
    QComboBox, QSizePolicy, QMessageBox,QPushButton, QCheckBox
import os
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QStandardPaths

from conf.contants import edst_picture_title_dict
from user.user_qt.user_defined import MyQLineEdit

from PyQt5.QtCore import Qt
from utils.readfile import read_txt, read_dst
from utils.treatfile import copy_file

from aftertreat.dataanalysis.caltwiss import CalTwiss
from user.user_qt.user_defined import treat_err, treat_err2
from utils.treat_directory import list_files_in_directory
from utils.treatfile import split_file, file_in_directory
from utils.beamconfig import BeamConfig
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from user.user_qt.page_utils.phaseellipse_dialog import PhaseEllipseWidget

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QLineEdit,
    QLabel, QFileDialog, QGridLayout, QSizePolicy, QRadioButton, QButtonGroup
)
gray240 = "rgb(240, 240, 240)"
from apis.qt_api.api import cal_beam_parameter
from apis.basic_api.api import plot_dataset
from utils.tool import safe_float, safe_int, safe_str
from utils.readfile import read_txt, read_edst
class PageBeam(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.decimals = 5
        self.obj_plt_ellipse = None
        self.cb_use_dst_num = 0
        self.cb_beam_type = "notdc"
        self.if_2b = None
        self.initUI()

    def initUI(self):
        # print(self.project_path)
        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QHBoxLayout()

        # 创建一个垂直组合框
        vertical_group_box1 = QGroupBox("Beam parameters")


        vertical_layout1 = QVBoxLayout()

#####################################################

        vbox_particle_input_file = QVBoxLayout()

        label_particle_input_file = QLabel("Multiparticle input file ")

        # default_size = label_particle_input_file .sizeHint()
        # print("Default Size:", default_size) #72 12

        input_file_select_layout = QHBoxLayout()
        self.text_particle_input_file  = MyQLineEdit(" ")
        self.button_select_input_file = QPushButton(QApplication.style().standardIcon(32),"")
        self.button_select_input_file.clicked.connect(self.select_dst_file)


        input_file_select_layout.addWidget(self.text_particle_input_file)
        input_file_select_layout.addWidget(self.button_select_input_file)


        self.button_import_beam_parameter = QPushButton("Import all beam parameters from file")
        self.button_import_beam_parameter.clicked.connect(self.import_beam_parameter)



        vbox_particle_input_file.addWidget(label_particle_input_file )
        vbox_particle_input_file.addLayout(input_file_select_layout)
        vbox_particle_input_file.addWidget(self.button_import_beam_parameter)

        particle_input_file_group_box = QGroupBox("")

        # particle_input_file_layout = QVBoxLayout()
        # particle_input_file_layout.addLayout(vbox_particle_input_file)
        particle_input_file_group_box.setLayout(vbox_particle_input_file)

###############################################
        hbox_charge = QHBoxLayout()

        label_charge = QLabel("Charge")
        label_charge.setFixedSize(90, 12)  # 设置宽度和高度
        label_charge.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_charge = MyQLineEdit("")
        label_charge_unit = QLabel("e")

        hbox_charge.addWidget(label_charge)
        hbox_charge.addWidget(self.text_charge)
        hbox_charge.addWidget(label_charge_unit)

############################
        hbox_mass = QHBoxLayout()

        label_mass = QLabel("Mass")
        label_mass.setFixedSize(90, 12)  # 设置宽度和高度
        label_mass.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_mass = MyQLineEdit("")
        label_mass_unit = QLabel("MeV")

        hbox_mass.addWidget(label_mass)
        hbox_mass.addWidget(self.text_mass)
        hbox_mass.addWidget(label_mass_unit)


############################
        hbox_current = QHBoxLayout()

        label_current = QLabel("Current")
        label_current.setFixedSize(90, 12)  # 设置宽度和高度
        label_current.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_current = MyQLineEdit("")

        label_current_unit = QLabel("mA")

        hbox_current.addWidget(label_current)
        hbox_current.addWidget(self.text_current)
        hbox_current.addWidget(label_current_unit)

############################
        hbox_particel_number = QHBoxLayout()

        label_particel_number = QLabel("Num of particle")
        label_particel_number.setFixedSize(90, 12)  # 设置宽度和高度
        label_particel_number.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_particel_number = MyQLineEdit("")
        label_particel_number_unit = QLabel("")

        hbox_particel_number.addWidget(label_particel_number)
        hbox_particel_number.addWidget(self.text_particel_number)
        hbox_particel_number.addWidget(label_particel_number_unit)

############################
        hbox_frequency = QHBoxLayout()

        label_frequency = QLabel("Frequency")
        label_frequency.setFixedSize(90, 12)  # 设置宽度和高度
        label_frequency.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_frequency = MyQLineEdit("")
        label_frequency_unit = QLabel("Hz")

        hbox_frequency.addWidget(label_frequency)
        hbox_frequency.addWidget(self.text_frequency)
        hbox_frequency.addWidget(label_frequency_unit)

############################
        hbox_energy = QHBoxLayout()

        label_energy = QLabel("Energy")
        label_energy.setFixedSize(90, 12)  # 设置宽度和高度
        label_energy.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_energy = MyQLineEdit("")
        label_energy_unit = QLabel("")

        hbox_energy.addWidget(label_energy)
        hbox_energy.addWidget(self.text_energy)
        hbox_energy.addWidget(label_energy_unit)



############################
        line_frame1 = QFrame()
        line_frame1.setFrameShape(QFrame.HLine)  # 设置为水平线
        line_frame1.setFrameShadow(QFrame.Sunken)  # 设置阴影效果
        line_frame1.setLineWidth(2)  # 设置线宽度
        line_frame1.setStyleSheet("color: blue;")  # 设置线颜色
#############################
        grid_twiss = QGridLayout()

        label_alpha_xx = QLabel("\u03B1<sub>xx‘</sub>")
        self.alpha_xx_text = MyQLineEdit()

        label_beta_xx = QLabel("\u03B2<sub>xx‘</sub>")
        self.beta_xx_text = MyQLineEdit()
        beta_xx_unit = QLabel("mm/\u03C0 mrad")


        label_alpha_yy = QLabel("\u03B1<sub>yy‘</sub>")
        self.alpha_yy_text = MyQLineEdit()

        label_beta_yy = QLabel("\u03B2<sub>yy‘</sub>")
        self.beta_yy_text = MyQLineEdit()
        beta_yy_unit = QLabel("mm/\u03C0 mrad")

        label_alpha_zz = QLabel("\u03B1<sub>zz‘</sub>")
        self.alpha_zz_text = MyQLineEdit()

        label_beta_zz = QLabel("\u03B2<sub>zz‘</sub>")
        self.beta_zz_text = MyQLineEdit()
        beta_zz_unit = QLabel("mm/\u03C0 mrad")


        grid_twiss.addWidget(label_alpha_xx, 0, 0)
        grid_twiss.addWidget(self.alpha_xx_text, 0, 1)

        grid_twiss.addWidget(label_beta_xx, 1, 0)
        grid_twiss.addWidget(self.beta_xx_text, 1, 1)
        grid_twiss.addWidget(beta_xx_unit, 1, 2)

        grid_twiss.addWidget(label_alpha_yy, 2, 0)
        grid_twiss.addWidget(self.alpha_yy_text, 2, 1)

        grid_twiss.addWidget(label_beta_yy, 3, 0)
        grid_twiss.addWidget(self.beta_yy_text, 3, 1)
        grid_twiss.addWidget(beta_yy_unit, 3, 2)


        grid_twiss.addWidget(label_alpha_zz, 4, 0)
        grid_twiss.addWidget(self.alpha_zz_text, 4, 1)

        grid_twiss.addWidget(label_beta_zz, 5, 0)
        grid_twiss.addWidget(self.beta_zz_text, 5, 1)
        grid_twiss.addWidget(beta_zz_unit, 5, 2)

 ############################
        line_frame2 = QFrame()
        line_frame2.setFrameShape(QFrame.HLine)  # 设置为水平线
        line_frame2.setFrameShadow(QFrame.Sunken)  # 设置阴影效果
        line_frame2.setLineWidth(2)  # 设置线宽度
        line_frame2.setStyleSheet("color: blue;")  # 设置线颜色

########################################################
        outer_group_box = QGroupBox("Twiss parameter")
        outer_layout = QVBoxLayout()
        outer_layout.addLayout(grid_twiss)
        outer_group_box.setLayout(outer_layout)


#######################################
        grid_emittince = QGridLayout()

        label_varepsilon_xx = QLabel("\u03B5<sub>xx‘</sub>")
        self.varepsilon_xx_text = MyQLineEdit()
        varepsilon_xx_unit = QLabel("\u03C0.mm.mrad")

        label_varepsilon_yy = QLabel("\u03B5<sub>yy‘</sub>")
        self.varepsilon_yy_text = MyQLineEdit()
        varepsilon_yy_unit = QLabel("\u03C0.mm.mrad")

        label_varepsilon_zz = QLabel("\u03B5<sub>zz‘</sub>")
        self.varepsilon_zz_text = MyQLineEdit()
        varepsilon_zz_unit = QLabel("\u03C0.mm.mrad")

        grid_emittince.addWidget(label_varepsilon_xx, 0 , 0)
        grid_emittince.addWidget(self.varepsilon_xx_text, 0, 1)
        grid_emittince.addWidget(varepsilon_xx_unit, 0, 2)

        grid_emittince.addWidget(label_varepsilon_yy, 1, 0)
        grid_emittince.addWidget(self.varepsilon_yy_text, 1, 1)
        grid_emittince.addWidget(varepsilon_yy_unit, 1, 2)

        grid_emittince.addWidget(label_varepsilon_zz, 2, 0)
        grid_emittince.addWidget(self.varepsilon_zz_text, 2, 1)
        grid_emittince.addWidget(varepsilon_zz_unit, 2, 2)

        emittance_group_box = QGroupBox("Emittance")
        emittance_layout = QVBoxLayout()
        emittance_layout.addLayout(grid_emittince)
        emittance_group_box.setLayout(emittance_layout)

###############################


        # vertical_layout1.addWidget(particle_input_file_group_box)
        # vertical_layout1.addLayout(hbox_charge)
        # vertical_layout1.addLayout(hbox_mass)
        # vertical_layout1.addLayout(hbox_current)
        # vertical_layout1.addLayout(hbox_particel_number)
        # vertical_layout1.addLayout(hbox_frequency)
        # vertical_layout1.addLayout(hbox_energy)

        grid_beam = QGridLayout()
        grid_beam.setContentsMargins(0, 0, 0, 0)
        grid_beam.setHorizontalSpacing(12)
        grid_beam.setVerticalSpacing(8)

        def add_row(r, title, edit, unit=""):
            lab = QLabel(title)
            lab.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 右对齐更整齐
            # 不要 setFixedHeight(12) 这种，会导致高 DPI 被裁切
            grid_beam.addWidget(lab, r, 0)
            grid_beam.addWidget(edit, r, 1)
            if unit:
                u = QLabel(unit)
                u.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                grid_beam.addWidget(u, r, 2)
            else:
                # 占位，保证三列结构稳定（可选）
                grid_beam.addWidget(QLabel(""), r, 2)

        # 三列的列宽策略：编辑框列可伸缩，单位列最小
        grid_beam.setColumnStretch(0, 0)  # label 列不拉伸
        grid_beam.setColumnStretch(1, 1)  # edit 列拉伸（关键）
        grid_beam.setColumnStretch(2, 0)  # unit 列不拉伸

        add_row(0, "Charge", self.text_charge, "e")
        add_row(1, "Mass", self.text_mass, "MeV")
        add_row(2, "Current", self.text_current, "mA")
        add_row(3, "Num of particle", self.text_particel_number, "")
        add_row(4, "Frequency", self.text_frequency, "Hz")
        add_row(5, "Energy", self.text_energy, "")

        vertical_layout1.addWidget(particle_input_file_group_box)
        vertical_layout1.addLayout(grid_beam)


        vertical_layout1.addWidget(line_frame1)
        vertical_layout1.addWidget(outer_group_box)
        vertical_layout1.addWidget(line_frame2)

        vertical_layout1.addWidget(emittance_group_box)


        vertical_group_box1.setLayout(vertical_layout1)
#########################################################################################


        vertical_group_box2 = QGroupBox()
        vertical_layout2 = QVBoxLayout()

#############################################################

        hbox_distribution = QHBoxLayout()

        label_distribution = QLabel("Distribution")

        # default_size = label_distribution.sizeHint()
        # print("Default Size:", default_size) #72 12

        # self.text_distribution = MyQLineEdit("")

#横向
        self.distribution_combo_trans = QComboBox(self)
        self.distribution_combo_trans.addItem("GS")
        self.distribution_combo_trans.addItem("WB")
        self.distribution_combo_trans.addItem("PB")
        self.distribution_combo_trans.addItem("KV")


        # combo_font = QFont("Arial", 12)  # 使用 Arial 字体，大小为 12
        # distribution_combo_trans.setFont(combo_font)

        # 连接下拉框的currentIndexChanged信号到处理函数
        self.distribution_combo_trans.currentIndexChanged.connect(self.distribution_selection_trans)

#纵向
        self.distribution_combo_longi= QComboBox(self)
        self.distribution_combo_longi.addItem("GS")
        self.distribution_combo_longi.addItem("WB")
        self.distribution_combo_longi.addItem("PB")
        self.distribution_combo_longi.addItem("KV")


        # combo_font = QFont("Arial", 12)  # 使用 Arial 字体，大小为 12
        # distribution_combo_longi.setFont(combo_font)

        # 连接下拉框的currentIndexChanged信号到处理函数
        self.distribution_combo_longi.currentIndexChanged.connect(self.distribution_selection_longi)



        hbox_distribution.addWidget(label_distribution)
        hbox_distribution.addStretch(2)
        hbox_distribution.addWidget(self.distribution_combo_trans)
        hbox_distribution.addStretch(1)
        hbox_distribution.addWidget(self.distribution_combo_longi)
        hbox_distribution.addStretch(1)
###########################################################################
        hbox_displacePos = QHBoxLayout()

        label_displacePos = QLabel("Position Deviation")
        label_displacePos.setFixedSize(150, 12)  # 设置宽度和高度
        label_displacePos.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_displacePos_x = MyQLineEdit("")
        self.text_displacePos_y = MyQLineEdit("")
        self.text_displacePos_z = MyQLineEdit("")



        hbox_displacePos.addWidget(label_displacePos)
        hbox_displacePos.addWidget(self.text_displacePos_x)
        hbox_displacePos.addWidget(self.text_displacePos_y)
        hbox_displacePos.addWidget(self.text_displacePos_z)

###########################################################################
        hbox_displaceDpos = QHBoxLayout()

        label_displaceDpos = QLabel("Momentum Deviation")
        label_displaceDpos.setFixedSize(150, 12)  # 设置宽度和高度
        label_displaceDpos.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_displaceDpos_x = MyQLineEdit("")
        self.text_displaceDpos_y = MyQLineEdit("")
        self.text_displaceDpos_z = MyQLineEdit("")


        hbox_displaceDpos.addWidget(label_displaceDpos)
        hbox_displaceDpos.addWidget(self.text_displaceDpos_x)
        hbox_displaceDpos.addWidget(self.text_displaceDpos_y)
        hbox_displaceDpos.addWidget(self.text_displaceDpos_z)



####################################################################################
        group_use_dst = QGroupBox("")  # GroupBox标题可自定义
        layout_use_dst = QHBoxLayout()

        label_use_dst = QLabel("Use particle file")
        self.cb_use_dst = QCheckBox('', self)
        self.cb_use_dst.stateChanged.connect(self.cb_use_dst_change)
        # self.cb_use_dst.setChecked(True)  # 设置默认选中

        layout_use_dst.addWidget(label_use_dst)
        layout_use_dst.addWidget(self.cb_use_dst)

        group_use_dst.setLayout(layout_use_dst)

        ###################################################

        group_cw = QGroupBox("")  # GroupBox标题可自定义
        layout_cw = QHBoxLayout()

        label_cw = QLabel("CW beam")
        self.cb_cw = QCheckBox('', self)
        self.cb_cw.stateChanged.connect(self.cb_cw_change)

        layout_cw.addWidget(label_cw)
        layout_cw.addWidget(self.cb_cw)

        group_cw.setLayout(layout_cw)
########################################################################################

        self.button_phase_ellipse = QPushButton("Visuallize preview of rms values")
        self.button_phase_ellipse.clicked.connect(self.plot_phase_ellipse)
        vertical_layout2.addLayout(hbox_distribution)
        vertical_layout2.addWidget(group_use_dst)
        vertical_layout2.addWidget(group_cw)
        # vertical_layout2.addWidget(self.button_phase_ellipse)

        # vertical_layout2.addLayout(hbox_displacePos)
        # vertical_layout2.addLayout(hbox_displaceDpos)


        ##############################
        group_box_beam_mode = QGroupBox("Beam Mode")
        beam_mode_layout = QHBoxLayout(group_box_beam_mode)

        self.rb_single_beam = QRadioButton("Single beam")
        self.rb_double_beam = QRadioButton("Double beam")

        # 默认选择单束
        self.rb_single_beam.setChecked(True)

        # 按钮组：保证两个选项互斥
        self.beam_mode_group = QButtonGroup(self)
        self.beam_mode_group.addButton(self.rb_single_beam, 1)
        self.beam_mode_group.addButton(self.rb_double_beam, 2)

        beam_mode_layout.addWidget(self.rb_single_beam)
        beam_mode_layout.addWidget(self.rb_double_beam)

        vertical_layout2.addWidget(group_box_beam_mode)
        vertical_layout2.addStretch(1)


        vertical_group_box2.setLayout(vertical_layout2)

        # =========================



#######################################################
        self.text_charge.setValidator(QIntValidator())
        self.text_mass.setValidator(QDoubleValidator())
        self.text_current.setValidator(QDoubleValidator())
        self.text_particel_number.setValidator(QIntValidator())
        self.text_frequency.setValidator(QDoubleValidator())
        self.text_energy.setValidator(QDoubleValidator())
        self.alpha_xx_text.setValidator(QDoubleValidator())
        self.alpha_yy_text.setValidator(QDoubleValidator())
        self.alpha_zz_text.setValidator(QDoubleValidator())
        self.beta_xx_text.setValidator(QDoubleValidator())
        self.beta_yy_text.setValidator(QDoubleValidator())
        self.beta_zz_text.setValidator(QDoubleValidator())

        self.varepsilon_xx_text.setValidator(QDoubleValidator())
        self.varepsilon_yy_text.setValidator(QDoubleValidator())
        self.varepsilon_zz_text.setValidator(QDoubleValidator())


        vertical_group_box1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        vertical_group_box2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        vertical_group_box1.setMinimumWidth(300)

        layout.addWidget(vertical_group_box1)
        layout.addWidget(vertical_group_box2)


        self.setLayout(layout)


        # self.text_particle_input_file.textChanged.connect(self.onParticleInputTextChanged)

        # text_float_group = [
        # self.text_mass, self.text_current, self.text_current, self.text_frequency,
        # self.text_energy, self.alpha_xx_text, self.beta_xx_text, self.alpha_yy_text, self.beta_yy_text, self.alpha_zz_text, self.beta_zz_text,
        # self.varepsilon_xx_text, self.varepsilon_yy_text, self.varepsilon_zz_text
        # ]
        # for i in text_float_group:
        #     i.setText("0.1")
        # self.text_particel_number.setText("10")

        self.twiss_button_group = [self.alpha_xx_text, self.beta_xx_text, self.alpha_yy_text,
                                   self.beta_yy_text, self.alpha_zz_text, self.beta_zz_text,
                          self.varepsilon_xx_text, self.varepsilon_yy_text, self.varepsilon_zz_text
        ]
        # for widget in self.twiss_button_group:
        #     widget.textChanged.connect(self.twiss_changed)

        for widget in self.twiss_button_group:
            widget.editingFinished.connect(self.twiss_changed)



        self.time0 = time.time()
    def cb_use_dst_change(self, state):
        if state == Qt.Checked:
            self.cb_use_dst_num = 1
        else:
            self.cb_use_dst_num = 0

        # print(self.cb_use_dst_num)

    def cb_cw_change(self,  state):
        z_parameter = [
            self.alpha_zz_text,
            self.beta_zz_text,
            self.varepsilon_zz_text,
        ]
        if state == Qt.Checked:
            self.cb_beam_type = "dc"
            for widget in z_parameter:
                widget.setText("0")
                widget.setEnabled(False)


        elif state == Qt.Unchecked:
            self.cb_beam_type = "notdc"
            for widget in z_parameter:
                widget.setEnabled(True)


        pass

    def twiss_changed(self):
        # print("Twiss 参数改变了！")
        # time0 = time.time()
        self.twiss_parameter = {
            "alpha_x": safe_float(self.alpha_xx_text.text()),
            "beta_x": safe_float(self.beta_xx_text.text()),
            "rms_emit_x": safe_float(self.varepsilon_xx_text.text()),

            "alpha_y": safe_float(self.alpha_yy_text.text()),
            "beta_y": safe_float(self.beta_yy_text.text()),
            "rms_emit_y": safe_float(self.varepsilon_yy_text.text()),

            "alpha_z": safe_float(self.alpha_zz_text.text()),
            "beta_z": safe_float(self.beta_zz_text.text()),
            "rms_emit_z": safe_float(self.varepsilon_zz_text.text()),
        }
        time1 = time.time()
        if self.obj_plt_ellipse is not None:
            self.obj_plt_ellipse.parameter_changed(self.twiss_parameter)

        # print(474, time1 - self.time0)

    def plot_phase_ellipse(self):
        # self.obj_plt_ellipse = FourPlotDialog()
        # self.obj_plt_ellipse.initUI()
        # self.obj_plt_ellipse.plot_image1(self.project_path, plot_dataset, "loss", 0)
        # self.obj_plt_ellipse.show()

        self.obj_plt_ellipse = PhaseEllipseWidget()
        self.obj_plt_ellipse.initUI()
        self.obj_plt_ellipse.show()
        self.twiss_changed()
        self.obj_plt_ellipse.closed.connect(self.on_ellipse_closed)

    def on_ellipse_closed(self):
        self.obj_plt_ellipse = None

    def updatePath(self, new_path):
        self.project_path = new_path

        self.clean_prarameter()

    def refreshUI(self):
        self.initUI()  # Call initUI to refresh the UI


    def distribution_selection_trans(self, index):
        # 处理用户的选择
        selected_option = self.sender().currentText()
        # self.label_result.setText(f"Selected Option: {selected_option}")
    def distribution_selection_longi(self, index):
        # 处理用户的选择
        selected_option = self.sender().currentText()
        # self.label_result.setText(f"Selected Option: {selected_option}")

    def sc_method_selection(self, index):
        # 处理用户的选择
        selected_option = self.sender().currentText()
        # self.label_result.setText(f"Selected Option: {selected_option}")


    def fill_parameter(self, file_path=None):
        beam_path = os.path.join(self.project_path, "InputFile", "beam.txt")

        item = {"projectPath": self.project_path,
                "otherPath": file_path
                }

        beam_obj = BeamConfig()
        beam_res = beam_obj.create_from_file(item)



        beam_res = beam_res["data"]['beamParams']

        for k, v in beam_res.items():
            if v is not None:
                beam_res[k] = str(v)

        self.text_particle_input_file.setText(beam_res.get("readparticledistribution"))

        self.text_charge.setText(beam_res.get('numofcharge'))
        self.text_charge.setText(beam_res.get('numofcharge'))
        self.text_mass.setText(beam_res.get('particlerestmass'))
        self.text_current.setText(beam_res.get('current'))
        self.text_particel_number.setText(beam_res.get('particlenumber'))
        self.text_frequency.setText(beam_res.get('frequency'))
        self.text_energy.setText(beam_res.get('kneticenergy'))


        self.alpha_xx_text.setText(beam_res.get('alpha_x'))
        self.beta_xx_text.setText(beam_res.get('beta_x'))
        self.varepsilon_xx_text.setText(beam_res.get('emit_x'))

        self.alpha_yy_text.setText(beam_res.get('alpha_y'))
        self.beta_yy_text.setText(beam_res.get('beta_y'))
        self.varepsilon_yy_text.setText(beam_res.get('emit_y'))


        self.alpha_zz_text.setText(beam_res.get('alpha_z'))
        self.beta_zz_text.setText(beam_res.get('beta_z'))
        self.varepsilon_zz_text.setText(beam_res.get('emit_z'))

        self.distribution_combo_trans.setCurrentText(beam_res.get('distribution_x'))
        self.distribution_combo_longi.setCurrentText(beam_res.get('distribution_y'))

        if beam_res.get("use_dst") is None:
            pass
        elif safe_int(beam_res.get("use_dst")) == 1:
            self.cb_use_dst.setChecked(True)
        elif safe_int(beam_res.get("use_dst")) == 0:
            self.cb_use_dst.setChecked(False)

        if beam_res.get("beamtype") == "dc":
            self.cb_cw.setChecked(True)
        else:
            self.cb_cw.setChecked(False)


            # if isinstance(beam_res.get('displacepos'), list) and len(beam_res.get('displacepos')) == 3:
            #     self.text_displacePos_x.setText(beam_res.get('displacepos')[0])
            #     self.text_displacePos_y.setText(beam_res.get('displacepos')[1])
            #     self.text_displacePos_z.setText(beam_res.get('displacepos')[2])
            # else:
            #     self.text_displacePos_x.clear()
            #     self.text_displacePos_y.clear()
            #     self.text_displacePos_z.clear()
            #
            # if isinstance(beam_res.get('displacedpos'), list) and len(beam_res.get('displacedpos')) == 3:
            #     self.text_displaceDpos_x.setText(beam_res.get('displacedpos')[0])
            #     self.text_displaceDpos_y.setText(beam_res.get('displacedpos')[1])
            #     self.text_displaceDpos_z.setText(beam_res.get('displacedpos')[2])
            # else:
            #     self.text_displaceDpos_x.clear()
            #     self.text_displaceDpos_y.clear()
            #     self.text_displaceDpos_z.clear()
        # print(self.text_particle_input_file.text())




    def generate_beam_list(self):
        res = {}


        res['readparticledistribution'] = self.text_particle_input_file.text()

        res['numofcharge'] = self.text_charge.text()

        res['numofcharge'] = self.text_charge.text()
        res['particlerestmass'] = self.text_mass.text()
        res['current'] = self.text_current.text()
        res['particlenumber'] = self.text_particel_number.text()

        res['frequency'] = self.text_frequency.text()

        res['kneticenergy'] = self.text_energy.text()

        res['alpha_x'] = self.alpha_xx_text.text()
        res['alpha_y'] = self.alpha_yy_text.text()
        res['alpha_z'] = self.alpha_zz_text.text()

        res['beta_x'] = self.beta_xx_text.text()
        res['beta_y'] = self.beta_yy_text.text()
        res['beta_z'] = self.beta_zz_text.text()

        res['emit_x'] = self.varepsilon_xx_text.text()
        res['emit_y'] = self.varepsilon_yy_text.text()
        res['emit_z'] = self.varepsilon_zz_text.text()

        res["distribution_x"] = self.distribution_combo_trans.currentText()
        res["distribution_y"] = self.distribution_combo_longi.currentText()


        res["use_dst"] = self.cb_use_dst_num
        res["beamtype"] = self.cb_beam_type
        return res

    def clear_beam_parameter_ui(self):
        self.text_mass.clear()
        self.text_current.clear()
        self.text_particel_number.clear()
        self.text_frequency.clear()
        self.text_energy.clear()

        self.alpha_xx_text.clear()
        self.beta_xx_text.clear()
        self.alpha_yy_text.clear()
        self.beta_yy_text.clear()
        self.alpha_zz_text.clear()
        self.beta_zz_text.clear()

        self.varepsilon_xx_text.clear()
        self.varepsilon_yy_text.clear()

        self.distribution_combo_trans.setCurrentIndex(0)
        self.distribution_combo_longi.setCurrentIndex(0)

    def import_beam_parameter(self, ):
        if not self.text_particle_input_file.text():
            QMessageBox.warning(None, 'Error', f'No dst file')
            return False

        doublebeam_mode = 0
        if Path(self.text_particle_input_file.text()).suffix.lower() == ".edst":
            doublebeam_mode = 1


        # if self.if_2b is None:
        #     dst_path = os.path.join(self.project_path, "InputFile", self.text_particle_input_file.text())
        # else:
        #     dst_path = os.path.join(self.project_path, "OutputFile", "generate_2beam", self.text_particle_input_file.text())


        if doublebeam_mode == 1:
            self.clear_beam_parameter_ui()
            edst_path = os.path.join(self.project_path, "InputFile", self.text_particle_input_file.text())
            edst_param = read_edst(edst_path)
            syn_p = edst_param["partran_dist"][-1]
            energy = syn_p[5]
            charge = syn_p[6]
            mass = syn_p[7]
            freq = edst_param["freq"]

            self.text_mass.setText(str(mass))
            self.text_frequency.setText(str(freq))
            self.text_energy.setText(str(energy))
            self.text_charge.setText(str(int(charge)))





        elif doublebeam_mode == 0:
            dst_path = os.path.join(self.project_path, "InputFile", self.text_particle_input_file.text())
            item = {"dstPath": dst_path}
            dst_res = cal_beam_parameter(item)
            if dst_res["code"] == -1:
                raise Exception(dst_res["data"]["msg"])

            dst_res = dst_res['data']['beamParams']

            # print(dst_res)
            self.text_mass.setText(str(dst_res.get('particlerestmass')))
            self.text_current.setText(str(dst_res.get('current')))
            self.text_particel_number.setText(str(dst_res.get('particlenumber')))
            self.text_frequency.setText(str(dst_res.get('frequency')))


            self.text_energy.setText(str(dst_res.get("kneticenergy")))


            self.alpha_xx_text.setText(str(round(dst_res.get("alpha_x"), self.decimals)))
            self.beta_xx_text.setText(str(round(dst_res.get("beta_x"), self.decimals)))

            self.alpha_yy_text.setText(str(round(dst_res.get("alpha_y"), self.decimals)))
            self.beta_yy_text.setText(str(round(dst_res.get("beta_y"), self.decimals)))

            self.alpha_zz_text.setText(str(round(dst_res.get("alpha_z"), self.decimals)))
            self.beta_zz_text.setText(str(round(dst_res.get("beta_z"), self.decimals)))

            self.varepsilon_xx_text.setText(str(round(dst_res.get("emit_x"), self.decimals)))
            self.varepsilon_yy_text.setText(str(round(dst_res.get("emit_y"), self.decimals)))
            self.varepsilon_zz_text.setText(str(round(dst_res.get("emit_z"), self.decimals)))

            self.distribution_combo_trans.setCurrentText(dst_res["distribution_x"])
            self.distribution_combo_longi.setCurrentText(dst_res["distribution_y"])

    def save_beam(self, save_path = None):
        beam_dict = self.generate_beam_list()
        for k, v in beam_dict.items():
            if v == '':
                beam_dict[k] = None



        item = {"projectPath": self.project_path,
                "otherPath": save_path
                }
        beam_obj = BeamConfig()

        for k, v in beam_dict.items():
            if v is not None:
                if k in beam_obj.int_keys:
                    beam_dict[k] = int(v)
                elif k in beam_obj.float_keys:
                    beam_dict[k] = float(v)


        res = beam_obj.set_param(**beam_dict)

        res = beam_obj.write_to_file(item)






        #
        #
        # # 打开文件以写入数据
        # with open(beam_path, 'w', encoding='utf-8') as file:
        #     # 遍历嵌套列表的每个子列表
        #     for sublist in beam_list:
        #         # 将子列表中的元素转换为字符串，并使用逗号分隔
        #         line = '   '.join(map(str, sublist))
        #         # 将每个子列表的字符串写入文件
        #         file.write(line + '\n')

    def clean_prarameter(self):
        text_group = [
        self.text_mass, self.text_current, self.text_current, self.text_particel_number, self.text_frequency,
        self.text_energy, self.alpha_xx_text, self.beta_xx_text, self.alpha_yy_text, self.beta_yy_text, self.alpha_zz_text, self.beta_zz_text,
        self.varepsilon_xx_text, self.varepsilon_yy_text, self.varepsilon_zz_text, self.text_displacePos_x,
        self.text_displacePos_y, self.text_displacePos_z, self.text_displaceDpos_x, self.text_displaceDpos_y,
        self.text_displaceDpos_z
        ]
        QComboBox_group = [self.distribution_combo_trans, self.distribution_combo_longi]
        for line_edit in text_group:
            line_edit.clear()
        for box in QComboBox_group:
            box.setCurrentIndex(0)

    def onParticleInputTextChanged(self):
        text_group = [
        self.text_mass, self.text_current, self.text_current, self.text_particel_number, self.text_frequency,
        self.text_energy, self.alpha_xx_text, self.beta_xx_text, self.alpha_yy_text, self.beta_yy_text, self.alpha_zz_text, self.beta_zz_text,
        self.varepsilon_xx_text, self.varepsilon_yy_text, self.varepsilon_zz_text, self.text_displacePos_x,
        self.text_displacePos_y, self.text_displacePos_z, self.text_displaceDpos_x, self.text_displaceDpos_y,
        self.text_displaceDpos_z
        ]
        QComboBox_group = [self.distribution_combo_trans, self.distribution_combo_longi]

        particle_input_text = self.text_particle_input_file.text()
        for line_edit in text_group:
            line_edit.setReadOnly(bool(particle_input_text))
            # 设置只读文本字段的背景颜色为灰色
            if bool(particle_input_text):
                line_edit.setStyleSheet(f"QLineEdit {{ background-color:  {gray240} }}")
            else:
                line_edit.setStyleSheet("")  # 恢复默认样式
        
        for box in QComboBox_group:
            box.setEnabled(not bool(particle_input_text))  # 反转布尔值以设置只读状态

            # 设置只读文本字段的背景颜色为灰色
            if bool(particle_input_text):
                box.setStyleSheet(f"QComboBox {{ background-color:  {gray240} }}")
            else:
                box.setStyleSheet("")  # 恢复默认样式


    def inspect(self):
        if not self.text_charge.text():
            e = "Missing charge"
            QMessageBox.warning(None, 'Error', e)
            return False
        else:
            return True

    def select_dst_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        default_directory = os.path.join(self.project_path, "InputFile")
        dst_file_path, _ = QFileDialog.getOpenFileName(self, "Select dst File", directory=default_directory,
                                                       options=options)

        if dst_file_path:
            #复制前的文件
            source_file = dst_file_path

            relative_dst_file_path = split_file(dst_file_path)[-1]
            target_folder = os.path.join(self.project_path, "InputFile")

            #复制后的文件
            target_dst_file = os.path.join(self.project_path, "InputFile", relative_dst_file_path)

            # print(file_in_directory(source_file, target_folder))

            print(source_file, target_folder)
            #如果文件已经文件夹中
            if file_in_directory(source_file, target_folder):
                print("beam", 1)
                self.text_particle_input_file.setText(relative_dst_file_path)

            #如果文件不在文件夹中并且没有重名
            elif not file_in_directory(source_file, target_folder) and \
                not file_in_directory(target_dst_file, target_folder):
                print("beam",2)
                copy_file(source_file, target_folder)
                self.text_particle_input_file.setText(relative_dst_file_path)

            # 如果文件不在文件夹中并且重名了

            elif not file_in_directory(source_file, target_folder) and \
                file_in_directory(target_dst_file, target_folder):
                msg = QMessageBox.question(self, '文件已存在', '文件已存在，是否要覆盖？',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                print("beam", 3)
                if msg == QMessageBox.No:
                    return 0
                elif msg == QMessageBox.Yes:
                    copy_file(source_file, target_folder)
                    self.text_particle_input_file.setText(relative_dst_file_path)

    def get_beam_mode(self):
        if self.rb_single_beam.isChecked():
            return "single"
        elif self.rb_double_beam.isChecked():
            return "double"

        # particle_input_text = self.text_particle_input_file.text()
        # if particle_input_text:
        #     for line_edit in text_group:
        #         line_edit.setReadOnly(True)
        #         line_edit.setStyleSheet("background-color: rgb(240, 240, 240);")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageBeam(r'C:\Users\wangh\Desktop\qx2')
    main_window.fill_parameter()
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")

    main_window.show()
    # main_window.fill_parameter()
    main_window.save_beam()
    sys.exit(app.exec_())