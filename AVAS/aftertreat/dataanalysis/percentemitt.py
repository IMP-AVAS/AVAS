import sys

import math
from dataprovision.beamparameter import DstParameter
from utils.tool import cal_twiss
import time
import copy
class PercentEmit():
    """
    本类为计算发射度及百分比发射度
    get_percent_emit：该函数用来得到百分比发射度，返回结果分别为对于xx1，yy1，zz1使用的是归一化发射度，就是*alpha*beta， xy和phiE
    使用非归一化发射度，

    需要强调的是本例子中的alpha， beta嗾使百分比的，这和tracewin是不一样的，tracewin的alpha和beta都是全部粒子计算出来的


    """
    def __init__(self, ):
        self.x_list = []
        self.x1_list = []
        self.y_list = []
        self.y1_list = []
        self.z_list = []
        self.z1_list = []
        self.phi_list = []
        self.E_list = []
        self.z_speed_list = []
        self.number = 0
        self.Ib = 0
        self.freq = 0
        self.BaseMassInMeV = 0
        self.__C_light = 299792458

        self.gamma = 0
        self.beta = 0
        self.energy = 0

    # 计算任意一个twiss参数和发射度
    def                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         cal_twiss_emitt(self, x, x1, coefficient=1):
        item = {
            "x": x,
            "x1": x1,
            "coefficient": coefficient,
            "gamma": self.gamma,
            "beta": self.beta,
        }

        res =cal_twiss(item)
        return res


    def get_size(self, x, x1, alpha_x, beta_x, gamma_x):
        #计算全发射度
        return gamma_x * x ** 2 + 2 * alpha_x * x * x1 + beta_x * x1 ** 2

    # 得到任意一个平面的百分比发射度
    def get_any_emit(self, x, y, ratio, coefficient):
        t0 = time.time()
        #########################################################
        alpha_100, beta_100, gamma_100, epsilon_100, norm_epsilon_100 = self.cal_twiss_emitt(x, y, coefficient)

        t1 = time.time()
        #print(t1-t0, "计算twiss时间")

        size_list = []
        for i in range(len(self.x_list)):
            size = self.get_size(x[i], y[i], alpha_100, beta_100, gamma_100)
            size_list.append(size)
        index = int(ratio * self.number)


        t2 = time.time()
        #print(t2-t1, "get_size时间")

        if index >= len(size_list):
            index = len(size_list) - 1

        size = sorted(size_list)[index]

        indices = [i for i, x in enumerate(size_list) if x <= size]

        any_x_list = [x[i] for i in indices]
        any_y_list = [y[i] for i in indices]
        # #print(len(any_x_list))
        # 根据百分比的例子计算rms的twiss参数
        alpha_percent, beta_percent, gamma_percent, epsilon_percent, norm_epsilon_percent = list(self.cal_twiss_emitt(any_x_list, any_y_list, coefficient))


        t3 = time.time()
        #print(t3-t2, "百分比计算twiss参数时间")
        ###########################################################

        # 根据100%twiss参数，计算的全发射度
        all_epsilon_100 = self.get_all_epsilon(any_x_list, any_y_list, alpha_100, beta_100, gamma_100)

        t4 = time.time()
        #print(t4-t3, "获取全发射度参数时间")

        ###########################################################
        # 根据百分比twiss参数，计算全发射度
        all_epsilon_percent = self.get_all_epsilon(any_x_list, any_y_list, alpha_percent, beta_percent, gamma_percent)
        t5 = time.time()
        #print(t5-t4, "百分比计算twiss参数计算发射度时间")

        ###########################################################
        res = [alpha_percent, beta_percent, gamma_percent,
               norm_epsilon_percent, norm_epsilon_100,
               all_epsilon_percent,  all_epsilon_100,
               epsilon_percent, epsilon_100]


        return res

    # 得到任意一个平面的全发射度
    def get_all_epsilon(self, x, x1, alpha_x, beta_x, gamma_x):
        #计算最大全发射度
        all_size = []
        for i in range(len(x)):
            all_size.append(self.get_size(x[i], x1[i], alpha_x, beta_x, gamma_x))

        return max(all_size)

    # 得到几个平面的百分比发射度
    def get_percent_emit(self, item):
        # item = {
        #     "ratio": ,
        #     "picture_type": ,
        #     "dst_path": ,
        #     "dst_dict": ,
        #
        # }
        t0 = time.time()


        ratio = item.get("ratio")
        picture_type = item.get("picture_type")
        dst_path = item.get("dst_path")
        dst_dict = item.get("dst_dict")

        this_dst_dict = {}
        if dst_path and not dst_dict:
            dst_obj = DstParameter(dst_path)
            this_dst_dict = dst_obj.get_parameter()
        if dst_dict:
            this_dst_dict = dst_dict
        t1 = time.time()
        # #print(t1 - t0, "读取文件的时间")

        self.energy = this_dst_dict["energy"]
        self.gamma = this_dst_dict["gamma"]
        self.beta = this_dst_dict["beta"]
        self.number = this_dst_dict["number"]


        coefficient = 0
        if "z1" in picture_type:
            coefficient = 3
        elif "x1" in picture_type or "y1" in picture_type \
                or "dp/p" in picture_type:
            coefficient = 1

        #判断是否需要norm

        #判断coefficient


        #这里的alpha，beta是根据百分比粒子求的
        #epsi_xx1：rms发射度(归一化)  all_epsi_xx1：全twiss参数全发射度  percent_all_epsi_xx1：根据百分比twiss参数 全发射度

        # #print(this_dst_dict)
        self.x_list = this_dst_dict[picture_type[0]]
        self.y_list = this_dst_dict[picture_type[1]]

        if len(set(self.x_list)) == 1 or len(set(self.y_list)) == 1:
            return [0] * 11


        (alpha_percent, beta_percent, gamma_percent,
               norm_epsilon_percent, norm_epsilon_100,   #归一化发射度
               no_norm_all_epsilon_percent,  no_norm_all_epsilon_100,    #非归一化全发射度
               no_norm_epsilon_percent, no_norm_epsilon_100)= self.get_any_emit(self.x_list,  self.y_list, ratio, coefficient)   #非归一化发射度

        t2 = time.time()
        # #print(t2-t1, "计算twiss参数的时间")

        #返回的都是rms发射度，唯一的区别是归一化还是不归一化

        norm_all_epsilon_percent = no_norm_all_epsilon_percent
        norm_all_epsilon_100 = no_norm_all_epsilon_100
        if coefficient != 0:
            norm_all_epsilon_percent = self.beta * self.gamma ** coefficient * no_norm_all_epsilon_100
            norm_all_epsilon_100 = self.beta * self.gamma ** coefficient * no_norm_all_epsilon_percent


        #最终返回的是rms发射度
        res = [
            alpha_percent, beta_percent, gamma_percent,
            norm_epsilon_percent, norm_epsilon_100,
            norm_all_epsilon_percent, norm_all_epsilon_100,
            no_norm_epsilon_percent, no_norm_epsilon_100,
            no_norm_all_epsilon_percent, no_norm_all_epsilon_100
        ]


        return res

    # 得到几个平面的100%发射度



if __name__ == '__main__':
    # ['phi', 'w_minus_mean']
    dst_path = r"C:\Users\wangh\Desktop\324\v3\OutputFile\inData.dst"
    # pt = ["y", "y1"]
    pt = ['phi', 'w_minus_mean']
    pt = ['x', 'x1']

    item = {
        "ratio": 1,
        "picture_type": pt,
        "dst_path": dst_path,
        "dst_dict": None,
    }
    obj = PercentEmit()
    # pt = [["z", "dp_p_100"],  ["z", "w_minus_mean"], ["z1", "1"]]

    res = obj.get_percent_emit(item)
    print(res)



    # for i in pt:
    #     item["picture_type"] = i
    #     res = obj.get_percent_emit(item)
    #
    #     print(res)