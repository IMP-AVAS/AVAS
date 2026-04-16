
# 工作流程：
#    generate_adjust_parameter：根据lattice_mulp记录需要adjust的元件及参数位置，这里的位置是整个
#    lattice_mulp中所有的内容转换成list

#    get_goal：修改参数，添加end，然后写入lattice
#    根据诊断命令，计算loss
import sys
from scipy.optimize import minimize

import numpy as np

from dataprovision.latticeparameter import LatticeParameter
from dataprovision.datasetparameter import DatasetParameter

from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name
from utils.treatlist import flatten_list, list_one_two
from utils.treatfile import copy_file, split_file
from utils.tool import write_to_txt, calculate_mean, calculate_rms, add_to_txt

import os

import random
from core.MultiParticle import MultiParticle
from utils.treat_directory import list_files_in_directory, copy_directory, delete_directory
import multiprocessing

import global_varible
import copy

from utils.tolattice import write_mulp_to_lattice_only_sim, write_mulp_to_lattice_only_sim2

from apps.err_adjust import Adjust_Error
from utils.exception import MissingcommandError
from utils.tool import judge_command_on_element, add_element_end_index, delete_element_end_index
from apps.diaginfo import DiagInfo

from aftertreat.dataanalysis.extodensity import ExtoDensity, MergeDensityData
class Error():
    """
    该类为误差分析
    """
    def __init__(self, item):

        project_path = item.get("project_path")
        seed = item.get("seed")
        if_normal = item.get("if_normal")
        field_path = item.get("field_path")
        if_generate_density_file = item.get("if_generate_density_file")
        self.device = item.get("device")
        self.item = item

        random.seed(seed)

        self.if_generate_density_file = if_generate_density_file

        self.field_path = field_path
        self.project_path = project_path
        self.if_normal = if_normal
        self.lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')
        self.lattice_path = os.path.join(self.project_path, 'InputFile', 'lattice.txt')

        self.input_path = os.path.join(self.project_path, 'InputFile')
        self.output_path = os.path.join(self.project_path, 'OutputFile')

        self.error_middle_path = os.path.join(self.project_path, 'OutputFile', 'error_middle')
        self.error_middle_output0_path = os.path.join(self.project_path, 'OutputFile', 'error_middle', 'output_0')
        self.error_output_path = os.path.join(self.project_path, 'OutputFile', 'error_output')
        self.normal_out_path = os.path.join(self.error_output_path, 'output_0_0')

        self.errors_par_tot_path = os.path.join(self.output_path, "errors_par_tot.txt")
        self.errors_par_path = os.path.join(self.output_path, "errors_par.txt")

        self.loss = []
        self.opti_res = []


        self.all_group = 1
        self.all_time = 1
        self.lattice_mulp_list = []
        self.errors_par_tot_list_first = []
        self.err_beam_stat_on = [0] * 13
        self.err_quad_stat_on = [0, 0, 0, 0, 0, 0, 0]
        self.err_cav_stat_on = [0, 0, 0, 0, 0, 0, 0]

        self.err_beam_dyn_on = [0] * 13
        self.err_quad_dyn_on = [0, 0, 0, 0, 0, 0, 0]
        self.err_cav_dyn_on = [0, 0, 0, 0, 0, 0, 0]
        self.err_step_command = []
        # self.err_beam_stat_on = []
        # self.err_quad_stat_on = []
        # self.err_cav_stat_on = []
        #
        # self.err_beam_dyn_on = []
        # self.err_quad_dyn_on = []
        # self.err_cav_dyn_on = []


        self.decimal = 5  # 小数点保留多少位
        self.result_queue = multiprocessing.Queue()

        if os.path.exists(self.error_middle_path):
            delete_directory(self.error_middle_path)
        os.makedirs(self.error_middle_path)


        if os.path.exists(self.error_output_path):
            delete_directory(self.error_output_path)
        os.makedirs(self.error_output_path)

        self.err_adjust_path = os.path.join(self.project_path, "OutputFile", "error_adjust")
        if os.path.exists(self.err_adjust_path):
            delete_directory(self.err_adjust_path)
        os.makedirs(self.err_adjust_path)

        v = LatticeParameter(self.lattice_mulp_path)
        v.get_parameter()
        self.lattice_total_length = v.total_length

    def delete_element_end_index(self, error_lattice):
        error_lattice_copy = copy.deepcopy(error_lattice)
        for i in error_lattice_copy:
            if i[0] in global_varible.all_element:
                i.pop()
        return error_lattice_copy

    def get_group_time(self):
        """
        得到group和time
        :return:
        """


        input_lines, _  = read_lattice_mulp_with_name(self.lattice_mulp_path)

        for i in input_lines:
            if i[0] == 'err_step':

                if len(i) != 3:
                    raise Exception("The err_step command miss parameters.")
                if int(i[1]) <= 0:
                    raise Exception("The group parameter of the err_step command must be a positive integer.")
                if int(i[2]) <= 0:
                    raise Exception("The time parameter of the err_step command must be a positive integer.")
                self.err_step_command = i

                self.all_group = int(i[1])
                self.all_time = int(i[2])

            elif i[0] == 'err_beam_stat_on':
                for j in range(1, len(i)):
                    self.err_beam_stat_on[j-1] = int(i[j])

            elif i[0] == 'err_quad_stat_on':
                for j in range(1, len(i)):
                    self.err_quad_stat_on[j-1] = int(i[j])

            elif i[0] == 'err_cav_stat_on':
                for j in range(1, len(i)):
                    self.err_cav_stat_on[j-1] = int(i[j])

            elif i[0] == 'err_beam_dyn_on':
                for j in range(1, len(i)):
                    self.err_beam_dyn_on[j-1] = int(i[j])

            elif i[0] == 'err_quad_dyn_on':
                for j in range(1, len(i)):
                    self.err_quad_dyn_on[j-1] = int(i[j])

            elif i[0] == 'err_cav_dyn_on':

                for j in range(1, len(i)):
                    self.err_cav_dyn_on[j-1] = int(i[j])

    def increase_error(self, input_lines):
        """
        向叠加场中添加误差, 将一个误差命令添加到所有的元件上
        """
        N = -1
        command = []
        error_use_index = 0

        res = copy.deepcopy(input_lines)

        for i in range(len(input_lines)):
            if input_lines[i][0] in global_varible.error_elemment_command and N == -1 and input_lines[i][-1] is False:
                N = int(input_lines[i][1])
                command = input_lines[i]
                command[1] = 1
                error_use_index = i

            elif N == -1:
                continue

            elif N == 0 or input_lines[i][0] == 'end':
                res[error_use_index][-1] = True

                err_judge = []
                for i in res:
                    if i[0] in global_varible.error_elemment_command:
                        err_judge.append(i[-1])

                # 当全部都是True
                if all(err_judge):
                    return res

                else:

                    return self.increase_error(res)


            elif input_lines[i][0] in global_varible.mulpud_element and N > 0:
                # 在叠加场添加磁场原件误差
                if input_lines[i][0] == 'field' and input_lines[i][4] == '3':
                    if command[0] in (
                            global_varible.error_elemment_command_quad + global_varible.error_elemment_command_quad_cpl):
                        res[i].append(command)

                # 在叠加场添加高频腔原件误差
                if input_lines[i][0] == 'field' and input_lines[i][4] == '1':
                    if command[0] in (global_varible.error_elemment_command_cav + global_varible.error_elemment_command_cav_cpl):
                        res[i].append(command)

                N -= 1

    def get_dimension(self, lst):
        if not isinstance(lst, list):
            return 0  # 不是列表，维度为 0
        else:
            return 1 + max(self.get_dimension(item) for item in lst)


    def set_error_to_lattice(self, lattice):
        # for i in lattice:
        #     print(i)
        lattice = copy.deepcopy(lattice)

        lattice = add_element_end_index(lattice)


        #为每个误差命令添加一个编号
        err_command = []
        index = 0
        for i in lattice:
            if i[0] in global_varible.error_elemment_command:
                i.append(f"err_{index}")
                index += 1
                err_command.append(i)

        # for i in err_command:
        #     print(i)
        # breakpoint()
        #每一个误差命令的作用范围
        err_command_action_scope = []
        for i in err_command:
            #误差命令的索引
            err_index = lattice.index(i)
            #作用元件数量
            N = int(lattice[err_index][1])
            #判断误差命令在哪个元件上
            command_on_element = judge_command_on_element(lattice, i)
            if command_on_element is not None:
                err_command_action_scope.append(list(range(command_on_element, command_on_element + N)))
            else:
                err_command_action_scope.append([])

        # for i in err_command:
        #     print(i)


        #根据命令和作用域向lattice插入
        for i in range(len(err_command)):
            if err_command[i][0] in global_varible.error_elemment_command_quad:

                for j in lattice:
                    if j[0] == 'field' and int(float(j[4])) == 3:
                        if int(j[-1].split("_")[-1]) in err_command_action_scope[i]:
                            j.insert(-1, err_command[i])
                    elif j[0] == "quad":
                        if int(j[-1].split("_")[-1]) in err_command_action_scope[i]:
                            j.insert(-1, err_command[i])

            elif err_command[i][0] in global_varible.error_elemment_command_cav:
                for j in lattice:
                    if j[0] == 'field' and int(float(j[4])) == 1:
                        if int(j[-1].split("_")[-1]) in err_command_action_scope[i]:
                            j.insert(-1, err_command[i])

        lattice = self.delete_element_end_index(lattice)

        return lattice


    def generate_lattice_mulp_list(self, group):

        input_lines, _ = read_lattice_mulp_with_name(self.lattice_mulp_path)

        #为cpl生成误差，如果是cpl，直接生成对应的误差
        input_lines_copy = self.generate_error(input_lines, group, 'cpl')

        #将误差命令添加到每个元件上，加到每个元件的结尾
        lattice = self.set_error_to_lattice(input_lines_copy)
        # for i in lattice:
        #     print(i)
        # print("----------------------------")


        #去掉误差命令
        lattice = [i for i in lattice if i[0] not in global_varible.error_elemment_command]

        res_treat = []

        error_commands_map = {
            'err_quad_stat': ['err_quad_ncpl_stat', 'err_quad_cpl_stat'],
            'err_quad_dyn': ['err_quad_ncpl_dyn', 'err_quad_cpl_dyn'],
            'err_cav_stat': ['err_cav_ncpl_stat', 'err_cav_cpl_stat'],
            'err_cav_dyn': ['err_cav_ncpl_dyn', 'err_cav_cpl_dyn']
        }
        #为每个误差添加唯一的误差，动态和静态，防止出现动态和静态同时存在
        for i in lattice:
            if self.get_dimension(i) == 1:
                res_treat.append(i)

            elif self.get_dimension(i) != 1:
                lis = []
                err_command_exist = []

                i_copy = copy.deepcopy(i)

                for j in i[::-1]:
                    if isinstance(j, list) and j[0] not in err_command_exist:
                        lis.append(j)

                        if j[0] in error_commands_map["err_quad_stat"]:
                            err_command_exist.extend(error_commands_map["err_quad_stat"])

                        elif j[0] in error_commands_map["err_quad_dyn"]:
                            err_command_exist.extend(error_commands_map["err_quad_dyn"])

                        elif j[0] in error_commands_map["err_cav_stat"]:
                            err_command_exist.extend(error_commands_map["err_cav_stat"])

                        elif j[0] in error_commands_map["err_cav_dyn"]:
                            err_command_exist.extend(error_commands_map["err_cav_dyn"])

                        # if j[0] in ['err_quad_ncpl_stat', 'err_quad_cpl_stat']:
                        #     err_command_exist.append('err_quad_ncpl_stat')
                        #     err_command_exist.append('err_quad_cpl_stat')
                        #
                        # elif j[0] in ['err_cav_ncpl_stat', 'err_cav_cpl_stat']:
                        #     err_command_exist.append('err_cav_ncpl_stat')
                        #     err_command_exist.append('err_cav_cpl_stat')
                        #
                        # elif j[0] in ['err_quad_ncpl_dyn', 'err_quad_cpl_dyn']:
                        #     err_command_exist.append('err_quad_ncpl_dyn')
                        #     err_command_exist.append('err_quad_cpl_dyn')
                        #
                        # elif j[0] in ['err_cav_ncpl_dyn', 'err_cav_cpl_dyn']:
                        #     err_command_exist.append('err_cav_ncpl_dyn')
                        #     err_command_exist.append('err_cav_cpl_dyn')

                        # err_command_exist.append(j[0])
                        i_copy.pop()
                    # 如果已经出现过
                    elif isinstance(j, list) and j[0] in err_command_exist:
                        i_copy.pop()

                    else:
                        lis.append(i_copy)
                        break

                for k in lis:
                    k1 = copy.deepcopy(k)
                    res_treat.append(k1)

        # for i in res_treat:
        #     print(i)
        # breakpoint()

        #删除误差后面的编号
        for i in res_treat:
            if i[0] in global_varible.error_elemment_command:
                i.pop()


        #对ncpl误差进行生成
        res_treat = self.generate_error(res_treat, group, 'ncpl')

        #将所有的cpl变成ncpl
        for i in res_treat:
            if i[0] == "err_cav_cpl_dyn":
                i[0] = "err_cav_ncpl_dyn"

            elif i[0] == "err_cav_cpl_stat":
                i[0] = "err_cav_ncpl_stat"

            elif i[0] == "err_quad_cpl_dyn":
                i[0] = "err_quad_ncpl_dyn"

            elif i[0] == "err_quad_cpl_stat":
                i[0] = "err_quad_ncpl_stat"

        #规定每个误差命令只作用于一个原件
        for i in res_treat:
            if i[0] in global_varible.error_elemment_command:
                i[1] = 1

        # for i in res_treat:
        #     print(i)

        # index = 0
        # for i in res_treat:
        #     if i[0] in global_varible.all_element:
        #         add_name = f'element_{index}'
        #         i.append(add_name)
        #         index += 1
        res_treat = add_element_end_index(res_treat)
        # for i in res_treat:
        #     print(i)
        # breakpoint()
        self.lattice_mulp_list = res_treat
        # for i in self.lattice_mulp_list:
        #     print(i)

        # for i in self.lattice_mulp_list:
        #     print(i)
        #返回值后面带了一个元件索引
        return self.lattice_mulp_list


        #
        # sys.exit(0)

    def generate_error_base(self, input, group):
        """
        根据每一个error命令产生对应的error
        :param input:
        :param group:
        :return:
        """
        input = copy.deepcopy(input)


        target = None
        if input[0] in global_varible.error_elemment_command:
            for i in range(3, len(input)):
                input[i] = float(input[i])

            input = input + [0] * (10 - len(input))
            target = input

            if int(input[2]) == 0:
                target = input

            elif int(input[2]) == 1:
                for i in range(3, len(input) - 1):
                    dx = float(input[i]) / self.all_group
                    target[i] = round(random.uniform(-1 * dx * (group), dx * (group)), self.decimal)
                target[2] = 0

            elif int(input[2]) == 2:
                for i in range(3, len(input) - 1):
                    dx = float(input[i]) / self.all_group
                    target[i] = round(random.gauss(0, dx * (group)), self.decimal)
                target[2] = 0

            elif int(input[2]) == -1:
                for i in range(3, len(input) - 1):
                    dx = float(input[i]) / self.all_group
                    target[i] = dx * (group)
                target[2] = 0

        if input[0] in global_varible.error_beam_command:
            for i in range(2, len(input)):
                input[i] = float(input[i])
            input = input + [0] * (15 - len(input))

            target = input

            if int(input[1]) == 0:
                target = input

            elif int(input[1]) == 1:
                for i in range(2, len(input)):
                    dx = float(input[i]) / self.all_group
                    target[i] = round(random.uniform(-1 * dx * group, dx * group), self.decimal)
                target[1] = 0


            elif int(input[1]) == 2:
                for i in range(2, len(input)):
                    dx = float(input[i]) / self.all_group
                    target[i] = round(random.gauss(0, dx * group), self.decimal)
                target[1] = 0

            elif int(input[1]) == -1:
                for i in range(2, len(input)):
                    dx = float(input[i]) / self.all_group
                    target[i] = dx * (group + 1)
                target[1] = 0

        if input[0] == 'err_quad_ncpl_stat' or input[0] =='err_quad_cpl_stat':
            for i in range(len(self.err_quad_stat_on)):
                if int(self.err_quad_stat_on[i]) == 0:
                    target[i + 3] = 0

        elif input[0] == 'err_quad_ncpl_dyn' or input[0] =='err_quad_cpl_dyn':
            for i in range(len(self.err_quad_dyn_on)):
                if int(self.err_quad_dyn_on[i]) == 0:
                    target[i + 3] = 0

        elif input[0] == 'err_cav_ncpl_stat' or input[0] =='err_cav_cpl_stat':
            for i in range(len(self.err_cav_stat_on)):
                if int(self.err_cav_stat_on[i]) == 0:
                    target[i + 3] = 0


        elif input[0] == 'err_cav_ncpl_dyn' or input[0] =='err_cav_cpl_dyn':
            for i in range(len(self.err_cav_dyn_on)):
                if int(self.err_cav_dyn_on[i]) == 0:
                    target[i + 3] = 0

        elif input[0] == 'err_beam_stat':
            for i in range(len(self.err_beam_stat_on)):
                if int(self.err_beam_stat_on[i]) == 0:
                    target[i + 2] = 0

        elif input[0] == 'err_beam_dyn':

            for i in range(len(self.err_beam_dyn_on)):
                if int(self.err_beam_dyn_on[i]) == 0:
                    target[i + 2] = 0

        return target

    def generate_error(self, input_lines, group, kind):
        """
        将lattice_mulp写进新的lattice，将误差变成AVAS后端需要的情况
        :param group:
        :return:
        """

        input_lines = copy.deepcopy(input_lines)

        #产生ncpl的误差
        if kind == 'ncpl':
            for i in range(len(input_lines)):
                if len(input_lines[i]) == 0:
                    continue

                elif input_lines[i][0] == 'err_step':
                    input_lines[i] = ['err_step', '1', '1']


                elif input_lines[i][0] in global_varible.error_elemment_command_ncpl or \
                        input_lines[i][0] in global_varible.error_beam_command:
                    input_lines[i] = self.generate_error_base(input_lines[i], group)

        #产生cpl的误差
        elif kind == 'cpl':
            for i in range(len(input_lines)):
                if len(input_lines[i]) == 0:
                    continue

                elif input_lines[i][0] in global_varible.error_elemment_command_stat_cpl or \
                        input_lines[i][0] in global_varible.error_elemment_command_dyn_cpl:
                    input_lines[i] = self.generate_error_base(input_lines[i], group)

        return input_lines


    def run_multiparticle(self, p_path, out_putfile_):
        item = {
            "project_path": p_path,
            "output_file": os.path.join(p_path, out_putfile_),
            "field_path": self.field_path,
            "errorlog_path": os.path.join(p_path, r'OutputFile/error_output/output_0/ErrorLog.txt'),
            "device": self.device,
        }
        multiparticle_obj = MultiParticle(item)

        res = multiparticle_obj.run()
        return res

    def run_normal(self):
        #模拟没有误差的情况
        write_mulp_to_lattice_only_sim2(self.lattice_mulp_path, self.lattice_path)

        ouput = os.path.normpath(os.path.join(self.project_path, 'OutputFile/error_middle/output_0'))
        os.mkdir(ouput)

        # process = multiprocessing.Process(target=self.run_multiparticle,
        #                                   args=(self.project_path, 'OutputFile/error_middle/output_0'))
        #
        # process.start()  # 启动子进程
        # process.join()  # 等待子进程运行结束

        self.run_multiparticle(self.project_path, 'OutputFile/error_middle/output_0')

        self.write_density_every_time(0, 0)

        copy_file(self.lattice_path, self.normal_out_path)

        new_name = f'output_0_0'


        copy_directory(self.error_middle_output0_path, self.error_output_path, new_name)

        delete_directory(self.error_middle_output0_path)

    # def get_normal_data(self):
    #     path = os.path.join(self.error_output_path, "output_-1_-1")
    #     dataset_path = os.path.join(path, "DataSet.txt")
    #     print(dataset_path)
    #     dataset_obj = DatasetParameter(dataset_path, self.project_path)
    #     dataset_obj.get_parameter()
    #
    #     normal_data = [0,
    #                    dataset_obj.num_of_particle,  # 总粒子数
    #                    dataset_obj.emit_x[0],  # m, rad
    #                    dataset_obj.emit_y[0],  # m, rad
    #                    dataset_obj.emit_z[0],  # m, rad
    #                    dataset_obj.x[-1],  # m
    #                    dataset_obj.y[-1],  # m
    #                    dataset_obj.x_1[-1],
    #                    dataset_obj.y_1[-1],
    #                    dataset_obj.rms_x[-1],
    #                    dataset_obj.rms_y[-1],
    #                    dataset_obj.rms_x1[-1],
    #                    dataset_obj.rms_y1[-1],
    #                    dataset_obj.ek[-1],  # MeV
    #                    dataset_obj.phi[-1],  # deg
    #
    #                    ]
    #     self.normal_data = normal_data
    #     return normal_data


    def write_err_par_tot_title(self):
        errors_par_tot_title = [[
        "step_err",     #组 0
        "ratio_loss", #束流损失率，1- 存在粒子/总粒子 or 损失粒子 / 总粒子
        "emit_x_increase", #,x, y z方向发射度增长， x/x0 - 1
        "emit_y_increase",
        "emit_z_increase",

        "x_center(m)", #中心位置 5
        "y_center(m)",
        "x_'(rad)",
        "y_'(rad)",

        "rms_x(m)",
        "rms_y(m)",
        "rms_x'(rad)",   #11
        "rms_y'(rad)",   #12

        "delat_energy(MeV)", #能量变化  13

        ]]
        write_to_txt(self.errors_par_tot_path, errors_par_tot_title)


    def write_err_par_title(self):
        # errors_par_title = [
        #     [
        #         "step_err",  # 组 0
        #         "ave(ratio_loss)",  # 束流损失率，1- 存在粒子/总粒子 or 损失粒子 / 总粒子
        #         "ave(emit_x_increase)",  # ,x, y z方向发射度增长， x/x0 - 1
        #         "ave(emit_y_increase)",
        #         "ave(emit_z_increase)",
        #         "rms(x_center(m))",  # 中心位置 5
        #         "rms(y_center(m))",#6
        #         "rms(x_'(rad))",  #7
        #         "rms(y_'(rad))",  #8
        #         "ave(rms_x(m))",  #9
        #         "ave(rms_y(m))", #10
        #         "ave(rms_x'(rad))",  # 11
        #         "ave(rms_y'(rad))",  # 12
        #
        #         "ave(delat_energy)",  # 能量变化  13
        #
        #         "ave(x_center(m))",  # 中心位置 14
        #         "ave(y_center(m))",
        #         "ave(x_'(rad))",
        #         "ave(y_'(rad))",
        #
        #         "rms(delat_energy(MeV))",  # 能量变化  18
        #
        #         "rms(rms_x(m))",  #19
        #         "rms(rms_y(m))",  # 20
        #         "rms(rms_x'(rad))",  # 21
        #         "rms(rms_y'(rad))",  # 22
        #     ]
        # ]
        errors_par_title = [
            [
                "step_err",  # 组 0
                "ave(ratio_loss)",  # 束流损失率，1- 存在粒子/总粒子 or 损失粒子 / 总粒子
                "ave(emit_x_increase)",  # ,x, y z方向发射度增长， x/x0 - 1
                "ave(emit_y_increase)",
                "ave(emit_z_increase)",

                "ave(x_center(m))",  # 中心位置 5
                "ave(y_center(m))",
                "ave(x_'(rad))",
                "ave(y_'(rad))",

                "ave(rms_x(m))",  # 9
                "ave(rms_y(m))",  # 10
                "ave(rms_x'(rad))",  # 11
                "ave(rms_y'(rad))",  # 12

                "ave(delat_energy)",  # 能量变化  13

                "rms(x_center(m))",  # 中心位置 14
                "rms(y_center(m))",#15
                "rms(x_'(rad))",  #16
                "rms(y_'(rad))",  #17


                "rms(rms_x(m))",  #18
                "rms(rms_y(m))",  # 19
                "rms(rms_x'(rad))",  # 20
                "rms(rms_y'(rad))",  # 21

                "rms(delat_energy(MeV))",  # 能量变化  22

            ]
        ]
        write_to_txt(self.errors_par_path, errors_par_title)

    def write_err_par_every_time(self, group, time):
        #误差模拟完毕后对文件进行后处理
        #1.解析dataset文件


        if time == 0:
            output = self.normal_out_path
        else:
            output = os.path.join(self.error_output_path, f"output_{group}_{time}")


        #解析正常的情况
        if self.if_normal == 1:
            dataset_path = os.path.join(self.normal_out_path, "DataSet.txt")

            dataset_obj = DatasetParameter(dataset_path, self.project_path)
            dataset_obj.get_parameter()
            normal_ek = dataset_obj.ek[-1]

        if self.if_normal == 0:
            normal_ek = 0


        dataset_path = os.path.join(output, "DataSet.txt")
        dataset_obj = DatasetParameter(dataset_path, self.project_path)

        v1 = dataset_obj.get_parameter()
        if v1 is False:
            errors_par_tot_list = [f"{group}_{time}"] + [1] + [0]*12
        elif dataset_obj.z[-1] < (self.lattice_total_length-0.05):
            errors_par_tot_list = [f"{group}_{time}"] + [1] + [0]*12
        else:
            errors_par_tot_list = [
            f"{group}_{time}",
            dataset_obj.loss[-1] / dataset_obj.num_of_particle,
            dataset_obj.emit_x[-1]/dataset_obj.emit_x[0] - 1,
            dataset_obj.emit_y[-1]/dataset_obj.emit_y[0] - 1,
            dataset_obj.emit_z[-1]/dataset_obj.emit_z[0] - 1,
            dataset_obj.x[-1],  # m
            dataset_obj.y[-1],  # m
            dataset_obj.x_1[-1],
            dataset_obj.y_1[-1],
            dataset_obj.rms_x[-1],
            dataset_obj.rms_y[-1],
            dataset_obj.rms_x1[-1],
            dataset_obj.rms_y1[-1],
            dataset_obj.ek[-1] - normal_ek,  # MeV
            # dataset_obj.phi[-1] - normal_data[14],  # deg
            ]


        #写入到errors_par_tot
        for i in range(1, len(errors_par_tot_list)):
            errors_par_tot_list[i] = "{:.5e}".format(errors_par_tot_list[i])
        add_to_txt(self.errors_par_tot_path, [errors_par_tot_list])

        #写入到errors_par
        if time == 0:
            t1_lis = errors_par_tot_list + [0] * 9
            t1_lis[0] = 0

            add_to_txt(self.errors_par_path, [t1_lis])

        elif time == self.all_time:
            errors_par_tot_list = read_txt(self.errors_par_tot_path, out="list")

            t_lis = [j for j in errors_par_tot_list[1:] if int(j[0].split("_")[0]) == group]

            t1_lis = [0] * 23
            if len(t_lis) == 1:
                t1_lis = t_lis[0] + [0] * 9
                t1_lis[0] = group
                t1_lis = [float(i) for i in t1_lis]




            elif len(t_lis) > 1:
                t1_lis[0] = group
                t1_lis[1] = calculate_mean([float(j[1]) for j in t_lis])
                t1_lis[2] = calculate_mean([float(j[2]) for j in t_lis])
                t1_lis[3] = calculate_mean([float(j[3]) for j in t_lis])
                t1_lis[4] = calculate_mean([float(j[4]) for j in t_lis])

                t1_lis[5] = calculate_mean([float(j[5]) for j in t_lis])
                t1_lis[6] = calculate_mean([float(j[6]) for j in t_lis])
                t1_lis[7] = calculate_mean([float(j[7]) for j in t_lis])
                t1_lis[8] = calculate_mean([float(j[8]) for j in t_lis])

                t1_lis[9] = calculate_mean([float(j[9]) for j in t_lis])
                t1_lis[10] = calculate_mean([float(j[10]) for j in t_lis])
                t1_lis[11] = calculate_mean([float(j[11]) for j in t_lis])
                t1_lis[12] = calculate_mean([float(j[12]) for j in t_lis])

                t1_lis[13] = calculate_mean([float(j[13]) for j in t_lis])

                t1_lis[14] = calculate_rms([float(j[5]) for j in t_lis])
                t1_lis[15] = calculate_rms([float(j[6]) for j in t_lis])
                t1_lis[16] = calculate_rms([float(j[7]) for j in t_lis])
                t1_lis[17] = calculate_rms([float(j[8]) for j in t_lis])

                t1_lis[18] = calculate_rms([float(j[9]) for j in t_lis])
                t1_lis[19] = calculate_rms([float(j[10]) for j in t_lis])
                t1_lis[20] = calculate_rms([float(j[11]) for j in t_lis])
                t1_lis[21] = calculate_rms([float(j[12]) for j in t_lis])

                t1_lis[22] = calculate_rms([float(j[13]) for j in t_lis])


            for i in range(1, len(t1_lis)):
                t1_lis[i] = "{:.5e}".format(t1_lis[i])
            add_to_txt(self.errors_par_path, [t1_lis])


    def write_density_every_time(self, group, time):
        if self.if_normal == 1 and self.if_generate_density_file == 1:
            pass
        else:
            return 0

        is_normal = 0
        if group == 0:
            is_normal = 1

        exdata_path = os.path.join(self.error_middle_output0_path, "ExData.edt")


        dataset_path = os.path.join(self.error_middle_output0_path, "DataSet.txt")
        target_density_path = os.path.join(self.output_path,  f"density_par_{group}_{time}.dat")
        # print(dataset_path)
        # sys.exit()

        # if is_normal == 1:
        #     density_obj = PlttoDensity(beamset_path,  dataset_path, target_density_path)
        #     density_obj.generate_density_file_onestep(is_normal)
        #
        # elif is_normal == 0:
        #     #如果不是正常模拟
        #     normal_density_path = os.path.join(self.output_path,  f"density_par_{0}_{0}.dat")
        #     density_obj = PlttoDensity(beamset_path, dataset_path, target_density_path, normal_density_path, self.project_path)
        #     density_obj.generate_density_file_onestep(is_normal)

        if is_normal == 1:
            density_obj = ExtoDensity(exdata_path,  dataset_path, target_density_path)
            density_obj.generate_density_file_onestep(is_normal)

        elif is_normal == 0:
            normal_density_path = os.path.join(self.output_path,  f"density_par_{0}_{0}.dat")
            density_obj = ExtoDensity(exdata_path, dataset_path, target_density_path, normal_density_path, self.project_path)
            density_obj.generate_density_file_onestep(is_normal)

        os.remove(exdata_path)

        if time == self.all_time:
            #到了某一组的最后一次模拟
            all_file = list_files_in_directory(self.output_path)

            filtered_files = [path for path in all_file if f'density_par_{group}' in path]
            target_density_path = os.path.join(self.output_path, f"density_tot_par_{group}.dat")

            merge_obj = MergeDensityData(filtered_files, target_density_path)
            merge_obj.generate_density_file()

        if group == self.all_group and time == self.all_time:
            #到了所有组的最后一次模拟
            all_file = list_files_in_directory(self.output_path)

            filtered_files = [path for path in all_file if f'density_tot_par' in path]
            target_density_path = os.path.join(self.output_path, f"density_tot_par.dat")

            merge_obj = MergeDensityData(filtered_files, target_density_path)
            merge_obj.generate_density_file()

    def write_err_datas(self, group, time):

        err_datas_path = os.path.join(self.output_path, f"Error_Datas_{group}_{time}.txt")
        lattice_path = self.lattice_path
        input,_ = read_lattice_mulp_with_name(lattice_path)
        # print(input)
        # 为每个元件加编号

        input = add_element_end_index(input)
        res = []
        for i in range(len(input)):
            if input[i][0] == global_varible.error_elemment_command_dyn_ncpl[1]:
                #quad
                index = input[i+1][-1].split('_')[-1]
                err_name = f"CAV_ERROR[{index}]"
                t_lis = [err_name] + input[i][3:]
                res.append(t_lis)
            elif input[i][0] == global_varible.error_elemment_command_dyn_ncpl[0]:
                # quad
                index = input[i + 1][-1].split('_')[-1]
                err_name = f"QUAD_ERROR[{index}]"
                t_lis = [err_name] + input[i][3:]
                res.append(t_lis)
        write_to_txt(err_datas_path, res)


    def judge_dyn_on(self):
        if len(self.err_step_command) == 0:
            raise MissingcommandError("err_step")
        if (set(self.err_beam_dyn_on) == {0} and
           set(self.err_quad_dyn_on) == {0} and
           set(self.err_cav_dyn_on) == {0}):
            raise Exception("Missing dynamic error on command")

    def judge_stat_on(self):
        if len(self.err_step_command) == 0:
            raise MissingcommandError("err_step")
        if (set(self.err_beam_stat_on) == {0} and
           set(self.err_quad_stat_on) == {0} and
           set(self.err_cav_stat_on) == {0}):
            raise Exception("Missing static error on command")

    def judge_stat_dyn_on(self):
        if len(self.err_step_command) == 0:
            raise MissingcommandError("err_step")
        if (set(self.err_beam_stat_on) == {0} and
           set(self.err_quad_stat_on) == {0} and
           set(self.err_cav_stat_on) == {0} and
           set(self.err_beam_dyn_on) == {0} and
           set(self.err_quad_dyn_on) == {0} and
           set(self.err_cav_dyn_on) == {0}):
            raise Exception("Missing error on command")

class Errorstat2(Error):
    def __init__(self, item):
        super().__init__(item)
        self.all_error_lattice = []
        # 只优化
        # self.only_adjust_sign = 0
        self.err_type = 'stat'
        self.diag_every = {}


    def run_use_corrected_result(self, opti_res_this, group, time, error_lattice):

        # x =np.array(corrected_result).reshape(np.array(adjust_parameter_num).shape)
        error_lattice = copy.deepcopy(error_lattice)


        if self.opti:
            for k, v in opti_res_this.items():
                print(k, v)
                for com in error_lattice:
                    if com[-1] == f'element_{k.split("_")[0]}':
                        com[int(k.split("_")[1])] = v
                        break



            # x = list_one_two(list(corrected_result), adjust_parameter_num)
            # for i in range(len(adjust_element_num)):
            #     for j in range(len(adjust_parameter_num[i])):
            #         for com in error_lattice:
            #             if com[-1] == f'element_{adjust_element_num[i]}':
            #                 com[adjust_parameter_num[i][j]] = x[i][j]
            #                 break

        # 删除error_lattice最后的编号
        error_lattice = self.delete_element_end_index(error_lattice)

        #动态误差全部注释掉，把静态误差变为动态误差
        for i in error_lattice:
            if (i[0] in global_varible.error_elemment_command_dyn_ncpl or
                    i[0] in global_varible.error_beam_dyn):
                i[0] = "!" + i[0]
            # 如果是静态误差，变成动态误差
            elif i[0] == 'err_beam_stat':
                i[0] = 'err_beam_dyn'

            elif i[0] == 'err_quad_ncpl_stat':
                i[0] = 'err_quad_ncpl_dyn'

            elif i[0] == 'err_cav_ncpl_stat':
                i[0] = 'err_cav_ncpl_dyn'


            # 开关
            elif i[0] in global_varible.error_elemment_dyn_on or i[0] == 'err_beam_dyn_on':
                i[0] = "!" + i[0]

            elif i[0] == 'err_beam_stat_on':
                i[0] = 'err_beam_dyn_on'

            elif i[0] == global_varible.error_elemment_stat_on[0]:
                i[0] = global_varible.error_elemment_dyn_on[0]

            elif i[0] == global_varible.error_elemment_stat_on[1]:
                i[0] = global_varible.error_elemment_dyn_on[1]

        error_lattice = [i for i in error_lattice if i[0] in global_varible.err_write_command]
        with open(self.lattice_path, 'w') as f:
            for i in error_lattice:
                f.write(' '.join(map(str, i)) + '\n')




        if os.path.exists(self.error_middle_output0_path):
            delete_directory(self.error_middle_output0_path)

        # if self.only_adjust_sign == 1:
        # if self.err_type == 'only_adjust':
        #     os.makedirs(self.error_middle_output0_path)
        #
        #     process = multiprocessing.Process(target=self.run_multiparticle, args=(self.project_path, 'OutputFile/error_middle/output_0'))
        # else:
        #     process = multiprocessing.Process(target=self.run_multiparticle, args=(self.project_path, 'OutputFile/error_middle'))
        #
        # process.start()  # 启动子进程
        # process.join()  # 等待子进程运行结束

        self.run_multiparticle(self.project_path, 'OutputFile/error_output')

    def run_one_time_opti(self, group, time, lattice_mulp_list):
        self.diag_every.clear()
        """
        静态误差完整跑一次, 需要矫正

        :param group:
        :param time:
        :return:
        """
        v = Adjust_Error(self.project_path, self.field_path)
        opti_res_this_dict, diag_res_this = v.opti_one_time_different_group(group, time, lattice_mulp_list)

        return opti_res_this_dict, diag_res_this



    def write_adjust_datas(self, group, time, opti_res_this):
        adjust_datas_path = os.path.join(self.output_path, f"Adjust_Datas_{group}_{time}.txt")
        #
        res = []
        # for i, index in enumerate(adjust_element_num):
        #     err_name = f"element_adjust[{index}]"
        #     t_lis = [err_name] + opti_res_this[i]
        #     res.append(t_lis)
        for k, v in opti_res_this.items():
            t_lis = [f"element_adjust[{k}]"] + [round(v, 5)]
            res.append(t_lis)
        write_to_txt(adjust_datas_path, res)
    def judge_opti(self,):
        "判断是否需要优化"
        lattice_mulp_list, _ = read_lattice_mulp_with_name(self.lattice_mulp_path )
        all_adjust_N = []
        all_diag_N = []
        for i in lattice_mulp_list:
            if i[0].lower() == "adjust":
                all_adjust_N.append(i[1])
            elif i[0].lower().startswith("diag"):
                all_diag_N.append(i[1])

        common_N = list(set(all_adjust_N) & set(all_diag_N))
        if len(common_N) != 0:
            return 1
        else:
            return 0

    def run(self):
        # print(1529)
        self.get_group_time()
        self.judge_stat_on()

        self.write_err_par_title()
        self.write_err_par_tot_title()
        if self.if_normal == 1:
            self.run_normal()
            self.write_err_par_every_time(0, 0)


        self.opti = self.judge_opti()

        if self.opti:
            print(1579, "进行优化")
            for i in range(1, self.all_group+1):
                for j in range(1, self.all_time + 1):
                    lattice_mulp_list = self.generate_lattice_mulp_list(i)
                    opti_res_this, loss_this = self.run_one_time_opti(i, j, lattice_mulp_list)
                    print(opti_res_this, loss_this)
                    # opti_res_this = {'1_8': 0.4933612120807681, '1_7': 0.7579544029403025,
                    #                  '5_8': 0.7614636313839422, '5_7': 0.25891675029296335}
                    #
                    # diag_res = {'1_1': [[1.204, -0.01123944581, 0.009045890000000001, 1.68642, 1.68972, 2.45712],
                    #                     [1.22, -0.012475369, 0.01064619, 1.83377, 1.83652, 2.4571]]}
                    group = i
                    time = j

                    # 使用优化后的结果运行一次
                    self.run_use_corrected_result(opti_res_this, group, time, lattice_mulp_list)

                    # 将优化参数写入到文件
                    self.write_adjust_datas(group, time,  opti_res_this)
                    # 将束诊参数写入到文件
                    item = {
                        "project_path": self.project_path,
                        "input_file": self.input_path,
                        "output_file": os.path.join(self.output_path, "error_output", f"output_{group}_{time}"),
                        "diag_file_path": os.path.join(self.output_path, f"par_diag_datas_{group}_{time}.txt"),
                    }
                    obj = DiagInfo(item)
                    obj.write_diag_info_to_file()


                    self.write_err_datas(i, j)
                    self.write_err_par_every_time(i, j)

        else:
            print(1590, "不进行优化")
            for i in range(1, self.all_group+1):
                for j in range(1, self.all_time+1):
                    print(i, j)
                    lattice_mulp_list = self.generate_lattice_mulp_list(i)
                    self.run_use_corrected_result(0, i, j, lattice_mulp_list)


def err_stat2(**item):
    default_item = {
        "project_path": None,
        "seed": 50,
        "if_normal": 1,
        "field_path": None,
        "if_generate_density_file":1
    }
    default_item.update(item)
    v = Errorstat2(default_item)
    v.run()


if __name__ == "__main__":



    path = r"C:\Users\anxin\Desktop\test_shao"

    item = {
        "project_path": path,
        "seed": 50,
        "if_normal": 0,
        "field_path": None,
        "if_generate_density_file":0
    }
    obj = err_stat2(**item)

