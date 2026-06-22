from ctypes import *
from avasx_structures import *

# 加载avasx4eng动态连接库
libavasx = CDLL("./libavasx.so")

# 初始化MPIObject函数
InitializeMPIObject = libavasx.InitializeMPIObject
InitializeMPIObject.argtypes = [POINTER(MPIObject)]

# 打印信息函数
PrintInformations = libavasx.PrintInformations
PrintInformations.argtypes = [POINTER(MPIObject)]

# 检查是否指定GPU函数
CheckWhetherDeviceAssigned = libavasx.CheckWhetherDeviceAssigned
CheckWhetherDeviceAssigned.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
CheckWhetherDeviceAssigned.restype = POINTER(c_int)

# 设置MPI进程的GPU函数
SetDeviceForProcessors = libavasx.SetDeviceForProcessors
SetDeviceForProcessors.argtypes = [POINTER(MPIObject), POINTER(c_int)]

# 设置NCCL函数
InitializeNCCL = libavasx.InitializeNCCL
InitializeNCCL.argtypes = [POINTER(MPIObject), POINTER(NCCLObject)]

# 检查命令行参数函数
CheckCommandLineArguments = libavasx.CheckCommandLineArguments
CheckCommandLineArguments.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
CheckCommandLineArguments.restype = c_bool

# 读取Runtime配置文件函数
LoadConfigurationFiles = libavasx.LoadConfigurationFiles
LoadConfigurationFiles.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
LoadConfigurationFiles.restype = POINTER(POINTER(ConfigLineList))

LoadRunningOptions = libavasx.LoadRunningOptions
LoadRunningOptions.argtypes = [POINTER(ConfigLineList), POINTER(MPIObject)]
LoadRunningOptions.restype = POINTER(RunningOptions)

InitializeBeam = libavasx.InitializeBeam
InitializeBeam.argtypes = [POINTER(ConfigLineList), POINTER(MPIObject), POINTER(RunningOptions)]
InitializeBeam.restype = POINTER(Beam)

InitializeLatticeComponents = libavasx.InitializeLatticeComponents
InitializeLatticeComponents.argtypes = [POINTER(ConfigLineList), POINTER(RunningOptions), POINTER(MPIObject)]
InitializeLatticeComponents.restype = POINTER(Lattice)

InitializeOutputPanels = libavasx.InitializeOutputPanels
InitializeOutputPanels.argtypes = [POINTER(Lattice), POINTER(Beam), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeOutputPanels.restype = c_bool

InitializeErrorParameters = libavasx.InitializeErrorParameters
InitializeErrorParameters.argtypes = [POINTER(Lattice), POINTER(ConfigLineList), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeErrorParameters.restype = c_bool

InitializeSuperpose = libavasx.InitializeSuperpose
InitializeSuperpose.argtypes = [POINTER(Lattice), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeSuperpose.restype = c_bool

InitializeBoundary = libavasx.InitializeBoundary
InitializeBoundary.argtypes = [POINTER(Lattice), POINTER(ConfigLineList), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeBoundary.restype = c_bool

InitializePhase = libavasx.InitializePhase
InitializePhase.argtypes = [POINTER(Lattice), POINTER(Beam), POINTER(RunningOptions), POINTER(MPIObject)]
InitializePhase.restype = c_int

InitializeCUBObject = libavasx.InitializeCUBObject
InitializeCUBObject.argtypes = [POINTER(Beam), POINTER(CUBObject), POINTER(MPIObject)]
InitializeCUBObject.restype = c_bool

InitializePIC = libavasx.InitializePIC
InitializePIC.argtypes = [POINTER(PIC), POINTER(RunningOptions), POINTER(CUBObject), POINTER(MPIObject)]
InitializePIC.restype = c_bool

InitializerFFTSolver = libavasx.InitializerFFTSolver
InitializerFFTSolver.argtypes = [POINTER(FFTSolver), POINTER(PIC), POINTER(MPIObject)]
InitializerFFTSolver.restype = c_bool

InitializeBeamStatistics = libavasx.InitializeBeamStatistics
InitializeBeamStatistics.argtypes = [POINTER(BeamStatistics), POINTER(RunningOptions)]

CreateCudaStream = libavasx.CreateCudaStream
CreateCudaStream.restype = c_void_p

RunSimulationWithoutSpaceChargeEffect = libavasx.RunSimulationWithoutSpaceChargeEffect
RunSimulationWithoutSpaceChargeEffect.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(MPIObject), POINTER(c_void_p)]
RunSimulationWithoutSpaceChargeEffect.restype = c_int

RunSimulationWithSpaceChargeEffectUsingFFT = libavasx.RunSimulationWithSpaceChargeEffectUsingFFT
RunSimulationWithSpaceChargeEffectUsingFFT.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(MPIObject), POINTER(NCCLObject), POINTER(PIC), POINTER(FFTSolver), POINTER(c_void_p)]
RunSimulationWithSpaceChargeEffectUsingFFT.restype = c_int

RunSimulationWithSpaceChargeEffectUsingPICNIC = libavasx.RunSimulationWithSpaceChargeEffectUsingPICNIC
RunSimulationWithSpaceChargeEffectUsingPICNIC.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(MPIObject), POINTER(NCCLObject), POINTER(PIC), POINTER(c_void_p)]
RunSimulationWithSpaceChargeEffectUsingPICNIC.restype = c_int

OutputPhaseParticles = libavasx.OutputPhaseParticles
OutputPhaseParticles.argtypes = [POINTER(Beam), POINTER(MPIObject), POINTER(c_char)]

OutputPanelPhaseParticles_Host = libavasx.OutputPanelPhaseParticles_Host
OutputPanelPhaseParticles_Host.argtypes = [POINTER(Beam), POINTER(Lattice), POINTER(CUBObject), POINTER(RunningOptions), POINTER(MPIObject)]

DestroyNCCL = libavasx.DestroyNCCL
DestroyNCCL.argtypes = [POINTER(NCCLObject)]