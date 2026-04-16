import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')
import os
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QDialog, QCheckBox, QButtonGroup, QMessageBox

from PyQt5.QtCore import Qt, QSize
from api import plot_cavity_syn_phase, plot_dataset,  plot_cavity_voltage,\
     plot_phase, plot_phase_advance
from user.user_qt.user_defined import treat_err

from user.user_qt.user_defined import MyQLineEdit
from utils.readfile import read_txt, read_dst
from user.user_qt.user_defined import gray240
import multiprocessing

from api import longdistance
from user.user_qt.user_defined import treat_err
class PageLongdistance(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.decimals = 5
        self.initUI()

    def initUI(self):
        # print(self.project_path)
        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QHBoxLayout()

        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()


########################################
        #算法维度选择
        dimension_groupbox = QGroupBox()

        dimension_layout = QHBoxLayout()
        self.cb_2d = QCheckBox('2D', self)
        self.cb_2d.stateChanged.connect(self.cb_2d_change)

        self.cb_3d = QCheckBox('3D', self)
        # self.cb_period.setChecked(True)  # 将 cb_period 设置为选中状态
        self.cb_3d.stateChanged.connect(self.cb_3d_change)

        # 创建一个按钮组
        button_group_1 = QButtonGroup(self)

        button_group_1.addButton(self.cb_2d)
        button_group_1.addButton(self.cb_3d)

        dimension_layout.addWidget(self.cb_2d)
        dimension_layout.addWidget(self.cb_3d)

        dimension_groupbox.setLayout(dimension_layout)
############################################

        groupbox_1 = QGroupBox()
        groupbox_1_layout = QVBoxLayout()
############################################
        dstfile_layout = QHBoxLayout()

        label_dstfile = QLabel("Multiparticle input file")
        label_dstfile.setFixedSize(150, 12)  # 设置宽度和高度
        label_dstfile.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_dstfile = MyQLineEdit("")


        dstfile_layout.addWidget(label_dstfile)
        dstfile_layout.addWidget(self.text_dstfile)
        groupbox_1_layout.addLayout(dstfile_layout)
############################################
        dc_pulse_layout = QHBoxLayout()

        self.cb_dc = QCheckBox('dc', self)
        self.cb_pulse = QCheckBox('pulse', self)


        # 创建一个按钮组
        button_group_1 = QButtonGroup(self)

        button_group_1.addButton(self.cb_dc)
        button_group_1.addButton(self.cb_pulse)

        dc_pulse_layout.addWidget(self.cb_dc)
        dc_pulse_layout.addWidget(self.cb_pulse)

        groupbox_1_layout.addLayout(dc_pulse_layout)
###################################################
        #束团数量
        numofbunch_layout = QHBoxLayout()

        label_numofbunch = QLabel("Nbr of bunch")
        label_numofbunch.setFixedSize(150, 12)  # 设置宽度和高度
        label_numofbunch.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_numofbunch = MyQLineEdit("32")



        numofbunch_layout.addWidget(label_numofbunch)
        numofbunch_layout.addWidget(self.text_numofbunch)
        groupbox_1_layout.addLayout(numofbunch_layout)

###############################################

        mag_layout = QHBoxLayout()

        label_mag = QLabel("external magnetic field")
        label_mag.setFixedSize(150, 12)  # 设置宽度和高度
        label_mag.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_mag_x = MyQLineEdit("0")
        self.text_mag_y = MyQLineEdit("0")
        self.text_mag_z = MyQLineEdit("0")

        label_mag_unit = QLabel("nT")

        mag_layout.addWidget(label_mag)
        mag_layout.addWidget(self.text_mag_x)
        mag_layout.addWidget(self.text_mag_y)
        mag_layout.addWidget(self.text_mag_z)
        mag_layout.addWidget(label_mag_unit)

        groupbox_1_layout.addLayout(mag_layout)
###########################################

        compmagnetic_layout = QHBoxLayout()

        label_compmagnetic  = QLabel("compensating magnetic field")
        label_compmagnetic .setFixedSize(150, 12)  # 设置宽度和高度
        label_compmagnetic .setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_compmagnetic_x = MyQLineEdit("0")
        self.text_compmagnetic_y = MyQLineEdit("0")
        self.text_compmagnetic_z = MyQLineEdit("0")

        label_compmagnetic_unit = QLabel("nT")

        compmagnetic_layout.addWidget(label_compmagnetic )
        compmagnetic_layout.addWidget(self.text_compmagnetic_x)
        compmagnetic_layout.addWidget(self.text_compmagnetic_y)
        compmagnetic_layout.addWidget(self.text_compmagnetic_z)
        compmagnetic_layout.addWidget(label_compmagnetic_unit)


        groupbox_1_layout.addLayout(compmagnetic_layout)
###########################################
        #补偿距离
        compdistance_layout = QHBoxLayout()

        label_compdistance = QLabel("compensating distance")
        label_compdistance.setFixedSize(150, 12)  # 设置宽度和高度
        label_compdistance.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_compdistance_start = MyQLineEdit("0")
        self.text_compdistance_end = MyQLineEdit("0")

        label_compdistance_unit = QLabel("m")


        compdistance_layout.addWidget(label_compdistance)
        compdistance_layout.addWidget(self.text_compdistance_start)
        compdistance_layout.addWidget(self.text_compdistance_end)
        compdistance_layout.addWidget(label_compdistance_unit)


        groupbox_1_layout.addLayout(compdistance_layout)
################################################################
        #电荷
        charge_layout = QHBoxLayout()

        label_charge = QLabel("charge")
        label_charge.setFixedSize(150, 12)  # 设置宽度和高度
        label_charge.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_charge = MyQLineEdit("")



        charge_layout.addWidget(label_charge)
        charge_layout.addWidget(self.text_charge)
        groupbox_1_layout.addLayout(charge_layout)
####################################################
        #正负束团
        posnegbeam_layout = QHBoxLayout()

        self.cb_posnegbeam = QCheckBox('Positive and negative bunch', self)


        posnegbeam_layout.addWidget(self.cb_posnegbeam)

        groupbox_1_layout.addLayout(posnegbeam_layout)
##################################################
        totallength_layout = QHBoxLayout()

        label_totallength = QLabel("total length")
        label_totallength.setFixedSize(150, 12)  # 设置宽度和高度
        label_totallength.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_totallength = MyQLineEdit("")
        label_totallength_unit = QLabel("m")


        totallength_layout.addWidget(label_totallength)
        totallength_layout.addWidget(self.text_totallength)
        totallength_layout.addWidget(label_totallength_unit)

        groupbox_1_layout.addLayout(totallength_layout)
###############################################################
        current_layout = QHBoxLayout()

        label_current = QLabel("current")
        label_current.setFixedSize(150, 12)  # 设置宽度和高度
        label_current.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_current = MyQLineEdit("")
        label_current_unit = QLabel("mA")


        current_layout.addWidget(label_current)
        current_layout.addWidget(self.text_current)
        current_layout.addWidget(label_current_unit)

        groupbox_1_layout.addLayout(current_layout)
###############################################################
        #nr ,nz, rnum
        nrz_2d_layout = QHBoxLayout()

        label_nr_2d = QLabel("nr")
        self.text_nr_2d = MyQLineEdit("20")

        label_nz_2d = QLabel("nz")
        self.text_nz_2d = MyQLineEdit("21")

        label_rnum_2d = QLabel("rnum")
        self.text_rnum_2d = MyQLineEdit("43")


        nrz_2d_layout.addWidget(label_nr_2d)
        nrz_2d_layout.addWidget(self.text_nr_2d)
        nrz_2d_layout.addWidget(label_nz_2d)
        nrz_2d_layout.addWidget(self.text_nz_2d)
        nrz_2d_layout.addWidget(label_rnum_2d)
        nrz_2d_layout.addWidget(self.text_rnum_2d)


        groupbox_1_layout.addLayout(nrz_2d_layout)
############################################
        #三维
        #nr ,nz, rnum
        nxyz_3d_layout = QHBoxLayout()

        label_nxy_3d = QLabel("nxy")
        self.text_nxy_3d = MyQLineEdit("400")

        label_nz_3d = QLabel("nz")
        self.text_nz_3d = MyQLineEdit("20")

        label_nx_3d = QLabel("nx")
        self.text_nx_3d = MyQLineEdit("50")

        label_ny_3d = QLabel("ny")
        self.text_ny_3d = MyQLineEdit("50")


        nxyz_3d_layout.addWidget(label_nxy_3d)
        nxyz_3d_layout.addWidget(self.text_nxy_3d)

        nxyz_3d_layout.addWidget(label_nz_3d)
        nxyz_3d_layout.addWidget(self.text_nz_3d)

        nxyz_3d_layout.addWidget(label_nx_3d)
        nxyz_3d_layout.addWidget(self.text_nx_3d)

        nxyz_3d_layout.addWidget(label_ny_3d)
        nxyz_3d_layout.addWidget(self.text_ny_3d)


        groupbox_1_layout.addLayout(nxyz_3d_layout)
################################################
        dt_layout = QHBoxLayout()

        label_timepulse = QLabel("dt of pulse")
        label_timepulse .setFixedSize(150, 12)  # 设置宽度和高度
        label_timepulse.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_timepulse = MyQLineEdit("20")


        label_timedc  = QLabel("dt of dc")
        label_timedc.setFixedSize(150, 12)  # 设置宽度和高度
        label_timedc.setAlignment(Qt.AlignCenter)  # 设置水平和垂直居中

        self.text_timedc = MyQLineEdit("10")



        dt_layout.addWidget(label_timepulse)
        dt_layout.addWidget(self.text_timepulse)
        dt_layout.addWidget(label_timedc)
        dt_layout.addWidget(self.text_timedc)



        groupbox_1_layout.addLayout(dt_layout)
################################################
        run_stop_layout = QHBoxLayout()
        self.run_button = QPushButton("run")
        self.run_button.clicked.connect(self.run_button_click)

        self.stop_button = QPushButton("stop")
        self.stop_button.clicked.connect(self.stop_button_click)

        run_stop_layout.addWidget(self.run_button)
        run_stop_layout.addWidget(self.stop_button)

        groupbox_1_layout.addLayout(run_stop_layout)

        groupbox_1.setLayout(groupbox_1_layout)
############################################
        group_box_layout.addWidget(dimension_groupbox)
        group_box_layout.addWidget(groupbox_1)
        group_box_layout.addStretch(1)



        group_box.setLayout(group_box_layout)

        layout.addWidget(group_box)
        self.setLayout(layout)
        self.fill_parameter()
        self.process = multiprocessing.Process()

    def cb_2d_change(self, state):
        text_group_2 = [self.text_nr_2d, self.text_nz_2d, self.text_rnum_2d]
        text_group_3 = [self.text_nxy_3d, self.text_nz_3d, self.text_nx_3d, self.text_ny_3d]
        if state == Qt.Checked:
            for i in text_group_3:
                i.setReadOnly(True)
                i.setStyleSheet(f"QLineEdit {{ background-color:  {gray240} }}")

            for i in text_group_2:
                i.setReadOnly(False)
                i.setStyleSheet("")




    def cb_3d_change(self, state):
        text_group_2 = [self.text_nr_2d, self.text_nz_2d, self.text_rnum_2d]
        text_group_3 = [self.text_nxy_3d, self.text_nz_3d, self.text_nx_3d, self.text_ny_3d]

        if state == Qt.Checked:
            for i in text_group_2:
                i.setReadOnly(True)
                i.setStyleSheet(f"QLineEdit {{ background-color:  {gray240} }}")

            for i in text_group_3:
                i.setReadOnly(False)
                i.setStyleSheet("")



    def fill_parameter(self):
        input_path = os.path.join(self.project_path, "InputFile", "LongAccelerator.txt")

        if os.path.exists(input_path):
            input_res = read_txt(input_path)
            print(input_res)
            self.text_dstfile.setText(input_res.get('particledistributionpath'))

            if int(input_res['dc']) == 0:
                self.cb_pulse.setChecked(True)
            elif int(input_res['dc']) == 1:
                self.cb_dc.setChecked(True)

            self.text_numofbunch.setText(input_res.get('numofshutuan'))

            self.text_mag_x.setText(input_res.get("magnetic")[0])
            self.text_mag_y.setText(input_res.get("magnetic")[1])
            self.text_mag_z.setText(input_res.get("magnetic")[2])

            self.text_compmagnetic_x.setText(input_res.get("compmagnetic")[0])
            self.text_compmagnetic_y.setText(input_res.get("compmagnetic")[1])
            self.text_compmagnetic_z.setText(input_res.get("compmagnetic")[2])

            self.text_compdistance_start.setText(input_res.get("compdistance")[0])
            self.text_compdistance_end.setText(input_res.get("compdistance")[1])

            self.text_charge.setText(input_res.get("charge"))

            if int(input_res['posnegbeam']) == 1:
                self.cb_posnegbeam.setChecked(True)

            self.text_totallength.setText(input_res.get("totallength"))
            self.text_current.setText(input_res.get("newcurrent"))

            if int(input_res.get("dimension")) == 2:
                self.cb_2d.setChecked(True)
                self.text_nr_2d.setText(input_res.get("nr"))
                self.text_nz_2d.setText(input_res.get("nz"))
                self.text_rnum_2d.setText(input_res.get("rnum"))

            elif int(input_res.get("dimension")) == 3:
                self.cb_3d.setChecked(True)
                self.text_nxy_3d.setText(input_res.get("nxy"))
                self.text_nz_3d.setText(input_res.get("nz"))
                self.text_nx_3d.setText(input_res.get("nx"))
                self.text_ny_3d.setText(input_res.get("ny"))

            self.text_timepulse.setText(input_res.get("timepulse"))
            self.text_timedc.setText(input_res.get("timedc"))
        else:
            print("LongAccelerator.txt文件不存在")
            # 设置默认值
            self.text_dstfile.setText("")

            self.text_numofbunch.setText("32")

            # 假设磁场默认值为0
            self.text_mag_x.setText("0")
            self.text_mag_y.setText("0")
            self.text_mag_z.setText("0")

            # 补偿磁场默认值
            self.text_compmagnetic_x.setText("0")
            self.text_compmagnetic_y.setText("0")
            self.text_compmagnetic_z.setText("0")

            # 补偿距离默认值
            self.text_compdistance_start.setText("0")
            self.text_compdistance_end.setText("0")

            self.text_charge.setText("")

            self.text_totallength.setText("")
            self.text_current.setText("")

            # 维度默认设置为2D或3D，根据您的需求选择

            self.text_nr_2d.setText("20")
            self.text_nz_2d.setText("21")
            self.text_rnum_2d.setText("43")

            # 如果3D不是默认值，则可以将其设置为False或不设置
            self.text_nxy_3d.setText("400")
            self.text_nz_3d.setText("20")
            self.text_nx_3d.setText("50")
            self.text_ny_3d.setText("50")

            self.text_timepulse.setText("20")
            self.text_timedc.setText("10")
    def generate_save_list(self):
        res = []
        res.append(['particleDistributionPath', self.text_dstfile.text()])

        if self.cb_2d.isChecked():
            res.append(["dimension", '2'])
        elif self.cb_3d.isChecked():
            res.append(["dimension", '3'])

        if self.cb_dc.isChecked():
            res.append(["dc", "1"])
        elif self.cb_pulse.isChecked():
            res.append(["dc", 0])

        res.append(["numofshutuan", self.text_numofbunch.text()])
        res.append(["magnetic", self.text_mag_x.text(), self.text_mag_y.text(),
                    self.text_mag_z.text()])

        res.append(["compmagnetic", self.text_compmagnetic_x.text(), self.text_compmagnetic_y.text(),
                    self.text_compmagnetic_z.text()])

        res.append(["compdistance", self.text_compdistance_start.text(), self.text_compdistance_end.text()])

        res.append(['charge', self.text_charge.text()])

        if self.cb_posnegbeam.isChecked():
            res.append(["posnegbeam", 1])
        else:
            res.append(["posnegbeam", 0])

        res.append(["totallength", self.text_totallength.text()])
        if self.text_current.text():
            res.append(["newcurrent", self.text_current.text()])

        if self.cb_2d.isChecked():
            res.append(["nr", self.text_nr_2d.text()])
            res.append(["nz", self.text_nz_2d.text()])
            res.append(["rnum", self.text_rnum_2d.text()])



        elif self.cb_3d.isChecked():
            res.append(["nxy", self.text_nxy_3d.text()])
            res.append(["nz", self.text_nz_3d.text()])
            res.append(["nx", self.text_nx_3d.text()])
            res.append(["ny", self.text_ny_3d.text()])

        res.append(["timepulse", self.text_timepulse.text()])
        res.append(["timedc", self.text_timedc.text()])

        return res

    def save(self):
        input_list = self.generate_save_list()

        longaccelerator_path = os.path.join(self.project_path, 'InputFile', 'LongAccelerator.txt')

        # 打开文件以写入数据
        with open(longaccelerator_path, 'w', encoding='utf-8') as file:
            # 遍历嵌套列表的每个子列表
            for sublist in input_list:
                # 将子列表中的元素转换为字符串，并使用逗号分隔
                line = '   '.join(map(str, sublist))
                # 将每个子列表的字符串写入文件
                file.write(line + '\n')

    @treat_err
    def run_button_click(self):
        print("开始运行")
        self.save()
        if self.cb_2d.isChecked():
            kind = 2
        elif self.cb_3d.isChecked():
            kind = 3

        if not self.process.is_alive():
            self.process = multiprocessing.Process(target=longdistance, args=(self.project_path, kind))
            self.process.start()
    @treat_err
    def stop_button_click(self):

        if self.process.is_alive():
            self.process.terminate()
            self.process.join()
        print("停止运行")
    def updatePath(self, new_path):
        self.project_path = new_path

        # particle_input_text = self.text_particle_input_file.text()
        # if particle_input_text:
        #     for line_edit in text_group:
        #         line_edit.setReadOnly(True)
        #         line_edit.setStyleSheet("background-color: rgb(240, 240, 240);")
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main_window = PageLongdistance(r'C:\Users\anxin\Desktop\126')
#     main_window.setGeometry(800, 500, 600, 650)
#     main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
#     main_window.show()
#     sys.exit(app.exec_())