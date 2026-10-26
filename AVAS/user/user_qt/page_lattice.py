import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction,\
    QVBoxLayout, QWidget, QPushButton, QLineEdit, QTextEdit, QHBoxLayout, QToolBar, QStackedWidget, \
    QButtonGroup, QShortcut,QMessageBox
import sys
import os

from user.user_qt.user_defined import treat_err
from utils.latticeconfig import LatticeConfig

from user.user_qt.lattice_file.lattice_ide import CodeEditorWithLineNumbers
class PageLattice(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.lattice_mulp_path = ''
        self.lattice_env_path = ''
        self.ctrl_pressed = False  # 添加一个标志来跟踪Ctrl键是否被按住
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        hbox_control = QHBoxLayout()

        self.button_save = QPushButton("Save")
        self.button_save.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_save.clicked.connect(self.save_all_lattice)
        self.text_file_path = QLineEdit()
        self.text_file_path.setReadOnly(True)


        hbox_control.addWidget(self.button_save)
        hbox_control.addWidget(self.text_file_path)
########################################################################


        hbox_cut = QHBoxLayout()
        self.button_mulp_lattice = QPushButton("lattice_mulp")
        self.button_env_lattice = QPushButton("lattice_env")
        # self.button_match_result = QPushButton("match result")
        # self.button_match_twiss = QPushButton("match twiss")
        self.button_input_twiss = QPushButton("input twiss")


        hbox_cut.addWidget(self.button_mulp_lattice)
        hbox_cut.addWidget(self.button_env_lattice)
        # hbox_cut.addWidget(self.button_match_result)
        # hbox_cut.addWidget(self.button_match_twiss)
        hbox_cut.addWidget(self.button_input_twiss)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.button_mulp_lattice)
        self.button_group.addButton(self.button_env_lattice)
        # self.button_group.addButton(self.button_match_result)
        # self.button_group.addButton(self.button_match_twiss)
        self.button_group.addButton(self.button_input_twiss)

        self.button_group.setExclusive(True)

        self.button_mulp_lattice.setCheckable(True)
        self.button_env_lattice.setCheckable(True)
        # self.button_match_result.setCheckable(True)
        # self.button_match_twiss.setCheckable(True)
        self.button_input_twiss.setCheckable(True)

###########################################################
        self.text_mulp_lattice = CodeEditorWithLineNumbers()
        self.text_env_lattice = QTextEdit()
        # self.text_match_result = QTextEdit()
        # self.text_match_twiss = QTextEdit()

        self.text_input_twiss = QTextEdit()


        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.text_mulp_lattice)
        self.stacked_widget.addWidget(self.text_env_lattice)
        # self.stacked_widget.addWidget(self.text_match_result)
        # self.stacked_widget.addWidget(self.text_match_twiss)
        self.stacked_widget.addWidget(self.text_input_twiss)


        self.button_mulp_lattice.clicked.connect(self.mulp_lattice_click)
        self.button_env_lattice.clicked.connect(self.env_lattice_click)
        # self.button_match_result.clicked.connect(self.match_result_click)
        # self.button_match_twiss.clicked.connect(self.match_twiss_click)
        self.button_input_twiss.clicked.connect(self.input_twiss_click)




########################################################
        layout.addLayout(hbox_control)
        # layout.addLayout(hbox_cut)
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)


        # # 连接文本输入框的文本更改信号到处理函数

        self.ignore_text_changed = False


        # if True:
        #     self.text_mulp_lattice.modes.append(modes.CodeCompletionMode())
        #     sh_text_lattice = self.text_mulp_lattice.modes.append(MySyntaxHighlighter(self.text_mulp_lattice.document()))
        #     sh_text_lattice.fold_detector = MyFoldDetector()
        #     self.text_mulp_lattice.panels.append(panels.FoldingPanel())




    def updatePath(self, new_path):
        self.project_path = new_path
        self.lattice_mulp_path = os.path.join(self.project_path, "InputFile", "lattice_mulp.txt")
        self.lattice_env_path = os.path.join(self.project_path, "InputFile", "lattice_env.txt")

    def fill_parameter(self):

        item = {"projectPath": self.project_path,}

        self.stacked_widget.setCurrentWidget(self.text_mulp_lattice)
        self.lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')
        # print(self.lattice_path)
        self.text_file_path.setText(self.lattice_mulp_path)

        obj = LatticeConfig()
        res = obj.create_from_file(item)


        if res["code"] == -1:
            raise Exception(str(res["data"]['msg']))
        file_contents = res["data"]["latticeParams"]

        self.text_mulp_lattice.setPlainText(file_contents, )




        # self.lattice_env_path = os.path.join(self.project_path, 'InputFile', 'lattice_env.txt')
        # self.text_file_path.setText(self.lattice_env_path)
        #
        # obj = LatticeConfig()
        # res = obj.create_from_file(item)
        # if res["code"] == -1:
        #     raise Exception(str(res["data"]['msg']))
        # file_contents = res["data"]["latticeParams"]
        #
        # self.text_env_lattice.setPlainText(file_contents)
        #
        # self.button_mulp_lattice.setChecked(True)
        # self.button_state()




    def save_all_lattice(self):
        item = {"projectPath": self.project_path,}

        item["sim_type"] = "mulp"
        obj = LatticeConfig()
        res = obj.set_param({"latticeInfo": self.text_mulp_lattice.toPlainText()})
        res = obj.write_to_file(item)
        if res["code"] == -1:
            raise Exception(str(res["data"]['msg']))



        #如果路径为空, 那么不保存
        # item["sim_type"] = "env"
        # obj = LatticeConfig()
        # res = obj.set_param({"latticeInfo": self.text_env_lattice.toPlainText()})
        # res = obj.write_to_file(item)
        # if res["code"] == -1:
        #     raise Exception(str(res["data"]['msg']))

    def fill_text_lattice_path(self, path):
        self.text_lattice_path.setText(path)

    # @treat_err
    def mulp_lattice_click(self):
        if not self.project_path:
            pass
        else:
            self.button_state()

            self.stacked_widget.setCurrentWidget(self.text_mulp_lattice)
            # self.lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')
            self.text_file_path.setText(self.lattice_mulp_path)
            #
            # with open(self.lattice_mulp_path, 'r', encoding='utf-8') as file:
            #     file_contents = file.read()
            #
            # self.text_lattice.setPlainText(file_contents, mime_type="text/plain", encoding='utf-8')

    @treat_err
    def env_lattice_click(self):
        if not self.project_path:
            pass
        else:
            self.button_state()
            self.stacked_widget.setCurrentWidget(self.text_env_lattice)
            # self.lattice_env_path = os.path.join(self.project_path, 'InputFile', 'lattice_env.txt')
            self.text_file_path.setText(self.lattice_env_path)
            #
            # if not os.path.exists(self.lattice_env_path):
            #     with open(self.lattice_env_path, 'w', encoding='utf-8') as file:
            #         file.write("")
            #
            # with open(self.lattice_env_path, 'r', encoding='utf-8') as file:
            #     file_contents = file.read()
            #
            # self.text_match_lattice.setPlainText(file_contents)


    @treat_err
    def input_twiss_click(self):
        if not self.project_path:
            pass
        else:
            self.button_state()
            self.stacked_widget.setCurrentWidget(self.text_input_twiss)
            self.input_twiss_path = os.path.join(self.project_path, 'OutputFile', 'env_input_twiss.txt')
            self.text_file_path.setText(self.input_twiss_path)

            if not os.path.exists(self.input_twiss_path):
                return 0

            with open(self.input_twiss_path, 'r', encoding='utf-8') as file:
                file_contents = file.read()
                self.text_input_twiss.setPlainText(file_contents)

    # @treat_err
    def button_state(self):
        button = self.sender()
        # print(button)

        if button is None:
            button = self.button_mulp_lattice
        # print(button)

        if button.isChecked():
            for other_button in self.button_group.buttons():
                if other_button is not button:
                    other_button.setChecked(False)


        # 自定义选中按钮的样式
        for btn in self.button_group.buttons():
            if btn.isChecked():
                btn.setStyleSheet("background-color: rgb(240, 240, 240); ")
            else:
                btn.setStyleSheet("")  # 恢复默认样式
    def inspect(self):
        pass
        return True

#
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageLattice(r'F:\using\test_avas_qt\cafe_AVAS')

    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.updatePath(r'F:\using\test_avas_qt\cafe_AVAS')
    main_window.fill_parameter()
    main_window.show()
    sys.exit(app.exec_())
