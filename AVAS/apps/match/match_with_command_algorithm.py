#进行twiss参数的匹配
import copy

from matplotlib.cbook import safe_first_element

from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name

from utils.tool import judge_command_on_element, judge_command_under_element, add_element_end_index, delete_element_end_index

import global_varible
import random
from scipy.optimize import minimize
import os
from core.MultiParticle import MultiParticle

from utils.treat_directory import list_files_in_directory, copy_directory, delete_directory
from apps.match.setdiaginfo import SetDiagInfo
import math

def position_loss( k_coefficient,
                    target_x, target_x1, target_y, target_y1,
                    rel_x, rel_x1,  rel_y, rel_y1,
                    not_consider_list
                ):
    def cal_loss(target_x, rel_x):
        return (target_x - rel_x)**2

    loss_x = cal_loss(target_x, rel_x)
    loss_x1 = cal_loss(target_x1, rel_x1)
    loss_y = cal_loss(target_y, rel_y)
    loss_y1 = cal_loss(target_y1, rel_y1)

    loss_list = [loss_x, loss_x1, loss_y, loss_y1]

    loss = 0
    for i in range(4):
        if not_consider_list[i] == 0:
            loss += loss_list[i]
    loss = k_coefficient/2 * loss
    return loss


def size_loss(  k_coefficient,
                    target_size_x, target_size_y, target_size_z,
                    rel_size_x, rel_size_y, rel_size_z,
                    not_consider_list
                ):
    def cal_loss(target_x, rel_x):
        if rel_x != 0:
            return ( (target_x - rel_x) /target_x )**2

        elif rel_x == 0:
            return 0

    loss_x = cal_loss(target_size_x, rel_size_x)
    loss_y = cal_loss(target_size_y, rel_size_y)
    loss_z = cal_loss(target_size_z, rel_size_z)

    loss_list = [loss_x, loss_y, loss_z]

    M = len([i for i in not_consider_list if i == 0])

    loss = 0
    for i in range(3):
        if not_consider_list[i] == 0:
            loss += loss_list[i]
    loss = k_coefficient / M * loss
    return loss



def twiss_loss(
        target_alpha_x,
        target_beta_x,
        target_alpha_y,
        target_beta_y,
        target_alpha_z,
        target_beta_z,

        rel_alpha_x,
        rel_beta_x,
        rel_alpha_y,
        rel_beta_y,
        rel_alpha_z,
        rel_beta_z,

        not_consider_x,
        not_consider_y,
        not_consider_z,
):
    #alpha_0代表目标值

    def calculate_twiss_distance(alpha, beta, alpha0, beta0):
        if beta0 == 0 or beta0 == 0:
            return 0
        # gamma = (1+alpha^2)/beta
        gamma = (1 + alpha ** 2) / beta
        gamma0 = (1 + alpha0 ** 2) / beta0


        R = (
            beta * gamma0
            + beta0 * gamma
            - 2 * alpha * alpha0
        )


        # 防止浮点误差导致 sqrt 负数
        if R < 2:
            R = 2


        loss = (
            math.sqrt(
                (R + math.sqrt(R ** 2 - 4)) / 2
            )
            - 1
        ) ** 2 / 2


        return loss


    loss_x = calculate_twiss_distance(
        rel_alpha_x,
        rel_beta_x,
        target_alpha_x,
        target_beta_x
    )


    loss_y = calculate_twiss_distance(
        rel_alpha_y,
        rel_beta_y,
        target_alpha_y,
        target_beta_y
    )
    loss_z = calculate_twiss_distance(
        rel_alpha_z,
        rel_beta_z,
        target_alpha_z,
        target_beta_z
    )

    loss_list = [loss_x, loss_y, loss_z]
    not_consider_list = [not_consider_x, not_consider_y, not_consider_z]

    loss = 0
    for i in range(3):
        if not_consider_list[i] == 0:
            loss += loss_list[i]

    return loss

class MatchWithConmmandalgorithm(object):
    def __init__(self, item):
        self.project_path = item.get("project_path")
        self.seed = item.get("seed")
        self.if_normal = item.get("if_normal")
        self.field_path = item.get("field_path")
        self.if_generate_density_file = item.get("if_generate_density_file")
        self.restart = item.get("restart", 0)
        self.lattice_path = os.path.join(self.project_path, "InputFile", "lattice.txt")
        self.match_sim_type = item.get("match_sim_type")
        self.device = item.get("device") or "cpu"

        self.match_adjust_out0_path = os.path.join(self.project_path, "OutputFile", "match_adjust", "output_0")

        if os.path.exists(self.match_adjust_out0_path):
            delete_directory(self.match_adjust_out0_path)
        os.makedirs(self.match_adjust_out0_path)

        self.v_index = 0
    def treat_set(self,  NN):

        """
        得到loss
        :return:
        """
        item = {
            "project_path": self.project_path,
            "input_file": os.path.join(self.project_path, "InputFile"),
            "output_file": os.path.join(self.project_path, r"OutputFile\match_adjust\output_0"),
            "diag_file_path": None,
            "dataset_mode": "env"
        }
        obj = SetDiagInfo(item)
        res = obj.generate_all_set_info()

        if NN is not None:
            set_dict = [i for i in res if int(i['set_command'][1]) == NN ]
        elif NN is None:
            set_dict = [i for i in res]
        loss_list = []
        for i in set_dict:
            if i['set_command'][0] == "set_position":

                k_coefficient = float(i['set_command'][2])
                target_x, target_x1, target_y, target_y1 = (float(i['set_command'][3]), float(i['set_command'][4]),
                                                            float(i['set_command'][5]), float(i['set_command'][6]))

                rel_x, rel_x1,  rel_y, rel_y1 = ( float(i['set_data']["center"][0]), float(i['set_data']["center"][1]),
                                                float(i['set_data']["center"][2]), float(i['set_data']["center"][3]) )


                not_consider_list = i['set_command'][7:11]
                not_consider_list = [int(i) for i in not_consider_list]

                loss = position_loss(
                    k_coefficient,
                    target_x, target_x1, target_y, target_y1,
                    rel_x, rel_x1,  rel_y, rel_y1,
                    not_consider_list
                )
                loss_list.append(loss)

            elif i['set_command'][0] == "set_rms_size":
                k_coefficient = float(i['set_command'][2])

                target_size_x, target_size_y, target_size_z = float(i['set_command'][2]), float(i['set_command'][3]), float(i['set_command'][4])
                rel_size_x, rel_size_y, rel_size_z = float(i['set_data']["rms_size"][0]), float(i['set_data']["rms_size"][1]), float(i['set_data']["rms_size"][2])

                not_consider_list = i['set_command'][7:11]
                not_consider_list = [int(i) for i in not_consider_list]

                loss = size_loss(
                    k_coefficient,
                    target_size_x, target_size_y, target_size_z,
                    rel_size_x, rel_size_y, rel_size_z,
                    not_consider_list
                )

                loss_list.append(loss)


            # elif i['set_command'][0] == "set_energy":
            #     target_energy = float(i['set_command'][2]),
            #     energy = float(i['set_data']["energy"][0])
            #     accuracy = float(i['set_command'][3])
            #     loss = (target_energy - energy) ** 2
            #     loss_list.append(loss)



            elif i['set_command'][0] == "set_twiss":
                target_alpha_x, target_beta_x = float(i['set_command'][2]), float(i['set_command'][3])
                target_alpha_y, target_beta_y =  float(i['set_command'][4]), float(i['set_command'][5])

                rel_alpha_x, rel_beta_x, rel_alpha_y, rel_beta_y = i["set_data"]["emit_x"][0], i["set_data"]["emit_x"][1],\
                i["set_data"]["emit_y"][0], i["set_data"]["emit_y"][1]

                #不考虑的值是1，考虑代表0
                not_consider_x = int(i["set_command"][8])
                not_consider_y = int(i["set_command"][9])
                not_consider_z = int(i["set_command"][10])

                target_alpha_z = 0
                target_beta_z = 0
                rel_alpha_z = 0
                rel_beta_z = 0

                loss = twiss_loss(
                target_alpha_x,
                target_beta_x,
                target_alpha_y,
                target_beta_y,
                target_alpha_z,
                target_beta_z,

                rel_alpha_x,
                rel_beta_x,
                rel_alpha_y,
                rel_beta_y,
                rel_alpha_z,
                rel_beta_z,

                not_consider_x,
                not_consider_y,
                not_consider_z,
                )

                loss_list.append(loss)

        print("283*", loss_list)

        all_loss = 0
        for i in loss_list:
            all_loss += i


        return all_loss /len(loss_list)


    def generate_match_parameter(self, input_lines):
        """
        解析 match 命令，并按照作用元件分组
        """

################################################
        #给每个原件末尾加一个索引
        lattice = add_element_end_index(input_lines)

        #给match命令添加一个索引
        index = 0
        for i in lattice:
            if i[0].startswith("match"):
                add_name = f'match_{index}'
                i.append(add_name)
                index += 1
###########################################

        # 1. 给 match 命令编号，并确定作用元件
        match_commands = []

        match_index = 0

        for command in lattice:

            if command[0] != "match":
                continue

            element_num = judge_command_on_element(lattice, command)

            match_commands.append({
                "name": f"match_{match_index}",  #判断是第几个match命令
                "element_num": element_num,        #作用于哪个原件上
                "parameter_num": int(command[2]),   #哪一个参数要修改
                "n": int(command[3]),      #关联值n的使用
                "range": [float(command[4]), float(command[5])],  #参数的范围
                "use_init": int(command[6]),        #是否使用初值
            })

            match_index += 1

        # 2. 按照元件编号分组
        match_info = {}

        for command in match_commands:

            element_num = command["element_num"]

            if element_num not in match_info:
                match_info[element_num] = {
                    "parameter_num": [], #哪一个参数要修改 1w
                    "range": [],      #参数的范围    2w
                    "n": [],          #关联值n的使用  1w
                    "use_init": [],   #是否使用初值  1w
                    "initial_value": [], #初值是多少  1w
                }

            info = match_info[element_num]

            info["parameter_num"].append(command["parameter_num"])
            info["range"].append(command["range"])
            info["n"].append(command["n"])
            info["use_init"].append(command["use_init"])
        # {1: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': []},
        #  2: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': []},
        #  3: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': []},
        #  12: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': []},
        #  13: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': []},
        #  14: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': []}}

        # 3. 获取各参数的初始值
        for command in lattice:

            if command[0] not in global_varible.mulp_element:
                continue

            element_num = int(command[-1].split("_")[-1])

            if element_num not in match_info:
                continue

            for parameter_num in match_info[element_num]["parameter_num"]:

                match_info[element_num]["initial_value"].append(
                    float(command[parameter_num])
                )

        # {1: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': [23.2007]},
        #  2: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': [-102.9382]},
        #  3: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': [30.9583]},
        #  12: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': [-21.5266]},
        #  13: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': [32.8803]},
        #  14: {'parameter_num': [8], 'range': [[-100.0, 100.0]], 'n': [0], 'use_init': [0], 'initial_value': [0.5652]}}

        return match_info



    def run_multiparticle(self, item):
        item_this = {
            "project_path": self.project_path,
            "output_file": item.get("output_file"),
            "field_path": self.field_path,
            "device": self.device,
            "env_par_mode": self.match_sim_type ,
        }

        multiparticle_obj = MultiParticle(item_this)

        res = multiparticle_obj.run()
        return res


    def get_goal(self, match_lattice, adjust_element_num, adjust_parameter_num, NN):
        def goal(x):
            print("--------------------")
            print('x', x)

            self.ini_this.append(x)

            # 给每个原件末尾加一个索引
            match_lattice_index = add_element_end_index(match_lattice)



            v1 = 0
            for i_index, i_value in enumerate(adjust_element_num):
                for j_index, j_value in enumerate(adjust_parameter_num[i_index]):
                    for com in match_lattice_index:
                        if com[-1] == f'element_{i_value}':
                            com[j_value] = x[v1]
                            break
                    v1 += 1
            #删除所有原件的索引
            match_lattice_no_index = delete_element_end_index(match_lattice_index)
            #注释掉所有的match命令

            for i in match_lattice_no_index:
                if i[0].startswith("match"):
                    i[0] = "!" + i[0]

            match_lattice_write = [i for i in match_lattice_no_index if i[0] in global_varible.mulp_basic_command]

            with open(self.lattice_path, 'w') as f:
                for i in match_lattice_write:
                    f.write(' '.join(map(str, i)) + '\n')



            # delete_directory(self.match_middle_output0_path)

            err_adjust_output0_path = os.path.join(self.project_path, "OutputFile", "match_adjust", "output_0" )
            # if os.path.exists(err_adjust_output0_path):
            #     delete_directory(err_adjust_output0_path)

            sim_item = {
                "output_file": os.path.join(self.project_path, "OutputFile", "match_adjust", "output_0"), #用来优化的地址
            }


            self.run_multiparticle(sim_item)
            loss = self.treat_set(NN)

            # delete_directory(err_adjust_output0_path)

            print("loss", loss)
            self.v_index += 1
            print(self.v_index)
            self.loss_this.append(loss)
            print("--------------------")

            if loss < 0.0005:
                raise Exception('已小于0.0005')

            return loss

        return goal


    def optimize_one_group(self, match_lattice, adjust_info, NN):

        match_lattice = copy.deepcopy(match_lattice)

        lattice_initial_value = []
        parameter_range = []
        use_initial_value = []
        n_ = []

        adjust_element_num = []
        adjust_parameter_num = []

        #######################################################################
        # 从adjust_info中提取数据

        for element_num, info in adjust_info.items():
            adjust_element_num.append(element_num)

            adjust_parameter_num.append(info["parameter_num"])

            lattice_initial_value.extend(info["initial_value"])

            parameter_range.extend(info["range"])

            use_initial_value.extend(info["use_init"])

            n_.extend(info["n"])

        print("adjust_element_num", adjust_element_num) #adjust_element_num [4, 5, 6]
        print("adjust_parameter_num", adjust_parameter_num) #adjust_parameter_num [[7], [7, 8], [7]]
        print("lattice_initial_value", lattice_initial_value)
        print("parameter_range", parameter_range)
        print("use_initial_value", use_initial_value)

        #######################################################################
        # 随机初值

        random_initial_value = [
            random.uniform(i[0], i[1])
            for i in parameter_range
        ]

        initial_value = random_initial_value

        # 是否使用lattice中的初值
        for i in range(len(initial_value)):

            if use_initial_value[i] == 1:
                initial_value[i] = lattice_initial_value[i]

        print('initial_value', initial_value)

        #######################################################################
        # 产生优化初值

        random_initial_value = [
            random.uniform(i[0], i[1])
            for i in parameter_range
        ]

        initial_value = random_initial_value

        for i in range(len(initial_value)):

            if use_initial_value[i] == 1:
                initial_value[i] = lattice_initial_value[i]

        print('initial_value', initial_value)

        #######################################################################
        # 根据n寻找哪些参数需要使用相同的值

        same_parameter = {}

        for index, n in enumerate(n_):

            if n == 0:
                continue

            if n not in same_parameter:
                same_parameter[n] = []

            same_parameter[n].append(index)

        # 例如：
        # n_ = [0, 1, 1, 2, 0, 2]
        #
        # same_parameter =
        # {
        #     1: [1, 2],
        #     2: [3, 5]
        # }

        #######################################################################
        # 建立相等约束

        constraints = []

        for indices in same_parameter.values():

            if len(indices) == 1:
                continue

            index_1 = indices[0]

            for index_2 in indices[1:]:
                # 保证优化开始时，相同的值就已经相同
                initial_value[index_2] = initial_value[index_1]

                constraints.append({
                    'type': 'eq',
                    'fun': lambda x, index_1=index_1, index_2=index_2:
                    x[index_2] - x[index_1]
                })

            #######################################################################

        ######################################################################

        # for constraint in constraints:
        #     print('约束条件函数结果:', constraint)


        # 修改元件的编号， 修改参数的编号，
        goal = self.get_goal(match_lattice, adjust_element_num, adjust_parameter_num, NN)

        options = {'maxiter': 100, 'eps': 10 ** -1, 'ftol': 10 ** -4}


        # result = minimize(fun=goal, x0=initial_value, constraints=constraints, bounds=parameter_range,
        #                   method='SLSQP', options=options)
        #
        # return result.x, result.fun


        try:
            result = minimize(fun=goal, x0=initial_value, constraints=constraints, bounds=parameter_range,
                              method='SLSQP', options=options)

            return result.x, result.fun

        except Exception:
            return self.ini_this[-1], self.loss_this[-1]


    def change_latticae_with_opti_res(self,  opti_res_this, error_lattice,
                                 adjust_element_num, adjust_parameter_num):
        error_lattice = copy.deepcopy(error_lattice)


        v1 = 0
        for i_index, i_value in enumerate(adjust_element_num):
            for j_index, j_value in enumerate(adjust_parameter_num[i_index]):
                for com in error_lattice:
                    if com[-1] == f'element_{i_value}':
                        com[j_value] = opti_res_this[v1]
                        break
                v1 += 1

        return error_lattice

    def opti_one_time_different_group(self, lattice_mulp_list):
        print(572)
        #使用不同的族数进行优化
        """
        静态误差完整跑一次, 需要矫正

        :param group:
        :param time:hg
        :return:
        """
        lattice_mulp_list = copy.deepcopy(lattice_mulp_list)

        all_match_N = []
        all_set_N = []
        for i in lattice_mulp_list:
            if i[0].lower() == "match":
                all_match_N.append(int(i[1]))
            elif i[0].lower().startswith("set"):
                all_set_N.append(int(i[1]))

        common_N = list(set(all_match_N) & set(all_set_N))
        # print(591, common_N)
        # print(all_match_N)
        iteration_step = 0
        common_N = sorted(common_N)

        opti_res_this_dict = {}
        for i in common_N:
            NN = i
            t_lattice = copy.deepcopy(lattice_mulp_list)
            for j in t_lattice:
                if j[0].lower() == "match" and int(j[1]) != i:
                    j.append(False)

                if j[0].lower().startswith("set") and int(j[1]) != i:
                    j.append(False)


            t_lattice = [k for k in t_lattice if k[-1] is not False]



            # for i in t_lattice:
            #     print(i)
            # sys.exit()
            # 得到lattice的定位信息

            match_info = self.generate_match_parameter(t_lattice)

            # 返回 哪些元件需要修改， 优化的初始初始值， 哪些参数需要修改， ,每个参数的范围，关联值n，是否使用初值

            self.ini_this = []
            self.loss_this = []


            opti_res_this, loss_this = self.optimize_one_group(t_lattice,
                                                               match_info, NN)

            # # print(618, match_element_num, match_parameter_initial_value, match_parameter_num, match_parameter_range, \
            # #     match_parameter_n, match_parameter_use_init)
            # # print(620, opti_res_this)
            #
            match_element_num = []
            match_parameter_num = []
            #
            # #######################################################################
            # # 从match_info中提取数据
            # #包括修改的原件数，还有参数索引
            for element_num, info in match_info.items():
                match_element_num.append(element_num)
                match_parameter_num.append(info["parameter_num"])
            #
            #
            lattice_mulp_list = self.change_latticae_with_opti_res(opti_res_this, \
                                lattice_mulp_list, match_element_num, match_parameter_num)
            # for i1 in lattice_mulp_list:
            #     print(i1)

            v1 = 0
            for i_index, i_value in enumerate(match_element_num):
                for j_index, j_value in enumerate(match_parameter_num[i_index]):
                    opti_res_this_dict[f"{i_value}_{j_value}"] = opti_res_this[v1]
                    v1 += 1

        #对于所有族的loss
        all_loss = self.treat_set(None)
        # #返回矫正参数信息, 这一次优化的结果， 只一次优化的损失， 束诊结果
        return opti_res_this_dict, all_loss

if __name__ == "__main__":
    item = \
        {
            "project_path": r"F:\using\test_avas_qt\env_project_match",
            "field_path": r"F:\using\test_avas_qt\env_project_match\FieldFile",
            "match_sim_type": "env", #匹配时使用的match_type
        }
    obj = MatchWithConmmandalgorithm(item)

    lattice_path = r"F:\using\test_avas_qt\env_project_match\InputFile\lattice_mulp.txt"
    lattice_list, _ = read_lattice_mulp_with_name(lattice_path)


    res= obj.opti_one_time_different_group(lattice_list)