import ctypes
import os

class LinacOPTEngine():
    def __init__(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
        parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
        self.dll_path = os.path.join(parent_directory, 'dllfile', 'Dll2.dll')  # 使用绝对路径连接得到完整的路径

        try:
            # 尝试加载DLL文件
            self.library = ctypes.CDLL(self.dll_path)
        except OSError as e:
            # 如果DLL文件不存在或加载出错，使用raise引发自定义的异常
            raise ValueError(f"Failed to load DLL '{self.dll_path}'. Reason: {e}")

    def Trace_win_file_change(self, str1, str2, str3, change_line_p, Number, out):
        res = self.library.Trace_win_file_change(str1, str2, str3, change_line_p, Number, out)

    def Trace_win_file(self, str1, str2, str3, str4):
        res = self.library.Trace_win_file(str1, str2, str3, str4)
        return res


    def Trace_win_beam_change(self, str1, str2, str3, change_line, out):
         res =  self.library.Trace_win_beam_change(str1, str2, str3, change_line, out)