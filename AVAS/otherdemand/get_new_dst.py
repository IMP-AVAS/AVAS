import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

from utils.readfile import read_dst, read_txt, read_dst_fast
import math
import numpy as np
from global_varible import c_light
import matplotlib.pyplot as plt
from global_varible import Pi

class DstParameter():
    """
    对dst文件进行解析
    """
    def __init__(self, dst_path):
        self.dst_path = dst_path
        self.number = 0
        self.freq = 0
        self.BaseMassInMeV = 0
        self.Ib = 0
        self.x_list = []   #mm
        self.x1_list = []   #mrad
        self.y_list = []
        self.y1_list = []

        self.phi_list = []
        self.E_list = []

        self.z_list = []
        self.z1_list = []

        self.energy = 0
        self.gamma = 0
        self.beta = 0
        self.z_speed_list = []

    def get_parameter(self):

        data = read_dst_fast(self.dst_path)

        self.number = data.get('number')
        self.freq = data.get('freq')
        self.BaseMassInMeV = data.get('basemassinmev')
        self.Ib = data.get('ib')

        data = data.get('partran_dist')





        new_data = []
        for index, i in enumerate(data):

            t_data = [0] * 6
            tmp_gamma = 1 + i[5] / self.BaseMassInMeV
            tmp_beta = math.sqrt(1 - 1.0 / tmp_gamma / tmp_gamma)
            tmp_speed = tmp_beta * c_light  # 总速度
            speedz = math.sqrt(pow(tmp_speed, 2) / (pow(i[1], 2) + pow(i[3], 2) + 1))
            tmp_betaz = speedz / c_light

            tmp_t0 = i[4] / (2 * math.pi * self.freq)

            t_data[4] = -1 * tmp_t0 * speedz
            # t_data[5] = tmp_betaz * speedz * tmp_gamma

            t_data[0] = i[0]/100- tmp_t0 * i[1] *  speedz
            t_data[1] = i[1]
            t_data[2] = i[2]/100- tmp_t0 * i[3] *  speedz
            t_data[3] = i[3]


            self.z_list.append(-1 * tmp_t0 * speedz * 1000)  # mm

            new_data.append(t_data)
        return new_data
    def plot(self):
        new_data = self.get_parameter()
        x = np.array([i[0] for i in new_data]) * 1000
        x1 = np.array([i[1] for i in new_data]) * 1000
        y = np.array([i[2] for i in new_data]) * 1000
        y1 = np.array([i[3] for i in new_data]) * 1000
        z = np.array([i[4] for i in new_data])*1000


        fig, axs = plt.subplots(2, 2, figsize=(10,12))  # 4行3列的子图布局
        axs[0, 0].scatter(x, x1)
        axs[0, 1].scatter(y, y1)
        axs[1, 0].scatter(z, x)
        axs[1, 1].scatter(x, y)
        plt.show()



if __name__ == '__main__':
    dst_path = r"C:\Users\wangh\Desktop\qiaoxin\test_qiao\OutputFile\100bu\outData_3.248352.dst"
    obj = DstParameter(dst_path)
    obj.plot()