import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QCheckBox, QButtonGroup, QTreeWidget, QTreeWidgetItem, QSpacerItem, QSizePolicy, QMessageBox

import os

from PyQt5.QtCore import QStandardPaths, QCoreApplication, pyqtSignal, QTimer
from api import change_particle_number

from user.user_qt.user_defined import treat_err
import multiprocessing

class PageFunction(QWidget):
    basic_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    match_signal = pyqtSignal(str)



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

        group_box_mulp_env = QGroupBox()

        hbox_mulp_env = QHBoxLayout()

        self.cb_mulp = QCheckBox('Multi_particles', self)
        self.cb_mulp.stateChanged.connect(self.cb_basic_change)

        self.cb_env = QCheckBox('Envelope', self)
        self.cb_env.stateChanged.connect(self.cb_basic_change)



        hbox_mulp_env.addWidget(self.cb_mulp)
        hbox_mulp_env.addWidget(self.cb_env)

        group_box_mulp_env.setLayout(hbox_mulp_env)


##########################################################################

        group_box_error = QGroupBox('Error')

        hbox_error = QHBoxLayout()

        self.cb_stat_error = QCheckBox("Static error")
        self.cb_stat_error.stateChanged.connect(self.cb_error_change)

        self.cb_dyn_error = QCheckBox("Dynamic error")
        self.cb_dyn_error.stateChanged.connect(self.cb_error_change)

        self.cb_stat_dyn_error = QCheckBox("Static error & Dynamic error")
        self.cb_stat_dyn_error.stateChanged.connect(self.cb_error_change)


        hbox_error.addWidget(self.cb_stat_error)
        hbox_error.addWidget(self.cb_dyn_error)
        hbox_error.addWidget(self.cb_stat_dyn_error)

        group_box_error.setLayout(hbox_error)

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
        hbox_match.addStretch(2)
        hbox_match.addWidget(self.cb_match_twiss)
        hbox_match.addStretch(1)
        hbox_match.addLayout(wrapper_layout)

        group_box_match.setLayout(hbox_match)


        self.cb_use_initial_value.setEnabled(False)

 ##########################################################################

##########################################################
        group_box_change_number = QGroupBox()
        hbox_change_number = QHBoxLayout()

        button_change_number = QPushButton("change Number")
        button_stop_change = QPushButton("Stop")

        button_change_number.clicked.connect(self.func_change)
        button_stop_change.clicked.connect(self.func_stop_change)
        group_box_change = QGroupBox()
        vbox_chang = QVBoxLayout()
        vbox_chang.addWidget(button_change_number)
        vbox_chang.addWidget(button_stop_change)
        group_box_change.setLayout(vbox_chang)

#############################
        button_dst_path = QPushButton("Import dst file")
        button_dst_path.clicked.connect(self.select_dst_file)

        self.text_phase_path =QLineEdit()

        label_change_number = QLabel("Particle number expansion multiple")
        self.text_change_number = QLineEdit()
        
        group_box_change_info = QGroupBox()
        vbox_change_info = QVBoxLayout()
        
        vbox_change_info.addWidget(button_dst_path)
        vbox_change_info.addWidget(self.text_phase_path)

        vbox_change_info.addWidget(label_change_number)
        vbox_change_info.addWidget(self.text_change_number)
        
        group_box_change_info.setLayout(vbox_change_info)
        
#########################################################

        hbox_change_number.addWidget(group_box_change)
        hbox_change_number.addWidget(group_box_change_info)



        group_box_change_number.setLayout(hbox_change_number)




########################################################
        vertical_layout_main.addWidget(group_box_mulp_env)
        vertical_layout_main.addWidget(group_box_error)
        vertical_layout_main.addWidget(group_box_match)
        vertical_layout_main.addWidget(group_box_change_number)


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

    @treat_err
    def select_dst_file(self):
        # desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        # default_folder_path = desktop_path
        #
        # folder_path, _ = QFileDialog.getOpenFileName(self, "Create New Folder", default_folder_path,
        #                                                  filter="Folders (*)")
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        dst_file_path, _ = QFileDialog.getOpenFileName(self, "Select dst File", options=options)

        if dst_file_path:
            # print(dst_file_path)
            self.text_phase_path.setText(dst_file_path)

    @treat_err
    def func_change(self,):
        infile_path = self.text_phase_path.text()
        if infile_path == '':
            return 0

        print('start change')
        outfile_path = os.path.join(self.project_path, 'OutputFile', 'change_num_result.dst')
        ratio = int(self.text_change_number.text())
        if self.change_num_process is None or not self.change_num_process.is_alive():
            self.change_num_process = multiprocessing.Process(target=change_particle_number,
                                                              args=(infile_path, outfile_path, ratio,))
            self.change_num_process.start()

    @treat_err
    def func_stop_change(self):
        if self.change_num_process is not None and self.change_num_process.is_alive():
            self.change_num_process.terminate()
            self.change_num_process.join()

        print('stop change')


    def cb_basic_change(self, state):
        if self.cb_mulp.isChecked():
            self.basic_signal.emit('basic_mulp')
        elif self.cb_env.isChecked():
            self.basic_signal.emit('basic_env')
        else:
            self.basic_signal.emit(None)


    def cb_error_change(self, state):
        if self.cb_stat_error.isChecked():
            self.error_signal.emit('stat_error')
        elif self.cb_dyn_error.isChecked():
            self.error_signal.emit('dyn_error')
        elif self.cb_stat_dyn_error.isChecked():
            self.error_signal.emit('stat_dyn')
        else:
            self.error_signal.emit(None)


    def cb_match_change(self, ):
        if not self.cb_match_twiss.isChecked():
            self.cb_use_initial_value.setEnabled(False)
            self.cb_use_initial_value.setChecked(False)
        else:
            self.cb_use_initial_value.setEnabled(True)

        if self.cb_use_initial_value.isChecked():
            self.match_signal.emit('match_twiss_ini')
        elif self.cb_match_twiss.isChecked():
            self.match_signal.emit('match_twiss')
        elif self.cb_input_twiss.isChecked():
            self.match_signal.emit('period_match')
        else:
            self.match_signal.emit(None)

    def inspect(self):
        pass
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageFunction(r'C:\Users\anxin\Desktop\00000')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    sys.exit(app.exec_())