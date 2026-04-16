import sys

from pandas.core.interchange.dataframe_protocol import DataFrame
import numpy as np
import matplotlib.pyplot as plt


from  utils.readfile import read_dst_fast
import struct
import os
def get_size(x, x1, alpha_x, beta_x, gamma_x):
    #计算全发射度
    return gamma_x * x ** 2 + 2 * alpha_x * x * x1 + beta_x * x1 ** 2

def write_to_dst(path, particle_info, p_dst):
    # particle_info = {
    #     "np": ,
    #     "Ib":
    #     "freq":
    #     "BaseMassInMeV": ,
    # }

    np = particle_info["np"]
    Ib = particle_info["Ib"]
    freq = particle_info["freq"]
    BaseMassInMeV = particle_info["BaseMassInMeV"]



    outputfile_one_step = path

    with open(outputfile_one_step, 'wb') as data0utFile:
        try:
            data0utFile.write(struct.pack('c', b'\x7D'))  # skip1
            data0utFile.write(struct.pack('c', b'\x64'))  # skip2

            data0utFile.write(struct.pack('i', np))
            data0utFile.write(struct.pack('d', Ib))  # mA
            data0utFile.write(struct.pack('d', freq/10**6))  # MHz

            data0utFile.write(struct.pack('c', b'\x7D'))

            for i in range(len(p_dst)):
                for j in range(6):
                    data0utFile.write(struct.pack('d', p_dst[i][j]))

            data0utFile.write(struct.pack('d', BaseMassInMeV))  # Mev

        except IOError:
            print("输出错误")

if __name__ == '__main__':
    input_path = r"C:\Users\wangh\Desktop\ge_kongxin\12_5.dst"
    output_path = r"C:\Users\wangh\Desktop\ge_kongxin\kongxin.dst"

    data_res = read_dst_fast(input_path)

    partran_dist = data_res['partran_dist']
    # print(partran_dist[:10])
    partran_dist[:, [0, 2]] *= 10


    alpha = 0
    beta = 1
    gamma_x = (1 + alpha ** 2) / beta

    size_xiao = []
    size_da = []
    size_list = []
    v1 =[]
    for i in partran_dist:
        x =i[0]
        y = i[2]
        size = get_size(x, y, alpha, beta, gamma_x)
        v1.append(size)
    big_size = np.max(v1)

    print("big_size", big_size)

    for i in partran_dist:
        x =i[0]
        y = i[2]
        size = get_size(x, y, alpha, beta, gamma_x)
        if  size > big_size * 0.4:
            size_da.append(i)
        else:
            if np.random.rand() < 0.2:  # 30% 概率保留中心粒子，可调
                size_xiao.append(i)
        size_list.append(size)

    size_da = np.array(size_da)
    size_xiao = np.array(size_xiao)

    # ✅ 给 size_da 添加随机误差（例如 5% 的高斯噪声）
    perturbed_list = [size_da]

    for i in range(3):
        mask = np.random.rand(len(size_da)) < 0.89
        selected = size_da[mask]

        # Step 2: 对选中的粒子加随机扰动
        # perturbation = np.random.normal(0, 0.2, selected.shape) * selected
        # size_da_perturbed = selected + perturbation

        size_da_perturbed = selected.copy()
        # size_da_perturbed[:, [0, 2]] += np.random.normal(0, 0.2, size_da_perturbed[:, [0, 2]].shape) * selected[
        #     :, [0, 2]]
        # size_da_perturbed[:, [1, 3, 4, 5]] += np.random.normal(0, 0.1, size_da_perturbed[:, [1, 3, 4, 5]].shape) * selected[
        #     :, [1, 3, 4, 5]]

        size_da_perturbed[:, [0, 2]] += np.random.uniform(-10, 10, size_da_perturbed[:, [0, 2]].shape)
        size_da_perturbed[:, [1, 3,]] += np.random.uniform(-0.0005/1000, 0.0005/1000, size_da_perturbed[:, [1, 3, ]].shape)
        size_da_perturbed[:, [4]] += np.random.uniform(
            -0.1, 0.1, size_da_perturbed[:, [4]].shape
        )
        size_da_perturbed[:, [5]] += np.random.uniform(
            -0.005, 0.005, size_da_perturbed[:, [5]].shape
        )
        # Step 3: 合并原始粒子 + 扩充后的粒子
        perturbed_list.append(size_da_perturbed)

    # 合并原始 + 加误差的
    size_da_expanded = np.vstack(perturbed_list)

    all_size = np.vstack((size_da_expanded, size_xiao))

    # print(len(all_size))
    # x = [i[0] for i  in all_size]
    # y = [i[2] for i in all_size]
    # plt.scatter(x, y, s = 1)
    # plt.title("空心化后的粒子分布")
    # plt.axis("equal")
    # plt.show()
    all_size[:, [0, 2]] /= 10

    particle_info = {
        "np": len(all_size),
        "Ib": data_res['ib'],
        "freq": data_res['freq'],
        "BaseMassInMeV": data_res['basemassinmev'],
    }

    write_to_dst(output_path, particle_info, all_size)