import argparse
import subprocess
import uuid
import os

from utils.tool import format_output

from utils.treat_directory import list_files_in_directory
from utils.treatfile import delete_file

from utils.inputconfig import InputConfig

from utils.iniconfig import IniConfig
import time
# def submit_job(username: str, output_path: str):
#     job_id = str(uuid.uuid4())[:8]
#     print(f"模拟提交 SLURM 任务：用户名={username}, 输出路径={output_path}")
#     return job_id, "模拟提交成功（开发环境）"


template = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition=cpup{partition}
#SBATCH --nodes=1
#SBATCH --time=01:00:00
#SBATCH --output={tmp_dir}\outputdata.log
#SBATCH --error={tmp_dir}\errordata.log
#SBATCH --cpus-per-task=56

cd {work_dir}
python apis/qt_api/hpc_simmode.py {project_path}
"""

template_gpu = """#!/bin/bash
#SBATCH --job-name={job_name}

#SBATCH --partition=avas
#SBATCH --gres=gpu:1

##SBATCH --nodelist=gpu010

#SBATCH --time=01:00:00
#SBATCH --output={tmp_dir}\outputdata.log
#SBATCH --error={tmp_dir}\errordata.log


cd {work_dir}
mpirun -np 1 python apis/qt_api/hpc_simmode.py {project_path}
"""

# template = """#!/bin/bash
# #SBATCH --job-name={job_name}
#
# #SBATCH --nodes=1
# #SBATCH --time=01:00:00
# #SBATCH --output={tmp_dir}\outputdata.log
# #SBATCH --error={tmp_dir}\errordata.log
#
# cd {work_dir}
# python apis/qt_api/hpc_simmode.py {project_path}
#
# """
######################################
# #!/bin/bash
# #SBATCH --job-name=AVAS_4bad7bc1
#
# #SBATCH --partition=gpup1
# #SBATCH --gres=gpu:1
#
# ##SBATCH --nodelist=gpu002
# #SBATCH --time=01:00:00
# #SBATCH --output=outputdata.log
# #SBATCH --error=errordata.log
# #SBATCH --cpus-per-task=54
#
# export OMPI_MCA_hwloc_base_binding_policy=none
# export OMPI_MCA_rmaps_base_mapping_policy=slot

#export OMPI_MCA_rmaps_base_mapping_policy=slot:PE=54   # 映射：一次拿 28 核
#export OMPI_MCA_hwloc_base_binding_policy=core

# module load cuda/11.8.0-gcc-4.8.5
# module load openmpi/4.1.5-gcc-9.4.0
# module load gcc/9.4.0-gcc-4.8.5
#
# cd /public/home/lzy_gpu/li521
#
# mpirun -np 1  python /public/home/lzy_gpu/li521/test_simmode.py

##################################

def submit_job(**item):
    # item = {"projectPath": ""
    #         ""
    #         }

    project_path = item["projectPath"]
    output_file = os.path.join(project_path, "OutputFile")
    tmp_dir = os.path.join(output_file, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)  # 确保 tmp 目录存在
    all_files_in_tmp_dir = list_files_in_directory(tmp_dir)
    for i in all_files_in_tmp_dir:
        delete_file(i)

    outputdata_path = os.path.join(tmp_dir, "outputdata.log")
    errordata_path = os.path.join(tmp_dir, "errordata.log")

    if os.path.exists(outputdata_path):
        os.remove(outputdata_path)
    if os.path.exists(errordata_path):
        os.remove(errordata_path)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    work_dir = os.path.dirname(script_directory)  # 获取上级目录的路径
    print(work_dir)

    job_name = "AVAS_" + str(uuid.uuid4())[:8]
    job_script = f"{job_name}.sh"

    job_script_path = os.path.join(tmp_dir, job_script)
    print(f"脚本写入路径: {job_script_path}")

    # 读取模板并填充

    # 确定节点
    iniobj = IniConfig()
    item_ini = {"projectPath": project_path}

    ini_res = iniobj.create_from_file(item_ini)
    ini_res = ini_res["data"]["iniParams"]

    if ini_res["input"]["device"] == "cpu":
        device = "cpu"
    elif ini_res["input"]["device"] == "gpu":
        device = "gpu"
    else:
        device = "cpu"
    if device == "cpu":
        partition = 8
        script_content = (template.replace("{job_name}", job_name).
                          replace("{project_path}", project_path).
                          replace("{tmp_dir}", tmp_dir).
                          replace("{work_dir}", work_dir).
                          replace("{partition}", str(partition))
                          )
    elif device == "gpu":
        partition = 8
        script_content = (template_gpu.replace("{job_name}", job_name).
                          replace("{project_path}", project_path).
                          replace("{tmp_dir}", tmp_dir).
                          replace("{work_dir}", work_dir).
                          replace("{partition}", str(partition))
                          )

    script_content = script_content.replace("\\", "/")

    # script_content = script_content.replace("{project_path}", project_path)
    # 写入 SLURM 脚本
    with open(job_script_path, "w") as f:
        f.write(script_content)

    # 提交作业
    result = subprocess.run(["sbatch", job_script_path], capture_output=True, text=True)
    lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    rows = [line.split() for line in lines]
    job_id = rows[0][3]

    # job_id = 111

    kwargs = {
        "jobInfo": {
            "projectPath": project_path,
            "jobName": job_name,
            "jobId": job_id,
        }
    }

    output = format_output(**kwargs)

    return output



if __name__ == "__main__":
    item = {"projectPath": r"C:\Users\anxin\Desktop\test_schedule\cafe_avas"}
    submit_job(**item)