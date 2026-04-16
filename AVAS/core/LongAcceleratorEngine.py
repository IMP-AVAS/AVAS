import ctypes
import sys
import os

class LongAcceleratorEngine():
    def __init__(self, kind):
        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
        if kind == 2:
            self.dll_path = os.path.join(parent_directory, 'dllfile', 'LongAccelerator2.dll')  # 使用绝对路径连接得到完整的路径
        elif kind == 3:
            self.dll_path = os.path.join(parent_directory, 'dllfile', 'LongAccelerator3.dll')  # 使用绝对路径连接得到完整的路径

        try:
            # 尝试加载DLL文件
            self.library = ctypes.CDLL(self.dll_path)

        except OSError as e:
            # 如果DLL文件不存在或加载出错，使用raise引发自定义的异常
            raise ValueError(f"Failed to load DLL '{self.dll_path}'. Reason: {e}")

    def get_path(self, inputfilepath, outputfilePath):

        inputfilepath = ctypes.c_wchar_p(inputfilepath)
        outputfilePath = ctypes.c_wchar_p(outputfilePath)

        res = self.library.path(inputfilepath, outputfilePath)

        return res

    #input, beam, lattice都应该为自定义的结构体
    def main_agent(self, value):
        res = self.library.main_agent(value)
        return res


