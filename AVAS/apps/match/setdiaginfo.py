import os.path

import global_varible
from dataprovision.latticeparameter import LatticeParameter
from dataprovision.datasetparameter import DatasetParameter
from dataprovision.envdatasetparameter import EnvDatasetParameter
from utils.readfile import read_lattice_mulp_with_name
import copy
from utils.tool import judge_command_on_element
from utils.tool import add_element_end_index, judge_command_under_element, write_to_txt, calculate_mean, calculate_rms, add_to_txt
import numpy as np

class SetDiagInfo():
    def __init__(self, item):
        self.project_path = item.get("project_path")
        self.input_file = item.get("input_file")
        self.output_file = item.get("output_file")
        self.set_file_path = item.get("set_file_path")
        self.dataset_mode = item.get("dataset_mode")

    def generate_all_set_info(self, ):
        input_file = self.input_file
        output_file = self.output_file

        lattice_mulp_path = os.path.join(input_file, "lattice_mulp.txt")

        # dataset_path = os.path.join(output_file, "DataSet.txt")
        dataset_path = os.path.join(output_file, "output.dat")

        lattice_mulp_list, lattice_mulp_name = read_lattice_mulp_with_name(lattice_mulp_path)

        set_every_location = []
        # 读取新的lattice信息


        # 产生每一个set针对的位置
        lattice_obj = LatticeParameter()
        lattice_obj.get_parameter(lattice_mulp_list)


        lattice_copy = copy.deepcopy(lattice_mulp_list)
        #######################
        #增加元件的索引
        lattice_copy = add_element_end_index(lattice_copy)


        index = 0
        #为set添加set_0
        for i in lattice_copy:
            if i[0].startswith("set"):
                add_name = f'set_{index}'
                i.append(add_name)
                index += 1
#################################################
        #
        #
        # #为原件添加索引
        # index = 0
        # for i in lattice_copy:
        #     if i[0] in global_varible.all_element:
        #         add_name = f'element_{index}'
        #         i.append(add_name)
        #         index += 1

        # for i in lattice_copy:
        #     print(66, i)

        # 查找所有的set_command
        # 查找所有的shift
        #每一个set_command对应一个shift
        all_set_command = [] #所有的set命令
        all_shift_in_field_commnad = []  #所有的shift_in_field 命令

        for index, i in enumerate(lattice_copy):
            if i[0].startswith("set"):
                all_set_command.append(i)

                if lattice_copy[index-1][0] == "shift_in_field":
                    all_shift_in_field_commnad.append(lattice_copy[index-1])
                else:
                    all_shift_in_field_commnad.append([None])



        set_index = [int(i[-1].split("_")[-1]) for i in all_set_command]  #所有set的索引
        set_command_list = [i for i in all_set_command]  #所有set的命令

        # print(89, set_index)
        # print(90, set_command_list)


        set_dict = []
        for i in range(len(set_index)):
            dic = {}
            dic['set_command'] = set_command_list[i]
            dic['set_order'] = i

            #判断set命令在哪个个原件下面
            set_command_under_element = judge_command_under_element(lattice_copy, set_command_list[i])

            #找到原件对应的索引序列
            ele_index = lattice_obj.v_index_with_sup.index(set_command_under_element)

            dic['position'] = lattice_obj.v_end_with_sup[ele_index]


            if all_shift_in_field_commnad[i][0] is not None:
                #这里需要将束诊的单位从mm换成m
                dic["position"] = dic["position"] + float(all_shift_in_field_commnad[i][1])/1000
            set_dict.append(dic)

        # print(114, set_dict)
        # for i in set_dict:
        #     print(i)
        new_set_dict = self.get_info_from_dataset(set_dict, dataset_path)
        return new_set_dict

    def write_set_info_to_file(self, ):

        new_set_dict = self.generate_all_set_info()


        write_lis = []
        for i in new_set_dict:
            index = i["set_order"]
            NN = i["set_command"][1]

            position = round(i["position"], 4) * 1000 #mm


            if i["set_command"][0] == 'set_energy':
                set_type = "energy"
            elif i["set_command"][0] == 'set_position':
                set_type = "center"
            elif i["set_command"][0] == 'set_size':
                set_type = "rms_size"

            elif i["set_command"][0] == 'set_twiss':
                set_type = "twiss"

            t_lis = [
                f"set_command_{index} {NN}" +  "\n",
                f"set_type {set_type}" + "\n",
                f"position {position:.4f}" + "\n",
            ]

            for k, v in i["set_data"].items():
                v_str = " ".join([f"{x:.4f}" for x in v])

                t_lis.append(
                    f"{k} {v_str}\n"
                )

            write_lis.append(t_lis)
        write_to_txt(self.set_file_path, write_lis)



    def get_info_from_dataset(self, set_dict, dataset_path):
        if self.dataset_mode == "mulp":
            dataset_obj = DatasetParameter(dataset_path, self.project_path)
        elif self.dataset_mode == "env":
            dataset_obj = EnvDatasetParameter(dataset_path, self.project_path)

        dataset_obj.get_parameter()

        z_ = dataset_obj.z


        for i in set_dict:
            position = i['position']

            index_of_position = 0


            delta_z = np.abs(np.array(z_) - position)

            index_of_position = np.argmin(delta_z)


            dic= {}
            center_x = dataset_obj.x[index_of_position] * 1000  # mm
            center_y = dataset_obj.y[index_of_position] * 1000  # mm

            center_x1 = dataset_obj.x1[index_of_position] * 1000  # mrad
            center_y1 = dataset_obj.y1[index_of_position] * 1000  # mrad

            # rms_x = dataset_obj.rms_x[index_of_position] * 1000  # mm
            # rms_y = dataset_obj.rms_y[index_of_position] * 1000  # mm

            energy = dataset_obj.ek[index_of_position]  #MeV

            emit_x = dataset_obj.emit_x[index_of_position]
            emit_y = dataset_obj.emit_y[index_of_position]

            alpha_x = dataset_obj.alpha_x[index_of_position]
            beta_x = dataset_obj.beta_x[index_of_position]

            alpha_y = dataset_obj.alpha_y[index_of_position]
            beta_y = dataset_obj.beta_y[index_of_position]

            # current = dataset_obj.current[index_of_position]

            dic["center"] = [center_x, center_x1, center_y, center_y1] #改成x ,x', y, y'
            # dic["rms_size"] = [rms_x, rms_y]  #改成rms_x, rms_y, rms_z
            dic["energy"] = [energy]
            dic["emit_x"] = [ alpha_x, beta_x, emit_x]
            dic["emit_y"] = [alpha_y, beta_y, emit_y]


            # dic["current"] = [current]
            set_dict[i["set_order"]]["set_data"] = dic


        print(211, set_dict)

        # 211[{'set_command': ['set_twiss', '1', '-0.4466', '0.737702', '-0.33856', '0.6970', 'set_0'],
        #      'set_order': 0,
        #      'position': np.float64(4.348450002),
        #      'set_data': {'center': [0.007107598, -0.014512480000000001], 'energy': [2.0],
        #                   'emit_x': [-0.4166403, 0.7184489, 0.1000005],
        #                   'emit_y': [-0.3475868, 0.6912392, 0.1000003]}}]
        return set_dict

if __name__ == "__main__":

    project = r"F:\using\test_avas_qt\env_project_match"
    item = {
        "project_path": project,
        "input_file":  os.path.join(project, "InputFile"),
        "output_file": r"F:\using\test_avas_qt\env_project_match\OutputFile\match_adjust\output_0",
        "diag_file_path" : r"C:\Users\shliu\Desktop\test_lattice\OutputFile\Set_Diag_Datas_1_2.txt",
        "dataset_mode": "env"
    }
    obj = SetDiagInfo(item)
    res = obj.generate_all_set_info()


    # print("-" * 50)
    # print(res)
    # # #
    # # # diag_file_path = r"C:\Users\shliu\Desktop\test_lattice\Diag_Datas_1_2.txt"
    # # obj.write_diag_info_to_file()