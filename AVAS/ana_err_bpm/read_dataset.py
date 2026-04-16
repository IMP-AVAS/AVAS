import numpy as np
from dataprovision.datasetparameter import DatasetParameter
import matplotlib.pyplot as plt

def read_dataset_dast(path):
    data = np.loadtxt(path)

    x = data[:, 1] + data[:, 29]
    # print(data[:, 29][-20:])
    # print(data[:, 1][-20:])
    y = data[:, 3] + data[:, 31]
    z = data[:, 33] + data[:, 5]


    phase = data[:, 40] * 2 * 180 * 81.25 * 10 ** 6

    max_y = data[:, 24]
    print(17, z[-1])
    print(18, np.max(max_y))
    # print(13, data[:, 1][27125])
    # print(14, data[:, 29][27125])
    # print(15, x[27125], )
    data= {
        "cx": x,
        "cy": y,
        "cz": z,
        "phase": phase,
        "max_y": max_y,

    }
    return data

def read_dataset_dast2(path, idx):
    data = np.loadtxt(path)

    x = data[:, 1] + data[:, 29]

    y = data[:, 3] + data[:, 31]
    z = data[:, 33] + data[:, 5]

    phase = data[:, 40] * 2 * 180 * 81.25 * 10 ** 6

    data= {
        "x_b": data[:, 1][idx],
        "dx": data[:, 29][idx]

    }
    return data

if __name__ == "__main__":
    # path = r"C:\Users\wangh\Desktop\hiaf_v2\result\dxy\output_0_0\DataSet.txt"
    # res = read_dataset_dast(path)
    # # print(res["cx"][-5:])
    # print(res["cz"][-5:])
    #
    # obj = DatasetParameter(path, project_path= None)
    # v = obj.get_parameter()
    #
    # # print(obj.x[-5:])
    # print(res["cz"][-5:])
    dataset_path = r"C:\Users\wangh\Desktop\新建文件夹\DataSet.txt"
    res_gpu =read_dataset_dast(dataset_path)
    import matplotlib.pyplot as plt
    plt.plot(res_gpu["cz"], res_gpu["max_y"])
    plt.show()


    # print("gpu", res_gpu)
    # z_gpu = res_gpu["cz"]
    # x_gpu = res_gpu["cx"]
    #
    #
    # dataset_path = r"C:\Users\wangh\Desktop\hiaf_v2\AVAS_HIAF_dxy\OutputFile\output_0\DataSet.txt"
    # res_cpu =read_dataset_dast(dataset_path)
    #
    #
    # z_cpu = res_cpu["cz"]
    # # print(66, z_cpu)
    # x_cpu = res_cpu["cx"]
    #
    #
    #
    # plt.plot(z_cpu, x_cpu, label="cpu", c = "red")
    # plt.plot(z_gpu, x_gpu, label="gpu", c= "blue")
    #
    # plt.legend()
    # plt.show()
    #

