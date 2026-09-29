from apps.match.match_with_command_algorithm import MatchWithConmmandalgorithm
from apps.match.setdiaginfo import SetDiagInfo
from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name
import os
from utils.treat_directory import list_files_in_directory, copy_directory, delete_directory
import copy
import global_varible
from utils.tool import judge_command_on_element, judge_command_under_element, add_element_end_index, delete_element_end_index
from core.MultiParticle import MultiParticle
from utils.treatfile import copy_file_rename, copy_file
from utils.tool import write_to_txt, calculate_mean, calculate_rms, add_to_txt

class MatchWithCommand():
    def __init__(self, item):
        self.item = item

        self.project_path = item.get("project_path")
        self.field_path = item.get("field_path")
        self.match_sim_type = item.get("match_sim_type")

        self.lattice_path = os.path.join(self.project_path, "InputFile", "lattice.txt")
        self.lattice_mulp_path = os.path.join(self.project_path, "InputFile", "lattice_mulp.txt")
        self.output_file = os.path.join(self.project_path, "OutputFile")
        self.device = item.get("device") or "cpu"

    def run_one_time_opti(self, lattice_mulp_list):

        item = {
            "project_path": self.project_path,
            "field_path": self.field_path,
            "match_sim_type": self.match_sim_type,  # 匹配时使用的match_type
        }
        v = MatchWithConmmandalgorithm(item)

        opti_res_this_dict, diag_res_this = v.opti_one_time_different_group(lattice_mulp_list)
        return opti_res_this_dict, diag_res_this


    def run_use_corrected_result(self, opti_res_this,  error_lattice):

        # x =np.array(corrected_result).reshape(np.array(adjust_parameter_num).shape)
        error_lattice = copy.deepcopy(error_lattice)

        error_lattice = add_element_end_index(error_lattice)


        for k, v in opti_res_this.items():
            print(k, v)
            for com in error_lattice:
                if com[-1] == f'element_{k.split("_")[0]}':
                    com[int(k.split("_")[1])] = v
                    break

        # 删除error_lattice最后的编号
        error_lattice = delete_element_end_index(error_lattice)

        error_lattice = [i for i in error_lattice if i[0] in global_varible.err_write_command]
        with open(self.lattice_path, 'w') as f:
            for i in error_lattice:
                f.write(' '.join(map(str, i)) + '\n')

        self.run_multiparticle(self.project_path, 'OutputFile')

    def run_multiparticle(self, p_path, out_putfile_, if_error=1):
        item = {
            "project_path": p_path,
            "output_file": os.path.join(p_path, out_putfile_),
            "field_path": self.field_path,
            "device": self.device,
            "if_error": if_error,
            "env_par_mode": self.match_sim_type,
        }
        multiparticle_obj = MultiParticle(item)

        res = multiparticle_obj.run()
        return res

    def write_adjust_datas(self,  opti_res_this):
        #将优化的最优参数写入到文件
        adjust_datas_path = os.path.join(self.project_path, "OutputFile", f"last_best_optimisation.txt")
        #
        res = []
        for k, v in opti_res_this.items():
            t_lis = [f"element_match[{k}]"] + [round(v, 5)]
            res.append(t_lis)
        write_to_txt(adjust_datas_path, res)

    def run(self):
        lattice_mulp_list, _ = read_lattice_mulp_with_name(self.lattice_mulp_path)

        opti_res_this, loss_this = self.run_one_time_opti(lattice_mulp_list)

        print("42*", opti_res_this, loss_this)

        # opti_res_this = {'1_8': 0.4933612120807681, '1_7': 0.7579544029403025,
        #                  '5_8': 0.7614636313839422, '5_7': 0.25891675029296335}
        #



        # 使用优化后的结果运行一次
        self.run_use_corrected_result(opti_res_this, lattice_mulp_list)

        #将lattice文件复制到Outputfila中
        copy_file(self.lattice_path, self.output_file)

        # 将优化参数写入到文件
        self.write_adjust_datas(opti_res_this)

        # 将束诊参数写入到文件
        item = {
            "project_path": self.project_path,
            "input_file": os.path.join(self.project_path, "InputFile"),
            "output_file": os.path.join(self.project_path, "OutputFile"),
            "set_file_path": os.path.join(self.project_path, "OutputFile", f"set_datas.txt"),
            "dataset_mode": "env",
        }
        obj = SetDiagInfo(item)
        obj.write_set_info_to_file()

        # 产生优化之后的lattice


if __name__ == '__main__':
    item = \
        {
            "project_path": r"F:\using\test_avas_qt\env_project_match",
            "field_path": r"F:\using\test_avas_qt\env_project_match\FieldFile",
            "match_sim_type": "env", #匹配时使用的match_type
        }
    obj = MatchWithCommand(item)

    obj.run()
