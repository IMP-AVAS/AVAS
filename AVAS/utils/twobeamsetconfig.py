#该文件的作用是对2beam_set文件进行操作和读取
from fontTools.cffLib import privateDictOperators

from utils.readfile import read_txt
from utils.tool import write_to_txt, convert_dic2lis
import copy
from utils.exception import (TypeError, ValueRangeError, ValueChooseError, ListLengthError,
                             UnknownkeywordError, ValueConvertError)
from utils.tool import format_output, convert_to_othertype_dict
import os
class Beam2Config():
    def __init__(self):
        self.g2bset_parameter = {
        "b1_phase_min": None,
        "b1_phase_max": None,

        "b2_phase_min": None,
        "b2_phase_max": None,

        "b1_phase_center": None,
        "b2_phase_center": None,

        "syn_p_charge": None,
        "syn_p_mass": None,
        "syn_p_phi": None,
        "syn_p_energy": None,
        }

        self.float_keys = ["b1_phase_min", "b1_phase_max", "b2_phase_min", "b2_phase_max",

        "b1_phase_center",
        "b2_phase_center",

        "syn_p_mass",
        "syn_p_phi",
        "syn_p_energy",]
        self.int_keys = ["syn_p_charge"]
        self.str_keys = []

    def create_from_file(self, item):
        other_path = item.get("otherPath")

        if other_path is None:
            path = os.path.join(item.get("projectPath"), "OutputFile", "generate_2beam", "2beam_set.txt")
        else:
            path = other_path

        kwargs = {}
        beam_lis = read_txt(path, out='list', case_sensitive=True)

        original_dict = {}
        for i in beam_lis:
            original_dict[i[0]] = i[1]

        for k, v in original_dict.items():
            original_dict[k] = self.convert_v(k, v)

        for k, v in original_dict.items():
            self.g2bset_parameter[k] = original_dict[k]



        kwargs.update({'g2bset_params': copy.deepcopy(self.g2bset_parameter)})
        output = format_output(**kwargs)
        return output

    def write_to_file(self, item):
        other_path = item.get("otherPath")

        if other_path is None:
            path = os.path.join(item.get("projectPath"), "OutputFile", "generate_2beam", "2beam_set.txt")
        else:
            path = other_path


        kwargs = {}

        v_dic = copy.deepcopy(self.g2bset_parameter)

        v_lis = convert_dic2lis(v_dic)

        new_vlis = []
        for index, i in enumerate(v_lis):
            if None in i:
                pass
            else:
                new_vlis.append(i)
        write_to_txt(path, new_vlis)

        kwargs.update({'g2bset_params': copy.deepcopy(self.g2bset_parameter)})
        output = format_output(**kwargs)
        return output


    def set_param(self,  **kwargs):
        for k, v in kwargs.items():
            if v == '':
                kwargs[k] = None
        kwargs1 = {}

        for k, v in kwargs.items():
            self.g2bset_parameter[k] = v

        kwargs1.update({'g2bset_params': copy.deepcopy(self.g2bset_parameter)})
        output = format_output(**kwargs1)
        return output

    def convert_v(self, k, v):
        if k in self.int_keys:
            v = convert_to_othertype_dict(k, v, int)
            return v

        elif k in self.float_keys:
            v = convert_to_othertype_dict(k, v, float)
            return v

        elif k in self.str_keys:
            v = convert_to_othertype_dict(k, v, str)
            return v

        else:
            return v




if __name__ == "__main__":
    item = {
        "projectPath": r"D:\using\test_avas_qt\test_beam"
    }

    obj = BeamConfig()
    res = obj.create_from_file(item)
    print(res)
    # para = {'numofcharge': None, 'particlerestmass': 939,}
    # res = obj.set_param(**para)
    # print(res)
    # obj.write_to_file(item)
