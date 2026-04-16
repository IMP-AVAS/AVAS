import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QCheckBox, QButtonGroup, QTreeWidget, QTreeWidgetItem, QSpacerItem, QSizePolicy, QMessageBox

import os

from PyQt5.QtCore import QStandardPaths, QCoreApplication, pyqtSignal, QTimer
from api import change_particle_number

from user.user_qt.user_defined import treat_err
import multiprocessing


class PageOthers(QWidget):
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

        layout = QVBoxLayout()

        # 创建一个垂直组合框
        vertical_group_box_main = QGroupBox("")

        vertical_layout_main = QVBoxLayout()

        ##########################################################################

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

        self.text_phase_path = QLineEdit()

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

        vertical_layout_main.addWidget(group_box_change_number)
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
    def func_change(self, ):
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
    def inspect(self):
        pass
        return True

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main_window = PageFunction(r'C:\Users\anxin\Desktop\00000')
#     main_window.setGeometry(800, 500, 600, 650)
#     main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
#     main_window.show()
#     sys.exit(app.exec_())