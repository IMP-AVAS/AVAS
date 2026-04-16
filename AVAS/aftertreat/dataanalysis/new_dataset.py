#这是一个用于将Dataset中的z变换成直接可用z的脚本

#主要涉及 1.质心转换 z转换， 2.最大包络转换
import numpy as np
import math

def trans_dataset2new(path, out_path):
    data = np.loadtxt(path)

    c_x = data[:, 1] + data[:, 29]
    c_y = data[:, 3] + data[:, 31]

    # v = data[:, 33]
    # print(v, len(v))

    N = data.shape[0]
    c_z = np.empty(N, dtype=float)

    sign1 = 0
    sign2 = 0

    for i in range(N):
        flag = data[i, 35]

        if flag == 0:
            sign2 = 0
            if sign1 == 0:
                c_z[i] = data[i, 5] + data[i, 33]
            else:
                c_z[i] = c_z[i - 1] + data[i, 38]

        elif flag == 1:
            step = math.sqrt(data[i, 37] ** 2 + data[i, 38] ** 2)
            c_z[i] = c_z[i - 1] + step
            sign1 = 1
            sign2 = 0

        else:
            # flag == 2 或其它
            if sign2 == 0:
                step = math.sqrt(data[i, 37] ** 2 + data[i, 38] ** 2)
                c_z[i] = c_z[i - 1] + step
                sign2 = 1
            else:
                # 连续第二个 2：跳过，但为了数组完整，需要给当前 i 一个值
                # 原来 continue 会导致 c_z 少一个元素；现在我们保持长度一致：延续上一个值
                c_z[i] = c_z[i - 1]

    print(c_z, len(c_z))

    #转换质心cx, cy, cz
    data[:, 1] = c_x
    data[:, 3] = c_y
    data[:, 5] = c_z

    #转换最大值
    data[:, 22] = data[:, 22] + c_x
    data[:, 24] = data[:, 24] + c_y
    data[:, 26] = data[:, 26] + c_z


    np.savetxt(
        out_path,
        data,
        fmt="%.6e"   # 科学计数法，适合物理数据
    )

    print(f"✅ 已写入新文件: {out_path}")

    return True

    # for i in range(len(dataset_info)):
    #     if (dataset_info[i][35] == 0):
    #         sign2 = 0
    #         if (sign1 == 0):
    #             c_z.append(dataset_info[i][5] + dataset_info[i][33])
    #         else:
    #             c_z.append(c_z[-1] + dataset_info[i][38])
    #     elif (dataset_info[i][35] == 1):
    #         c_z.append(c_z[-1] + math.sqrt(dataset_info[i][37] ** 2 + dataset_info[i][38] ** 2))
    #         sign1 = 1
    #         sign2 = 0
    #
    #     elif (sign2 == 0):
    #         # 条件为2( 第35个数据为2 )， sign2= 0
    #         # 也就是说，如果这一次的标志为2，但是前一次的标志也为0， 1，那么进入这次循环
    #         c_z.append(c_z[-1] + math.sqrt(dataset_info[i][37] ** 2 + dataset_info[i][38] ** 2))
    #         sign2 = 1
    #
    #     else:
    #         # 条件为2， sign2 = 1
    #         # 也就是说，如果这一次的标志为2，但是前一次的标志也为2，那么进入这次循环
    #         continue

    # return data


if __name__ == "__main__":
    path = r"C:\Users\wangh\Desktop\test_dataset\DataSet.txt"
    new_path  =  r"C:\Users\wangh\Desktop\test_dataset\DataSet_New.txt"
    res = trans_dataset2new(path, new_path)


    # print(res)