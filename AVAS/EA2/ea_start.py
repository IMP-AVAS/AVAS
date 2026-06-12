#这是一个工程分析的启动代码

import math
from pathlib import Path
# Import refactored modules
from project import ProjectManager
from analysis import AnalysisManager
from config import MRAD_TO_DEGREE, DEFAULT_ANALYSIS_SETTINGS
from utils_ea import logger, get_input  # Import logger

from paths import AnalysisPaths, ProjectPaths

MRAD_TO_DEGREE = 180 / (math.pi * 1000)  # Milliradians to degrees 毫弧度

from sobol_calculator import SobolCalculator

class EaStart():
    def __init__(self, ):
        pass

    def run(self, item):
        #this_analysis_setting = {
        # 'mode': 'block',  # Switch to block mode
        # 'block_size': 6,
        # 'parameter_number': 8 * 6,
        # }

        custom_analysis_setting = {
            'mode': 'single',  # 'single', 'block'
            'parameter_number': 8 * 6,
            "elements_quantity": [2, 6],  # Example: [2 elements type 1, 6 elements type 3]
            "elements_type": [1, 3],  # Corresponding element types above

            'block_size': 6,  # Only used when mode='block'
            'error_commands': [  # Error command templates corresponding to elements_type
                ['err_cav_ncpl_dyn', '1', '0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0'],
                ['err_quad_ncpl_dyn', '1', '0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']],

            "bounds_lower":
                [[-0.5, -0.5, -2 * MRAD_TO_DEGREE, -2 * MRAD_TO_DEGREE, -0.5, -0.1],  # 6 parameter bounds for element type 1
                 [-0.5, -0.5, -2 * MRAD_TO_DEGREE, -2 * MRAD_TO_DEGREE, -2 * MRAD_TO_DEGREE, -0.5]],

            "bounds_upper":
                [[0.5, 0.5, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 0.5, 0.1],  # 6 parameter bounds for element type 1
                 [0.5, 0.5, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 0.5]],

        }
        custom_analysis_setting.update(item["this_analysis_setting"])
################################################################################
        origin_project_path = item["origin_project_path"]
        root_path = item["root_path"]
        run_mode = item["run_mode"]
        sample_size = item["sample_size"]
        round_id = item["round_id"]
        group_id = item["group_id"]

        platform = item["platform"]
        cpu_num = item["cpu_num"]
        gpu_num = item["gpu_num"]

        #根据mode判断是复制还是继续模拟
        project_manager = ProjectManager(root_path=str(root_path), origin_project_path=origin_project_path, mode=run_mode)

        #获取analysis id
        # next_group_id = project_manager.get_next_analysis_group_id()
        # next_group_id = 1

        #创建analysis中的文件和更新config
        analysis_manager = AnalysisManager(
            project_root_dir=project_manager.paths.root_dir,
            group_id=group_id,  # Specify analysis group ID, or set to None for user input
            analysis_config=custom_analysis_setting,
            simple_size=sample_size,  # Current round samplele size
            random_seed=1,  # Current round random seed
            round_id=round_id,  # Current analysis round ID (starting from 0)
            mode=run_mode, # 'new' or 'old'

        )

        #产生input_data
        analysis_manager.generate_input_data()

        #根据input_data进行模拟和保存数据
        analysis_manager.run_simulations_for_round(platform = platform, cpu_num = cpu_num, gpu_num = gpu_num)



    def calculate_sensibility(self, item):

        root_path = Path(item["root_path"])
        group_id = item["group_id"]



        analysis_paths = AnalysisPaths(root_path, group_id)


        output_data_file = analysis_paths.output_data_file
        sobol_results_dir = analysis_paths.sobol_results_dir

        # --- 执行 ---
        calculator = SobolCalculator(output_data_file, sobol_results_dir)
        calculator.calculate_round(round_num=10**5)




if __name__ == "__main__":
    item = {
        "origin_project_path": r"C:\Users\shliu\Desktop\eatest\EA_CAFe_MEBT",
        "root_path": r"C:\Users\shliu\Desktop\eatest\EA_CAFe_MEBT2",
        "run_mode": "new", #这次是重新运行还是老的项目再次运行
        "sample_size": 2,
        "round_id": None,
        "group_id": 1,
        "cal_round_num": -1,


       "platform": "cpu", #"gpu",
        "cpu_num": None,
        "gpu_num": None,

        "this_analysis_setting":{
            'mode': 'block',  # Switch to block mode
            'block_size': 6,
            'parameter_number': 8 * 6,  # Still 48 parameters
            "bounds_lower":
                [[-0.5, -0.5, -2 * MRAD_TO_DEGREE, -2 * MRAD_TO_DEGREE, -0.5, -0.1],
                 # 6 parameter bounds for element type 1
                 [-0.5, -0.5, -2 * MRAD_TO_DEGREE, -2 * MRAD_TO_DEGREE, -2 * MRAD_TO_DEGREE, -0.5]],

            "bounds_upper":
                [[0.5, 0.5, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 0.5, 0.1],  # 6 parameter bounds for element type 1
                 [0.5, 0.5, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 0.5]],

            }
    }
    obj = EaStart()
    obj.run(item)

    res = obj.calculate_sensibility(item)
    print(res)