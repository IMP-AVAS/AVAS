import sys
import os
from ctypes import *
from sim_gpu.structures import *
from sim_gpu.initializer import *
from sim_gpu.run import *
import time

class MPIContext:
    try :
        def __init__(self):
            from mpi4py import MPI  # 延迟导入，确保只有在需要时才触发
            self.comm = MPI.COMM_WORLD
            self.rank = self.comm.Get_rank()
            self.comm_size = self.comm.Get_size()
            self.mpi_obj = None
            self.mpi_ptr = None
            self._setup_mpi_obj()
        def _setup_mpi_obj(self):
            self.mpi_obj = MPIObject()
            self.mpi_obj.commSize = self.comm_size
            self.mpi_obj.rank = self.rank
            self.mpi_ptr = pointer(self.mpi_obj)
            SetDeviceForProcessors(self.mpi_ptr, c_int(-1))
            print(f"[MPI] Init success - rank={self.rank}, size={self.comm_size}")
    except Exception as e:
        print("[MPI] 初始化失败:", e)
        import traceback
        traceback.print_exc()
        self.comm = None
        self.rank = 0
        self.comm_size = 1
        self.mpi_obj = None


class CUB:
    def __init__(self, beam_ptr, mpi_handler):
        self.cub_obj = CUBObject()
        InitializeCUB(beam_ptr, pointer(self.cub_obj), pointer(mpi_handler.mpi_obj))


class PICHandler:
    def __init__(self, running_options, cub_handler, mpi_handler):
        self.pic = PIC()
        InitializePIC(pointer(self.pic), running_options,
                      pointer(cub_handler.cub_obj), pointer(mpi_handler.mpi_obj))


class Statistics:
    def __init__(self, running_options):
        self.statistics = BeamStatistics()
        InitializeBeamStatistics(pointer(self.statistics), running_options)


class FFT:
    def __init__(self, pic_handler, mpi_handler):
        self.fft_solver = FFTSolver()
        InitializerFFT(pointer(self.fft_solver), pointer(pic_handler.pic), pointer(mpi_handler.mpi_obj))


class Beam:
    def __init__(self, config_path, mpi_handler, lattice_ptr, running_options):
        self.beam_ptr = InitializeBeam(config_path, pointer(mpi_handler.mpi_obj),
                                       lattice_ptr, running_options)


class SimulationRunner:
    def __init__(self, item):
        self.project_path = item["project_path"]
        self.input_file = item.get("input_file")
        self.input_txt = item["input_path"]
        self.beam_txt = item["beam_path"]
        self.lattice_txt = item["lattice_path"]

        print(57, self.input_txt, self.beam_txt, self.lattice_txt)

        self.mpi_handler = MPIContext()
        self.configs = self._read_configs()
        self.running_options = LoadRunningOptions(self.configs[0])
        # 创建输出目录
        self.output_path = (self.running_options[0].outputPath).decode()
        if not os.path.isdir(self.output_path):
            os.mkdir(self.output_path)
        if not os.path.isdir(os.path.join(self.output_path, "output_0")):
            os.mkdir(os.path.join(self.output_path, "output_0"))
        # 如果存在误差分析则修改输出目录
        if self.configs[4]:
            self.running_options[0].outputPath = (os.path.join(self.output_path, "output_0")).encode()
            self.output_path = os.path.join(self.output_path, "output_0")
        self._initialize_components()
        self._setup_streams()

    # def _check_args(self, argv):
    #     argc = len(argv)
    #     c_argv = (c_char_p * argc)()
    #     for i in range(argc):
    #         c_argv[i] = argv[i].encode()
    #     if not CheckCommandLineArguments(c_int(argc), c_argv):
    #         exit()

    def _read_configs(self):
        # 动态生成配置参数
        config_args = [
            "avas",
            f"common={self.input_txt}",
            f"beam={self.beam_txt}",
            f"lattice={self.lattice_txt}"
        ]
        # print(config_args)
        argc = len(config_args)
        argv_c = (c_char_p * argc)()
        for i, arg in enumerate(config_args):
            argv_c[i] = arg.encode()
        return ReadConfigurations(c_int(argc), argv_c)

    def _initialize_components(self):
        # 初始化晶格
        self.lattice_ptr = InitializeLatticeComponents(self.configs[2], self.running_options)
        if not self.lattice_ptr:
            sys.exit("Failed to initialize lattice components")
        print(
            f"rank={self.mpi_handler.rank}: components={self.lattice_ptr[0].numComponents}, length={self.lattice_ptr[0].latticeLength}")

        # 设置误差项
        InitializeErrorParameters(self.lattice_ptr, self.configs[4], self.configs[5])
        if not InitializeSuperpose(self.lattice_ptr, self.configs[6]):
            sys.exit("Failed to initialize superpose")

        # 初始化束流
        self.beam_handler = Beam(self.configs[1], self.mpi_handler,
                                 self.lattice_ptr, self.running_options)
        print(
            f"rank={self.mpi_handler.rank}: holding {self.beam_handler.beam_ptr[0].particles_gpu.numParticles} of {self.beam_handler.beam_ptr[0].particles_init.numParticles}")

        # 初始化CUB
        self.cub_handler = CUB(self.beam_handler.beam_ptr, self.mpi_handler)

        # 初始化PIC
        self.pic_handler = PICHandler(self.running_options, self.cub_handler, self.mpi_handler)

        # 初始化BeamStatistics
        self.beamStatistics = Statistics(self.running_options)

        # 初始化FFT
        self.fft_handler = FFT(self.pic_handler, self.mpi_handler)

        # 初始化输出
        self.output_obj = OutputObject()
        InitializeOutputObject(self.configs[3], self.running_options,
                               self.beam_handler.beam_ptr, self.lattice_ptr,
                               pointer(self.output_obj))

    def _setup_streams(self):
        self.cu_stream = (c_void_p * 2)()
        self.cu_stream[0] = CreateCudaStream()
        self.cu_stream[1] = CreateCudaStream()

    def run(self):
        start_time = time.time()
        InitializePhase(self.lattice_ptr, self.beam_handler.beam_ptr,
                        self.running_options, pointer(self.mpi_handler.mpi_obj))

        if self.running_options[0].spaceChargeFlag:
            if self.running_options[0].spaceChargeMethod == 0:
                itr_cnt = RunSimulationWithSpaceChargeUsingFFT(
                    self.running_options,
                    self.lattice_ptr,
                    self.beam_handler.beam_ptr,
                    pointer(self.beamStatistics.statistics),
                    pointer(self.cub_handler.cub_obj),
                    pointer(self.mpi_handler.mpi_obj),
                    pointer(self.pic_handler.pic),
                    pointer(self.fft_handler.fft_solver),
                    pointer(self.output_obj),
                    self.cu_stream
                )
            else:
                itr_cnt = RunSimulationWithSpaceChargeUsingPICNIC(
                    self.running_options,
                    self.lattice_ptr,
                    self.beam_handler.beam_ptr,
                    pointer(self.beamStatistics.statistics),
                    pointer(self.cub_handler.cub_obj),
                    pointer(self.mpi_handler.mpi_obj),
                    pointer(self.pic_handler.pic),
                    pointer(self.output_obj),
                    self.cu_stream
                )
        else:
            itr_cnt = RunSimulationWithoutSpaceCharge(
                self.running_options,
                self.lattice_ptr,
                self.beam_handler.beam_ptr,
                pointer(self.beamStatistics.statistics),
                pointer(self.cub_handler.cub_obj),
                pointer(self.mpi_handler.mpi_obj),
                pointer(self.output_obj),
                self.cu_stream
            )

        print(f"rank={self.mpi_handler.rank}: steps={itr_cnt}, time={time.time() - start_time:.2f}s")
        # OutputRealParticles(self.beam_handler.beam_ptr,
        #                     pointer(self.mpi_handler.mpi_obj), b"real.dat")
        outDataPath = os.path.join(self.output_path, "outData_%f.dst" % self.lattice_ptr[0].latticeLength)
        OutputPhaseParticles(self.beam_handler.beam_ptr, pointer(self.mpi_handler.mpi_obj), outDataPath.encode())

        # 释放内存
        ReleaseBeamStatistics(pointer(self.beamStatistics.statistics))
        ReleaseOutputObject(self.running_options, pointer(self.output_obj))
        ReleaseLatticeComponents(self.lattice_ptr)
        ReleaseBeam(self.beam_handler.beam_ptr)
        ReleasePIC(pointer(self.pic_handler.pic))
        ReleaseCUBObject(pointer(self.cub_handler.cub_obj))
        ReleaseMPIObject(pointer(self.mpi_handler.mpi_obj))
        ReleaseFFTSolver(pointer(self.fft_handler.fft_solver))
        ReleaseConfigurations(self.configs)

        cudaDeviceReset()
#        MPI_Finalize()

if __name__ == "__main__":
    project_path = r"/root/GAVAS/"
    item = {
        "project_path": project_path
    }
    
    simulator = SimulationRunner(item)
    simulator.run()
