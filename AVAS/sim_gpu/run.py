from ctypes import *
from sim_gpu.structures import *
import os

script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径

libpicso_path = os.path.join(parent_directory, 'dllfile', "libPIC.so")  # 使用绝对路径连接得到完整的路径


# 打开动态链接库
libPIC = CDLL(libpicso_path)
libCudaRT = CDLL("libcudart.so")
libMPI = CDLL("libmpi.so")



# 推进函数_FFT
RunSimulationWithSpaceChargeUsingFFT = libPIC.RunSimulationWithSpaceChargeUsingFFT
RunSimulationWithSpaceChargeUsingFFT.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(MPIObject), POINTER(PIC), POINTER(FFTSolver), POINTER(OutputObject), c_void_p]
RunSimulationWithSpaceChargeUsingFFT.restype = c_int

# 推进函数_PICNIC
RunSimulationWithSpaceChargeUsingPICNIC = libPIC.RunSimulationWithSpaceChargeUsingPICNIC
RunSimulationWithSpaceChargeUsingPICNIC.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(MPIObject), POINTER(PIC), POINTER(OutputObject), c_void_p]
RunSimulationWithSpaceChargeUsingPICNIC.restype = c_int

RunSimulationWithoutSpaceCharge = libPIC.RunSimulationWithoutSpaceCharge
RunSimulationWithoutSpaceCharge.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(MPIObject), POINTER(OutputObject), c_void_p]
RunSimulationWithoutSpaceCharge.restype = c_int

# 输出运行时长和迭代步数
OutputRealParticles = libPIC.OutputRealParticles
OutputPhaseParticles = libPIC.OutputPhaseParticles
OutputRealParticles.argtypes = [POINTER(Beam), POINTER(MPIObject), c_void_p]
OutputPhaseParticles.argtypes = [POINTER(Beam), POINTER(MPIObject), c_void_p]

# 释放内存
ReleaseBeamStatistics = libPIC.ReleaseBeamStatistics
ReleaseOutputObject = libPIC.ReleaseOutputObject
ReleaseLatticeComponents = libPIC.ReleaseLatticeComponents
ReleaseBeam = libPIC.ReleaseBeam
ReleasePIC = libPIC.ReleasePIC
ReleaseCUBObject = libPIC.ReleaseCUBObject
ReleaseMPIObject = libPIC.ReleaseMPIObject
ReleaseFFTSolver = libPIC.ReleaseFFTSolver
ReleaseConfigurations = libPIC.ReleaseConfigurations
ReleaseBeamStatistics.argtypes = [POINTER(BeamStatistics)]
ReleaseOutputObject.argtypes = [POINTER(RunningOptions), POINTER(OutputObject)]
ReleaseLatticeComponents.argtypes = [POINTER(Lattice)]
ReleaseBeam.argtypes = [POINTER(Beam)]
ReleasePIC.argtypes = [POINTER(PIC)]
ReleaseCUBObject.argtypes = [POINTER(CUBObject)]
ReleaseMPIObject.argtypes = [POINTER(MPIObject)]
ReleaseFFTSolver.argtypes = [POINTER(FFTSolver)]
ReleaseConfigurations.argtypes = [POINTER(POINTER(Configurations))]

# 重置GPU
cudaDeviceReset = libCudaRT.cudaDeviceReset
#cudaDeviceReset.restype = [c_int]

MPI_Finalize = libMPI.MPI_Finalize
