
import copy

from matplotlib.cbook import safe_first_element

from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name

from utils.tool import judge_command_on_element, judge_command_under_element, add_element_end_index, delete_element_end_index

import global_varible
import random
from scipy.optimize import minimize
import os
from core.MultiParticle import MultiParticle

from utils.treat_directory import list_files_in_directory, copy_directory, delete_directory
from apps.match_with_command.setdiaginfo import SetDiagInfo
import math


#该函数的作用是周期匹配的算法
class PeriodMatchalgorithm():
    def __init__(self, item):
        self.project_path = item.get("project_path")
        self.seed = item.get("seed")
        self.if_normal = item.get("if_normal")
        self.field_path = item.get("field_path")
        self.if_generate_density_file = item.get("if_generate_density_file")
        self.restart = item.get("restart", 0)
        self.lattice_path = os.path.join(self.project_path, "InputFile", "lattice.txt")
        self.match_sim_type = item.get("match_sim_type")
        self.device = item.get("device") or "cpu"

        self.match_opti_out0_path = os.path.join(self.project_path, "OutputFile", "match_opti", "output_0")

        if os.path.exists(self.match_opti_out0_path):
            delete_directory(self.match_opti_out0_path)
        os.makedirs(self.match_opti_out0_path)

    def opti_one_time(self):
        # 1. 读取beam_client.txt.


if __name__ == "__main__":
    item = \
        {
            "project_path": r"F:\using\test_avas_qt\env_project_match",
            "field_path": r"F:\using\test_avas_qt\env_project_match\FieldFile",
            "match_sim_type": "env",  # 匹配时使用的match_type
        }
    obj = PeriodMatchalgorithm(item)

    lattice_path = r"F:\using\test_avas_qt\env_project_match\InputFile\lattice_mulp.txt"
    lattice_list, _ = read_lattice_mulp_with_name(lattice_path)

    res = obj.opti_one_time_different_group(lattice_list)


