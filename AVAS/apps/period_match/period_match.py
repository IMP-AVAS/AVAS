#周期匹配
#该代码的功能是为把入口和每个周期的出口做失配度
#优化的是 alpha beta
import os
from apps.period_match.period_match_algorithm import PeriodMatchalgorithm
from apps.match_with_command.setdiaginfo import SetDiagInfo
from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name
import os
from utils.treat_directory import list_files_in_directory, copy_directory, delete_directory
import copy
import global_varible
from utils.tool import judge_command_on_element, judge_command_under_element, add_element_end_index, delete_element_end_index
from core.MultiParticle import MultiParticle
from utils.treatfile import copy_file_rename, copy_file
from utils.tool import write_to_txt, calculate_mean, calculate_rms, add_to_txt

#k 客户端client
class PeriodMatch():
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
        #这里的国际应该是
        #1. 修改入口的twiss参数
        #2. 读取每个周期出口的twiss参数
        #3. 计算入口twiss和出口twiss的失配度

        item = {
            "project_path": self.project_path,
            "field_path": self.field_path,
            "match_sim_type": self.match_sim_type,  # 匹配时使用的match_type
        }
        v = PeriodMatchalgorithm(item)

        opti_res_this_dict, diag_res_this = v.opti_one_time(lattice_mulp_list)
        return opti_res_this_dict, diag_res_this


    def run_use_corrected_result(self, opti_res_this,  error_lattice):



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