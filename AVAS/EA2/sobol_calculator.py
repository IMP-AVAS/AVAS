import os
import json
import h5py
import numpy as np


class SobolCalculator:
    def __init__(self, input_h5_path, output_json_path):
        """
        初始化计算器
        :param input_h5_path: 输入的 HDF5 文件路径
        :param output_json_path: 输出的 JSON 保存路径
        """
        self.input_h5_path = input_h5_path
        self.output_json_path = output_json_path

    def calculate_round(self, round_num):
        """
        读取数据并计算 Sobol 因子
        :param round_id: 轮次 ID (整数)，例如 1 对应 round_001
        """
        # 1. 基础检查
        if not os.path.exists(self.input_h5_path):
            print(f"[错误] 找不到输入文件: {self.input_h5_path}")
            return

        # 准备数据结构
        effect = {
            'ST': {},  # 总效应
            'S': {}  # 一阶效应
        }

        # 拼接组名
        print(f"[-] 正在读取文件: {self.input_h5_path}")

        data_dic = {}

        with h5py.File(self.input_h5_path, "r") as f:
            round_name_list = list(f.keys())[:round_num]
            key_in_round_list = list(f[round_name_list[0]].keys())

            for key in key_in_round_list:
                data_list = []

                for round_name in round_name_list:
                    data = f[round_name][key][()]
                    data_list.append(data)

                data_dic[key] = np.concatenate(data_list, axis=0)


        y_a = np.array(data_dic['input_A'])
        y_b = np.array(data_dic['input_B'])

        # 2. 循环计算 (检测 input_Au_0, input_Au_1 ...)
        i = 0
        while f'input_Au_{i}' in data_dic and f'input_Bu_{i}' in data_dic:
            # 读取重采样矩阵输出
            y_a_u = np.array(data_dic[f'input_Au_{i}'])
            y_b_u = np.array(data_dic[f'input_Bu_{i}'])

            # --- Sobol 计算公式 ---
            # 分母：总方差 (Total Variance proxy)
            denominator = sum((y_a - y_b) ** 2 + (y_a_u - y_b_u) ** 2)

            numerator_s = sum((y_b - y_b_u) ** 2 + (y_a - y_a_u) ** 2)
            S_u = 1 - numerator_s / denominator

            # 总效应敏感度 ST
            numerator_st = sum((y_b - y_a_u) ** 2 + (y_a - y_b_u) ** 2)
            ST_u = numerator_st / denominator

            # 存入结果
            effect['S'][i] = S_u.tolist() if isinstance(S_u, np.ndarray) else S_u
            effect['ST'][i] = ST_u.tolist() if isinstance(ST_u, np.ndarray) else ST_u

            i += 1

        print(f"[-] 计算完毕，共处理了 {i} 个变量。")


        with open(self.output_json_path, 'w', encoding='utf-8') as f:
            json.dump(effect, f, indent=4)

        return effect


# ==========================================
#              主程序入口
# ==========================================
if __name__ == "__main__":
    # --- 在这里直接修改配置 ---


    # 1. 输入文件路径 (确保路径正确)
    H5_FILE_PATH = r"C:\Users\shliu\Desktop\eatest\EA_CAFe_MEBT2\001analysis\data_dir\OutData.h5"

    # 2. 输出文件路径
    JSON_SAVE_PATH = r'C:\Users\shliu\Desktop\eatest\EA_CAFe_MEBT2\001analysis\data_dir\OutData.json'

    # 3. 轮次 ID (对应 round_001, round_002 等)
    ROUND_ID = 0

    # --- 执行 ---
    calculator = SobolCalculator(H5_FILE_PATH, JSON_SAVE_PATH)
    calculator.calculate_round(round_num=10**5)


