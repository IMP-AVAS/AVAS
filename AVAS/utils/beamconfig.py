from fontTools.cffLib import privateDictOperators

from utils.readfile import read_txt
from utils.tool import write_to_txt, convert_dic2lis
import copy
from utils.exception import (TypeError, ValueRangeError, ValueChooseError, ListLengthError,
                             UnknownkeywordError, ValueConvertError)
from utils.tool import format_output, convert_to_othertype_dict
import os
class BeamConfig():
    def __init__(self):
        self.beam_parameter = {}

        self.beam_parameter_keys = ['readparticledistribution', 'numofcharge', 'particlerestmass',
                                    'current', 'particlenumber', 'frequency',
                                    'kneticenergy', 'alpha_x', 'beta_x', 'emit_x',
                                    "alpha_y", "beta_y", "emit_y",
                                    "alpha_z", "beta_z", "emit_z",
                                    'distribution_x', 'distribution_y', "use_dst", "beamtype"]


        self.str_keys = ['readparticledistribution', 'distribution_x', "distribution_y",
                         "beamtype"]

        self.int_keys = ['numofcharge', 'particlenumber', "use_dst"]
        self.float_keys = ['particlerestmass', 'current', 'frequency', 'kneticenergy',
                            "alpha_x", "beta_x", "emit_x",
                           "alpha_y", "beta_y", "emit_y",
                           "alpha_z", "beta_z", "emit_z",
                           ]



        self.beam_parameter = {'readparticledistribution': None,  'numofcharge': None,
                               'particlerestmass': None, 'current': None,
                       'particlenumber': None, 'frequency': None, 'kneticenergy': None,
                        "alpha_x": None, "beta_x": None, "emit_x": None,
                        "alpha_y": None, "beta_y": None, "emit_y": None,
                        "alpha_z": None, "beta_z": None, "emit_z": None,
                        "distribution_x": None, "distribution_y": None, "use_dst":None,
                        "beamtype": None
                }



    def read_beam_txt(self, path):
        #读取beam文件
        beam_lis = read_txt(path, out='list', case_sensitive=True)

        res = {}
        for i in beam_lis:
            if len(i) == 2:
                res[i[0]] = i[1]
            else:
                res[i[0]] = i[1:]

        return res


    def create_from_file(self, item):
        other_path = item.get("otherPath")
        if other_path is None:
            path = os.path.join(item.get("projectPath"), "InputFile", "beam.txt")
        else:
            path = other_path


        kwargs = {}


        original_dict = self.read_beam_txt(path)


        if "twissx" in original_dict.keys():
            original_dict["alpha_x"] = original_dict["twissx"][0]
            original_dict["beta_x"] = original_dict["twissx"][1]
            original_dict["emit_x"] = original_dict["twissx"][2]
            del original_dict["twissx"]
        if "twissy" in original_dict.keys():
            original_dict["alpha_y"] = original_dict["twissy"][0]
            original_dict["beta_y"] = original_dict["twissy"][1]
            original_dict["emit_y"] = original_dict["twissy"][2]
            del original_dict["twissy"]
        if "twissz" in original_dict.keys():
            original_dict["alpha_z"] = original_dict["twissz"][0]
            original_dict["beta_z"] = original_dict["twissz"][1]
            original_dict["emit_z"] = original_dict["twissz"][2]
            del original_dict["twissz"]
        if "distribution" in original_dict.keys():
            original_dict["distribution_x"] = original_dict["distribution"][0]
            original_dict["distribution_y"] = original_dict["distribution"][1]
            del original_dict["distribution"]
        if original_dict.get("readparticledistribution") == "unknown":
            original_dict["readparticledistribution"] = None

        # #验证是否存在未知元素
        # for k, v in original_dict.items():
        #     if k not in self.beam_parameter_keys:
        #         raise UnknownkeywordError(message=None, key=k)

        #如果不存在未知元素, 转换类型
        for k, v in original_dict.items():
            original_dict[k] = self.convert_v(k, v)

        #赋值给self.beam_parameter
        # if self.validate_type(original_dict):
        for k, v in original_dict.items():
            self.beam_parameter[k] = original_dict[k]


        # print("read", self.beam_parameter)
        kwargs.update({'beamParams': copy.deepcopy(self.beam_parameter)})
        output = format_output(**kwargs)
        return output

    def write_to_file(self, item):

        other_path = item.get("otherPath")

        use_dst = self.beam_parameter.get("use_dst")

        if other_path is None:
            path = os.path.join(item.get("projectPath"), "InputFile", "beam.txt")
        else:
            path = other_path

        kwargs = {}

        v_dic = copy.deepcopy(self.beam_parameter)
        if use_dst == 1:
            v_dic['readparticledistribution'] = self.beam_parameter['readparticledistribution']
        elif use_dst == 0:
            v_dic['readparticledistribution'] = "unknown"

        v_dic['numofcharge'] = self.beam_parameter['numofcharge']

        v_dic["twissx"] = [self.beam_parameter["alpha_x"], self.beam_parameter["beta_x"], self.beam_parameter["emit_x"]]
        v_dic["twissy"] = [self.beam_parameter["alpha_y"], self.beam_parameter["beta_y"], self.beam_parameter["emit_y"]]
        v_dic["twissz"] = [self.beam_parameter["alpha_z"], self.beam_parameter["beta_z"], self.beam_parameter["emit_z"]]
        v_dic["distribution"] = [self.beam_parameter["distribution_x"], self.beam_parameter["distribution_y"]]

        v_key = ["alpha_x", "beta_x", "emit_x",
                       "alpha_y", "beta_y", "emit_y",
                       "alpha_z", "beta_z", "emit_z", "distribution_x", "distribution_y"]
        for i in v_key:
            del v_dic[i]

        v_lis = convert_dic2lis(v_dic)

        new_vlis = []
        for index, i in enumerate(v_lis):
            if None in i:
                pass
            else:
                new_vlis.append(i)
            # v_lis[index] = ["" if v is None else v for v in i]
        write_to_txt(path, new_vlis)


        kwargs.update({'beamParams': copy.deepcopy(self.beam_parameter)})
        output = format_output(**kwargs)
        return output

    def set_param(self,  **kwargs):
        for k, v in kwargs.items():
            if v == '':
                kwargs[k] = None
        kwargs1 = {}

        self.validate_type(kwargs)
        for k, v in kwargs.items():
            self.beam_parameter[k] = v



        kwargs1.update({'beamParams': copy.deepcopy(self.beam_parameter)})
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

    def validate_type(self, param):
        #验证关键词的类型
        for k, v in param.items():
            if k == "readparticledistribution" and v is not None:
                if not isinstance(v, str):
                    raise TypeError(k, str, type(v))
            elif k in self.int_keys and v is not None:
                if not isinstance(v, int):
                    raise TypeError(k, int, type(v))
            elif k in self.float_keys and v is not None:
                if not isinstance(v, (int, float)):
                    raise TypeError(k, float, type(v))
            elif (k == "distribution_x" or k == "distribution_y") and v is not None:
                if v not in ["WB", "PB", "GS", "KV", "undefined"]:
                    raise ValueChooseError(k, ["WB", "PB", "GS", "KV", "undefined"], v)

            # elif k not in self.beam_parameter_keys:
            #     raise UnknownkeywordError(k)

        return True

    def validate_run(self, item):
        pass
        # res = self.create_from_file(item)
        # if res["code"] == -1:
        #     raise Exception(res["data"]["msg"])
        # beam_params = res["data"]["beamParams"]
        # #当所有输入符合
        #
        # # for k in self.beam_parameter_keys:
        # #     if beam_params[k] is None:
        # #         raise Exception(f"missing parameter {k}")
        #

        # self.with_dst_keys = ['readparticledistribution', 'numofcharge']
        #
        # self.no_dst_keys = ['numofcharge', 'particlerestmass',
        #                     'current', 'particlenumber', 'frequency',
        #                     'kneticenergy', 'alpha_x', 'beta_x', 'emit_x',
        #                     'distribution_x', 'distribution_y', "beamtype"]
        # #当所有输入符合
        # use_dst = self.beam_parameter.get("use_dst")
        # if use_dst == 1:
        #     for k in self.with_dst_keys:
        #         if beam_params[k] is None:
        #             raise Exception(f"missing parameter {k}")
        #
        # else:
        #     for k in self.no_dst_keys:
        #         if beam_params[k] is None:
        #             raise Exception(f"missing parameter {k}")


if __name__ == "__main__":
    item = {
        "projectPath": r"C:\Users\wangh\Desktop\test_page_2b"
    }

    obj = BeamConfig()
    res = obj.create_from_file(item)
    print(res)
    # para = {'numofcharge': None, 'particlerestmass': 939,}
    # res = obj.set_param(**para)
    # print(res)
    # obj.write_to_file(item)
