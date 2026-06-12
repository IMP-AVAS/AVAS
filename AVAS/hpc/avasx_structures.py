from ctypes import *

BUFFER_SIZE = 512
FFT = 0
EDST = 1

# 定义float3结构体
class float3(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float)
    ]

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

# 定义cufftDoubleComplex
class cufftDoubleComplex(Structure):
    _fields_ = [
        ("x", c_double),
        ("y", c_double)
    ]

# 定义Particles结构体
class Particles(Structure):
    _fields_ = [
        ("numParticles", c_int),
        ("numNormalParticles", c_int),
        ("numNotMissedParticles", c_int),
        ("numStatusChanged", POINTER(c_int)),
        ("numStatusMissed", POINTER(c_int)),
        ("status", POINTER(c_int)),
        ("phaseFlag", POINTER(c_int)),
        ("bendFlag", POINTER(c_int)),
        ("insideFlag", POINTER(c_int)),
        ("globalIdx", POINTER(c_int)),
        ("locatedIdx", POINTER(c_int)),
        ("picGridIndex", POINTER(c_int)),
        ("panelIdx", POINTER(c_int)),
        ("index", POINTER(c_int)),
        ("boundaryIdx", POINTER(c_int)),
        ("pos", POINTER(double3)),
        ("vel", POINTER(double3)),
        ("transPos", POINTER(double3)),
        ("transVel", POINTER(double3)),
        ("phasePos", POINTER(double3)),
        ("phaseVel", POINTER(double3)),
        ("charge", POINTER(c_double)),
        ("numCharge", POINTER(c_double)),
        ("massMev", POINTER(c_double)),
        ("numMacro", POINTER(c_double)),
        ("qOverMass", POINTER(c_double)),
        ("extMagnField", POINTER(double3)),
        ("extElecField", POINTER(double3)),
        ("intElecField", POINTER(double3)),
        ("phaseTimeStamp", POINTER(c_double))
    ]

# 定义SyncParticle结构体
class SyncParticle(Structure):
    _fields_ = [
        ("status", c_int),
        ("phaseFlag", c_int),
        ("bendFlag", c_int),
        ("locatedIdx", c_int),
        ("panelIdx", c_int),
        ("charge", c_double),
        ("numCharge", c_double),
        ("massMev", c_double),
        ("numMacro", c_double),
        ("qOverMass", c_double),
        ("cavityEz", c_double),
        ("pos", double3),
        ("vel", double3),
        ("oldPos", double3),
        ("oldVel", double3),
        ("phasePos", double3),
        ("phaseVel", double3),
        ("extMagnField", double3),
        ("extElecField", double3),
        ("timeStamp", c_double),
        ("oldTimeStamp", c_double),
        ("phaseTimeStamp", c_double),
        ("rx", c_double),
        ("ry", c_double),
        ("deflection", c_int)
    ]

# 定义Beam结构体
class Beam(Structure):
    _fields_ = [
        ("dst_or_edst", c_int),
        ("frequence", c_double),
        ("intensity", c_double),
        ("massMev", c_double),
        ("numCharge", c_double),
        ("initBunchCharge", c_double),
        ("timeStart", c_double),
        ("timeLength", c_double),
        ("kneticEnergySum", c_double),
        ("distributionType", c_int * 2),
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

# 定义BaseFieldList结构体
class BaseFieldList(Structure):
    pass
BaseFieldList._fields_ = [
    ("name", c_char * BUFFER_SIZE),
    ("nx", c_int),
    ("ny", c_int),
    ("nz", c_int),
    ("min_x", c_double),
    ("max_x", c_double),
    ("min_y", c_double),
    ("max_y", c_double),
    ("max_z", c_double),
    ("dx", c_double),
    ("dy", c_double),
    ("dz", c_double),
    ("field_cpu", POINTER(float6)),
    ("magnField_cpu", POINTER(float3)),
    ("field_gpu", POINTER(float6)),
    ("magnField_gpu", POINTER(float3)),
    ("next", POINTER(BaseFieldList)),
    ("magnx_cpu", POINTER(c_float)),
    ("magny_cpu", POINTER(c_float)),
    ("magnz_cpu", POINTER(c_float)),
    ("elecx_cpu", POINTER(c_float)),
    ("elecy_cpu", POINTER(c_float)),
    ("elecz_cpu", POINTER(c_float)),
    ("magnx_array", c_void_p),
    ("magny_array", c_void_p),
    ("magnz_array", c_void_p),
    ("elecx_array", c_void_p),
    ("elecy_array", c_void_p),
    ("elecz_array", c_void_p),
    ("texMagnxObj", c_ulonglong),
    ("texMagnyObj", c_ulonglong),
    ("texMagnzObj", c_ulonglong),
    ("texElecxObj", c_ulonglong),
    ("texElecyObj", c_ulonglong),
    ("texEleczObj", c_ulonglong)
]

# 定义ErrorParameters结构体
class ErrorParameters(Structure):
    _fields_ = [
        ("sw", c_int*7),
        ("err_x", c_double),
        ("err_y", c_double),
        ("err_z", c_double),
        ("err_rx", c_double),
        ("err_ry", c_double),
        ("err_rz", c_double),
        ("err_kg", c_double),
        ("err_s", c_double)
    ]

class LatticeComponents(Structure):
    _fields_ = [
        ("phiScanned", c_bool),
        ("type", c_int),
        ("entrance_z", c_double),
        ("exit_z", c_double),
        ("len", c_double),
        ("rad", c_double),
        ("freq", c_double),
        ("phiS", c_double),
        ("ke", c_double),
        ("kb", c_double),
        ("phi0", c_double),
        ("time0", c_double),
        ("gradient", c_double),
        ("err_ke", c_double),
        ("err_kb", c_double),
        ("err_phi0", c_double),
        ("min_x", c_double),
        ("max_x", c_double),
        ("min_y", c_double),
        ("max_y", c_double),
        ("max_z", c_double),
        ("nx", c_int),
        ("ny", c_int),
        ("nz", c_int),
        ("dx", c_double),
        ("dy", c_double),
        ("dz", c_double),
        ("inv_dx", c_double),
        ("inv_dy", c_double),
        ("inv_dz", c_double),
        ("enableErrorAnalysis", c_int),
        ("errorParameters", ErrorParameters),
        ("isSuperpose", c_int),
        ("superposeFirstIdx", c_int),
        ("superposeLastIdx", c_int),
        ("isSuperposeBend", c_int),
        ("firstSuperposeLine", c_int),
        ("superposeoutLine", c_int),
        ("superpose_entrance_z", c_double),
        ("superpose_exit_z", c_double),
        ("err_offset", double3),
        ("err_rotate", double3),
        ("no_err_offset", double3),
        ("no_err_rotate", double3),
        ("bend_exit_offset", double3),
        ("bend_exit_rotate", double3),
        ("field_cpu", POINTER(float6)),
        ("mangField_cpu", POINTER(float3)),
        ("field_gpu", POINTER(float6)),
        ("magnField_gpu", POINTER(float3)),
        ("texMagnxObj", c_ulonglong),
        ("texMagnyObj", c_ulonglong),
        ("texMagnzObj", c_ulonglong),
        ("texElecxObj", c_ulonglong),
        ("texElecyObj", c_ulonglong),
        ("texEleczObj", c_ulonglong)
    ]

# 定义OutputPanels结构体
class OutputPanels(Structure):
    _fields_ = [
        ("panel_z", c_double),
        ("phasePos_cpu", POINTER(double3)),
        ("phaseVel_cpu", POINTER(double3)),
        ("phaseTimeStamp_cpu", POINTER(c_double)),
        ("numCharge_cpu", POINTER(c_double)),
        ("massMev_cpu", POINTER(c_double)),
        ("numMacro_cpu", POINTER(c_double)),
        ("phasePos_gpu", POINTER(double3)),
        ("phaseVel_gpu", POINTER(double3)),
        ("phaseTimeStamp_gpu", POINTER(c_double)),
        ("numCharge_gpu", POINTER(c_double)),
        ("massMev_gpu", POINTER(c_double)),
        ("numMacro_gpu", POINTER(c_double)),
        ("tracerPhasePos", double3),
        ("tracerPhaseVel", double3),
        ("tracerPhaseTimeStamp", c_double),
        ("tracerNumCharge", c_double),
        ("tracerMassMev", c_double),
        ("tracerNumMacro", c_double)
    ]

# 定义LatticeBoundaries结构体
class LatticeBoundaries(Structure):
    _fields_ = [
        ("type", c_int),
        ("deflection", c_int),
        ("positive_or_negative", c_int),
        ("entrance_z", c_double),
        ("exit_z", c_double),
        ("len", c_double),
        ("d1", c_double),
        ("d2", c_double),
        ("dA", c_double),
        ("isSuperpose", c_int),
        ("superposeFirstIdx", c_int),
        ("superposeLastIdx", c_int),
        ("isSuperposeBend", c_int),
        ("superpose_entrance_z", c_double),
        ("superpose_exit_z", c_double),
        ("offset", double3),
        ("rotate", double3),
        ("bend_exit_offset", double3),
        ("bend_exit_rotate", double3)
    ]

# 定义Lattice结构体
class Lattice(Structure):
    _fields_ = [
        ("numComponents", c_int),
        ("numPanels", c_int),
        ("numBoundaries", c_int),
        ("lattice_exit_z", c_double),
        ("boundary_exit_z", c_double),
        ("latticeComponents_cpu", POINTER(LatticeComponents)),
        ("latticeComponents_gpu", POINTER(LatticeComponents)),
        ("outputPanels_cpu", POINTER(OutputPanels)),
        ("outputPanels_gpu", POINTER(OutputPanels)),
        ("latticeBoundaries_cpu", POINTER(LatticeBoundaries)),
        ("latticeBoundaries_gpu", POINTER(LatticeBoundaries)),
        ("baseFieldList", POINTER(BaseFieldList))
    ]

# 定义ConfigLineList结构体
class ConfigLineList(Structure):
    pass
ConfigLineList._fields_ = [
    ("buffer", c_char * BUFFER_SIZE),
    ("componentIdx", c_int),
    ("lineIdx", c_int),
    ("next", POINTER(ConfigLineList))
]

# 定义RunningOptions结构体
class RunningOptions(Structure):
    _fields_ = [
        ("enableSpaceCharge", c_bool),
        ("enableAggregation", c_bool),
        ("enablePCHistogram", c_bool),
        ("enableScanPhase", c_bool),
        ("enableLoopBoundary", c_bool),
        ("spaceChargeMethod", c_int),
        ("numPICGridPoints", c_int * 3),
        ("arrangeSequenceInterval", c_int),
        ("blockGroupSize", c_int),
        ("numMemoryCopies", c_int),
        ("statOutputInterval", c_int),
        ("numPCHistogram", c_int),
        ("dumpPeriodicity", c_int),
        ("stepPerCycle", c_double),
        ("scanAngleStep", c_double),
        ("rmsSize", c_double * 3),
        ("fieldPath", c_char * BUFFER_SIZE),
        ("outputPath", c_char * BUFFER_SIZE),
        ("beamPath", c_char * BUFFER_SIZE)
    ]

# 定义CUBObject结构体
class CUBObject(Structure):
    _fields_ = [
        ("buffer", c_void_p),
        ("bufferSize", c_size_t),
        ("segmentOffset", POINTER(c_int)),
        ("data", POINTER(c_double)),
        ("iReduceValue", POINTER(c_int)),
        ("fReduceValue", POINTER(c_double)),
        ("status", POINTER(c_int)),
        ("phaseFlag", POINTER(c_int)),
        ("bendFlag", POINTER(c_int)),
        ("globalIdx", POINTER(c_int)),
        ("locatedIdx", POINTER(c_int)),
        ("panelIdx", POINTER(c_int)),
        ("fixedIndex", POINTER(c_int)),
        ("picGridIndex", POINTER(c_int)),
        ("boundaryIdx", POINTER(c_int)),
        ("pos", POINTER(double3)),
        ("vel", POINTER(double3)),
        ("transPos", POINTER(double3)),
        ("transVel", POINTER(double3)),
        ("phasePos", POINTER(double3)),
        ("phaseVel", POINTER(double3)),
        ("charge", POINTER(c_double)),
        ("numCharge", POINTER(c_double)),
        ("massMev", POINTER(c_double)),
        ("numMacro", POINTER(c_double)),
        ("qOverMass", POINTER(c_double)),
        ("phaseTimeStamp", POINTER(c_double))
    ]

# 定义ScanPhaseThreadArgs结构体
class ScanPhaseThreadArgs(Structure):
    _fields_ = [
        ("n", c_int),
        ("idx", c_int),
        ("success", POINTER(c_bool)),
        ("timeStep", c_double),
        ("scanAngleStep", c_double),
        ("phi0Last", c_double),
        ("phi0", POINTER(c_double)),
        ("phiS", POINTER(c_double)),
        ("phiE", POINTER(c_double)),
        ("latticeComponents", POINTER(LatticeComponents)),
        ("scanParticle", SyncParticle)
    ]

# 定义MPIObject结构体
class MPIObject(Structure):
    _fields_ = [
        ("rank", c_int),
        ("commSize", c_int),
        ("devIdx", c_int),
        ("avgNumParticles", c_int),
        ("numNormalParticles", c_int),
        ("numNotMissedParticles", c_int),
        ("phaseFlag", c_int),
        ("bendFlag", c_int),
        ("numNoneZeroGrid", POINTER(c_int)),
        ("gridOffset", POINTER(c_int)),
        ("sendNoneZeroGridIndex", POINTER(c_int)),
        ("recvNoneZeroGridIndex", POINTER(c_int)),
        ("sendNoneZeroGridCharge", POINTER(c_double)),
        ("recvNoneZeroGridCharge", POINTER(c_double)),
        ("sendStatus", c_void_p),
        ("recvStatus", c_void_p),
        ("sendRequest", c_void_p),
        ("recvRequest", c_void_p),
        ("infos", POINTER(c_char_p))
    ]

# 定义LoadBeamThreadArgs结构体
class LoadBeamThreadArgs(Structure):
    _fields_ = [
        ("fp", c_void_p),
        ("threadIdx", c_int),
        ("numParticles", c_int),
        ("readBytes", c_size_t),
        ("offset", c_size_t),
        ("pos", POINTER(double3)),
        ("vel", POINTER(double3)),
        ("numCharge", POINTER(c_double)),
        ("massMev", POINTER(c_double)),
        ("numMacro", POINTER(c_double)),
        ("minTime", c_double),
        ("maxTime", c_double),
        ("kneticEnergySum", c_double)
    ]

# 定义NCCL结构体
class NCCLObject(Structure):
    _feilds_ = [
        ("id", c_void_p),
        ("comm", c_void_p)
    ]

# 定义PIC结构体
class PIC(Structure):
    _fields_ = [
        ("fixedIndex_gpu", POINTER(c_int)),
        ("nx", c_int),
        ("ny", c_int),
        ("nz", c_int),
        ("numCopies", c_int),
        ("dx", c_double),
        ("dy", c_double),
        ("dz", c_double),
        ("inv_dx", c_double),
        ("inv_dy", c_double),
        ("inv_dz", c_double),
        ("inv_dx_sq", c_double),
        ("inv_dy_sq", c_double),
        ("inv_dz_sq", c_double),
        ("min_x", c_double),
        ("max_x", c_double),
        ("min_y", c_double),
        ("max_y", c_double),
        ("min_z", c_double),
        ("max_z", c_double),
        ("gridCharge_cpu", POINTER(c_double)),
        ("gridCharge_gpu", POINTER(c_double)),
        ("distributedGridCharge_gpu", POINTER(c_double)),
        ("diffGridCharge_gpu", POINTER(c_double)),
        ("gridCoef_cpu", POINTER(c_double)),
        ("gridCoef_gpu", POINTER(c_double)),
        ("gridPotential_cpu", POINTER(c_double)),
        ("gridPotential_gpu", POINTER(c_double)),
        ("cutoffInt", c_int * 3),
        ("cutoffIntRadius", c_int),
        ("gridMark_cpu", POINTER(c_int)),
        ("gridMark_gpu", POINTER(c_int)),
        ("noneZeroLine_cpu", POINTER(c_int)),
        ("noneZeroLine_gpu", POINTER(c_int)),
        ("flaggedGridCharge_gpu", POINTER(c_double)),
        ("flaggedGridIndex_gpu", POINTER(c_int)),
        ("segmentOffset", POINTER(c_int)),
        ("field_cpu", POINTER(double3)),
        ("field_gpu", POINTER(double3))
    ]

# 定义BeamStatistics结构体
class BeamStatistics(Structure):
    _fields_ = [
        ("pcHistogram_cpu", POINTER(c_int)),
        ("pcHistogram_gpu", POINTER(c_int)),
        ("avgEz", c_double),
        ("bunchCharge", c_double),
        ("maxPos", c_double * 3),
        ("avgPos", c_double * 3),
        ("avgVel", c_double * 3),
        ("avgVelSlope", c_double * 3),
        ("maxVelSlope", c_double * 3),
        ("varPos", c_double * 3),
        ("stdPos", c_double * 3),
        ("varVelSlope", c_double * 3),
        ("stdVelSlope", c_double * 3),
        ("varCross", c_double * 3),
        ("emit", c_double * 3),
        ("emitAlpha", c_double * 3),
        ("emitBeta", c_double * 3),
        ("minHis", c_double * 4),
        ("maxHis", c_double * 4),
        ("avgHis", c_double * 4),
        ("beta", c_double),
        ("gamma", c_double)
    ]

# 定义FFTSolver结构体
class FFTSolver(Structure):
    _fields_ = [
        ("workspace", c_void_p),
        ("fftHandle", c_int),
        ("complex_cpu", POINTER(cufftDoubleComplex)),
        ("complex_gpu", POINTER(cufftDoubleComplex)),
        ("gridCharge_cpu", POINTER(cufftDoubleComplex)),
        ("gridCharge_gpu", POINTER(cufftDoubleComplex)),
        ("gridPotential_cpu", POINTER(cufftDoubleComplex)),
        ("gridPotential_gpu", POINTER(cufftDoubleComplex)),
        ("skx", POINTER(c_double)),
        ("sky", POINTER(c_double)),
        ("skz", POINTER(c_double))
    ]
