import numpy as np
import matplotlib.pyplot as plt


# 读取单粒子结果
def read_sp(path):
    data = np.loadtxt(path)

    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]

    phase = data[:, 7] * 2 * 180 * 81.25 * 10 ** 6
    energy = data[:, 6]

    loss = 10 ** 5 - np.array(data[:, 28])
    data = {
        "cx": x,
        "cy": y,
        "cz": z,
        "phase": phase,
        "energy": energy,
        "loss": loss
    }
    return data


def read_dataset_fast(path):
    data = np.loadtxt(path)

    x = data[:, 1] + data[:, 29]
    y = data[:, 3] + data[:, 31]
    z = data[:, 33] + data[:, 5]
    phase = data[:, 40] * 2 * 180 * 81.25 * 10 ** 6
    energy = data[:, 0]
    number = np.array(data[:, 28])
    loss = 10 ** 5 - np.array(data[:, 28])
    rms_x = data[:, 16]
    rms_y = data[:, 18]

    data = {
        "cx": x,
        "cy": y,
        "cz": z,
        "phase": phase,
        "energy": energy,
        "loss": loss,
        "rms_x": rms_x,
        "rms_y": rms_y,
        "number": number,

    }
    return data


if __name__ == "__main__":
    dataset_path = r"C:\Users\wangh\Desktop\HIAF_ana\hiaf_v2\AVAS_HIAF_ek\OutputFile\error_output\output_0_0\SingleParticle.txt"
    res_gpu = read_sp(dataset_path)
    import matplotlib.pyplot as plt

    plt.plot(res_gpu["cz"], np.array(res_gpu["cy"]) * 1000)
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

