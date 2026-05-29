#根据dataset提取x，y, phase,在不同的位置

# import sys
# avas_path = r'/public/home/lzy_gpu/li1221/AVAS_control'
# sys.path.append(avas_path)

import os
import pandas as pd
from datetime import timedelta
import numpy as np

pd.set_option("display.max_columns", None)
from ana_err_bpm.read_dataset import read_dataset_fast

from multiprocessing import Pool, cpu_count


def get_bpm(dataset_path, posi):
    data = read_dataset_fast(dataset_path)

    z = np.asarray(data["cz"])
    x = np.asarray(data["cx"])
    y = np.asarray(data["cy"])
    phase = np.asarray(data["phase"])
    energy = np.asarray(data["energy"])
    loss_lis = np.asarray(data["loss"])
    rms_x = np.asarray(data["rms_x"])
    rms_y = np.asarray(data["rms_y"])
    number = np.asarray(data["number"])

    idx = np.searchsorted(z, posi, side="right") - 1
    idx = int(np.clip(idx, 0, len(z) - 2))  # 注意 len(z)-2

    z0, z1 = z[idx], z[idx + 1]
    t = (posi - z0) / (z1 - z0)


    bpm_x = (1 - t) * x[idx] + t * x[idx + 1]
    bpm_y = (1 - t) * y[idx] + t * y[idx + 1]
    bpm_phase = (1 - t) * phase[idx] + t * phase[idx + 1]

    energy = (1-t) * energy[idx] + t * energy[idx + 1]
    loss = (1-t) * loss_lis[idx] + t* loss_lis[idx + 1]
    bpm_rms_x = (1-t) * rms_x[idx] + t* rms_x[idx + 1]
    bpm_rms_y = (1-t) * rms_y[idx] + t* rms_y[idx + 1]
    bpm_number = (1-t) * number[idx] + t* number[idx + 1]

    return {
        "bpm_x": bpm_x * 1000,
        "bpm_y": bpm_y * 1000,
        "bpm_phase": bpm_phase,
        "energy": energy,
        "loss": loss,
        "bpm_rms_x": bpm_rms_x*1000,
        "bpm_rms_y": bpm_rms_y *1000,
        "bpm_number": bpm_number
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
    dataset_paths = [os.path.join(dataset_path_base, f"output_{group}_{i}", "dataset.txt") for i in range(1,21)]

    dataset_paths = [i for i in dataset_paths if os.path.exists(i)]
    num_workers = max(cpu_count() - 3, 1)

    with Pool(num_workers) as pool:  # 使用上下文管理器
        # 准备每一步的参数
        args = [(i, bpm_name, bpm_posi) for i in dataset_paths]
        # 使用进程池并行执行每一步数据处理
        one_group_res = pool.map(get_one_time_res, args)


    bpm_one_group_dict = {i: {"bpm_x": [], "bpm_y": [], "bpm_phase": [], "energy": [], "loss": [],
                              "bpm_rms_x": [], "bpm_rms_y": [], "bpm_number":[],
                              }
                           for i in bpm_name}
    

    kv_map = {"bpm_x": [], "bpm_y": [], "bpm_phase": [], "energy": [], "loss": [],
                              "bpm_rms_x": [], "bpm_rms_y": [], "bpm_number":[],
                              }
    k_param = [k for k, v in kv_map.items()]
    # print(113, k_param)
    for i in bpm_name:
        for j in one_group_res:
            for k in k_param:
                bpm_one_group_dict[i][k].append(j[i][k])
            # bpm_one_group_dict[i]["bpm_x"].append(j[i]["bpm_x"])
            # bpm_one_group_dict[i]["bpm_y"].append(j[i]["bpm_y"])
            # bpm_one_group_dict[i]["bpm_phase"].append(j[i]["bpm_phase"])
            # bpm_one_group_dict[i]["energy"].append(j[i]["energy"])
            # bpm_one_group_dict[i]["loss"].append(j[i]["loss"])

    return bpm_one_group_dict


if __name__ == "__main__":

    project_path = r"C:\Users\wangh\Desktop\HIAF_0509\HIAH_0509dE"
    #dataset_path_normal = r"C:\Users\wangh\Desktop\HIAF_ana\hiaf_v2\AVAS_HIAF_ek\OutputFile\error_output\output_0_0\SingleParticle.txt"
    dataset_path_normal = os.path.join(project_path, "outputfile", "error_output", "output_0_0", "dataset.txt") 

    bpm_table = r"C:\Users\wangh\Desktop\HIAF_code_0509\bpm_v2.xlsx"
    dataset_path_base = os.path.join(project_path, "OutputFile", "error_output")



    df_bpmphase = pd.read_excel(bpm_table, )

    bpm_name = df_bpmphase["name_bpm"].tolist()
    bpm_posi = df_bpmphase["bpm_posi"].tolist()


    # dataset_path_base = r"C:\Users\wangh\Desktop\HIAF_ana\hiaf_v2\AVAS_HIAF_ek\OutputFile\error_output"

    # project_path =  r"C:\Users\wangh\Desktop\HIAF_ana\hiaf_v2\AVAS_HIAF_ek"


    # print(bpm_one_group_dict)


    #正常模拟的结果
    args = (dataset_path_normal, bpm_name, bpm_posi)
    one_time_res = get_one_time_res(args)

    bpmphase_normal = [v["bpm_phase"] for k,v in one_time_res.items()]

    energy_normal = [v["energy"] for k,v in one_time_res.items()]

    for i in range(1,6):
        print(i)
        rows = []
        bpm_one_group_dict = get_one_group_res(bpm_name, bpm_posi, dataset_path_base, project_path, i)
        for bpm, v in bpm_one_group_dict.items():
            rows.append({
                "bpm_name": bpm,
                "bpm_x": v["bpm_x"],
                "bpm_y": v["bpm_y"],
                "bpm_phase": v["bpm_phase"],
                "energy": v["energy"],
                "loss": v["loss"],
                "bpm_rms_x": v["bpm_rms_x"],
                "bpm_rms_y": v["bpm_rms_y"],
                "bpm_number": v["bpm_number"],


                "bpmx_max": np.max(v["bpm_x"]),
                "bpmx_min": np.min(v["bpm_x"]),

                "bpmy_max": np.max(v["bpm_y"]),
                "bpmy_min": np.min(v["bpm_y"]),

                "energy_max": np.max(v["energy"]),
                "energy_min": np.min(v["energy"]),


                "bpmphase_max": np.max(v["bpm_phase"]),
                "bpmphase_min": np.min(v["bpm_phase"]),

                "loss_max": np.max(v["loss"]),
                "loss_min": np.min(v["loss"]),


                "bpm_rmsx_max": np.max(v["bpm_rms_x"]),
                "bpm_rmsx_min": np.min(v["bpm_rms_x"]),

                "bpm_rmsy_max": np.max(v["bpm_rms_y"]),
                "bpm_rmsy_min": np.min(v["bpm_rms_y"]),

            })
        #
        df = pd.DataFrame(rows)
        df["bpmphase_normal"] = bpmphase_normal
        df["energy_normal"] = energy_normal


        # print(df)
        df.to_excel(f"d_e_{i}.xlsx", index=False)

