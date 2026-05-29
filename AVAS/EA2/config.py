import math

# Constants
MRAD_TO_DEGREE = 180 / (math.pi * 1000)  # Milliradians to degrees 毫弧度

# Matplotlib Chinese font settings
MATPLOTLIB_FONT_SETTINGS = {
    'font.sans-serif': ['SimHei'],  # HeiTi
    'axes.unicode_minus': False     # Fix minus sign display as square
}

# Default project settings
DEFAULT_PROJECT_SETTINGS = {
    'version': '1.0',
    'last_opened': None,
    'current_analysis_group': None
}

# Default analysis settings
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

# Simulation result parsing configuration
SIMULATION_RESULT_COLUMNS = [
    'emittance_x', 'emittance_y', 'emittance_z',
    'centroid_x_mm', 'centroid_y_mm',
    'envelope_x_mm', 'envelope_y_mm',
    # 'alpha_x', 'beta_x', 'alpha_y', 'beta_y' # If more columns need parsing
]

SIMULATION_UNIT_CONVERSION_FACTORS = {
    'centroid_x_mm': 1000,
    'centroid_y_mm': 1000,
    'envelope_x_mm': 1000,
    'envelope_y_mm': 1000,
}