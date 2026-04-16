import os

folder_path = r"C:\Users\anxin\Desktop\AVAS_control"  # 替换为你要列出文件的文件夹路径

def list_files(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list



files = list_files(folder_path)

for file in files:
    print(file)
