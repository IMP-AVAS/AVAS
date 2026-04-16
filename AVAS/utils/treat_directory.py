import os
import shutil
from send2trash import send2trash
from pathlib import Path

# def list_files_in_directory(directory):
#     """
#     查找一个文件夹下面的所有文件
#     :param directory:
#     :return:【】
#     """
#     files = []
#     for root, _, file_names in os.walk(directory):
#         for file_name in file_names:
#             files.append(os.path.join(root, file_name))
#         break
#
#     files1 = []
#     for root, _, file_names in os.walk(directory):
#         files1.append(root)
#     files += files1[1:]
#     return files

def list_files_in_directory(directory, sort_by="name", reverse=False):
    """
    查找一个文件夹下面的所有文件，并按时间排序
    :param directory: 目标文件夹路径
    :param sort_by: 排序依据，可选 "mtime"（修改时间）或 "ctime"（创建时间）
    :param reverse: 是否降序（最新的文件在前）
    :return: 按时间排序的文件列表
    """

    folder_path = Path(directory)  # 目标文件夹路径
    if sort_by == "name":
        file_list = [f.as_posix() for f in folder_path.iterdir()]
        return file_list


    elif sort_by == "mtime":
        #"修改时间"
        files_with_time = [(f, f.stat().st_mtime) for f in folder_path.iterdir()]

        # 按时间排序（最新的文件排在最前）
        files_with_time.sort(key=lambda x: x[1], reverse=reverse)

        files_with_time = [i[0].as_posix() for i in files_with_time]
        return files_with_time



def copy_directory(source_folder, destination_folder, new_name=None):
    """
    复制一个文件夹
    :param source_folder:
    :param destination_folder:
    :param new_name:
    :return:
    """
    # 修改目标文件夹的名字
    if not new_name:
        destination_folder = os.path.join(destination_folder, source_folder.split("\\")[-1])
    else:
        destination_folder = os.path.join(destination_folder, new_name)

    if os.path.exists(destination_folder):
        send2trash(destination_folder)

    shutil.copytree(source_folder, destination_folder)

def delete_directory(path):
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

    path = r"C:\Users\shliu\Desktop\InputFile"
    res = list_files_in_directory(path, reverse=True)
    print(res)

