import os.path
import sys
import time

from utils.readfile import read_dst, read_txt, read_dst_fast
import math

from global_varible import Pi, c_light
from dataprovision.latticeparameter import LatticeParameter
from utils.getinfotools import get_mass_freq
import random
import numpy as np

class DatasetParameter():
    """
    对dataset文件进行解析
    """

    def __init__(self, dataset_path, project_path=None):
        self.dataset_path = dataset_path
        self.z = []
        self.project_path = project_path
        self.len_num_evert_step = 41

    def get_parameter(self):
        dataset_info = read_txt(self.dataset_path, out='list')


        if len(dataset_info) == 0:
            return False
        if len(dataset_info) == 1:
            return False


        if len(dataset_info[-1]) != self.len_num_evert_step:
            dataset_info = dataset_info[:-1]
        # index = 0

        # nan_in = False
        # for index0, i in enumerate(dataset_info):
        #     if '-nan(ind)' in i or 'nan' in i:
        #         nan_in = True
        #         index = index0
        #         break
        # if nan_in:
        #     dataset_info = dataset_info[: index]
        # else:
        #     pass

        self.num_of_particle = float(dataset_info[0][28])

        dataset_info = [[float(j) for j in i] for i in dataset_info]


        self.dataset_index = [int(i[39]) for i in dataset_info]

        # random.seed(40)
        # for i in range(1, len(dataset_info)):
        #     selected_number = random.choice([0,1,2])
        #     dataset_info[i][35] = selected_number
        #     # print(i, selected_number)

        self.z = []
        sign1 = 0
        sign2 = 0
        #一旦进入二级铁，sign1就永远=1，

        for i in range(len(dataset_info)):
            if (dataset_info[i][35] == 0):
                sign2 = 0
                if (sign1 == 0):
                    self.z.append(dataset_info[i][5] + dataset_info[i][33])
                else:
                    self.z.append(self.z[-1] + dataset_info[i][38])
            elif (dataset_info[i][35] == 1):
                self.z.append(self.z[-1] + math.sqrt(dataset_info[i][37] ** 2 + dataset_info[i][38] ** 2))
                sign1 = 1
                sign2 = 0

            elif (sign2 == 0):
                #条件为2( 第35个数据为2 )， sign2= 0
                # 也就是说，如果这一次的标志为2，但是前一次的标志也为0， 1，那么进入这次循环
                self.z.append(self.z[-1] + math.sqrt(dataset_info[i][37] ** 2 + dataset_info[i][38] ** 2))
                sign2 = 1

            else:
                print(87)
                #条件为2， sign2 = 1
                #也就是说，如果这一次的标志为2，但是前一次的标志也为2，那么进入这次循环
                continue

        # for i in range(len(dataset_info)):
        #     if dataset_info[i][35] == 0:
        #         self.z.append(dataset_info[i][5] + dataset_info[i][33])
        #
        #     elif dataset_info[i][35] == 1:
        #         self.z.append(self.z[-1] + math.sqrt(dataset_info[i][37] ** 2 + dataset_info[i][38] ** 2))
        #
        #     elif dataset_info[i][35] == 2:
        #         pass


        self.x = [i[1] + i[29] for i in dataset_info]  # m
        self.px = [i[2] for i in dataset_info]  # MeV

        self.y = [i[3] + i[31] for i in dataset_info]
        self.py = [i[4] for i in dataset_info]

        # print("66")
        # print([i[1] for i in dataset_info][:4])
        # print([i[3] for i in dataset_info])
        self.syn_x = [i[29] for i in dataset_info]
        self.syn_y = [i[31] for i in dataset_info]



        self.pz = [i[6] for i in dataset_info]

        self.x_1 = [self.px[i] / self.pz[i] for i in range(len(self.pz))]  # rad
        self.y_1 = [self.py[i] / self.pz[i] for i in range(len(self.pz))]

        self.alpha_x = [i[7] for i in dataset_info]
        self.alpha_y = [i[8] for i in dataset_info]
        self.alpha_z = [i[9] for i in dataset_info]

        self.beta_x = [i[10] for i in dataset_info]  ##  mm/π.mrad
        self.beta_y = [i[11] for i in dataset_info]
        self.beta_z = [i[12] for i in dataset_info]

        self.emit_x = [i[13] for i in dataset_info]  # * 10**6 以后是 π.mm.mrad
        self.emit_y = [i[14] for i in dataset_info]
        self.emit_z = [i[15] for i in dataset_info]

        self.rms_x = [i[16] for i in dataset_info]  # 原本的单位是m, * 10**3 以后是mm
        self.rms_xx = [-1 * i[16] for i in dataset_info]
        self.rms_x1 = [i[17] for i in dataset_info]  # rad

        self.rms_y = [i[18] for i in dataset_info]
        self.rms_yy = [-1 * i[18] for i in dataset_info]
        self.rms_y1 = [i[19] for i in dataset_info]

        self.rms_z = [i[20] for i in dataset_info]
        self.rms_zz = [-1 * i[20] for i in dataset_info]

        self.rms_z1 = [i[21] for i in dataset_info]


        self.max_x = [i[22] for i in dataset_info]  # m
        self.max_xx = [-1 * i[22] for i in dataset_info]

        self.max_x1 = [i[23] for i in dataset_info]  # m
        self.max_z = [i[26] for i in dataset_info]  # m
        self.max_z1 = [i[27] for i in dataset_info]  # m


        self.max_y = [i[24] for i in dataset_info]
        self.max_yy = [-1 * i[24] for i in dataset_info]

        self.ek = [i[0] for i in dataset_info]  ##MeV

        self.loss = [self.num_of_particle - i[28] for i in dataset_info]  ##
        self.number_exist = [i[28] for i in dataset_info]

        self.sync_pz = [i[34] for i in dataset_info]



        if self.project_path:
            beam_info = get_mass_freq(self.project_path)
            self.BaseMassInMeV = beam_info["particlerestmass"]
            self.freq = beam_info["frequency"]
            self.current = beam_info["current"]
            self.current = np.array(self.number_exist) / self.num_of_particle * self.current



        if self.project_path:
            self.get_phi()


        if self.project_path:
            self.particle_t = [i[40] for i in dataset_info] #粒子飞行时间
            self.abs_phase = [i[40] *  2 * 180 * self.freq  for i in dataset_info] #绝对相位

        return True

    def get_lattice_end_index(self):
        lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')
        lattice_obj = LatticeParameter(lattice_mulp_path)
        lattice_obj.get_parameter()
        total_length = lattice_obj.total_length

        end_index = 0
        for i in range(len(self.z)):
            if self.z[i] > total_length:
                end_index = i
                break
        print("end_index", end_index)
        return end_index


    def get_phi(self):

        beta = []
        self.phi = []
        self.phi_phi = []
        for i in range(len(self.rms_z)):
            gammaaaa = self.ek[i] / self.BaseMassInMeV + 1
            beta.append(math.sqrt(1 - 1.0 / gammaaaa / gammaaaa))
            v = self.rms_z[i] / (beta[-1] * c_light) * self.freq * 360
            self.phi.append(v)
            self.phi_phi.append(-1 * v)


if __name__ == "__main__":
    # path1 = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_0_0\DataSet.txt"
    # obj = DatasetParameter(path1)
    # obj.get_parameter()
    # print(obj.z)
    #
    path1 = r"C:\Users\wangh\Desktop\test_maxin\proton\OutputFile\DataSet.txt"
    project_path =None
    obj = DatasetParameter(path1, project_path)
    v = obj.get_parameter()
    # print(len(obj.z)
    print(len(obj.rms_y))



    #
    # import numpy as np
    # import time
    # t0 = time.time()
    # path1 = r"C:\Users\shliu\Desktop\jiqunshiyong\test_err_dyn\OutputFile\DataSet.txt"
    # path1 = r"C:\Users\shliu\Desktop\test_yiman3\AVAS1\OutputFile\error_middle\output_0\DataSet.txt"
    # obj = DatasetParameter(path1)
    # obj.get_parameter()
    # print(obj.dataset_index)
