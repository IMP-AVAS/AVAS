

import os

# script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
# parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
#
# dll_dir = os.path.join(parent_directory, "dllfile")
#
# os.add_dll_directory(dll_dir)

import platform
import ctypes
import ctypes.wintypes as wt
from ctypes import cdll
from contextlib import contextmanager

# ------------------ Windows DLL search flags (Python 3.8+) ------------------
LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR  = 0x00000100
LOAD_LIBRARY_SEARCH_DEFAULT_DIRS  = 0x00001000
WINMODE = LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR | LOAD_LIBRARY_SEARCH_DEFAULT_DIRS

# ------------------ Diagnostics: list loaded modules ------------------
def list_loaded_modules_keyword(keyword: str):
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)

    EnumProcessModules = psapi.EnumProcessModules
    EnumProcessModules.argtypes = [wt.HANDLE, ctypes.POINTER(wt.HMODULE), wt.DWORD, ctypes.POINTER(wt.DWORD)]
    EnumProcessModules.restype = wt.BOOL

    GetModuleFileNameW = k32.GetModuleFileNameW
    GetModuleFileNameW.argtypes = [wt.HMODULE, wt.LPWSTR, wt.DWORD]
    GetModuleFileNameW.restype = wt.DWORD

    hProcess = k32.GetCurrentProcess()
    arr = (wt.HMODULE * 4096)()
    needed = wt.DWORD()

    if not EnumProcessModules(hProcess, arr, ctypes.sizeof(arr), ctypes.byref(needed)):
        return []

    n = needed.value // ctypes.sizeof(wt.HMODULE)
    out = []
    buf = ctypes.create_unicode_buffer(4096)
    for i in range(n):
        if GetModuleFileNameW(arr[i], buf, 4096):
            p = buf.value
            if keyword.lower() in p.lower():
                out.append(p)
    return out

@contextmanager
def without_qt_bin_on_path():
    """临时移除 Qt bin，避免同名 DLL 抢占（退出后恢复 PATH）。"""
    old = os.environ.get("PATH", "")
    parts = old.split(";")
    parts = [p for p in parts if ("PyQt5\\Qt5\\bin" not in p and "PyQt6\\Qt6\\bin" not in p)]
    os.environ["PATH"] = ";".join(parts)
    try:
        yield
    finally:
        os.environ["PATH"] = old

# ------------------ Engine ------------------
# class MultiParticleEngine:
#     def __init__(self):
#         script_directory = os.path.dirname(os.path.abspath(__file__))
#         parent_directory = os.path.dirname(script_directory)
#
#         self.dll_dir  = os.path.join(parent_directory, "dllfile")
#         self.dll_path = os.path.join(self.dll_dir, "AVAS.dll")
#         self.so_path  = os.path.join(parent_directory, "dllfile", "libAVAS.so")
#
#         # 必须保存 add_dll_directory 的句柄，否则会失效
#         self._dll_dir_handles = []
#         # 保存预加载 DLL 的引用，避免被 GC
#         self._preloaded = []
#
#         try:
#             if platform.system() == "Windows":
#                 if not os.path.isdir(self.dll_dir):
#                     raise FileNotFoundError(f"dll_dir not found: {self.dll_dir}")
#                 if not os.path.isfile(self.dll_path):
#                     raise FileNotFoundError(f"AVAS.dll not found: {self.dll_path}")
#
#
#                 print("Before load, AVAS modules:", list_loaded_modules_keyword("AVAS"))
#
#                 # 5) 加载 AVAS.dll（加载瞬间可临时移除 Qt bin）
#                 with without_qt_bin_on_path():
#                     self.library = ctypes.WinDLL(self.dll_path, winmode=WINMODE)
#
#                 # 6) 加载后打印（可选）
#                 print("After load, AVAS modules:", list_loaded_modules_keyword("AVAS"))
#
#                 # 7) 设置函数签名（强烈建议，避免参数传错导致 native 崩溃）
#                 #    根据你实际 C 接口改；这里按你用法先给出常见签名
#                 self.library.path.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p]
#                 self.library.path.restype  = ctypes.c_int
#
#                 self.library.main_agent.argtypes = [ctypes.POINTER(ctypes.c_int)]
#                 self.library.main_agent.restype  = ctypes.c_int
#
#             elif platform.system() == "Linux":
#                 if not os.path.isfile(self.so_path):
#                     raise FileNotFoundError(f"libAVAS.so not found: {self.so_path}")
#                 self.AVAS_cdll = cdll.LoadLibrary(self.so_path)
#
#                 # Linux 下也建议设签名（按实际接口调整）
#                 self.AVAS_cdll.path.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
#                 self.AVAS_cdll.path.restype  = ctypes.c_int
#                 self.AVAS_cdll.main_agent.argtypes = [ctypes.POINTER(ctypes.c_int)]
#                 self.AVAS_cdll.main_agent.restype  = ctypes.c_int
#
#         except Exception as e:
#             raise ValueError(f"Failed to init MultiParticleEngine. Reason: {e}")
#
#     def get_path(self, inputfilepath, outputfilePath, fieldfilePath):
#         if platform.system() == "Windows":
#             # 直接传 str 即可（argtypes 已设为 c_wchar_p）
#             return self.library.path(inputfilepath, outputfilePath, fieldfilePath)
#         else:
#             return self.AVAS_cdll.path(
#                 inputfilepath.encode("utf-8"),
#                 outputfilePath.encode("utf-8"),
#                 fieldfilePath.encode("utf-8"),
#             )
#
#     def main_agent(self, value: int):
#         v = ctypes.c_int(int(value))
#         pv = ctypes.pointer(v)
#
#         # 触发调用前后再查一次模块（很多依赖会 delay-load）
#         if platform.system() == "Windows":
#
#             res = self.library.main_agent(pv)
#
#             return res
#         else:
#             return self.AVAS_cdll.main_agent(pv)

class MultiParticleEngine():
    def __init__(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径

        self.dll_dir = os.path.join(parent_directory, "dllfile")
        self.dll_path = os.path.join(parent_directory, 'dllfile', 'AVAS.dll')  # 使用绝对路径连接得到完整的路径
        self.so_path = os.path.join(parent_directory, 'dllfile', 'libAVAS.so')  # 使用绝对路径连接得到完整的路径
        # 必须保存 add_dll_directory 的句柄，否则会失效
        self._dll_dir_handles = []
        # 保存预加载 DLL 的引用，避免被 GC
        self._preloaded = []

        try:
            if platform.system() == "Windows":

                print("Before load, MSVCP modules:", list_loaded_modules_keyword("msvcp140"))
                self.library = ctypes.CDLL(self.dll_path)  # 或 WinDLL
                print("After load, MSVCP modules:", list_loaded_modules_keyword("msvcp140"))
                print("<<" * 32)
            elif platform.system() == "Linux":
                self.AVAS_cdll = cdll.LoadLibrary(self.so_path)  # Load Dynamic Link Library

        except OSError as e:
            if platform.system() == 'Windows':
                # 尝试加载DLL文件
                raise ValueError(f"Failed to load DLL '{self.dll_path}'. Reason: {e}")
            elif platform.system() == "Linux":
                raise ValueError(f"Failed to load so '{self.so_path}'. Reason: {e}")

    def get_path(self, inputfilepath, outputfilePath, fieldfilePath):
        if platform.system() == 'Windows':
            inputfilepath = ctypes.c_wchar_p(inputfilepath)
            outputfilePath = ctypes.c_wchar_p(outputfilePath)
            fieldfilePath = ctypes.c_wchar_p(fieldfilePath)
            res = self.library.path(inputfilepath, outputfilePath, fieldfilePath)

        elif platform.system() == "Linux":
            inputfilepath = ctypes.c_char_p(inputfilepath.encode('utf-8'))  # 转为字节并包装为 c_char_p
            outputfilePath = ctypes.c_char_p(outputfilePath.encode('utf-8'))
            fieldfilePath = ctypes.c_char_p(fieldfilePath.encode('utf-8'))
            res = self.AVAS_cdll.path(inputfilepath, outputfilePath, fieldfilePath)

        return res

    # input, beam, lattice都应该为自定义的结构体
    def main_agent(self, value):

        value = ctypes.c_int(value)
        value = ctypes.pointer(value)
        if platform.system() == 'Windows':
            res = self.library.main_agent(value)
        elif platform.system() == "Linux":
            res = self.AVAS_cdll.main_agent(value)

        return res

# ------------------ test ------------------
if __name__ == "__main__":

    project_path =r"F:\using\test_avas_qt\cafe_AVAS"
    inputfile = os.path.join(project_path, "InputFile")
    outputfile = os.path.join(project_path, "OutputFile")
    fieldfile = os.path.join(project_path, "InputFile")

    obj = MultiParticleEngine()
    obj.get_path(inputfile, outputfile, fieldfile)

    obj.main_agent(1)

