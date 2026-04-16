import matplotlib.pyplot as plt
import numpy as np
class PlotPhaseEllipse():
    def __init__(self, ):
        self.fig_size = (6.4, 4.8)
        picture_type_list = ["xx1", "yy1", "zz1", "xy","phiw"]
        self.fontsize = 14
        self.set_legend = 0

    def get_x_y(self, picture_type, parameter_item):
        if picture_type == "xx1":
            self.xlabel = "X(mm) - X'(mrad)"
        elif picture_type == "yy1":
            self.xlabel = "Y(mm) - Y'(mrad)"
        elif picture_type == "zz1":
            self.xlabel = "Z(mm) - Z'(mrad)"
        elif picture_type == "xy":
            self.xlabel = "X(mm) - Y(mrad)"
        elif picture_type == "phiw":
            self.xlabel = "Z(mm) - Z'(mrad)"

        self.alpha = parameter_item["alpha"]
        self.beta = parameter_item["beta"]
        self.rms_emit = parameter_item["rms_emit"]





    def run(self, show_, fig=None):
        alpha = self.alpha
        beta = self.beta
        gamma = (1 + alpha ** 2) / (beta+0.1)

        emit = self.rms_emit * 4**2
        # print(self.x, self.y)
        # print(fig)
        if not fig:
            fig, ax1 = plt.subplots(figsize=self.fig_size)
        else:
            ax1 = fig.add_subplot(111)


        # x = np.linspace(-2.5, 2.5, 40)
        # xp = np.linspace(-2.5, 2.5, 40)
        #
        # x, xp = np.meshgrid(x, xp)
        # ax1.contour(x, xp, gamma * x ** 2 + 2 * alpha * x * xp + beta * xp ** 2,
        #            [emit], colors='r')

        # 估算椭圆的大小范围，扩大 meshgrid 范围
        # x_max = -alpha * np.sqrt(emit/(beta + 0.1)) * 1.4
        # y_max = np.sqrt(emit * gamma) *1.4
        x_max = 2
        y_max = 4

        x = np.linspace(-x_max, x_max, 200)
        xp = np.linspace(-y_max, y_max, 200)
        x, xp = np.meshgrid(x, xp)

        ax1.contour(x, xp, gamma * x ** 2 + 2 * alpha * x * xp + beta * xp ** 2,
                    [emit], colors='r')


        # 添加标题和标签
        # plt.title('Bar Chart Example')

        ax1.set_xlabel(self.xlabel, fontsize=self.fontsize)
        # ax1.set_ylabel(self.ylabel, fontsize=self.fontsize)
        #
        # if len(self.xlim) == 2:
        #     ax1.set_xlim(self.xlim[0], self.xlim[1])
        #
        #
        # if len(self.ylim) == 2:
        #     ax1.set_ylim(self.ylim[0], self.ylim[1])


        if self.set_legend == 1:
            ax1.legend()

        #

        ax1.grid()
        if show_:
            plt.show()
            return None

        else:
            return None

if __name__ == '__main__':
    obj = PlotPhaseEllipse()

    item = {
        "alpha": -0.46109213,
        "beta": 0.38656878,
        "rms_emit": 0.2001403,
    }
    obj.get_x_y(picture_type="xx1", parameter_item=item)
    obj.run(show_=1)

