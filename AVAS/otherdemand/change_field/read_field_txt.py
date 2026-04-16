import os
import random

import numpy as np

def read_txt(input):
    with open(input, encoding='UTF-8') as file_object:
        input_lines = []
        for line in file_object:
            input_lines.append(line)


    input_lines = [i.split() for i in input_lines if i.strip()]

    return input_lines


def treat_cav(basepath, field_name):
    filedex = [".edx", ".edy", ".edz", ".bdx", ".bdy", ".bdz"]
    for i in filedex:
        out = []

        path_in = os.path.join(basepath, f"{field_name}{i}" )
        path_out =  os.path.join(basepath, f"{field_name}_2{i}"  )

        input = read_txt(path_in)

        out.append(input[0])
        out.append(input[1])
        out.append(input[2])
        out.append(input[3])

        for i in input[4:]:
            num = float(i[0])
            num = '{:.8f}'.format(num + random.uniform(0, num))
            out.append([num])
        # write(path_out, out)

def treat_sol(basepath, field_name):
    filedex = [".edx"]
    for i in filedex:
        out = []

        path_in = os.path.join(basepath, f"{field_name}{i}" )
        path_out =  os.path.join(basepath, f"{field_name}_2{i}"  )

        input = read_txt(path_in)
        out.append(input[0])
        out.append(input[1])
        out.append(input[2])
        out.append(input[3])
        print(out)
        for i in input[4:]:
            num = float(i[0])
            num = '{:.8f}'.format(num + random.uniform(0, num))
            out.append(num[0])
        # print(out)
        # print(np.max(out))
        # write(path_out, out)


# def write(path, content):
#     with open(path, 'w', encoding='utf-8') as f:
#         for i in content:
#             f.write(' '.join(map(str, i)) + '\n')

if __name__ == '__main__':
    base_path = r"C:\Users\wangh\Desktop\qiaoxin-04-07\RFQ"
    field_name = "RFQ"
    treat_sol(base_path, field_name)
