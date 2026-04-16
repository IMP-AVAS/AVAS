
import numpy as np
import os
import pandas as pd
import numpy
from dataprovision.beamset import BeamsetParameter
import math
from global_varible import c_light, Pi
from dataprovision.latticeparameter import LatticeParameter
import matplotlib.pyplot as plt
from apps.calacceptance import Acceptance
from matplotlib.colors import LinearSegmentedColormap
class PlotAcc(Acceptance):
    def __init__(self, project_path = None):
        self.project_path = project_path
        self.plt_path = os.path.join(project_path, "OutputFile", "BeamSet.plt")
        if project_path:
            self.latttice_mulp_path = os.path.join(project_path, 'InputFile', 'lattice_mulp.txt')

    def run(self, kind):
        loss_min_emit, _, _,  _  = self.cal_accptance(kind)

        self.plot(None, self.t_alpha, self.t_beta, self.t_gamma, loss_min_emit, self.loss_particles, kind)

        return 0

    def plot(self, fig,  alpha, beta, gamma, loss_min_emit, loss_particles, kind):

        if not fig:
            fig = plt.figure(figsize = (6.4, 4.8))

        ax1 = fig.add_subplot(111)

        col_map = {
            0: ('x', 'xx'),
            1: ('y', 'yy'),
            2: ('z', 'zz'),
            3: ('phi', 'E')
        }

        if kind in col_map:
            col_x, col_y = col_map[kind]

            # 提取 numpy 数组
            x = loss_particles[col_x].values
            y = loss_particles[col_y].values

            # 散点图
            ax1.scatter(x, y, s=1, c='k')

            # 计算可视化范围
            margin = 1.2
            minx, maxx = x.min() * margin, x.max() * margin
            miny, maxy = y.min() * margin, y.max() * margin

            ax1.set_xlim(minx, maxx)
            ax1.set_ylim(miny, maxy)
            ax1.set_xlabel(col_x)
            ax1.set_ylabel(col_y)

        x = np.linspace(minx, maxx, 40)
        xp = np.linspace(miny, maxy, 40)


        # ax1.set_ylim([-60, 60])
        # ax1.set_xlim([-40, 40])
        x, xp = np.meshgrid(x, xp)

        Z = gamma * x ** 2 + 2 * alpha * x * xp + beta * xp ** 2
        # print("Z.min(), Z.max1() =", Z.min(), Z.max())
        # print("loss_min_emit =", loss_min_emit)

        ax1.contour(x, xp, gamma * x ** 2 + 2 * alpha * x * xp + beta * xp ** 2,
                   [loss_min_emit], colors='r')

        # colors = [(1, 1, 1), *plt.cm.jet(np.linspace(0, 1, 256))]  # 第一个颜色为白色，其余为 'jet'
        # custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors)
        #
        # ax2 = fig.add_subplot(223)
        # if kind in col_map:
        #     col_x, col_y = col_map[kind]
        #
        #     # 提取 numpy 数组
        #     #不丢失的粒子
        #
        #
        #     x1 = self.new_in_exist_dis.loc[self.new_in_exist_dis['loss'] == 1, col_x].values
        #     y1 = self.new_in_exist_dis.loc[self.new_in_exist_dis['loss'] == 1, col_y].values
        #     index1 = self.new_in_exist_dis.loc[self.new_in_exist_dis['loss'] == 1, "index"].values
        #     index1 = np.array(index1) / self.np
        #     print(len(index1))
        #     scatter = ax2.scatter(x1, y1, c=index1, s=1.0, cmap=custom_cmap, vmin=0, vmax=1.0)
        #     ax2.scatter(x1, y1, s=1, c='r')
        #     fig.colorbar(scatter, ax=ax2)
        #
        # ax3 = fig.add_subplot(224)
        # if kind in col_map:
        #     col_x, col_y = col_map[kind]
        #     x2 = self.new_out_exist_dis.loc[self.new_out_exist_dis['loss'] == 1, col_x].values
        #     y2 = self.new_out_exist_dis.loc[self.new_out_exist_dis['loss'] == 1, col_y].values
        #     index2 = self.new_out_exist_dis.loc[self.new_out_exist_dis['loss'] == 1, "index"].values
        #     index2 = np.array(index2) / self.np
        #     print(len(index2))
        #     scatter = ax3.scatter(x2, y2, c=index2, s=1.0, cmap=custom_cmap, vmin=0, vmax=1.0)
        #     fig.colorbar(scatter, ax=ax3)


        plt.show()



if __name__ == "__main__":
    project_path = r"C:\Users\shliu\Desktop\xiaochu"
    # project_path = r"C:\Users\shliu\Desktop\xiaochu"
    obj = PlotAcc(project_path)
    obj.run(0)