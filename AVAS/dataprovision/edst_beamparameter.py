import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

from utils.readfile import read_dst, read_txt, read_dst_fast, read_edst
import math
import numpy as np
from global_varible import c_light

from global_varible import Pi



import logging
logger = logging.getLogger(__name__)
class EdstParameter:
    """
    对 dst 文件进行解析（向量化加速版）
    partran_dist columns assumed:
    0:x, 1:x', 2:y, 3:y', 4:phi(rad), 5:W(MeV)
    """
    def __init__(self, item):
        self.edst_path = item.get('edst_path')

        # header / scalar
        # self.number = 0
        # self.freq = 0.0
        # self.BaseMassInMeV = 0.0
        # self.Ib = 0.0
        # self.energy = 0.0
        #
        # # arrays
        # self.x = None
        # self.x1 = None
        # self.y = None
        # self.y1 = None
        # self.phi_rad = None
        # self.phi_deg = None
        # self.w = None
        #
        # self.z = None
        # self.z1 = None
        # self.z_speed = None
        # self.dp_p = None
        #
        # # stats
        # self.center_x = 0.0
        # self.center_y = 0.0
        # self.rms_x = 0.0
        # self.rms_y = 0.0

    def get_parameter(self):
        raw = read_edst(self.edst_path)

        # ---- scalars ----
        self.number = int(raw.get("number"))
        self.freq = float(raw.get("freq"))
        par = np.asarray(raw.get("partran_dist"), dtype=np.float64)
        self.BaseMassInMeV = float(raw.get("basemassinmev"))

        mass_charge = par[:, [6, 7]]
        #代表的是电荷和质量

        # 找出所有不同的 质量-电荷 组合
        unique_mass_charge = np.unique(mass_charge, axis=0)
        print(unique_mass_charge)

        key1 = unique_mass_charge[0]
        key2 = unique_mass_charge[1]

        mask1 = np.all(np.isclose(mass_charge, key1), axis=1)
        mask2 = np.all(np.isclose(mass_charge, key2), axis=1)

        par_group1 = par[mask1]
        par_group2 = par[mask2]

        print(len(par))

    ################粒子1的信息
        self.b1_x = par_group1[:, 0] * 10 #mm
        self.b1_x1 = par_group1[:, 1] * 1000 #mrad
        self.b1_y = par_group1[:, 2] * 10
        self.b1_y1 = par_group1[:, 3] * 1000

        self.b1_phi_rad = par_group1[:, 4]            # rad
        self.b1_phi_deg = par_group1[:, 4] * 180.0 / Pi   # deg

        self.b1_w = par_group1[:, 5] #MeV

    ################粒子2的信息
        self.b2_x = par_group2[:, 0] * 10  # mm
        self.b2_x1 = par_group2[:, 1] * 1000  # mrad
        self.b2_y = par_group2[:, 2] * 10
        self.b2_y1 = par_group2[:, 3] * 1000

        self.b2_phi_rad = par_group2[:, 4]            # rad
        self.b2_phi_deg = par_group2[:, 4] * 180.0 / Pi   # deg

        self.b2_w = par_group2[:, 5]  # MeV

        return {
            "number": self.number,
            "freq": self.freq,  #Hz
            "BaseMassInMeV": self.BaseMassInMeV,
            "unique_mass_charge": unique_mass_charge,
            "number_1": len(par_group1),
            "number_2": len(par_group2),

            "b1_x": self.b1_x,
            "b1_x1": self.b1_x1,
            "b1_y": self.b1_y,
            "b1_y1": self.b1_y1,
            "b1_phi_rad": self.b1_phi_rad,
            "b1_phi_deg": self.b1_phi_deg,
            "b1_w": self.b1_w,

            "b2_x": self.b2_x,
            "b2_x1": self.b2_x1,
            "b2_y": self.b2_y,
            "b2_y1": self.b2_y1,
            "b2_phi_rad": self.b2_phi_rad,
            "b2_phi_deg": self.b2_phi_deg,
            "b2_w": self.b2_w,
        }



        # return {
        #     "number": self.number,
        #     "freq": self.freq,
        #     "BaseMassInMeV": self.BaseMassInMeV,
        #     "Ib": self.Ib,
        #     "energy": self.energy,
        #     "gamma": self.syn_gamma,
        #     "beta": self.syn_beta,
        #
        #
        #     "x": self.x,          # mm
        #     "y": self.y,          # mm
        #     "z": self.z * 1000,          # mm
        #
        #     "x1": self.x1,        # mrad (显示用)
        #     "y1": self.y1,        # mrad
        #     "z1": self.z1,        # 你定义的相对速度偏差 *1000
        #
        #     "phi": self.phi_deg,  # deg（你注释写rad，但你这里确实是deg）
        #     "w": self.w,          # MeV
        #     "dp_p": self.dp_p,    # fraction
        #
        #     "w_minus_mean": self.w_minus_mean,
        #     "dp_p_100": self.dp_p * 100,
        # }


if __name__ == "__main__":

    dst_path = r"C:\Users\wangh\Desktop\qx\2beam\OutputFile\outData_6.992532.edst"

    obj = EdstParameter(dst_path)
    res = obj.get_parameter()

    # import matplotlib.pyplot as plt
    # print(np.max(res["dp_p"]), np.min(res["dp_p"]) )
    # plt.scatter(res["z"], res["dp_p"]*100, s=2)
    #
    # plt.show()
