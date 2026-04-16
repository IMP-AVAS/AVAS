#z这个脚本通过读取dst文件，然后修改流强等参数，实现模拟

import struct
import numpy
import numpy as np
import os
from utils.exception import CustomFileNotFoundError
import re
import global_varible
import time


def read_dst_fast(input):
    t0 = time.time()
    with open(input, 'rb') as f:
        f.read(2)  # 跳过前2个字节

        # 读取整数和两个双精度浮点数
        number = struct.unpack("<i", f.read(4))[0]
        print("粒子数", number/10000, "万")
        Ib = struct.unpack("<d", f.read(8))[0]
        freq = struct.unpack("<d", f.read(8))[0]

        f.read(1)  # 跳过1个字节

        # 读取 6 * number 个双精度浮点数 cm mrad
        partran_dist = np.fromfile(f, dtype='<f8', count=6 * number).reshape(number, 6)

        # 读取最后一个双精度浮点数
        BaseMassInMeV = struct.unpack("<d", f.read(8))[0]

    res= {}
    res['number'] = number
    res['ib'] = Ib
    res['freq'] = freq
    res['partran_dist'] = partran_dist
    res['basemassinmev'] = BaseMassInMeV
    t1 = time.time()
    print("读文件时间", t1 - t0)
    res['kneticenergy'] = float(partran_dist[:, 5].mean())
    t2 = time.time()

    print("计算能量时间", t2 - t1)

    return res


def write_to_dst(path, particle_info):
    # particle_info = {
    #     "np": ,
    #     "Ib":
    #     "freq":
    #     "BaseMassInMeV": ,
    # }

    np = particle_info["number"]
    Ib = particle_info["ib"]
    freq = particle_info["freq"]
    BaseMassInMeV = particle_info["basemassinmev"]

    p_dst = particle_info["partran_dist"]

    outputfile_one_step = path

    with open(outputfile_one_step, 'wb') as data0utFile:
        try:
            data0utFile.write(struct.pack('c', b'\x7D'))  # skip1
            data0utFile.write(struct.pack('c', b'\x64'))  # skip2

            data0utFile.write(struct.pack('i', np))
            data0utFile.write(struct.pack('d', Ib))  # mA
            data0utFile.write(struct.pack('d', freq))  # MHz

            data0utFile.write(struct.pack('c', b'\x7D'))

            for i in range(len(p_dst)):
                for j in range(6):
                    data0utFile.write(struct.pack('d', p_dst[i][j]))

            data0utFile.write(struct.pack('d', BaseMassInMeV))  # Mev

        except IOError:
            print("输出错误")

if __name__ == "__main__":
    #读取原来的分布
    import copy
    ori_dst = r"C:\Users\wangh\Desktop\test_energy\danengsan_p10_3\avas_p10_sol_2\InputFile\p10_2.dst"
    ori_fenbu = read_dst_fast(ori_dst)
    print(ori_fenbu)

    new_fenbu = copy.copy(ori_fenbu)

    pdst = new_fenbu["partran_dist"]

    for i in pdst:
        i[1] = 0.000001
        i[3] = 0.000001

######################
    #修改参数


    #生成新的分布
    new_dst = r"C:\Users\wangh\Desktop\test_energy\danengsan_p10_3\avas_p10_sol_2\InputFile\p10_4.dst"
    write_to_dst(new_dst, new_fenbu)
