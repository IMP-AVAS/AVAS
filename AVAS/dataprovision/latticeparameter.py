import copy
import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

from utils.readfile import read_txt, read_lattice_mulp_with_name
import global_varible
from utils.tool import add_element_end_index, judge_command_on_element

from utils.tool import write_to_txt, calculate_mean, calculate_rms, add_to_txt
from utils.tool import add_element_end_index, judge_command_under_element, write_to_txt, calculate_mean, calculate_rms, add_to_txt
import numpy as np
import logging
from logger.logger_config import setup_logger
logger = logging.getLogger(__name__)


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

    def get_superpose_range(lattice, start_name):
        """
        从某个superpose开始，到superposeend结束
        """

        block = []
        inside = False

        for item in lattice:

            if item[0] == "superpose" and item[-1] == start_name:
                inside = True

            if inside:
                block.append(item)

            if inside and item[0] == "superposeend":
                break

        return block

    def get_parameter(self, lattice_list = None):
        #通常的情况，用于获取长度等
        if not lattice_list:
            lattice_info_ini, lattice_info_name = read_lattice_mulp_with_name(self.lattice_path)
        elif lattice_list:
            lattice_info_ini = copy.deepcopy(lattice_list)

        # lattice_info_ini, lattice_info_name = read_lattice_mulp_with_name(self.lattice_path)

        #给原件和suppose分别加索引
        lattice_info_ini = add_element_end_index(lattice_info_ini)
        index = 0
        for i in lattice_info_ini:
            if i[0].startswith("superpose"):
                i.append(f"superpose_{index}")
                index += 1
        ##########################################

        lattice_info_before_end = []
        for i in lattice_info_ini:
            lattice_info_before_end.append(i)
            if i[0] == 'end':
                break

        use_commands = (global_varible.mulp_element + ['superpose', 'superposeend', "superposeout"] + ['lattice', 'lattice_end'] +
                        ['end'])



        lattice_info = [i for i in lattice_info_before_end if i[0] in use_commands]


        # for i in lattice_info:
        #     if i[0] in global_varible.control_diag_element:
        #         i[1] = 0

        start = 0  # 每个元件的起点
        length = 0  # 每个元件的长度

        #分两种情况计算
        #不考虑叠加场，只是把

        ele_inex= 0
        self.v_index = []

        for i in lattice_info:
            if i[0] in global_varible.all_element:

                length = float(i[1])
                self.v_len.append(length)  #每个原件的长度
                self.v_name.append(i[0]) #每个原件的名字
                self.v_index.append(ele_inex)
                ele_inex += 1

        #考虑叠加长，把叠加场的信息加进来
        #判断叠加场在哪个原件上面，哪个原件下面，确定叠加场中原件的数量

        # for i in lattice_info:
        #     print(i)

        #每个叠加场
        ############################################################################
        self.sup_field_list = [] #理想的模式是 【{起点原件， 终点原件}， {}， {}】

        this_sup_start_index = None
        this_sup_end_index = None
        sup_field_index = 0

        for i in lattice_info:
            if this_sup_start_index is None:
                if i[0] == "superpose":
                    this_sup_start_index = lattice_info.index(i)
            if this_sup_end_index is None:
                if i[0] == "superposeend":
                    this_sup_end_index = lattice_info.index(i)

            if this_sup_start_index and this_sup_end_index:
                sup_field_dict = {}

                sup_field_dict["start_index"] = {}
                sup_field_dict["end_index"] = {}

                sup_lattice_list = lattice_info[this_sup_start_index:this_sup_end_index]

                every_ele_end_distance = [] #记录每一个原价的终点
                eyery_ele_index = [] #记录每一个原件的index

                for index, i  in enumerate(sup_lattice_list):
                    if i[0] in global_varible.mulp_element:

                        end_distance = float(i[1]) + float(sup_lattice_list[index-1][1])
                        every_ele_end_distance.append(end_distance)
                        eyery_ele_index.append(int(i[-1].split("_")[-1]))
                sup_field_index += 1
                sup_field_dict["start_index"] = eyery_ele_index[0]
                sup_field_dict["end_index"] = eyery_ele_index[-1]   #end_index代表的是
                sup_field_dict["sup_length"] = np.max(every_ele_end_distance)
                sup_field_dict["sup_field_index"] = f"sup_field_{sup_field_index}"

                self.sup_field_list.append(sup_field_dict)

                this_sup_start_index = None
                this_sup_end_index = None

        #[{'start_index': 1, 'end_index': 10, 'sup_length': np.float64(1.13623)}, {'start_index': 18, 'end_index': 27, 'sup_length': np.float64(1.13604)}]


        if len(self.sup_field_list) != 0: #如果确实存在叠加场
            self.v_len_with_sup = copy.deepcopy(self.v_len)
            self.v_name_with_sup = copy.deepcopy(self.v_name)
            self.v_index_with_sup = copy.deepcopy(self.v_index) #如果有叠加场，其实是最后一个原件的索引
            for i in reversed(self.sup_field_list):
                self.v_len_with_sup[i["start_index"]:i["end_index"] + 1] = [i["sup_length"]]
                self.v_name_with_sup[i["start_index"]:i["end_index"] + 1] = [i["sup_field_index"]]
                self.v_index_with_sup[i["start_index"]:i["end_index"] + 1] = [i["end_index"]]

            # print("sup_field_list", self.sup_field_list)
            # print("self.v_len_with_sup", self.v_len_with_sup)  #每个原件的长度
            # print("self.v_name_with_sup", self.v_name_with_sup)
            # print("self.v_index_with_sup", self.v_index_with_sup)

        elif len(self.sup_field_list) == 0:  # 如果不存在叠加场

            self.v_len_with_sup = copy.deepcopy(self.v_len)
            self.v_name_with_sup = copy.deepcopy(self.v_name)
            self.v_index_with_sup = copy.deepcopy(self.v_index)

        # self.sup_field_list
        # self.v_len_with_sup
        # self.v_name_with_sup
        #  self.v_index_with_sup
        self.v_end_with_sup = np.cumsum(self.v_len_with_sup)
        self.v_start_with_sup = np.cumsum([0] + self.v_len_with_sup[:-1])

        # print("self.sup_field_list", self.sup_field_list)
        # print("self.v_len_with_sup", self.v_len_with_sup)  #每个原件的长度
        # print("self.v_name_with_sup", self.v_name_with_sup)
        # print("self.v_index_with_sup", self.v_index_with_sup)

        #添加同步相位
        for i in lattice_info:
            if i[0] == 'field' and i[4] == '1':
                self.phi_syn.append(float(i[6]))
            elif i[0] in global_varible.all_element:
                self.phi_syn.append(0)

        for i in lattice_info:
            if i[0] in global_varible.all_element:
                self.aperture.append(float(i[2]))

        self.total_length = self.v_end_with_sup[-1]

        self.lattice_info =lattice_info



    #该函数的功能是为了获取每个周期的开始和结束
    def get_period(self, lattice_list = None):
        self.get_parameter(lattice_list)

        #在这里使用的命令
        this_commands = global_varible.mulp_element + ['lattice', 'lattice_end']

        new_lattice_list = [i for i in self.lattice_info if i[0] in this_commands]

        new_lattice_list = add_element_end_index(new_lattice_list)

        #给lattice和lattice_end添加索引
        lattice_start_index = 0
        lattice_end_index = 0
        for i in new_lattice_list:
            if i[0] == "lattice":
                i.append(f"lattice_{lattice_start_index}")
                lattice_start_index += 1
            elif i[0] == "lattice_end":
                i.append(f"lattice_end_{lattice_end_index}")
                lattice_end_index += 1


        #判断每个lattice 和lattice_end 在那些原件上
        lattice_on_element_list = []

        lattice_start = None
        lattice_end = None
        for i in new_lattice_list:
            if lattice_start is None:
                if i[0] == "lattice":
                    lattice_start = judge_command_on_element(new_lattice_list, i)
                    this_small_period = int(i[1]) #大周期内每个小周期的数量
            elif lattice_end is None:
                if i[0] == "lattice_end":
                    lattice_end = judge_command_on_element(new_lattice_list, i)
                    #如果是最后一个lattice_end在end上面
                    if lattice_end == -1:
                        lattice_end = self.v_index_with_sup[-1]


            if lattice_start is not None and lattice_end is not None:
                lattice_on_element_list.append([lattice_start, lattice_end, this_small_period])
                lattice_start = None
                lattice_end = None

        logger.info(lattice_on_element_list)
        self.v_start_end = []
        #这里采取的是如果, 凑不够这么多原件，最后的几个原件就不计算了

        for i in lattice_on_element_list:
            start, end, step = i

            points = list(range(start, end + 1, step))

            every_small_period = [
                (points[i], points[i + 1]-1)
                for i in range(len(points) - 1)
            ]

            logger.info(every_small_period)

            for j in every_small_period:
                # 查找末尾原件的索引
                end_list_index = self.v_index_with_sup.index(j[1])

                if end_list_index is None:
                    #如果原件的出口找不到，目前可能的原因为
                    #1. 周期的结束不在叠加场的出口，而是在叠加场内部
                    raise Exception("The period setting is incorrect.")

                end_distance = self.v_end_with_sup[end_list_index]

                logger.info(self.v_name_with_sup[end_list_index])

                if self.v_name_with_sup[end_list_index].startswith("sup"):
                    #如果出口原件是叠加场，那么入口只能用叠加场前面原件（也就是end_list_index -1 ）的出口作为入口

                    #如果叠加长作为第一个原件
                    if end_list_index == 0 :
                        start_distance = 0
                    else:
                        start_distance = self.v_end_with_sup[end_list_index-1]
                else:
                    #如果不是叠加场，那么就找到第一个原件对应的索引

                    start_index = self.v_index_with_sup.index(j[0])

                    start_distance = self.v_start_with_sup[ start_index ]

                self.v_start_end.append([start_distance, end_distance])

        # print(279, self.v_start_end)
        return self.v_start_end








if __name__ == "__main__":
    setup_logger(
        level=logging.INFO,
    )


    #C:\Users\anxin\Desktop\AVAS_control\dataprovision\latticeparameter.py
    lattice_path = r"C:\Users\wangh\Desktop\field_ciads\InputFile\lattice_mulp.txt"
    res = LatticeParameter(lattice_path)
    res.get_parameter()
    print(res.total_length)
    # res.get_period()
    # print(res.total_length)
    # print(res.v_len)
    # res.get_period()
    # print(res.total_length)
    # print(res.v_start)
    # print(res.v_len)

    # res.get_total_length()