#根据dataset提取x，y, phase

# import sys
# avas_path = r'/public/home/lzy_gpu/li1221/AVAS_control'
# sys.path.append(avas_path)

import os
import pandas as pd
from datetime import timedelta
import numpy as np
from dataprovision.datasetparameter import DatasetParameter
pd.set_option("display.max_columns", None)
from ana_err_bpm.read_dataset import read_dataset_dast, read_dataset_dast2

from multiprocessing import Pool, cpu_count
#
# def get_bpm(dataset_path,  posi):
#     data = read_dataset_dast(dataset_path)
#
#
#     z = np.asarray(data["cz"])  # 确保是 numpy array
#     # 找到第一个 > posi 的位置，再减 1 => 最后一个 <= posi
#     idx = np.searchsorted(z, posi, side="right") - 1
#     idx = int(np.clip(idx, 0, len(z) - 1))
#
#
#     res = read_dataset_dast2(dataset_path, idx)
#     print(26, res)
#
#     return {
#         "bpm_x": data["cx"][idx] * 1000,
#         "bpm_y": data["cy"][idx] * 1000,
#         "bpm_phase": data["phase"][idx],
#     }

def get_bpm(dataset_path, posi):
    data = read_dataset_dast(dataset_path)

    z = np.asarray(data["cz"])
    x = np.asarray(data["cx"])
    y = np.asarray(data["cy"])
    phase = np.asarray(data["phase"])

    idx = np.searchsorted(z, posi, side="right") - 1
    idx = int(np.clip(idx, 0, len(z) - 2))  # 注意 len(z)-2

    z0, z1 = z[idx], z[idx + 1]
    t = (posi - z0) / (z1 - z0)

    bpm_x = (1 - t) * x[idx] + t * x[idx + 1]
    bpm_y = (1 - t) * y[idx] + t * y[idx + 1]
    bpm_phase = (1 - t) * phase[idx] + t * phase[idx + 1]

    return {
        "bpm_x": bpm_x * 1000,
        "bpm_y": bpm_y * 1000,
        "bpm_phase": bpm_phase,
    }

    # obj = DatasetParameter(dataset_path, project_path)
    # obj.get_parameter()
    # # print(obj.x)
    # index = 0
    # # print(obj.z[-1] - obj.z[-2])
    # for i in obj.z:
    #     if i > posi:
    #         break
    #     else:
    #         index += 1
    # if index >= (len(obj.z)-1):
    #     index = len(obj.z) - 1
    # #单位是m
    # data = {
    #     "bpm_x": obj.x[index] *1000,
    #     "bpm_y": obj.y[index] * 1000,
    #     "bpm_phase": obj.abs_phase[index],
    # }
    #
    # return data


def get_one_time_res(args):
    dataset_path, bpm_name, bpm_posi = args
    one_time_res = {}
    for j in range(len(bpm_posi)):
        res = get_bpm(dataset_path, bpm_posi[j])
        one_time_res[bpm_name[j]] = res
    return one_time_res


def get_one_group_res(bpm_name, bpm_posi, dataset_path_base, project_path,  group):
    dataset_paths = [os.path.join(dataset_path_base, f"output_{group}_{i}", "DataSet.txt") for i in range(1,101)]


    num_workers = max(cpu_count() - 3, 1)

    with Pool(num_workers) as pool:  # 使用上下文管理器
        # 准备每一步的参数
        args = [(i, bpm_name, bpm_posi) for i in dataset_paths]
        # 使用进程池并行执行每一步数据处理
        one_group_res = pool.map(get_one_time_res, args)


    bpm_one_group_dict = {i: {"bpm_x": [], "bpm_y": [], "bpm_phase": [],} for i in bpm_name}
    for i in bpm_name:
        for j in one_group_res:
            bpm_one_group_dict[i]["bpm_x"].append(j[i]["bpm_x"])
            bpm_one_group_dict[i]["bpm_y"].append(j[i]["bpm_y"])
            bpm_one_group_dict[i]["bpm_phase"].append(j[i]["bpm_phase"])

    return bpm_one_group_dict


if __name__ == "__main__":
    dataset_path = r"C:\Users\wangh\Desktop\hiaf_v2\result\dxy\g2\output_2_90\DataSet.txt"
    res =get_bpm(dataset_path, 97)
    print("gpu", res)

    dataset_path = r"C:\Users\wangh\Desktop\hiaf_v2\AVAS_HIAF_dxy\OutputFile\output_0\DataSet.txt"
    res =get_bpm(dataset_path, 97)
    print("cpu", res)

    # bpm_table = r"/public/home/lzy_gpu/li1221/ana_err_bpm/bpm_v2.xlsx"
    # df_bpmphase = pd.read_excel(bpm_table, )
    #
    # bpm_name = df_bpmphase["name_bpm"].tolist()
    # bpm_posi = df_bpmphase["bpm_posi"].tolist()
    # dataset_path_base = r"/public/home/lzy_gpu/li1221/AVAS_HIAF_dxy/OutputFile/error_output"
    # project_path =  r"/public/home/lzy_gpu/li1221/AVAS_HIAF_dxy"
    # bpm_one_group_dict = get_one_group_res(bpm_name, bpm_posi, dataset_path_base, project_path, 1)
    # # print(bpm_one_group_dict)
    #
    # rows = []
    # for bpm, v in bpm_one_group_dict.items():
    #     rows.append({
    #         "bpm_name": bpm,
    #         "bpm_x": v["bpm_x"],
    #         "bpm_y": v["bpm_y"],
    #         "bpm_phase": v["bpm_phase"],
    #
    #         "bpmx_max": np.max(v["bpm_x"]),
    #         "bpmx_min": np.min(v["bpm_x"]),
    #
    #         "bpmy_max": np.max(v["bpm_y"]),
    #         "bpmy_min": np.min(v["bpm_y"]),
    #
    #         "bpmphase_max": np.max(v["bpm_phase"]),
    #         "bpmphase_min": np.min(v["bpm_phase"]),
    #
    #     })
    #
    # df = pd.DataFrame(rows)
    # # print(df)
    # df.to_excel("dxy.xlsx", index=False)

