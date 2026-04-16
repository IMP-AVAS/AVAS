import shutil
import os
from utils.treat_directory import list_files_in_directory
import time
from datetime import datetime
from send2trash import send2trash

from pathlib import Path

# 复制文件到目标文件夹
def copy_file(source_file, target_folder):
    shutil.copy(source_file, target_folder)

#将文件切割成一个个列表（/ \）
def split_file(file_path):
    # 将文件路径使用"/"进行分割
    parts = file_path.split('/')
    # 对每个部分再次使用"\\"进行分割，并将结果扁平化
    parts = [subpart.lower() for part in parts for subpart in part.split('\\')]
    return parts

# 判断哪一个文件是否在文件夹中():
def file_in_directory(file, directory):
    file_list = os.path.normpath(file)
    directory_list = [os.path.normpath(i) for i in list_files_in_directory(directory)]
    # print(file)
    # print(directory_list)
    if file_list in directory_list:
        return True
    else:
        return False


def check_file_update(file_path):
    """
    检查指定文件的最后修改时间。

    参数:
    file_path (str): 文件的完整路径。

    返回:
    str: 文件最后修改时间的人类可读字符串，如果文件不存在则返回错误信息。
    """
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 获取文件的最后修改时间
        last_modified_time = os.stat(file_path).st_mtime
        now = datetime.now().timestamp()
        if now - last_modified_time <= 1:
            #正在更新
            return 1
        else:
            #停止更新
            return 0

    else:
        #"文件不存在"
        return 2



def delete_file(path):
    """
    删除一个文件夹
    :param path:
    :return:
    """
    p = Path(path)
    if not p.exists():
        print("路径不存在")
        return

    if p.is_file():
        p.unlink()  # 删除文件
    elif p.is_dir():
        shutil.rmtree(p)  # 删除整个文件夹
    else:
        print("不是文件也不是文件夹")

if __name__ == "__main__":
    path1 = r"C:\Users\shliu\Desktop\111"
    path2 = r"C:\Users\shliu\Desktop\test_time"
    # res = file_in_directory(path1, path2)
    # print(res)
    delete_file(path1)