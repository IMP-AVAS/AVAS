import os.path

import global_varible
from dataprovision.latticeparameter import LatticeParameter
from dataprovision.datasetparameter import DatasetParameter
from utils.readfile import read_lattice_mulp_with_name
import copy
from utils.tool import judge_command_on_element
from utils.tool import add_element_end_index, write_to_txt, calculate_mean, calculate_rms, add_to_txt
class DiagInfo():
    def __init__(self, item):
        self.project_path = item.get("project_path")
        self.input_file = item.get("input_file")
        self.output_file = item.get("output_file")
        self.diag_file_path = item.get("diag_file_path")
    def generate_all_diag_info(self, ):
        input_file = self.input_file
        output_file = self.output_file

        lattice_mulp_path = os.path.join(input_file, "lattice_mulp.txt")

        dataset_path = os.path.join(output_file, "DataSet.txt")



        lattice_mulp_list, lattice_mulp_name = read_lattice_mulp_with_name(lattice_mulp_path)

        diag_every_location = []
        # 读取新的lattice信息


        # 产生每一个diag针对的位置
        lattice_obj = LatticeParameter()
        lattice_obj.get_parameter(lattice_mulp_list)


        lattice_copy = copy.deepcopy(lattice_mulp_list)

        lattice_copy = add_element_end_index(lattice_copy)




        # index = 0
        # #为diag添加diag_0
        # for i in lattice_copy:
        #     if i[0].startswith("diag"):
        #         add_name = f'diag_{index}'
        #         i.append(add_name)
        #         index += 1
        #
        # #为原件添加索引
        # index = 0
        # for i in lattice_copy:
        #     if i[0] in global_varible.long_element:
        #         add_name = f'element_{index}'
        #         i.append(add_name)
        #         index += 1

        # 查找所有的diag_command
        # 查找所有的shift
        all_diag_command = []
        all_shift_in_field_commnad = []
        all_diag_name = []

        for index, i in enumerate(lattice_copy):
            if i[0].startswith("diag"):
                all_diag_command.append(i)

                if lattice_copy[index-1][0] == "shift_in_field":
                    all_shift_in_field_commnad.append(lattice_copy[index-1])
                else:
                    all_shift_in_field_commnad.append([None])
                all_diag_name.append(lattice_mulp_name[index])


        diag_index = [int(i[-1].split("_")[-1]) for i in all_diag_command]
        diag_command_list = [i[:-1] for i in all_diag_command]

        diag_dict = []
        for i in range(len(diag_index)):
            dic = {}
            dic['diag_command'] = diag_command_list[i]
            dic['diag_order'] = i
            dic["element_index"] = diag_index[i]
            dic["diag_name"] = all_diag_name[i]
            if diag_index[i] == -1:
                dic['position'] = lattice_obj.total_length
            else:
                dic['position'] = lattice_obj.v_start[diag_index[i]]

            #考虑shift的影响
            if all_shift_in_field_commnad[i][0] is not None:
                #这里需要将束诊的单位从mm换成m
                dic["position"] = dic["position"] + float(all_shift_in_field_commnad[i][1]) /1000
            diag_dict.append(dic)

        # for i in diag_dict:
        #     print(i)
        new_diag_dict = self.get_info_from_dataset(diag_dict, dataset_path)
        return new_diag_dict

    def write_diag_info_to_file(self, ):

        new_diag_dict = self.generate_all_diag_info()


        write_lis = []
        for i in new_diag_dict:
            index = i["diag_order"]
            NN = i["diag_command"][1]
            element_index = i["element_index"]
            diag_name = i["diag_name"]
            position = round(i["position"], 4) * 1000 #mm
            center = i["diag_data"]["center"]    #mm
            rms_size = i["diag_data"]["rms_size"]  # mm
            energy = i["diag_data"]["energy"]  #MeV
            current = i["diag_data"]["current"] #A

            if i["diag_command"][0] == 'diag_energy':
                diag_type = "energy"
            elif i["diag_command"][0] == 'diag_position':
                diag_type = "center"
            elif i["diag_command"][0] == 'diag_size':
                diag_type = "rms_size"

            t_lis = [
                f"diag_command_{index} {NN} {element_index}" + "\n",
                f"diag_name {diag_name}" + "\n",
                f"diag_type {diag_type}" + "\n",
                f"position {position:.4f}" + "\n",
                f"center  {center[0]:.4f}  {center[1]:.4f}\n",
                f"rms_size {rms_size[0]:.4f} {rms_size[1]:.4f}" + "\n",
                f"energy {energy[0]:.4f}" + "\n",
                f"current {current[0]:.4f}" + "\n",

            ]

            write_lis.append(t_lis)
        write_to_txt(self.diag_file_path, write_lis)



    def get_info_from_dataset(self, diag_dict, dataset_path):
        dataset_obj = DatasetParameter(dataset_path, self.project_path)
        dataset_obj.get_parameter()

        z_ = dataset_obj.z


        for i in diag_dict:
            position = i['position']

            index_of_position = 0

            #找到束诊位置对应的
            for index, i1 in enumerate(z_):
                if i1 > position:
                    index_of_position = index - 1
                    break

            dic= {}
            center_x = dataset_obj.x[index_of_position] * 1000  # mm
            center_y = dataset_obj.y[index_of_position] * 1000  # mm

            rms_x = dataset_obj.rms_x[index_of_position] * 1000  # mm
            rms_y = dataset_obj.rms_y[index_of_position] * 1000  # mm

            energy = dataset_obj.ek[index_of_position]  #MeV
            current = dataset_obj.current[index_of_position]
            dic["center"] = [center_x, center_y]
            dic["rms_size"] = [rms_x, rms_y]
            dic["energy"] = [energy]
            dic["current"] = [current]
            diag_dict[i["diag_order"]]["diag_data"] = dic

        return diag_dict

if __name__ == "__main__":

    project = r"C:\Users\shliu\Desktop\test_lattice"
    item = {
        "project_path": project,
        "input_file": r"C:\Users\shliu\Desktop\test_lattice\InputFile",
        "output_file": r"C:\Users\shliu\Desktop\test_lattice\OutputFile",
        "diag_file_path" : r"C:\Users\shliu\Desktop\test_lattice\OutputFile\Diag_Datas_1_2.txt"
    }
    obj = DiagInfo(item)
    # obj.generate_all_diag_info(item)
    #
    # diag_file_path = r"C:\Users\shliu\Desktop\test_lattice\Diag_Datas_1_2.txt"
    obj.write_diag_info_to_file()