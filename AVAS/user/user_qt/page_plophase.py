import sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGroupBox, QPushButton, QLineEdit,
    QLabel, QFileDialog, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt

from dataprovision.beamset import BeamsetParameter
from user.user_qt.page_utils.pltdialog import PltPlotDialog
from user.user_qt.page_utils.dstdialog import DstPlotDialog

import logging
from logger.logger_config import setup_logger
logger = logging.getLogger(__name__)
from aftertreat.dataanalysis.treatplt import TreatPlt

class PagePlotphase(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

        self.dst_path = None
        self.plt_path = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # =========================
        # DST Import / Plot
        # =========================
        group_box_dst = QGroupBox("DST Import / Plot")
        dst_layout = QVBoxLayout(group_box_dst)

        self.button_import_dst_file = QPushButton("Import dst File")
        self.button_import_dst_file.clicked.connect(self.select_dst_file)

        self.text_dst_path = QLineEdit()
        self.text_dst_path.setPlaceholderText("")

        self.button_plot_dst = QPushButton("Plot")
        self.button_plot_dst.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")

        self.button_plot_dst.clicked.connect(self.plot_dst)

        dst_layout.addWidget(self.button_import_dst_file)
        dst_layout.addWidget(self.text_dst_path)
        dst_layout.addWidget(self.button_plot_dst)

        # =========================
        # PLT Import / Plot
        # =========================
        group_box_plt = QGroupBox("Plt Import / Plot")
        plt_layout = QVBoxLayout(group_box_plt)

        # --- 第一行：导入按钮 + “All steps” + steps 输入框
        grid_import_plt = QGridLayout()

        self.button_import_plt_file = QPushButton("Import plt File")
        self.button_import_plt_file.clicked.connect(self.select_plt_file)

        label_all_steps = QLabel("All steps")
        self.text_step_of_plt = QLineEdit()
        self.text_step_of_plt.setPlaceholderText("")

        grid_import_plt.addWidget(self.button_import_plt_file, 0, 0)
        grid_import_plt.addWidget(label_all_steps,         0, 1 )
        grid_import_plt.addWidget(self.text_step_of_plt,   0, 2)

        # 让右侧输入框更宽
        grid_import_plt.setColumnStretch(0, 1)
        grid_import_plt.setColumnStretch(1, 1)
        grid_import_plt.setColumnStretch(2, 1)
        label_all_steps.setAlignment(Qt.AlignCenter)   #让all_step居中


        plt_layout.addLayout(grid_import_plt)

        # --- plt 路径输入框
        self.text_plt_path = QLineEdit()
        self.text_plt_path.setPlaceholderText("")
        plt_layout.addWidget(self.text_plt_path)

        # --- Location / Step 的筛选
        grid_where_plt = QGridLayout()

        label_location = QLabel("Location")
        self.text_location = QLineEdit()
        self.text_location.setPlaceholderText("")


        label_step = QLabel("Step")
        self.text_step_of_this = QLineEdit()
        self.text_step_of_this.setPlaceholderText("")
        self.text_step_of_this.editingFinished.connect(self.get_location_to_step)

        grid_where_plt.addWidget(label_step,         0, 0)
        grid_where_plt.addWidget(self.text_step_of_this,     0, 1)

        grid_where_plt.addWidget(label_location,     1, 0)
        grid_where_plt.addWidget(self.text_location, 1, 1)


        # 右边输入框吃满宽度
        grid_where_plt.setColumnStretch(0, 1)
        grid_where_plt.setColumnStretch(1, 1)

        plt_layout.addLayout(grid_where_plt)

        # --- Plot 按钮（plt）
        self.button_plot_plt = QPushButton("Plot")
        self.button_plot_plt.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_plot_plt.clicked.connect(self.plot_plt)
        plt_layout.addWidget(self.button_plot_plt)

        plt_layout.addStretch(1)

        # =========================
        # Add to main layout
        # =========================
        main_layout.addWidget(group_box_dst)
        main_layout.addWidget(group_box_plt)

    def plot_dst(self):
        self.cavity_voltage_dialog = DstPlotDialog(self.dst_path)
        self.cavity_voltage_dialog.plot_image()
        self.cavity_voltage_dialog.show()

    def select_dst_file(self):
        dst_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select dst File",
            self.project_path,
            "DST Files (*.dst);;All Files (*)"
        )
        if dst_file_path:
            self.text_dst_path.setText(dst_file_path)
            self.dst_path = dst_file_path

    def select_plt_file(self):
        plt_file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select plt File",
            self.project_path,
            "PLT Files (*.plt);;All Files (*)"
        )

        if plt_file_path:


            self.text_plt_path.setText(plt_file_path)
            self.plt_path = plt_file_path

        item = {
            "project_path": self.project_path,
            "plt_path": self.plt_path,
        }
        plt_obj = TreatPlt(item)
        plt_step = plt_obj.get_dataset_plt_base_info()
        self.text_step_of_plt.setText(f"{plt_step}")

    def get_location_to_step(self):
        self.num_step_of_this = int(self.text_step_of_this.text())

        treat_plt_item = {
            "project_path": self.project_path,
            "plt_path": self.plt_path,
        }

        treat_plt_obj = TreatPlt(treat_plt_item)
        treat_plt_obj.get_dataset_plt_base_info()
        z_list = treat_plt_obj.dataset_z_list
        location_to_z = z_list[self.num_step_of_this]
        self.text_location.setText(f"{location_to_z}")

    def plot_plt(self):
        item = {
            "plt_path": self.plt_path,
            "project_path": self.project_path,
            "num": self.num_step_of_this,
        }
        w = PltPlotDialog(item)
        w.plot_image()
        w.show()


if __name__ == '__main__':
    setup_logger(
        level=logging.INFO,
    )

    app = QApplication(sys.argv)
    w = PagePlotphase(r'C:\Users\wangh\Desktop\324\v3')
    w.setGeometry(800, 500, 360, 320)
    w.setStyleSheet("background-color: rgb(253, 253, 253);")
    w.show()
    sys.exit(app.exec_())
