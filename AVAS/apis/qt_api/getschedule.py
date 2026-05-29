#获取模拟的进度条
from PyQt5.QtWidgets import QWidget
import os
from dataprovision.datasetparameter import DatasetParameter
from utils.treatfile import check_file_update
from dataprovision.latticeparameter import LatticeParameter
from utils.iniconfig import IniConfig
from utils.tool import format_output
from utils.readfile import read_txt
from utils.treat_directory import list_files_in_directory
from dataprovision.par_out_ana import  ana_syn_particle
class GetSchedule():
    def __init__(self, item):
        self.project_path = item["projectPath"]
        self.ini_path = os.path.join(self.project_path, "InputFile", "ini.ini")
        self.lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')

    def get_mode(self):
        item = {"projectPath": self.project_path}

        ini_obj = IniConfig()
        ini_info = ini_obj.create_from_file(item)
        if ini_info["code"] == -1:
            raise Exception(ini_info["data"]['msg'])

        ini_info = ini_info["data"]["iniParams"]
        base_mode = ini_info["input"]["sim_type"]

        err_mode = ini_info["error"]["error_type"]
        match = ini_info["match"]

        match_mode = ''
        if match["cal_input_twiss"] == 1:
            match_mode = 'cal_input_twiss'
        elif match["match_with_twiss"] == 1:
            match_mode = 'match_with_twiss'

        res = {
            "base_mode": base_mode,
            "err_mode": err_mode,
            "match_mode": match_mode,
        }
        return res

    def get_base_mulp_schedule(self):
        dic = {"totalLength": "",
               "currentLength": "",
               "allStep": 1,
               "currentStep": 1,
               }

        lattice_obj = LatticeParameter(self.lattice_mulp_path)
        lattice_obj.get_parameter()
        total_length = lattice_obj.total_length
        total_length = round(total_length, 6)
        dic["totalLength"] = total_length
        self.total_length = total_length

        dataset_path = os.path.join(self.project_path, 'OutputFile', 'DataSet.txt')
        syn_par_path = os.path.join(self.project_path, 'OutputFile', 'synParticle.txt')

        if not os.path.exists(dataset_path):
            dic["currentLength"] = 0
            return dic
        else:
            # dataset_obj = DatasetParameter(dataset_path)
            # res = dataset_obj.get_parameter()
            syn_info = ana_syn_particle(syn_par_path)

            if syn_info is False:
                z = 0
            else:
                # z = dataset_obj.z[-1]
                # z = round(z, 6)
                z = round(syn_info[0], 6)
                if z > total_length:
                    z = total_length
                    dic["currentLength"] = total_length

            dic["currentLength"] = z
        return dic

    def get_error_schedule(self):
        dic = {"totalLength": "",
               "currentLength": "",
               "allStep": "",
               "currentStep": "",
               }

        lattice_obj = LatticeParameter(self.lattice_mulp_path)
        lattice_obj.get_parameter()
        total_length = lattice_obj.total_length
        total_length = round(total_length, 6)
        dic["totalLength"] = total_length
        self.total_length = total_length

        input_lines = read_txt(self.lattice_mulp_path, out='list')

        for i in input_lines:
            if i[0] == 'err_step':
                all_group = int(i[1])
                all_time = int(i[2])
                break

        all_step = all_group * all_time
        dic["allStep"] = all_step


        error_output_path = os.path.join(self.project_path, 'OutputFile', 'error_output')
        error_middle_path = os.path.join(self.project_path, 'OutputFile', 'error_middle')
        error_middle_output0_path = os.path.join(self.project_path, 'OutputFile', 'error_middle', 'output_0')

        all_files = list_files_in_directory(error_output_path,"mtime")

        #如果还没进行模拟
        if len(all_files) == 0:
            currentStep = 0

        #如果已经进行了模拟
        else:
            last_file = all_files[-1]
            now_group = int(last_file.split("/")[-1].split("_")[1])
            now_time = int(last_file.split("/")[-1].split("_")[2])
            if now_group == 0:
                currentStep = 1
            else:
                currentStep = (now_group - 1) * all_time + now_time + 1

        dic["currentStep"] = currentStep

        #如果全模拟完了
        if currentStep > all_step:
            dic["currentStep"] = all_step
            dic["currentLength"] = total_length
            return dic


        dataset_path = os.path.join(error_middle_output0_path, 'DataSet.txt')
        syn_par_path = os.path.join(error_middle_output0_path, 'synParticle.txt')

        if not os.path.exists(dataset_path):
            dic["currentLength"] = 0
            return dic
        else:
            # dataset_obj = DatasetParameter(dataset_path)
            # res = dataset_obj.get_parameter()
            syn_info = ana_syn_particle(syn_par_path)

            if syn_info is False:
                z = 0
            else:
                # z = dataset_obj.z[-1]
                # z = round(z, 6)
                z = round(syn_info[0], 6)
                if z > total_length:
                    z = total_length

            dic["currentLength"] = z


        return dic


    def main(self):
        mode = self.get_mode()
        base_mode = mode["base_mode"]
        err_mode = mode["err_mode"]
        match_mode = mode["match_mode"]



        kwargs = {}

        try:
            if err_mode == "" and match_mode == "":
                if base_mode == "mulp":
                    res = self.get_base_mulp_schedule()

            elif err_mode in ["stat", "dyn", "stat_dyn"]:
                res = self.get_error_schedule()
            one_ratio = res["currentLength"] / res["totalLength"]
            if one_ratio >= 0.98:
                res["currentLength"] = res["totalLength"]
        except Exception as e:
            code = 1
            msg = str(e)
            res = {"totalLength": self.total_length,
                   "currentLength": 0,
                   "allStep": 1,
                   "currentStep": 1,
                   }
            kwargs.update({'schedule': res})
            output = format_output(code, msg=msg, **kwargs)
            return output

            # res = {"totalLength": 1,

        kwargs.update({'schedule':res})
        output = format_output(**kwargs)
        # print(192, output)
        return output




if __name__ == '__main__':
    import time
    path = r"C:\Users\anxin\Desktop\test_schedule\cafe_avas_error"
    # path = r"C:\Users\shliu\Desktop\test_schedule\cafe_avas"

    item = {"projectPath": path}
    obj = GetSchedule(item)
    obj.main()
    # for i in range(1000):
    #     res = obj.main()
    #     print(res)
    #     time.sleep(1)
