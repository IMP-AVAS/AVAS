"""此文件为画相图"""
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import struct
from scipy.stats import gaussian_kde
from utils.readfile import read_dst_fast
from sklearn.neighbors import KernelDensity
import global_varible
import time
# matplotlib.use("TkAgg")
from utils.griddensity import grid_density
from matplotlib.colors import LinearSegmentedColormap
import time
import matplotlib.style as mplstyle
mplstyle.use('fast')


class PlotPhase:
    def __init__(self, dst_path):
        self.dst_path = dst_path
        self.fig_size = (12.8, 9.2)
        self.fontsize = 18
        self.gird_bins = 100
        self.maxpar_num = 10**4
    def run(self, show_, fig=None, save_path=None):
        t0 = time.time()
        res = read_dst_fast(self.dst_path)

        partran_dist = np.array(res['partran_dist'])
        for i in partran_dist:
            print(i)
        # 限制最大点数以提高效率
        # if len(partran_dist) >= self.maxpar_num:
        #     indices = np.random.choice(len(partran_dist),  self.maxpar_num, replace=False)
        #     partran_dist = partran_dist[indices]

        x = partran_dist[:, 0] * 10
        x1 = partran_dist[:, 1] * 1000
        y = partran_dist[:, 2] * 10
        y1 = partran_dist[:, 3] * 1000
        phi = partran_dist[:, 4] * 180 / global_varible.Pi
        print(phi)
        E = partran_dist[:, 5]
        E -= np.mean(E)


        # if not fig:
        #     fig, axs = plt.subplots(4, 3, figsize=(7, 7))  # 4行3列的子图布局
        # plt.subplots_adjust(wspace=0.1, hspace=0.3)
        # font1 = {'family': 'Times New Roman', 'weight': 'bold', 'size': fontsize}
        #
        # self._plot_density(axs[0, 0], res_fft["x"], res_fft["x1"], "x(mm)", "x'(mrad)", font1, "a")
        # self._plot_density(axs[0, 1], res_fft["y"], res_fft["y1"], "y(mm)", "y'(mrad)", font1, "b")
        # self._plot_density(axs[0, 2], res_fft["phi"], res_fft["E"], "φ(deg)", "Energy(MeV)", font1, "c")


        if not fig:
            fig = plt.figure(figsize=self.fig_size)

        font1 = {'family': 'Times New Roman', 'weight': 'bold', 'size': self.fontsize}

        # 绘制子图
        self._plot_density(fig, 221, x, x1, "x(mm)", "x'(mrad)", font1)
        self._plot_density(fig, 222, y, y1, "y(mm)", "y'(mrad)", font1)
        self._plot_density(fig, 223, phi, E, "φ(deg)", "Energy(MeV)", font1)
        self._plot_density(fig, 224, x, y, "x(mm)", "y(mm)", font1)
        t1 = time.time()
        print(t1-t0)
        if show_:
            plt.show()
            t2 =time.time()

            return None
        else:
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)
            plt.close(fig)  # 释放资源，防止内存堆积
            return fig  # 返回 fig 方便外部进一步处理（可选）

    # def _plot_density(self, fig, position, x, y, xlabel, ylabel, font):
    #     ax = fig.add_subplot(position)
    #     xy = np.vstack([x, y]).T
    #     # if xlabel == "φ(deg)":
    #     #     bd = np.max(y)/100
    #     #     kde = KernelDensity(kernel='tophat', bandwidth=bd).fit(xy)
    #     # else:
    #     kde = KernelDensity(kernel='gaussian', bandwidth="scott").fit(xy)
    #     # kde = KernelDensity(kernel='gaussian', bandwidth='scott').fit(xy)
    #
    #     log_density = kde.score_samples(xy)
    #     z = np.exp(log_density)
    #     z /= max(z)  # 归一化
    #
    #     scatter = ax.scatter(x, y, c=z, s=1.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    #     fig.colorbar(scatter, ax=ax)
    #     ax.set_xlabel(xlabel, fontdict=font)
    #     ax.set_ylabel(ylabel, fontdict=font)
    #     ax.grid(linestyle="--")
    def _plot_density(self, fig, position, x, y, xlabel, ylabel, font):
        t0 = time.time()
        ax = fig.add_subplot(position)

        # 设置网格数，比如 100x100，可调整
        # 计算 2D 直方图
        z = grid_density(x, y, self.gird_bins, norm=True)
        # 画密度图
        colors = [(1, 1, 1), *plt.cm.jet(np.linspace(0, 1, 256))]  # 第一个颜色为白色，其余为 'jet'
        custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors)

        tracewin_jet = make_tracewin_like_jet()

        scatter = ax.scatter(x, y, c=z, s=1.0, cmap=custom_cmap, vmin=0, vmax=1.0)
        fig.colorbar(scatter, ax=ax)
        ax.set_xlabel(xlabel, fontdict=font)
        ax.set_ylabel(ylabel, fontdict=font)

        ax.tick_params(axis='x', labelsize=14)  # x 轴刻度字体大小
        ax.tick_params(axis='y', labelsize=14)

        ax.grid(linestyle="--")


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


def make_tracewin_like_jet(low_frac=0.1, N=256):
    """
    在 jet 的低端加一段“白 -> jet(low_frac)”的渐变，
    其余部分保持原始 jet。

    low_frac: 0~1，颜色条底部多少比例做提亮
    N:        colormap 采样数
    """
    # 采样原始 jet
    base_x = np.linspace(0.0, 1.0, N)
    jet = plt.cm.jet(base_x)  # (N, 4) RGBA，已经是 numpy 数组

    # 需要替换的低端长度（索引数）
    k = max(2, int(low_frac * N))  # 至少 2，避免除零

    # 找到 low_frac 对应的 jet 颜色
    target_rgba = plt.cm.jet(low_frac)  # 这是个 tuple 或 array
    target_rgb = np.asarray(target_rgba[:3], dtype=np.float64)

    # 白色
    white = np.array([1.0, 1.0, 1.0], dtype=np.float64)

    # 构造从 white -> target_rgb 的渐变
    new_low = np.zeros((k, 4), dtype=np.float64)
    for i in range(k):
        t = i / (k - 1)  # 0 ~ 1
        rgb = (1.0 - t) * white + t * target_rgb
        new_low[i, :3] = rgb
        new_low[i, 3] = 1.0  # alpha 固定为 1

    # 拷贝 jet 颜色，并用 new_low 覆盖前 k 个
    new_colors = jet.copy()
    new_colors[:k, :] = new_low

    # 构造新的 colormap
    return LinearSegmentedColormap.from_list("tracewin_like_jet", new_colors)

if __name__ == "__main__":
    import time
    t0 = time.time()
    dst_path = r"C:\Users\wangh\Desktop\test_energy\danengsan_p10_3\avas_p10_sol_2\OutputFile\outData_1.650000.dst"
    # dst_path =r"C:\Users\shliu\Desktop\boun\part_dtl1.dst"
    plot_phase = PlotPhase(dst_path)

    plot_phase.run(show_=True)
    t1 = time.time()
    print(t1-t0)
