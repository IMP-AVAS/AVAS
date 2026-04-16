#dst文件的发射度页面


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
from apis.basic_api.api import plot_dst

from aftertreat.dataanalysis.out_percentemitt import cla_twiss_output_standard
import time
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget,
    QTextBrowser, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIntValidator
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QPushButton, QTabWidget, QTextBrowser, QLabel,
    QLineEdit, QGroupBox, QCheckBox, QTextEdit, QSizePolicy
)
from PyQt5.QtCore import Qt


class DstEmitDialog(QDialog):
    emit_ratio_signal = pyqtSignal(float)
    def __init__(self, parent=None):
        super(DstEmitDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Beam Parameters")
        self.resize(980, 820)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # =========================
        # 顶部区域
        # =========================
        top_layout = QHBoxLayout()
        top_layout.setSpacing(18)

        # 左侧按钮区
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        distrib_layout = QHBoxLayout()
        distrib_layout.setSpacing(8)
        #
        # self.btn_eps = QPushButton("ε distrib.")
        # self.btn_sigma = QPushButton("σ distrib.")
        self.btn_eps = QPushButton(" ")
        self.btn_sigma = QPushButton(" ")
        self.btn_eps.setCheckable(True)
        self.btn_sigma.setCheckable(True)
        self.btn_eps.setChecked(True)

        self.btn_eps.setMinimumHeight(42)
        self.btn_sigma.setMinimumHeight(42)

        distrib_layout.addWidget(self.btn_eps)
        distrib_layout.addWidget(self.btn_sigma)

        # self.btn_matrix = QPushButton("σBeam matrix")
        self.btn_matrix = QPushButton(" ")
        self.btn_matrix.setMinimumHeight(48)
        self.btn_matrix.setStyleSheet("font-size: 18px; font-weight: bold;")

        left_layout.addLayout(distrib_layout)
        left_layout.addWidget(self.btn_matrix)

        top_layout.addWidget(left_widget, 1)

        # 右侧 Emittance calculated
        emittance_group = QGroupBox("Emittance calculated")
        emittance_layout = QGridLayout(emittance_group)
        emittance_layout.setHorizontalSpacing(10)
        emittance_layout.setVerticalSpacing(10)

        lbl_emit = QLabel("Emittance (%)")
        self.edit_emit = QLineEdit("100")
        self.edit_emit.setFixedHeight(32)
        self.edit_emit.setValidator(QIntValidator(1, 100, self))  # 只允许 1~100 整数
        self.edit_emit.setPlaceholderText("1~100")

        self.btn_emit_ok = QPushButton("Ok")
        self.btn_emit_ok.clicked.connect(self.get_percent_text)

        self.btn_emit_ok.setFixedHeight(32)

        self.chk_nrms = QCheckBox("N rms")
        self.edit_nrms = QLineEdit("")
        self.edit_nrms.setFixedHeight(32)
        self.edit_nrms.setEnabled(False)
        self.chk_nrms.toggled.connect(self.edit_nrms.setEnabled)

        emittance_layout.addWidget(lbl_emit, 0, 0)
        emittance_layout.addWidget(self.edit_emit, 0, 1)
        emittance_layout.addWidget(self.btn_emit_ok, 0, 2)

        emittance_layout.addWidget(self.chk_nrms, 1, 0)
        emittance_layout.addWidget(self.edit_nrms, 1, 1)

        top_layout.addWidget(emittance_group, 1)

        main_layout.addLayout(top_layout)

        # =========================
        # Filtering 标题
        # =========================
        filter_title = QLabel("Filtering (iteratif process)")
        filter_title.setStyleSheet("font-size: 15px;")
        # main_layout.addWidget(filter_title)

        # =========================
        # Filtering 行
        # =========================
        filter_group = QGroupBox()
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(10)

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setMinimumWidth(110)
        self.btn_apply.setFixedHeight(34)

        filter_layout.addWidget(self.btn_apply)
        filter_layout.addWidget(QLabel("Exclude all particle above"))

        self.edit_rms = QLineEdit("0")
        self.edit_rms.setFixedHeight(32)
        self.edit_rms.setMaximumWidth(180)
        filter_layout.addWidget(self.edit_rms)

        filter_layout.addWidget(QLabel("x Rms"))
        filter_layout.addStretch()

        # main_layout.addWidget(filter_group)

        # =========================
        # Tab 区域
        # =========================
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.page_twiss = self.create_text_page()
        self.page_center = self.create_text_page()
        self.page_size = self.create_text_page()
        self.page_fwhm = self.create_text_page()

        self.tab_widget.addTab(self.page_twiss, "Twiss / Emit.")
        self.tab_widget.addTab(self.page_center, "Center")
        self.tab_widget.addTab(self.page_size, "Size")
        self.tab_widget.addTab(self.page_fwhm, "FWHM")

        main_layout.addWidget(self.tab_widget, 1)

        # =========================
        # 底部按钮
        # =========================
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton("✓ OK")
        self.ok_btn.setMinimumWidth(100)
        self.ok_btn.setFixedHeight(36)
        self.ok_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        # 初始化页面内容
        self.update_pages()

    def create_text_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(6, 6, 6, 6)

        text_browser = QTextBrowser()
        text_browser.setObjectName("text_browser")
        text_browser.setLineWrapMode(QTextEdit.NoWrap)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background: white;
                border: 1px solid #bfbfbf;
                font-family: "Courier New", "Consolas", monospace;
                font-size: 23px;
                padding: 8px;
            }
        """)
        layout.addWidget(text_browser)

        return page

    def set_page_text(self, page, text):
        text_browser = page.findChild(QTextBrowser, "text_browser")
        if text_browser:
            text_browser.setText(text)

    def check_emit_value(self):
        txt = self.edit_emit.text().strip()

        if txt == "":
            QMessageBox.warning(self, "Input Error", "Please enter an integer between 1 and 100 for Emittance (%)")
            self.edit_emit.setText("100")
            self.edit_emit.selectAll()
            self.edit_emit.setFocus()
            return False

        val = int(txt)
        if not (1 <= val <= 100):
            QMessageBox.warning(self, "Input Error", "Please enter an integer between 1 and 100 for Emittance (%)")
            self.edit_emit.setText("100")
            self.edit_emit.selectAll()
            self.edit_emit.setFocus()
            return False

        return True

    def get_percent_text(self):
        if not self.check_emit_value():
            return None

        txt = self.edit_emit.text().strip()
        val = float(txt)/100
        self.emit_ratio_signal.emit(float(val))

        return val




    def update_pages(self, emit_page_text=None):
        if emit_page_text is None:
            emit_page_text = {}
        twiss_text = (
        )
        center_text = (
        )
        size_text = (
        )
        fwhm_text = (
        )

        twiss_text = emit_page_text.get("twiss_text")
        center_text = emit_page_text.get("center_text")
        size_text = emit_page_text.get("size_text")
        fwhm_text = emit_page_text.get("fwhm_text")

        self.set_page_text(self.page_twiss, twiss_text)
        self.set_page_text(self.page_center, center_text)
        self.set_page_text(self.page_size, size_text)
        self.set_page_text(self.page_fwhm, fwhm_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = DstEmitDialog()
    w.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = DstEmitDialog()
    w.show()
    sys.exit(app.exec_())