# coding: utf-8

import sys
import os
import time
from ctypes import *
from hpc.avasx_functions import *
from hpc.avasx_structures import *


class Avasx:
    def __init__(self, runtime, beam, lattice, boundary=None):
        from mpi4py import MPI

        self.input_txt = runtime
        self.beam_txt = beam
        self.lattice_txt = lattice
        self.boundary_txt = boundary
        # MPIObject对象, 必须第一个初始化
        self.mpiObject = MPIObject()
        self.mpiObject_ptr = POINTER(MPIObject)(self.mpiObject)
        InitializeMPIObject(self.mpiObject_ptr)

        # NCCLObject读向
        self.ncclObject = NCCLObject()
        self.ncclObject_ptr = POINTER(NCCLObject)(self.ncclObject)

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
        self.configLineList = LoadConfigurationFiles(self.argc, self.argv, self.mpiObject_ptr)
        # 检查配置文件是否读取正确
        if (not self.configLineList[0]) or (not self.configLineList[1]) or (not self.configLineList[2]):
            sys.exit(0)
        # 初始化运行环境
        init_success = self.init_env()
        if not init_success:
            sys.exit(0)


    # 初始化运行环境
    def init_env(self):
        # 设置GPU
        assigned_ptr = CheckWhetherDeviceAssigned(self.argc, self.argv, self.mpiObject_ptr)
        SetDeviceForProcessors(self.mpiObject_ptr, assigned_ptr)

        # 建立NCCL通信链路
        InitializeNCCL(self.mpiObject_ptr, self.ncclObject_ptr)

        # 设置self.runningOptions_ptr
        self.runningOptions_ptr = LoadRunningOptions(self.configLineList[0], self.mpiObject_ptr)
        # rank0创建目录outputPath和err_outputPath
        if self.mpiObject.rank == 0:
            outputPath = string_at(self.runningOptions_ptr.contents.outputPath).decode()
            if not os.path.exists(outputPath):
                os.mkdir(outputPath)
            err_outputPath = os.path.join(outputPath, "output_0")
            if not os.path.exists(err_outputPath):
                os.mkdir(err_outputPath)
            # 如果存在误差分析，则修改self.runningOptions_ptr.contents.outputPath到output_0
            if self.configLineList[4]:
                self.runningOptions_ptr.contents.outputPath = err_outputPath.encode()           
            

        # 读取粒子文件
        startTime = time.time()
        self.beam_ptr = InitializeBeam(self.configLineList[1], self.mpiObject_ptr, self.runningOptions_ptr)
        if not self.beam_ptr:
            return False
        endTime = time.time()
        # 打印读取粒子信息
        self.mpiObject.infos[self.mpiObject.rank] = b"Holding %d particles of total %d, loading particles cost time = %f s."%(self.beam_ptr.contents.particles_cpu.numParticles, self.beam_ptr.contents.particles_init.numParticles, endTime-startTime)
        PrintInformations(self.mpiObject_ptr)
        
        # 初始化加速器结构
        startTime = time.time()
        self.lattice_ptr = InitializeLatticeComponents(self.configLineList[2], self.runningOptions_ptr, self.mpiObject_ptr)
        if not self.lattice_ptr:
            return False
        no_err = InitializeOutputPanels(self.lattice_ptr, self.beam_ptr, self.configLineList[3], self.mpiObject_ptr)
        if not no_err:
            return False
        no_err = InitializeErrorParameters(self.lattice_ptr, self.configLineList[4], self.configLineList[5], self.mpiObject_ptr)
        if not no_err:
            return False
        no_err = InitializeSuperpose(self.lattice_ptr, self.configLineList[6], self.mpiObject_ptr)
        if not no_err:
            return False
        no_err = InitializeBoundary(self.lattice_ptr, self.configLineList[7], self.configLineList[8], self.mpiObject_ptr)
        if not no_err:
            return False
        endTime = time.time()
        # 打印边界信息
        if self.lattice_ptr.contents.numBoundaries:
            self.mpiObject.infos[self.mpiObject.rank] = b"The number of lattice boundaries = %d, boundary length = %f m."%(self.lattice_ptr.contents.numBoundaries, self.lattice_ptr.contents.boundary_exit_z)
            PrintInformations(self.mpiObject_ptr)
        # 打印初始化加速器结构信息
        self.mpiObject.infos[self.mpiObject.rank] = b"The number of lattice components = %d, lattice length = %f m, lattice creating cost time = %f s."%(self.lattice_ptr.contents.numComponents, self.lattice_ptr.contents.lattice_exit_z, endTime-startTime)
        PrintInformations(self.mpiObject_ptr)


        # 扫相
        if self.runningOptions_ptr.contents.enableScanPhase:
            startTime = time.time()
            scanSteps = InitializePhase(self.lattice_ptr, self.beam_ptr, self.runningOptions_ptr, self.mpiObject_ptr)
            endTime = time.time()
            # 打印扫相信息
            self.mpiObject.infos[self.mpiObject.rank] = b"The number of phase scanning steps = %d, phase scanning cost time = %f s."%(scanSteps, endTime-startTime)
            PrintInformations(self.mpiObject_ptr)
        
        # 初始化CUBObject
        no_err = InitializeCUBObject(self.beam_ptr, self.cubObject_ptr, self.mpiObject_ptr)
        if not no_err:
            return False

        # 初始化PIC
        no_err = InitializePIC(self.pic_ptr, self.runningOptions_ptr, self.cubObject_ptr, self.mpiObject_ptr)
        if not no_err:
            return False

        # 初始化FFTSolver
        no_err = InitializerFFTSolver(self.fftSolver_ptr, self.pic_ptr, self.mpiObject_ptr)
        if not no_err:
            return False

        # 初始化BeamStatistics
        InitializeBeamStatistics(self.beamStatistics_ptr, self.runningOptions_ptr)

        # 创建CUDA流
        self.cuStream_ptr = (c_void_p * 2)()
        self.cuStream_ptr[0] = CreateCudaStream()
        self.cuStream_ptr[1] = CreateCudaStream()

        # 初始化成功返回True
        return True

    def run(self):
        # 打印空间电荷效应求解方法
        if self.runningOptions_ptr.contents.spaceChargeMethod == 0:
            self.mpiObject.infos[self.mpiObject.rank] = b"Using FFT as a PIC solver."
        else:
            self.mpiObject.infos[self.mpiObject.rank] = b"Using PICNIC as a PIC solver."
        PrintInformations(self.mpiObject_ptr)

        # 运行仿真
        startTime = time.time()
        numSteps = 0
        if self.runningOptions_ptr.contents.enableSpaceCharge:
            if self.runningOptions_ptr.contents.spaceChargeMethod == FFT:
                numSteps = RunSimulationWithSpaceChargeEffectUsingFFT(self.runningOptions_ptr, self.lattice_ptr, self.beam_ptr, self.beamStatistics_ptr, self.cubObject_ptr, self.mpiObject_ptr, self.ncclObject_ptr, self.pic_ptr, self.fftSolver_ptr, self.cuStream_ptr)
            else:
                numSteps = RunSimulationWithSpaceChargeEffectUsingPICNIC(self.runningOptions_ptr, self.lattice_ptr, self.beam_ptr, self.beamStatistics_ptr, self.cubObject_ptr, self.mpiObject_ptr, self.ncclObject_ptr, self.pic_ptr, self.cuStream_ptr)
        else:
            numSteps = RunSimulationWithoutSpaceChargeEffect(self.runningOptions_ptr, self.lattice_ptr, self.beam_ptr, self.beamStatistics_ptr, self.cubObject_ptr, self.mpiObject_ptr, self.cuStream_ptr)
        MPI.COMM_WORLD.Barrier()
        endTime = time.time()
        if self.mpiObject.rank == 0:
            print()
        self.mpiObject.infos[self.mpiObject.rank] = b"Pushing steps = %d, total cost time = %f s."%(numSteps, endTime-startTime)
        PrintInformations(self.mpiObject_ptr)

        #输出结果
        if self.beam_ptr.contents.dst_or_edst == EDST:
            output_path = os.path.join(string_at(self.runningOptions_ptr.contents.outputPath).decode(), "outData_%f.edst"%(self.lattice_ptr.contents.lattice_exit_z))
            OutputPhaseParticles(self.beam_ptr, self.mpiObject_ptr, output_path.encode())
        else:
            output_path = os.path.join(string_at(self.runningOptions_ptr.contents.outputPath).decode(), "outData_%f.dst"%(self.lattice_ptr.contents.lattice_exit_z))
            OutputPhaseParticles(self.beam_ptr, self.mpiObject_ptr, output_path.encode())
        OutputPanelPhaseParticles_Host(self.beam_ptr, self.lattice_ptr, self.cubObject_ptr, self.runningOptions_ptr, self.mpiObject_ptr)


    def release(self):
        DestroyNCCL(self.ncclObject)
        sys.exit(0)


# avasx = Avasx("/root/AVASX/Bend/A5/input.txt", "/root/AVASX/Bend/A5/beam.txt", "/root/AVASX/Bend/A5/lattice_mulp.txt", "/root/AVASX/Bend/A5/boundary.txt")
# avasx.run()
#avasx.release()

 