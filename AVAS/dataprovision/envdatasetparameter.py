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


class EnvDatasetParameter():
    def __init__(self, dataset_path, project_path=None):
        self.dataset_path = dataset_path
        self.z = []
        self.project_path = project_path
        # self.len_num_evert_step = 41


    def get_parameter(self):
        dataset_info = read_txt(self.dataset_path, out='list')[1:]
        ####################################
        dataset_info = [[float(j) for j in i[1:]] for i in dataset_info]

        dataset_info = [["#"] + i for i in dataset_info]
        #########################
        self.z = [i[1] for i in dataset_info] #m

        self.x = [i[2] for i in dataset_info] #m
        self.x1 = [i[3] for i in dataset_info]  #rad


        self.y = [i[4] for i in dataset_info]  #m
        self.y1 = [i[5] for i in dataset_info]  #rad


        self.ek = [i[8] for i in dataset_info]

        self.beta_rel = [i[10] for i in dataset_info]
        self.gamma_rel = [i[11] for i in dataset_info]

        self.emit_x = [i[12] for i in dataset_info]  # pi·mm·mrad。
        self.emit_y = [i[13] for i in dataset_info]  # pi·mm·mrad。
        self.emit_z = [i[14] for i in dataset_info]

        self.alpha_x = [i[15] for i in dataset_info]
        self.beta_x = [i[16] for i in dataset_info]

        self.alpha_y = [i[17] for i in dataset_info]
        self.beta_y = [i[18] for i in dataset_info]

        return 1


