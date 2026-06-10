from utils.readfile import read_txt
from utils.exception import (TypeError, ValueRangeError, ValueChooseError, ListLengthError,
                             UnknownkeywordError, ValueConvertError, MisskeywordError)
from utils.tool import write_to_txt, convert_dic2lis
import copy
from utils.iniconfig import IniConfig
from utils.tool import format_output ,convert_to_othertype_dict
import os
class InputConfig():
    def __init__(self):
        self.input_parameter_keys = ["sim_type", "scmethod", "spacecharge", "steppercycle", "dumpperiodicity",
                                     "spacechargelong", "spacechargetype", "fieldSource", "device", "pchistogram_start", "pchistogram_grid",
                                     "longlimits_start", "longlimits_phase", "longlimits_energy", "boundary", "randomseed",
                                     "numofgrid_x", "numofgrid_y", "numofgrid_z", "meshrms_x", "meshrms_y", "meshrms_z",
                                     "adaptive_grid"
                                     ]


        self.input_parameter = {"sim_type": None, 'spacecharge': None, 'steppercycle': None, 'dumpperiodicity':None,
                                "spacechargelong": None, "spacechargetype": None, "pchistogram_start":None, "pchistogram_grid":None,
                                "longlimits_start": None, "longlimits_phase": None, "longlimits_energy": None,
                                "boundary": None, "randomseed": None,
                                "numofgrid_x": None, "numofgrid_y": None, "numofgrid_z": None, "meshrms_x": None, "meshrms_y": None, "meshrms_z": None,
                                "adaptive_grid":None
                                }

        self.int_keys = ["spacecharge", "steppercycle", "dumpperiodicity",
                         "spacechargelong", "spacechargetype", "pchistogram_start", "pchistogram_grid", "longlimits_start", "boundary", "randomseed",
                         "numofgrid_x", "numofgrid_y", "numofgrid_z",
                         ]
        self.float_keys = ["longlimits_phase", "longlimits_energy", "meshrms_x", "meshrms_y", "meshrms_z"]


        self.mulp_keys = ["sim_type", "scmethod", "spacecharge", "steppercycle", "dumpperiodicity", ]
        self.env_keys = ["spacechargelong", "spacechargetype"]


    def read_input_txt(self, path):
        #读取beam文件
        input_lis = read_txt(path, out='list', readdall=True, case_sensitive=True, )

        res = {}
        for i in input_lis:
            if len(i) == 2:
                res[i[0]] = i[1]
            else:
                res[i[0]] = i[1:]


        return res

    def create_from_file(self, item):
        other_path = item.get("otherPath")
        if other_path is None:
            path = os.path.join(item.get("projectPath"), "InputFile", "input.txt")
        else:
            path = other_path

        kwargs = {}

        original_dict = self.read_input_txt(path)
        if "pchistogram" in original_dict.keys():

            original_dict["pchistogram_start"] = original_dict["pchistogram"][0]
            original_dict["pchistogram_grid"] = original_dict["pchistogram"][1]
        if "longlimits" in original_dict.keys():
            original_dict["longlimits_start"] = original_dict["longlimits"][0]
            original_dict["longlimits_phase"] = original_dict["longlimits"][1]
            original_dict["longlimits_energy"] = original_dict["longlimits"][2]

        if "numofgrid" in original_dict.keys():
            original_dict["numofgrid_x"] = original_dict["numofgrid"][0]
            original_dict["numofgrid_y"] = original_dict["numofgrid"][1]
            original_dict["numofgrid_z"] = original_dict["numofgrid"][2]

        if "meshrms" in original_dict.keys():
            original_dict["meshrms_x"] = original_dict["meshrms"][0]
            original_dict["meshrms_y"] = original_dict["meshrms"][1]
            original_dict["meshrms_z"] = original_dict["meshrms"][2]

        # 验证是否存在未知元素
        # for k, v in original_dict.items():
        #     if k not in self.input_parameter_keys:
        #         raise UnknownkeywordError(message=None, key=k)


        # 如果不存在未知元素, 转换类型
        for k, v in original_dict.items():
            original_dict[k] = self.convert_v(k, v)

        for k, v in original_dict.items():
            self.input_parameter[k] = original_dict[k]



        kwargs.update({'inputParams': copy.deepcopy(self.input_parameter)})
        output = format_output(**kwargs)
        return output

    def set_param(self, **kwargs):
        for k, v in kwargs.items():
            if v == '':
                kwargs[k] = None
        kwargs1 = {}
        #验证类型
        self.validate_type(kwargs)

        for k, v in kwargs.items():
            self.input_parameter[k] = v


        kwargs1.update({'inputParams': copy.deepcopy(self.input_parameter)})
        output = format_output(**kwargs1)
        return output

    def write_to_file(self, item):
        other_path = item.get("otherPath")
        if other_path is None:
            path = os.path.join(item.get("projectPath"), "InputFile", "input.txt")
        else:
            path = other_path

        kwargs = {}

        v_dic = {}

        if self.input_parameter["sim_type"] == 'mulp':
            v_dic = copy.deepcopy(self.input_parameter)
            v_dic["pchistogram"] = [v_dic["pchistogram_start"], v_dic["pchistogram_grid"]]
            v_dic["longlimits"] = [v_dic["longlimits_start"], v_dic["longlimits_phase"], v_dic["longlimits_energy"]]

            #如果使用自适应性网格，就删除所有
            if v_dic["adaptive_grid"] == 1:
                v_dic["numofgrid"] = [v_dic["numofgrid_x"], v_dic["numofgrid_y"], v_dic["numofgrid_z"]]
                v_dic["meshrms"] = [v_dic["meshrms_x"], v_dic["meshrms_y"], v_dic["meshrms_z"]]

            need_delete = ["spacechargelong", "spacechargetype",
                           "pchistogram_start", "pchistogram_grid",
                           "longlimits_start", "longlimits_phase", "longlimits_energy",
                           "numofgrid_x", "numofgrid_y", "numofgrid_z",
                           "meshrms_x", "meshrms_y", "meshrms_z"
                           ]

            for i in need_delete:
                del v_dic[i]


        elif self.input_parameter["sim_type"] == 'env':

            v_dic["sim_type"] = self.input_parameter["sim_type"]
            v_dic["spacechargelong"] = self.input_parameter["spacechargelong"]
            v_dic["spacechargetype"] = self.input_parameter["spacechargetype"]


        v_lis = convert_dic2lis(v_dic)

        new_vlis = []
        for index, i in enumerate(v_lis):
            if None in i:
                pass
            else:
                new_vlis.append(i)

        write_to_txt(path, new_vlis)


        kwargs.update({'inputParams': copy.deepcopy(self.input_parameter)})
        output = format_output(**kwargs)
        return output


    def validate_type(self, param):
        #验证关键词的类型
        for k, v in param.items():
            if k == "scmethod" and v is not None:
                if v not in ["FFT", "SPICNIC"]:
                    raise ValueChooseError(k, ["FFT", "SPICNIC"], v)

            elif k == "spacecharge" and v is not None:
                if v not in [0, 1]:
                    raise ValueChooseError(k, [0, 1], v)
            elif k == "steppercycle" and v is not None:
                if not isinstance(v, int):
                    raise TypeError(k, int, type(v))
                if v <= 0:
                    raise ValueRangeError(k, ["1", "+inf"], v)

            elif k == "dumpperiodicity" and v is not None:
                if not isinstance(v, int):
                    raise TypeError(k, int, type(v))
                if v < 0:
                    raise ValueRangeError(k, ["0", "+inf"], v)

            elif k == "maxthreads" and v is not None:
                if not isinstance(v, int):
                    raise TypeError(k, int, type(v))

            # elif k not in self.input_parameter_keys:
            #     raise UnknownkeywordError(k)

        return True



    def convert_v(self, k, v):
        if k in self.int_keys:
            v = convert_to_othertype_dict(k, v, int)
            return v

        if k in self.float_keys:
            v = convert_to_othertype_dict(k, v, float)
            return v

        else:
            return v

    def validate_run(self, item):
        pass
        # res = self.create_from_file(item)
        #
        # input_params = res["data"]["inputParams"]
        #当所有输入符合
        # if input_params["sim_type"] == 'mulp':
        #     for k in self.mulp_keys:
        #         if input_params[k] is None:
        #             raise MisskeywordError(f"{k}")
        #
        # elif input_params["sim_type"] == 'env':
        #     for k in self.env_keys:
        #         if input_params[k] is None:
        #             raise MisskeywordError(f"{k}")

if __name__ == "__main__":
    import json

    path = r"C:\Users\shliu\Desktop\test429"
    item = {"projectPath": path}

    obj = InputConfig()
    res = obj.create_from_file(item)
    set_param = {'boundary ': 0}
    res = obj.set_param(**set_param)
    obj.write_to_file(item)




    # v = {k: v if v else " " for k, v in res["data"]["inputParams"].items()}
    # print(1, v)
    # # print(res)
    # # for k, v in res["data"]["inputParams"].items():
    # #     if v:
    # #         print(v)
    # v = json.dumps(v)
    # print(2, v)
    # set_param = {'scanphase': None}
    # res = obj.set_param(**set_param)
    # print(254, res)
    # obj.write_to_file(item)
