from matplotlib import pyplot as plt

from aftertreat.dataanalysis.treatplt import TreatPlt



from aftertreat.picture.plotphase2 import plot_dst_density
from dataprovision.edst_beamparameter import EdstParameter
from conf.contants import edst_picture_title_dict, edst_picture_type_key_dict

tick_font = 12
def plot_edst_picture(item):
    ax = item.get("ax")
    picture_type_x = item.get("picture_type_x")  # x
    picture_type_y = item.get("picture_type_y")  # x1
    picture_title_x = item.get("picture_title_x")  # X(mm)
    picture_title_y = item.get("picture_title_y")  # Y(mm)
    edst_dict = item.get("edst_dict")

    font1 = item.get("fon1")

    # 获取x的key
    beam1_x_key =edst_picture_type_key_dict[picture_type_x][0]  # b1_x
    beam2_x_key =edst_picture_type_key_dict[picture_type_x][1]  # b2_x

    # 获取y的key
    beam1_y_key = edst_picture_type_key_dict[picture_type_y][0]  # b1_y
    beam2_y_key = edst_picture_type_key_dict[picture_type_y][1]  # b2_y

    print(
        beam1_x_key, beam2_x_key, beam1_y_key, beam2_y_key)

    data_x_1 = edst_dict[beam1_x_key]
    data_x_2 = edst_dict[beam2_x_key]
    print(32, len(data_x_1), len(data_x_2))

    data_y_1 = edst_dict[beam1_y_key]
    data_y_2 = edst_dict[beam2_y_key]
    print(36, len(data_y_1), len(data_y_2))


    ax.scatter(data_x_1, data_y_1, c="darkred", marker="o", label="Beam1", s=2)
    ax.scatter(data_x_2, data_y_2, c="steelblue", marker="o", label="Beam2", s=2)

    ax.tick_params(axis='x', labelsize=tick_font)
    ax.tick_params(axis='y', labelsize=tick_font)
    ax.grid(linestyle="--")
    ax.set_title(f"{picture_title_x} - {picture_title_y}", fontdict=font1)

class Plotedst():
    def __init__(self):
        self.fig_size = (12.8 *2 /3, 9.2*2 /3)
        self.fig_size = (6.4, 6)
        self.fontsize = 12
        self.gird_bins = 100


    def run(self, item):
        show_ = item.get("show_")
        fig =  item.get("fig")
        save_path = item.get("save_path")
        picture_type = item.get("picture_type")
        edst_path = item.get("edst_path")
        edst_dict = item.get("edst_dict")



        if not edst_dict:
            item = {"edst_path":edst_path}
            edst_obj = EdstParameter(item)
            edst_dict = edst_obj.get_parameter()

        if not picture_type:
            picture_type = [
                ["x", "x1"],
                ["y", "y1"],
                ["phi", "w"],
                ["phi", "y"],
            ]
        else:
            picture_type = picture_type

        picture_title = []
        for i in picture_type:
            v1 = []
            v1.append(edst_picture_title_dict[i[0]])
            v1.append(edst_picture_title_dict[i[1]])
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



        for index, i  in enumerate(picture_type):
            item = {
                "ax":picture_axs_dict[index],
                "picture_type_x": picture_type[index][0], # x
                "picture_type_y": picture_type[index][1],  # x1
                "picture_title_x": picture_title[index][0],  # X(mm)
                "picture_title_y": picture_title[index][1],  # Y(mm)
                "font1": font1,
                "edst_dict": edst_dict,
            }
            plot_edst_picture(item)

        particle_1_cm = edst_dict["unique_mass_charge"][0]   #电荷质量
        particle_2_cm = edst_dict["unique_mass_charge"][1]

        fig.text(
            0.01, 0.92,
            f'Particle 1: charge {particle_1_cm[0]:.0f} mass {particle_1_cm[1]:.3f} number {edst_dict["number_1"]} red\n'
            f'Particle 2: charge {particle_2_cm[0]:.0f} mass {particle_2_cm[1]:.3f} number {edst_dict["number_2"]} blue',
            fontsize=11,
            color='black'
        )

        # fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.9])
        fig.subplots_adjust(
            left=0.1, right=0.92,
            bottom=0.07, top=0.85,
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


    obj = Plotedst()
    edst_path = r"C:\Users\wangh\Desktop\test_xiao\OutputFile\outData_2.022640.edst"


    item = {
        "show_": 1,
        "fig": None,
        "save_path": None,
        "picture_type":  [["x", "x1"], ["y", "y1"], ["phi", "w"], ["phi", "y"]],
        "edst_path": edst_path,
        "edst_dict": None,
        }

    obj.run(item)