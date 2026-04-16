
import os
import copy
import sys
import re


def read_txt(input, out='dict', readdall=None, case_sensitive=None):
    """
    :param input: 需要读取的txt文件
    :out:结果返回的类型，可选参数为dict， list
    :return:{}or[]
    注意：当输出为字典格式的时候，文件中存在相同key会出现覆盖的情况
    """
    if not os.path.exists(input):
        raise Exception("文件不存在")

    with open(input, encoding='UTF-8') as file_object:
        input_lines = []
        if not readdall:
            for line in file_object:
                line = line.lstrip('\ufeff')
                line = line.strip()
                if '!' in line:
                    # 如果当前行包含感叹号，只保留感叹号之前的内容
                    line = line.split('!', 1)[0]
                    input_lines.append(line)
                    continue  # 跳出循环，停止读取接下来的内容
                else:
                    input_lines.append(line)
        elif readdall:
            for line in file_object:
                line = line.lstrip('\ufeff')
                line = line.strip()
                input_lines.append(line)


    input_lines = [i.split() if i.strip() else [] for i in input_lines]

    if not case_sensitive:
        #如果大小写不敏感，全都变成小写，如果敏感
        input_lines = [[word.lower() for word in line] for line in input_lines]

    # for i in input_lines:
    #     if i[0] == 'bend':
    #         i[1] == float(i[4]/180) * float(i[5])

    if out == 'list':
        return input_lines


    res = {}
    for i in input_lines:
        tmp_dict = {}
        if len(i) == 1:
            res[i[0]] = None
        elif len(i) == 2:
            res[i[0]] = i[1]
        else:
            res[i[0]] = i[1:]
    return res

# if os.path.exists(file_path):
#     os.remove(file_path)
#     print("文件已删除")
# else:
#     print("文件不存在")
# def read_tracewin(in_put):
#
#     with open(in_put, encoding='utf-8') as file_object:
#         lines = file_object.readlines()
#
#     tracewin_list = []
#
#     for line in lines:
#         lst = line.split()
#         tracewin_list.append(lst)
#
#     return tracewin_list

def read_tracewin(in_put):

    with open(in_put, encoding='utf-8') as file_object:
        lines = file_object.readlines()

    tracewin_list = []

    for line in lines:
        lst = line
        if lst[0] == ";":
            new_command = [lst]
        elif line != "":
            new_command = line.split(";", 1)[0].split()
        elif line == "":
            new_command = []


        tracewin_list.append(new_command)

    return tracewin_list


def chexck_superposeend(lis, i):
    element_lis = ['drift', 'field_map', 'quad', 'bend', 'thin_steer', 'edge']
    diag_list = ['DIAG_CURRENT'.lower(), 'DIAG_SIZE'.lower(), 'DIAG_POSITION'.lower(),  "DIAG_PHASE".lower()]

    sup_before = False
    sup_after = False
    if lis[i][0].lower() not in element_lis:
        return False


    elif lis[i][0].lower() in element_lis:

        for ele in lis[:i][::-1]:
            if len(ele) == 0:
                pass
            elif ele[0].lower() == "superpose_map":
                sup_before = True
            elif ele[0].lower() in element_lis or ele[0].lower() in diag_list:
                break

        for ele in lis[i+1:]:
            if len(ele) == 0:
                pass
            elif ele[0].lower() == "superpose_map":
                sup_after = True
            elif ele[0].lower() in element_lis or ele[0].lower() in diag_list:
                break
    if sup_before is True and sup_after is False:
        return True
    else:
        return False

def tran_tracewin_avas(tracewin_list):


    avas_list =[['start']]
    no_identify_list = []


    pass_list = ['SHIFT_IN_FIELD_MAP'.lower(), "SHIFT_BEAM".lower(),
                'SET_SYNC_PHASE'.lower(),  'ADJUST'.lower(), "DIAG_PHASE".lower(),
                "PLOT_DST_LOST".lower(),
                ]
    diag_list = ['DIAG_CURRENT'.lower(), 'DIAG_SIZE'.lower(), 'DIAG_POSITION'.lower(),  "DIAG_PHASE".lower()]

    freq = 0
    for index, stat in enumerate(tracewin_list):

        if len(stat) == 0:
            avas_list.append([])

        elif stat[0][0] == ";":
            stat[0] = "!" + stat[0][1:]
            avas_list.append(stat)

        elif stat[0].lower() == "freq":
            freq = float(stat[1])*10**6

        elif stat[0].lower() == "drift":
            tmp = [stat[0].lower(), float(stat[1])/1000, float(stat[2])/1000, 0]
            avas_list.append(tmp)
            
            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])

        elif stat[0].lower() == "superpose_map":

            tmp = ["superpose", float(stat[1])/1000, float(stat[2])/1000, float(stat[3])/1000, stat[4], stat[5], stat[6] ]
            avas_list.append(tmp)

        elif stat[0].lower() == 'FIELD_MAP'.lower():
            if int(stat[1]) == 7:
                #静电场
                tmp = ["field", float(stat[2])/1000,float(stat[4])/1000, 0, 2, 0, 0, stat[6], 0, stat[9]]

            elif int(stat[1]) == 70:
                tmp = ["field", float(stat[2])/1000, float(stat[4])/1000,0, 3, 0, 0,   0, stat[5], stat[9]]

            elif int(stat[1]) == 7700:
                tmp = ["field", float(stat[2])/1000,float(stat[4])/1000, 0, 1, freq, stat[3], stat[6],stat[5], stat[9]]

            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])


        elif stat[0].lower() == "QUAD".lower():
            tmp = ['quad', float(stat[1])/1000, float(stat[3])/1000, 0, float(stat[2])]
            if tmp[4] == 0:
                tmp = ["drift", float(stat[1])/1000, float(stat[3])/1000, 0 ]


            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])

        elif stat[0].lower() == "SOLENOID".lower():
            tmp = ['solenoid', float(stat[1])/1000, float(stat[3])/1000, 0, float(stat[2])]
            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])

        elif stat[0].lower() == "BEND".lower():
            # tmp = ['bend', 0,  float(stat[4])/1000, 0, float(stat[1]), float(stat[2])/1000,  , int(stat[5])]
            tmp = ['bend', 0,  float(stat[4])/1000, 0, float(stat[1]), float(stat[2])/1000, float(stat[3]), int(stat[5])]
            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])

        elif stat[0].lower() == "THIN_STEERING".lower():

            tmp = ['steerer', 0,  float(stat[3])/1000, 0,  float(stat[1]), float(stat[2]), int(stat[4]), 100]
            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])

        elif stat[0].lower() == "edge" :
            tmp = ['edge', 0,  float(stat[6])/1000, 0,  float(stat[1]), float(stat[2])/1000, float(stat[3])/1000, float(stat[4]), float(stat[5]), int(stat[7]) ]
            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                 avas_list.append(["superposeend"])

        elif stat[0].lower() == "repeat_ele".lower():
            tmp = stat
            avas_list.append(stat)

        elif stat[0].lower() == "end":
            tmp =stat
            avas_list.append(stat)

        elif stat[0].lower() in diag_list:
            tmp = ["diag_size",0, 0, 0 ,0 ]
            avas_list.append(tmp)

        elif stat[0].lower() == "lattice":
            tmp = stat
            avas_list.append(stat)

        elif stat[0].lower() == "lattice_end":
            tmp = stat
            avas_list.append(stat)



        elif stat[0].lower() in pass_list:
            pass

        else:
            print("未识别命令", stat)
            pass


    #删除带repeat的空格
    avas_list = delete_repeat_space(avas_list)

    avas_list2 = []
    #解决元件重复命令
    for i in range(len(avas_list)):
        if len(avas_list[i]) == 0:
            avas_list2.append([])

        elif avas_list[i][0].lower() == "repeat_ele":
            avas_list2.append(["!repeat"])
            for _ in range(int(avas_list[i][1]) - 1):
                avas_list2.append(list(avas_list[i+1]))

        else:
            avas_list2.append(avas_list[i])
    return avas_list2


def delete_repeat_space(lis):
    lis = copy.deepcopy(lis)

    v = False
    for index in range(len(lis) - 1):  # 
        if len(lis[index]) > 0 and lis[index][0].lower() == "repeat_ele" and len(lis[index+1]) == 0:
            del lis[index + 1]
            v = True
            break

    # for i in lis:
    #     print(i)
    # print("------------------------------")
    # breakpoint()

    if v is False:
        return lis
    else:
        return delete_repeat_space(lis)  # 递归调用，但只在有修改时调用



def write_to_avas_lattice(new_avaslattice, avas_lattice_path):
    with open(avas_lattice_path, 'w', encoding='UTF-8' ) as file_object:
        for i in new_avaslattice:
            tmp_s = " ".join(map(str, i))
            file_object.write(tmp_s+"\n")



if __name__ == "__main__":
    tracewin_lattiace_path = r"C:\Users\shliu\Desktop\双束模拟\tr.txt"
    avas_lattice_path = r"C:\Users\shliu\Desktop\双束模拟\av.txt"

    # 修改后的lattice

    tracewin_lattice = read_tracewin(tracewin_lattiace_path)

    # for i in tracewin_lattice:
    #     if len(i) > 1:
    #         if i[0].lower() == "drift":
    #             print(i)

    avas_lattice_list = tran_tracewin_avas(tracewin_lattice)

    write_to_avas_lattice(avas_lattice_list, avas_lattice_path)