#该文件为AVAS t_code可视化的一部分，对plt中某一步或者
#在该处强调，beamset中步数是多于dataset中的

#对plt文件中的某一步进行处理，得到可以用来画图的数据


from dataprovision.beamset import BeamsetParameter

from dataprovision.datasetparameter import DatasetParameter
import pandas as pd
import os
import numpy as np
import global_varible

class TreatPlt():
    def __init__(self, item):

        self.plt_path = item.get("plt_path")
        self.project_path = item.get("project_path")



    def get_dataset_plt_base_info(self):
        #
        dataset_path = os.path.join(self.project_path, "OutputFile", "DataSet.txt")

        dataset_obj = DatasetParameter(dataset_path)
        dataset_obj.get_parameter()


        # dataset中总的步长数
        dataset_num = len(dataset_obj.dataset_index)

        self.dataset_index_list = dataset_obj.dataset_index
        self.dataset_z_list = dataset_obj.z

        self.plt_obj = BeamsetParameter(self.plt_path)
        #plt中一共有多少步

        plt_step = self.plt_obj.get_step()

        #所有步数的dict
        all_step_dict = self.plt_obj.get_all_dict()

        self.plt_index_list = [i["index"] for i in all_step_dict]

        self.np = self.plt_obj.numofp
        self.Ib = self.plt_obj.Ib
        self.freq = self.plt_obj.freq * 10 ** 6  # 变成Hz
        self.BaseMassInMeV = self.plt_obj.BaseMassInMeV


        self.dataset_df = pd.DataFrame({
            "index": dataset_obj.dataset_index,
            "cx": dataset_obj.syn_x,
            "cy": dataset_obj.syn_y,
            "t_z": dataset_obj.ek
        })


        return dataset_num



    def get_num_to_dataset_plt(self, num):
        #该函数的功能是根据用户使用的num，推断出使用的index，dataset和plt文件对应的步数
        dataset_index = self.dataset_index_list[num]

        plt_num = self.plt_index_list.index(dataset_index)

        return plt_num



    def get_parameter_one_step(self, num ):

        self.plt_obj.get_one_parameter(num)


        m0 = self.BaseMassInMeV

        part_dict =  self.plt_obj.one_step_dict
        part_list =  self.plt_obj.one_step_list   #粒子分布数据

        target_index = int(part_dict["index"])
        matched = self.dataset_df[self.dataset_df["index"] == target_index]

        row = matched.iloc[0]
        syn_cx = row["cx"]
        syn_cy = row["cy"]
        syn_tz = row["t_z"] #纵向能量
        # print(part_list)

        part_arr = np.array(part_list.tolist())

        part_arr[: , 0] += syn_cx
        part_arr[: , 2] += syn_cy
        # print(part_arr)

        #没有丢失的粒子
        exist_particle = part_arr[np.isclose(part_arr[:, 6], 1)]


        #同步粒子的信息
        syn_gamma = 1 + syn_tz/m0
        syn_betaz = np.sqrt(1-1/(syn_gamma ** 2))
        syn_speedz = syn_betaz * global_varible.c_light

        #pz = beta * gamma
        uz = exist_particle[:, 5]

        # 若 uz 可能带符号，保留符号更自然
        gamma_z = np.sqrt(1.0 + uz ** 2)
        beta_z = uz / gamma_z
        e_z = (gamma_z - 1.0) * m0  #纵向能量，也就是纵向动能
        v_z = beta_z * global_varible.c_light

        # 相对速度偏差（无量纲）
        z1 = (v_z - syn_speedz) / syn_speedz

        # 相对动量偏差 dp/p_s
        dp_p = (gamma_z * beta_z - syn_gamma * syn_betaz) / (syn_gamma * syn_betaz)

        t = -(exist_particle[:, 4] / v_z)
        phi = t * 2 * global_varible.Pi * self.freq

        n = exist_particle.shape[0]
        new_particle = np.zeros((n, 16), dtype=exist_particle.dtype)
        new_particle[:, :8] = exist_particle

        new_particle[:, 8] = exist_particle[:, 1] / exist_particle[:, 5]
        new_particle[:, 9] = exist_particle[:, 3] / exist_particle[:, 5]
        new_particle[:, 10] = z1
        new_particle[:, 11] = dp_p
        new_particle[:, 12] = phi
        new_particle[:, 13] = e_z

        self.mean_energy =  np.mean(e_z)
        new_particle[:, 14] = e_z - self.mean_energy
        new_particle[:, 15] = new_particle[:, 11] * 100

        exist_particle = new_particle

        #返回的数据格式
        #[x ,px, y, py,z, pz, loss ,index, x1, y1,z1. dp_p, phi]

        # for i in exist_particle:
        #     beta_z = np.sqrt(i[5]**2/(1+i[5]**2))
        #     gamma_z = 1/np.sqrt(1-beta_z**2)
        #     t_z = (gamma_z -1) * self.BaseMassInMeV
        #     v_z = beta_z * global_varible.c_light
        #     z1 = (v_z - syn_speedz ) / syn_speedz
        #     dp_p =(gamma_z * v_z - syn_gamma * syn_speedz) / (syn_gamma * syn_speedz)
        #
        #
        self.number = len(exist_particle)


        dst_dict = {

            "number": self.number,
            "freq": self.freq,
            "BaseMassInMeV": self.BaseMassInMeV,
            "Ib": self.Ib,
            "energy": self.mean_energy,
            "gamma": syn_gamma,
            "beta": syn_betaz,

            "x": exist_particle[:, 0] * 1000,
            "px": exist_particle[:, 1],
            "y": exist_particle[:, 2] * 1000,
            "py": exist_particle[:, 3],
            "z": exist_particle[:, 4] * 1000,
            "pz": exist_particle[:, 5],
            "loss": exist_particle[:, 6],
            "index": exist_particle[:, 7],
            "x1": exist_particle[:, 8] * 1000,
            "y1": exist_particle[:, 9] * 1000,
            "z1": exist_particle[:, 10] * 1000,
            "dp_p": exist_particle[:, 11] ,

            "phi": exist_particle[:, 12] * 180 /global_varible.Pi,
            "w": exist_particle[:, 13],
            "w_minus_mean": exist_particle[:, 14],
            "dp_p_100": exist_particle[:, 15],

        }
        return part_arr, exist_particle, dst_dict



if __name__ == "__main__":
    item = {
        "plt_path": r"C:\Users\wangh\Desktop\phase_plot\v1\OutputFile\BeamSet.plt",
        "project_path": r"C:\Users\wangh\Desktop\phase_plot\v1",
    }
    plot_obj = TreatPlt(item)
    plot_obj.get_all_plt_dict()
    # dataset_df = plot_obj.get_dataset_parameter()
    # parameter = plot_obj.get_parameter_one_step(300, dataset_df)
    # print(parameter)