#用于将density中的图像可视化
from aftertreat.picture.initialplot import PicturePlot_2D, Picturedensity
from dataprovision.densityparameter import DensityParameter
import matplotlib.pyplot as plt
import numpy as np
from utils.tool import get_list_interval, generate_web_picture_param
import sys
class PlotDensity(Picturedensity):
    def __init__(self, path, picture_type, sample_interval):
        super(PlotDensity, self).__init__()
        self.path = path
        self.bins = 300
        self.picture_type = picture_type
        self.sample_interval = sample_interval

    def get_x_y(self, ):
        picture_type = self.picture_type
        sample_interval = self.sample_interval

        file_obj = DensityParameter(self.path)
        data = file_obj.get_parameter()
        self.bins = file_obj.grid_num
        # print(data["tab_lis"])
        type_lis = ['x', 'y', 'r', 'z']
        self.z = data["zg_lis"]

        index = type_lis.index(picture_type)

        self.y = []
        self.density = []
        for i in range(len(self.z)):
            #获取最大值最小值
            v = [data["minb_lis"][i][index] * 1000, data["maxb_lis"][i][index] * 1000]
            self.y.append(v)
            this_density = np.array(data["tab_lis"][i][index])

            if index == 2:
                bin_edges = np.linspace(v[0], v[1], self.bins + 1)
                # 面积
                area = np.array([bin_edges[i] ** 2 - bin_edges[i - 1] ** 2 for i in range(1, len(bin_edges))])
                ration = this_density / area
                this_density = ration
            self.density.append(this_density)




        # print(self.y)
        self.xlabel = "Position(m)"

        if picture_type == 'x':
            self.ylabel = "X (mm)"
        elif picture_type == 'y':
            self.ylabel = "Y (mm)"
        elif picture_type == 'r':
            self.ylabel = "R (mm)"
        elif picture_type == 'z':
            self.ylabel = "Z (mm)"

        #根据参数生成矩阵
        self.z_m = np.tile(self.z, (self.bins, 1))

        self.y_m = np.zeros((self.bins, len(self.z)))
        self.density_m = np.zeros((self.bins, len(self.z)))

        for i in range(len(self.z)):
            min_edge = self.y[i][0]
            max_edge = self.y[i][1]



            bin_edges = np.linspace(min_edge, max_edge, self.bins + 1)

            self.y_m[:, i] = bin_edges[:-1]


            self.density_m[:, i] = self.density[i] / np.max(self.density[i])
            #

        self.z_m = self.z_m[:,::sample_interval]
        self.y_m = self.y_m[:,::sample_interval]
        self.density_m = self.density_m[:,::sample_interval]

class PlotDensityLevel(PicturePlot_2D):
    def __init__(self, path, picture_type, sample_interval):
        super().__init__()
        self.bins = 300
        self.path = path
        self.picture_type = picture_type
        self.sample_interval = sample_interval

    def get_x_y(self):
        picture_type = self.picture_type
        sample_interval = self.sample_interval

        file_obj = DensityParameter(self.path)
        data = file_obj.get_parameter()
        self.bins = file_obj.grid_num

        # print(data["tab_lis"])
        type_lis = ['x', 'y', 'r', 'z']
        self.x = data["zg_lis"]

        index = type_lis.index(picture_type)
        edge_max = []
        edge_min = []
        if index != 2:
            for i in range(len(self.x)):
                v = [data["minb_lis"][i][index] * 1000, data["maxb_lis"][i][index] * 1000]

                density = data["tab_lis"][i][index]

                bin_edges = np.linspace(v[0], v[1], self.bins + 1)
                mid = len(bin_edges) // 2

                density = np.array(density)

                counts1 = density[mid:]
                counts2 = density[:mid][::-1]
                edge1 = bin_edges[mid:]
                edge2 = bin_edges[:mid][::-1]



                ratio = counts1 + counts2

                # 归一化 ratio，使得总和为 1
                ratio_normalized = ratio / np.sum(ratio)

                # 计算归一化后的累积比例
                cumulative_ratio = np.cumsum(ratio_normalized)
                # print(cumulative_ratio)

                # 找到达到90%、99%、99.9%累积值的索引
                thresholds = [0.9, 0.99, 0.999, 0.9999]
                threshold_indices = [np.searchsorted(cumulative_ratio, threshold) for threshold in thresholds]
                # print(threshold_indices)

                # 获取对应边界的值
                # 上边界
                boundaries1 = [edge1[idx] for idx in threshold_indices]
                #下边界
                boundaries2 = [edge2[idx] for idx in threshold_indices]
                # print(boundaries1)
                # print(boundaries2)

                edge_max.append(boundaries1)
                edge_min.append(boundaries2)
                # breakpoint()

            edge_max_90 = [i[0] for i in edge_max]
            edge_max_99 = [i[1] for i in edge_max]
            edge_max_999 = [i[2] for i in edge_max]
            edge_max_9999 = [i[2] for i in edge_max]

            edge_min_90 = [i[0] for i in edge_min]
            edge_min_99 = [i[1] for i in edge_min]
            edge_min_999 = [i[2] for i in edge_min]
            edge_min_9999 = [i[2] for i in edge_min]

            self.y = [
                edge_max_90,
                edge_max_99,
                edge_max_999,
                edge_max_9999,
                edge_min_90,
                edge_min_99,
                edge_min_999,
                edge_min_9999,

            ]
        elif index ==2:
            for i in range(len(self.x)):
                v = [data["minb_lis"][i][index] * 1000, data["maxb_lis"][i][index] * 1000]

                density = data["tab_lis"][i][index]


                ratio = density

                # 归一化 ratio，使得总和为 1
                ratio_normalized = ratio / np.sum(ratio)

                # 计算归一化后的累积比例
                cumulative_ratio = np.cumsum(ratio_normalized)
                # print(cumulative_ratio)
                bin_edges = np.linspace(v[0], v[1], self.bins + 1)[:self.bins]
                edge1 = bin_edges
                # 找到达到90%、99%、99.9%累积值的索引
                thresholds = [0.9, 0.99, 0.999, 0.9999]
                threshold_indices = [np.searchsorted(cumulative_ratio, threshold) for threshold in thresholds]
                # print(threshold_indices)

                # 获取对应边界的值
                # 上边界
                boundaries1 = [edge1[idx] for idx in threshold_indices]

                edge_max.append(boundaries1)

                # breakpoint()

                edge_max_90 = [i[0] for i in edge_max]
                edge_max_99 = [i[1] for i in edge_max]
                edge_max_999 = [i[2] for i in edge_max]
                edge_max_9999 = [i[2] for i in edge_max]



                self.y = [
                    edge_max_90,
                    edge_max_99,
                    edge_max_999,
                    edge_max_9999,
                ]
        # self.xlim = [0.5, 0.75]
        self.colors = ['r', 'b', 'blueviolet', 'g'] * 2

        self.xlabel = "Position(m)"

        if picture_type == 'x':
            self.ylabel = "X Particle density probability (mm)"

        elif picture_type == 'y':
            self.ylabel = "Y Particle density probability (mm)"

        elif picture_type == 'r':
            self.ylabel = "R Particle density probability (mm)"

        elif picture_type == 'z':
            self.ylabel = "Z Particle density probability (mm)"

        labels = [r'$10^{-1}$', r'$10^{-2}$', r'$10^{-3}$', r'$10^{-4}$', None, None, None, None]
        self.labels = labels
        self.set_legend = True

        self.x = get_list_interval(self.x, self.sample_interval)
        self.y = get_list_interval(self.y, self.sample_interval)

        self.y = [[float(x) for x in row] for row in self.y]

        if not isinstance(self.y[0], list):
            self.y = [self.y]
        if not isinstance(self.x[0], list):
            self.x = [self.x]

        if len(self.x) != len(self.y):
            self.x = self.x * len(self.y)
        # print(len(self.x))
        # print(len(edge_max_90))


class PlotDensityProcess(PicturePlot_2D):
    """
    用来将density文件中其他数据可视化
    """
    def __init__(self, path, density_plane, picture_type, sample_interval):
        super().__init__()
        self.path = path
        self.density_plane = density_plane
        self.picture_type = picture_type
        self.sample_interval = sample_interval

    def get_x_y(self,):
        density_plane = self.density_plane
        picture_type = self.picture_type
        sample_interval = self.sample_interval
        file_obj = DensityParameter(self.path)
        data = file_obj.get_parameter()
        self.x = data["zg_lis"]
        emit = data["emit_lis"]
        moy = data["moy_lis"]
        rms_size_lis = data["rms_size_lis"]
        maxb_lis = data["maxb_lis"]
        minb_lis = data["minb_lis"]
        maxr_lis = data["maxr_lis"]
        minr_lis = data["minr_lis"]
        lost_lis = data["lost_lis"]
        maxlost_lis = data["maxlost_lis"]
        minlost_lis = data["minlost_lis"]
        print(rms_size_lis[:10])
        if picture_type == "centroid":
            if density_plane == "x":
                self.y = [i[0] for i in moy]
            elif density_plane == "y":
                self.y = [i[1] for i in moy]
            elif density_plane == "r":
                self.y = [i[2] for i in moy]
            elif density_plane == "z":
                self.y = [i[3] for i in moy]
            self.y = np.array(self.y) * 1000
            self.ylabel = f"Residual orbit  {density_plane.upper()} (mm)"
            self.xlabel = "z(m)"

        elif picture_type == "rms_size":
            if density_plane == "x":
                self.y = [i[0] for i in rms_size_lis]
            elif density_plane == "y":
                self.y = [i[1] for i in rms_size_lis]
            elif density_plane == "r":
                self.y = [i[2] for i in rms_size_lis]
            elif density_plane == "z":
                self.y = [i[3] for i in rms_size_lis]
            self.y = np.array(self.y) * 1000
            self.ylabel = f"Rms size  {density_plane.upper()} (mm)"
            self.xlabel = "z(m)"

        elif picture_type == "rms_size_max":
            if density_plane == "x":
                y0 = [i[0] for i in maxb_lis]
                y1 = [i[0] for i in minb_lis]
            elif density_plane == "y":
                y0 = [i[1] for i in maxb_lis]
                y1 = [i[1] for i in minb_lis]
            elif density_plane == "r":
                y0 = [i[2] for i in maxb_lis]
                y1 = [i[2] for i in minb_lis]

            elif density_plane == "z":
                y0 = [i[3] for i in maxb_lis]
                y1 = [i[3] for i in minb_lis]
            y0 = np.array(y0) * 1000
            y1 = np.array(y1) * 1000

            self.y = [list(y0), list(y1)]
            # self.y = np.array(self.y) * 1000
            # self.ylim = [-5, 5]
            self.ylabel = f"Max rms size  {density_plane.upper()} (mm)"
            self.xlabel = "z(m)"

        elif picture_type == "emit":
            y0 = [i[0] * 10**6 for i in emit]
            y1 = [i[1] * 10**6 for i in emit]
            y2 = [i[2] * 10**6 for i in emit]
            self.y = [y0, y1, y2]
            self.labels = [r"$\varepsilon_{xx'}$", r"$\varepsilon_{yy'}$", r"$\varepsilon_{zz'}$"]
            self.ylabel = r"$Rms emittanace (\pi.mm.mrad)$"
            self.xlabel = "z(m)"
            self.set_legend = 1
        elif picture_type == "lost":
            self.y = lost_lis
            self.ylabel = f"Lost"
            self.xlabel = "z(m)"
        elif picture_type == "maxlost":
            self.y = lost_lis
            self.ylabel = f"Max lost"
            self.xlabel = "z(m)"
        elif picture_type == "minlost":
            self.y = lost_lis
            self.ylabel = f"Min lost"
            self.xlabel = "z(m)"

        self.x = get_list_interval(self.x, self.sample_interval)
        self.y = get_list_interval(self.y, self.sample_interval)

        self.y = list(self.y)
        if not isinstance(self.y[0], list):
            self.y = [self.y]

        # if picture_name == 'emit_x':
        #     self.y = [i[0] *10**6 for i in emit]
        #
        #     self.xlabel = "z(m)"
        #     self.ylabel = "Average Emit_x(pi*mm*mrad)"
        #
        # elif picture_name == 'lost':
        #     self.y = data["lost_lis"]
        #
        #
        #     self.xlabel = "z(m)"
        #     self.ylabel = "Average Loss(pi*mm*mrad)"
        #
        #
        # elif picture_name == 'rms_x':
        #     rms_size_lis = data["rms_size_lis"]
        #     rmsx = [i[0]*10**3 for i in rms_size_lis]
        #
        #     self.y = rmsx
        #     self.xlabel = "z(m)"
        #     self.ylabel = "Average Rms_x(mm)"
        #
        # elif picture_name == 'av_xy':
        #     moy_lis = data["moy_lis"]
        #     x = [i[0]*10**3 for i in moy_lis]
        #     y = [i[1]*10**3 for i in moy_lis]
        #     self.y = [x, y]
        #     self.labels = ['x', 'y',]
        #     self.xlabel = "z(m)"
        #     self.ylabel = "Average Position(mm)"
        #     self.set_legend = 1
        #
        #
        # elif picture_name == 'rms_xy':
        #     rms_size_lis = data["rms_size_lis"]
        #
        #     rmsx = [i[0]*10**3 for i in rms_size_lis]
        #     rmsy = [i[1]*10**3 for i in rms_size_lis]
        #
        #     self.y = [rmsx, rmsy]
        #     self.xlabel = "z(m)"
        #     self.ylabel = "Average Rms size(mm)"
        #     self.labels = ['x', 'y',]
        #     self.set_legend = 1
if __name__ == "__main__":
    # path1 = r"C:\Users\shliu\Desktop\testz\OutputFile\density_par_2_2.dat"
    # path2 = r"C:\Users\shliu\Desktop\testz\OutputFile\density_tot_par_2.dat"
    # path3 = r"C:\Users\shliu\Desktop\testz\OutputFile\density_tot_par.dat"

    # path1 = r"C:\Users\shliu\Desktop\test_yiman3\AVAS1\OutputFile\density_par_1_98.dat"
    path1 = r"C:\Users\wangh\Desktop\long_dis2\av_err\OutputFile\density_tot_par.dat"
    # obj = PlotDensityProcess(path1, "x", "centroid", 1)
    # obj.get_x_y()
    # obj.run(show_=1)

    obj = PlotDensity(path1, "x", 1 )


    obj.get_x_y()
    obj.xlim = [-150,150]
    obj.run(show_=1, fig = None)

    # # v = PlotDensityLevel(path1)
    # # v.get_x_y(picture_type='r')
    # # v.ylim = [0, 50]
    # # v.run(show_=1, fig=None)
    # v = PlotDensityLevel(path1, "x", 1)
    # v.get_x_y()
    # v.run(show_=1, fig=None)