from utils.readfile import read_txt
from utils.tool import write_to_txt, convert_dic2lis
from utils.tool import format_output
import os

class LatticeConfig():
    def __init__(self):
        self.lattice_parameter = 'start\ndrift 0.01 0.02 0\ndrift 0.01 0.02 0\nend\n'


    # def initialize_lattice(self):
    #     self.lattice_parameter = [
    #         ["start"],
    #         ["drift", 0.01, 0.02, 0],
    #         ["drift", 0.01, 0.02, 0],
    #         ["end"]
    #     ]

    def create_from_file(self, item):
        other_path = item.get("otherPath")
        sim_type = item.get("sim_type")
        if other_path is None:
            if sim_type == "env":
                path = os.path.join(item.get("projectPath"), "InputFile", "lattice_env.txt")
            else:
                path = os.path.join(item.get("projectPath"), "InputFile", "lattice_mulp.txt")
        else:
            path = other_path

        kwargs = {}
        try:
            # self.input_lis = read_txt(path, out='list', case_sensitive=False)
            # self.lattice_parameter = self.input_lis

            with open(path, 'r', encoding='utf-8') as file:
                file_contents = file.read()
            self.lattice_parameter = file_contents
        except Exception as e:
            code = -1
            msg = str(e)
            kwargs.update({'latticeParams': ''})
            output = format_output(code, msg=msg, **kwargs)
        kwargs.update({'latticeParams': self.lattice_parameter})
        output = format_output(**kwargs)
        return output

    def set_param(self, params):
        kwargs = {}
        try:
            self.lattice_parameter = params["latticeInfo"]
        except Exception as e:
            code = -1
            msg = str(e)
            kwargs.update({'latticeParams': ''})
            output = format_output(code, msg=msg, **kwargs)
        kwargs.update({'latticeParams': self.lattice_parameter })
        output = format_output(**kwargs)
        return output



    def add_element(self):
        return self.lattice_parameter
    def write_to_file(self, item):

        other_path = item.get("otherPath")
        sim_type = item.get("sim_type")
        if other_path is None:
            if sim_type == "env":
                path = os.path.join(item.get("projectPath"), "InputFile", "lattice_env.txt")
            else:
                path = os.path.join(item.get("projectPath"), "InputFile", "lattice_mulp.txt")
        else:
            path = other_path


        kwargs = {}

        try:
            with open(path, 'w', encoding='utf-8') as file:
                # 遍历嵌套列表的每个子列表
                file.write(self.lattice_parameter)

        except Exception as e:
            code = -1
            msg = str(e)
            kwargs.update({'latticeParams': ''})
            output = format_output(code, msg=msg, **kwargs)
        kwargs.update({'latticeParams': self.lattice_parameter })
        output = format_output(**kwargs)
        return output


if __name__ == "__main__":
    path = r"C:\Users\shliu\Desktop\AVAS_0.5\example"
    obj = LatticeConfig()
    item = {"projectPath": path,
            "sim_type": "mulp",
            }
    res = obj.create_from_file(item)
    print(res)