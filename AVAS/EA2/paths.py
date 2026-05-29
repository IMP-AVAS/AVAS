from pathlib import Path
import os
import shutil
from typing import List

class ProjectPaths:
    """Manage top-level project directory structure and file paths."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()  # Ensure absolute path

        self.base_dir = self.root_dir / 'base_dir'
        self.field_dir = self.root_dir / 'field_dir'
        self.settings_file = self.root_dir / 'project_settings.json'

    def create_project_dirs(self):
        """Create basic project directory structure."""
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.field_dir.mkdir(parents=True, exist_ok=True)

    def is_project_initialized(self) -> bool:
        """Check if project directory is initialized (by checking settings.json)."""
        return self.settings_file.exists()



class AnalysisPaths:
    """Manage directory structure and file paths for specific analysis groups."""

    def __init__(self, project_root_dir: Path, group_id: int):
        self.group_id = group_id
        self.project_root_dir = project_root_dir.resolve()

        self.analysis_dir_name = f"{group_id:03d}analysis"
        self.analysis_dir = self.project_root_dir / self.analysis_dir_name

        self.clones_dir = self.analysis_dir / 'clones_dir'
        self.data_dir = self.analysis_dir / 'data_dir'
        self.analysis_settings_file = self.analysis_dir / 'analysis_settings.json'

        self.input_data_file = self.data_dir / 'InputData.h5'
        self.output_data_file = self.data_dir / 'OutData.h5'
        # self.sobol_results_dir = self.data_dir / 'sobol_result' # If needed

    def create_analysis_dirs(self):
        """Create analysis group directory structure."""
        self.analysis_dir.mkdir(parents=True, exist_ok=True) #OO1ANALYSIS
        self.clones_dir.mkdir(parents=True, exist_ok=True) # OO1ANALYSIS/clones_dir
        # self.sobol_results_dir.mkdir(parents=True, exist_ok=True) # If needed

    def get_clone_path(self, clone_id: int) -> Path:
        """Get path for specific clone directory."""
        return self.clones_dir / f'base_{clone_id}'

    def get_clone_input_file_path(self, clone_id: int, filename='lattice_mulp.txt') -> Path:
        """Get input file path in specific clone directory."""
        return self.get_clone_path(clone_id) / 'InputFile' / filename

    def get_clone_output_file_path(self, clone_id: int, filename='errors_par_tot.txt') -> Path:
        """Get output file path in specific clone directory."""
        return self.get_clone_path(clone_id) / 'OutputFile' / filename