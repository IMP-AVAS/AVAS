import sys

# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')
from core.LongAcceleratorEngine import LongAcceleratorEngine
import os
import shutil

class LongAccelerator():
    """
    多粒子模拟
    """
    def __init__(self, project_path, kind):   #*arg **kwargs #dllpath写死
        self.project_path = project_path
        self.LongAccelerator_engine = LongAcceleratorEngine(kind)
        self.kind = kind
    #     return res
    def copy_file(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
        if self.kind == 2:

            source_r = os.path.join(parent_directory, 'staticfile', 'ifr.txt')  # 使用绝对路径连接得到完整的路径
            source_z = os.path.join(parent_directory, 'staticfile', 'ifz.txt')  # 使用绝对路径连接得到完整的路径

            target_r = os.path.join(self.project_path, 'InputFile', 'ifr.txt')
            target_z = os.path.join(self.project_path, 'InputFile', 'ifz.txt')

            shutil.copy(source_r, target_r)
            shutil.copy(source_z, target_z)

        elif self.kind == 3:
            source_x = os.path.join(parent_directory, 'staticfile', 'ifx3d_3.txt')  # 使用绝对路径连接得到完整的路径
            source_z = os.path.join(parent_directory, 'staticfile', 'ifz3d_3.txt')  # 使用绝对路径连接得到完整的路径

            target_x = os.path.join(self.project_path, 'InputFile', 'ifx3d_3.txt')
            target_z = os.path.join(self.project_path, 'InputFile', 'ifz3d_3.txt')

            shutil.copy(source_x, target_x)
            shutil.copy(source_z, target_z)




    def run(self, input_file='InputFile', output_file='OutputFile'):
        self.copy_file()
        inputfilepath = os.path.join(self.project_path, input_file)
        outputfilePath = os.path.join(self.project_path, output_file)
        print(inputfilepath)
        print(outputfilePath)

        res_tmp = self.LongAccelerator_engine.get_path(inputfilepath, outputfilePath)

        res = self.LongAccelerator_engine.main_agent(1)
        print(res)
        if res == 1:
            raise Exception('error')

        return res

# if __name__ == "__main__":
#     project_path = r'C:\Users\anxin\Desktop\126'
#     AVAS_obj = LongAccelerator(project_path, 3)
#     AVAS_obj.run()
