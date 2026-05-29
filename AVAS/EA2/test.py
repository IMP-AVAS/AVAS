import math
import os
import sys
from pathlib import Path

# 获取项目根目录 (AVAS_control)
project_root = Path(__file__).parent.parent
# print(project_root)
# sys.exit()
# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(project_root))

from apis.qt_api.SimMode import SimMode


def run_avas(path):
    item = {'projectPath': path,}
    obj = SimMode(item)
    obj.run()


path_temp = Path('/public/home/likai/AVAS_control-dev2/ea_avas_2/no_error_1')
print(path_temp)
run_avas(path_temp)
