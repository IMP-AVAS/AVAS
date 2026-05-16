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

from utils.treatfile import copy_file, copy_file_rename
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
from utils.twobeamsetconfig import Beam2Config
from apps.dst2edst import Dst2edst

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


class Pagegenerate2beam(QWidget):
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
        self.twobeam_set_path = os.path.join(self.project_path, "OutputFile", "generate_2beam", "2beam_set.txt")

        self.g2b_setting = {}


        self.b1_dst_path =  os.path.join(self.project_path, "OutputFile", "generate_2beam", "2beam_first.dst")
        self.b2_dst_path = os.path.join(self.project_path, "OutputFile", "generate_2beam", "2beam_second.dst")



        self.initUI()

    def initUI(self):
        self.setWindowTitle("Generate Two Beams")
        self.resize(400, 200)

        main_layout = QVBoxLayout(self)

        title = QLabel("Two-beam generation")
        main_layout.addWidget(title)
#################################################################
        top_button_layout = QHBoxLayout()

        self.btn_save = QPushButton("Save")
        top_button_layout.addWidget(self.btn_save)

        # 让 Save 按钮靠左，右边留空
        top_button_layout.addStretch()

        main_layout.addLayout(top_button_layout)

        # 连接保存函数
        self.btn_save.clicked.connect(self.save_2beam_set)
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


        ########################################################################

        ###################################################################################
        # 束流1的中心位置
        phase_center_group = QGroupBox("Phase center")
        phase_center_layout = QVBoxLayout(phase_center_group)

        beam1_center_layout = QHBoxLayout()
        beam1_center_layout.addWidget(QLabel("Beam 1 phase center deviation:"))

        self.le_beam1_center = QLineEdit()
        beam1_center_layout.addWidget(self.le_beam1_center)

        beam1_center_layout.addWidget(QLabel("deg"))

        # 束流2的中心位置
        beam2_center_layout = QHBoxLayout()
        beam2_center_layout.addWidget(QLabel("Beam 2 phase center deviation:"))

        self.le_beam2_center = QLineEdit()
        beam2_center_layout.addWidget(self.le_beam2_center)

        beam2_center_layout.addWidget(QLabel("deg"))

        phase_center_layout.addLayout(beam1_center_layout)
        phase_center_layout.addLayout(beam2_center_layout)
        main_layout.addWidget(phase_center_group)

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
        self.key_line_map = {
        "b1_phase_min": self.le_beam1_phase_min,
        "b1_phase_max": self.le_beam1_phase_max,

        "b2_phase_min": self.le_beam2_phase_min,
        "b2_phase_max": self.le_beam2_phase_max,

        "b1_phase_center": self.le_beam1_center,
        "b2_phase_center": self.le_beam2_center,

        "syn_p_charge": self.text_charge,
        "syn_p_mass": self.text_mass,
        "syn_p_phi": self.text_phi,
        "syn_p_energy": self.text_energy,
        }

        self.fill_parameter()

    def fill_parameter(self):
        if os.path.exists(self.beam1_path):
            self.beam1_window.fill_parameter(self.beam1_path)

        if os.path.exists(self.beam2_path):
            self.beam2_window.fill_parameter(self.beam2_path)

        if os.path.exists(self.twobeam_set_path):
            obj = Beam2Config()
            item = {"projectPath": self.project_path}
            g2bset_params = obj.create_from_file(item)["data"]["g2bset_params"]

            for key, line in self.key_line_map.items():
                line.setText(str(g2bset_params.get(key)))



    def open_beam1_page(self):
        self.beam1_window.show()

    def open_beam2_page(self):
        self.beam2_window.show()

    def generate_2beam(self):
        self.save_2beam_set()
        set_dict = {}
        for  key, line in self.key_line_map.items():
            set_dict[key] = safe_float(line.text())

        set_dict["syn_p_charge"] = safe_int( self.text_charge.text())
        set_dict["b1_charge"] = safe_int(self.beam1_window.text_charge.text())
        set_dict["b2_charge"] = safe_int(self.beam2_window.text_charge.text())

        set_dict["b1_path"] = self.b1_dst_path
        set_dict["b2_path"] = self.b2_dst_path

        set_dict["2beam_mode"] = self.get_two_beam_mode()
        set_dict["edst_path"] = os.path.join(self.dir_generate_2b, "2beam.edst")

        obj = Dst2edst(set_dict)
        obj.run()

        print(set_dict)

        #复制文件到Inputfile
        source_file1 = self.b1_dst_path
        source_file2 = self.b2_dst_path
        source_file3 = os.path.join(self.dir_generate_2b, "2beam.edst")

        target_folder =  os.path.join(self.project_path, "InputFile")
        copy_file(source_file1, target_folder)
        copy_file(source_file2, target_folder)
        copy_file(source_file3, target_folder)
        pass

    def generate_beam1(self):
        save_path = self.beam1_path
        self.beam1_window.save_beam(save_path)
        use_dst = self.beam1_window.cb_use_dst_num
        #如果不使用分布，那么就生成新的
        print(use_dst)
        if use_dst == 0:
            obj = GenDst()
            input = save_path
            out_put = self.b1_dst_path
            obj.generate_dst(input, out_put)

        #如果使用，那么就复制后重命名
        else:
            source_file = os.path.join(self.dir_generate_2b, self.beam1_window.text_particle_input_file.text())
            target_folder = self.dir_generate_2b
            new_name = "2beam_first.dst"
            new_file_path = os.path.join(target_folder, new_name)

            #如果源文件不叫2beam_first.dst
            if self.beam1_window.text_particle_input_file.text() != "2beam_first.dst":
                copy_file_rename(source_file, target_folder, new_name)
            elif self.beam1_window.text_particle_input_file.text() == "2beam_first.dst":
                pass


            #无论是否存在，都把文件重新复制，如果不存在就是复制后重命名，如果存在，那就重新复制一次
            # copy_file_rename(source_file, target_folder, new_name)
            # #判断是否存在我们要复制的文件，如果已经存在，那么直接跳过
            # if os.path.exists(new_file_path):
            #     pass
            # #如果不存在，那么就复制
            # else:
            #     copy_file_rename(source_file, target_folder, new_name)


    def generate_beam2(self):
        save_path = self.beam2_path
        self.beam2_window.save_beam(save_path)

        use_dst = self.beam2_window.cb_use_dst_num
        obj = GenDst()
        # 如果不使用分布，那么就生成新的
        if use_dst == 0:
            input = save_path
            out_put = self.b2_dst_path
            obj.generate_dst(input, out_put)
        else:
            source_file = os.path.join(self.dir_generate_2b, self.beam1_window.text_particle_input_file.text())
            target_folder = self.dir_generate_2b
            new_name = "2beam_second.dst"
            new_file_path = os.path.join(target_folder, new_name)

            # 如果源文件不叫2beam_first.dst
            if self.beam1_window.text_particle_input_file.text() != "2beam_second.dst":
                copy_file_rename(source_file, target_folder, new_name)
            elif self.beam1_window.text_particle_input_file.text() == "2beam_second.dst":
                pass


            #判断是否存在我们要复制的文件，如果已经存在，那么直接跳过

            # if os.path.exists(new_file_path):
            #     pass
            # #如果不存在，那么就复制
            # else:
            #     copy_file_rename(source_file, target_folder, new_name)


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

    def save_2beam_set(self):
        self.beam1_window.save_beam(self.beam1_path)
        self.beam2_window.save_beam(self.beam2_path)

        set_dict = {}
        for  key, line in self.key_line_map.items():
            set_dict[key] = safe_float(line.text())

        set_dict["syn_p_charge"] = safe_int( self.text_charge.text())

        obj = Beam2Config()
        obj.set_param(**set_dict)
        item = {"projectPath": self.project_path}
        obj.write_to_file(item)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    project_path = r"C:\Users\wangh\Desktop\test_page_2b"

    window = Pagegenerate2beam(project_path)
    window.show()

    sys.exit(app.exec_())