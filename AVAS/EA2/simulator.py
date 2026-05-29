import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from apis.qt_api.SimMode import SimMode  # Assume this API is in apis directory
from config import SIMULATION_RESULT_COLUMNS, SIMULATION_UNIT_CONVERSION_FACTORS
from utils_ea import logger, format_sign_space, read_lines_from_file


class AvasSimulator:
    """
    Encapsulate AVAS simulator execution and result parsing.
    """

    def __init__(self):
        self._sim_mode_class = SimMode
        self._result_columns = SIMULATION_RESULT_COLUMNS
        self._unit_conversion_factors = SIMULATION_UNIT_CONVERSION_FACTORS

    def _run_simulation(self, project_path: Path):
        """
        Run single AVAS simulation.

        Args:
            project_path (Path): Simulation project path (i.e., clone directory).
        """
        logger.debug(f"Running simulation in {project_path}.")
        item = {'projectPath': str(project_path)}
        try:
            obj = self._sim_mode_class(item)
            obj.run()
        except Exception as e:
            logger.error(f"Simulation failed in {project_path}: {e}")
            raise

    def _parse_results(self, result_file: Path) -> List[float]:
        """
        Parse simulation result file errors_par_tot.txt.
        """
        lines = read_lines_from_file(result_file)

        if len(lines) < 2:
            logger.error(f"Result file {result_file} has insufficient lines, cannot parse.")
            raise ValueError(f"Result file {result_file} has insufficient lines.")

        # Assume results are in third line (index 2)
        res_parts = lines[1].split()
        if len(res_parts) < 11:  # Ensure enough columns to parse first 10
            logger.error(f"Result file {result_file} third line data format incorrect or insufficient columns.")
            raise ValueError(f"Result file {result_file} format error.")

        try:
            # Original code indices and meanings:
            # res[2]: emittance_x
            # res[3]: emittance_y
            # res[4]: emittance_z
            # res[5]: centroid_x
            # res[6]: centroid_y
            # res[9]: envelope_x
            # res[10]: envelope_y

            raw_values = {
                'emittance_x': float(res_parts[2]),
                'emittance_y': float(res_parts[3]),
                'emittance_z': float(res_parts[4]),
                'centroid_x': float(res_parts[5]),
                'centroid_y': float(res_parts[6]),
                'envelope_x': float(res_parts[9]),
                'envelope_y': float(res_parts[10]),
                'alpha_x': float(res_parts[14]),
                'beta_x': float(res_parts[15]),
                'alpha_y': float(res_parts[16]),
                'beta_y': float(res_parts[17]),
                # ...
            }

            parsed_results = []
            for col_name in self._result_columns:
                base_name = col_name.replace('_mm', '')  # Remove unit suffix to find raw data
                value = raw_values.get(base_name)
                if value is None:
                    raise KeyError(f"Column not found in raw results: {base_name}")

                # Apply unit conversion
                if col_name in self._unit_conversion_factors:
                    value *= self._unit_conversion_factors[col_name]
                parsed_results.append(value)

            return parsed_results

        except (IndexError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse result file {result_file}: {e}")
            raise ValueError(f"Failed to parse result file {result_file}: {e}")

    def run_and_get_result(self, clone_path: Path, result_file: Path) -> List[str]:
        """
        Run simulation and parse results upon completion.
        """
        self._run_simulation(clone_path)
        raw_results = self._parse_results(result_file)
        # Format results as strings, consistent with original code
        return [format_sign_space(x) for x in raw_results]
