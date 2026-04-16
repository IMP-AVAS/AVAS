import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from dataprovision.datasetparameter import DatasetParameter
from dataprovision.latticeparameter import LatticeParameter
import os
import time
import sys
from PyQt5.QtWidgets import QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget,QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QMessageBox,\
    QApplication,QHBoxLayout

from utils.readfile import read_runsignal
from apis.qt_api.getschedule import GetSchedule

class ScheduleThread(QThread):
    schedule_signal = pyqtSignal(dict)
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.process = None

    def run(self):
        item = {"projectPath": self.project_path}
        obj = GetSchedule(item)
        res = obj.main()
        self.schedule_signal.emit(res)





class PageOutput(QWidget):
    schedule_error_signal = pyqtSignal(str)

    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.num_of_z = 0
        self.demical = 2
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QVBoxLayout()

        self.layout_1 = QHBoxLayout()

        label_progress = QLabel("Progress")
        self.label_location = QLabel()

        self.layout_1.addWidget(label_progress)
        self.layout_1.addWidget(self.label_location)


        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.layout_2 = QHBoxLayout()
        length_label = QLabel("length")
        self.currrent_length_label = QLabel(" ")

        vlabel = QLabel("/")
        self.total_length_label = QLabel(" ")

        self.layout_2.addWidget(length_label)
        self.layout_2.addWidget(self.currrent_length_label)
        self.layout_2.addWidget(vlabel)
        self.layout_2.addWidget(self.total_length_label)
        self.layout_2.addStretch(1)

        self.layout_3 = QHBoxLayout()
        step_label = QLabel("step")
        self.currrent_step_label = QLabel(" ")

        vlabel = QLabel("/")
        self.total_step_label = QLabel(" ")

        self.layout_3.addWidget(step_label)
        self.layout_3.addWidget(self.currrent_step_label)
        self.layout_3.addWidget(vlabel)
        self.layout_3.addWidget(self.total_step_label)
        self.layout_3.addStretch(1)


        self.button_save = QPushButton("b1")

        layout.addLayout(self.layout_1)
        layout.addWidget(self.progress_bar)
        layout.addLayout(self.layout_2)
        layout.addLayout(self.layout_3)

        layout.addStretch(1)


        # 初始化进度条的值
        self.progress_value = 0
        self.progress_bar.setValue(self.progress_value)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)


    def update_progress(self):
        self.schedule_thread = ScheduleThread(self.project_path)
        self.schedule_thread.start()
        self.schedule_thread.schedule_signal.connect(self.update_progress1)

    def update_progress1(self, signal):
        res = signal

        if res["code"] == -1:
            error_msg = res["data"]["msg"]
            self.schedule_error_signal.emit(error_msg)
        else:
            currentLength = res["data"]["schedule"]["currentLength"]
            totalLength = res["data"]["schedule"]["totalLength"]
            currentTime = res["data"]["schedule"]["currentStep"]
            allTime = res["data"]["schedule"]["allStep"]

            self.currrent_length_label.setText(str(currentLength))
            self.total_length_label.setText(str(totalLength))
            self.currrent_step_label.setText(str(currentTime))
            self.total_step_label.setText(str(allTime))
            ratio = currentLength / totalLength
            self.progress_bar.setValue(int(ratio * 100))


    def updatePath(self, new_path):
        self.project_path = new_path


def main():
    app = QApplication(sys.argv)
    main_window = PageOutput(r'E:\using\test_avas_qt\fileld_ciads')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    main_window.update_progress()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
