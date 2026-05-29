import os
import shutil
import json
import datetime
from pathlib import Path
from typing import Optional

from utils_ea import logger, get_input, create_or_load_json_config, save_json_config
from config import DEFAULT_PROJECT_SETTINGS, MATPLOTLIB_FONT_SETTINGS
from paths import ProjectPaths
from typing import List, Dict, Any, Optional
from utils_ea import copy_directory

class ProjectManager:
    """
    Responsible for basic management of AVAS engineering projects, including directory structure, global configuration.
    This is the top-level management class for projects.
    """

    def __init__(self, root_path: str, origin_project_path: str, mode: str = 'new'):
        """
        Initialize project manager.
        Args:
            root_path (str): Path to project root directory.
            mode (str): 'new' create new project, 'old' load existing project.
        """

        self.paths = ProjectPaths(Path(root_path))
        self.base_dir = Path(origin_project_path["base_dir"])
        self.field_dir = Path(origin_project_path["field_dir"])

        self.config: dict = {}  # Project global configuration

        self._initialize_matplotlib()

        if mode == 'new':
            #如果是新的，那就生成所需要的基础文件
            self._setup_new_project()
        elif mode == 'old':
            self._load_existing_project()
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'new' or 'old'.")

        # Update project last opened time
        self.config['last_opened'] = datetime.datetime.now().isoformat()
        save_json_config(self.paths.settings_file, self.config)
        logger.info(f"Project '{self.paths.root_dir.name}' initialized successfully.")

    def _initialize_matplotlib(self):
        """Set matplotlib Chinese fonts."""
        import matplotlib
        matplotlib.rcParams.update(MATPLOTLIB_FONT_SETTINGS)
        logger.debug("Matplotlib fonts configured.")

    def _setup_new_project(self):
        """Set up new project directory structure and initial files."""
        #直接创建新的项目
        self.paths.create_project_dirs()
        #把原来的文件复制到dst文件

        copy_directory(self.base_dir, self.paths.root_dir,True)
        copy_directory(self.field_dir, self.paths.root_dir, True)

        self.config = create_or_load_json_config(self.paths.settings_file, DEFAULT_PROJECT_SETTINGS, mode='new')
        self.config['path_root'] = str(self.paths.root_dir)  # Store root_path in configuration

    def _load_existing_project(self):
        """Load existing project."""
        if not self.paths.root_dir.exists():
            raise FileNotFoundError(f"Project directory {self.paths.root_dir} does not exist.")

        self.config = create_or_load_json_config(self.paths.settings_file, DEFAULT_PROJECT_SETTINGS, mode='old')

        # Verify path_root consistency
        if self.config.get('path_root') and self.config['path_root'] != str(self.paths.root_dir):
            logger.warning(
                f"Project root path in configuration file '{self.config['path_root']}' differs from current load path '{self.paths.root_dir}'. Will use current path.")
            self.config['path_root'] = str(self.paths.root_dir)


    def get_next_analysis_group_id(self) -> int:
        """Get next available analysis group ID.""" #如果是003，那么这里就是004

        if not self.paths.root_dir.exists():
            return []

        groups = []
        for item in self.paths.root_dir.iterdir():
            if item.is_dir() and item.name.endswith("analysis"):
                prefix = item.name[:3]
                if prefix.isdigit():
                    groups.append(int(prefix))

        groups.sort()

        existing_groups = groups

        next_group = (max(existing_groups) + 1) if existing_groups else 1

        return next_group

    @property
    def current_analysis_group(self) -> Optional[int]:
        """Get or set current active analysis group ID."""
        #目前正在分析的id
        return self.config.get('current_analysis_group')

    @current_analysis_group.setter
    def current_analysis_group(self, group_id: int):
        self.config['current_analysis_group'] = group_id
        save_json_config(self.paths.settings_file, self.config)
        logger.info(f"Current analysis group set to {group_id:03d}")