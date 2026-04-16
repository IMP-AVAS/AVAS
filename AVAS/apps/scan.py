
from core.MultiParticle import AVAS

from utils.beamconfig import BeamConfig
from utils.inputconfig import InputConfig
from utils.latticeconfig import LatticeConfig

class Scan():
    def __init__(self, dllpath, projectpath, scan_parameter, scan_start, scan_end, scan_step, scan_parameter_place):# scan_parameter_place 为 input , beam , lattice
        self.dllpath = dllpath
        self.projectpath = projectpath
        self.scan_parameter = scan_parameter
        self.scan_start = scan_start
        self.scan_end = scan_end
        self.scan_step = scan_step
        self.scan_parameter_place = scan_parameter_place

        self.scan_list = self._genrate_scan_list()
        self.avas = AVAS(self.dllpath, self.projectpath)

    def genrate_scan_list(self):
        scan_list = []
        for i in range(self.scan_start, self.scan_end, self.scan_step):
            dic = {self.scan_parameter: i}
            scan_list.append(dic)
        return scan_list

    def run(self):
        for i in self.scan_list:
            res = self.avas.run(input_change={self.scan_parameter: i} if self.scan_parameter_place == 'input' else None,
                        beam_change={self.scan_parameter: i} if self.scan_parameter_place == 'beam' else None,
                        lattice_change={self.scan_parameter: i} if self.scan_parameter_place == 'lattice' else None)
        return None
