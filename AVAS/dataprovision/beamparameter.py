import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

from utils.readfile import read_dst, read_txt, read_dst_fast
import math
import numpy as np
from global_varible import c_light

from global_varible import Pi



import logging
logger = logging.getLogger(__name__)
class DstParameter:
    """
    对 dst 文件进行解析（向量化加速版）
    partran_dist columns assumed:
    0:x, 1:x', 2:y, 3:y', 4:phi(rad), 5:W(MeV)
    """
    def __init__(self, dst_path):
        self.dst_path = dst_path

        # header / scalar
        self.number = 0
        self.freq = 0.0
        self.BaseMassInMeV = 0.0
        self.Ib = 0.0
        self.energy = 0.0

        # arrays
        self.x = None
        self.x1 = None
        self.y = None
        self.y1 = None
        self.phi_rad = None
        self.phi_deg = None
        self.w = None

        self.z = None
        self.z1 = None
        self.z_speed = None
        self.dp_p = None

        # stats
        self.center_x = 0.0
        self.center_y = 0.0
        self.rms_x = 0.0
        self.rms_y = 0.0

    def get_parameter(self):
        raw = read_dst_fast(self.dst_path)

        # ---- scalars ----
        self.number = int(raw.get("number"))
        self.freq = float(raw.get("freq"))
        self.BaseMassInMeV = float(raw.get("basemassinmev"))
        self.Ib = float(raw.get("ib"))
        self.energy = float(raw.get("kneticenergy"))

        par = np.asarray(raw.get("partran_dist"), dtype=np.float64)
        # 防御：确保至少6列
        if par.ndim != 2 or par.shape[1] < 6:
            raise ValueError(f"partran_dist shape invalid: {par.shape}, expected (N, >=6)")

        # ---- base phase space (vectorized) ----
        # 单位转换
        self.x  = par[:, 0] * 10.0          # mm
        self.x1 = par[:, 1] * 1000.0        # mrad (只是展示用；物理计算仍用 par[:,1])
        self.y  = par[:, 2] * 10.0          # mm
        self.y1 = par[:, 3] * 1000.0        # mrad

        self.phi_rad = par[:, 4]            # rad
        self.phi_deg = par[:, 4] * 180.0 / Pi   # deg

        # 动能/能量（按你的循环里 i[5] 的用法）
        self.w = par[:, 5]                  # MeV

        # ---- synchronous particle ----
        self.syn_gamma = 1.0 + self.energy / self.BaseMassInMeV
        self.syn_beta = math.sqrt(1.0 - 1.0 / (self.syn_gamma * self.syn_gamma))
        syn_speed = self.syn_beta * c_light
        syn_speedz = syn_speed

        # ---- per-particle (vectorized) ----
        tmp_gamma = 1.0 + self.w / self.BaseMassInMeV
        tmp_beta = np.sqrt(1.0 - 1.0 / (tmp_gamma * tmp_gamma))
        tmp_speed = tmp_beta * c_light  #纵向速度

        tmp_t0 = self.phi_rad / (2.0 * math.pi * self.freq)  # seconds
        self.z = (-tmp_t0 * tmp_speed)
        # 这里使用原始 par[:,1], par[:,3]（未乘1000），保持与你原公式一致
        xp = par[:, 1]
        yp = par[:, 3]


        # self.dp_p = (tmp_gamma * self.z_speed - self.syn_gamma * syn_speedz) / (self.syn_gamma * syn_speedz)
        self.dp_p = (tmp_gamma * tmp_beta - self.syn_gamma * self.syn_beta) / (self.syn_gamma * self.syn_beta)

        avg_z_speed = np.mean(tmp_speed)
        self.z1 = (tmp_speed - avg_z_speed) / avg_z_speed * 1000.0  # mrad-like scale

        # ---- stats (vectorized) ----
        self.center_x = float(np.mean(self.x))
        self.center_y = float(np.mean(self.y))
        # 你原来是 sum(...) / number；等价于 mean
        self.rms_x = float(np.sqrt(np.mean((self.x - self.center_x) ** 2)))
        self.rms_y = float(np.sqrt(np.mean((self.y - self.center_y) ** 2)))

        # ---- return dict of arrays ----
        self.w_minus_mean = self.w - self.energy


        return {
            "number": self.number,
            "freq": self.freq,
            "BaseMassInMeV": self.BaseMassInMeV,
            "Ib": self.Ib,
            "energy": self.energy,
            "gamma": self.syn_gamma,
            "beta": self.syn_beta,


            "x": self.x,          # mm
            "y": self.y,          # mm
            "z": self.z * 1000,          # mm

            "x1": self.x1,        # mrad (显示用)
            "y1": self.y1,        # mrad
            "z1": self.z1,        # 你定义的相对速度偏差 *1000

            "phi": self.phi_deg,  # deg（你注释写rad，但你这里确实是deg）
            "w": self.w,          # MeV
            "dp_p": self.dp_p,    # fraction

            "w_minus_mean": self.w_minus_mean,
            "dp_p_100": self.dp_p * 100,
        }



# class DstParameter():
#     """
#     对dst文件进行解析
#     """
#     def __init__(self, dst_path):
#         self.dst_path = dst_path
#         self.number = 0
#         self.freq = 0
#         self.BaseMassInMeV = 0
#         self.Ib = 0
#         self.x_list = []   #mm
#         self.x1_list = []   #mrad
#         self.y_list = []
#         self.y1_list = []
#
#         self.phi_list = []
#         self.E_list = []
#
#         self.z_list = []
#         self.z1_list = []
#
#         self.energy = 0
#         self.gamma = 0
#         self.beta = 0
#         self.z_speed_list = []
#
#     def get_parameter(self):
#
#         data = read_dst_fast(self.dst_path)
#
#         self.number = data.get('number')
#         self.freq = data.get('freq')
#         self.BaseMassInMeV = data.get('basemassinmev')
#         self.Ib = data.get('ib')
#         self.energy = data.get('kneticenergy')
#         partran_dist = data.get('partran_dist')
#
#
#
#         self.x_list = partran_dist[:, 0] * 10   #mm
#         self.x1_list = partran_dist[:, 1] * 1000# mrad
#         self.y_list = partran_dist[:, 2] * 10
#         self.y1_list = partran_dist[:, 3] * 1000
#
#         self.phi_list = partran_dist[:, 4]   #rad
#         self.phi_list_deg =  partran_dist[:, 4] * 180 / Pi   #度
#         self.E_list = [i[5] for i in data]
#
#         self.z_list = []
#         self.z_speed_list = []
#         self.dp_p_list = []
#
#
#
#         syn_Phi = np.average(self.phi_list_deg)
#
#         syn_gamma = 1.0 +  self.energy / self.BaseMassInMeV
#         syn_beta = math.sqrt(1 - 1.0 / syn_gamma / syn_gamma)
#         syn_speed = syn_beta * c_light
#         syn_speedz = syn_speed
#
#
#         #该部分代码
#         for index, i in enumerate(data):
#             tmp_gamma = 1 + i[5] / self.BaseMassInMeV
#             tmp_beta = math.sqrt(1 - 1.0 / tmp_gamma / tmp_gamma)
#             tmp_speed = tmp_beta * c_light  # 总速度
#             tmp_speedz = math.sqrt(pow(tmp_speed, 2) / (pow(i[1], 2) + pow(i[3], 2) + 1))
#
#             tmp_t0 = i[4] / (2 * math.pi * self.freq)
#
#             self.z_list.append(-1 * tmp_t0 * tmp_speedz * 1000)  # mm
#
#             ##############################
#             # 使用z方向的速度
#             # self.z_speed_list.append(speedz)
#             # 总速度
#             self.z_speed_list.append(tmp_speedz)
#             #############################################
#             dp_p = (tmp_gamma * tmp_speedz - syn_gamma * syn_speedz) / (syn_gamma * syn_speedz)
#             self.dp_p_list.append(dp_p)
#
#
#             ##################
#         average_z_speed = np.mean(self.z_speed_list)
#
#
#         self.z1_list = [(i - average_z_speed) / average_z_speed * 1000 for i in self.z_speed_list]
#
#         #中心x
#         self.center_x = np.mean(self.x_list)
#
#         #中心y
#         self.center_y = np.mean(self.y_list)
#
#         #包络x
#
#         self.rms_x = np.sqrt( np.sum([(i-self.center_x)**2 for i in self.x_list ]) / self.number)
#
#         self.rms_y = np.sqrt( np.sum([(i-self.center_y)**2 for i in self.y_list ]) / self.number)
#
#
#         # v = PercentEmit(self.dst_path)
#         # self.emit = v.get_100_emit()
#
#         data = {
#             "x": self.x_list, #mm
#             "y": self.y_list,
#             "z": self.z_list,
#
#             "x1": self.x1_list, #mrad
#             "y1": self.y1_list,
#             "z1": self.z1_list,
#
#             "phi": self.phi_list_deg, #rad
#             "w":  self.E_list, #MeV
#             "dp_p": self.dp_p_list, #小数
#
#         }
#
#         return data


if __name__ == "__main__":
    # project_path = r"C:\Users\anxin\Desktop\00000"
    # res = get_entrance_beam_parameter(project_path)
    # print(res)

    # dst_path = r"C:\Users\anxin\Desktop\00000\InputFile\part_rfq.dst"
    # # obj = DstParameter(dst_path)
    # # obj.get_parameter()
    # # print(obj.x_list)
    from logger.logger_config import setup_logger
    dst_path = r"C:\Users\wangh\Desktop\phase_plot\1w.dst"

    obj = DstParameter(dst_path)
    res = obj.get_parameter()
    print(res["dp_p"][:10])
    print(res["dp_p_100"][:10])
        # import matplotlib.pyplot as plt
    # print(np.max(res["dp_p"]), np.min(res["dp_p"]) )
    # plt.scatter(res["z"], res["dp_p"]*100, s=2)
    #
    # plt.show()
