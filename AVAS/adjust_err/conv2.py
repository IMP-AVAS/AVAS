
import os
import copy
import sys
import re
os.chdir(sys.path[0])

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
def read_tracewin(in_put):

    with open(in_put, encoding='utf-8') as file_object:
        lines = file_object.readlines()



    tracewin_list = []

    for line in lines:
        lst = line.split()
        tracewin_list.append(lst)

    # tracewin_list = [[word.lower() for word in line] for line in tracewin_list]

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
                'SET_SYNC_PHASE'.lower(), 'lattice', 'lattice_end', 'ADJUST'.lower(), "DIAG_PHASE".lower(),
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
            tmp = ["superpose", float(stat[1])/1000]
            avas_list.append(tmp)

        elif stat[0].lower() == 'FIELD_MAP'.lower():
            if int(stat[1]) == 70:
                tmp = ["field", float(stat[2])/1000, float(stat[4])/1000, 0,3,0,0,1, stat[5], stat[9]]

            elif int(stat[1]) == 7700:
                tmp = ["field", float(stat[2])/1000,float(stat[4])/1000, 0, 1, freq, stat[3], stat[6], stat[5], stat[9]]

            avas_list.append(tmp)

            if chexck_superposeend(tracewin_list, index):
                avas_list.append(["superposeend"])


        elif stat[0].lower() == "QUAD".lower():
            tmp = ['quad', float(stat[1])/1000, float(stat[3])/1000, 0, float(stat[2]), 0, 0]
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
            tmp = stat
            avas_list.append(tmp)

        elif stat[0].lower() in pass_list:
            pass

        else:
            print(101, stat)
            # pass

    #删掉repeat_ele后面的空格


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

def judge_adjust_element(tracewin_lattice, index):
    trace_element_lis = ['drift', 'field_map', 'quad', 'bend', 'thin_steering', 'edge', ]
    trace_diag_list = ['DIAG_CURRENT'.lower(), 'DIAG_SIZE'.lower(), 'DIAG_POSITION'.lower(),  "DIAG_PHASE".lower(),]

    #判断adjust作用于哪个元件
    v = 0
    for i in tracewin_lattice[index: ]:
        if len(i) == 0:
            pass
        elif i[0].lower() in trace_element_lis or i[0] in trace_diag_list:
            v = int(i[-1].split("_")[-1])
            break
    return v

def import_adjust(tracewin_lattice_path, adjust_file):
    trace_element_lis = ['drift', 'field_map', 'quad', 'bend', 'thin_steering', 'edge', ]
    trace_diag_list = ['DIAG_CURRENT'.lower(), 'DIAG_SIZE'.lower(), 'DIAG_POSITION'.lower(),  "DIAG_PHASE".lower(),]

    tracewin_lattice = read_txt(tracewin_lattice_path, out='list', case_sensitive= True)

    #增加索引
    index = 1
    for i in tracewin_lattice:
        if len(i) == 0:
            pass
        elif i[0].lower() in trace_element_lis or i[0].lower() in trace_diag_list:
            i.append(f"ele_{index}")
            index+=1
        elif i[0].lower() == "repeat_ele":
            index += int(i[1]) -1

    #得到一个列表，记录adjust调整的所有原件
    adjust_command = []
    for index, i in enumerate(tracewin_lattice):
        v= []
        if len(i) == 0:
            pass
        elif i[0].lower() == "adjust":
            v = i[:6]
            ele = judge_adjust_element(tracewin_lattice, index)
            v.append(ele)
            adjust_command.append(v)



    #构建adjust表
    adjust_lis = []

    #读取adjust文件
    adjust_content = read_txt(adjust_file, out='list', case_sensitive= True)
    for i in adjust_content:
        filtered_data = [item for item in i if ':' not in item][2:]
        filtered_data = [list(pair) for pair in zip(filtered_data[::2], filtered_data[1::2])]
        for j in filtered_data:
            adjust_lis.append(j)

    #添加修改的参数位置
    for i in adjust_lis:
        ele_index = int(i[0])
        
        ele_in_lattiace = 0
        for m, n in enumerate(tracewin_lattice):
            if len(n) == 0:
                pass
            elif n[-1] == f"ele_{ele_index}":
                ele_in_lattiace = m
        
        #寻找adjust_num:也就是修改的第几个参数
        for m in tracewin_lattice[:ele_in_lattiace][::-1]:
            if m[0].lower() == "ADJUST".lower():
                i.append(int(m[2]))
                break
    adjust_lis = [[int(item[0])] + item[1:] for item in adjust_lis]
    #[[6238, '-3.96117e-005', 2], [6642, '-0.00198424', 1], [7652, '0.00129728', 2]]

    #将上面的值幅值到命令
    for i in adjust_lis:
        for j in adjust_command:
            if j[-1] == i[0]:
                j.append(i[1])
                t_v = j
                break
        for j in adjust_command:
            if j[1] == t_v[1] and j[3] == t_v[3] and len(j) == 7:
                j.append(t_v[-1])


    adjust_command = [i for i in adjust_command if len(i) == 8]


    adjust_element_index = [i[-2] for i in adjust_command]

    #修改lattice

    for i in tracewin_lattice:
        if len(i) == 0:
            pass
        elif i[0].lower() in trace_element_lis or i[0] in trace_diag_list:
            corre_ele_index = int(i[-1].split("_")[-1])
            corre_command = []
            #i就是对应的原件
            if corre_ele_index in adjust_element_index:
                for j in adjust_command:
                    if j[-2] == corre_ele_index:
                        corre_command = j
                i[int(corre_command[2])] = corre_command[-1]

    # for i in tracewin_lattice:
    #     if len(i) == 0:
    #         pass
    #     elif i[0].lower() in trace_element_lis or i[0] in trace_diag_list:
    #         corre_ele_index = int(i[-1].split("_")[-1])
    #         corre_command = []
    #         #i就是对应的原件
    #         if corre_ele_index in adjust_element_index:
    #             print(i)


    adjust_tracewin_lattice = tracewin_lattice

    #删除索引
    for i in tracewin_lattice:
        if len(i) == 0:
            pass
        elif i[0].lower() in trace_element_lis or i[0].lower() in trace_diag_list:
            del i[-1]

    return adjust_tracewin_lattice

def add_err(avas_lattice, error_file, group, time):
    avas_element_lis = ['drift', 'field', 'quad', 'bend', 'steerer', 'edge', ]
    avas_diag_list = ['DIAG_CURRENT'.lower(), 'DIAG_SIZE'.lower(), 'DIAG_POSITION'.lower(),  "DIAG_PHASE".lower(),]

    #增加索引
    index = 1
    for i in avas_lattice:
        if len(i) == 0:
            pass
        elif i[0].lower() in avas_element_lis or i[0].lower() in avas_diag_list:
            i.append(f"ele_{index}")
            index+=1
    
    err_content = read_txt(error_file, out='list', case_sensitive= True)[5:]

    err_on_lis = [
        ["err_step", group, time],
        ["err_beam_dyn_on"] + [1] * 13,
        ["err_quad_dyn_on"] + [1] * 7,
        ["err_cav_dyn_on"] + [1] * 7,
    ]
    for i in err_content:
        if len(i) == 0:
            pass
        elif i[0].lower() == "ERROR_BEAM".lower():
            err_on_lis.append(["err_beam_dyn", 0] + i[1:14])

    for i in err_content:
        ele_index=0
        if len(i) == 0:
            pass
        elif i[0].lower() in ['QUAD_ERROR'.lower(), 'CAV_ERROR'.lower()]:
            ele_index = re.findall(r'\d+', i[1])
            ele_index = int(ele_index[0])


        err_lis = []
        if len(i) == 0:
            pass
        elif i[0].lower() == "QUAD_ERROR".lower():
            err_lis = ["err_quad_ncpl_dyn", 1, 0] + i[2:8] + [0]
        elif i[0].lower() == "CAV_ERROR".lower():
            err_lis = ["err_cav_ncpl_dyn", 1, 0] + i[2:6] + [i[7]] + [i[8]] + [0]
        for j in avas_lattice:
            if len(j) == 0:
                pass
            elif j[-1] == f"ele_{ele_index}":
                j.append(err_lis)
                break



    new_avaslattice = []
    for i in avas_lattice:
        if len(i) == 0:
            new_avaslattice.append(i)
        elif isinstance(i[-1], list):
            new_avaslattice.append(i[-1])
            new_avaslattice.append(i[:-1])
        else:
            new_avaslattice.append(i)



    for item in reversed(err_on_lis):
        new_avaslattice.insert(1, item)
        #删除索引

    for i in new_avaslattice:
        if len(i) == 0:
            pass
        elif i[0].lower() in avas_element_lis or i[0].lower() in avas_diag_list:
            del i[-1]

    return new_avaslattice

def write_to_avas_lattice(new_avaslattice, avas_lattice_path):
    with open(avas_lattice_path, 'w', encoding='UTF-8' ) as file_object:
        for i in new_avaslattice:
            tmp_s = " ".join(map(str, i))
            file_object.write(tmp_s+"\n")



if __name__ == "__main__":
    tracewin_lattiace_path =r"C:\Users\shliu\Desktop\tr\full_sc_template.dat"
    # in_put = "test1.txt"
    avas_lattice_path =r'"C:\Users\shliu\Desktop\tr\latticae_mulp.txt"'
    adjust_file = r"C:\Users\shliu\Desktop\test_yiman\test3\result\Adjusted_Values.txt_0"
    # error_file = r"E:\AVAS_CONTROL\相关程序\lattice转换\adjust_err\Error_Datas.txt_3"
    #修改后的lattice
    # adjust_tracewin_lattice = import_adjust(tracewin_lattiace_path, adjust_file)


    #将lattice转换成avas
    avas_lattice = tran_tracewin_avas(adjust_tracewin_lattice)
    #
    # new_avaslattice = add_err(avas_lattice, error_file)
    # # write_to_avas_lattice(new_avaslattice, avas_lattice_path)
