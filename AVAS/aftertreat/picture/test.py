from dataprovision.beamset import BeamsetParameter
from dataprovision.datasetparameter import DatasetParameter
import math
from global_varible import c_light, Pi

import struct
import os
import numpy
from dataprovision.latticeparameter import LatticeParameter
from aftertreat.dataanalysis.plt2dstdata import plt2dstdata
"""此文件为画相图"""

import numpy as np
import matplotlib.pyplot as plt

from utils.griddensity import grid_density
from matplotlib.colors import LinearSegmentedColormap
import time
from global_varible import c_light, Pi
class PLlotdstfromplt():
    def __init__(self, plt_path, dataset_path, distance):
        self.plt_path = plt_path
        self.distance = distance
        self.dataset_path = dataset_path
        self.fig_size = (12.8, 9.2)
        self.fontsize = 18
        self.gird_bins = 100
        self.maxpar_num = 10**4


    def get_xy(self):
        targe_dict_index = 0

        obj = BeamsetParameter(self.plt_path)
        all_step = obj.get_step()
        print(all_step)
        all_dict = obj.get_all_dict()

        targe_dict_index= 6852
        # targe_dict_index = None
        # for i in all_dict:
        #     if i["location"] > self.distance:
        #         targe_dict_index = all_dict.index(i)
        #         break
        # if targe_dict_index is None:
        #     targe_dict_index = all_step -1

        part_dict = all_dict[targe_dict_index]

        _, part_list = obj.get_one_parameter(targe_dict_index)

        # print(part_dict, targe_dict_index)
        np = obj.numofp
        Ib = obj.Ib
        freq = obj.freq *10**6 #变成Hz
        BaseMassInMeV = obj.BaseMassInMeV

        bunch_info = {
        "numofp": np,
        "Ib": Ib,            #mA
        "freq": freq,        #Hz
        "BaseMassInMeV": BaseMassInMeV,  #MeV
        "bunch_tpye": part_dict["tpye"],  #0/1
        }
        new_part_list = plt2dstdata(bunch_info, part_list)
        return new_part_list, part_dict

    def run(self,show_, fig=None, save_path=None):
        partran_dist, part_dict = self. get_xy()
        partran_dist = np.array(partran_dist)
        print(part_dict)
        # print(partran_dist)
        x = partran_dist[:, 0] * 1000
        x1 = partran_dist[:, 1] * 1000  #mrad
        y = partran_dist[:, 2] * 1000
        y1 = partran_dist[:, 3] * 1000
        phi = partran_dist[:, 4] * 180 / Pi
        E = partran_dist[:, 5]
        E -= np.mean(E)
        z = partran_dist[:, 6] *1000


        dataset_obj = DatasetParameter(self.dataset_path)
        dataset_obj.get_parameter()

        #dataset中所有的序号
        part_list = dataset_obj.dataset_index
        dataset_this_index = part_list.index(part_dict["index"])

        syn_x = dataset_obj.syn_x
        syn_y = dataset_obj.syn_y

        x += syn_x[dataset_this_index]
        y += syn_y[dataset_this_index]
        print(syn_x[dataset_this_index], syn_y[dataset_this_index])

        if not fig:
            fig = plt.figure(figsize=self.fig_size)

        font1 = {'family': 'Times New Roman', 'weight': 'bold', 'size': self.fontsize}

        # 绘制子图
        self._plot_density(fig, 221, x, x1, "x(mm)", "x'(mrad)", font1)
        self._plot_density(fig, 222, y, y1, "y(mm)", "y'(mrad)", font1)
        # self._plot_density(fig, 223, phi, E, "φ(deg)", "Energy(MeV)", font1)
        self._plot_density(fig, 223, z, x, "z(mm)", "x(mm)", font1)

        self._plot_density(fig, 224, x, y, "x(mm)", "y(mm)", font1)

        if show_:
            plt.show()


            return None
        else:
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)
            plt.close(fig)  # 释放资源，防止内存堆积
            return fig
    def _plot_density(self, fig, position, x, y, xlabel, ylabel, font):
        t0 = time.time()
        ax = fig.add_subplot(position)

        # 设置网格数，比如 100x100，可调整

        # 计算 2D 直方图
        z = grid_density(x, y, self.gird_bins, norm=True)
        # 画密度图
        colors = [(1, 1, 1), *plt.cm.jet(np.linspace(0, 1, 256))]  # 第一个颜色为白色，其余为 'jet'
        custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors)

        scatter = ax.scatter(x, y, c=z, s=1.0, cmap=custom_cmap, vmin=0, vmax=1.0)
        fig.colorbar(scatter, ax=ax)
        ax.set_xlabel(xlabel, fontdict=font)
        ax.set_ylabel(ylabel, fontdict=font)

        ax.tick_params(axis='x', labelsize=14)  # x 轴刻度字体大小
        ax.tick_params(axis='y', labelsize=14)

        ax.grid(linestyle="--")

if __name__ == '__main__':
    plt_path1 = R"C:\Users\wangh\Desktop\qiaoxin\test_qiao\OutputFile\BeamSet.plt"


    dataset_path = r"C:\Users\wangh\Desktop\qiaoxin\test_qiao\OutputFile\DataSet.txt"

    obj = PLlotdstfromplt(plt_path1, dataset_path, 3)
    obj.run(show_=1)


    # res = obj.get_all_dict()
    # print(res)

    # all_step = obj.get_step()
    # print(all_step)
    #
    # obj.get_one_parameter(200)
    #
    # np = obj.numofp
    # Ib = obj.Ib
    # freq = obj.freq * 10 ** 6  # 变成Hz
    # BaseMassInMeV = obj.BaseMassInMeV
    #
    # part_dict = obj.one_step_dict
    # part_list = obj.one_step_list
    # print(part_dict)