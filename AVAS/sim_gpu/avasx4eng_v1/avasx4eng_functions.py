from ctypes import *
from avasx4eng_structures import *

# 加载avasx4eng动态连接库
libavasx4eng = CDLL("./libavasx4eng.so")

# 初始化MPIObject函数
InitializeMPIObject = libavasx4eng.InitializeMPIObject
InitializeMPIObject.argtypes = [POINTER(MPIObject)]

# 打印信息函数
PrintInformations = libavasx4eng.PrintInformations
PrintInformations.argtypes = [POINTER(MPIObject)]

# 检查是否指定GPU函数
CheckWhetherDeviceAssigned = libavasx4eng.CheckWhetherDeviceAssigned
CheckWhetherDeviceAssigned.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
CheckWhetherDeviceAssigned.restype = POINTER(c_int)

# 设置MPI进程的GPU函数
SetDeviceForProcessors = libavasx4eng.SetDeviceForProcessors
SetDeviceForProcessors.argtypes = [POINTER(MPIObject), POINTER(c_int)]

# 检查命令行参数函数
CheckCommandLineArguments = libavasx4eng.CheckCommandLineArguments
CheckCommandLineArguments.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
CheckCommandLineArguments.restype = c_bool

# 读取Runtime配置文件函数
LoadRuntimeConfigFile = libavasx4eng.LoadRuntimeConfigFile
LoadRuntimeConfigFile.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
LoadRuntimeConfigFile.restype = POINTER(ConfigLineList)

# 读取Beam配置文件函数
LoadBeamConfigFile = libavasx4eng.LoadBeamConfigFile
LoadBeamConfigFile.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
LoadBeamConfigFile.restype = POINTER(ConfigLineList)

# 读取Lattice配置文件函数
LoadLatticeConfigFiles = libavasx4eng.LoadLatticeConfigFiles
LoadLatticeConfigFiles.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
LoadLatticeConfigFiles.restype = POINTER(LatticeConfigFileList)

# 读取boundary配置文件函数
LoadBoundaryConfigFile = libavasx4eng.LoadBoundaryConfigFile
LoadBoundaryConfigFile.argtypes = [c_int, POINTER(c_char_p), POINTER(MPIObject)]
LoadBoundaryConfigFile.restype = POINTER(POINTER(ConfigLineList))

LoadRunningOptions = libavasx4eng.LoadRunningOptions
LoadRunningOptions.argtypes = [POINTER(ConfigLineList), POINTER(MPIObject)]
LoadRunningOptions.restype = POINTER(RunningOptions)

InitializeBeam = libavasx4eng.InitializeBeam
InitializeBeam.argtypes = [POINTER(ConfigLineList), POINTER(RunningOptions), POINTER(MPIObject)]
InitializeBeam.restype = POINTER(Beam)

InitializeLatticeComponents = libavasx4eng.InitializeLatticeComponents
InitializeLatticeComponents.argtypes = [POINTER(ConfigLineList), POINTER(RunningOptions), POINTER(MPIObject)]
InitializeLatticeComponents.restype = POINTER(Lattice)

InitializeSuperpose = libavasx4eng.InitializeSuperpose
InitializeSuperpose.argtypes = [POINTER(Lattice), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeSuperpose.restype = c_bool

InitializeBoundary = libavasx4eng.InitializeBoundary
InitializeBoundary.argtypes = [POINTER(Lattice), POINTER(ConfigLineList), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeBoundary.restype = c_bool

CheckLatticeComponentsAndBoundaries = libavasx4eng.CheckLatticeComponentsAndBoundaries
CheckLatticeComponentsAndBoundaries.argtypes = [POINTER(Lattice), POINTER(MPIObject)]
CheckLatticeComponentsAndBoundaries.restype = c_bool

InitializePhase = libavasx4eng.InitializePhase
InitializePhase.argtypes = [POINTER(Lattice), POINTER(Beam), POINTER(RunningOptions), POINTER(MPIObject)]
InitializePhase.restype = c_int

InitializeCUBObject = libavasx4eng.InitializeCUBObject
InitializeCUBObject.argtypes = [POINTER(Beam), POINTER(CUBObject), POINTER(MPIObject)]
InitializeCUBObject.restype = c_bool

InitializePIC = libavasx4eng.InitializePIC
InitializePIC.argtypes = [POINTER(PIC), POINTER(RunningOptions), POINTER(CUBObject), POINTER(MPIObject)]
InitializePIC.restype = c_bool

InitializerFFTSolver = libavasx4eng.InitializerFFTSolver
InitializerFFTSolver.argtypes = [POINTER(FFTSolver), POINTER(PIC), POINTER(MPIObject)]
InitializerFFTSolver.restype = c_bool

InitializeBeamStatistics = libavasx4eng.InitializeBeamStatistics
InitializeBeamStatistics.argtypes = [POINTER(BeamStatistics), POINTER(RunningOptions)]

CreateCudaStream = libavasx4eng.CreateCudaStream
CreateCudaStream.restype = c_void_p

ResetErrorParameters = libavasx4eng.ResetErrorParameters
ResetErrorParameters.argtypes = [POINTER(Lattice)]

InitializeErrorParameters = libavasx4eng.InitializeErrorParameters
InitializeErrorParameters.argtypes = [POINTER(Lattice), POINTER(ConfigLineList), POINTER(ConfigLineList), POINTER(MPIObject)]
InitializeErrorParameters.restype = c_bool

ResetOutputPanels = libavasx4eng.ResetOutputPanels
ResetOutputPanels.argtypes = [POINTER(Lattice), POINTER(Beam), POINTER(ConfigLineList)]

ResetBeam = libavasx4eng.ResetBeam
ResetBeam.argtypes = [POINTER(Beam)]

RunSimulationWithoutSpaceChargeEffect = libavasx4eng.RunSimulationWithoutSpaceChargeEffect
RunSimulationWithoutSpaceChargeEffect.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(c_void_p)]
RunSimulationWithoutSpaceChargeEffect.restype = c_int

RunSimulationWithSpaceChargeEffectUsingFFT = libavasx4eng.RunSimulationWithSpaceChargeEffectUsingFFT
RunSimulationWithSpaceChargeEffectUsingFFT.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(PIC), POINTER(FFTSolver), POINTER(c_void_p)]
RunSimulationWithSpaceChargeEffectUsingFFT.restype = c_int

RunSimulationWithSpaceChargeEffectUsingPICNIC = libavasx4eng.RunSimulationWithSpaceChargeEffectUsingPICNIC
RunSimulationWithSpaceChargeEffectUsingPICNIC.argtypes = [POINTER(RunningOptions), POINTER(Lattice), POINTER(Beam), POINTER(BeamStatistics), POINTER(CUBObject), POINTER(PIC), POINTER(c_void_p)]
RunSimulationWithSpaceChargeEffectUsingPICNIC.restype = c_int
