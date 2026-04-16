import os.path
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QVBoxLayout, QWidget, QPushButton, \
    QStackedWidget, QMenu, QLabel, QLineEdit, QTextEdit, QGridLayout, QHBoxLayout, QFrame, QFileDialog, QGroupBox, \
    QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView
import global_varible
from dataprovision.latticeparameter import LatticeParameter
from PyQt5.QtCore import QTimer
class PageData(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.setObjectName('page_data')
        self.project_path = project_path

        self.name = []
        self.length1 = []
        self.phi_ref = []
        self.phi_syn = []
        self.w = []
        self.length2 = []
        self.phi_abs = []

        self.row = 1
        self.col = 8
        self.decimals = 5
        self.initUI()

    def initUI(self):
        # print(self.project_path)
        self.resize(1200, 650)

        self.setStyleSheet("background-color: rgb(250, 250, 250);")

        layout = QHBoxLayout()

        # 创建一个垂直组合框
        vertical_group_box_main = QGroupBox("Data")

        vertical_layout_main = QVBoxLayout()

        # 在垂直布局中添加一个 QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(self.row)  # 设置列数
        self.table_widget.setColumnCount(self.col)  # 设置列数



        self.table_widget.setShowGrid(False)

        # 填充表格数据
        data = [['' * self.col] for _ in range(self.row)]


        #
        for row, rowData in enumerate(data):
            for col, value in enumerate(rowData):
                item = QTableWidgetItem(value)
                self.table_widget.setItem(row, col, item)

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # 设置表头
        self.table_widget.setHorizontalHeaderLabels(["#", "Type", "Length", f"{global_varible.greek_letters_upper['phi']} RF(degs)",f"{global_varible.greek_letters_upper['phi']} synch.(degs)",
                                                "W", 'Length(total)', f"{global_varible.greek_letters_upper['phi']} Abs(degs)"])

        # 添加表格到垂直布局
        vertical_layout_main.addWidget(self.table_widget)

        vertical_group_box_main.setLayout(vertical_layout_main)
        #########################################################################################

        layout.addWidget(vertical_group_box_main)

        self.setLayout(layout)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.your_slot_function)
        # self.timer.start(3000)  # 每隔3秒触发一次定时器

    def fill_parameter(self):
        path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')

        obj = LatticeParameter(path)
        obj.get_parameter()
        self.name = obj.v_name

        self.row = len(self.name)

        self.table_widget.setRowCount(self.row)  # 设置列数
        self.table_widget.setColumnCount(self.col)  # 设置列数



        data = [['' for _ in range(self.col)] for _ in range(self.row)]


        for i in range(self.row):
            data[i][0] = str(i + 1)
            data[i][1] = self.name[i]
            data[i][2] = str(self.treat_decimals(obj.v_len[i]))
            data[i][4] = str(obj.phi_syn[i])
            data[i][6] = str(self.treat_decimals(obj.v_start[i] + obj.v_len[i]))


        #
        for row, rowData in enumerate(data):
            for col, value in enumerate(rowData):
                item = QTableWidgetItem(value)
                self.table_widget.setItem(row, col, item)

        vertical_header = self.table_widget.verticalHeader()
        vertical_header.setVisible(False)
    def updatePath(self, new_path):
        self.project_path = new_path

    def treat_decimals(self, num):
        if num <=1e-5:
            return "{:e}".format(num)
        else:
            return round(num, self.decimals)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageData(r'C:\Users\anxin\Desktop\test_ini')
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    main_window.fill_parameter()
    sys.exit(app.exec_())