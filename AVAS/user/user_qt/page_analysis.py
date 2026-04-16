import sys
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, \
    QLabel, QLineEdit, QHBoxLayout, QFileDialog, QGroupBox, \
    QCheckBox, QButtonGroup

import os
from PyQt5.QtCore import Qt
from apis.basic_api.api import plot_cavity_syn_phase, plot_dataset,  plot_cavity_voltage,\
     plot_dst, plot_phase_advance

from aftertreat.dataanalysis.plttodstfile import Plttozcode
from user.user_qt.page_utils.picture_dialog import (PictureDialog1, MulpEnvelopeDialog,
                                                    MulpEmittanceDialog, CavityVoltageDialog, BeamPahseAdvance)











class PhaseDialog(PictureDialog1, ):
    def __init__(self, file_path, func):
        super().__init__()
        self.file_path = file_path
        self.func = func


    def plot_image(self):
        item = {
            "filePath": self.file_path,
            "pictureType": "xx1",
            "platform": "qt",
            "show_": 0,
            "sampleInterval": 1,
            "needData": False,
            "projectPath": r"D:\using\test_avas_qt\cafe_avas"
        }
        self.func(**item)







# class BeamPahseAdvanceDialog(MyPictureDialog):
#     def __init__(self, project_path, func, pm):
#         super().__init__(project_path, func)
#         self.pm = pm
#
#     def plot_image(self):
#
#         self.func(self.project_path, self.pm, show_=0, fig=self.fig)
#         self.canvas.draw()

#
#
#
#
# class EnvBeamOutDialog(MyPictureDialog):
#
#     def __init__(self, project_path, func, picture_name):
#         super().__init__(project_path, func, )
#         self.picture_name = picture_name
#
#     def plot_image(self, ):
#         self.func(self.project_path, self.picture_name, show_=0, fig=self.fig)

# class EnvAlphaDialog(EnvelopeDialog):
#     def __init__(self, project_path, func):
#         super().__init__(project_path, func)
#         self.picture_name = 'alpha_x'
#
#     def contextMenuEvent(self, event):
#         cmenu = QMenu(self)
#
#         menu_items = {
#             "alpha_x": cmenu.addAction("alpha_x"),
#             "alpha_y": cmenu.addAction("alpha_y"),
#             "alpha_z": cmenu.addAction("alpha_z"),
#         }
#
#         action = cmenu.exec_(self.mapToGlobal(event.pos()))
#
#         for item_name, menu_item in menu_items.items():
#             if action == menu_item:
#                 self.picture_name = item_name
#                 break
#         self.fig.clf()
#         self.plot_image()
#
# class EnvBetaTwissDialog(EnvelopeDialog):
#     def __init__(self, project_path, func):
#         super().__init__(project_path, func)
#         self.picture_name = 'beta_x'
#
#     def contextMenuEvent(self, event):
#         cmenu = QMenu(self)
#
#         menu_items = {
#             "beta_x": cmenu.addAction("beta_x"),
#             "beta_y": cmenu.addAction("beta_y"),
#             "beta_z": cmenu.addAction("beta_z"),
#         }
#
#         action = cmenu.exec_(self.mapToGlobal(event.pos()))
#
#         for item_name, menu_item in menu_items.items():
#             if action == menu_item:
#                 self.picture_name = item_name
#                 break
#
#         self.fig.clf()
#         self.plot_image()
#
# class EnvEmitDialog(EnvelopeDialog):
#     def __init__(self, project_path, func):
#         super().__init__(project_path, func)
#         self.picture_name = 'emit_x'
#
#     def contextMenuEvent(self, event):
#         cmenu = QMenu(self)
#
#         menu_items = {
#             "emit_x": cmenu.addAction("emit_x"),
#             "emit_y": cmenu.addAction("emit_y"),
#             "emit_z": cmenu.addAction("emit_z"),
#         }
#
#         action = cmenu.exec_(self.mapToGlobal(event.pos()))
#
#         for item_name, menu_item in menu_items.items():
#             if action == menu_item:
#                 self.picture_name = item_name
#                 break
#
#         self.fig.clf()
#         self.plot_image()

class PageAnalysis(QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path
        self.lattice_path = self.project_path + r"\inputFile" + r'\lattice.txt'
        #相移meter和oeriod
        self.pahse_advance_mp = 'Period'

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        group_box = QGroupBox("Analysis")
        group_box_layout = QHBoxLayout()


##############################################

        env_picture_group_box = QGroupBox("Env")
        vbox_env = QVBoxLayout()


        self.button_env_gamma= QPushButton("Gamma")
        self.button_env_gamma.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        # self.button_env_gamma.clicked.connect(self.env_gamma_dialog)

        self.button_env_beta= QPushButton("Beta")
        self.button_env_beta.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        # self.button_env_beta.clicked.connect(self.env_beta_dialog)

        self.button_env_alpha= QPushButton("Alpha")
        self.button_env_alpha.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        # self.button_env_alpha.clicked.connect(self.env_alpha_dialog)

        self.button_env_twiss_beta= QPushButton("Beta(twiss)")
        self.button_env_twiss_beta.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        # self.button_env_twiss_beta.clicked.connect(self.env_twiss_beta_dialog)

        self.button_env_emit= QPushButton("Emittance")
        self.button_env_emit.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        # self.button_env_emit.clicked.connect(self.env_emit_dialog)

        vbox_env.addWidget(self.button_env_gamma)
        vbox_env.addWidget(self.button_env_beta)
        vbox_env.addWidget(self.button_env_alpha)
        vbox_env.addWidget(self.button_env_twiss_beta)
        vbox_env.addWidget(self.button_env_emit)



        vbox_env.addStretch(1)
        env_picture_group_box.setLayout(vbox_env)

#############
#################################################
        vbox_phase_advance = QVBoxLayout()
        self.cb_meter = QCheckBox('Meter', self)
        self.cb_meter.stateChanged.connect(self.meter_change)

        self.cb_period = QCheckBox('Period', self)
        # self.cb_period.setChecked(True)  # 将 cb_period 设置为选中状态
        self.cb_period.stateChanged.connect(self.period_change)

        # 创建一个按钮组
        button_group = QButtonGroup(self)
        button_group.addButton(self.cb_meter)
        button_group.addButton(self.cb_period)



        vbox_phase_advance.addWidget(self.cb_meter)
        vbox_phase_advance.addWidget(self.cb_period)

        phase_advance_group_box = QGroupBox("Pha Advance")
        phase_advance_group_box.setLayout(vbox_phase_advance)


########################################################
        vbox_picture = QVBoxLayout()

        self.button_beam_pahse_advance = QPushButton("Beam pha advance")
        self.button_beam_pahse_advance.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_beam_pahse_advance.clicked.connect(self.beam_pahse_advance_dialog)

        self.button_sync_phase = QPushButton("Syn Phase")
        self.button_sync_phase.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_sync_phase.clicked.connect(self.sync_phase_dialog)  # 连接按钮的点击事件到绘图函数

        self.button_envelope = QPushButton("Envelope")
        self.button_envelope.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_envelope.clicked.connect(self.envelope_dialog)

        self.button_loss = QPushButton("loss")
        self.button_loss.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_loss.clicked.connect(self.plot_loss_dialog)

        self.button_energy = QPushButton("Energy")
        self.button_energy.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_energy.clicked.connect(self.plot_energy_dialog)

        self.button_emittance = QPushButton("Emittance")
        self.button_emittance.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_emittance.clicked.connect(self.emittance_dialog)

        self.button_cavity_voltage= QPushButton("cavity_voltage")
        self.button_cavity_voltage.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_cavity_voltage.clicked.connect(self.cavity_voltage_dialog)

        vbox_picture.addWidget(phase_advance_group_box)
        vbox_picture.addWidget(self.button_beam_pahse_advance)
        vbox_picture.addWidget(self.button_sync_phase)
        vbox_picture.addWidget(self.button_envelope)
        vbox_picture.addWidget(self.button_loss)
        vbox_picture.addWidget(self.button_energy)
        vbox_picture.addWidget(self.button_emittance)
        vbox_picture.addWidget(self.button_cavity_voltage)
        vbox_picture.addStretch(1)

        picture_group_box = QGroupBox("Mulp")
        picture_group_box.setLayout(vbox_picture)

  #######################################################################
        group_box_1 = QGroupBox()
        gb1_layout = QVBoxLayout()

        plt_to_dst_group_box = QGroupBox()
        plt_to_dst_layout = QVBoxLayout()
        label_plt_to_dst = QLabel("Convert plt to dst (step)")
        
        self.step_of_plt_line = QLineEdit("")
        self.button_convert_plt = QPushButton("convert")
        self.button_convert_plt.clicked.connect(self.convert_plt_to_dst)
        
        hbox_plt_to_dst = QHBoxLayout()
        hbox_plt_to_dst.addWidget(self.step_of_plt_line)
        hbox_plt_to_dst.addWidget(self.button_convert_plt)

        self.all_step_of_plt_line = QLineEdit("")
        self.button_get_all_step = QPushButton("get all step")
        self.button_get_all_step.clicked.connect(self.get_all_step)

        hbox_get_all_step = QHBoxLayout()
        hbox_get_all_step.addWidget(self.all_step_of_plt_line )
        hbox_get_all_step.addWidget(self.button_get_all_step)


        plt_to_dst_layout.addWidget(label_plt_to_dst)
        plt_to_dst_layout.addLayout(hbox_get_all_step)
        plt_to_dst_layout.addLayout(hbox_plt_to_dst)
        plt_to_dst_group_box.setLayout(plt_to_dst_layout)
####

        vbox_phase = QVBoxLayout()

        self.button_import_dst_file = QPushButton("Import dst File")
        self.button_import_dst_file.clicked.connect(self.select_dst_file)

        self.text_phase_path =QLineEdit()

        self.button_plot_phase = QPushButton("Plot")
        self.button_plot_phase.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_plot_phase.clicked.connect(self.plot_phase)  # 连接按钮的点击事件到绘图函数

        vbox_phase.addWidget(self.button_import_dst_file)
        vbox_phase.addWidget(self.text_phase_path)
        vbox_phase.addWidget(self.button_plot_phase)

        phase_group_box = QGroupBox()
        phase_group_box.setLayout(vbox_phase)


        self.button_input =  QPushButton("Input")
        self.button_input.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_input.clicked.connect(self.button_input_plot)  # 连接按钮的点击事件到绘图函数

        self.button_output = QPushButton("Output")
        self.button_output.setStyleSheet("background-color: rgb(240, 240, 240); border: 1px solid black;")
        self.button_output.clicked.connect(self.button_output_plot)  # 连接按钮的点击事件到绘图函数

        layout_in_out = QHBoxLayout()
        layout_in_out.addWidget(self.button_input)
        layout_in_out.addWidget(self.button_output)

        group_box_in_out = QGroupBox()
        # group_box_in_out.setLayout(layout_in_out)



        # gb1_layout.addWidget(plt_to_dst_group_box)
        # gb1_layout.addWidget(phase_group_box)
        # gb1_layout.addWidget(group_box_in_out)
        gb1_layout.addStretch(1)

        group_box_1.setLayout(gb1_layout)

################################################################


################################################################

        group_box_layout.addWidget(group_box_1)
        # group_box_layout.addWidget(env_picture_group_box)
        group_box_layout.addWidget(picture_group_box)


        group_box.setLayout(group_box_layout)

        layout.addWidget(group_box)
        self.setLayout(layout)



###########errr
    def get_all_step(self):
        beamset_path = os.path.join(self.project_path, "OutputFile", "BeamSet.plt")
        obj = Plttozcode(beamset_path)
        all_step = obj.get_all_step()
        self.all_step_of_plt_line.setText(str(all_step - 1))

    def button_input_plot(self):
        dst_path = os.path.join(self.project_path, "OutputFile", "inData.dst")

        func = plot_dst
        self.phase_dialog = PhaseDialog(self.project_path, func, dst_path)
        self.phase_dialog.initUI()
        self.phase_dialog.plot_image()
        self.phase_dialog.show()

        pass


    def button_output_plot(self):
        pass



    def convert_plt_to_dst(self):
        beamset_path = os.path.join(self.project_path, "OutputFile", "BeamSet.plt")
        print(beamset_path)
        obj = Plttozcode(beamset_path)
        print(685, int(self.step_of_plt_line.text()))
        obj.write_to_dst(int(self.step_of_plt_line.text()))

    # if 1:
    #     def env_gamma_dialog(self):
    #         picture_name = 'gamma'
    #         func = plot_env_beam_out
    #         self.dialog = EnvBeamOutDialog(self.project_path, func, picture_name)
    #         self.dialog.initUI()
    #         self.dialog.plot_image()
    #         self.dialog.show()
    #
    #
    #     def env_beta_dialog(self):
    #         picture_name = 'beta'
    #         func = plot_env_beam_out
    #         self.dialog = EnvBeamOutDialog(self.project_path, func, picture_name)
    #         self.dialog.initUI()
    #         self.dialog.plot_image()
    #         self.dialog.show()
    #
    #     def env_alpha_dialog(self):
    #         func = plot_env_beam_out
    #         self.dialog = EnvAlphaDialog(self.project_path, func)
    #         self.dialog.initUI()
    #         self.dialog.plot_image()
    #         self.dialog.show()
    #
    #
    #     def env_twiss_beta_dialog(self):
    #         func = plot_env_beam_out
    #         self.dialog = EnvBetaTwissDialog(self.project_path, func)
    #         self.dialog.initUI()
    #         self.dialog.plot_image()
    #         self.dialog.show()
    #
    #     def env_emit_dialog(self):
    #         func = plot_env_beam_out
    #         self.dialog = EnvEmitDialog(self.project_path, func)
    #         self.dialog.initUI()
    #         self.dialog.plot_image()
    #         self.dialog.show()


    def sync_phase_dialog(self):
        lattice_mulp_path = os.path.join(self.project_path, "InputFile", "lattice_mulp.txt")

        self.syn_phase_dialog = PictureDialog1()
        self.syn_phase_dialog.initUI()

        item = {
            "projectPath": self.project_path,  "show_": 0, "platform": "qt"}

        self.syn_phase_dialog.plot_image1(item, plot_cavity_syn_phase,)
        self.syn_phase_dialog.show()

    def plot_phase(self):

        if self.text_phase_path.text() == '':
            # print('ddd')
            return 0

        self.phase_dialog = PictureDialog1()
        self.phase_dialog.fig = Figure(figsize=(6.4*2, 4.6*2))
        self.phase_dialog.initUI()
        item = {
            "filePath": self.text_phase_path.text() ,
            "pictureType": "xx1",
            "platform": "qt",
            "show_": 0,
            "sampleInterval": 1,
            "needData": False,
            "projectPath": r"D:\using\test_avas_qt\cafe_avas"
        }


        self.phase_dialog.plot_image1(item, plot_phase,)
        self.phase_dialog.show()

    # def plot_dataset_dialog(self, message ):
    #     self.loss_dialog = PlotOnePicture1(self.project_path, plot_dataset, message)
    #     self.loss_dialog.initUI()
    #     self.loss_dialog.plot_image()
    #     self.loss_dialog.show()

    def plot_energy_dialog(self, ):

        self.energy_dialog = PictureDialog1()
        self.energy_dialog.initUI()
        item = {
            "projectPath": self.project_path, "pictureType":"energy",  "show_": 0, "platform": "qt"}

        self.energy_dialog.plot_image1(item, plot_dataset)
        self.energy_dialog.show()


    def plot_loss_dialog(self, ):
        self.loss_dialog = PictureDialog1()
        self.loss_dialog.initUI()
        item = {
            "projectPath": self.project_path, "pictureType":"loss",  "show_": 0, "platform": "qt"}

        self.loss_dialog.plot_image1(item, plot_dataset)
        self.loss_dialog.show()


    def emittance_dialog(self):
        self.emittance_dialog = MulpEmittanceDialog(self.project_path, plot_dataset)
        self.emittance_dialog.initUI()
        self.emittance_dialog.show()

    def cavity_voltage_dialog(self):
        # func = plot_cavity_voltage
        self.cavity_voltage_dialog = CavityVoltageDialog(self.project_path, plot_cavity_voltage)
        self.cavity_voltage_dialog.initUI()
        self.cavity_voltage_dialog.plot_image()
        self.cavity_voltage_dialog.show()

    def envelope_dialog(self):

        # func = plot_dataset
        self.envelope_dialog = MulpEnvelopeDialog(self.project_path, plot_dataset)
        self.envelope_dialog.initUI()
        self.envelope_dialog.show()

    def beam_pahse_advance_dialog(self):

        func = plot_phase_advance
        self.beam_phase_dialog = BeamPahseAdvance(self.project_path, func, )
        self.beam_phase_dialog.initUI()
        self.beam_phase_dialog.plot_image()
        self.beam_phase_dialog.show()

    def updatePath(self, new_path):
        self.project_path = new_path

    def meter_change(self, state):

        if state == Qt.Checked:
            self.pahse_advance_mp = 'Meter'


    def period_change(self, state):
        if state == Qt.Checked:
            self.pahse_advance_mp = 'Period'




    def select_dst_file(self):

        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        dst_file_path, _ = QFileDialog.getOpenFileName(self, "Select dst File", options=options)

        if dst_file_path:
            # print(dst_file_path)
            self.text_phase_path.setText(dst_file_path)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = PageAnalysis(r'C:\Users\shliu\Desktop\test825')
    main_window.setGeometry(800, 500, 600, 650)
    main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    main_window.show()
    sys.exit(app.exec_())


    # app = QApplication(sys.argv)
    # main_window = CavityVoltageDialog(r'C:\Users\anxin\Desktop\00000', plot_cavity_voltage )
    # main_window.initUI()
    # main_window.setGeometry(800, 500, 600, 650)
    # main_window.setStyleSheet("background-color: rgb(253, 253, 253);")
    # main_window.show()
    # sys.exit(app.exec_())