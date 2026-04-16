import sys
avas_path = r'/public/home/lzy_gpu/li1221/AVAS_control'
sys.path.append(avas_path)

# import sys
# avas_path = r'/public/home/lzy_gpu/li1221/AVAS_control'
# sys.path.append(avas_path)

import os
import pandas as pd
from datetime import timedelta
import numpy as np
from dataprovision.datasetparameter import DatasetParameter
pd.set_option("display.max_columns", None)
from read_dataset import read_dataset_dast

def get_bpm(dataset_path, project_path,  posi):
    data = read_dataset_dast(dataset_path)


    z = np.asarray(data["cz"])  # 确保是 numpy array
    # 找到第一个 > posi 的位置，再减 1 => 最后一个 <= posi
    idx = np.searchsorted(z, posi, side="right") - 1
    idx = int(np.clip(idx, 0, len(z) - 1))

    return {
        "bpm_x": data["cx"][idx] * 1000,
        "bpm_y": data["cy"][idx] * 1000,
        "bpm_phase": data["phase"][idx],
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

def get_one_group_res(bpm_name, bpm_posi, dataset_path_base, project_path,  group):
    dataset_paths = [os.path.join(dataset_path_base, f"output_{group}_{i}", "DataSet.txt") for i in range(1,3)]

    one_group_res = []

    for i in range(len(dataset_paths)):
        one_time_res = {}
        v_index = 1
        for j in range(len(bpm_posi)):

            dataset_path = dataset_paths[i]
            print(i, v_index)
            v_index +=1

            res = get_bpm(dataset_path, project_path, bpm_posi[j])
            one_time_res[ bpm_name[j]] = res
        one_group_res.append(one_time_res)
    # print(one_group_res)

    bpm_one_group_dict = {i: {"bpm_x": [], "bpm_y": [], "bpm_phase": [],} for i in bpm_name}
    for i in bpm_name:
        for j in one_group_res:
            bpm_one_group_dict[i]["bpm_x"].append(j[i]["bpm_x"])
            bpm_one_group_dict[i]["bpm_y"].append(j[i]["bpm_y"])
            bpm_one_group_dict[i]["bpm_phase"].append(j[i]["bpm_phase"])

    return bpm_one_group_dict
if __name__ == "__main__":

    bpm_table = r"/public/home/lzy_gpu/li1221/ana_err_bpm/bpm_v2.xlsx"
    df_bpmphase = pd.read_excel(bpm_table, )

    bpm_name = df_bpmphase["name_bpm"].tolist()
    bpm_posi = df_bpmphase["bpm_posi"].tolist()
    dataset_path_base = r"/public/home/lzy_gpu/li1221/AVAS_HIAF_dxy/OutputFile/error_output"
    project_path =  r"/public/home/lzy_gpu/li1221/AVAS_HIAF_dxy"
    bpm_one_group_dict = get_one_group_res(bpm_name, bpm_posi, dataset_path_base, project_path, 1)
    # print(bpm_one_group_dict)

    rows = []
    for bpm, v in bpm_one_group_dict.items():
        rows.append({
            "bpm_name": bpm,
            "bpm_x": v["bpm_x"],
            "bpm_y": v["bpm_y"],
            "bpm_phase": v["bpm_phase"],

            "bpmx_max": np.max(v["bpm_x"]),
            "bpmx_min": np.min(v["bpm_x"]),

            "bpmy_max": np.max(v["bpm_y"]),
            "bpmy_min": np.min(v["bpm_y"]),

            "bpmphase_max": np.max(v["bpm_phase"]),
            "bpmphase_min": np.min(v["bpm_phase"]),

        })

    df = pd.DataFrame(rows)
    # print(df)
    df.to_excel("dxy_g1.xlsx", index=False)


    # for k , v in bpm_one_group_dict.items():
    #     v["bpmx_max"] = np.max(v["bpm_x"])
    #     v["bpmy_max"] = np.max(v["bpm_y"])
    #     v["bpmphase_max"] = np.max(v["bpm_phase"])
    #
    # # print(bpm_one_group_dict)
    #
    # df_base = []
    # for k ,v in bpm_one_group_dict.items():
    #     df_base.append(v)
    #
    # df = pd.DataFrame(df_base)
    # df["bpm_name"] = bpm_name
    # print(df)

    #
    # import pandas as pd
    #
    # rows = []
    # for bpm, vals in bpm_one_group_dict.items():
    #     rows.append({
    #         "bpm": bpm,
    #         "bpm_x": vals["bpm_x"][0],
    #         "bpm_y": vals["bpm_y"][0],
    #         "bpm_phase": vals["bpm_phase"][0],
    #     })
    #
    # df = pd.DataFrame(rows)
    # print(df)

    # {'bpm1-1': {'bpm_x': [6.30263e-06, 6.30263e-06, 6.30263e-06],
    #             'bpm_y': [-9.23497e-05, -9.23497e-05, -9.23497e-05],
    #             'bpm_phase': [423.62190000000004, 423.62190000000004, 423.62190000000004]},
    #
    #  'bpm1-2': {'bpm_x': [6.60078282e-06, 6.60078282e-06, 6.60078282e-06],