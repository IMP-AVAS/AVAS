from scipy.optimize import minimize

import numpy as np

from utils.treatlist import flatten_list
from utils.tool import judge_command_on_element, delete_element_end_index

import os


import random
from core.MultiParticle import MultiParticle

import global_varible
import copy

from apps.diaginfo import DiagInfo
class Adjust_Error():
    """
    应该接收一个列表
    但是返回优化结果和
    """
    def __init__(self, project_path, field_path):
        self.diag_res = {}
        self.project_path = project_path
        self.lattice_mulp_path = os.path.join(self.project_path, "InputFile", "lattice_mulp.txt")
        self.lattice_path = os.path.join(self.project_path, "InputFile", "lattice.txt")
        self.error_elemment_command = global_varible.error_elemment_command


        self.error_beam_command = global_varible.error_beam_command
        self.error_beam_stat = global_varible.error_beam_stat
        self.error_beam_dyn = global_varible.error_beam_dyn
        self.field_path = field_path

        self.input_path = os.path.join(self.project_path, 'InputFile')
        self.output_path = os.path.join(self.project_path, 'OutputFile')

        self.error_middle_path = os.path.join(self.project_path, 'OutputFile', 'error_middle')
        self.error_middle_output0_path = os.path.join(self.project_path, 'OutputFile', 'error_middle', 'output_0')
        self.error_output_path = os.path.join(self.project_path, 'OutputFile', 'error_output')
        self.normal_out_path = os.path.join(self.error_output_path, 'output_0_0')

        self.errors_par_tot_path = os.path.join(self.output_path, "errors_par_tot.txt")
        self.errors_par_path = os.path.join(self.output_path, "errors_par.txt")
        self.err_adjust_path = os.path.join(self.project_path, "OutputFile", "error_adjust")

    def judge_command_on_element(self, lattice, command):
        #返回一个命令对应的是哪个元件
        lattice = copy.deepcopy(lattice)

        command_index = lattice.index(command)
        command_on_element = None
        for i in range(command_index, len(lattice)):
            if lattice[i][0] in global_varible.long_element:
                command_on_element = int(lattice[i][-1].split("_")[1])
                break
        return command_on_element

    def run_multiparticle(self, p_path, out_putfile_):
        item = {
            "project_path": p_path,
            "output_file": os.path.join(p_path, out_putfile_),
            "field_file": self.field_path,
            "errorlog_path": os.path.join(p_path, r'OutputFile/error_adjust/output_0/ErrorLog.txt'),
        }
        multiparticle_obj = MultiParticle(item)

        res = multiparticle_obj.run()
        return res

    def generate_adjust_parameter(self, input_lines):
        """
        产生定位信息, adjust命令中哪些参数需要修改
        """
        adjust_parameter_lattice_command = []  # 原来的命令
        adjust_element_num = []  # 第几个元件要改
        adjust_parameter_num = []  # 第几个参数要改
        adjust_parameter_range = []  # 参数的范围
        adjust_parameter_n = []  # 具有一样的值
        adjust_parameter_use_init = []  # 是否使用初值
        adjust_parameter_initial_value = []

        adjust_parameter_num_per = []
        adjust_parameter_range_per = []
        adjust_parameter_n_per = []
        adjust_parameter_use_init_per = []
        index = -1

        index = 0
        # 为adjust命令增加编号
        lattice = copy.deepcopy(input_lines)
        for i in lattice:
            if i[0] == "adjust":
                add_name = f'adjust_{index}'
                i.append(add_name)
                index += 1

        # 为每个调整命令增加作用元件数
        for i in lattice:
            if i[0] == "adjust":
                adjust_on_element = judge_command_on_element(lattice, i)
                i.append(adjust_on_element)
                if adjust_on_element not in adjust_element_num:
                    adjust_element_num.append(adjust_on_element)

        # [['adjust', '0', '1', '0', '0', '0.3', '0', 'adjust_0', 2]]
        all_adjust_command = []
        for i in lattice:
            if i[0] == "adjust":
                all_adjust_command.append(copy.deepcopy(i))

        adjust_parameter_num = [[] for _ in range(len(adjust_element_num))]
        adjust_parameter_range = [[] for _ in range(len(adjust_element_num))]
        adjust_parameter_n = [[] for _ in range(len(adjust_element_num))]
        adjust_parameter_use_init = [[] for _ in range(len(adjust_element_num))]
        for i in lattice:
            print(i)
        for i in lattice:
            if i[0] == "adjust":
                index = adjust_element_num.index(i[-1])
                adjust_parameter_num[index].append(int(i[2]))
                adjust_parameter_range[index].append([float(i[4]), float(i[5])])
                adjust_parameter_n[index].append(int(i[3]))
                adjust_parameter_use_init[index].append(int(i[6]))

        adjust_parameter_initial_value = [[] for _ in range(len(adjust_element_num))]
        print(adjust_element_num)
        for i in range(len(adjust_element_num)):
            for j in lattice:
                if j[0] in global_varible.mulpud_element and int(j[-1].split("_")[-1]) == adjust_element_num[i]:
                    for k in adjust_parameter_num[i]:
                        adjust_parameter_initial_value[i].append(float(j[k]))

                #     for k in adjust_parameter_num[i]:
                #
                #         #检查参数是否超过命令的长度
                #         if k > len(j[:-1]) -1:
                #             v = BaseError()
                #             command = []
                #             for com in all_adjust_command:
                #                 if com[-1] == adjust_element_num[i] and int(com[2]) == k:
                #                     command = com
                #                     break
                #             v.adjust_param_value_error(command[:-2])
                #
                #         adjust_parameter_initial_value[i].append(float(j[k]))
                # break
        #返回 哪些元件需要修改， 优化的初始初始值， 哪些参数需要修改， ,每个参数的范围，关联值n，是否使用初值
        return adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num, adjust_parameter_range, \
            adjust_parameter_n, adjust_parameter_use_init

        #[15, 16]
        # [[-38.0], [-0.3, 0.3]]
        # [[6], [5, 4]]  adjust_parameter_num
        # [[[-0.5, 0.5]], [[-0.5, 0.5], [-0.5, 0.5]]]
        # [[0], [0, 0]]
        # [[1], [1, 0]]

    def treat_diag(self, group, time, NN):

        """
        得到loss
        :return:
        """
        item = {
            "project_path": self.project_path,
            "input_file": os.path.join(self.project_path, "InputFile"),
            "output_file": os.path.join(self.project_path, r"OutputFile\error_adjust\output_0"),
            "diag_file_path": None,
        }
        obj = DiagInfo(item)
        res = obj.generate_all_diag_info()

        if NN is not None:
            diag_dict = [i for i in res if int(i['diag_command'][1]) == NN ]
        elif NN is None:
            diag_dict = [i for i in res]
        loss_list = []
        for i in diag_dict:
            if i['diag_command'][0] == "diag_position":
                target_x, target_y = float(i['diag_command'][2]), float(i['diag_command'][3])
                center_x, center_y = float(i['diag_data']["center"][0]), float(i['diag_data']["center"][1])
                accuracy = float(i['diag_command'][4])
                loss = ((center_x - target_x) ** 2) + ((center_y - target_y) ** 2)
                loss_list.append(loss)

            elif i['diag_command'][0] == "diag_size":
                target_x, target_y = float(i['diag_command'][2]), float(i['diag_command'][3])
                rms_size_x, rms_size_y = float(i['diag_data']["rms_size"][0]), float(i['diag_data']["rms_size"][1])
                accuracy = float(i['diag_command'][4])
                loss = ((rms_size_x - target_x) ** 2) + ((rms_size_y - target_y) ** 2)
                loss_list.append(loss)

            elif i['diag_command'][0] == "diag_energy":
                target_energy = float(i['diag_command'][2]),
                energy = float(i['diag_data']["energy"][0])
                accuracy = float(i['diag_command'][3])
                loss = (target_energy - energy) ** 2
                loss_list.append(loss)

        all_loss = 0
        for i in loss_list:
            all_loss += i
        return all_loss /len(loss_list)


        # diag_every_location = []
        # # 读取新的lattice信息
        #
        #
        # input_lines = error_lattice
        #
        # # 产生每一个diag针对的位置
        # lattice_obj = LatticeParameter()
        # lattice_obj.get_parameter(error_lattice)
        #
        #
        # lattice_copy = copy.deepcopy(input_lines)
        # index = 0
        # #为diag添加diag_0
        # for i in lattice_copy:
        #     if i[0].startswith("diag"):
        #         add_name = f'diag_{index}'
        #         i.append(add_name)
        #         index += 1
        #
        # index = 0
        # for i in lattice_copy:
        #     if i[0] in global_varible.long_element:
        #         add_name = f'element_{index}'
        #         i.append(add_name)
        #         index += 1
        #
        # all_diag_command = []
        # for i in lattice_copy:
        #     if i[0].startswith("diag"):
        #         all_diag_command.append(i)
        #
        # diag_index = []
        # diag_command_list = []
        # for i in all_diag_command:
        #     adjust_on_element = self.judge_command_on_element(lattice_copy, i)
        #     if adjust_on_element is not None:
        #         diag_index.append(adjust_on_element - 1)
        #     else:
        #         diag_index.append(-1)
        #
        #     diag_command_list.append(i[:5])
        #
        # diag = []
        #
        # for i in range(len(diag_index)):
        #     dic = {}
        #     dic['diag_command'] = diag_command_list[i]
        #     dic['diag_order'] = i
        #     dic['position'] = lattice_obj.v_start[diag_index[i]] + lattice_obj.v_len[diag_index[i]]
        #     diag.append(dic)
        #
        # # print(diag_index)
        # # print(diag)
        # # sys.exit()
        # error_adjust_output0_path = os.path.join(self.project_path, 'OutputFile', 'error_adjust', 'output_0')
        # dataset_path = os.path.join(error_adjust_output0_path, 'dataset.txt')
        #
        # dataset_obj = DatasetParameter(dataset_path)
        # dataset_obj.get_parameter()
        #
        # z_ = dataset_obj.z
        #
        #
        # loss_type = []
        # loss_list = []
        #
        # target_energy_list = []
        # target_position_list = []
        # target_size_list = []
        #
        #
        # for i in diag:
        #     position = i['position']
        #     print("position", position)
        #     index_of_position = 0
        #     for index, i1 in enumerate(z_):
        #         if i1 > position:
        #             index_of_position = index - 1
        #             break
        #
        #
        #
        #     center_x = dataset_obj.x[index_of_position] * 1000    #mm
        #     center_y = dataset_obj.y[index_of_position] * 1000    #mm
        #
        #     rms_x = dataset_obj.rms_x[index_of_position] * 1000   #mm
        #     rms_y = dataset_obj.rms_y[index_of_position] * 1000   #mm
        #
        #     energy = dataset_obj.ek[index_of_position]
        #
        #     v = [position, center_x, center_y, rms_x, rms_y, energy]
        #     diag_every_location.append(v)
        #     if i['diag_command'][0] == 'diag_position':
        #
        #         target_x, target_y = float(i['diag_command'][2]), float(i['diag_command'][3])
        #         accuracy = float(i['diag_command'][4])
        #         loss = ((center_x - target_x) ** 2) + ((center_y - target_y) ** 2)
        #
        #         target_position_list.append(target_x)
        #         loss_list.append(loss)
        #         loss_type.append('diag_position')
        #
        #     if i['diag_command'][0] == 'diag_size':
        #
        #
        #         target_x, target_y = float(i['diag_command'][2]), float(i['diag_command'][3])
        #
        #         accuracy = float(i['diag_command'][4])
        #
        #         print(target_x, rms_x, ((rms_x - target_x) ** 2) )
        #         print(target_y, rms_y, ((rms_y - target_y) ** 2) )
        #
        #         target_size_list.append(target_x)
        #         loss = ((rms_x - target_x) ** 2) + ((rms_y - target_y) ** 2)
        #         loss_list.append(loss)
        #
        #         loss_type.append('diag_size')
        #
        #     if i['diag_command'][0] == 'diag_energy':
        #         target_energy = float(i['diag_command'][2])
        #
        #         print('target_energy', target_energy)
        #         print('res_energy', energy)
        #
        #         accuracy = float(i['diag_command'][3])
        #
        #         loss = ((energy - target_energy) ** 2)
        #
        #         target_energy_list.append(target_energy)
        #         loss_list.append(loss)
        #         loss_type.append('diag_energy')
        #
        #
        # diag_res = {}
        # diag_res[f"{group}_{time}"] = diag_every_location
        #
        # all_loss = 0
        # for i in loss_list:
        #     all_loss += i
        #
        # return all_loss, diag_res

    # def treat_diag(self, group, time, error_lattice):
    #
    #     """
    #     得到loss
    #     :return:
    #     """
    #     diag_every_location = []
    #     # 读取新的lattice信息
    #
    #
    #     input_lines = error_lattice
    #
    #     # 产生每一个diag针对的位置
    #     lattice_obj = LatticeParameter()
    #     lattice_obj.get_parameter(error_lattice)
    #
    #
    #     lattice_copy = copy.deepcopy(input_lines)
    #     index = 0
    #     #为diag添加diag_0
    #     for i in lattice_copy:
    #         if i[0].startswith("diag"):
    #             add_name = f'diag_{index}'
    #             i.append(add_name)
    #             index += 1
    #
    #     index = 0
    #     for i in lattice_copy:
    #         if i[0] in global_varible.long_element:
    #             add_name = f'element_{index}'
    #             i.append(add_name)
    #             index += 1
    #
    #     all_diag_command = []
    #     for i in lattice_copy:
    #         if i[0].startswith("diag"):
    #             all_diag_command.append(i)
    #
    #     diag_index = []
    #     diag_command_list = []
    #     for i in all_diag_command:
    #         adjust_on_element = self.judge_command_on_element(lattice_copy, i)
    #         if adjust_on_element is not None:
    #             diag_index.append(adjust_on_element - 1)
    #         else:
    #             diag_index.append(-1)
    #
    #         diag_command_list.append(i[:5])
    #
    #     diag = []
    #
    #     for i in range(len(diag_index)):
    #         dic = {}
    #         dic['diag_command'] = diag_command_list[i]
    #         dic['diag_order'] = i
    #         dic['position'] = lattice_obj.v_start[diag_index[i]] + lattice_obj.v_len[diag_index[i]]
    #         diag.append(dic)
    #
    #     # print(diag_index)
    #     # print(diag)
    #     # sys.exit()
    #     error_adjust_output0_path = os.path.join(self.project_path, 'OutputFile', 'error_adjust', 'output_0')
    #     dataset_path = os.path.join(error_adjust_output0_path, 'dataset.txt')
    #
    #     dataset_obj = DatasetParameter(dataset_path)
    #     dataset_obj.get_parameter()
    #
    #     z_ = dataset_obj.z
    #
    #
    #     loss_type = []
    #     loss_list = []
    #
    #     target_energy_list = []
    #     target_position_list = []
    #     target_size_list = []
    #
    #
    #     for i in diag:
    #         position = i['position']
    #         print("position", position)
    #         index_of_position = 0
    #         for index, i1 in enumerate(z_):
    #             if i1 > position:
    #                 index_of_position = index - 1
    #                 break
    #
    #
    #
    #         center_x = dataset_obj.x[index_of_position] * 1000    #mm
    #         center_y = dataset_obj.y[index_of_position] * 1000    #mm
    #
    #         rms_x = dataset_obj.rms_x[index_of_position] * 1000   #mm
    #         rms_y = dataset_obj.rms_y[index_of_position] * 1000   #mm
    #
    #         energy = dataset_obj.ek[index_of_position]
    #
    #         v = [position, center_x, center_y, rms_x, rms_y, energy]
    #         diag_every_location.append(v)
    #         if i['diag_command'][0] == 'diag_position':
    #
    #             target_x, target_y = float(i['diag_command'][2]), float(i['diag_command'][3])
    #             accuracy = float(i['diag_command'][4])
    #             loss = ((center_x - target_x) ** 2) + ((center_y - target_y) ** 2)
    #
    #             target_position_list.append(target_x)
    #             loss_list.append(loss)
    #             loss_type.append('diag_position')
    #
    #         if i['diag_command'][0] == 'diag_size':
    #
    #
    #             target_x, target_y = float(i['diag_command'][2]), float(i['diag_command'][3])
    #
    #             accuracy = float(i['diag_command'][4])
    #
    #             print(target_x, rms_x, ((rms_x - target_x) ** 2) )
    #             print(target_y, rms_y, ((rms_y - target_y) ** 2) )
    #
    #             target_size_list.append(target_x)
    #             loss = ((rms_x - target_x) ** 2) + ((rms_y - target_y) ** 2)
    #             loss_list.append(loss)
    #
    #             loss_type.append('diag_size')
    #
    #         if i['diag_command'][0] == 'diag_energy':
    #             target_energy = float(i['diag_command'][2])
    #
    #             print('target_energy', target_energy)
    #             print('res_energy', energy)
    #
    #             accuracy = float(i['diag_command'][3])
    #
    #             loss = ((energy - target_energy) ** 2)
    #
    #             target_energy_list.append(target_energy)
    #             loss_list.append(loss)
    #             loss_type.append('diag_energy')
    #
    #
    #     diag_res = {}
    #     diag_res[f"{group}_{time}"] = diag_every_location
    #
    #     all_loss = 0
    #     for i in loss_list:
    #         all_loss += i
    #
    #     return all_loss, diag_res

    def get_goal(self, error_lattice, adjust_element_num, adjust_parameter_num, group, time, NN):
        def goal(x):
            print("--------------------")
            print('x', x)

            self.ini_this.append(x)

            v1 = 0
            for i_index, i_value in enumerate(adjust_element_num):
                for j_index, j_value in enumerate(adjust_parameter_num[i_index]):
                    for com in error_lattice:
                        if com[-1] == f'element_{i_value}':
                            com[j_value] = x[v1]
                            break
                    v1 += 1

            error_lattice_no_index = delete_element_end_index(error_lattice)


            error_lattice_write = copy.deepcopy(error_lattice_no_index)


            for index, i in enumerate(error_lattice[::-1]):
                index = -1 * index - 1
                if index == -1 and i[0].startswith("diag"):
                    break

                if index == -2 and i[0].startswith("diag"):
                    break

                if i[0].startswith("diag"):
                    error_lattice_write.insert(index + 1, ['end'])
                    break


            for i in error_lattice_write:

                if i[0] in global_varible.error_elemment_command_dyn_ncpl or i[0] in global_varible.error_beam_dyn:
                    i[0] = "!" + i[0]
                # 如果是静态误差，变成动态误差
                elif i[0] == 'err_beam_stat':
                    i[0] = 'err_beam_dyn'

                elif i[0] == 'err_quad_ncpl_stat':
                    i[0] = 'err_quad_ncpl_dyn'

                elif i[0] == 'err_cav_ncpl_stat':
                    i[0] = 'err_cav_ncpl_dyn'


                # 开关
                elif i[0] in global_varible.error_elemment_dyn_on:
                    i[0] = "!" + i[0]

                elif i[0] == global_varible.error_elemment_stat_on[0]:
                    i[0] = global_varible.error_elemment_dyn_on[0]

                elif i[0] == global_varible.error_elemment_stat_on[1]:
                    i[0] = global_varible.error_elemment_dyn_on[1]

                #     print(4)
                # print(2, i)
            error_lattice_write = [i for i in error_lattice_write if i[0] in global_varible.err_write_command]

            with open(self.lattice_path, 'w') as f:
                for i in error_lattice_write:
                    f.write(' '.join(map(str, i)) + '\n')



            # delete_directory(self.error_middle_output0_path)

            err_adjust_output0_path = os.path.join(self.project_path, "OutputFile", "error_adjust", "output_0" )
            # if os.path.exists(err_adjust_output0_path):
            #     delete_directory(err_adjust_output0_path)

            self.run_multiparticle(self.project_path, 'OutputFile/error_adjust')
            loss = self.treat_diag(group, time, NN)

            # delete_directory(err_adjust_output0_path)

            print("loss", loss)
            self.loss_this.append(loss)
            print("--------------------")

            if loss < 0.05:
                raise Exception('已小于0.05')

            return loss

        return goal
    def optimize_one_group(self, group, time, error_lattice,
                           adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num,
                           adjust_parameter_range, \
                           adjust_parameter_n, adjust_parameter_use_init, NN):

        error_lattice = copy.deepcopy(error_lattice)

        # lattice中原本的初值
        # lattice_initial_value =np.array(adjust_parameter_initial_value).reshape(-1)

        lattice_initial_value = flatten_list(adjust_parameter_initial_value)

        # print('lattice_initial_value', lattice_initial_value)

        # 范围
        parameter_range = np.array(flatten_list(adjust_parameter_range)).reshape(-1, 2)
        # print('parameter_range', parameter_range)

        # 随机初值
        random_initial_value = [random.uniform(i[0], i[1]) for i in parameter_range]

        # 是否使用初值
        # use_initial_value = np.array(adjust_parameter_use_init).reshape(-1)
        use_initial_value = np.hstack(adjust_parameter_use_init)

        # 最终初值
        initial_value = random_initial_value
        for i in range(len(initial_value)):
            if use_initial_value[i] == 1:
                initial_value[i] = lattice_initial_value[i]

        print('initial_value', initial_value)

        # 是否使用相同的值
        # n_ = np.array(adjust_parameter_n).reshape(-1)
        n_ = flatten_list(adjust_parameter_n)
        # print('n_', n_)

        unique_elements, unique_indices = np.unique(n_, return_index=True)
        print(unique_elements, unique_indices)

        indiaces = []

        for i in range(len(unique_elements)):
            if unique_elements[i] != 0:
                indiaces.append([index for index, element in enumerate(n_) if element == unique_elements[i]])


        constraints = []
        for i in indiaces:
            if len(i) == 1:
                continue
            for j in range(1, len(i)):
                # print([i[j]], i[0])
                initial_value[i[j]] = initial_value[i[0]]
                constraints.append({'type': 'eq', 'fun': lambda x: x[i[j]] - x[i[0]]})


        # for constraint in constraints:
        #     print('约束条件函数结果:', constraint)

        goal = self.get_goal(error_lattice, adjust_element_num, adjust_parameter_num, group, time, NN)

        options = {'maxiter': 100, 'eps': 10**-1, 'ftol': 10**-4}


        # result = minimize(fun=goal, x0=initial_value, constraints=constraints, bounds=parameter_range,
        #                       method='SLSQP', options=options)
        #
        # return result.x, result.fun

        try:
            result = minimize(fun=goal, x0=initial_value, constraints=constraints, bounds=parameter_range,
                              method='SLSQP', options=options)

            return result.x, result.fun

        except Exception:
            return self.ini_this[-1], self.loss_this[-1]


    def opti_one_time(self, group, time, lattice_mulp_list):
        """
        静态误差完整跑一次, 需要矫正

        :param group:
        :param time:hg
        :return:
        """

        # 得到lattice的定位信息
        adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num, adjust_parameter_range, \
            adjust_parameter_n, adjust_parameter_use_init = self.generate_adjust_parameter(lattice_mulp_list)
        #[1][[0.1]][[8]][[[0.0, 1.0]]][[0]][[1]]
        opti_res_this, loss_this = self.optimize_one_group(group, time, lattice_mulp_list,
                                                           adjust_element_num, adjust_parameter_initial_value,
                                                           adjust_parameter_num,
                                                           adjust_parameter_range,\
                                                           adjust_parameter_n, adjust_parameter_use_init)

        adjust_info = [adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num, adjust_parameter_range, \
            adjust_parameter_n, adjust_parameter_use_init]

        #返回矫正参数信息, 这一次优化的结果， 只一次优化的损失， 束诊结果
        return adjust_info, opti_res_this, loss_this, self.diag_res

    def opti_one_time_different_group(self, group, time, lattice_mulp_list):
        print(572)
        #使用不同的组数进行优化
        """
        静态误差完整跑一次, 需要矫正

        :param group:
        :param time:hg
        :return:
        """
        lattice_mulp_list = copy.deepcopy(lattice_mulp_list)

        all_adjust_N = []
        all_diag_N = []
        for i in lattice_mulp_list:
            if i[0].lower() == "adjust":
                all_adjust_N.append(int(i[1]))
            elif i[0].lower().startswith("diag"):
                all_diag_N.append(int(i[1]))

        common_N = list(set(all_adjust_N) & set(all_diag_N))
        # print(591, common_N)
        # print(all_adjust_N)
        iteration_step = 0
        common_N = sorted(common_N)

        opti_res_this_dict = {}
        for i in common_N:
            NN = i
            t_lattice = copy.deepcopy(lattice_mulp_list)
            for j in t_lattice:
                if j[0].lower() == "adjust" and int(j[1]) != i:
                    j.append(False)

                if j[0].lower().startswith("diag") and int(j[1]) != i:
                    j.append(False)

            t_lattice = [k for k in t_lattice if k[-1] is not False]
            # for i in t_lattice:
            #     print(i)
            # sys.exit()
            # 得到lattice的定位信息
            adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num, adjust_parameter_range, \
                adjust_parameter_n, adjust_parameter_use_init = self.generate_adjust_parameter(t_lattice)
            # 返回 哪些元件需要修改， 优化的初始初始值， 哪些参数需要修改， ,每个参数的范围，关联值n，是否使用初值

            print( adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num, adjust_parameter_range, \
                adjust_parameter_n, adjust_parameter_use_init)

            self.ini_this = []
            self.loss_this = []

            opti_res_this, loss_this = self.optimize_one_group(group, time, t_lattice,
                                                               adjust_element_num, adjust_parameter_initial_value,
                                                               adjust_parameter_num,
                                                               adjust_parameter_range,
                                                               adjust_parameter_n, adjust_parameter_use_init, NN)

            # print(618, adjust_element_num, adjust_parameter_initial_value, adjust_parameter_num, adjust_parameter_range, \
            #     adjust_parameter_n, adjust_parameter_use_init)
            # print(620, opti_res_this)

            lattice_mulp_list = self.change_latticae_with_opti_res(opti_res_this, lattice_mulp_list, adjust_element_num, adjust_parameter_num)
            # for i1 in lattice_mulp_list:
            #     print(i1)

            v1 = 0
            for i_index, i_value in enumerate(adjust_element_num):
                for j_index, j_value in enumerate(adjust_parameter_num[i_index]):
                    opti_res_this_dict[f"{i_value}_{j_value}"] = opti_res_this[v1]
                    v1 += 1

        all_loss = self.treat_diag(group, time, None)

    #返回矫正参数信息, 这一次优化的结果， 只一次优化的损失， 束诊结果
        return opti_res_this_dict, all_loss

    # sys.exit()
    # self.run_use_corrected_result(opti_res_this, group, time, lattice_mulp_list,
    #                               adjust_element_num, adjust_parameter_num)

    def change_latticae_with_opti_res(self,  opti_res_this, error_lattice,
                                 adjust_element_num, adjust_parameter_num):
        error_lattice = copy.deepcopy(error_lattice)
        # x = list_one_two(list(opti_res_this), adjust_parameter_num)
        # for i in range(len(adjust_element_num)):
        #     for j in range(len(adjust_parameter_num[i])):
        #         for com in error_lattice:
        #             if com[-1] == f'element_{adjust_element_num[i]}':
        #                 com[adjust_parameter_num[i][j]] = x[i][j]
        #                 break

        v1 = 0
        for i_index, i_value in enumerate(adjust_element_num):
            for j_index, j_value in enumerate(adjust_parameter_num[i_index]):
                for com in error_lattice:
                    if com[-1] == f'element_{i_value}':
                        com[j_value] = opti_res_this[v1]
                        break
                v1 += 1

        return error_lattice
