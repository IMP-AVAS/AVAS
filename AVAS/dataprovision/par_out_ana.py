#用来解析多粒子的输出文件
import numpy as np
import matplotlib.pyplot as plt
from utils.readfile import read_txt

def ana_syn_particle(path):
    #用来解析synparticle.txt
    # data_info = read_txt(path, out='list')
    # dataset_info = [[float(j) for j in i[1:]] for i in data_info]
    # print(data_info)
    last_line = None

    with open(path, "r", encoding="utf-8") as f:
        last_line = f.readlines()[-1].strip()
    last_line_info = last_line.split(" ")
    last_line_info = [float(i) for i in last_line_info[2:] if i]
    # z_s Ek_s x_s y_s γβ_x γβ_y γβ_z dir α
    return last_line_info
    print(last_line_info)


if __name__ == "__main__":
    path = r"C:\Users\wangh\Desktop\cafe\AVAS\OutputFile\synParticle.txt"
    res= ana_syn_particle(path)
    print(res)