from ctypes import *

BUFFERSIZE = 256


# 定义double3结构体
class double3(Structure):
    _fields_ = [
        ("x", c_double),
        ("y", c_double),
        ("z", c_double)
    ]


# 定义float6结构体
class float6(Structure):
    _align_ = 32
    _fields_ = [
        ("bx", c_float),
        ("by", c_float),
        ("bz", c_float),
        ("ex", c_float),
        ("ey", c_float),
        ("ez", c_float)
    ]


# 定义读取配置文件的结构体
class Configurations(Structure):
    _fields_ = [
        ("buffer", c_char * BUFFERSIZE),
        ("componentIdx", c_int),
        ("lineIdx", c_int),
        ("next", c_void_p)
    ]


# 定义保存运行参数的结构体
class RunningOptions(Structure):
    _fields_ = [
        ("spaceChargeFlag", c_bool),
        ("usingAggregation", c_bool),
        ("histogramFlag", c_bool),
        ("numGridofPIC", c_int * 3),
        ("arrangeSequenceInterval", c_int),
        ("blockGroupSize", c_int),
        ("numPCHistogram", c_int),
        ("spaceChargeMethod", c_int),
        ("dumpPeriodicity", c_int),
        ("statOutputInterval", c_int),
        ("numBufferPool", c_int),
        ("bufferoolSize", c_int),
        ("numSamplingCoef", c_float),
        ("stepPerCycle", c_double),
        ("scanAngleStep", c_double),
        ("rmsSize", c_double * 3),
        ("fieldPath", c_char * BUFFERSIZE),
        ("outputPath", c_char * BUFFERSIZE),
        ("beamPath", c_char * BUFFERSIZE)
    ]


# 定义MPI对象结构体
class MPIObject(Structure):
    _fields_ = [
        ("rank", c_int),
        ("commSize", c_int),
        ("devIdx", c_int),
        ("avgNumParticles", c_int),
        ("phaseFlag", c_int),
        ("numNormalParticles", c_int),
        ("numReducedInside", c_int),
        ("numNotMissedParticles", c_int),
        ("numNoneZeroGrid", c_void_p),
        ("sendNoneZeroGridCharge", c_void_p),
        ("recvNoneZeroGridCharge", c_void_p),
        ("sendNoneZeroGridIndex", c_void_p),
        ("recvNoneZeroGridIndex", c_void_p),
        ("sendStatus", c_void_p),
        ("recvStatus", c_void_p),
        ("sendRequest", c_void_p),
        ("recvRequest", c_void_p)
    ]


# 定义加速器结构体
class Lattice(Structure):
    _fields_ = [
        ("numComponents", c_int),
        ("latticeLength", c_double),
        ("latticeComponents_cpu", c_void_p),
        ("latticeComponents_gpu", c_void_p),
        ("baseComponents", c_void_p)
    ]


# 定义粒子结构体
class Particles(Structure):
    _fields_ = [
        ("status", c_void_p),
        ("numStatusChanged", c_void_p),
        ("numStatusMissed", c_void_p),
        ("phaseFlag", c_void_p),
        ("insideFlag", c_void_p),
        ("panelIdx", c_void_p),
        ("globalIdx", c_void_p),
        ("index", c_void_p),
        ("locatedIdx", c_void_p),
        ("numNormalParticles", c_int),
        ("numParticles", c_int),
        ("numNotMissedParticles", c_int),
        ("picGridIndex", c_void_p),
        ("charge", c_double),
        ("mass", c_double),
        ("qOverMass", c_double),
        ("massMev", c_double),
        ("pos", c_void_p),
        ("vel", c_void_p),
        ("phasePos", c_void_p),
        ("phaseVel", c_void_p),
        ("extMagnField", c_void_p),
        ("extElecField", c_void_p),
        ("intElecField", c_void_p),
        ("timeStamp", c_void_p),
        ("phaseTimeStamp", c_void_p)
    ]


# 定义示踪粒子结构体
class SyncParticle(Structure):
    _fields_ = [
        ("charge", c_double),
        ("mass", c_double),
        ("qOverMass", c_double),
        ("massMev", c_double),
        ("cavityEz", c_double),
        ("status", c_int),
        ("locatedIdx", c_int),
        ("phaseFlag", c_int),
        ("pos", double3),
        ("vel", double3),
        ("phasePos", double3),
        ("phaseVel", double3),
        ("extMagnField", double3),
        ("extElecField", double3),
        ("timeStamp", c_double),
        ("phaseTimeStamp", c_double)
    ]


# 定义束流结构体
class Beam(Structure):
    _fields_ = [
        ("distributionType", c_int * 2),
        ("numCharge", c_double),
        ("particleRestMass", c_double),
        ("frequence", c_double),
        ("current", c_double),
        ("timeStart", c_double),
        ("timeLength", c_double),
        ("kneticEnergySum", c_double),
        ("twissx", c_double * 3),
        ("twissy", c_double * 3),
        ("twissz", c_double * 3),
        ("displacePosition", c_double * 3),
        ("displacedPosition", c_double * 3),
        ("kneticEnergy", c_double * 2),
        ("particles_cpu", Particles),
        ("particles_gpu", Particles),
        ("particles_init", Particles),
        ("scanParticle", SyncParticle),
        ("tracerParticle", SyncParticle)
    ]


# 定义CUB结构体
class CUBObject(Structure):
    _fields_ = [
        ("buffer", c_void_p),
        ("bufferSize", c_size_t),
        ("iReduceVale", c_void_p),
        ("fixedIndex", c_void_p),
        ("locatedIdx", c_void_p),
        ("phaseFlag", c_void_p),
        ("status", c_void_p),
        ("panelIdx", c_void_p),
        ("globalIdx", c_void_p),
        ("picGridIndex", c_void_p),
        ("fReduceValue", c_void_p),
        ("timeStamp", c_void_p),
        ("phaseTimeStamp", c_void_p),
        ("pos", c_void_p),
        ("vel", c_void_p),
        ("phasePos", c_void_p),
        ("phaseVel", c_void_p),
        ("segmentOffset", c_void_p),
        ("pvxyz", c_void_p)
    ]


# 定义PIC结构体
class PIC(Structure):
    _fields_ = [
        ("nx", c_int),
        ("ny", c_int),
        ("nz", c_int),
        ("numCopies", c_int),
        ("dx", c_double),
        ("dy", c_double),
        ("dz", c_double),
        ("minx", c_double),
        ("miny", c_double),
        ("minz", c_double),
        ("maxx", c_double),
        ("maxy", c_double),
        ("maxz", c_double),
        ("gridCharge_cpu", c_void_p),
        ("gridCharge_gpu", c_void_p),
        ("gridCoef_cpu", c_void_p),
        ("gridCoef_gpu", c_void_p),
        ("distributedGridCharge", c_void_p),
        ("gridPotential_cpu", c_void_p),
        ("gridPotential_gpu", c_void_p),
        ("diffGridCharge", c_void_p),
        ("fixedIndex", c_void_p),
        ("cutoffInt", c_int * 3),
        ("cutoffIntRadius", c_int),
        ("field_cpu", c_void_p),
        ("field_gpu", c_void_p),
        ("noneZeroFlag_gpu", c_void_p),
        ("noneZeroFlag_cpu", c_void_p),
        ("noneZeroLine_cpu", c_void_p),
        ("noneZeroLine_gpu", c_void_p),
        ("noneZeroGridCharge", c_void_p),
        ("noneZeroGridIndex", c_void_p),
        ("segmentOffset", c_void_p)
    ]


# 定义束流统计结构体
class BeamStatistics(Structure):
    _fields_ = [
        ("pcHistogram_cpu", c_void_p),
        ("pcHistogram_gpu", c_void_p),
        ("avgPos", c_double * 3),
        ("avgVel", c_double * 3),
        ("avgVelSlope", c_double * 3),
        ("varPos", c_double * 3),
        ("varVelSlope", c_double * 3),
        ("stdPos", c_double * 3),
        ("stdVelSlope", c_double * 3),
        ("varCross", c_double * 3),
        ("avgEz", c_double),
        ("emit", c_double * 3),
        ("emitAlpha", c_double * 3),
        ("emitBeta", c_double * 3),
        ("maxVelSlope", c_double * 3),
        ("maxPos", c_double * 3),
        ("minHis", c_double * 4),
        ("maxHis", c_double * 4),
        ("avgHis", c_double * 4),
        ("beta", c_double),
        ("gamma", c_double),
    ]


# 定义FFT求解器结构体
class FFTSolver(Structure):
    _fields_ = [
        ("fftHandle", c_int),
        ("fftGridCharge_gpu", c_void_p),
        ("fftGridCharge_cpu", c_void_p),
        ("gridCharge_cpu", c_void_p),
        ("gridCharge_gpu", c_void_p),
        ("skx", c_void_p),
        ("sky", c_void_p),
        ("skz", c_void_p)
    ]


# 定义基础器件结构包括器件文件名，大小，磁场和电场强度
class BaseComponents(Structure):
    _fields_ = [
        ("name", c_char * BUFFERSIZE),
        ("nx", c_int),
        ("ny", c_int),
        ("nz", c_int),
        ("minx", c_double),
        ("maxx", c_double),
        ("miny", c_double),
        ("maxy", c_double),
        ("maxz", c_double),
        ("dx", c_double),
        ("dy", c_double),
        ("dz", c_double),
        ("field_cpu", c_void_p),
        ("field_gpu", c_void_p),
        ("next", c_void_p)
    ]


class ErrorParameters(Structure):
    _fields_ = [
        ("sw", c_int * 7),
        ("errx", c_double),
        ("erry", c_double),
        ("errz", c_double),
        ("errpx", c_double),
        ("errpy", c_double),
        ("errpz", c_double),
        ("errkg", c_double),
        ("errs", c_double)
    ]


# 定义实际器件结构包括器件类型，大小，指向磁场、电场强度指针
class LatticeComponents(Structure):
    _fields_ = [
        ("phiScanned", c_bool),
        ("zstart", c_double),
        ("zend", c_double),
        ("len", c_double),
        ("rad", c_double),
        ("freq", c_double),
        ("phiS", c_double),
        ("ke", c_double),
        ("kb", c_double),
        ("phi0", c_double),
        ("time0", c_double),
        ("superposeEnd", c_double),
        ("gradient", c_double),
        ("errorAnalysis", c_int),
        ("type", c_int),
        ("nx", c_int),
        ("ny", c_int),
        ("nz", c_int),
        ("superpose", c_int),
        ("superposeStartIdx", c_int),
        ("superposeEndIdx", c_int),
        ("minx", c_double),
        ("maxx", c_double),
        ("miny", c_double),
        ("maxy", c_double),
        ("maxz", c_double),
        ("dx", c_double),
        ("dy", c_double),
        ("dz", c_double),
        ("field_cpu", c_void_p),
        ("field_gpu", c_void_p),
        ("errorParameters", ErrorParameters)
    ]


# 定义保存多线程扫相参数的结构体
class ScanPhaseThreadArgs(Structure):
    _fields_ = [
        ("n", c_int),
        ("idx", c_int),
        ("success", c_void_p),
        ("timeStep", c_double),
        ("scanAngleStep", c_double),
        ("phi0Last", c_double),
        ("phi0", c_void_p),
        ("phiS", c_void_p),
        ("phiE", c_void_p),
        ("latticeComponents", c_void_p),
        ("scanParticle", SyncParticle)
    ]


# 定义保存MPI数据的结构体
class LoadBeamThreadArgs(Structure):
    _fields_ = [
        ("idx", c_int),
        ("fp", c_void_p),
        ("readBytes", c_size_t),
        ("offset", c_size_t),
        ("n", c_int),
        ("pos", c_void_p),
        ("vel", c_void_p),
        ("minTime", c_double),
        ("maxTime", c_double),
        ("KneticEnergySum", c_double)
    ]


# 定义插值面板
class OutputPanels(Structure):
    _fields_ = [
        ("panelz", c_double),
        ("phasePos_cpu", c_void_p),
        ("phaseVel_cpu", c_void_p),
        ("phasePos_gpu", c_void_p),
        ("phaseVel_gpu", c_void_p),
        ("phaseTimeStamp_cpu", c_void_p),
        ("phaseTimeStamp_gpu", c_void_p)
    ]


# 定义缓冲池
class BufferPool(Structure):
    _fields_ = [
        ("mutex", c_void_p),
        ("bufferPoolCnt", c_int),
        ("itr", c_void_p),
        ("phaseFlag", c_void_p),
        ("timeStamp", c_void_p),
        ("posz", c_void_p),
        ("outputData_cpu", POINTER(c_void_p)),
        ("outputData_gpu", c_void_p)
    ]


# 定义
class BufferPoolThreadArgs(Structure):
    _fields_ = [
        ("threadIdx", c_int),
        ("fp", c_void_p),
        ("runningOptions", RunningOptions),
        ("beam", Beam),
        ("mpiObject", c_void_p),
        ("bufferPool", BufferPool)
    ]


class OutputData(Structure):
    _fields_ = [
        ("posx", c_double),
        ("velx", c_double),
        ("posy", c_double),
        ("vely", c_double),
        ("posz", c_double),
        ("velz", c_double),
        ("status", c_int),
        ("globalIdx", c_int)
    ]


class OutputObject(Structure):
    _fields_ = [
        ("numPanels", c_int),
        ("panels_cpu", c_void_p),
        ("panels_gpu", c_void_p),
        ("bufferPool", c_void_p)
    ]

