
import ctypes

import os
from ctypes import POINTER, c_char_p, cdll
import platform


class PartranSimCpuEngine():
    def __init__(self, item=None):
        self.env_par_mode = item.get("env_par_mode")

        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径

        self.dll_dir = os.path.join(parent_directory, "dllfile")

        self.par_dll_path = os.path.join(parent_directory, 'dllfile', 'AVAS.dll')  # 使用绝对路径连接得到完整的路径
        self.par_so_path = os.path.join(parent_directory, 'dllfile', 'libAVAS.so')  # 使用绝对路径连接得到完整的路径


        if platform.system() == "Windows":
            self.library_win = ctypes.CDLL(self.par_dll_path)  # 或 WinDLL
        elif platform.system() == "Linux":
            self.library_linux = cdll.LoadLibrary(self.par_so_path)  # Load Dynamic Link Library


    def get_path(self, inputfilepath, outputfilePath, fieldfilePath):
        if platform.system() == 'Windows':
            inputfilepath = ctypes.c_wchar_p(inputfilepath)
            outputfilePath = ctypes.c_wchar_p(outputfilePath)
            fieldfilePath = ctypes.c_wchar_p(fieldfilePath)
            res = self.library_win.path(inputfilepath, outputfilePath, fieldfilePath)

        elif platform.system() == "Linux":
            inputfilepath = ctypes.c_char_p(inputfilepath.encode('utf-8'))  # 转为字节并包装为 c_char_p
            outputfilePath = ctypes.c_char_p(outputfilePath.encode('utf-8'))
            fieldfilePath = ctypes.c_char_p(fieldfilePath.encode('utf-8'))
            res = self.library_linux.path(inputfilepath, outputfilePath, fieldfilePath)
        return res

    # input, beam, lattice都应该为自定义的结构体
    def main_agent(self, value):
        value = ctypes.c_int(value)
        value = ctypes.pointer(value)
        if platform.system() == 'Windows':
            res = self.library_win.main_agent(value)
        elif platform.system() == "Linux":
            res = self.library_linux.main_agent(value)

        return res


class EnvSimCpuEngine():
    def __init__(self, item=None):
        self.env_par_mode = item.get("env_par_mode")

        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径

        self.dll_dir = os.path.join(parent_directory, "dllfile")

        self.env_dll_path = os.path.join(parent_directory, 'dllfile', 'LinacMTLIB.dll')

        if platform.system() == "Windows":
            self.library_win = ctypes.CDLL(self.env_dll_path)
        elif platform.system() == "Linux":
            pass

    def get_path(self, inputfilepath, outputfilePath, fieldfilePath):
        if platform.system() == "Windows":
            inputfilepath = ctypes.c_wchar_p(inputfilepath)
            outputfilePath = ctypes.c_wchar_p(outputfilePath)
            fieldfilePath = ctypes.c_wchar_p(fieldfilePath)
            res = self.library_win.path(inputfilepath, outputfilePath, fieldfilePath)
        elif platform.system() == "Linux":
            pass

        return res

    # input, beam, lattice都应该为自定义的结构体
    def main_agent(self, value):

        value = ctypes.c_int(value)
        value = ctypes.pointer(value)
        if platform.system() == 'Windows':
            res = self.library_win.main_agent(value)
        elif platform.system() == "Linux":
            res = self.library_linux.main_agent(value)

        return res











def run_agent(inputfile, outputfile, fieldfile):
    obj = MultiParticleEngine()
    obj.get_path(inputfile, outputfile, fieldfile)
    obj.main_agent(1)
if __name__ == '__main__':
    project_path = r"C:\Users\wangh\Desktop\ip_safe_lebt\ip_safe_lebt"
    inputfile = os.path.join(project_path, "InputFile")
    outputfile = os.path.join(project_path, "OutputFile")
    fieldfile = os.path.join(project_path, "InputFile")

    item = {
        "env_par_mode": "par",
    }
    obj = MultiParticleEngine(item)
    obj.get_path(inputfile, outputfile, fieldfile)
    obj.main_agent(1)

    # import threading
    # import time
    # import os
    # from multiprocessing import Process
    #
    #
    # # 创建一个停止标志，用于停止执行
    # obj = MultiParticleEngine()
    # obj.get_path(inputfile, outputfile, fieldfile)
    # #
    # # obj.main_agent(0)
    #
    # process = Process(target=run_agent, args=(inputfile, outputfile, fieldfile))
    # process.start()

