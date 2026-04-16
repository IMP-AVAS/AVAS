"""改文件定义了图像的初始类"""
import sys

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from utils.treatlist import get_dimension
import numpy as np
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import LinearSegmentedColormap
from utils.my_jet import make_tracewin_like_jet
class PicturelBar_2D():
    """
    二维柱状图，父类
    """
    def __init__(self):
        self.title = ''
        self.xlabel = ''
        self.ylabel = ''
        self.fontsize = 14
        self.x = []
        self.y = []
        self.color = 'red'



    def get_x_y(self, file_path):
        self.x = []
        self.y = []
        return self.x, self.y

    def run(self, show_, fig=None):
        if not fig:
            fig, ax1 = plt.subplots(figsize=self.fig_size)
        elif fig:
            ax1 = fig.add_subplot(111)
        # 创建柱状图
        ax1.bar(self.x, self.y, color = self.color)

        # plt.xlim(0, max(self.x) + 1)
        # plt.ylim(0, max(self.y) + 1)

        # 添加标题和标签
        # plt.title('Bar Chart Example')
        ax1.set_xlabel(self.xlabel, fontsize=self.fontsize)
        ax1.set_ylabel(self.ylabel, fontsize=self.fontsize)
        if show_:
            plt.show()
            return None

        else:
            return None



        # plt.xticks(fontsize=30)  # 设置x轴刻度标签的大小
        # plt.yticks(fontsize=30)  # 设置y轴刻度标签的大小

        # font = {'size': 15}
        # plt.legend(prop=font)
        #
        # bwith = 1.5  # 边框宽度设置为
        # TK = plt.gca()  # 获取边框
        # TK.spines['bottom'].set_linewidth(bwith)  # 图框下边
        # TK.spines['left'].set_linewidth(bwith)  # 图框左边
        # TK.spines['top'].set_linewidth(bwith)  # 图框上边
        # TK.spines['right'].set_linewidth(bwith)  # 图框右边

        # 设置小坐标的大小
        # plt.tick_params(axis='both', direction='in', labelsize=12.5)
        # plt.tick_params(which='major', width=1.5, length=6)
        # plt.tick_params(which='minor', width=1, length=3)

        # x_major_locator = MultipleLocator(0.2)
        # # 把x轴的刻度间隔设置为1，并存在变量里
        # xminorLocator = MultipleLocator(0.05)  # 将x轴次刻度标签设置为n的倍数

        # y_major_locator = MultipleLocator(20)
        # # 把y轴的刻度间隔设置为10，并存在变量里
        # y_minor_locator = MultipleLocator(5)
        # # 把y轴的刻度间隔设置为10，并存在变量里

        # ax = plt.gca()
        # # ax为两条坐标轴的实例
        # ax.xaxis.set_major_locator(x_major_locator)
        # ax.xaxis.set_minor_locator(xminorLocator)
        # # 把x轴的主刻度设置为1的倍数

        # ax.yaxis.set_major_locator(y_major_locator)
        # ax.yaxis.set_minor_locator(y_minor_locator)

        # 显示图像

class PicturePlot_2D():
    """
    二维散点图，折线图，父类
    """
    def __init__(self):
        self.title = ''
        self.xlabel = ''
        self.ylabel = ''
        self.fontsize = 14
        self.fig_size = (6.4, 4.8)
        self.x = []
        self.y = []
        self.colors = ['r', 'b', 'g']
        self.markers = [None] * 10
        self.labels = [None] * 10
        self.xlim = []
        self.ylim = []
        self.set_legend = 0
        self.patch_list=None

    def get_x_y(self):
        self.x = []
        self.y = []
        return self.x, self.y

    def run(self, show_, fig=None, save_path=None ):
        # print(self.x, self.y)
        # print(fig)
        if not fig:
            fig, ax1 = plt.subplots(figsize=self.fig_size)
        else:
            ax1 = fig.add_subplot(111)


        # 创建柱状图
        if len(self.y) == 0:
            print("The ordinate is empty")

        elif isinstance(self.y[0], list):
            if not isinstance(self.x[0], list):
                for i in range(len(self.y)):
                    ax1.plot(self.x, self.y[i], color=self.colors[i], marker=self.markers[i], label=self.labels[i])

            elif isinstance(self.x[0], list):
                for i in range(len(self.y)):
                    ax1.plot(self.x[i], self.y[i], color=self.colors[i], marker=self.markers[i], label=self.labels[i])




        elif isinstance(self.y[0], int) or isinstance(self.y[0], float):
            ax1.plot(self.x, self.y, color=self.colors[0], marker=self.markers[0])


        # 添加标题和标签
        # plt.title('Bar Chart Example')

        ax1.set_xlabel(self.xlabel, fontsize=self.fontsize)
        ax1.set_ylabel(self.ylabel, fontsize=self.fontsize)

        if len(self.xlim) == 2:
            ax1.set_xlim(self.xlim[0], self.xlim[1])


        if len(self.ylim) == 2:
            ax1.set_ylim(self.ylim[0], self.ylim[1])



        if self.set_legend == 1:
            ax1.legend()


        if self.patch_list:
            for shapes in self.patch_list:
                for shape in shapes:
                    ax1.add_patch(shape)

        ax1.ticklabel_format(style='plain', axis='y', useOffset=False)
        # ax1.set_ylim(0, 200)
        # ax1.grid()
        if show_:
            plt.show()
            return None
        else:
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)
            plt.close(fig)  # 释放资源，防止内存堆积
            return fig  # 返回 fig 方便外部进一步处理（可选）


class CompoundShape():
    def __init__(self, ):
        pass

    def create_shapes(self, square_origin, length, height, element):
        facecolor = ""
        if element == "sol":
            facecolor = "lime"
        elif element == "cav":
            facecolor = "yellow"

        shapes = []

        # 创建正方形
        square = patches.Rectangle(square_origin, length, height, linewidth=1, edgecolor="black", facecolor=facecolor)

        shapes.append(square)
        ratio = 0.9
        points_inside_square_1 = [
            (square_origin[0], square_origin[1] + ratio * height),
            (square_origin[0] + 1 / 3 * length, square_origin[1] + (1 - ratio) * height),
            (square_origin[0] + 2 / 3 * length, square_origin[1] + ratio * height),
            (square_origin[0] + 1 * length, square_origin[1] + (1 - ratio) * height),

        ]

        curve_codes_1 = [Path.MOVETO] + [Path.LINETO] * 3
        curve_path_1 = Path(points_inside_square_1, curve_codes_1)

        # 创建曲线
        curve_patch_1 = patches.PathPatch(curve_path_1, linewidth=0.5, facecolor='none')
        shapes.append(curve_patch_1)

        points_inside_square_2 = [
            (square_origin[0], square_origin[1] + (1 - ratio) * height),
            (square_origin[0] + 1 / 3 * length, square_origin[1] + ratio * height),
            (square_origin[0] + 2 / 3 * length, square_origin[1] + (1 - ratio) * height),
            (square_origin[0] + 1 * length, square_origin[1] + ratio * height),

        ]

        curve_codes_2 = [Path.MOVETO] + [Path.LINETO] * 3
        curve_path_2 = Path(points_inside_square_2, curve_codes_2)

        # 创建曲线
        curve_patch_2 = patches.PathPatch(curve_path_2, linewidth=0.5, facecolor='none')
        shapes.append(curve_patch_2)

        # 创建圆形

        return shapes

class PicturePlot_2ax():
    def __init__(self):
        self.title = ''
        self.xlabel = ''
        self.ylabel1 = ''
        self.ylabel2 = ''
        self.fontsize = 14
        self.fig_size = (7, 4.8)
        self.x = []
        self.y = []
        self.colors = ['r', 'b', 'g']
        self.markers = [None] * 10

        self.labels1 = [None] * 10
        self.labels2 = [None] * 10

        self.xlim = []
        self.ylim = []
        self.set_legend = 0
        self.xy = {}

    def get_x_y(self):
        self.xy = {"ax1_x": [],
                     "ax1_y": [],
                     "ax2_x": [],
                     "ax2_y": [],
                     }
        return self.xy

    def run(self, show_, fig=None, save_path=None):
        if not fig:
            fig, ax1 = plt.subplots(figsize=self.fig_size)
        elif fig:
            ax1 = fig.add_subplot(111)


        lines1 = []
        #处理第一个坐标轴
        if True:
            for i in range(len(self.xy['ax1_x'])):
                line, = ax1.plot(self.xy['ax1_x'][i], self.xy['ax1_y'][i], label=self.labels1[i], color=self.colors1[i])
                lines1.append(line)
            ax1.set_xlabel(self.xlabel)
            ax1.set_ylabel(self.ylabel1, color='b')

        lines2 = []
        ax2 = ax1.twinx()
        # 创建第二个坐标轴，共享相同的x轴
        if True:
            for i in range(len(self.xy['ax2_x'])):
                line, = ax2.plot(self.xy['ax2_x'][i], self.xy['ax2_y'][i], label=self.labels2[i], color=self.colors2[i])
                lines1.append(line)

            ax2.set_ylabel(self.ylabel2, color='b')



        if self.set_legend == 1:
            lines = lines1 + lines2
            labels = [line.get_label() for line in lines]

        # 在图表外部显示图例，防止遮挡
        ax1.legend(lines, labels, loc='upper left')

        plt.subplots_adjust(left=0.1, right=0.85, top=0.9, bottom=0.1)

        x_major_locator = MultipleLocator(1)
        # 把x轴的刻度间隔设置为1，并存在变量里
        ax1.xaxis.set_major_locator(x_major_locator)

        ax1.ticklabel_format(style='plain', axis='y', useOffset=False)
        if show_:
            plt.show()
            return None
        else:
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)
            plt.close(fig)  # 释放资源，防止内存堆积
            return fig  # 返回 fig 方便外部进一步处理（可选）

class Picturedensity():
    """
    二维散点图，折线图，父类
    """
    def __init__(self):
        self.title = ''
        self.xlabel = ''
        self.ylabel = ''
        self.fontsize = 14
        self.fig_size = (6.4, 4.8)
        self.x = []
        self.y = []
        self.colors = ['r', 'b', 'g']
        self.markers = [None] * 10
        self.labels = [None] * 10
        self.xlim = []
        self.ylim = []
        self.set_legend = 0
        self.patch_list=None

    def get_data(self):
        self.z = []
        self.y = []
        self.density = []
        self.z_m = []
        self.y_m = []
        self.density_m = []
        return self.z, self.y, self.density

    def run(self, show_, fig, save_path=None):
        # print(self.z, self.y)
        # print(fig)
        # print(self.density)
        if not fig:
            fig, ax1 = plt.subplots(figsize=self.fig_size)
        elif fig:
            ax1 = fig.add_subplot(111)


        colors = [(1, 1, 1), *plt.cm.jet(np.linspace(0, 1, 256))]  # 第一个颜色为白色，其余为 'jet'
        custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors)
        # tracewin_like_jet = make_tracewin_like_jet()

        # 使用pcolormesh绘制密度图
        mesh = ax1.pcolormesh(self.z_m, self.y_m,self.density_m, cmap=custom_cmap, shading='auto')

        # 为图像添加颜色条，并设置标签
        colorbar = fig.colorbar(mesh, ax=ax1)
        colorbar.set_label('Density')  # 设置颜色条标签

        # 添加标题和标签
        # plt.title('Bar Chart Example')

        ax1.set_xlabel(self.xlabel, fontsize=self.fontsize)
        ax1.set_ylabel(self.ylabel, fontsize=self.fontsize)

        if len(self.xlim) == 2:
            ax1.set_xlim(self.xlim[0], self.xlim[1])


        if len(self.ylim) == 2:
            ax1.set_ylim(self.ylim[0], self.ylim[1])

        if self.set_legend == 1:
            ax1.legend()

        ax1.grid()

        if show_:
            plt.show()
            return None
        else:
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)
            plt.close(fig)  # 释放资源，防止内存堆积
            return fig  # 返回 fig 方便外部进一步处理（可选）

# if __name__ == "__main__":
#     v = PicturelBar_2D()
#     v.run()