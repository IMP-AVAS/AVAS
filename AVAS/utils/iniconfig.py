

import configparser
import os
from utils.tool import format_output
import copy
from utils import exception as exce


class IniConfig():
    def __init__(self):
        self.ini_parameter = \
        {"project": {"project_path": "",
                     "fieldSource": "",
                     },
        "lattice":{"length": 0},
         "input": {"sim_type": "mulp", "device": "cpu"},
         "match": {"cal_input_twiss": 0, "match_with_twiss": 0, "use_initial_value": 0},
         "error": {"error_type": "", "seed": 0, "if_normal": 1},
         }

        self.str_keys = ["sim_type", "project_path", "fieldSource",  "error_type",  "device"]
    # def initialize_ini(self):


    def create_from_file(self, item):
        """
        读取 INI 文件并返回其内容作为一个字典。

        :return: 包含 INI 文件内容的字典
        """
        other_path = item.get("otherPath")
        if other_path is None:
            path = os.path.join(item.get("projectPath"), "InputFile", "ini.ini")
        else:
            path = other_path

        kwargs = {}
        config = configparser.ConfigParser()
        config.optionxform = str

        config.read(path, encoding='utf-8')  # 确保文件以正确的编码读取



        if not os.path.exists(path):
            print(f"文件路径 {path} 不存在。")
            return False

        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(path, encoding='utf-8')  # 确保文件以正确的编码读取

        for section in config.sections():
            for key, value in config.items(section):
                if key not in self.str_keys:
                    self.ini_parameter[section][key] = int(value)
                else:
                    self.ini_parameter[section][key] = value



        # print("read", self.ini_parameter)
        kwargs.update({'iniParams': copy.deepcopy(self.ini_parameter)})
        output = format_output(**kwargs)
        return output

    def set_param(self, **kwargs):
        """
        更新 INI 文件中的值。

        :param kwargs: 字典格式的键值对，用于更新 INI 文件
        """
        for k, v in kwargs.items():
            for k1, v1 in v.items():
                if v1 == None:
                    v[k1] = ""

        kwargs1 = {}

        try:
            for section, values in kwargs.items():
                if section in self.ini_parameter:
                    self.ini_parameter[section].update(values)
                else:
                    print(89, f"{section} 不存在。")

        except Exception as e:
            code = -1
            msg = str(e)
            kwargs1.update({'iniParams': {}})
            output = format_output(code, msg=msg, **kwargs1)
            return output

        kwargs1.update({'iniParams': copy.deepcopy(self.ini_parameter)})
        output = format_output(**kwargs1)
        return output

    def write_to_file(self, item):
        """
        将字典内容写入 INI 文件。

        :param ini_dict: 包含 INI 文件内容的字典
        :param output_path: 输出 INI 文件的路径
        """
        other_path = item.get("otherPath")
        if other_path is None:
            path = os.path.join(item.get("projectPath"), "InputFile", "ini.ini")
        else:
            path = other_path

        kwargs = {}
        try:
            config = configparser.ConfigParser()
            config.optionxform = str

            for section, section_data in self.ini_parameter.items():
                config[section] = section_data

            with open(path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)

        except Exception as e:
            code = -1
            msg = str(e)
            kwargs.update({'iniParams': {}})
            output = format_output(code, msg=msg, **kwargs)
            return output

        kwargs.update({'iniParams': copy.deepcopy(self.ini_parameter)})
        output = format_output(**kwargs)
        return output

    def validate_run(self, item):
        ini_info_base = self.create_from_file(item)
        if ini_info_base["code"] == -1:
            raise Exception(ini_info_base["data"]['msg'])
        ini_info = ini_info_base["data"]["iniParams"]
        base_mode = ini_info["input"]["sim_type"]

        match_mode = [
            ini_info["match"]["cal_input_twiss"],
            ini_info["match"]["match_with_twiss"],
            ini_info["match"]["use_initial_value"],
        ]

        err_mode = ini_info["error"]["error_type"]
        err_seed = ini_info["error"]["seed"]

        if base_mode not in ["mulp", "env"]:
            raise exce.ValueRangeError('sim type', ["mulp", "env"], base_mode)

        all_error_type = ["stat", "dyn", "stat_dyn", ""]
        if err_mode not in all_error_type:
            raise exce.ValueRangeError('error type', all_error_type, err_mode)

        return ini_info_base

# 示例用法

if __name__ == '__main__':
    item = {"projectPath": r"C:\Users\anxin\Desktop\test_schedule\cafe_avas"
    }
    cfg = IniConfig()
    cfg.validate_run(item)
    # file_path = r"C:\Users\shliu\Desktop\test1113\test1\InputFile\ini.ini" # 替换为你的 INI 文件路径
    # cfg = IniConfig()
    # res = cfg.creat_from_file(file_path)
    # print(res)
    # print(res)
    # # cfg.write_to_file(file_path)
    #
    # cfg.set_ini(
    #     project={"project_path": "C:/new/path"},
    #     lattice={"length": 100},
    #     match={"use_initial_value": 1}
    # )
    #
    #
    # print(cfg.ini_dict)
    # ini_dict = cfg.initialize()
    # cfg.write_ini(ini_dict)
    # item = {"projectPath": r"C:\Users\shliu\Desktop\test4212"
    # }
    # cfg = IniConfig()
    # # cfg.write_to_file(item)
    #
    # res = cfg.create_from_file(item)
    # # print(res)
    #
    # param = {'project': {'fieldSource': "thisProject", }}
    # res = cfg.set_param(**param)
    # print(res)
    # res = cfg.write_to_file(item)
    # print(res)