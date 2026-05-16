from matplotlib import pyplot as plt

from aftertreat.dataanalysis.treatplt import TreatPlt
from utils.pixel_scatter import pixel_scatter, warmup
import numpy as np
from utils.my_jet import make_tracewin_like_jet
from scipy.ndimage import gaussian_filter


from aftertreat.picture.plotphase2 import plot_dst_density


class PlotPlt():
    def __init__(self):
        self.fig_size = (12.8 *2 /3, 9.2*2 /3)
        self.fig_size = (6.4, 6)
        self.fontsize = 12
        self.gird_bins = 100

        self.picture_title_dict = {
            "x": "X(mmm)",
            "y": "Y(mmm)",
            "z": "Z(mmm)",
            "x1": "X'(mrad)",
            "y1": "Y'(mrad)",
            "z1": "Z'(mrad)",
            "phi": "Φ(deg)",
            "w": "W(MeV)",
            "w_minus_mean": "W(MeV)",
            "dp_p_100": "dp/p(%)",
        }


    def run(self, item):
        show_ = item.get("show_")
        fig =  item.get("fig")
        save_path = item.get("save_path")
        picture_type = item.get("picture_type")
        project_path = item.get("project_path")
        plt_path = item.get("plt_path")
        num = item.get("num") #要画的步数
        part_arr = item.get("part_arr")
        exist_particle = item.get("exist_particle")
        dst_dict = item.get("dst_dict")
        twiss_dict = item.get("twiss_dict")


        treat_plt_item = {
            "project_path": project_path,
            "plt_path": plt_path,
        }
        treat_plt_obj = TreatPlt(treat_plt_item)
        treat_plt_obj.get_dataset_plt_base_info()

        if not dst_dict:
            part_arr, exist_particle, dst_dict = treat_plt_obj.get_parameter_one_step(num)

        self.particle_number = len(exist_particle)

        self.mean_energy = dst_dict["energy"]

        if not picture_type:
            picture_type = [
                ["x", "x1"],
                ["y", "y1"],
                ["phi", "w"],
                ["z", "z1"],
            ]
        else:
            picture_type = picture_type

        picture_title = []
        for i in picture_type:
            v1 = []
            v1.append(self.picture_title_dict[i[0]])
            v1.append(self.picture_title_dict[i[1]])
            picture_title.append(v1)


        if not fig:
            fig, axs  = plt.subplots(2, 2, figsize=self.fig_size)

        else:
            fig.clf()  # 清空，防止重复叠加
            axs = fig.subplots(2, 2)

        font1 = {'family': 'Times New Roman', 'weight': 'bold', 'size': self.fontsize + 2}

        picture_axs_dict = {
            0: axs[0, 0],
            1: axs[0, 1],
            2: axs[1, 0],
            3: axs[1, 1],
        }

        #[x, px, y, py, z, pz, loss, index, x1, y1, z1, dp_p, phi, w, wmm]
        particle_coor = ["x", "px", "y", "py", "z", "pz", "loss", "index",
                         "x1", "y1", "z1", "dp_p", "phi", "w", "w_minus_mean"]

        for index, i  in enumerate(picture_type):
            #该可视化暂时不考虑twiss
            if twiss_dict:
                this_twiss = twiss_dict.get(tuple(i))
            else:
                this_twiss = None


            # x_coor = picture_type[index][0]  # "x"
            # y_coor = picture_type[index][1]  # "x1"
            #
            # x_coor_index = particle_coor.index(x_coor)
            # y_coor_index = particle_coor.index(y_coor)
            #
            # x_coor_data = exist_particle[:, x_coor_index]
            # y_coor_data = exist_particle[:, y_coor_index]

            x_coor_data, y_coor_data =dst_dict[picture_type[index][0]], dst_dict[picture_type[index][1]]

            plot_dst_density(
            picture_axs_dict[index]
            , x_coor_data, y_coor_data,   #数据
                picture_title[index][0], picture_title[index][1], font1, this_twiss)
        fig.text(0.01, 0.95, f'Particle Number  {self.particle_number},       Energy {self.mean_energy:.2f} MeV',
                 fontsize=14, color='black')


        # fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
        fig.subplots_adjust(
            left=0.1, right=0.92,
            bottom=0.07, top=0.88,
            wspace=0.35, hspace=0.3
        )

        # plt.tight_layout()

        if show_:
            plt.show()
            return None
        else:
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)

            plt.close(fig)  # 释放资源，防止内存堆积
            return fig  # 返回 fig 方便外部进一步处理（可选）




if __name__ == "__main__":

    # dst_path = r"F:\save\python_code\scatter\cpu_scatter_demo2\cafe1000.dst"
    # dst_path =r"C:\Users\shliu\Desktop\boun\part_dtl1.dst"


    obj = PlotPlt()

#     twiss_dict = {
#                ('x', 'x1'): [0.45984189722071056, 0.0022521969232173356, 537.8990433522753, 0.20308236242798774,
#                                  0.20308236242798774, 4.257084533623627, 4.257084533623627],
#                    ('y', 'y1'): [0.46854114674211955, 0.002272549423486523, 536.6355484227173, 0.20294352311397842,
#                                  0.20294352311397842, 3.9587416256866277, 3.9587416256866277],
#                    ('phi', 'w_minus_mean'): [-0.47430878477069255, 749.9521183628002, 0.0016333960439832438,
#                                              0.04617777600718212, 0.04617777600718212, 1.3506006118135256,
#                                              1.3506006118135256],
#                    ('x', 'y'): [-0.00037095395635608106, 0.9958525676282671, 1.004164843384848, 0.049470558419913574,
#                                 0.049470558419913574, 1.0091302180742312, 1.0091302180742312]
# }
    twiss_dict = {
        ('x', 'x1'): [-0.003096,0.001855, 537.8990433522753, 0.201845, 0.201845,
                      4.969541 , 4.969541 ],
        ('y', 'y1'): [0.46854114674211955, 0.002272549423486523, 536.6355484227173, 0.20294352311397842,
                      0.20294352311397842, 3.9587416256866277, 3.9587416256866277],
        ('phi', 'w_minus_mean'): [-0.47430878477069255, 749.9521183628002, 0.0016333960439832438,
                                  0.04617777600718212, 0.04617777600718212, 1.3506006118135256,
                                  1.3506006118135256],
        ('x', 'y'): [-0.00037095395635608106, 0.9958525676282671, 1.004164843384848, 0.049470558419913574,
                     0.049470558419913574, 1.0091302180742312, 1.0091302180742312]
    }

    item = {
        "show_": 1,
        "fig": None,
        "save_path": None,
        "picture_type":  [["x", "x1"], ["y", "y1"], ["phi", "w"], ["x", "y"]],
        "project_path": r"C:\Users\wangh\Desktop\324\v1",
        "plt_path": r"C:\Users\wangh\Desktop\324\v1\OutputFile\BeamSet.plt",
        "num": 0,
        "part_arr": None,
        "exist_particle": None,
        "dst_dict": None,
        "twiss_dict": twiss_dict,
        }

    obj.run(item)