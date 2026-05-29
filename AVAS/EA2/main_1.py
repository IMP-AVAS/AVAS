import sys

# Chinese font settings (Windows recommended SimHei, Linux can use SimSun or NotoSansCJK)
# Note: These settings have been moved to config.py and ProjectManager.__init__,
# re-setting here might override, or just to ensure it works even without ProjectManager instantiation.
# Better approach is to set uniformly when ProjectManager is instantiated.
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # HeiTi
# matplotlib.rcParams['axes.unicode_minus'] = False  # Fix minus sign display as square

from pathlib import Path

# # 获取项目根目录 (AVAS_control)
# project_root = Path(__file__).parent.parent
#
# # 将项目根目录添加到 Python 路径
# sys.path.insert(0, str(project_root))
import sys
sys.path.append(r"F:\AVAS_CONTROL\AVAS\AVAS")

# Import refactored modules
from project import ProjectManager
from analysis import AnalysisManager
from config import MRAD_TO_DEGREE, DEFAULT_ANALYSIS_SETTINGS
from utils_ea import logger, get_input  # Import logger

if __name__ == "__main__":
    # Configure log level
    logger.setLevel('INFO')

    test_root_path = Path(r'C:\Users\wangh\Desktop\ea_test\AVAS\EA_CAFe_MEBT')

    # --- Phase 1: Project initialization or loading ---
    try:
        # Create a new project
        # project_manager = ProjectManager(root_path=str(test_root_path), mode='new')
        # input('Please prepare files in base_dir and field_dir')

        # Or load an existing project
        project_manager = ProjectManager(root_path=str(test_root_path), mode='old')

    except Exception as e:
        logger.error(f'Project initialization failed: {e}')
        sys.exit(1)

    # --- Phase 2: Analysis group initialization or loading ---
    # Can choose via user interaction or code specification
    try:
        # Get next available analysis group ID as default
        next_group_id = project_manager.get_next_analysis_group_id()

        # Example analysis settings (can modify as needed or fully customize)
        custom_analysis_setting = DEFAULT_ANALYSIS_SETTINGS.copy()
        """
            Using MEBT as default example

            DEFAULT_ANALYSIS_SETTINGS = {
                'mode': 'single',  # 'single', 'block'
                'parameter_number': 8 * 6,
                "elements_quantity": [2, 6], # Example: [2 elements type 1, 6 elements type 3]
                "elements_type": [1, 3],     # Corresponding element types above
                "bounds":
                    [[0.5, 0.5, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 0.5, 0.1], # 6 parameter bounds for element type 1
                     [0.5, 0.5, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 2 * MRAD_TO_DEGREE, 0.5]], # 6 parameter bounds for element type 3
                'block_size': 6, # Only used when mode='block'
                'error_commands': [ # Error command templates corresponding to elements_type
                    ['err_cav_ncpl_dyn', '1', '0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0'],
                    ['err_quad_ncpl_dyn', '1', '0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0']
                ]
            }
        """
        custom_analysis_setting.update({
            'mode': 'block',  # Switch to block mode
            'block_size': 6,
            'parameter_number': 8 * 6,  # Still 48 parameters
            # ... Other parameters can also be overridden
        })

        # Create or load an analysis group
        analysis_manager = AnalysisManager(
            project_root_dir=project_manager.paths.root_dir,
            group_id=7,  # Specify analysis group ID, or set to None for user input
            analysis_config=custom_analysis_setting,
            simple_size=500,  # Current round sample size
            random_seed=1,  # Current round random seed
            round_id=0,  # Current analysis round ID (starting from 0)
            mode='new'  # 'new' or 'old'
        )

        # Example: To run second round, can do this:
        # analysis_manager = AnalysisManager(
        #     project_root_dir=project_manager.paths.root_dir,
        #     group_id=1,
        #     analysis_config=None, # If configuration unchanged, can omit
        #     simple_size=20, # Change sample size
        #     random_seed=analysis_manager.config['random'][-1] + 1, # Auto-increment random seed
        #     round_id=analysis_manager.config['round_id'][-1] + 1, # Auto-increment round ID
        #     mode='old' # Load in old mode and start new round
        # )

    except Exception as e:
        logger.error(f"Analysis group initialization failed: {e}")
        sys.exit(1)

    # --- Phase 3: Execute analysis workflow ---
    try:
        logger.info("\n--- Starting input data generation ---")
        analysis_manager.generate_input_data()

        logger.info("\n--- Starting simulation execution ---")
        # Can specify CPU count, e.g., cpu_count() means all CPU cores
        analysis_manager.run_simulations_for_round(cpu_number=1,
                                                   overwrite_output='y')  # y means force overwrite results

        logger.info("\n--- Analysis workflow completed ---")

    except Exception as e:
        logger.critical(f"Critical error occurred during analysis execution: {e}", exc_info=True)
        sys.exit(1)