from ctypes import *
from structures import *
import os

script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径

libpicso_path = os.path.join(parent_directory, 'dllfile', "libPIC.so")  # 使用绝对路径连接得到完整的路径

# print(10, libpicso_path)
# print(11, os.path.exists(libpicso_path))
# 打开动态链接库
libPIC = CDLL(r"C:\Users\shliu\Desktop\AVAS\AVAS\dllfile\libPIC.so")

# 设置命令行检查函数
CheckCommandLineArguments = libPIC.CheckCommandLineArguments
CheckCommandLineArguments.argtypes = [c_int, POINTER(c_char_p)]
CheckCommandLineArguments.restype = c_bool

# 指定MPI设备函数
SetDeviceForProcessors = libPIC.SetDeviceForProcessors
SetDeviceForProcessors.argtypes = [POINTER(MPIObject)]

# 读取配置文件函数
ReadConfigurations = libPIC.ReadConfigurations
ReadConfigurations.argtypes = [c_int, POINTER(c_char_p)]
ReadConfigurations.restype = POINTER(POINTER(Configurations))

# 初始化运行参数函数
LoadRunningOptions = libPIC.LoadRunningOptions
LoadRunningOptions.argtypes = [POINTER(Configurations)]
LoadRunningOptions.restype = POINTER(RunningOptions)

# 初始化加速器函数
InitializeLatticeComponents = libPIC.InitializeLatticeComponents
InitializeLatticeComponents.argtypes = [POINTER(Configurations), POINTER(RunningOptions)]
InitializeLatticeComponents.restype = POINTER(Lattice)

# 设置误差项
InitializeErrorParameters = libPIC.InitializeErrorParameters
InitializeErrorParameters.argtypes = [POINTER(Lattice), POINTER(Configurations), POINTER(Configurations)]

# 设置叠加长
InitializeSuperpose = libPIC.InitializeSuperpose
InitializeSuperpose.argtypes = [POINTER(Lattice), POINTER(Configurations)]
InitializeSuperpose.restype = c_bool


# 初始化束流函数
InitializeBeam = libPIC.InitializeBeam
InitializeBeam.argtypes = [POINTER(Configurations), POINTER(MPIObject), POINTER(Lattice), POINTER(RunningOptions)]
InitializeBeam.restype = POINTER(Beam)

# 初始化统计束流结构体
InitializeBeamStatistics = libPIC.InitializeBeamStatistics
InitializeBeamStatistics.argtypes = [POINTER(BeamStatistics), POINTER(RunningOptions)]

# 初始化CUB函数
InitializeCUB = libPIC.InitializeCUB

InitializeCUB.argtypes = [POINTER(Beam), POINTER(CUBObject), POINTER(MPIObject)]

# 初始化PIC函数
InitializePIC = libPIC.InitializePIC
InitializePIC.argtypes = [POINTER(PIC), POINTER(RunningOptions), POINTER(CUBObject), POINTER(MPIObject)]

# 初始化FFT函数
InitializerFFT = libPIC.InitializerFFT
InitializerFFT.argtypes = [POINTER(FFTSolver), POINTER(PIC), POINTER(MPIObject)]

# 初始化输出数据结构体
InitializeOutputObject = libPIC.InitializeOutputObject
InitializeOutputObject.argtypes = [POINTER(Configurations), POINTER(RunningOptions), POINTER(Beam), POINTER(Lattice), POINTER(OutputObject)]

# 初始化扫相函数
InitializePhase = libPIC.InitializePhase
InitializePhase.argtypes = [POINTER(Lattice), POINTER(Beam), POINTER(RunningOptions), POINTER(MPIObject)]
InitializePhase.restype = c_int
# 创建CUDA流函数
CreateCudaStream = libPIC.CreateCudaStream
CreateCudaStream.restype = c_void_p
