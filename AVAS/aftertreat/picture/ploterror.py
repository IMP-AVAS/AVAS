from aftertreat.picture.initialplot import PicturePlot_2D, CompoundShape, PicturePlot_2ax
from utils.readfile import read_txt
import os


class PlotErrout(PicturePlot_2D):

    def __init__(self, file_path, stat_method, picture_type, ):
        """
        picture_type
        { 1: 发射度增长
        }
        """
        super().__init__()
        self.err_par_path = file_path
        self.stat_method = stat_method
        self.picture_type = picture_type



    def get_x_y(self):
        data = read_txt(self.err_par_path, out='list')[1:]


        data = [[float(j) for j in i] for i in data]

        self.x = [int(i[0]) for i in data]
        # if self.picture_type == 1:
        # #发射度增长
        #     emit_x_increase = [i[2] * 100 for i in data]
        #     emit_y_increase = [i[3] * 100 for i in data]
        #     emit_z_increase = [i[4] * 100 for i in data]
        #     self.y = [emit_x_increase, emit_y_increase, emit_z_increase]
        #
        #     self.xlabel = "step"
        #     self.ylabel = "Emittance growth (%)"
        #
        #     self.labels = ["emit_xx'", "emit_yy'", "emit_zz'"]
        #     self.colors = ['r', 'b', 'g']
        #     self.set_legend = 1
        #
        # if self.picture_type == 2:
        #     #loss 图
        #     loss = [i[1] * 100 for i in data]
        #
        #     self.y = loss
        #
        #     self.xlabel = "step"
        #     self.ylabel = "Loss (%)"

        if self.stat_method == 'average':
            if self.picture_type == 'xy':
            #ave_cen x, y
                ave_cen_x = [i[5] * 1000 for i in data]
                ave_cen_y = [i[6] * 1000 for i in data]

                self.y = [ave_cen_x, ave_cen_y]

                self.xlabel = "step"
                self.ylabel = "Average of beam position(mm)"

                self.labels = ["X", "Y", ]
                self.colors = ['r', 'b']
                self.set_legend = 1

            elif self.picture_type == "x1y1":
                # ave_cen x', y'

                ave_cen_x = [i[7] * 1000 for i in data]
                ave_cen_y = [i[8] * 1000 for i in data]

                self.y = [ave_cen_x, ave_cen_y]

                self.xlabel = "step"
                self.ylabel = "Average of beam angle(mrad)"

                self.labels = ["X'", "Y'", ]
                self.colors = ['r', 'b']
                self.set_legend = 1


            elif self.picture_type == 'rms_xy':
                # ave(rms_x) 包络的平均值

                ave_rms_x = [i[9] * 1000 for i in data]
                ave_rms_y = [i[10] * 1000 for i in data]

                self.y = [ave_rms_x, ave_rms_y]

                self.xlabel = "step"
                self.ylabel = "Average of rms size(mm)"

                self.labels = ["X", "Y", ]
                self.colors = ['r', 'b']
                self.set_legend = 1
            if self.picture_type == 'rms_x1y1':
                # ave(rms_x') 包络的平均值
                av_rms_x1 = [i[11] * 1000 for i in data]
                av_rms_y1 = [i[12] * 1000 for i in data]

                self.y = [av_rms_x1, av_rms_y1]

                self.xlabel = "step"
                self.ylabel = "Average of rms angle size(mrad)"

                self.labels = ["X'", "Y'", ]
                self.colors = ['r', 'b']
                self.set_legend = 1
            elif self.picture_type == 'ek':
                # ave_cen Enery

                ave_cen_ek = [i[13] * 1000 for i in data]
                self.y = ave_cen_ek

                self.xlabel = "step"
                self.ylabel = "Average of beam energy change(keV)"

        elif self.stat_method == 'rms':

            if self.picture_type == 'xy':
            #rms cen x, y

                rms_cen_x = [i[14] * 1000 for i in data]
                rms_cen_y = [i[15] * 1000 for i in data]

                self.y = [rms_cen_x, rms_cen_y]

                self.xlabel = "step"
                self.ylabel = "Rms  of beam position(mm)"

                self.labels = ["X", "Y", ]
                self.colors = ['r', 'b']
                self.set_legend = 1



            elif self.picture_type == 'x1y1':
            #rms_cen x', y'

                rms_cen_x = [i[16] * 1000 for i in data]
                rms_cen_y = [i[17] * 1000 for i in data]

                self.y = [rms_cen_x, rms_cen_y]

                self.xlabel = "step"
                self.ylabel = "rms of beam angle(mrad)"

                self.labels = ["X'", "Y'", ]
                self.colors = ['r', 'b']
                self.set_legend = 1


            elif self.picture_type == 'rms_xy':
            #rms(rms_x) 包络的平均值

                rms_rms_x = [i[18] * 1000 for i in data]
                rms_rms_y = [i[19] * 1000 for i in data]

                self.y = [rms_rms_x, rms_rms_y]

                self.xlabel = "step"
                self.ylabel = "Rms of rms size(mm)"

                self.labels = ["X", "Y", ]
                self.colors = ['r', 'b']
                self.set_legend = 1




            elif self.picture_type == 'rms_x1y1':
            #rms(rms_x') 包络的平均值
                rms_rms_x1 = [i[20] * 1000 for i in data]
                rms_rms_y1 = [i[21] * 1000 for i in data]

                self.y = [rms_rms_x1, rms_rms_y1]

                self.xlabel = "step"
                self.ylabel = "Rms of rms angle size(mrad)"

                self.labels = ["X'", "Y'", ]
                self.colors = ['r', 'b']
                self.set_legend = 1
            elif self.picture_type == 'ek':
            #rms_cen Enery

                rms_cen_ek = [i[22] * 1000 for i in data]
                print(189, rms_cen_ek)
                self.y = rms_cen_ek

                self.xlabel = "step"
                self.ylabel = "Rms of beam energy change(keV)"

            if not isinstance(self.y[0], list):
                self.y = [self.y]
            if not isinstance(self.x[0], list):
                self.x = [self.x]

            if len(self.x) != len(self.y):
                self.x = self.x * len(self.y)
class PlotErr_emit_loss(PicturePlot_2ax):
    def __init__(self, file_path, type_='par'):
        super().__init__()
        self.err_par_path = file_path
        self.type_ = type_

    def get_x_y(self):
        data = read_txt(self.err_par_path, out='list')[1:]
        data = [[float(j) for j in i] for i in data]

        x = [int(i[0]) for i in data]

        emit_x_increase = [i[2] * 100 for i in data]
        emit_y_increase = [i[3] * 100 for i in data]
        emit_z_increase = [i[4] * 100 for i in data]


        self.xy['ax1_x'] = [x] * 3
        self.xy['ax1_y'] = [emit_x_increase] + [emit_y_increase] + [emit_z_increase]

        loss = [i[1] * 100 for i in data]

        self.xy['ax2_x'] = [x]
        self.xy['ax2_y'] = [loss]

        self.xlabel = "Step of errors"

        self.ylabel1 = "Emittance growth (%)"
        self.ylabel2 = "Loss(%)"

        self.labels1 = ["emit_xx'", "emit_yy'", "emit_zz'"]
        self.labels2 = ["loss"]

        self.colors1 = ['r', 'b', 'g']
        self.colors2 = ['m']

        self.set_legend = 1



if __name__ == "__main__":
    project_path = r"C:\Users\shliu\Desktop\testPPT\testerror"
    # obj = PlotErr_emit_loss(project_path, 1)
    # obj.get_x_y()
    # obj.run(show_=1)

    obj = PlotErrout(project_path, "av_rms_xy")
    obj.get_x_y()
    obj.run(show_=1)