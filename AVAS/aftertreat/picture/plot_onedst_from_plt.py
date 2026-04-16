

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

import time
from global_varible import c_light, Pi

class PLlotdstfromplt():
    def __init__(self, plt_path, distance, dataset_path=None, specified_index= None, ):
        self.plt_path = plt_path
        self.distance = distance
        self.dataset_path = dataset_path
        self.specified_index = specified_index

        self.fig_size = (12.8, 9.2)
        self.fontsize = 18
        self.gird_bins = 100
        self.maxpar_num = 10**4



    def get_xy(self):


        obj = BeamsetParameter(self.plt_path)
        all_step = obj.get_step()
        print("所有步数", all_step)
        all_dict = obj.get_all_dict()
        print("最后一组", all_dict[-1])


        targe_dict_index = None
        for i in all_dict:
            if i["location"] > self.distance:
                targe_dict_index = all_dict.index(i)

                break
        #如果找不到比指定位置大的，选最后一个位置
        if targe_dict_index is None:
            targe_dict_index = all_step -1

        #如果指定的索引比所有的索引都大，那么选最后一个
        if self.specified_index is not None:
            if self.specified_index >= all_step:
                targe_dict_index = all_step -1

        targe_dict_index = targe_dict_index


        part_dict = all_dict[targe_dict_index]
        print("使用的一组", part_dict)
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


        return part_dict, new_part_list

    def get_dataset_data(self, plt_index):
        dataset_obj = DatasetParameter(self.dataset_path)
        dataset_obj.get_parameter()
        dataset_index_list = dataset_obj.dataset_index

        dataset_index = None
        #如果dataset中存在plt的索引
        if plt_index in dataset_index_list:
            dataset_index = dataset_index_list.index(plt_index)
        #如果dataset中不存在plt对应的索引
        elif plt_index not in dataset_index_list:
            t_index = plt_index -1
            if t_index  in dataset_index_list:
                dataset_index = dataset_index_list.index(t_index)
            else:
                dataset_index = None

        if dataset_index is not None:
            syn_x = dataset_obj.syn_x[dataset_index]
            syn_y = dataset_obj.syn_y[dataset_index]
        else:
            print("dataset中没有对应数据")
            syn_x = 0
            syn_y = 0
        return syn_x, syn_y


    def run(self,show_, fig=None, save_path=None):
        partran_dict, partran_dist = self. get_xy()

        partran_dist = numpy.array(partran_dist)
        x = partran_dist[:, 0] * 1000
        x1 = partran_dist[:, 1] * 1000  #mrad
        y = partran_dist[:, 2] * 1000
        y1 = partran_dist[:, 3] * 1000
        phi = partran_dist[:, 4] * 180 / Pi
        E = partran_dist[:, 5]
        E -= np.mean(E)
        z = partran_dist[:, 6] *1000

        plt_index = partran_dict["index"]
        syn_x, syn_y = self.get_dataset_data(plt_index)

        x = x + syn_x *1000
        y = y + syn_y *1000


        if not fig:
            fig = plt.figure(figsize=self.fig_size)

        font1 = {'family': 'Times New Roman', 'weight': 'bold', 'size': self.fontsize}

        # 绘制子图
        self._plot_density(fig, 221, x, x1, "x(mm)", "x'(mrad)", font1)
        self._plot_density(fig, 222, y, y1, "y(mm)", "y'(mrad)", font1)
        # self._plot_density(fig, 223, phi, E, "φ(deg)", "Energy(MeV)", font1)
        self._plot_density(fig, 223, z, x, "z(mm)", "x(mm)", font1)

        self._plot_density(fig, 224, z, y, "z(mm)", "y(mm)", font1)

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
        # colors = [(1, 1, 1), *plt.cm.jet(np.linspace(0, 1, 256))]  # 第一个颜色为白色，其余为 'jet'
        # custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors)
        #
        # scatter = ax.scatter(x, y, c=z, s=1.0, cmap=custom_cmap, vmin=0, vmax=1.0)

        # fig.colorbar(scatter, ax=ax)
        ax.scatter(x, y)

        ax.set_xlabel(xlabel, fontdict=font)
        ax.set_ylabel(ylabel, fontdict=font)

        ax.tick_params(axis='x', labelsize=14)  # x 轴刻度字体大小
        ax.tick_params(axis='y', labelsize=14)

        ax.grid(linestyle="--")

if __name__ == '__main__':
    project = r"C:\Users\wangh\Desktop\qiaoxin\Outputfile"
    plt_path = os.path.join(project, "BeamSet.plt")
    dataset_path = os.path.join(project, "DataSet.txt")

    #
    obj = PLlotdstfromplt(plt_path, 0.1, dataset_path, None)

    obj.run(show_=1)

    # obj.get_dataset_data(100)
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