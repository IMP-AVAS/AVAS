import os
import shutil
import json
import numpy as np
import h5py
import time
import datetime
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from utils_ea import logger, get_input, create_or_load_json_config, save_json_config, copy_directory, format_sign_space, \
    read_lines_from_file
from config import DEFAULT_ANALYSIS_SETTINGS, MRAD_TO_DEGREE
from paths import AnalysisPaths, ProjectPaths
from simulator import AvasSimulator
import os
import sys
# =========================================================================
# Module-level functions: For single simulation tasks in multiprocessing
# =========================================================================
def run_single_simulation_task(
        clone_id: int,
        error_array: np.ndarray,  # <--- Important parameter
        project_root_dir: Path,
        group_id: int,
        base_simulation_path: Path,
        analysis_setting_for_task: Dict,
        simulator_instance: AvasSimulator,
        field_path: Path,
        gpu_id: int,
        platform,
) -> List[str]:
    """
    An independent function to execute a single simulation task in a multiprocessing pool.
    It receives all necessary parameters instead of relying on a class instance (which is not serializable).
    """
    if platform == "gpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)


    task_paths = AnalysisPaths(project_root_dir, group_id)


    analysis_dir_name = task_paths.analysis_dir  #OO1ANALYSIS
    clones_dir = task_paths.clones_dir  #OO1ANALYSIS/clones

    clone_path = task_paths.get_clone_path(clone_id)  #/clones/base_0
    result_file = task_paths.get_clone_output_file_path(clone_id)  #/clones/base_0/outputfile


    # 1. Copy base files
    copy_directory(base_simulation_path, clones_dir, new_name=f"base_{clone_id}")

    # 2. Modify input file
    lattice_path = task_paths.get_clone_input_file_path(clone_id)

    original_lines = read_lines_from_file(lattice_path)
    new_lines = []

    # === Fix point 1: Redefine element_param_start_indices and current_element_counters ===
    # Calculate starting indices for each element type parameter
    element_param_start_indices = {}
    current_param_idx = 0
    for elem_type, quantity in zip(analysis_setting_for_task['elements_type'],
                                   analysis_setting_for_task['elements_quantity']):
        element_param_start_indices[elem_type] = current_param_idx
        current_param_idx += quantity * 6  # Each element has 6 parameters

    # Initialize counters for each element type
    current_element_counters = {elem_type: 0 for elem_type in analysis_setting_for_task['elements_type']}
    # ==========================================================================================

    # Iterate through original lines and modify
    for line_orig in original_lines:
        stripped_line = line_orig.strip()

        if stripped_line.startswith('end '):
            new_lines.append(line_orig)
            break

        processed_this_line = False
        for elem_type in analysis_setting_for_task['elements_type']:
            parts = stripped_line.split()
            if len(parts) > 4 and parts[0] == 'field' and parts[4] == str(elem_type):
                # === Fix point 2: Define element_errors ===
                type_start_param_idx = element_param_start_indices[elem_type]  #误差的起始值 0
                type_element_count = current_element_counters[elem_type]       #这是该类型原件的第几个

                error_start_index = type_start_param_idx + (type_element_count * 6)   #这个原件对应的误差的起点
                element_errors = error_array[error_start_index: error_start_index + 6]  # <--- element_errors defined here
                # ==================================#这个原件对应的误差

                error_command_template_for_this_type = None
                for et_cfg, tmpl_cfg in zip(analysis_setting_for_task['elements_type'],
                                            analysis_setting_for_task['error_commands']):
                    if et_cfg == elem_type:
                        error_command_template_for_this_type = tmpl_cfg[:] #找到该误差类型对应的误差命令
                        break
                if error_command_template_for_this_type is None:
                    raise ValueError(f"Cannot find error command template for element type {elem_type}.")

                error_str_values = [format_sign_space(x) for x in element_errors]  #把误差字符串化
                error_command_template_for_this_type[3:9] = error_str_values

                insert_line = ' '.join(error_command_template_for_this_type) + '\n'
                new_lines.append(insert_line)
                new_lines.append(line_orig)
                processed_this_line = True
                current_element_counters[elem_type] += 1
                break

        if not processed_this_line:
            if not line_orig.endswith('\n'):
                new_lines.append(line_orig + '\n')
            else:
                new_lines.append(line_orig)

    with open(lattice_path, 'w', encoding='UTF-8') as dat_file:
        dat_file.writelines(new_lines)
    logger.debug(f"Subprocess {os.getpid()} modified file: {lattice_path}")

    # 3. Run simulation and get results
    results = simulator_instance.run_and_get_result(clone_path, result_file, field_path, platform)
    logger.debug(f"Subprocess {os.getpid()} completed simulation: clone_id={clone_id}")

    # 4. Clean up clone directory
    shutil.rmtree(clone_path)
    logger.debug(f"Subprocess {os.getpid()} cleaned up directory: {clone_path}")

    return results

# =========================================================================
# AnalysisManager class (remaining part)
# =========================================================================
class AnalysisManager:
    """
    Responsible for lifecycle management of specific analysis groups, including configuration, data generation, simulation execution, and result storage.
    """

    def __init__(self, project_root_dir: Path, group_id: Optional[int] = None, analysis_config: Dict = None,
                 simple_size: int = None, random_seed: int = None, round_id: int = None,
                 mode: str = 'new'):
        self._project_root_dir = project_root_dir
        self.paths = None
        self.config: dict = {}
        self._base_simulation_path = project_root_dir / 'base_dir'
        self.field_path = os.path.join(project_root_dir, 'field_dir')

        self.simulator = AvasSimulator()  # AvasSimulator instance
        self.mode = mode
        self.group_id = group_id

        # self._resolve_group_id(group_id, mode)  #产生group_id, 001analysis

        self.paths = AnalysisPaths(self._project_root_dir, self.group_id)

        #获取config
        if self.mode == 'new':
            self._setup_new_analysis(analysis_config, simple_size, random_seed, round_id)
        elif self.mode == 'old':
            self._load_existing_analysis(analysis_config, simple_size, random_seed, round_id)
        else:
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'new' or 'old'.")

        self._current_round_id = self.config['round_id'][-1]
        self._current_simple_size = self.config['simple_size'][-1]
        self._current_random_seed = self.config['random'][-1]
        # _prepare_error_command_template no longer needed as templates are passed directly from config['setting'] to module-level function
        # self._prepare_error_command_template() # <-- Delete this line

        logger.info(f"Analysis group {self.group_id:03d} initialized, current round {self._current_round_id}.")

    def _resolve_group_id(self, group_id: Optional[int], mode: str):
        """Determine analysis group ID based on mode and user input."""
        pass
        # project_paths_temp = ProjectPaths(self._project_root_dir)
        # existing_groups = project_paths_temp.get_existing_analysis_groups()
        # next_group_id = project_paths_temp.get_next_group_id()
        #
        # if group_id is None:
        #     self.group_id = next_group_id
        # else:
        #     self.group_id = group_id
        #
        # final_mode = mode
        # #如果是新模式，但是使用的id已经存在
        # if mode == 'new' and self.group_id in existing_groups:
        #     raise Exception(f"Group {self.group_id:03d} already exists.")
        #
        # elif mode == 'old' and self.group_id not in existing_groups:
        #     raise Exception(f"Group {self.group_id:03d} does not exist.")
        #
        # self.mode = final_mode

    def _setup_new_analysis(self, analysis_config: Dict, simple_size: int, random_seed: int, round_id: int):
        self.paths.create_analysis_dirs()  #创建analysis

        logger.info(f"Created analysis directory: {self.paths.analysis_dir}")

        effective_analysis_config = DEFAULT_ANALYSIS_SETTINGS.copy()
        #更新用户设置的analysis中的内容
        effective_analysis_config.update(analysis_config)

        #如果是第一次模拟，随机数和round都设为0
        self.config = {
            'setting': effective_analysis_config,
            'simple_size': [simple_size if simple_size is not None else 10],
            'random': [0],
            'round_id': [0]
        }

        save_json_config(self.paths.analysis_settings_file, self.config)

    def _load_existing_analysis(self, analysis_config: Dict, simple_size: int, random_seed: int, round_id: int):
        if not self.paths.analysis_dir.exists():
            raise FileNotFoundError(f"Analysis directory {self.paths.analysis_dir} does not exist, cannot load.")


        self.config = create_or_load_json_config(self.paths.analysis_settings_file, DEFAULT_ANALYSIS_SETTINGS,
                                                 mode='old')

        #查找这一次设置和上一次设置不一样的地方
        if analysis_config:
            inconsistent_keys = []
            for key in ['mode', 'parameter_number', 'elements_quantity', 'elements_type', 'bounds', 'block_size',
                        'error_commands']:
                if key in analysis_config and analysis_config[key] != self.config['setting'].get(key):
                    inconsistent_keys.append(key)

            if inconsistent_keys:
                error_msg = f"Input analysis configuration inconsistent with existing project configuration, please check: {inconsistent_keys}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        #如果是重新模拟，那么随机数和round_id +1
        self.config['simple_size'].append(simple_size if simple_size is not None else self.config['simple_size'][-1])
        self.config['random'].append(self.config['random'][-1] + 1)
        self.config['round_id'].append(self.config['round_id'][-1] + 1)

        save_json_config(self.paths.analysis_settings_file, self.config)

    # _prepare_error_command_template method no longer needed, deleted

    # copy_base_files and modify_dat_file methods should also be deleted as their logic has been moved to run_single_simulation_task function

    def generate_input_data(self):
        """
        Generate input data based on current analysis settings and store in HDF5 file.
        """
        #总的参数数量
        param_number = self.config['setting']['parameter_number']

        #
        np.random.seed(self._current_random_seed)
        simple_size = self._current_simple_size
        elements_quantity = self.config['setting']['elements_quantity']  #2, 6

        # input_A = np.random.uniform(-1, 1, size=(simple_size, param_number))
        # input_B = np.random.uniform(-1, 1, size=(simple_size, param_number))

        bounds_lower = self.config['setting']['bounds_lower']
        bounds_upper = self.config['setting']['bounds_upper']

        input_A = np.random.uniform(bounds_lower, bounds_upper)
        input_B = np.random.uniform(bounds_lower, bounds_upper)

        scale_factors = []


        #取得参数的上界和下界
        # sample = np.random.uniform(low=lower, high=upper)



        input_Au_list = []
        input_Bu_list = []

        mode = self.config['setting']['mode']
        if mode == 'single':
            for i in range(param_number):
                temp_A = input_B.copy()
                temp_B = input_A.copy()
                temp_A[:, i] = input_A[:, i]
                temp_B[:, i] = input_B[:, i]
                input_Au_list.append(temp_A)
                input_Bu_list.append(temp_B)
        elif mode == 'block':
            block_size = self.config['setting']['block_size']
            for start in range(0, param_number, block_size):
                end = min(start + block_size, param_number)
                temp_A = input_B.copy()
                temp_B = input_A.copy()
                temp_A[:, start:end] = input_A[:, start:end]
                temp_B[:, start:end] = input_B[:, start:end]
                input_Au_list.append(temp_A)
                input_Bu_list.append(temp_B)
        else:
            raise ValueError(f"Unsupported analysis mode: {mode}")

        #如果这组round已经存在，那就删除原来的
        with h5py.File(self.paths.input_data_file, 'a') as inputdata_file:
            round_name = f'round_{self._current_round_id}'
            if round_name in inputdata_file:
                del inputdata_file[round_name]

            # input_data.h5
            # ├── round_0
            # │   ├── input_A
            # │   ├── input_B
            # │   ├── input_Au_0
            # │   └── input_Bu_0
            # ├── round_1
            # │   ├── input_A
            # │   ├── input_B
            # │   ├── input_Au_0
            # │   └── input_Bu_0
            # └── round_2
            # ├── input_A
            # ├── input_B
            # ├── input_Au_0
            # └── input_Bu_0

            grp = inputdata_file.create_group(round_name)
            grp.create_dataset('input_A', data=input_A )
            grp.create_dataset('input_B', data=input_B )

            for i, (A_mod, B_mod) in enumerate(zip(input_Au_list, input_Bu_list)):
                grp.create_dataset(f'input_Au_{i}', data=A_mod)
                grp.create_dataset(f'input_Bu_{i}', data=B_mod)

        logger.info(f"Generated and saved input data for round {self._current_round_id} to {self.paths.input_data_file}.")

    def run_simulations_for_round(self, platform = None, cpu_num = None, gpu_num = None):
        """
        Execute all simulations for current round using parallel computing.

        Args:
            cpu_number (int, optional): Number of CPUs for parallel processing. Defaults to system CPU count minus one.
            overwrite_output (str): 'y' force overwrite existing results, 'n' skip existing keys.
        """
        if cpu_num is None:
            cpu_num = max(1, cpu_count() - 1)

        round_name = f'round_{self._current_round_id}'

        with h5py.File(self.paths.input_data_file, 'r') as inputdata_file:
            if round_name not in inputdata_file:
                raise KeyError(
                    f"Round '{round_name}' data not found in input data file {self.paths.input_data_file}. Please generate input data first.")

            input_keys = [k for k in inputdata_file[round_name].keys() if k.startswith('input_')]  #所有的矩阵 key
            total_keys = len(input_keys)
            logger.info(f"Round '{round_name}' requires calculation of {total_keys} keys.")

            for idx, key in enumerate(input_keys, 1):
                start_datetime = datetime.datetime.now()
                logger.info(f"\n--- [{idx}/{total_keys}] Starting calculation for key: {key} ---")
                logger.info(f"Start time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                start_time = time.time()

                with h5py.File(self.paths.output_data_file, 'a') as outputdata_file:
                    if round_name not in outputdata_file:
                        grp = outputdata_file.create_group(round_name)
                    else:
                        grp = outputdata_file[round_name]



                #表示把这个dataset的实际数据读出来
                input_temp = inputdata_file[round_name][key][()]
                #["input_A",]所有参数

                # Create a task for each sample, passing all necessary context as parameters
                def get_gpu_id(idx):
                    if gpu_num is None:
                        return None
                    return idx%gpu_num
                all_task_args = [
                    (
                        clone_idx,  # clone_id   0
                        errors_for_clone,  # error_array    这一组误差
                        self._project_root_dir,  # project_root_dir
                        self.group_id,  # group_id
                        self._base_simulation_path,  # base_simulation_path   project/base_dtr
                        self.config['setting'],  # analysis_setting_for_task (configuration dictionary)
                        self.simulator,  # simulator_instance (simulator instance),
                        self.field_path,
                        get_gpu_id(clone_idx),
                        platform
                    )
                    for clone_idx, errors_for_clone in enumerate(input_temp)
                ]
                if platform == "cpu":
                    with Pool(cpu_num) as pool:
                        # Call module-level run_single_simulation_task function
                        output_temp = pool.starmap(run_single_simulation_task, all_task_args)

                elif platform == "gpu":

                    with Pool(gpu_num) as pool:
                        # Call module-level run_single_simulation_task function
                        output_temp = pool.starmap(run_single_simulation_task, all_task_args)

                output_temp_np = np.array([[float(x) for x in row] for row in output_temp])

                with h5py.File(self.paths.output_data_file, 'a') as outputdata_file:
                    grp = outputdata_file[round_name]
                    if key in grp:
                        del grp[key]
                    grp.create_dataset(key, data=output_temp_np)

                end_datetime = datetime.datetime.now()
                elapsed = time.time() - start_time
                logger.info(f'End time: {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
                logger.info(f'Completed key: {key}, time taken {elapsed:.2f} seconds')

        logger.info(f"All simulation calculations for round {self._current_round_id} completed.")