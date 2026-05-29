##画出口处的束损和发射度

from aftertreat.picture.initialplot import PicturePlot_2D, CompoundShape, PicturePlot_2ax
from utils.readfile import read_txt
import os


class PlotErr_emit_loss(PicturePlot_2ax):
    def __init__(self, file_path, type_='par'):
        super().__init__()
        self.err_par_path = file_path
        self.type_ = type_

    def get_x_y(self):
        data = read_txt(self.err_par_path, out='list')[1:]
        data = [[float(j) for j in i] for i in data]

        # x = [int(i[0]) for i in data]
        x = [0,2,2.5,3,3.5,4]

        x = [0, 2, 4, 6, 8]

        emit_x_increase = [i[2] * 100 for i in data]
        emit_y_increase = [i[3] * 100 for i in data]
        emit_z_increase = [i[4] * 100 for i in data]


        self.xy['ax1_x'] = [x] * 3
        self.xy['ax1_y'] = [emit_x_increase] + [emit_y_increase] + [emit_z_increase]

        loss = [i[1] * 100 for i in data]

        self.xy['ax2_x'] = [x]
        self.xy['ax2_y'] = [loss]

        print(loss)
        self.xlabel = "Step of errors"

        self.ylabel1 = "Emittance growth (%)"
        self.ylabel2 = "Loss(%)"

        self.labels1 = ["emit_xx'", "emit_yy'", "emit_zz'"]
        self.labels2 = ["loss"]

        self.colors1 = ['r', 'b', 'g']
        self.colors2 = ['m']

        self.set_legend = 1

if __name__ ==  "__main__":
    project_path = r"F:\AVAS_CONTROL\AVAS_control\ana_err_bpm\errors_par_dphi.txt"
    obj = PlotErr_emit_loss(project_path, 1)
    obj.get_x_y()
    obj.run(show_=1)