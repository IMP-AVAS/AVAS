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

class SinglePparameter():
    """
    """

    def __init__(self, single_p_path, project_path=None):
        self.single_p_path = single_p_path
        self.z = []
        self.project_path = project_path
        self.len_num_evert_step = 41

    def get_parameter(self):
        single_p_info = read_txt(self.single_p_path, out='list')[3:]


        if len(single_p_info) == 0:
            return False
        if len(single_p_info) == 1:
            return False

        single_p_info = [[float(j) for j in i] for i in single_p_info]

        self.x = [i[0] for i in single_p_info]
        self.y = [i[1] for i in single_p_info]
        self.z = [i[2] for i in single_p_info]

        self.ek = [i[6] for i in single_p_info]
        self.particle_t = [i[7] for i in single_p_info]

        if self.project_path:
            beam_info = get_mass_freq(self.project_path)
            self.freq = beam_info["frequency"]

        if self.project_path:
            self.abs_phase = [i[7] *  2 * 180 * self.freq  for i in single_p_info] #

        return True





if __name__ == "__main__":
    # path1 = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_0_0\DataSet.txt"
    # obj = DatasetParameter(path1)
    # obj.get_parameter()
    # print(obj.z)
    #
    path1 = r"D:\using\test_avas_qt\test_one_p\OutputFile\SingleParticle.txt"
    project_path = r"D:\using\test_avas_qt\test_one_p"
    obj = SinglePparameter(path1, project_path)
    v = obj.get_parameter()
    # print(obj.x)
    # print(obj.abs_phase)
    # #

