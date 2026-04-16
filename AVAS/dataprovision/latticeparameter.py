import copy
import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

from utils.readfile import read_txt, read_lattice_mulp_with_name
import global_varible
from utils.tool import add_element_end_index, judge_command_on_element


#得到 lattice的基本信息
class LatticeParameter():
    """
    对lattice文件进行解析
    """
    def __init__(self, lattice_mulp_path=None):
        """
        self.v_start_end: 每个周期的起点和终点
        self.v_start: 每个元件的起点
        self.v_len: 每个元件的长度
        self.v_name: 每个元件的名字
        """
        self.lattice_path =lattice_mulp_path
        self.v_start = [] #每个原件的起点
        self.v_len = []   #每个原件的长度
        self.v_start_end = []   #每个周期的起点和终点
        self.v_name = []
        self.phi_syn = []
        self.aperture = []
        self.total_length = 0

    def get_parameter(self, lattice_list = None):
        #通常的情况，用于获取长度等
        if not lattice_list:
            lattice_info_ini, lattice_info_name = read_lattice_mulp_with_name(self.lattice_path)
        elif lattice_list:
            lattice_info_ini = copy.deepcopy(lattice_list)

        # lattice_info_ini, lattice_info_name = read_lattice_mulp_with_name(self.lattice_path)

        lattice_info_before_end = []
        for i in lattice_info_ini:
            lattice_info_before_end.append(i)
            if i[0] == 'end':
                break

        use_commands = (global_varible.mulpud_element + ['superpose', 'superposeend', "superposeout"] + ['lattice', 'lattice_end'] +
                        ['end'] + global_varible.control_diag_element)



        lattice_info = [i for i in lattice_info_before_end if i[0] in use_commands]

        for i in lattice_info:
            if i[0] in global_varible.control_diag_element:
                i[1] = 0

        start = 0  # 每个元件的起点
        length = 0  # 每个元件的长度

        for i, line in enumerate(lattice_info):

            if line[0] in global_varible.all_element:
                if lattice_info[i - 1][0] == "superpose":
                    pass
                else:
                    self.v_start.append(start)
                    length = float(line[1])
                    self.v_len.append(length)
                    self.v_name.append(line[0])
                    start = start + length

            elif line[0] == "superpose":
                if lattice_info[i + 2][0] == "superpose":
                    self.v_start.append(start)

                    length = float(lattice_info[i + 2][1]) - float(line[1])
                    self.v_len.append(length)

                    self.v_name.append(lattice_info[i + 1][0])

                    start = start + length



                elif lattice_info[i + 2][0] == "superposeend" or lattice_info[i + 2][0] == "superposeout":

                    self.v_start.append(start)

                    length = float((lattice_info[i + 1][1]))

                    self.v_len.append(length)
                    self.v_name.append(lattice_info[i + 1][0])

                    start = start + length


        #添加同步相位
        for i in lattice_info:
            if i[0] == 'field' and i[4] == '1':
                self.phi_syn.append(float(i[6]))
            elif i[0] in global_varible.all_element:
                self.phi_syn.append(0)

        for i in lattice_info:
            if i[0] in global_varible.all_element:
                self.aperture.append(float(i[2]))

        self.total_length = self.v_start[-1] + self.v_len[-1]

        self.lattice_info =lattice_info

    def get_period(self, lattice_list = None):
        self.get_parameter(lattice_list)

        #1. 确定束诊原件的序号，指在所有原件中的, 不包含命令
        diag_element_index = []
        element_index = 0
        for index, line in enumerate(self.lattice_info):
            if line[0] in global_varible.control_diag_element:
                diag_element_index.append(element_index)

            if line[0] in global_varible.all_element:
                element_index += 1



        new_v_len = [item for i, item in enumerate(self.v_len) if i not in diag_element_index]
        new_v_start = [item for i, item in enumerate(self.v_start) if i not in diag_element_index]


        this_commands = global_varible.mulpud_element + ['lattice', 'lattice_end']



        new_lattice_list = [i for i in self.lattice_info if i[0] in this_commands]
        # for i in new_lattice_list:
        #     print(i)

        # period_all = []
        # period_every = []
        # for i in new_lattice_list:
        #     if i[0] == 'lattice':
        #         num_one_period = int(line[1])
        #         in_lattice = True
        #
        #     elif line[0] == 'lattice_end':
        #         in_lattice = False


        new_lattice_list = add_element_end_index(new_lattice_list)

        lattice_start_index = 0
        lattice_end_index = 0
        for i in new_lattice_list:
            if i[0] == "lattice":
                i.append(f"lattice_{lattice_start_index}")
                lattice_start_index += 1
            elif i[0] == "lattice_end":
                i.append(f"lattice_end_{lattice_end_index}")
                lattice_end_index += 1
        # for i in new_lattice_list:
        #     print(i)


        period_all = []
        in_lattice = False

        for line in new_lattice_list:
            if line[0] == 'lattice':
                in_lattice = True
                period_size = int(line[1])  # lattice X Y -> X 是每个周期的行数
                period_start =judge_command_on_element(new_lattice_list, line)

            elif line[0] == 'lattice_end':
                perirod_end = judge_command_on_element(new_lattice_list, line)
                if perirod_end == -1:
                    perirod_end = len(new_v_start)
                if in_lattice is False:
                    raise Exception("This lattice_end command is missing the corresponding lattice command.")

                if in_lattice is True:

                    if (perirod_end - period_start) % period_size != 0:
                        print(period_start, perirod_end)
                        raise Exception("This lattice cannot be divided into an integer number of periods.")

                    for i in range(period_start, perirod_end, period_size):
                        chunk = [i, i + period_size-1]
                        period_all.append(chunk)

                in_lattice = False


        self.v_start_end = []

        for i in period_all:
            v_start_end_every = []
            v_start_end_every.append(new_v_start[i[0]])
            v_start_end_every.append(new_v_start[i[1]] + new_v_len[i[1]])
            self.v_start_end.append(v_start_end_every)

        # if v_p[i] != 0:
        #     #包含一个周期的起点和终点
        #     v_start_end_every = []
        #     num_one_period = v_p[i]
        #     index_ = num_one_period - 1
        #     v_start_end_every.append(self.v_start[i])
        #
        #     index_end = i + num_one_period - 1
        #
        #     v_start_end_every.append(self.v_start[index_end] + self.v_len[index_end])
        #     self.v_start_end.append(v_start_end_every)
        # print(period_all)
        #
        #         # if in_lattice is True:
        #         #     # 对 current_period 分组
        #         #     for i in range(0, len(current_period), period_size):
        #         #         chunk = current_period[i:i + period_size]
        #         #         periods.append(chunk)
        #         #     in_lattice = False
        #         #     current_period = []
        #         #     continue
        #         #
        #         # if in_lattice:
        #         #     current_period.append(line)
        #
        #
        #
        #
        # pass



    # def get_parameter(self, lattice_list=None):
    #     if not lattice_list:
    #         lattice_info_ini, lattice_info_name = read_lattice_mulp_with_name(self.lattice_path)
    #     elif lattice_list:
    #         lattice_info_ini = copy.deepcopy(lattice_list)
    #
    #     lattice_info_before_end = []
    #     for i in lattice_info_ini:
    #         lattice_info_before_end.append(i)
    #         if i[0] == 'end':
    #             break
    #
    #     use_commands = (global_varible.mulpud_element + ['superpose', 'superposeend'] + ['lattice', 'lattice_end'] +
    #                     ['end'] + global_varible.control_diag_element)
    #
    #
    #
    #     lattice_info = [i for i in lattice_info_before_end if i[0] in use_commands]
    #
    #     for i in lattice_info:
    #         if i[0] in global_varible.control_diag_element:
    #             i[1] = 0
    #
    #
    #     in_lattice = False
    #
    #     start = 0  # 每个元件的起点
    #     length = 0  # 每个元件的长度
    #
    #
    #     v_p = []  # 记录周期
    #
    #     for i, line in enumerate(lattice_info):
    #         if line[0] == 'lattice':
    #             num_one_period = int(line[1])
    #             in_lattice = True
    #
    #         elif line[0] == 'lattice_end':
    #             in_lattice = False
    #
    #         # 不在周期
    #         if line[0] in global_varible.all_element:
    #
    #             if lattice_info[i - 1][0] == "superpose":
    #                 pass
    #             else:
    #                 self.v_start.append(start)
    #
    #                 length = float(line[1])
    #                 self.v_len.append(length)
    #
    #                 self.v_name.append(line[0])
    #
    #                 start = start + length
    #
    #                 if in_lattice:
    #                     v_p.append(num_one_period)
    #                 else:
    #                     v_p.append(0)
    #
    #
    #         elif line[0] == "superpose":
    #             if lattice_info[i + 2][0] == "superpose":
    #                 self.v_start.append(start)
    #
    #                 length = float(lattice_info[i + 2][1]) - float(line[1])
    #                 self.v_len.append(length)
    #
    #                 self.v_name.append(lattice_info[i + 1][0])
    #
    #                 start = start + length
    #
    #                 if in_lattice:
    #                     v_p.append(num_one_period)
    #                 else:
    #                     v_p.append(0)
    #
    #             elif lattice_info[i + 2][0] == "superposeend":
    #
    #                 self.v_start.append(start)
    #
    #                 length = float((lattice_info[i + 1][1]))
    #
    #                 self.v_len.append(length)
    #                 self.v_name.append(lattice_info[i + 1][0])
    #
    #                 start = start + length
    #
    #                 if in_lattice:
    #                     v_p.append(num_one_period)
    #                 else:
    #                     v_p.append(0)
    #
    #
    #     # print(self.v_start, len(self.v_start))
    #     # print(self.v_len, len(self.v_len))
    #     # print( v_p, len(v_p))
    #
    #     # print(self.v_start)
    #     # print(len(self.v_start))
    #     # print(len(v_p))
    #     index_ = 0
    #     for i in range(len(self.v_start)):
    #
    #         if index_ > 0:
    #             index_ = index_ - 1
    #             continue
    #
    #         if v_p[i] != 0:
    #             #包含一个周期的起点和终点
    #             v_start_end_every = []
    #             num_one_period = v_p[i]
    #             index_ = num_one_period - 1
    #             v_start_end_every.append(self.v_start[i])
    #
    #             index_end = i + num_one_period - 1
    #
    #             v_start_end_every.append(self.v_start[index_end] + self.v_len[index_end])
    #             self.v_start_end.append(v_start_end_every)
    #
    #     #添加同步相位
    #     for i in lattice_info:
    #         if i[0] == 'field' and i[4] == '1':
    #             self.phi_syn.append(float(i[6]))
    #         elif i[0] in global_varible.all_element:
    #             self.phi_syn.append(0)
    #
    #     for i in lattice_info:
    #         if i[0] in global_varible.all_element:
    #             self.aperture.append(float(i[2]))
    #
    #     self.total_length = self.v_start[-1] + self.v_len[-1]



if __name__ == "__main__":
    #C:\Users\anxin\Desktop\AVAS_control\dataprovision\latticeparameter.py
    lattice_path = r"C:\Users\shliu\Desktop\hpc_test\cafe2\InputFile\lattice_mulp.txt"
    res = LatticeParameter(lattice_path)
    res.get_parameter()
    print(res.total_length)
    # print(res.v_len)
    # res.get_period()
    # print(res.total_length)
    # print(res.v_start)
    # print(res.v_len)

    # res.get_total_length()