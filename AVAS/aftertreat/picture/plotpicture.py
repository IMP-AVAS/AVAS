import matplotlib.pyplot as plt
from utils.readfile import read_txt, read_dst, read_lattice_mulp_with_name
from aftertreat.picture.initialplot import PicturelBar_2D, PicturePlot_2D
import numpy as np
from dataprovision.latticeparameter import LatticeParameter
from dataprovision.datasetparameter import DatasetParameter
from utils.readfile import read_lattice_mulp_with_name
class PlotCavityVoltage(PicturelBar_2D):
    """
    腔压图
    """
    def __init__(self, lattiace_mulp_path , ratio):
        super().__init__( )
        self.ratio = ratio
        self.title = 'Cavity Voltage'
        self.xlabel = 'Cavity (Num)'
        self.ylabel = 'Cavity Voltage(MV/M)'
        # self.project_path = project_path
        # self.beam_path = self.project_path + r'\InputFile' + r'\beam.txt'
        # self.lattice_path = self.project_path + r'\InputFile' + r'\lattice_mulp.txt'
        # self.input_path = self.project_path + r'\InputFile' + r'\input.txt'
        # self.dataset_path = self.project_path + r'\OutputFile' + r'\DataSet.txt'
        self.lattice_mulp_path = lattiace_mulp_path

    def get_x_y(self, ):

        all_info, _ = read_lattice_mulp_with_name(self.lattice_mulp_path)
        x = []
        y = []
        index = 1
        for i in all_info:
            if i[0] == 'field' and float(i[4]) == 1:
                x.append(index)
                y.append(float(i[7]) * self.ratio[i[9]])
                index += 1
            if i[0] == "end":
                break
        self.x = x
        self.y = y

        return self.x, self.y
import os

class PlotCavitySynPhase(PicturePlot_2D):
    """
    同步相位图
    """
    def __init__(self, lattice_mulp_path):
        super().__init__()
        self.title = ''
        self.xlabel = 'Cavity (Num)'
        self.ylabel = 'Synchronous phase ( deg )'

        # self.project_path = project_path
        # self.beam_path = self.project_path + r'\InputFile' + r'\beam.txt'
        # self.lattice_path = self.project_path + r'\InputFile' + r'\lattice.txt'
        # self.input_path = self.project_path + r'\InputFile' + r'\input.txt'
        self.lattice_mulp_path = lattice_mulp_path


    def get_x_y(self,):
        all_info = read_txt(self.lattice_mulp_path, out='list')
        x = []
        y = []
        index = 1
        for i in all_info:
            if i[0] == 'field' and float(i[4]) == 1:
                x.append(index)
                y.append(float(i[6]))
                index += 1
            if i[0] == "end":
                break
        self.x = [x]
        self.y = [y]
        self.markers = ['o']

        return self.x, self.y

class PlotPhaseAdvance(PicturePlot_2D):
    """
    束流相移
    """
    def __init__(self, project_path, picture_type):
        super().__init__()
        self.xlabel = "Position( m )"
        self.labels = [r"$\sigma_{x}$", r"$\sigma_{y}$", r"$\sigma_{z}$"]

        self.project_path = project_path
        self.beam_path = os.path.join(self.project_path, 'InputFile', 'beam.txt')
        self.lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')
        self.input_path = os.path.join(self.project_path, 'InputFile', 'input.txt')
        self.dataset_path = os.path.join(self.project_path, 'OutputFile', 'DataSet.txt')
        self.picture_type = picture_type

    def get_x_y(self):
        out_type = self.picture_type
        if out_type == 'period':
            self.ylabel = "Phase advance( deg )"
        elif out_type == "meter":
            self.ylabel = "Phase advance( deg/m )"

        dataset_obj = DatasetParameter(self.dataset_path)
        dataset_obj.get_parameter()

        lattcie_mulp_list, lattice_mulp_name = read_lattice_mulp_with_name(self.lattice_mulp_path)

        lattice_obj = LatticeParameter()
        lattice_obj.get_period(lattcie_mulp_list)
        v_start_end = lattice_obj.v_start_end

        z = dataset_obj.z ##

        Beta_x = dataset_obj.beta_x ##
        Beta_y = dataset_obj.beta_y ##
        Beta_z = dataset_obj.beta_z ##


        period_pa_x = []
        period_pa_y = []
        period_pa_z = []

        dz = [(z[i + 1] - z[i]) * 1000 for i in range(len(z) - 1)]
        dz.append(dz[-1])  ##


        for i in v_start_end:
            sig_x = 0
            sig_y = 0
            sig_z = 0
            for j in range(0, len(z)):
                if z[j] >= i[0] and z[j] < i[1]:
                    sig_x += (1 / Beta_x[j]) * dz[j]
                    sig_y += (1 / Beta_y[j]) * dz[j]
                    sig_z += (1 / Beta_z[j]) * dz[j]

                if z[j] > i[1] or j == len(z) - 1:
                    period_pa_x.append(sig_x)
                    period_pa_y.append(sig_y)
                    period_pa_z.append(sig_z)
                    break


        period_pa_x = [i * 180 / np.pi / 1000 for i in period_pa_x]
        period_pa_y = [i * 180 / np.pi / 1000 for i in period_pa_y]
        period_pa_z = [i * 180 / np.pi / 1000 for i in period_pa_z]

        period_length = [i[1] - i[0] for i in v_start_end]
        if out_type == "meter":
            period_pa_x = [period_pa_x[i] / period_length[i] for i in range(len(period_pa_x))]
            period_pa_y = [period_pa_y[i] / period_length[i] for i in range(len(period_pa_y))]
            period_pa_z = [period_pa_z[i] / period_length[i] for i in range(len(period_pa_z))]

        x_coor = [i[1] for i in v_start_end]
        period_pa = [period_pa_x, period_pa_y, period_pa_z]

        self.x = x_coor
        self.y = period_pa
        # print(self.x)
        # print(self.y)
        self.xlim = [0, max(self.x) * 1.05]
        self.ylim = [0, max(period_pa_x + period_pa_y + period_pa_z) * 1.1]

        self.markers = ['o', 'o', 'o']
        self.set_legend = 1
        # self.labels = ['x', 'y', 'z']

        if not isinstance(self.y[0], list):
            self.y = [self.y]
        if not isinstance(self.x[0], list):
            self.x = [self.x]

        if len(self.x) != len(self.y):
            self.x = self.x * len(self.y)


        return self.x, self.y



if __name__ == "__main__":
    project_path = r"C:\Users\wangh\Desktop\yiman\1gEv"
    obj = PlotPhaseAdvance(project_path, "period" )
    obj.get_x_y()
    obj.run(show_=1, fig =None)