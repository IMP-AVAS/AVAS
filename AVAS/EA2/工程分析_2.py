import math
import os
import shutil
import json
import subprocess
from multiprocessing import Pool, cpu_count
import time
import datetime
import h5py
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# 设置中文字体（Windows 推荐使用 SimHei，Linux 可用 SimSun 或 NotoSansCJK）
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题

MRAD_TO_DEGREE = 180 / (math.pi * 1000)  # 毫弧度转度


def format_sign_space(x):
    if x >= 0:
        return f" {x:.16f}"  # 正数前空一格，无符号
    else:
        return f"{x:.16f}"  # 负数直接带负号，不空格


class EA:
    """
    工程分析工具类

    项目结构说明：

    project_root/
    │
    ├── bases_dir/                          # 存放 base_template 文件夹和 TraceWin 执行程序
    │   ├── base_template/                  # 最初的 lattice 配置模板
    │   │   ├── ini_file:       a1.ini      # 初始配置文件
    │   │   └── dat_file:       a1.dat      # 初始数据文件
    │   └── tracewin_exe:      TraceWin_noGUI_old.exe  # TraceWin 可执行程序
    │
    ├── field_dir/                          # 存放各种场配置的目录
    │
    ├── 001ANALYSIS/                        # 自动编号的分析目录
    │   ├── CLONES/                         # 克隆目录，复制自 base_template
    │   │   ├── base_0/                     # 第一次克隆
    │   │   ├── base_1/                     # 第二次克隆
    │   │   └── base_2/                     # ...
    │   └── DATAS/                          # 存放数据的目录
    │       ├── InputData.h5                # 仿真输入数据（可选结构）
    │       ├── OutputData.h5               # 仿真输出数据
    │       └── SobolResult/                # 敏感性分析结果文件夹
    │
    ├── 002ANALYSIS/
    │
    └── 003ANALYSIS/
    """

    def __init__(self, path_config, mode='new'):
        """
        path_config = {
            'project_root': r'E:\project\002test',
            'bases_dir': 'bases',
            'base_template': 'base',
            'ini_file': 'a1.ini',
            'dat_file': 'a1.dat',
            'tracewin_exe': 'TraceWin_noGUI_old.exe',
            'field_dir': 'field',
        }
        """
        self.cpu_number = None
        self.round_id = f'{0:03d}'
        self.analysis_id = f'{0:03d}'
        self.analysis_settings = {}
        self.this_analysis_setting = {}
        required_keys = {
            'project_root', 'bases_dir', 'base_template',
            'ini_file', 'dat_file', 'tracewin_exe', 'field_dir'
        }
        missing_keys = required_keys - path_config.keys()

        if missing_keys:
            raise ValueError(f"path_config 缺少必要的键: {missing_keys}")

        self.path_config = path_config
        self.PATH_DICT = {
            'ROOT': self.path_config['project_root'],
            'BASE': os.path.join(path_config['project_root'], path_config['bases_dir'], path_config['base_template']),
            'field': os.path.join(path_config['project_root'], path_config['field_dir']),
        }
        if mode == 'new':
            paths_exist = [p for p in self.PATH_DICT.values() if os.path.exists(p)]
            if paths_exist:
                answer = input("检测到已有项目目录，是否全部删除并重建？[y/N]: ").strip().lower()
                if answer == 'y':
                    print()
                    path = self.path_config['project_root']
                    shutil.rmtree(path)

        os.makedirs(self.PATH_DICT['BASE'], exist_ok=True)
        os.makedirs(self.PATH_DICT['field'], exist_ok=True)

        if mode == 'new':
            print('请准备好基础文件：ini文件, dat文件, 场文件, 以及TraceWin.exe文件. 注意在dat中设定使用场文件\n')
            input('准备好后请按回车继续...')

        path_temp = os.path.dirname(self.PATH_DICT['BASE'])
        exe_files = [f for f in os.listdir(path_temp) if
                     f.endswith('.exe') and os.path.isfile(os.path.join(path_temp, f))]
        if len(exe_files) == 1:
            exe_name = exe_files[0]
            exe_path = os.path.join(path_temp, exe_name)
        elif len(exe_files) == 0:
            raise FileNotFoundError("未找到任何 .exe 文件")
        else:
            raise RuntimeError(f"找到多个 .exe 文件：{exe_files}，请手动指定")
        self.PATH_DICT['TraceWin'] = exe_path

        if not mode == 'new':
            self.load_analysis_settings()

    def initialize_analysis(self, analysis_id=None, mode='new'):
        """
        初始化工程目录。

        参数:
        - analysis_id: 指定分析编号（如 "001"），为 None 时自动编号。
        - overwrite: 如果 True，则会覆盖已有的分析文件夹。
        """
        if analysis_id is None:
            analysis_id = self._get_next_analysis_id()
        self.analysis_id = analysis_id
        analysis_dir = os.path.join(self.PATH_DICT['ROOT'], f'{analysis_id}ANALYSIS')
        clones_dir = os.path.join(analysis_dir, 'CLONES')
        datas_dir = os.path.join(analysis_dir, 'DATAS')
        self.PATH_DICT['clones'] = clones_dir
        self.PATH_DICT['datas'] = datas_dir

        if os.path.exists(analysis_dir):
            if mode == 'new':
                raise FileExistsError(f"分析目录 {analysis_dir} 已存在，请指定 mode='old' 或使用新编号。")
            else:
                print(f"分析目录 {analysis_dir} 已存在, 将在原有的数据基础上继续分析")

        os.makedirs(self.PATH_DICT['clones'], exist_ok=True)
        os.makedirs(self.PATH_DICT['datas'], exist_ok=True)

    def _get_next_analysis_id(self):
        """自动查找下一个可用的分析编号，如 '004'。"""
        existing = [
            name for name in os.listdir(self.PATH_DICT['ROOT'])
            if len(name) == 11 and name.endswith('ANALYSIS')
        ]
        ids = [int(name[:3]) for name in existing if name[:3].isdigit()]
        next_id = max(ids, default=0) + 1
        return f"{next_id:03d}"

    def copy_base(self, copy_id=0, overwrite=True):
        """
        复制最初的base文件，如果失败则重试。
        """
        base_path = self.PATH_DICT['BASE']
        copy_path = os.path.join(self.PATH_DICT['clones'], self.path_config['base_template'] + '_' + str(copy_id))

        if os.path.exists(copy_path):
            if overwrite:
                shutil.rmtree(copy_path)
            else:
                raise FileExistsError(f"克隆目录已存在且 overwrite=False: {copy_path}")

        retry_count = 0
        success = False

        while not success:
            try:
                shutil.copytree(base_path, copy_path)
                if os.path.exists(copy_path):
                    success = True
            except Exception as e:
                retry_count += 1
                print(f"复制失败，第 {retry_count} 次重试。原因: {e}")
                if os.path.exists(copy_path):
                    shutil.rmtree(copy_path)
                time.sleep(0.1)  # 避免系统文件锁定问题

    def analysis_setting(self, setting_dict=None, round_id=0):
        """
        分析的设定，参数数量，边界，模式等等
        """
        self.round_id = f'{round_id:03d}'
        default_setting = {
            'id': str(self.analysis_id) + '_' + str(self.round_id),
            'parameter_number': 232 * 6,
            'simple_size': 5,
            "elements_type": ['FIELD_MAP 7700', 'FIELD_MAP 70', 'QUAD'],
            "bounds":
                [[0.5, 0.5, 0.8 * MRAD_TO_DEGREE, 0.8 * MRAD_TO_DEGREE, 0.5, 0.1],
                 [0.5, 0.5, 0.8 * MRAD_TO_DEGREE, 0.8 * MRAD_TO_DEGREE, 0.8 * MRAD_TO_DEGREE, 0.5],
                 [0.5, 0.5, 0.8 * MRAD_TO_DEGREE, 0.8 * MRAD_TO_DEGREE, 0.8 * MRAD_TO_DEGREE, 0.5]],
            # List[List[float]]
            "elements_quantity": [137, 53, 42],  # list[int]
            'random_seed': 0,
            'mode': 'single',  # 'single', 'block', 'custom'
            'block_size': 6,
            'exchange_indices': None,

            'Error Commands': [
                ['ERROR_CAV_NCPL_DYN', '1', '0', '0', '0', '0', '0', '0', '0', '0', '1'],
                ['ERROR_QUAD_NCPL_DYN', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1'],
                ['ERROR_QUAD_NCPL_DYN', '1', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '1'],

            ]
        }
        if setting_dict is None:
            setting_dict = default_setting
        full_setting = {**default_setting, **setting_dict}
        self.analysis_settings[full_setting['id']] = full_setting
        self.this_analysis_setting = full_setting
        self.save_analysis_settings()
        if self.this_analysis_setting['mode'] in ('single', 'block'):
            self.check_setting()

    def check_setting(self):
        """
        检验本次setting是否合理
        """
        setting = self.this_analysis_setting

        # 检查 parameter_number 是否是 6 的倍数
        if setting['parameter_number'] % 6 != 0:
            raise ValueError("parameter_number 不是 6 的倍数")

        # 计算元件总数
        total_elements = sum(setting['elements_quantity'])

        # 检查 parameter_number 是否等于 6 × 元件总数
        if setting['parameter_number'] != total_elements * 6:
            raise ValueError(
                f"parameter_number 与元件总数不符，应该为 {total_elements * 6}，实际为 {setting['parameter_number']}")

        # 检查 elements_type, bounds, elements_quantity, Error Commands 长度是否一致
        lengths = [
            len(setting['elements_type']),
            len(setting['bounds']),
            len(setting['elements_quantity']),
            len(setting['Error Commands'])
        ]
        if len(set(lengths)) != 1:
            raise ValueError(f"元素类型、边界、元件数量、误差命令维度不一致: {lengths}")

        # 检查每组边界是否长度为6
        for i, bound in enumerate(setting['bounds']):
            if len(bound) != 6:
                raise ValueError(f"第 {i + 1} 个边界维度不是 6，而是 {len(bound)}")

    def save_analysis_settings(self):
        """
        保存设置集
        """
        save_path = os.path.join(self.PATH_DICT['ROOT'], 'analysis_settings.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_settings, f, indent=4, ensure_ascii=False)

    def load_analysis_settings(self):
        """
        加载设置集，适用于mode=’old‘
        """
        load_path = os.path.join(self.PATH_DICT['ROOT'], 'analysis_settings.json')
        if os.path.exists(load_path):
            with open(load_path, 'r', encoding='utf-8') as f:
                self.analysis_settings = json.load(f)
        else:
            self.analysis_settings = {}

    def generate_data(self):
        """
        产生输入数据
        """
        parameter_number = self.this_analysis_setting['parameter_number']
        np.random.seed(self.this_analysis_setting['random_seed'])
        simple_size = self.this_analysis_setting['simple_size']
        bounds = self.this_analysis_setting['bounds']
        elements_quantity = self.this_analysis_setting['elements_quantity']
        input_A = np.random.uniform(-1, 1, size=(simple_size, parameter_number))
        input_B = np.random.uniform(-1, 1, size=(simple_size, parameter_number))

        # 缩放因子
        scale_factors = np.concatenate([
            np.tile(bounds, num) for bounds, num in zip(bounds, elements_quantity)
        ])

        input_Au_list = []
        input_Bu_list = []

        mode = self.this_analysis_setting['mode']
        if mode == 'single':
            for i in range(parameter_number):
                temp_A = input_B.copy()
                temp_B = input_A.copy()
                temp_A[:, i] = input_A[:, i]
                temp_B[:, i] = input_B[:, i]
                input_Au_list.append(temp_A)
                input_Bu_list.append(temp_B)

        elif mode == 'block':
            block_size = self.this_analysis_setting['block_size']
            for start in range(0, parameter_number, block_size):
                end = min(start + block_size, parameter_number)
                temp_A = input_B.copy()
                temp_B = input_A.copy()
                temp_A[:, start:end] = input_A[:, start:end]
                temp_B[:, start:end] = input_B[:, start:end]
                input_Au_list.append(temp_A)
                input_Bu_list.append(temp_B)

        elif mode == 'custom':
            exchange_indices = self.this_analysis_setting['exchange_indices']
            if exchange_indices is None:
                raise ValueError("custom 模式必须提供 exchange_indices")
            for idx_group in exchange_indices:
                temp_A = input_B.copy()
                temp_B = input_A.copy()
                temp_A[:, idx_group] = input_A[:, idx_group]
                temp_B[:, idx_group] = input_B[:, idx_group]
                input_Au_list.append(temp_A)
                input_Bu_list.append(temp_B)

        inputdata_path = os.path.join(self.PATH_DICT['datas'], 'InputData.h5')
        self.PATH_DICT['InputData'] = inputdata_path
        with h5py.File(inputdata_path, 'a') as inputdata_file:
            round_name = f'round_{self.round_id}'
            if round_name in inputdata_file:
                del inputdata_file[round_name]
            grp = inputdata_file.create_group(round_name)
            grp.create_dataset('input_A', data=input_A * scale_factors)
            grp.create_dataset('input_B', data=input_B * scale_factors)

            for i, (A_mod, B_mod) in enumerate(zip(input_Au_list, input_Bu_list)):
                grp.create_dataset(f'input_Au_{i}', data=A_mod * scale_factors)
                grp.create_dataset(f'input_Bu_{i}', data=B_mod * scale_factors)

    def modify_dat_file(self, file_id, errors):
        """
        修改dat文件
        """
        copy_path = os.path.join(self.PATH_DICT['clones'], self.path_config['base_template'] + '_' + str(file_id))
        dat_path = os.path.join(copy_path, self.path_config['dat_file'])

        with open(dat_path, encoding='UTF-8') as dat_file:
            lines_temp = dat_file.readlines()
        new_lines = []
        counters = {}
        acc = 0
        for key, q in zip(self.this_analysis_setting['elements_type'], self.this_analysis_setting['elements_quantity']):
            counters[key] = acc
            acc += q
        for line in lines_temp:
            stripped = line.strip()
            if stripped.startswith('end '):
                new_lines.append(line)
                break

            for key, error_command in zip(self.this_analysis_setting['elements_type'],
                                          self.this_analysis_setting['Error Commands']):
                if stripped.startswith(key):
                    start_index = counters[key] * 6
                    error = errors[start_index: start_index + 6]
                    counters[key] += 1
                    error_str = [format_sign_space(x) for x in error]
                    error_command[3: 9] = error_str
                    insert_line = ' '.join(error_command) + '\n'
                    new_lines.append(insert_line)
            new_lines.append(line)
            with open(dat_path, 'w', encoding='UTF-8') as dat_file:
                dat_file.writelines(new_lines)

    def run_command(self, file_id):
        """
        利用cmd, 调用TraceWin实现仿真
        """
        copy_path = os.path.join(self.PATH_DICT['clones'], self.path_config['base_template'] + '_' + str(file_id))
        ini_path = os.path.join(copy_path, self.path_config['ini_file'])
        result_file = os.path.join(copy_path, 'result', 'Statistic_Errors_1_ENV.txt')
        root = self.PATH_DICT['ROOT']
        TraceWin = self.PATH_DICT['TraceWin']
        command = f'{TraceWin} {ini_path}'
        # print(command)
        num = 0
        while True:
            subprocess.run(command, shell=True, capture_output=True, text=True,
                           cwd=root)
            if os.path.exists(result_file):
                break
            else:
                time.sleep(0.1)
                num += 1

                print(f"{copy_path}, 第{num}次运行失败")

    def get_result(self, file_id):
        """
        获取仿真结果
        """
        copy_path = os.path.join(self.PATH_DICT['clones'], self.path_config['base_template'] + '_' + str(file_id))
        result_file = os.path.join(copy_path, 'result', 'Statistic_Errors_1_ENV.txt')
        if not os.path.exists(result_file):
            raise FileNotFoundError(f"未找到输出文件: {result_file}")

        with open(result_file, encoding='UTF-8') as f:
            lines = [line.strip().lstrip('\ufeff') for line in f if line.strip()]

        if len(lines) < 3:
            print("文件行数不足")
            return None

        res = lines[2].split()  # 第3行（索引为2），按空格分割成列表
        try:
            v = [
                float(res[2]), float(res[3]), float(res[4]),  # 发射度
                float(res[5]) * 1000, float(res[6]) * 1000,  # 质心位置，单位变为 mm
                float(res[11]) * 1000, float(res[12]) * 1000,  # 包络尺寸，单位变为 mm
                float(res[20]), float(res[21]), float(res[22]), float(res[23])  # x方向α,β, y方向α,β
            ]

            # v = [float(_) for _ in res]
            v_str = [format_sign_space(x) for x in v]
            shutil.rmtree(copy_path)
            return v_str
        except (IndexError, ValueError) as e:
            print(f"解析失败: {e}")
            return None

    def simulation_one_round(self, cpu_number, overwrite='y'):
        """
        利用并行实现仿真一轮。
        如果 overwrite='y'：强制覆盖已有结果。
        如果 overwrite='n'：跳过已存在的 key。
        """
        self.cpu_number = cpu_number
        try:
            inputdata_path = self.PATH_DICT['InputData']
        except KeyError:
            raise FileNotFoundError("疑似没有输入数据：未在 self.PATH_DICT 中找到 'InputData'")

        round_name = f'round_{self.round_id}'
        outputdata_path = os.path.join(self.PATH_DICT['datas'], 'OutputData.h5')
        self.PATH_DICT['OutputData'] = outputdata_path

        with h5py.File(inputdata_path, 'r') as inputdata_file:
            keys = list(inputdata_file[round_name].keys())
            total_keys = len(keys)
            print(f'本轮共需要计算 {total_keys} 个 key')

            for idx, key in enumerate(keys, 1):
                start_datetime = datetime.datetime.now()
                print(f'\n[{idx}/{total_keys}] 开始计算 key: {key}')
                print(f'开始时间: {start_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
                start_time = time.time()

                with h5py.File(outputdata_path, 'a') as outputdata_file:
                    if round_name not in outputdata_file:
                        grp = outputdata_file.create_group(round_name)
                    else:
                        grp = outputdata_file[round_name]

                    if key in grp and overwrite != 'y':
                        print(f"key: {key} 已存在，跳过计算（因 overwrite='{overwrite}'）")
                        continue  # 跳过已存在的 key

                # 读取输入数据并并行计算
                input_temp = inputdata_file[round_name][key][()]
                index_inputs = [(self, i, input_temp[i]) for i in range(len(input_temp))]
                output_temp = run_bases_multiprocessing(self.cpu_number, index_inputs)
                output_temp = np.array([[float(x) for x in row] for row in output_temp])

                # 再次打开输出文件并写入数据
                with h5py.File(outputdata_path, 'a') as outputdata_file:
                    grp = outputdata_file[round_name]
                    if key in grp:
                        del grp[key]
                    grp.create_dataset(key, data=output_temp)

                end_datetime = datetime.datetime.now()
                elapsed = time.time() - start_time
                print(f'结束时间: {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
                print(f'完成 key: {key}，耗时 {elapsed:.2f} 秒')

    def deal_datas_for_one_round(self, round_id=None):
        try:
            outputdata_path = os.path.join(self.PATH_DICT['datas'], 'OutputData.h5')
        except KeyError:
            raise FileNotFoundError("疑似没有输出数据：未在 self.PATH_DICT 中找到 'OutputData'")
        save_path = os.path.join(self.PATH_DICT['datas'], 'effect.json')
        effect = {
            'ST': {},
            'S': {}
        }
        if round_id is None:
            round_name = f'round_{self.round_id}'
        else:
            round_name = f'round_{round_id:03d}'
        with h5py.File(outputdata_path, 'r') as outputdata_file:
            group = outputdata_file[round_name]
            y_a = np.array(group['input_A'])
            y_b = np.array(group['input_B'])

            i = 0
            while f'input_Au_{i}' in group and f'input_Bu_{i}' in group:
                y_a_u = np.array(group[f'input_Au_{i}'])
                y_b_u = np.array(group[f'input_Bu_{i}'])
                S_u = 1 - sum((y_b - y_b_u) ** 2 + (y_a - y_a_u) ** 2) / sum((y_a - y_b) ** 2 + (y_a_u - y_b_u) ** 2)
                ST_u = sum((y_b - y_a_u) ** 2 + (y_a - y_b_u) ** 2) / sum((y_a - y_b) ** 2 + (y_a_u - y_b_u) ** 2)
                effect['S'][i] = S_u.tolist()
                effect['ST'][i] = ST_u.tolist()
                i += 1
        with open(save_path, 'w') as f:
            json.dump(effect, f, indent=4)

    def deal_datas_for_all_rounds(self):
        try:
            outputdata_path = os.path.join(self.PATH_DICT['datas'], 'OutputData.h5')
        except KeyError:
            raise FileNotFoundError("疑似没有输出数据：未在 self.PATH_DICT 中找到 'OutputData'")

        save_path = os.path.join(self.PATH_DICT['datas'], 'effect.json')
        effect = {
            'ST': {},
            'S': {}
        }

        # 用于收集所有轮次的数据（二维拼接）
        y_a_all = []
        y_b_all = []
        y_a_u_all = {}  # key: i -> list of y_a_u_i from all rounds
        y_b_u_all = {}

        with h5py.File(outputdata_path, 'r') as outputdata_file:
            round_keys = [key for key in outputdata_file.keys() if key.startswith('round_')]
            for round_name in round_keys:
                group = outputdata_file[round_name]
                y_a_all.append(np.array(group['input_A']))  # shape: N x n
                y_b_all.append(np.array(group['input_B']))

                i = 0
                while f'input_Au_{i}' in group and f'input_Bu_{i}' in group:
                    if i not in y_a_u_all:
                        y_a_u_all[i] = []
                        y_b_u_all[i] = []
                    y_a_u_all[i].append(np.array(group[f'input_Au_{i}']))  # shape: N x n
                    y_b_u_all[i].append(np.array(group[f'input_Bu_{i}']))
                    i += 1

        # 沿 axis=0 拼接为 (kN x n)
        y_a = np.vstack(y_a_all)
        y_b = np.vstack(y_b_all)

        for i in y_a_u_all:
            y_a_u = np.vstack(y_a_u_all[i])
            y_b_u = np.vstack(y_b_u_all[i])
            denominator = sum((y_a - y_b) ** 2 + (y_a_u - y_b_u) ** 2)
            if denominator == 0:
                S_u = 0
                ST_u = 0
            else:
                S_u = 1 - sum((y_b - y_b_u) ** 2 + (y_a - y_a_u) ** 2) / denominator
                ST_u = sum((y_b - y_a_u) ** 2 + (y_a - y_b_u) ** 2) / denominator
            effect['S'][i] = S_u.tolist()
            effect['ST'][i] = ST_u.tolist()

        # 保存结果
        with open(save_path, 'w') as f:
            json.dump(effect, f, indent=4)

    def get_elements_order(self):
        """
        返回每个元件在 error 数组中的编号顺序，例如：[53, 0, 54, 1, …]
        """
        base_path = self.PATH_DICT['BASE']
        dat_path = os.path.join(base_path, self.path_config['dat_file'])

        # 获取元件类型和数量，并构建 counters
        elements_type_list = self.this_analysis_setting['elements_type']
        elements_quantity_list = self.this_analysis_setting['elements_quantity']

        counters = {}
        acc = 0
        for key, q in zip(elements_type_list, elements_quantity_list):
            counters[key] = acc
            acc += q

        # 遍历 dat 文件提取编号
        element_order = []
        with open(dat_path, 'r', encoding='UTF-8') as dat_file:
            for line in dat_file:
                stripped = line.strip()
                for key in elements_type_list:
                    if stripped.startswith(key):
                        element_order.append(counters[key])
                        counters[key] += 1
                        break  # 每行只匹配一个元素类型

        return element_order

    def plot_effect_by_element_order(self, mode='scatter', dims=None, save_fig=False, point_size=10):
        import matplotlib
        import matplotlib.pyplot as plt
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False

        # 读取 effect.json
        json_path = os.path.join(self.PATH_DICT['datas'], 'effect.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            effect = json.load(f)

        S_dict = effect.get('S', {})
        ST_dict = effect.get('ST', {})

        keys = sorted(map(int, S_dict.keys()))
        print(keys)
        dim_total = len(S_dict[str(keys[0])])
        dim_names = ['x发射度', 'y发射度', 'z发射度', '质心x', '质心y', 'rms_x', 'rms_y']

        if dims is None:
            dims = list(range(dim_total))
        else:
            for d in dims:
                if d < 0 or d >= dim_total:
                    raise ValueError(f"维度索引 {d} 超出范围，应在 0~{dim_total - 1} 之间")

        element_order = self.get_elements_order()
        print("原始元素顺序:", element_order)

        element_order_sorted = sorted(element_order)
        print("排序后元素顺序:", element_order_sorted)

        if len(element_order) != len(keys):
            raise ValueError(f"元件顺序数量 {len(element_order)} 与 effect 中元件数量 {len(keys)} 不一致")

        for d in dims:
            S_values = np.array([float(S_dict[str(k)][d]) for k in keys])
            ST_values = np.array([float(ST_dict[str(k)][d]) for k in keys])

            S_values_sorted = [S_values[i] for i in element_order]
            ST_values_sorted = [ST_values[i] for i in element_order]

            plt.figure(figsize=(12, 6))
            if mode == 'scatter':
                plt.scatter(keys, S_values_sorted, label='S', marker='o', s=point_size)
                plt.scatter(keys, ST_values_sorted, label='ST', marker='x', s=point_size)
            elif mode == 'line':
                plt.plot(element_order, S_values, label='S', marker='o', markersize=point_size / 2, linewidth=1)
                plt.plot(element_order, ST_values, label='ST', marker='x', markersize=point_size / 2, linewidth=1)
            else:
                raise ValueError("mode 应为 'scatter' 或 'line'")

            plt.xlabel('元件', fontsize=12)
            plt.ylabel(dim_names[d], fontsize=12)
            plt.title(f'Effect: S & ST - {dim_names[d]}', fontsize=14)
            plt.legend()

            # 设置横坐标
            skip = 10  # 每隔10个显示一个标签，可以根据实际情况调整
            xticks_to_show = range(len(keys))[::skip]  # 隔行取横坐标
            xticks_pos = list(range(0, len(keys), skip))  # 对应的位置索引
            plt.xticks(xticks_pos, xticks_to_show, rotation=45)

            # 添加网格线
            plt.grid(True, linestyle='--', alpha=0.6)  # 虚线网格，半透明
            plt.tight_layout()

            if save_fig:
                save_dir = os.path.join(self.PATH_DICT['datas'], 'plots')
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f'effect_dim_{d}_{dim_names[d]}.png')
                plt.savefig(save_path, dpi=300)
                plt.close()
            else:
                plt.show()


def run_one_base(ea, idx, error_array):
    """
    准备并行的函数
    """
    ea.copy_base(copy_id=idx)
    ea.modify_dat_file(file_id=idx, errors=error_array)
    ea.run_command(file_id=idx)
    return ea.get_result(file_id=idx)


def run_bases_multiprocessing(number_of_cpu, all_inputs):
    """
    并行模拟的函数
    """
    with Pool(number_of_cpu) as bases_pool:
        bases_res = bases_pool.starmap(run_one_base, all_inputs)
    return bases_res


if __name__ == "__main__":
    test_path_config = {
        'project_root': r'E:\project\003test',
        'bases_dir': 'bases',
        'base_template': 'base',
        'ini_file': 'a1.ini',
        'dat_file': 'a1.dat',
        'tracewin_exe': 'TraceWin_noGUI_old.exe',
        'field_dir': 'field',
    }

    test_EA = EA(test_path_config, mode='old')

    # 测试不同输入是否得到不同输出
    run_test = False
    if run_test:
        print('测试不同输入是否得到不同输出')
        test_EA.initialize_analysis('001', 'old')
        test_EA.analysis_setting(round_id=1,
                                 setting_dict={
                                     'simple_size': 100,
                                 }, )
        test_EA.generate_data()

        InputData_path = test_EA.PATH_DICT['InputData']
        with h5py.File(InputData_path, 'r') as test_inputdata_file:
            round_id = f'round_{test_EA.round_id}'
            InputData_round = test_inputdata_file[round_id]
            error_test_1 = InputData_round['input_A'][0]
            error_test_2 = InputData_round['input_A'][1]
            Input_A = InputData_round['input_A'][:]

        # 第一个输入：全零
        test_EA.copy_base(copy_id=0)
        test_EA.modify_dat_file(0, np.zeros(232 * 6))
        test_EA.run_command(0)
        res_0 = test_EA.get_result(0)
        print("res_0:", res_0)

        # 第二个输入：误差输入1
        test_EA.copy_base(copy_id=1)
        test_EA.modify_dat_file(1, error_test_1)
        test_EA.run_command(1)
        res_1 = test_EA.get_result(1)
        print("res_1:", res_1)

        # 第三个输入：误差输入2
        test_EA.copy_base(copy_id=2)
        test_EA.modify_dat_file(2, error_test_2)
        test_EA.run_command(2)
        res_2 = test_EA.get_result(2)
        print("res_2:", res_2)

    # 测试run_one_base
    run_test = False
    if run_test:
        print('测试run_one_base')
        # 不使用run_one_base
        test_EA.copy_base(copy_id=0)
        test_EA.modify_dat_file(0, np.zeros(232 * 6))
        test_EA.run_command(0)
        res_0 = test_EA.get_result(0)
        print(f"{'不使用:':<8}{res_0}")

        # 使用run_one_base
        res_0 = run_one_base(test_EA, 0, np.zeros(232 * 6))
        print(f"{'使用:':<8}{res_0}")

    # 测试多进程
    run_test = False
    if run_test:
        print('测试多进程')

        Index_Inputs = [(test_EA, i, Input_A[i]) for i in range(len(Input_A))]
        res = run_bases_multiprocessing(10, Index_Inputs)
        for i in range(len(res)):
            print(i, res[i])
        res = None

        for i in range(len(Input_A)):
            res = run_one_base(test_EA, 0, Input_A[i])
            print(i, res)

    # 测试写入输出
    run_test = False
    if run_test:
        print('测试写入输出')
        Index_Inputs = [(test_EA, i, Input_A[i]) for i in range(len(Input_A))]
        res = run_bases_multiprocessing(10, Index_Inputs)
        res_float = np.array([[float(x) for x in row] for row in res])
        OutputData_path = os.path.join(test_EA.PATH_DICT['datas'], 'OutputData.h5')
        with h5py.File(OutputData_path, 'a') as test_Outputdata_file:
            round_id = f'round_{test_EA.round_id}'
            Grp = test_Outputdata_file.create_group(round_id)
            Grp.create_dataset('input_A', data=res_float)

    # 测试simulation_one_round
    run_test = False
    if run_test:
        print('测试simulation_one_round')
        test_EA.simulation_one_round(20, overwrite='n')

    # 测试运行多轮
    run_test = True
    if run_test:
        # 完成
        test_EA.initialize_analysis('002', 'old')
        for i in range(10):
            print(f'第{i}轮模拟: ')
            test_EA.analysis_setting(round_id=i,
                                     setting_dict={
                                         'simple_size': 100,
                                         'random_seed': i + 100,
                                     }, )
            test_EA.generate_data()
            test_EA.simulation_one_round(20, 'n')

    # 测试元件为单位模式
    run_test = False
    if run_test:
        # 完成（一轮（size=100）时间为4小时33分钟）
        test_EA.initialize_analysis('003', 'old')
        test_EA.analysis_setting(round_id=2,
                                 setting_dict={
                                     'simple_size': 100,
                                     'mode': 'block',  # 'single', 'block', 'custom'
                                 }, )
        test_EA.generate_data()
        print(int(cpu_count() - 4))
        test_EA.simulation_one_round(28, overwrite='y')

    # 测试deal_data
    run_test = False
    if run_test:
        # 完成
        test_EA.initialize_analysis('003', 'old')
        test_EA.deal_datas_for_one_round(round_id=2)

    # get_elements_order
    run_test = False
    if run_test:
        print('测试get_elements_order')
        test_EA.initialize_analysis('001', 'old')
        test_EA.analysis_setting(round_id=1,
                                 setting_dict={
                                     'simple_size': 100,
                                     'mode': 'block',  # 'single', 'block', 'custom'
                                 }, )
        print(test_EA.get_elements_order())

    # 测试画图
    run_test = False
    if run_test:
        # 完成
        test_EA.initialize_analysis('003', 'old')
        test_EA.analysis_setting(round_id=2,
                                 setting_dict={
                                     'simple_size': 100,
                                     'mode': 'block',  # 'single', 'block', 'custom'
                                 }, )
        test_EA.plot_effect_by_element_order(dims=[3])
