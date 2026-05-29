#该文件的作用为生成dst文件

import ctypes
import os
from ctypes import POINTER, c_char_p, cdll
import platform


class GenDst():
    def __init__(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径

        self.dll_dir = os.path.join(parent_directory, "dllfile")
        self.dll_path = os.path.join(parent_directory, 'dllfile', 'AVAS.dll')  # 使用绝对路径连接得到完整的路径
        self.so_path = os.path.join(parent_directory, 'dllfile', 'libAVAS.so')  # 使用绝对路径连接得到完整的路径
        try:
            if platform.system() == "Windows":
                self.library = ctypes.CDLL(self.dll_path)  # 或 WinDLL
            elif platform.system() == "Linux":
                self.AVAS_cdll = cdll.LoadLibrary(self.so_path)  # Load Dynamic Link Library

        except OSError as e:
            if platform.system() == 'Windows':
                # 尝试加载DLL文件
                raise ValueError(f"Failed to load DLL '{self.dll_path}'. Reason: {e}")
            elif platform.system() == "Linux":
                raise ValueError(f"Failed to load so '{self.so_path}'. Reason: {e}")
    def generate_dst(self, input, output):
        if platform.system() == "Windows":
            self.library.GenBunch(ctypes.c_wchar_p(input),
                ctypes.c_wchar_p(output))
        elif platform.system() == "Linux":
            print(input, output)
            input =  ctypes.c_char_p(input.encode('utf-8'))
            output = ctypes.c_char_p(output.encode('utf-8'))

            # input =  ctypes.c_char_p(input),
            # output = ctypes.c_char_p(output)

            self.AVAS_cdll.GenBunch(input,
                output)



if __name__ == '__main__':
    obj = GenDst()
    input = r"C:\Users\wangh\Desktop\test_gdst\beam.txt"
    output = r"C:\Users\wangh\Desktop\test_gdst\beam.dst"
    obj.generate_dst(input, output)