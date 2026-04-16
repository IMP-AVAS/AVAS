#此函数用来在模拟前对lattice进行检验，
from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name
from utils.exception import MissingcommandError
import global_varible
from utils.tool import delete_element_end_index, add_element_end_index
from utils.exception import BaseError
from utils.tool import can_convert_to_othertype, convert_to_othertype

element_length_dict = {
    "drift": 3, "field": 9, "quad": 4, "solenoid": 4,
    "bend": 7, "steer": 7, "edge": 9
}

command_min_length_dict = {
    "diag_position": 4, "diag_size": 4, "diag_energy": 3,
    "adjust": 5,
    'err_quad_ncpl_stat': 1, 'err_quad_ncpl_dyn': 1, 'err_cav_ncpl_stat': 1, 'err_cav_ncpl_dyn': 1,
    'err_quad_cpl_stat': 1, 'err_quad_cpl_dyn': 1, 'err_cav_cpl_stat': 1, 'err_cav_cpl_dyn': 1,
    "err_beam_dyn": 0, "lattice": 2, "lattice_end": 0, "superposeout": 6, "superposeend": 0,
    "err_step": 2,
    "superpose": 1, "start": 0, "end": 0,
    'err_quad_dyn_on': 0,
    'err_cav_dyn_on': 0,
    'err_quad_stat_on': 0,
    'err_cav_stat_on': 0,
    "err_beam_dyn_on": 0,
    "err_beam_stat_on": 0,

}

element_param_name_dict = {
    'drift': ['length', 'radius'],
    'field': ['length', 'radius', "plc", 'fieldType', 'frequency', 'Phase',
                                                        'ke', 'kb', 'fieldMap'],
    'quad': ['length', 'radius', 'plc', 'gradient'],
    "solenoid": ['length', 'radius', 'plc', 'gradient'],
    "bend" : ['length', 'radius', 'plc', "curvature Radius", "field gradient index",  "direction"],
    "steer": ['length', 'radius', "plc", r"bx\ex", r"by\ey", "type", "max_value"],
    "edge": ["plc", 'radius', "plc", "rotation angle", "Curvature radius", "Total gap of magnet",
            "k1", "k2", "direction"]
}
element_param_type_dict = {
    'drift': [float, float, float],
    'field': [float, float, float, int, float, float, float, float, str],
    'quad': [float, float, float, float],
    "solenoid": [float, float, float, float],
    "bend": [float, float, float, float, float, float, int],
    "steer": [float, float, float, float, float, int ,float],
    "edge": [float, float, float, float, float, float,
             float, float, int]
}

command_param_type_dict = {
    "diag_position": [float, float, float, float],
    "diag_size": [float, float, float, float],
    "diag_energy": [float, float, float],
    "adjust": [float, int, int, float, float, int],
    'err_quad_ncpl_stat': [int, int] + [float] * 7,
    'err_quad_ncpl_dyn': [int, int] + [float] * 7,
    'err_cav_ncpl_stat': [int, int] + [float] * 7,
    'err_cav_ncpl_dyn': [int, int] + [float] * 7,
    'err_quad_cpl_stat':  [int, int] + [float] * 7,
    'err_quad_cpl_dyn':  [int, int] + [float] * 7,
    'err_cav_cpl_stat':  [int, int] + [float] * 7,
    'err_cav_cpl_dyn':  [int, int] + [float] * 7,
    "err_beam_dyn": [int] + [float] * 12,
    "lattice": [int, int],
    "lattice_end": [], 
    "superposeout": [float] * 6,
    "superposeend": [],
    "err_step": [int, int],
    "superpose": [float],
    "start": [],
    "end": [],
    'err_quad_dyn_on': [int] * 7,
    'err_cav_dyn_on': [int] * 7,
    'err_quad_stat_on': [int] * 7,
    'err_cav_stat_on': [int] * 7,
    "err_beam_dyn_on": [int] * 13,
    "err_beam_stat_on": [int] * 13,
}

#该字典用于标记某些命令或元件的固定值选项
command_param_fixed_dict = {
    "adjust": {"e_6": [0, 1]},
    'err_quad_ncpl_stat': {"e_2": [0, 1, 2]},
    'err_quad_ncpl_dyn': {"e_2": [0, 1, 2]},
    'err_cav_ncpl_stat': {"e_2": [0, 1, 2]},
    'err_cav_ncpl_dyn': {"e_2": [0, 1, 2]},
    'err_quad_cpl_stat':  {"e_2": [0, 1, 2]},
    'err_quad_cpl_dyn':  {"e_2": [0, 1, 2]},
    'err_cav_cpl_stat':  {"e_2": [0, 1, 2]},
    'err_cav_cpl_dyn':  {"e_2": [0, 1, 2]},
    "err_beam_dyn": {"e_1": [0, 1, 2]},

    'err_quad_dyn_on': {f"e_{i}": [0, 1] for i in range(1, 8)},
    'err_cav_dyn_on': {f"e_{i}": [0, 1] for i in range(1, 8)},
    'err_quad_stat_on': {f"e_{i}": [0, 1] for i in range(1, 8)},
    'err_cav_stat_on': {f"e_{i}": [0, 1] for i in range(1, 8)},
    "err_beam_dyn_on": {f"e_{i}": [0, 1] for i in range(1, 14)},
    "err_beam_stat_on": {f"e_{i}": [0, 1] for i in range(1, 14)},
}
element_param_fixed_dict = {
    # 'field': {"e_4": [1, 3]},
    "bend": {"e_7": [0, 1]},
    "steer": {"e_6": [0,1]},
    "edge": {"e_9": [0, 1]},
}

class JudgeLattice():
    def __init__(self, lattice_mulp_path):
        self.lattice_mulp_path = lattice_mulp_path


    def common_inspect(self):
        pass
    def judge_dyn_error(self, lattice_mulp_list):
        pass
    def judge_stat_error(self, lattice_mulp_list):
        pass
    def judge_stat_dyn_error(self, lattice_mulp_list):
        pass

    def add_command_end_index(self, lattice_mulp_list):
        command_keys = list(command_min_length_dict.keys())
        index = 0
        for i in lattice_mulp_list:
            if i[0] in command_keys:
                i.append(f"command_{index}")
                index += 1
        return lattice_mulp_list

    def test_convert(self, list1, list2):
        if len(list1) > len(list2):
            list1 = list1[0: len(list2)]
        res = [can_convert_to_othertype(list1[i], list2[i]) for i in range(len(list1))]
        return res

    def convert_param_type(self, list1, list2):
        if len(list1) > len(list2):
            list1 = list1[0: len(list2)]
        res = [convert_to_othertype(list1[i], list2[i]) for i in range(len(list1))]
        return res

    def chexck_superposeend(self, lis, i):
        element_lis = ['drift', 'field', 'quad', 'bend', 'steer', 'edge']
        diag_list = ['DIAG_CURRENT'.lower(), 'DIAG_SIZE'.lower(), 'DIAG_POSITION'.lower(), "DIAG_PHASE".lower()]

        sup_before = False
        sup_after = False
        if lis[i][0].lower() not in element_lis:
            return False


        elif lis[i][0].lower() in element_lis:

            for ele in lis[:i][::-1]:
                if len(ele) == 0:
                    pass
                elif ele[0].lower() == "superpose":
                    sup_before = True
                elif ele[0].lower() in element_lis or ele[0].lower() in diag_list or ele[0].lower() == "start":
                    break

            for ele in lis[i + 1:]:
                if len(ele) == 0:
                    pass
                elif ele[0].lower() == "superposeend" or ele[0].lower() == "superposeout" or\
                    ele[0].lower() == "superpose":

                    sup_after = True

                elif ele[0].lower() in element_lis or ele[0].lower() in diag_list or ele[0].lower() == "end":
                    break
        if sup_before is True and sup_after is False:
            return True
        else:
            return False

    def judge_base_element_command(self, lattice_mulp_list):
        #1. 先检查start ，end
        #2. 检查长度
        #3. 检查类大型
        #4. 检测叠加场
        #4. 检测固定值
        base_error = BaseError()

        if len(lattice_mulp_list) == 0:
            return True

        # 检查start和end
        all_command = [i[0] for i in lattice_mulp_list]
        if all_command[-1] != "end":
            base_error.miss_end_error()
        if all_command[0] != "start":
            base_error.miss_start_error()



        #在最后边添加索引
        lattice_mulp_list_with_index = add_element_end_index(lattice_mulp_list)
        lattice_mulp_list_with_index = self.add_command_end_index(lattice_mulp_list_with_index)
        element_length_keys = list(element_length_dict.keys())
        command_min_length_keys = list(command_min_length_dict.keys())


        for index, i in enumerate(lattice_mulp_list_with_index):
            #检测长度
            if i[0] in element_length_keys and len(i) != (element_length_dict[i[0]] + 2):
                base_error.element_length_error(i)

            elif i[0] in command_min_length_keys and len(i) < (command_min_length_dict[i[0]] + 2):
                base_error.command_length_error(i)

            #检测类型
            if i[0] in element_length_keys:
                command = i[1:-1]
                target_type = element_param_type_dict[i[0]]
                res = self.test_convert(command, target_type)
                if all(res):
                    #说明这个元件没有问题
                    new_type_command = self.convert_param_type(command, target_type)
                    pass
                else:
                    error_param_index = res.index(False)
                    base_error.element_length_error(i)

            elif i[0] in command_min_length_keys:
                command = i[1:-1]
                target_type = command_param_type_dict[i[0]]
                res = self.test_convert(command, target_type)
                if all(res):
                    #说明这个命令没有问题
                    new_type_command = self.convert_param_type(command, target_type)
                    pass
                else:
                    base_error.command_length_error(i)

            #将改变类型后的赋值
            i = [i[0]] + new_type_command + [i[-1]]

            #检测叠加场
            if i[0] in element_length_keys:
                superpose_condition = self.chexck_superposeend(lattice_mulp_list_with_index, index)
                if superpose_condition:
                    base_error.miss_superposeend_error(i)

            #检查固定值
            command_param_fixed_dict_keys = list(command_param_fixed_dict.keys())
            element_param_fixed_dict_keys = list(element_param_fixed_dict.keys())
            if i[0] in element_param_fixed_dict_keys:
                for k, v in element_param_fixed_dict[i[0]].items():
                    param_index = int(k.split("_")[1])
                    if i[param_index] not in v:
                        base_error.fix_value_error(i, param_index, v)

            elif i[0] in command_param_fixed_dict_keys:
                for k, v in command_param_fixed_dict[i[0]].items():
                    param_index = int(k.split("_")[1])
                    if param_index > len(i)-2:
                        break
                    if i[param_index] not in v:
                        base_error.fix_value_error(i, param_index, v)


        # elifm
    def judge_lattice(self, mode):
        lattice_mulp_list, _ = read_lattice_mulp_with_name(self.lattice_mulp_path)
        self.judge_base_element_command(lattice_mulp_list)

        if mode == "err_dyn":
            pass

        # sim_mode = [
        # "stat_error", "dyn_error", "stat_dyn_error",
        # ]

        # if sim_mode == "dyn_error":
        #     self.judge_dyn_error(lattice_mulp_list)
        #
        # if sim_mode == "dyn_error":
        #     self.judge_stat_error(lattice_mulp_list)
        # if sim_mode == "stat_dyn_error":
        #     self.judge_stat_dyn_error(lattice_mulp_list)


if __name__ == '__main__':
    lattice_mulp_path = r"C:\Users\anxin\Desktop\test_shao2\InputFile\lattice_mulp.txt"
    v = JudgeLattice(lattice_mulp_path)
    res = v.judge_lattice(1)
    print(res)