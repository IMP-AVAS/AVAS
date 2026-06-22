from ctypes import *
from avasx4eng_functions import *
from avasx4eng_structures import *
from mpi4py import MPI
import sys
import os
import time

class Avasx4Eng:
    def __init__(self, runtime, beam, lattice, boundary=None):
        # MPIObject对象
        self.mpiObject = MPIObject()
        self.mpiObject_ptr = POINTER(MPIObject)(self.mpiObject)
        InitializeMPIObject(self.mpiObject_ptr)
        self.message_buffer_ptr = self.mpiObject.infos[self.mpiObject.rank]

        # CUBObject对象
        self.cubObject = CUBObject()
        self.cubObject_ptr = POINTER(CUBObject)(self.cubObject)

        # FFTSolver对象
        self.fftSolver = FFTSolver()
        self.fftSolver_ptr = POINTER(FFTSolver)(self.fftSolver)

        # PIC对象
        self.pic = PIC()
        self.pic_ptr = POINTER(PIC)(self.pic)

        # BeamStatistics对象
        self.beamStatistics = BeamStatistics()
        self.beamStatistics_ptr = POINTER(BeamStatistics)(self.beamStatistics)

        # 取得命令行参数
        config_args_with_boundary = [
            "avas",
            f"runtime={runtime}",
            f"beam={beam}",
            f"lattice={lattice}",
            f"boundary={boundary}"
        ]
        config_args_without_boundary = [
            "avas",
            f"runtime={runtime}",
            f"beam={beam}",
            f"lattice={lattice}"
        ]

        args = config_args_with_boundary if boundary is not None else config_args_without_boundary
        self.argc = len(args)
        self.argv = (c_char_p * self.argc)()
        for i in range(self.argc):
            self.argv[i] = args[i].encode()
        # 检查命令行参数是否正确
        if not CheckCommandLineArguments(self.argc, self.argv, self.mpiObject_ptr):
            sys.exit(0)
        
        # 读取命令行参数指定的配置文件
        startTime = time.time()
        self.runtimeConfigList_ptr = LoadRuntimeConfigFile(self.argc, self.argv, self.mpiObject_ptr)
        self.beamConfigList_ptr = LoadBeamConfigFile(self.argc, self.argv, self.mpiObject_ptr)
        self.latticeConfigFileList_ptr = LoadLatticeConfigFiles(self.argc, self.argv, self.mpiObject_ptr)
        self.boundaryConfigList_ptr = LoadBoundaryConfigFile(self.argc, self.argv, self.mpiObject_ptr)
        # 检查配置文件是否读取正确
        if (not self.runtimeConfigList_ptr) or (not self.beamConfigList_ptr) or (not self.latticeConfigFileList_ptr):
            sys.exit(0)
        endTime = time.time()
        # 打印读取配置文件信息
        info = b"The number of responsible lattices = %d, file loading cost time = %f s."%(self.mpiObject.numTasks, endTime-startTime)
        info = create_string_buffer(info)
        memmove(self.message_buffer_ptr, info, len(info))
        PrintInformations(self.mpiObject_ptr)
        # 初始化运行环境
        self.init_env()

    # 初始化运行环境
    def init_env(self):
        # 设置GPU
        assigned_ptr = CheckWhetherDeviceAssigned(self.argc, self.argv, self.mpiObject_ptr)
        SetDeviceForProcessors(self.mpiObject_ptr, assigned_ptr)

        # 设置self.runningOptions_ptr
        self.runningOptions_ptr = LoadRunningOptions(self.runtimeConfigList_ptr, self.mpiObject_ptr)
        # rank0创建目录
        if self.mpiObject.rank == 0:
            outputPath = string_at(self.runningOptions_ptr.contents.outputPath).decode()
            if not os.path.exists(outputPath):
                os.mkdir(outputPath)

        # 读取粒子文件
        startTime = time.time()
        self.beam_ptr = InitializeBeam(self.beamConfigList_ptr, self.runningOptions_ptr, self.mpiObject_ptr)
        if not self.beam_ptr:
            return False
        endTime = time.time()
        # 打印读取粒子信息
        info = b"The number of simulated particles = %d, beam loading cost time = %f s."%(self.beam_ptr.contents.particles_init_cpu.numParticles, endTime-startTime)
        info = create_string_buffer(info)
        memmove(self.message_buffer_ptr, info, len(info))
        PrintInformations(self.mpiObject_ptr)
        
        #初始化加速器结构
        startTime = time.time()
        self.lattice_ptr = InitializeLatticeComponents(self.latticeConfigFileList_ptr.contents.componentList, self.runningOptions_ptr, self.mpiObject_ptr)
        if not self.lattice_ptr:
            return False
        info = b"Using File \"%s\" to initialize a lattice."%(self.latticeConfigFileList_ptr.contents.fileName)
        info = create_string_buffer(info)
        memmove(self.message_buffer_ptr, info, len(info))
        PrintInformations(self.mpiObject_ptr)

        # 设置叠加场
        no_err = InitializeSuperpose(self.lattice_ptr, self.latticeConfigFileList_ptr.contents.superposeCommandList, self.mpiObject_ptr)
        if not no_err:
            sys.exit(0)

        # 设置边界
        no_err = InitializeBoundary(self.lattice_ptr, self.boundaryConfigList_ptr[0], self.boundaryConfigList_ptr[1], self.mpiObject)
        if not no_err:
            sys.exit(0)
        endTime = time.time()

        # 打印初始化加速器结构信息
        info = b"The number of lattice components = %d, lattice length = %f m, lattice creating cost time = %f s."%(self.lattice_ptr.contents.numComponents, self.lattice_ptr.contents.lattice_exit_z, endTime-startTime)
        info = create_string_buffer(info)
        memmove(self.message_buffer_ptr, info, len(info))
        PrintInformations(self.mpiObject_ptr)

        # 打印边界结构信息
        info = b"The number of lattice boundaries = %d, boundary length = %f m."%(self.lattice_ptr.contents.numBoundaries, self.lattice_ptr.contents.boundary_exit_z)
        info = create_string_buffer(info)
        memmove(self.message_buffer_ptr, info, len(info))
        PrintInformations(self.mpiObject_ptr)

        # 检查边界是否与lattice匹配
        no_err = CheckLatticeComponentsAndBoundaries(self.lattice_ptr, self.mpiObject_ptr)
        if not no_err:
            sys.exit(0)


        # 扫相
        if self.runningOptions_ptr.contents.enableScanPhase:
            startTime = time.time()
            scanSteps = InitializePhase(self.lattice_ptr, self.beam_ptr, self.runningOptions_ptr, self.mpiObject_ptr)
            endTime = time.time()
            # 打印扫相信息
            info = b"The number of phase scanning steps = %d, phase scanning cost time = %f s."%(scanSteps, endTime-startTime)
            info = create_string_buffer(info)
            memmove(self.message_buffer_ptr, info, len(info))
            PrintInformations(self.mpiObject_ptr)
        
        # 初始化CUBObject
        no_err = InitializeCUBObject(self.beam_ptr, self.cubObject_ptr, self.mpiObject_ptr)
        if not no_err:
            sys.exit(0)

        # 初始化PIC
        no_err = InitializePIC(self.pic_ptr, self.runningOptions_ptr, self.cubObject_ptr, self.mpiObject_ptr)
        if not no_err:
            sys.exit(0)

        # 初始化FFTSolver
        no_err = InitializerFFTSolver(self.fftSolver_ptr, self.pic_ptr, self.mpiObject_ptr)
        if not no_err:
            sys.exit(0)

        # 初始化BeamStatistics
        InitializeBeamStatistics(self.beamStatistics_ptr, self.runningOptions_ptr)

        # 创建CUDA流
        self.cuStream_ptr = (c_void_p * 2)()
        self.cuStream_ptr[0] = CreateCudaStream()
        self.cuStream_ptr[1] = CreateCudaStream()

    def run(self):
        # 找到每个MPI进程对应要处理的第一个任务
        node_ptr = self.latticeConfigFileList_ptr
        for i in range(self.mpiObject.rank * self.mpiObject.avgTasks):
            node_ptr = node_ptr.contents.next

        if self.runningOptions_ptr.contents.spaceChargeMethod == 0:
            info = b"Using FFT as a PIC solver."
            info = create_string_buffer(info)
            memmove(self.message_buffer_ptr, info, len(info))
            PrintInformations(self.mpiObject_ptr)
        else:
            info = b"Using PICNIC as a PIC solver."
            info = create_string_buffer(info)
            memmove(self.message_buffer_ptr, info, len(info))
            PrintInformations(self.mpiObject_ptr)
        
        startTime = time.time()
        for i in range(self.mpiObject.numTasks):
            # 设置lattice中的fileName指向node中的fileName
            self.lattice_ptr.contents.fileName = create_string_buffer(node_ptr.contents.fileName)
            # 重置lattice中的enableErrorAnalysis等于0
            ResetErrorParameters(self.lattice_ptr)
            # 重新设置误差
            no_err = InitializeErrorParameters(self.lattice_ptr, node_ptr.contents.errorSwitchList, node_ptr.contents.errorCommandList, self.mpiObject_ptr)
            if not no_err:
                sys.exit(0)
            # 重新设置outputPanels
            ResetOutputPanels(self.lattice_ptr, self.beam_ptr, node_ptr.contents.outputPanelList)
            # 重置beam
            ResetBeam(self.beam_ptr)
            # 启动仿真
            if not self.runningOptions_ptr.contents.enableSpaceCharge:
                RunSimulationWithoutSpaceChargeEffect(self.runningOptions_ptr, self.lattice_ptr, self.beam_ptr, self.beamStatistics_ptr, self.cubObject_ptr, self.cuStream_ptr)
            else:
                if self.runningOptions_ptr.contents.spaceChargeMethod == 0:
                    RunSimulationWithSpaceChargeEffectUsingFFT(self.runningOptions_ptr, self.lattice_ptr, self.beam_ptr, self.beamStatistics_ptr, self.cubObject_ptr, self.pic_ptr, self.fftSolver_ptr, self.cuStream_ptr)
                else:
                    RunSimulationWithSpaceChargeEffectUsingPICNIC(self.runningOptions_ptr, self.lattice_ptr, self.beam_ptr, self.beamStatistics_ptr, self.cubObject_ptr, self.pic_ptr, self.cuStream_ptr)
            node_ptr = node_ptr.contents.next
        endTime = time.time()
        info = b"Total cost time = %f s."%(endTime-startTime)
        info = create_string_buffer(info)
        memmove(self.message_buffer_ptr, info, len(info))
        PrintInformations(self.mpiObject_ptr)


        

#avasx4eng = Avasx4Eng()
#avasx4eng.run()
 
