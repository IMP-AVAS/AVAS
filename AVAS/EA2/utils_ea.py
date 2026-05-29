import os
import sys
import shutil
import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional  # 添加这些导入

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def format_sign_space(x):
    """Format number, positive numbers with leading space, negative numbers with sign."""
    if x >= 0:
        return f" {x:.16f}"
    else:
        return f"{x:.16f}"


def get_input(prompt, input_type=str, default=None,
              valid_range=None, exclude=None, retry=True, allow_empty_default=False):
    """
    General interactive input function.

    Parameters:
        prompt: Prompt text
        input_type: Expected type (str, int, float, etc.)
        default: Default value (use by pressing enter)
        valid_range: Valid range (tuple or list)
        exclude: Disallowed values (list or set)
        retry: Whether to allow retry
        allow_empty_default: If default is None, whether to allow empty string input and return None.

    Returns:
        Valid input (converted type)
    """
    while True:
        default_str = f"[Default: {default}] " if default is not None else ""
        user_input = input(f"{prompt} {default_str}").strip()

        # Default value handling
        if not user_input:
            if default is not None:
                return default
            elif allow_empty_default:
                return None

        # Type conversion
        try:
            value = input_type(user_input)
        except ValueError:
            logger.warning(f"Input format error, should be {input_type.__name__} type. Please re-enter.")
            if not retry:
                raise
            continue

        # Range check
        if valid_range is not None:
            if isinstance(valid_range, (tuple, list)) and not (valid_range[0] <= value <= valid_range[-1]):
                logger.warning(f"Please enter value within range {valid_range}. Please re-enter.")
                if retry:
                    continue
                else:
                    raise ValueError("Input out of range")

        # Exclusion check
        if exclude and value in exclude:
            logger.warning(f"Value '{value}' already exists or not allowed, please re-enter.")
            if not retry:
                raise
            continue

        return value


def create_or_load_json_config(file_path: Path, default_config: dict, mode: str = 'new', ask_overwrite=False):
    """
    Create, load, or overwrite JSON configuration file.

    Args:
        file_path (Path): Path to configuration file.
        default_config (dict): Default configuration to write if file doesn't exist.
        mode (str): 'new' for create mode, 'old' for load mode.
        ask_overwrite (bool): In 'new' mode, if file exists, whether to ask about overwriting.

    Returns:
        dict: Loaded or created configuration.
    """

    #如果是新项目，那就把默认值写入到project_settings.json
    if mode == 'new':  # Confirm is create
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        logger.info(f"Created new configuration file: {file_path}")
        return default_config

    #如果是老项目，那就直接加载project_settings.json
    if mode == 'old':
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file {file_path} not found, cannot load.")
        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Successfully loaded configuration file: {file_path}")
        return config

    return {}  # Theoretically won't reach here


def save_json_config(file_path: Path, config: dict):
    """Save configuration dictionary to JSON file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    logger.info(f"Saved configuration file: {file_path}")


def copy_directory(src: Path, dst: Path, overwrite: bool = True, retry_attempts: int = 3, retry_delay_sec: float = 0.1, new_name=None):
    """
    Copy directory, supports overwrite and retry.

    Args:
        src (Path): Source directory path.
        dst (Path): Target directory path.
        overwrite (bool): Whether to overwrite if target directory exists.
        retry_attempts (int): Number of retry attempts.
        retry_delay_sec (float): Retry interval.

    Raises:
        FileExistsError: If target directory exists and overwrite not allowed.
        Exception: If copy fails and retry attempts exhausted.
    """

    if not new_name:
        destination_folder = dst/src.name
    else:
        destination_folder = dst/new_name

    if destination_folder.exists():
        if overwrite:
            shutil.rmtree(destination_folder)
            logger.debug(f"Deleted existing directory: {destination_folder}")
        else:
            raise FileExistsError(f"Target directory already exists and overwrite not allowed: {destination_folder}")



    for attempt in range(retry_attempts):
        try:
            print(151, src, destination_folder)
            shutil.copytree(src, destination_folder)
            if destination_folder.exists():  # Verify if really copied successfully
                logger.debug(f"Successfully copied directory from {src} to {destination_folder}")
                return
        except Exception as e:
            logger.warning(f"Copy failed (attempt {attempt + 1}/{retry_attempts}): {e}")
            if destination_folder.exists():  # If partial copy failed, clean up
                shutil.rmtree(destination_folder)
            time.sleep(retry_delay_sec)

    raise Exception(f"Directory copy failed, still unable to complete after {retry_attempts} retries: {src} -> {destination_folder}")


def read_lines_from_file(file_path: Path, encoding='UTF-8', strip_bom=True) -> List[str]:
    """Read file content, preserve original line breaks, and optionally remove BOM header."""
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    with open(file_path, 'r', encoding=encoding) as f:
        # Read all lines, preserve original line breaks and empty lines
        lines = f.readlines()

        # Handle BOM header
        if strip_bom and lines and lines[0].startswith('\ufeff'):
            lines[0] = lines[0][1:]  # Remove UTF-8 BOM
    return lines

if __name__ == '__main__':
    from pathlib import Path

    src = Path(r"C:\Users\wangh\Desktop\ea_test\AVAS")
    dst = Path(r"C:\Users\wangh\Desktop\ea_test\dst_file")

    copy_directory(src, dst, overwrite=True, retry_attempts=3, retry_delay_sec=0.1)