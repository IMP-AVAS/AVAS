#该页面用于生成双束，按照用户指定的规则

import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget,QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QGroupBox,\
    QComboBox, QSizePolicy, QMessageBox,QPushButton, QCheckBox
import os
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QStandardPaths
from user.user_qt.user_defined import MyQLineEdit

from utils.treatfile import copy_file
from utils.treatfile import split_file, file_in_directory


from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout,
    QGroupBox, QRadioButton,
    QComboBox, QMessageBox
)

from user.user_qt.page_beam import PageBeam
import os
from user.user_qt.page_utils.parametergridwidget import ParameterGridWidget
from utils.tool import safe_float, safe_int
from core.gendst import GenDst

class PageBeamFor2Beam(PageBeam):
    def __init__(self, project_path, beam_id=1):
        self.beam_id = beam_id

        # 调用父类 PageBeam 的初始化
        super().__init__(project_path)

        # 父类 initUI() 已经执行完，这里可以继续修改界面
    def func(self):
        pass

    def select_dst_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        default_directory = os.path.join(self.project_path, "InputFile")
        dst_file_path, _ = QFileDialog.getOpenFileName(self, "Select dst File", directory=default_directory,
                                                       options=options)

        if dst_file_path:
            # 复制前的文件
            source_file = dst_file_path

            relative_dst_file_path = split_file(dst_file_path)[-1]
            target_folder = os.path.join(self.project_path, "OutputFile", "generate_2beam")

            # 复制后的文件
            target_dst_file = os.path.join(target_folder, relative_dst_file_path)

            # print(file_in_directory(source_file, target_folder))

            # 如果文件已经文件夹中
            if file_in_directory(source_file, target_folder):
                self.text_particle_input_file.setText(relative_dst_file_path)

            # 如果文件不在文件夹中并且没有重名
            elif not file_in_directory(source_file, target_folder) and \
                    not file_in_directory(target_dst_file, target_folder):
                copy_file(source_file, target_folder)
                self.text_particle_input_file.setText(relative_dst_file_path)

            # 如果文件不在文件夹中并且重名了
            elif not file_in_directory(source_file, target_folder) and \
                    file_in_directory(target_dst_file, target_folder):
                msg = QMessageBox.question(self, '文件已存在', '文件已存在，是否要覆盖？',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if msg == QMessageBox.No:
                    return 0
                elif msg == QMessageBox.Yes:
                    copy_file(source_file, target_folder)
                    self.text_particle_input_file.setText(relative_dst_file_path)


class generate2beam(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.decimals = 5

        # 用来保存弹出的窗口对象，防止窗口一闪而过被回收
        self.beam1_window = None
        self.beam2_window = None

        #创建双束生成的文件夹

        self.dir_generate_2b = os.path.join(self.project_path, "OutputFile", "generate_2beam")

        os.makedirs(self.dir_generate_2b, exist_ok=True)

        self.beam1_path = os.path.join(self.dir_generate_2b, "beam1.txt")
        self.beam2_path = os.path.join(self.dir_generate_2b, "beam2.txt")

        self.g2b_setting = {}

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Generate Two Beams")
        self.resize(400, 200)

        main_layout = QVBoxLayout(self)

        title = QLabel("Two-beam generation")
        main_layout.addWidget(title)


        ##############################################

        self.beam1_window = PageBeamFor2Beam(self.project_path)
        self.beam1_window.setWindowTitle("Beam 1 Parameters")
        self.beam1_window.if_2b = 1

        self.beam2_window = PageBeamFor2Beam(self.project_path)
        self.beam2_window.setWindowTitle("Beam 2 Parameters")
        self.beam2_window.if_2b = 1

        setbeam_layout = QHBoxLayout()

        self.btn_beam1 = QPushButton("Set Beam 1")
        self.btn_beam2 = QPushButton("Set Beam 2")

        setbeam_layout.addWidget(self.btn_beam1)
        setbeam_layout.addWidget(self.btn_beam2)

        main_layout.addLayout(setbeam_layout)

        self.btn_beam1.clicked.connect(self.open_beam1_page)
        self.btn_beam2.clicked.connect(self.open_beam2_page)
        #####################################
        #用来生成一个bunch
        gb_layout = QHBoxLayout()

        self.btn_gb_beam1 = QPushButton("Generate Beam 1")
        self.btn_gb_beam2 = QPushButton("Generate Beam 2")

        gb_layout.addWidget(self.btn_gb_beam1)
        gb_layout.addWidget(self.btn_gb_beam2)

        main_layout.addLayout(gb_layout)

        self.btn_gb_beam1.clicked.connect(self.generate_beam1)
        self.btn_gb_beam2.clicked.connect(self.generate_beam2)


        ##############################################################################
        #选择结合模式
        #1.两种束流都是直流束
        #2.两种束流都是脉冲束
        mode_group = QGroupBox("Two-beam mode")
        mode_layout = QVBoxLayout(mode_group)

        self.rb_both_dc = QRadioButton("Beam 1: DC beam    Beam 2: DC beam")
        self.rb_both_pulse = QRadioButton("Beam 1: Pulse beam    Beam 2: Pulse beam")
        self.rb_beam1_dc_beam2_pulse = QRadioButton("Beam 1: DC beam    Beam 2: Pulse beam")
        self.rb_beam1_pulse_beam2_dc = QRadioButton("Beam 1: Pulse beam    Beam 2: DC beam")

        self.rb_both_pulse.setChecked(True)

        mode_layout.addWidget(self.rb_both_dc)
        mode_layout.addWidget(self.rb_both_pulse)
        mode_layout.addWidget(self.rb_beam1_dc_beam2_pulse)
        mode_layout.addWidget(self.rb_beam1_pulse_beam2_dc)

        main_layout.addWidget(mode_group)


        ##########################################################################################
         #beam1和beam2的相位范围
        phase_group = QGroupBox("Phase range")
        phase_layout = QVBoxLayout(phase_group)

        # Beam 1 phase range
        beam1_phase_layout = QHBoxLayout()
        beam1_phase_layout.addWidget(QLabel("Beam 1 phase range:"))

        self.le_beam1_phase_min = QLineEdit()
        self.le_beam1_phase_max = QLineEdit()

        self.le_beam1_phase_min.setText("-180")
        self.le_beam1_phase_max.setText("180")

        beam1_phase_layout.addWidget(QLabel("Min"))
        beam1_phase_layout.addWidget(self.le_beam1_phase_min)
        beam1_phase_layout.addWidget(QLabel("deg"))

        beam1_phase_layout.addWidget(QLabel("Max"))
        beam1_phase_layout.addWidget(self.le_beam1_phase_max)
        beam1_phase_layout.addWidget(QLabel("deg"))


        # Beam 2 phase range
        beam2_phase_layout = QHBoxLayout()
        beam2_phase_layout.addWidget(QLabel("Beam 2 phase range:"))

        self.le_beam2_phase_min = QLineEdit()
        self.le_beam2_phase_max = QLineEdit()

        self.le_beam2_phase_min.setText("-180")
        self.le_beam2_phase_max.setText("180")

        beam2_phase_layout.addWidget(QLabel("Min"))
        beam2_phase_layout.addWidget(self.le_beam2_phase_min)
        beam2_phase_layout.addWidget(QLabel("deg"))

        beam2_phase_layout.addWidget(QLabel("Max"))
        beam2_phase_layout.addWidget(self.le_beam2_phase_max)
        beam2_phase_layout.addWidget(QLabel("deg"))

        phase_layout.addLayout(beam1_phase_layout)
        phase_layout.addLayout(beam2_phase_layout)
        main_layout.addWidget(phase_group)

###################################################################################
        # 束流1的中心位置
        phase_center_group = QGroupBox("Phase center")
        phase_center_layout = QVBoxLayout(phase_center_group)

        beam1_center_layout = QHBoxLayout()
        beam1_center_layout.addWidget(QLabel("Beam 1 phase range:"))


        self.le_beam1_center = QLineEdit()
        beam1_center_layout.addWidget(self.le_beam1_center)

        beam1_center_layout.addWidget(QLabel("deg"))

        # 束流2的中心位置
        beam2_center_layout = QHBoxLayout()
        beam2_center_layout.addWidget(QLabel("Beam 2 phase range:"))


        self.le_beam2_center = QLineEdit()
        beam2_center_layout.addWidget(self.le_beam2_center)

        beam2_center_layout.addWidget(QLabel("deg"))

        phase_center_layout.addLayout(beam1_center_layout)
        phase_center_layout.addLayout(beam2_center_layout)
        main_layout.addWidget(phase_center_group)




        ########################################################################
        #同步粒子的信息

        self.beam_param_widget = ParameterGridWidget()

        self.text_charge = MyQLineEdit("")
        self.text_mass = MyQLineEdit("")
        self.text_phi = MyQLineEdit("")
        self.text_energy = MyQLineEdit("")

        self.beam_param_widget.add_rows([
            ("Charge", self.text_charge, "e"),
            ("Mass", self.text_mass, "MeV"),
            ("Phi", self.text_phi, "deg"),
            ("Energy", self.text_energy, "MeV"),
        ])

        main_layout.addWidget(self.beam_param_widget)

        ###############################################################################
        generate_edst_button =  QPushButton("Generate 2 beam")
        generate_edst_button.clicked.connect(self.generate_2beam)
        main_layout.addWidget(generate_edst_button)
        #####################################################################


    def open_beam1_page(self):
        self.beam1_window.show()

    def open_beam2_page(self):
        self.beam2_window.show()

    def generate_2beam(self):
        self.g2b_setting = {
        "b1_phase_min": safe_float(self.le_beam1_phase_min.text()),
        "b1_phase_max": safe_float(self.le_beam1_phase_max.text()),

        "b2_phase_min": safe_float(self.le_beam2_phase_min.text()),
        "b2_phase_max": safe_float(self.le_beam2_phase_max.text()),

        "b1_phase_center": safe_float(self.le_beam1_center.text()),
        "b2_phase_center": safe_float(self.le_beam2_center.text()),

        "syn_p_charge": safe_int(self.text_charge.text()),
        "syn_p_maxx": safe_float(self.text_mass.text()),
        "syn_p_phi": safe_float(self.text_phi.text()),
        "syn_p_energy": safe_float(self.text_energy.text()),
        }

        print(self.g2b_setting)
        pass

    def generate_beam1(self):
        save_path = os.path.join(self.project_path, "OutputFile", "generate_2beam", "beam1.txt")
        self.beam1_window.save_beam(save_path)

        obj = GenDst()

        input = save_path
        out_put = os.path.join(self.project_path, "OutputFile", "generate_2beam", "2beam_first.dst")
        obj.generate_dst(input, out_put)

    def generate_beam2(self):
        save_path = os.path.join(self.project_path, "OutputFile", "generate_2beam", "beam2.txt")
        self.beam2_window.save_beam(save_path)

        obj = GenDst()

        input = save_path
        out_put = os.path.join(self.project_path, "OutputFile", "generate_2beam", "2beam_second.dst")
        obj.generate_dst(input, out_put)

    def get_two_beam_mode(self):
        #将dc定义为1，puslse定义为0
        if self.rb_both_dc.isChecked():
            return (1, 1)

        elif self.rb_both_pulse.isChecked():
            return (0, 0)

        elif self.rb_beam1_dc_beam2_pulse.isChecked():
            return (1, 0)

        elif self.rb_beam1_pulse_beam2_dc.isChecked():
            return (0, 1)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    project_path = r"C:\Users\wangh\Desktop\test_page_2b"

    window = generate2beam(project_path)
    window.show()

    sys.exit(app.exec_())