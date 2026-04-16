import sys

from dataprovision.beamset import BeamsetParameter
import math
from global_varible import c_light, Pi

import struct
import os
import numpy
from utils.getinfotools import get_mass_freq, get_timestep
import numpy as np
from dataprovision.datasetparameter import DatasetParameter
import time
from multiprocessing import Pool, cpu_count
from dataprovision.densityparameter import DensityParameter
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataprovision.exdataparameter import Exdata
import pandas as pd

def read_exdata_onestep_worker(args):
    # print(args)
    # index0 plt中的索引
    ex_data_this, dataset_info, dataset_index_list = args

    # exdata中的index
    ex_index = ex_data_this["index"]

    if ex_index in dataset_index_list:
        index_dataset = dataset_index_list.index(ex_index)
    else:
        return {}

    zg = ex_data_this["z_ave"]

    emit = [dataset_info["emit_x"][index_dataset], dataset_info["emit_y"][index_dataset], dataset_info["emit_z"][index_dataset]]
    rms_size = [dataset_info["rms_x"][index_dataset], dataset_info["rms_y"][index_dataset], dataset_info["rms_z"][index_dataset]]

    nownumofp = int(dataset_info["number_exist"][index_dataset])
    moy = [ex_data_this["x_ave"], ex_data_this["y_ave"], ex_data_this["r_ave"], 0]

    # 应该是相对于中心的偏移值，但是这里的z不知道中心值是谁，只能相对于自己的中心值，等后处理加上中心值的偏移
    maxb = [ex_data_this["x_max"], ex_data_this["y_max"], ex_data_this["r_max"], ex_data_this["z_max"] - zg]
    minb = [ex_data_this["x_min"], ex_data_this["y_min"], ex_data_this["r_min"], ex_data_this["z_min"] - zg]

    maxr = maxb
    minr = minb

    tab = [ex_data_this["tab_x"], ex_data_this["tab_y"], ex_data_this["tab_r"], ex_data_this["tab_z"]]

    # t3 = time.time()
    # dt3 = t3-t2
    # self.dt3 += dt3
    res = {}
    res["zg"] = zg
    res["emit"] = emit
    res["rms_size"] = rms_size
    res["nownumofp"] = nownumofp
    res["moy"] = moy
    res["maxb"] = maxb
    res["minb"] = minb
    res["maxr"] = maxr
    res["minr"] = minr
    res["tab"] = tab

    return res


class ExtoDensity():
    def __init__(self,  exdata_path, dataset_path, target_density_path, normal_density_path=None, project_path=None):
        self.project_path = project_path
        self.exdata_path = exdata_path
        self.dataset_path = dataset_path
        self.target_density_path = target_density_path
        self.normal_density_path = normal_density_path

        self.bins = 300




    def generatet_density_data_onestep(self, isnormal):
        """
        使用多进程并行生成密度数据
        """
        # dataset_obj = DatasetParameter(self.dataset_path)
        # dataset_obj.get_parameter()
        #
        # #dataset中所有的序号
        # dataset_index_list = dataset_obj.dataset_index
        #
        # ex_data_obj = Exdata(self.exdata_path)
        # ex_data_list = ex_data_obj.get_param()
        # all_step = ex_data_obj.step
        # print(f"总步长是{all_step}")
        #
        # # print(all_step)
        #
        # # breakpoint()
        # # 使用进程池并行处理每一步的数据
        #
        # num_workers = max(cpu_count() - 3, 1)  # 根据 CPU 核心数动态调整
        # # num_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))
        # print(f"使用的 CPU 数量: {num_workers}")
        #
        # v1 = [i for i in range(0, all_step-1)]
        # step_list = v1
        #
        # dataset_info = {
        #     "emit_x": dataset_obj.emit_x,
        #     "emit_y": dataset_obj.emit_y,
        #     "emit_z": dataset_obj.emit_z,
        #     "rms_x": dataset_obj.rms_x,
        #     "rms_y": dataset_obj.rms_y,
        #     "rms_z": dataset_obj.rms_z,
        #     "number_exist": dataset_obj.number_exist,
        #
        # }
        #
        # t0 = time.time()
        # print(f"cpu数量{cpu_count()}")
        # with Pool(num_workers) as pool:  # 使用上下文管理器
        #     # 准备每一步的参数
        #     args = [(ex_data_list[i], dataset_info, dataset_index_list) for i in step_list]
        #
        #     # 使用进程池并行执行每一步数据处理
        #
        #     results = pool.map(read_exdata_onestep_worker, args)
        #
        # t1 = time.time()
        # dt10 = t1 - t0
        # print(f"多线程时间{dt10}")
        #
        # # 使用普通for循环串行执行每一步数据处理
        # t2 = time.time()
        # args = [(ex_data_list[i], dataset_info, dataset_index_list) for i in step_list]
        # results = []
        # for arg in args:
        #     result = read_exdata_onestep_worker(arg)
        #     results.append(result)
        #
        # t3 = time.time()
        # dt32 = t3 - t2
        # print(f"单线程时间{dt32}")

################################################################
        # results = []
        # # 收集并整理结果
        # for i in step_list:
        #     args = (dataset_obj, i, dataset_index_list)
        #     results.append(self.read_beamset_onestep_worker(args))

        # with ThreadPoolExecutor(max_workers=20) as executor:
        #     # 准备每一步的参数
        #     args = [(dataset_obj, i, dataset_index_list) for i in range(all_step)]
        #
        #     # 提交任务到线程池，将 Future 与步骤索引关联
        #     future_to_step = {executor.submit(self.read_beamset_onestep_worker, arg): arg[1] for arg in args}
        #
        #     # 收集结果
        #     results = []
        #     for future in as_completed(future_to_step):
        #         step_index = future_to_step[future]  # 获取任务的步骤索引
        #         result = future.result()  # 获取任务结果
        #         results.append((step_index, result))  # 将步骤索引与结果关联
        #
        #         # try:
        #         #     result = future.result()  # 获取任务结果
        #         #     results.append((step_index, result))  # 将步骤索引与结果关联
        #         # except Exception as e:
        #         #     print(f"Step {step_index} raised an exception: {e}")
        #
        # # 排序结果，确保按照步骤索引顺序返回
        # results.sort(key=lambda x: x[0])
        # results = [res[1] for res in results]  # 提取最终结果
##################################################################
        dataset_obj = DatasetParameter(self.dataset_path)
        dataset_obj.get_parameter()
        t0 = time.time()
        ds_df = pd.DataFrame({
            "index": dataset_obj.dataset_index,
            "emit_x": dataset_obj.emit_x,
            "emit_y": dataset_obj.emit_y,
            "emit_z": dataset_obj.emit_z,
            "rms_x": dataset_obj.rms_x,
            "rms_y": dataset_obj.rms_y,
            "rms_z": dataset_obj.rms_z,
            "number_exist": dataset_obj.number_exist,
        })

        # 2. 读取 exdata → DataFrame
        ex_data_obj = Exdata(self.exdata_path)
        ex_df = pd.DataFrame(ex_data_obj.get_param())  # 每行就是一步
        # pd.set_option('display.max_columns', None)

        all_step = len(ex_df)  # == ex_data_obj.step

        # 3. merge 只做一次匹配，避免 Python for 查表
        merged = ex_df.merge(ds_df, on="index", how="inner", copy=False)

        # -------- 下面把各列一次性转成 NumPy 数组 ----------
        zg = merged["z_ave"].to_numpy(dtype=np.float32)

        emit = merged[["emit_x", "emit_y", "emit_z"]].to_numpy(dtype=np.float32)
        rms_size = merged[["rms_x", "rms_y", "rms_z"]].to_numpy(dtype=np.float32)

        nownumofp = merged["number_exist"].to_numpy(dtype=np.int32)

        moy = merged[["x_ave", "y_ave", "r_ave"]].to_numpy(dtype=np.float32)
        moy = np.column_stack([moy, np.zeros_like(zg)])  # 第 4 列占位

        z_max_shift = (merged["z_max"].to_numpy(dtype=np.float32) - zg)
        z_min_shift = (merged["z_min"].to_numpy(dtype=np.float32) - zg)


        maxb = np.column_stack([merged[["x_max", "y_max", "r_max"]], z_max_shift]).astype(np.float32)
        minb = np.column_stack([merged[["x_min", "y_min", "r_min"]], z_min_shift]).astype(np.float32)

        maxr = maxb.copy()
        minr = minb.copy()

        tab = merged[["tab_x", "tab_y", "tab_r", "tab_z"]].to_numpy(object)

        # 4. 打包成原来期望的 results (list[dict])，后面代码可直接复用
        results = [
            {
                "zg": zg[i],
                "emit": emit[i],
                "rms_size": rms_size[i],
                "nownumofp": int(nownumofp[i]),
                "moy": moy[i],
                "maxb": maxb[i],
                "minb": minb[i],
                "maxr": maxr[i],
                "minr": minr[i],
                "tab": tab[i],  # [tab_x, tab_y, tab_r, tab_z]
            }
            for i in range(len(zg))
        ]
        t1 = time.time()
        dt = t1-t0
        print(f"新算法时间{dt}")
######################################################################################
        results = list(filter(bool, results))

        zg_lis = [res["zg"] for res in results]
        emit_lis = [res["emit"] for res in results]
        rms_size_lis = [res["rms_size"] for res in results]
        nownumofp_lis = [res["nownumofp"] for res in results]
        moy_lis = [res["moy"] for res in results]
        maxb_lis = [res["maxb"] for res in results]
        minb_lis = [res["minb"] for res in results]
        maxr_lis = [res["maxr"] for res in results]
        minr_lis = [res["minr"] for res in results]
        tab_lis = [res["tab"] for res in results]

        lost_lis = [0] + [nownumofp_lis[i] - nownumofp_lis[i - 1] for i in range(1, len(nownumofp_lis))]
        lost_lis = lost_lis
        maxlost_lis = lost_lis
        minlost_lis = lost_lis
        # print(zg_lis)
        if isnormal == 0:
            density_normal_obj = DensityParameter(self.normal_density_path)
            normal_data = density_normal_obj.get_parameter()
            normal_zg_lis = np.array(normal_data["zg_lis"])

            normal_step = len(normal_zg_lis)

            if normal_step <= len(zg_lis):
                #如果这次模拟步数多于正常模拟
                delta_zg = np.array(zg_lis)[:normal_step] - normal_zg_lis

                emit_lis = emit_lis[0:normal_step]
                rms_size_lis = rms_size_lis[0:normal_step]
                nownumofp_lis = nownumofp_lis[0:normal_step]
                lost_lis = lost_lis[0:normal_step]
                minlost_lis = minlost_lis[0:normal_step]
                maxlost_lis = maxlost_lis[0:normal_step]

                moy_lis = np.array(moy_lis)[0:normal_step]
                moy_lis[:, 3] = delta_zg

                maxb_lis = np.array(maxb_lis)[0:normal_step]
                maxb_lis[:, 3] += delta_zg

                minb_lis = np.array(minb_lis)[0:normal_step]
                minb_lis[:, 3] += delta_zg

                maxr_lis = np.array(maxr_lis)[0:normal_step]
                maxr_lis[:, 3] += delta_zg

                minr_lis = np.array(minr_lis)[0:normal_step]
                minr_lis[:, 3] += delta_zg

                tab_lis = tab_lis[0:normal_step]
                zg_lis = normal_zg_lis


            elif normal_step > len(zg_lis):
                last_step_zg = zg_lis[-1] - zg_lis[-2]

                delta_step = normal_step - len(zg_lis)

                for i in range(delta_step):
                    next_z = zg_lis[-1] + last_step_zg
                    zg_lis.append(next_z)
                    # zg_lis = np.append(zg_lis, next_z)
                # print(len(zg_lis))
                # print(normal_zg_lis[-10:])
                # print(zg_lis[-10:])
                delta_zg = np.array(zg_lis) - normal_zg_lis

                emit_lis = emit_lis + [emit_lis[-1]] * delta_step
                # print(emit_lis)
                rms_size_lis = rms_size_lis + [rms_size_lis[-1]] * delta_step
                nownumofp_lis = nownumofp_lis + [nownumofp_lis[-1]] * delta_step


                moy_lis = np.array(moy_lis + [moy_lis[-1]] * delta_step)

                moy_lis[:, 3] = delta_zg

                maxb_lis = np.array(maxb_lis + [maxb_lis[-1]] * delta_step)
                maxb_lis[:, 3] += delta_zg

                minb_lis = np.array(minb_lis + [minb_lis[-1]] * delta_step)
                minb_lis[:, 3] += delta_zg

                maxr_lis = np.array(maxr_lis + [maxr_lis[-1]] * delta_step)
                maxr_lis[:, 3] += delta_zg

                minr_lis = np.array(minr_lis + [minr_lis[-1]] * delta_step)
                minr_lis[:, 3] += delta_zg

                tab_lis = tab_lis + [tab_lis[-1]] * delta_step

                lost_lis = lost_lis + [0] * delta_step
                minlost_lis = minlost_lis + [0] * delta_step
                maxlost_lis = maxlost_lis + [0] * delta_step
                zg_lis = normal_zg_lis

        res = {}
        res["zg_lis"] = zg_lis
        res["emit_lis"] = emit_lis
        res["rms_size_lis"] = rms_size_lis
        res["nownumofp_lis"] = nownumofp_lis
        res["lost_lis"] = lost_lis
        res["maxlost_lis"] = maxlost_lis
        res["minlost_lis"] = minlost_lis
        res["moy_lis"] = moy_lis
        res["maxb_lis"] = maxb_lis
        res["minb_lis"] = minb_lis
        res["maxr_lis"] = maxr_lis
        res["minr_lis"] = minr_lis
        res["tab_lis"] = tab_lis

        return res

    def write_file(self, path, data):
        self.bins = len(data["tab_lis"][0][0])
        binary_data = []  # 使用列表来存储中间结果，减少拼接操作
        binary_data.append(struct.pack("i", len(data["zg_lis"])))  # 文件共有多少步
        binary_data.append(struct.pack("i", self.bins))  # 网格划分步数

        for i in range(len(data["zg_lis"])):
            binary_data.append(struct.pack('f', data["zg_lis"][i]))  # 打包 zg_lis
            binary_data.append(struct.pack('f' * 3, *data["emit_lis"][i]))  # 打包 emit_lis
            binary_data.append(struct.pack('f' * 3, *data["rms_size_lis"][i]))  # 打包 rms_size
            binary_data.append(struct.pack('i', data["nownumofp_lis"][i]))  # 打包 nownumofp_lis
            binary_data.append(struct.pack('i', data["lost_lis"][i]))  # 打包 lost_lis
            binary_data.append(struct.pack('i', data["maxlost_lis"][i]))  # 打包 maxlost_lis
            binary_data.append(struct.pack('i', data["minlost_lis"][i]))  # 打包 minlost_lis

            binary_data.append(struct.pack('f' * 4, *data["moy_lis"][i]))
            binary_data.append(struct.pack('f' * 4, *data["maxb_lis"][i]))
            binary_data.append(struct.pack('f' * 4, *data["minb_lis"][i]))
            binary_data.append(struct.pack('f' * 4, *data["maxr_lis"][i]))
            binary_data.append(struct.pack('f' * 4, *data["minr_lis"][i]))

            binary_data.append(struct.pack('i' * self.bins, *data["tab_lis"][i][0]))
            binary_data.append(struct.pack('i' * self.bins, *data["tab_lis"][i][1]))
            binary_data.append(struct.pack('i' * self.bins, *data["tab_lis"][i][2]))
            binary_data.append(struct.pack('i' * self.bins, *data["tab_lis"][i][3]))

        # 最后统一写入文件
        with open(path, "wb") as f:
            f.write(b''.join(binary_data))  # 使用 join 一次性写入

    def generate_density_file_onestep(self, isnormal):
        data = self.generatet_density_data_onestep(isnormal)
        self.write_file(self.target_density_path, data)


class MergeDensityData(ExtoDensity):
    def __init__(self, source_paths, target_path):
        self.source_paths = source_paths
        self.target_path = target_path
        self.bins = 300

    def generate_data(self):
        all_data = []

        for path in self.source_paths:
            density_obj = DensityParameter(path)
            data = density_obj.get_parameter()
            all_data.append(data)
        res = {}
        zg_lis = all_data[0]["zg_lis"]
        # print(zg_lis)
        data_length = len(all_data)

        # for i in range(data_length):
        #     print(414, len(all_data[i]["emit_lis"]))

        all_emit_lis = np.array([all_data[i]["emit_lis"] for i in range(data_length)])
        emit_lis = np.mean(all_emit_lis, axis=0)

        all_rms_size_lis = np.array([all_data[i]["rms_size_lis"] for i in range(data_length)])
        rms_size_lis = np.mean(all_rms_size_lis, axis=0)

        all_nownumofp_lis = np.array([all_data[i]["nownumofp_lis"] for i in range(data_length)])
        nownumofp_lis = np.mean(all_nownumofp_lis, axis=0).astype(int)

        all_lost_lis = np.array([all_data[i]["lost_lis"] for i in range(data_length)])
        lost_lis = np.mean(all_lost_lis, axis=0).astype(int)
        maxlost_lis = np.max(all_lost_lis, axis=0)
        minlost_lis = np.min(all_lost_lis, axis=0)

        all_moy_lis = np.array([all_data[i]["moy_lis"] for i in range(data_length)])
        moy_lis = np.mean(all_moy_lis, axis=0)

        all_maxb_lis = np.array([all_data[i]["maxb_lis"] for i in range(data_length)])
        maxb_lis = np.max(all_maxb_lis, axis=0)

        all_minb_lis = np.array([all_data[i]["minb_lis"] for i in range(data_length)])
        minb_lis = np.min(all_minb_lis, axis=0)

        #最大值中的最小值
        all_maxr_lis = np.array([all_data[i]["maxr_lis"] for i in range(data_length)])
        maxr_lis = np.min(all_maxr_lis, axis=0)  # 注意！

        #最小值中的最大值
        all_minr_lis = np.array([all_data[i]["minr_lis"] for i in range(data_length)])
        minr_lis = np.max(all_minr_lis, axis=0)  # 注意！


        all_tab_lis = [all_data[i]["tab_lis"] for i in range(data_length)]

        self.bins = density_obj.grid_num
        combined_counts = []


        #一共多少步
        for i in range(len(zg_lis)):
            # print(i)
            combined_x = np.array([0 for i1 in range(self.bins)])
            combined_y = np.array([0 for i1 in range(self.bins)])
            combined_r = np.array([0 for i1 in range(self.bins)])
            combined_z = np.array([0 for i1 in range(self.bins)])

            new_min_x = minb_lis[i][0]
            new_min_y = minb_lis[i][1]
            new_min_r = minb_lis[i][2]
            new_min_z = minb_lis[i][3]

            new_max_x = maxb_lis[i][0]
            new_max_y = maxb_lis[i][1]
            new_max_r = maxb_lis[i][2]
            new_max_z = maxb_lis[i][3]

            for j in range(data_length):
                ori_min_x = all_minb_lis[j][i][0]
                ori_min_y = all_minb_lis[j][i][1]
                ori_min_r = all_minb_lis[j][i][2]
                ori_min_z = all_minb_lis[j][i][3]

                ori_max_x = all_maxb_lis[j][i][0]
                ori_max_y = all_maxb_lis[j][i][1]
                ori_max_r = all_maxb_lis[j][i][2]
                ori_max_z = all_maxb_lis[j][i][3]

                xbins = np.linspace(new_min_x, new_max_x, self.bins+1)
                # print(xbins)
                countsx_rescaled, _ = np.histogram(np.linspace(ori_min_x, ori_max_x, self.bins), bins=xbins,
                                                    weights=all_tab_lis[j][i][0])



                combined_x += countsx_rescaled

                ybins = np.linspace(new_min_y, new_max_y, self.bins+1)
                countsy_rescaled, _ = np.histogram(np.linspace(ori_min_y, ori_max_y, self.bins), bins=ybins,
                                                    weights=all_tab_lis[j][i][1])


                combined_y += countsy_rescaled

                rbins = np.linspace(new_min_r, new_max_r, self.bins+1)
                countsr_rescaled, _ = np.histogram(np.linspace(ori_min_r, ori_max_r, self.bins), bins=rbins,
                                                   weights=all_tab_lis[j][i][2])
                combined_r += countsr_rescaled

                zbins = np.linspace(new_min_z, new_max_z, self.bins+1)
                countsz_rescaled, _ = np.histogram(np.linspace(ori_min_z, ori_max_z, self.bins), bins=zbins,
                                                   weights=all_tab_lis[j][i][3])
                combined_z += countsz_rescaled

            v_lis = [combined_x, combined_y, combined_r, combined_z]
            combined_counts.append(v_lis)
        tab_lis = combined_counts

        res["zg_lis"] = zg_lis
        res["emit_lis"] = emit_lis
        res["rms_size_lis"] = rms_size_lis
        res["nownumofp_lis"] = nownumofp_lis
        res["lost_lis"] = lost_lis
        res["maxlost_lis"] = maxlost_lis
        res["minlost_lis"] = minlost_lis
        res["moy_lis"] = moy_lis
        res["maxb_lis"] = maxb_lis
        res["minb_lis"] = minb_lis
        res["maxr_lis"] = maxr_lis
        res["minr_lis"] = minr_lis
        res["tab_lis"] = tab_lis

        return res
    def generate_density_file(self):
        data = self.generate_data()
        self.write_file(self.target_path, data)

if __name__ == "__main__":
    exdata_path = r"C:\Users\wangh\Desktop\hiaf_v2\result\output_0\PCHistogram.dat"
    dataset_path = r"C:\Users\wangh\Desktop\hiaf_v2\result\output_0\DataSet.txt"
    target_density_path = r"C:\Users\wangh\Desktop\hiaf_v2\result\density_par_2_100.dat"
    normal_density_path = r"C:\Users\wangh\Desktop\hiaf_v2\result\density_par_0_0.dat"

    obj = ExtoDensity(exdata_path, dataset_path, target_density_path, normal_density_path)

    obj.generate_density_file_onestep(isnormal=1)




    #
    #
    # # beamset_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_1_1\BeamSet.plt"
    # # dataset_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_1_1\DataSet.txt"
    # # target_density_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_1_1\density_1_1.dat"
    # # normal_density_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_0_0\density_0_0.dat"
    # # project_path = r"C:\Users\shliu\Desktop\testz"
    #
    # # obj = PlttoDensity(beamset_path, dataset_path, target_density_path, normal_density_path, project_path)
    # # obj.generate_density_file_onestep(isnormal=0)
    #
    # # beamset_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_1_2\BeamSet.plt"
    # # dataset_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_1_2\DataSet.txt"
    # # target_density_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_1_2\density_1_2.dat"
    # # normal_density_path = r"C:\Users\shliu\Desktop\testz\OutputFile\error_output\output_0_0\density_0_0.dat"
    # # project_path = r"C:\Users\shliu\Desktop\testz"
    #
    # # obj = PlttoDensity(beamset_path, dataset_path, target_density_path, normal_density_path, project_path)
    # # obj.generate_density_file_onestep(isnormal=0)
    #
    # paths = [
    #     r"C:\Users\wangh\Desktop\likai_duibi\02_AVAS_Env_error\OutputFile\density_par_0_0.dat",
    #     r"C:\Users\wangh\Desktop\likai_duibi\02_AVAS_Env_error\OutputFile\density_par_1_1.dat",
    # ]
    #
    # target_path = r"C:\Users\wangh\Desktop\likai_duibi\02_AVAS_Env_error\OutputFile\density_tot.dat"
    # obj = MergeDensityData(paths, target_path)
    # obj.generate_density_file()