import numpy as np
import matplotlib.pyplot as plt
import math
from aftertreat.picture.initialplot import PicturePlot_2D, CompoundShape
from utils.readfile import read_txt, read_dst
from dataprovision.datasetparameter import DatasetParameter
from dataprovision.latticeparameter import LatticeParameter
from utils.tool import get_list_interval
import os
import matplotlib
# matplotlib.use('Qt5Agg')
# [ 'emittance_x', 'emittance_y', 'emittance_z',
# 'longitudinal_phase', ]
class PlotDataSet(PicturePlot_2D):
    """
    dataset文件的可视化
    """
    def __init__(self, dataset_path, picture_name, sample_interval=1, project_path=None):
        super().__init__()
        self.picture_name = picture_name
        self.sample_interval = sample_interval
        self.BaseMassInMeV = 0
        self.freq = 0

        if project_path:
            self.project_path = project_path
        else:
            self.project_path = None
        self.dataset_path = dataset_path
        # self.beam_path = self.project_path + r'\InputFile' + r'\beam.txt'
        if self.project_path:
            self.lattice_mulp_path = os.path.join(self.project_path, "InputFile", 'lattice_mulp.txt')
        # self.lattice_mulp_path = self.project_path + r'\InputFile' + r'\lattice_mulp.txt'
        # self.input_path = self.project_path + r'\InputFile' + r'\input.txt'
        # self.dataset_path = os.path.join(self.project_path, "OutputFile", "Dataset.txt" )
        # if dataset_path:
        #     self.dataset_path = dataset_path
        # else:



    def get_x_y(self):

        dataset_obj = DatasetParameter(self.dataset_path, self.project_path)
        dataset_obj.get_parameter()
        # end_index = dataset_obj.get_lattice_end_index() + 1
        end_index = -1
        z = dataset_obj.z[:end_index]  # 束团纵向位置

        ek = dataset_obj.ek[:end_index]  # 束团平均能量



        emit_x = [i * 10**6 for i in dataset_obj.emit_x][:end_index]
        emit_y = [i * 10**6 for i in dataset_obj.emit_y][:end_index]
        emit_z = [i * 10**6 for i in dataset_obj.emit_z][:end_index]

        rms_x = [i *10**3 for i in dataset_obj.rms_x][:end_index]#单位变成mm
        rms_xx = [i *10**3 for i in dataset_obj.rms_xx][:end_index]

        rms_y = [i *10**3 for i in dataset_obj.rms_y][:end_index]
        rms_yy = [i *10**3 for i in dataset_obj.rms_yy][:end_index]

        max_x = [i *10**3 for i in dataset_obj.max_x][:end_index]
        max_xx = [i *10**3 for i in dataset_obj.max_xx][:end_index]

        max_y = [i *10**3 for i in dataset_obj.max_y][:end_index]
        max_yy = [i *10**3 for i in dataset_obj.max_yy][:end_index]


        alpha_x = dataset_obj.alpha_x[:end_index]
        alpha_y = dataset_obj.alpha_y[:end_index]
        alpha_z = dataset_obj.alpha_z[:end_index]

        beta_x = dataset_obj.beta_x[:end_index]
        beta_y = dataset_obj.beta_y[:end_index]
        beta_z = dataset_obj.beta_z[:end_index]

        center_x = [i * 10**3 for i in dataset_obj.x][:end_index]#变为mm
        center_y = [i *10**3 for i in dataset_obj.y][:end_index]

        loss = dataset_obj.loss[:end_index]
        # phi = dataset_obj.phi[:end_index]
        # phi_phi = dataset_obj.phi_phi[:end_index]
        # BaseMassInMeV = dataset_obj.BaseMassInMeV
        # freq = dataset_obj.freq
        #
        # # for i in range(len(dataset_obj.ek)):
        # #     gammaaaa = dataset_obj.ek[i] / BaseMassInMeV + 1
        # #     beta.append(math.sqrt(1 - 1.0 / gammaaaa / gammaaaa))
        # #     v = dataset_obj.rms_z[i] / (beta[-1] * C_light) * freq * 360
        # #     # rms_z.append(dataset_obj.rms_z[i] / (beta[-1] * C_light) * freq * 360)
        # #     # rms_zz.append(-1 * (dataset_obj.rms_z[i] / (beta[-1] * C_light) * freq * 360))
        # #     rms_z.append(v)
        # #     rms_zz.append(-1 * v)
        # #
        # # for i in range(len(data)):
        # #     gammaaaa = data[i][0] / BaseMassInMeV + 1
        # #     beta.append(math.sqrt(1 - 1.0 / gammaaaa / gammaaaa))
        # #     rms_z.append(data[i][20] / (beta[-1] * C_light) * freq * 360)
        # #     rms_zz.append(-1 * (data[i][20] / (beta[-1] * C_light) * 162.5e6 * 360))

        if self.picture_name == "c_x":
            self.x = z
            self.y = [center_x]
            self.xlabel = "z(m)"
            self.ylabel = "Cener x(mm)"
            self.ylim = [-5, 5]

        if self.picture_name == "c_y":
            self.x = z
            self.y = [center_y]
            self.xlabel = "z(m)"
            self.ylabel = "Cener y(mm)"
            # self.ylim = [-max(loss)-3, max(loss) + 3]


        elif self.picture_name == 'c_xy':
            self.x = z
            self.y = [center_x, center_y]

            self.xlabel = "z(m)"
            self.ylabel = "Center x and y(mm)"

            self.labels = ['x', 'y']
            self.colors = ['r', 'b',]
            self.set_legend = 1
            self.ylim = [-5, 5]



        if self.picture_name == 'loss':
            self.x = z
            self.y = loss
            self.xlabel = "z(m)"
            self.ylabel = "loss"
            self.ylim = [-max(loss)-100, max(loss) + 100]


        elif self.picture_name == 'emittance_x':
            self.x = z
            self.y = emit_x


            self.xlabel = "z(m)"
            self.ylabel = "Emit_x(pi*mm*mrad)"


        elif self.picture_name == 'emittance_y':
            self.x = z
            self.y = emit_y

            self.xlabel = "z(m)"
            self.ylabel = "Emit_y(pi*mm*mrad)"



        elif self.picture_name == 'emittance_z':
            self.x = z
            self.y = emit_z

            self.xlabel = "z(m)"
            self.ylabel = "Emit_z(pi*mm*mrad)"


        elif self.picture_name == 'rms_x':
            self.x = z
            # print(z)
            # print(rms_x)
            # print(len(rms_x))

            self.y = [rms_x, rms_xx]

            self.xlabel = "z(m)"
            self.ylabel = "RMS_x Size(mm)"

            self.colors = ['r', 'r']
            self.ylim = [ -2 * np.max(np.array(rms_x)),  2 * np.max(np.array(rms_x)) ]

        elif self.picture_name == 'rms_y':
            self.x = z
            self.y = [rms_y, rms_yy]

            self.xlabel = "z(m)"
            self.ylabel = "RMS_y Size(mm)"
            self.colors = ['b', 'b']


        elif self.picture_name == 'rms_xy':
            self.x = z
            self.y = [rms_x, rms_xx, rms_y, rms_yy]

            self.xlabel = "z(m)"
            self.ylabel = "RMS_xy Size(mm)"

            self.labels = ['x', None, 'y', None]
            self.colors = ['r', 'r', 'b', 'b']
            self.set_legend = 1


        elif self.picture_name == 'max_x':
            self.x = z
            self.y = [max_x, max_xx]

            self.xlabel = "z(m)"
            self.ylabel = "Max_x Size(mm)"

            self.colors = ['r', 'r']


        elif self.picture_name == 'max_y':
            self.x = z
            self.y = [max_y, max_yy]
            self.xlabel = "z(m)"
            self.ylabel = "Max_y Size(mm)"
            self.colors = ['b', 'b']


        elif self.picture_name == 'max_xy':
            self.x = z
            self.y = [max_x, max_xx, max_y, max_yy]

            self.xlabel = "z(m)"
            self.ylabel = "Max_xy Size(mm)"

            self.labels = ['x', None, 'y', None]
            self.colors = ['r', 'r', 'b', 'b']
            self.set_legend = 1


        # elif self.picture_name == 'phi':
        #     self.x = z
        #     self.y = phi
        #
        #     self.xlabel = "z(m)"
        #     v_freq = freq/(10**6)
        #     self.ylabel = f"P(deg)({v_freq}MHz)"



        elif self.picture_name == 'energy':
            self.x = z
            self.y = ek

            self.xlabel = "z(m)"
            self.ylabel = "Ek(MeV)"

        elif self.picture_name == 'alpha_x':
            self.x = z
            self.y = alpha_x

            self.xlabel = "z(m)"
            self.ylabel = r"$\alpha_{x}$"

        elif self.picture_name == 'beta_x':
            self.x = z
            self.y = beta_x

            self.xlabel = "z(m)"
            self.ylabel = r"$\beta_{x}$" + "(mm/" + r"$\pi$ mrad)"

        elif self.picture_name == 'beta_y':
            self.x = z
            self.y = beta_y

            self.xlabel = "z(m)"
            self.ylabel = r"$\beta_{y}$" + "(mm/" + r"$\pi$ mrad)"

        elif self.picture_name == 'beta_z':
            self.x = z
            self.y = beta_z

            self.xlabel = "z(m)"
            self.ylabel = r"$\beta_{z}$" + "(mm/" + r"$\pi$ mrad)"

        elif self.picture_name == 'beta_xyz':
            self.x = z
            self.y = [beta_x, beta_y, beta_z]

            self.xlabel = "z(m)"
            self.ylabel = r"$\beta_{xyz}$" + "(mm/" + r"$\pi$ mrad)"

            self.labels = [r"$\beta_{x}$", r"$\beta_{y}$", r"$\beta_{z}$"]
            self.set_legend = 1

        self.x = get_list_interval(self.x, self.sample_interval)
        self.y = get_list_interval(self.y, self.sample_interval)
        #根据sample_interval

        #判断是否需要对y再嵌套一层
        if not isinstance(self.y[0], list):
            self.y = [self.y]
        if not isinstance(self.x[0], list):
            self.x = [self.x]

        if len(self.x) != len(self.y):
            self.x = self.x * len(self.y)

        return self.x, self.y

    def need_element(self, aper=1):

        obj_compound = CompoundShape()
        patch_list = []

        #获取lattice参数
        lattice_res = LatticeParameter(self.lattice_mulp_path)
        lattice_res.get_parameter()
        aperture = [i * 1000 for i in lattice_res.aperture]

        for i in range(len(lattice_res.v_name)):



            height = aperture[i] * 2

            element = ''
            if lattice_res.v_name[i] == "field" and lattice_res.phi_syn[i]:
                element = "cav"
            elif lattice_res.v_name[i] == "field" and not lattice_res.phi_syn[i]:
                element = "sol"

            if element:
                square_origin = [lattice_res.v_start[i], -0.5 * height]
                patch_list.append(obj_compound.create_shapes(square_origin, lattice_res.v_len[i], height, element))


        aperture_up = [i for i in aperture]
        aperture_up += [aperture_up[-1]]
        print(aperture_up)

        aperture_down = [-i for i in aperture]
        aperture_down += [aperture_down[-1]]

        aper_x = lattice_res.v_start + [lattice_res.v_start[-1] + lattice_res.v_len[-1]]
        print(aper_x)


        self.labels = self.labels + [None, None]
        self.colors += ["black", "black"]

        self.patch_list = patch_list


        # print(354, self.x )
        # print(355, self.y )

        if aper == 0:
            self.x = self.x[:-2]

            self.y = self.y[:-2]
            self.labels = self.labels[:-2]
            self.colors = self.colors[:-2]




if __name__ == "__main__":
    project_path = None
    dataset_path = r"C:\Users\wangh\Desktop\long_dis2\av_input\kongxin\DataSet.txt"
    project_path = r"C:\Users\wangh\Desktop\long_dis2\av_input"
    a = PlotDataSet(project_path=project_path,  picture_name = 'c_xy', dataset_path=dataset_path)

    a.get_x_y()
    # a.need_element(aper=1)
    a.run(show_=1)


