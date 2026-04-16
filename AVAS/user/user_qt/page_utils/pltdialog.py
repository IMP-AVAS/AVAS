#plt文件的可视化页面

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit,  QGridLayout, QHBoxLayout,  QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QDialog, QCheckBox, QButtonGroup, QMessageBox

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from functools import partial
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import matplotlib

from PyQt5.QtCore import pyqtSignal
from utils.readfile import read_lattice_mulp_with_name
import os
import sys
from dataprovision.beamparameter import DstParameter
from apis.basic_api.api import plot_plt

from aftertreat.dataanalysis.out_percentemitt import cla_twiss_output_standard
import time

import logging
from logger.logger_config import setup_logger
from aftertreat.dataanalysis.treatplt import TreatPlt
from conf.contants import dst_picture_title_dict, option_type_dict
from user.user_qt.page_utils.dstdialog import DstPlotDialog
logger = logging.getLogger(__name__)


class PltPlotDialog(DstPlotDialog):
    def __init__(self, item):
        self.plt_path = item.get("plt_path")
        self.project_path = item.get("project_path")
        self.num = item.get("num")

        self.part_arr, self.exist_particle, self.dst_dict = self.get_plt_dict()

        # 先让父类去完成大部分通用初始化
        super().__init__(dst_path=None)

        # 如果你想让默认图和 dst 不一样，可以在这里改


    def get_plt_dict(self):
        treat_plt_item = {
            "project_path": self.project_path,
            "plt_path": self.plt_path,
        }
        treat_plt_obj = TreatPlt(treat_plt_item)
        treat_plt_obj.get_dataset_plt_base_info()
        part_arr, exist_particle, dst_dict = treat_plt_obj.get_parameter_one_step(self.num)
        return part_arr, exist_particle, dst_dict

    def plot_image(self):
        self.fig.clear()

        item = {
            "ratio": self.emit_ratio,
            "picture_type": self.picture_type,
            "dst_path": None,
            "dst_dict": self.dst_dict,
        }

        twiss_dict, twiss_text = cla_twiss_output_standard(item)

        item = {
            "plt_path": self.plt_path,
            "picture_type": self.picture_type,
            "show_": 0,
            "fig": self.fig,
            "platform": "qt",
            "sampleInterval": 1,
            "needData": False,
            "project_path": self.project_path,
            "location": "out",
            "dst_dict": self.dst_dict,
            "part_arr": self.part_arr,
            "exist_particle": self.exist_particle,
            "twiss_dict": twiss_dict,
            "num": self.num,
        }

        plot_plt(item)
        self.canvas.draw()

        emit_page_text = {
            "twiss_text": twiss_text,
            "certer_text": None,
            "size_text": None,
            "fwhm_text": None,
        }
        self.dst_emit_obj.update_pages(emit_page_text)



if __name__ == '__main__':
    setup_logger(
        level=logging.INFO,
    )

    app = QApplication(sys.argv)
    item = {
        "plt_path": r"C:\Users\wangh\Desktop\phase_plot\v1\OutputFile\BeamSet.plt",
        "project_path": r"C:\Users\wangh\Desktop\phase_plot\v1",
        "num": 0
    }
    w = PltPlotDialog(item)
    w.plot_image()
    w.show()
    sys.exit(app.exec_())