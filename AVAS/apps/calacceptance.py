import sys

import numpy as np
import os
import pandas as pd
import numpy
from dataprovision.beamset import BeamsetParameter
import math
from global_varible import c_light, Pi
from dataprovision.latticeparameter import LatticeParameter
import matplotlib.pyplot as plt
import matplotlib
from utils.tool import trans_xp_xx1
from utils.tool import cal_twiss
class Acceptance():
    def __init__(self, project_path = None):
        self.project_path = project_path
        self.plt_path = os.path.join(project_path, "OutputFile", "BeamSet.plt")
        if project_path:
            self.latttice_mulp_path = os.path.join(project_path, 'InputFile', 'lattice_mulp.txt')

    def get_para(self, num):
        obj = BeamsetParameter(self.plt_path)
        obj.get_one_parameter(num)

        self.np = obj.numofp
        self.Ib = obj.Ib
        self.freq = obj.freq *10**6 #单位Hz
        self.BaseMassInMeV = obj.BaseMassInMeV


        item={
            "BaseMassInMeV": self.BaseMassInMeV,
            "freq": self.freq,

        }

        part_dict = obj.one_step_dict
        part_list = obj.one_step_list

        item = {
            "BaseMassInMeV": self.BaseMassInMeV,
            "freq": self.freq,
            "part_dict": part_dict,
            "part_list": part_list,
            "num":num
        }


        all_part = trans_xp_xx1(item)



        return all_part


    def cal_accptance(self, kind):

        in_dis = self.get_para(0)
        out_dis = self.get_para(-1)

        in_dis = pd.DataFrame(in_dis, columns=['x', 'xx', 'y', 'yy', 'z', 'zz', 'phi', 'E', 'loss', "index"])
        out_dis = pd.DataFrame(out_dis, columns=['x', 'xx', 'y', 'yy', 'z', 'zz', 'phi', 'E', 'loss', "index"])
        # pd.set_option('display.max_columns', None)
        # print(in_dis)
        # # v= in_dis[in_dis["loss"] == 0]
        # # print(v)
        # x = in_dis["z"].values
        # y = in_dis["zz"].values
        #
        # x1 = in_dis["phi"].values
        # y1 = in_dis["E"].values
        # # plt.scatter(x, y, c='b', s=1)
        # plt.scatter(x1, y1)
        # plt.show()
        # sys.exit()
        #
        #
        # in_dis = in_dis.sort_values(by='index')
        # out_dis = out_dis.sort_values(by='index')

        w = in_dis["E"].mean()

        m = self.BaseMassInMeV

        self.gamma = w / m + 1
        self.beta = (1 - 1 / self.gamma ** 2) ** 0.5
        btgm = self.gamma * self.beta

        in_dis["E"] -= w
        # print(in_dis)

        #丢失的粒子
        loss_particles = in_dis[out_dis["loss"] == 0].copy()


        self.new_in_exist_dis = in_dis[out_dis["loss"] == 1].copy()
        self.new_out_exist_dis = out_dis[out_dis["loss"] == 1].copy()



        loss_particles_rows, _ = loss_particles.shape

        if loss_particles_rows == 0:
            raise Exception("All particels passed  through the lattice, avas can not calculate acceptance.")

        if kind == 0:
            #x方向
            emit_norm, t_alpha, t_beta, t_gamma = self.twiss(in_dis["x"], in_dis["xx"], 1)

            print(emit_norm, t_alpha, t_beta, t_gamma )

            loss_particles.loc[:,'ellipse'] = (t_gamma * loss_particles["x"] ** 2 +
                             2 * t_alpha * loss_particles["x"] * loss_particles["xx"] +
                             t_beta * loss_particles["xx"] ** 2)

            loss_particles = loss_particles.sort_values(by='ellipse')


            loss_min_emit = loss_particles['ellipse'].min()

            min_loss_index = loss_particles['ellipse'].idxmin()

            # 找到对应的 z 和 zz
            x_min = loss_particles.loc[min_loss_index, 'x']
            xx_min = loss_particles.loc[min_loss_index, 'xx']

            norm_emit = loss_min_emit * btgm

            self.t_alpha = t_alpha
            self.t_beta = t_beta
            self.t_gamma = t_gamma
            self.loss_particles = loss_particles
            return loss_min_emit, norm_emit, x_min, xx_min


        elif kind == 1:
            #y方向
            emit_norm, t_alpha, t_beta, t_gamma = self.twiss(in_dis["y"], in_dis["yy"], 1)

            print(emit_norm, t_alpha, t_beta, t_gamma )

            loss_particles.loc[:,'ellipse'] = (t_gamma * loss_particles["y"] ** 2 +
                             2 * t_alpha * loss_particles["y"] * loss_particles["yy"] +
                             t_beta * loss_particles["yy"] ** 2)

            loss_min_emit = loss_particles['ellipse'].min()

            min_loss_index = loss_particles['ellipse'].idxmin()

            # 找到对应的 z 和 zz
            y_min = loss_particles.loc[min_loss_index, 'y']
            yy_min = loss_particles.loc[min_loss_index, 'yy']

            norm_emit = loss_min_emit * btgm

            self.t_alpha = t_alpha
            self.t_beta = t_beta
            self.t_gamma = t_gamma
            self.loss_particles = loss_particles

            return loss_min_emit, norm_emit, y_min, yy_min



        elif kind == 2:

            emit_norm, t_alpha, t_beta, t_gamma = self.twiss(in_dis["z"], in_dis["zz"], 3)
            print(274, emit_norm, t_alpha, t_beta, t_gamma)


            loss_particles.loc[:,'ellipse'] = (t_gamma * loss_particles["z"] ** 2 +
                             2 * t_alpha * loss_particles["z"] * loss_particles["zz"] +
                             t_beta * loss_particles["zz"] ** 2)
            l1 = loss_particles.sort_values(by='ellipse')

            loss_min_emit = loss_particles['ellipse'].min()

            min_loss_index = loss_particles['ellipse'].idxmin()

            # 找到对应的 z 和 zz
            z_min = loss_particles.loc[min_loss_index, 'z']
            zz_min = loss_particles.loc[min_loss_index, 'zz']

            norm_emit = loss_min_emit * btgm *self.gamma**2
            self.t_alpha = t_alpha
            self.t_beta = t_beta
            self.t_gamma = t_gamma
            self.loss_particles = loss_particles

            return loss_min_emit, norm_emit, z_min, zz_min

        elif kind == 3:
            _, t_alpha, t_beta, t_gamma = self.twiss(in_dis["phi"], in_dis["E"], 1)

            print(t_alpha, t_beta, t_gamma)

            loss_particles.loc[:,'ellipse'] = (t_gamma * loss_particles["phi"] ** 2 +
                             2 * t_alpha * loss_particles["phi"] * loss_particles["E"] +
                             t_beta * loss_particles["E"] ** 2)

            loss_min_emit = loss_particles['ellipse'].min()


            min_loss_index = loss_particles['ellipse'].idxmin()

            # 找到对应的 z 和 zz
            phi_min = loss_particles.loc[min_loss_index, 'phi']
            E_min = loss_particles.loc[min_loss_index, 'E'] + w

            self.t_alpha = t_alpha
            self.t_beta = t_beta
            self.t_gamma = t_gamma
            self.loss_particles = loss_particles

            return loss_min_emit, None, phi_min, E_min,

    def twiss(self, x, x1, coefficient):
        # x_sigma = numpy.average(x ** 2)
        # y_sigma = numpy.average(y ** 2)
        # x_y_corr = numpy.average(x * y)
        # emit = (x_sigma * y_sigma - x_y_corr ** 2) ** 0.5
        # print("emit", emit)
        # beta = x_sigma / emit
        # gamma = y_sigma / emit
        # alpha = - x_y_corr / emit
        # emit_norm = btgm * emit
        # return emit_norm, alpha, beta, gamma
        item = {
            "x": x,
            "x1": x1,
            "coefficient": coefficient,
            "gamma": self.gamma,
            "beta": self.beta,
        }
        alpha_x, beta_x, gamma_x, epsilon_x, norm_epsilon_x =cal_twiss(item)
        return norm_epsilon_x, alpha_x, beta_x, gamma_x


if __name__ == "__main__":
    project_path = r"C:\Users\shliu\Desktop\xiaochu"
    obj = Acceptance(project_path)
    obj.cal_accptance(0)