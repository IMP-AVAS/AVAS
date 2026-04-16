import math
import copy
import global_varible
import os
import uuid
import numpy as np
def write_to_txt(path, lis):
    with open(path, 'w') as f:
        for i in lis:
            f.write(' '.join(map(str, i)) + '\n')

def add_to_txt(path, lis):
    with open(path, 'a') as f:
        for i in lis:
            f.write(' '.join(map(str, i)) + '\n')


def calculate_rms(data):
    if not data:
        raise ValueError("The input list cannot be empty.")
    x_mean = calculate_mean(data)
    square_sum = sum((x-x_mean) ** 2 for x in data)
    mean_square = square_sum / len(data)
    rms = math.sqrt(mean_square)

    return rms

def calculate_mean(data):
    if not data:
        raise ValueError("The input list cannot be empty.")

    total_sum = sum(data)
    mean = total_sum / len(data)

    return mean

def convert_dic2lis(dic):
    res = []
    for k, v in dic.items():
        v_lis = []
        if isinstance(v, list):
            v_lis.append(k)
            v_lis.extend(v)
        else:
            v_lis.append(k)
            v_lis.append(v)
        res.append(v_lis)

    return res

def format_output(code=0, msg="success", **kwargs):

    return {
        "code": code,
        "data": {
            "msg": msg,
            **kwargs
        }
    }


def judge_command_on_element(lattice, command):
    # 返回一个命令对应的是哪个元件
    lattice = copy.deepcopy(lattice)

    command_index = lattice.index(command)
    command_on_element = None
    for i in range(command_index, len(lattice)):
        if lattice[i][0] in global_varible.all_element:
            command_on_element = int(lattice[i][-1].split("_")[1])
            break
    if command_on_element is None:
        command_on_element = -1
    return command_on_element

def delete_element_end_index(error_lattice):
    error_lattice_copy = copy.deepcopy(error_lattice)
    for i in error_lattice_copy:
        if i[0] in global_varible.all_element:
            i.pop()
    return error_lattice_copy

def add_element_end_index(lattice):
    lattice = copy.deepcopy(lattice)
    index = 0
    for i in lattice:
        if i[0] in global_varible.all_element:
            add_name = f'element_{index}'
            i.append(add_name)
            index += 1
    return lattice


#判断一个数能否转化成其他类型
def can_convert_to_othertype(s: str, target_type) -> bool:
    try:
        if target_type == int:
            v1 = float(s)
            if not v1.is_integer():  # 用 `is_integer()` 避免浮点数精度问题
                raise ValueError("Cannot convert to an integer")
        elif target_type == float:
            float(s)
        elif target_type == str:
            str(s)
        return True
    except ValueError:
        return False

def convert_to_othertype(s: str, target_type):
    if target_type == int:
        v1 = int(float(s))
    elif target_type == float:
        v1 = float(s)
    if target_type == str:
        v1 = str(s)
    return v1

def convert_to_othertype_dict(k , v, target_type) :
    #对字典的类型进行转换
    if v is None:
        return None

    else:
        try:
            if target_type == int:
                v = int(float(v))
            elif target_type == float:
                v = float(v)
            elif target_type == str:
                v = str(v)
            return v
        except:
            raise ValueError(f"Cannot {k} {v} to target type {target_type}")




def safe_float(v, default=0.0):
    try:
        if v is None:
            return default
        return float(v)
    except ValueError:
        return default

def safe_int(v, default=0):
    try:
        if v is None:
            return default
        return int(v)
    except (ValueError, TypeError):
        return default

def safe_str(v, default=""):
    try:
        if v is None:
            return default
        return str(v)
    except (ValueError, TypeError):
        return default
def get_list_interval(data, interval):
    #该函数是为了间隔获取数据，如果是一个一维列表，就直接操作，如果是多维列表，
    #就分别获取每个列表的间隔数据

    if isinstance(data[0], list):
        new_data = [i[::interval] for i in data]
    else:
        new_data = data[::interval]
    return new_data

def generate_web_picture_param(obj, ):
    pictureParam = {
        "labelx": "",
        "labely": "",
        "datax": [],
        "datay": [],
        "legends": [],
    }

    pictureParam["labelx"] = obj.xlabel
    pictureParam["labely"] = obj.ylabel
    pictureParam["datax"] = obj.x
    pictureParam["datay"] = obj.y
    pictureParam["legends"] = obj.labels[: len(obj.y)]
    return pictureParam

def generate_web_picture_path(project_path):
    picture_save_directory = os.path.join(project_path, "OutputFile", "Picture")
    os.makedirs(picture_save_directory, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.png"
    save_path = os.path.join(picture_save_directory, filename)
    return save_path


def trans_xp_xx1(item):
    # freq= {
    #     "BaseMassInMeV":,
    #      "freq":,
    #        "average_vz":
    #         "part_dict"
    # }
    BaseMassInMeV = item["BaseMassInMeV"]
    freq = item["freq"]
    part_dict = item["part_dict"]
    part_list = item["part_list"]
    num = item["num"]

    all_exist_v = []

    #入口时，计算所有粒子的平均值
    #出口，只计算还存在的粒子的平均值
    for particle in part_list:
        p2 = particle[1] ** 2 + particle[3] ** 2 + particle[5] ** 2
        beta = math.sqrt(p2 / (1 + p2))
        # gamma = 1 / math.sqrt(1 - beta ** 2)
        v = beta* global_varible.c_light

        # beta_z = math.sqrt(particle[5] ** 2 / (1 + particle[5] ** 2))
        # v_z = beta_z * global_varible.c_light

        all_exist_v.append(v)

    average_v = np.mean(all_exist_v)
    # print(len(all_exist_v))


    all_part = []
    #用于处理将x-p空间的数据转换成xx1空间
    for particle in part_list:
        # print(186, particle)

        p2 = particle[1] ** 2 + particle[3] ** 2 + particle[5] ** 2
        beta = math.sqrt(p2 / (1 + p2))
        gamma = 1 / math.sqrt(1 - beta ** 2)
        v = beta* global_varible.c_light

        beta_z = math.sqrt(particle[5] ** 2 / (1 + particle[5] ** 2))
        v_z = beta_z * global_varible.c_light

        v_x = (particle[1] / particle[5]) * v_z
        v_y = (particle[3] / particle[5]) * v_z

        t = -(particle[4] / v_z)

        x = (particle[0] + v_x * t) * 1000  # mm

        xx = particle[1] / particle[5] * 1000
        y = (particle[2] + v_y * t) * 1000
        yy = particle[3] / particle[5] * 1000

        # z = (part_dict['location'] + particle[4])* 1000
        z = particle[4] * 1000

        zz = (v - average_v) / average_v * 1000

        phi = t * 2 * global_varible.Pi * freq / global_varible.Pi * 180  # 度

        E = (gamma - 1) * BaseMassInMeV  # MeV

        part_index = particle[7]
        tlist = [x, xx, y, yy, z, zz, phi, E, 1, part_index]

        # exist_part.append(tlist)

        if num == -1:
            if particle[6] == 0:
                tlist = [0] * 8 + [0, particle[7]]

        all_part.append(tlist)
    return all_part

def cal_twiss(item):
    x = item["x"]
    x1 = item["x1"]
    # print(275, x, x1)
    coefficient = item["coefficient"]
    gamma = item["gamma"]
    beta = item["beta"]


    average_x = np.mean(x)
    average_x1 = np.mean(x1)
    sigma_x = np.average([(i - average_x) ** 2 for i in x])
    sigma_x1 = np.average([(i - average_x1) ** 2 for i in x1])

    sigma_xx1 = np.average([(x[i] - average_x) * (x1[i] - average_x1) for i in range(len(x))])
    # print("sigma_x =", sigma_x)
    # print("sigma_x1 =", sigma_x1)
    # print("sigma_xx1 =", sigma_xx1)
    # print("expr =", sigma_x * sigma_x1 - sigma_xx1 * sigma_xx1)

    epsilon_x = math.sqrt(sigma_x * sigma_x1 - sigma_xx1 * sigma_xx1)

    beta_x = sigma_x / epsilon_x
    alpha_x = -sigma_xx1 / epsilon_x
    gamma_x = (1 + alpha_x ** 2) / beta_x

    if coefficient != 0:
        norm_epsilon_x = beta * gamma ** (coefficient) * epsilon_x
    else:
        norm_epsilon_x = epsilon_x

    return alpha_x, beta_x, gamma_x, epsilon_x, norm_epsilon_x

if __name__ == '__main__':
    # code = 1
    # msg = "s"
    # kwargs = {"x": [1, 2, 3],
    #           "y": [1, 2, 3]}
    # value = format_output(msg ="dad")
    # print(value)
    v = "10.0"
    print(can_convert_to_othertype(v, float))