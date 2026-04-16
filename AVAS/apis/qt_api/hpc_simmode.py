import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from apis.qt_api.SimMode import SimMode


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("hpc_simmode.py parameter Error")

    project_path = sys.argv[1]
    item = {"projectPath": project_path}
    obj = SimMode(item)
    obj.run()

