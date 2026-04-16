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
import matplotlib as mpl
from scipy.ndimage import gaussian_filter

from utils.pixel_scatter import pixel_scatter, warmup
class PlotPhase:
    def __init__(self, dst_path):
        self.dst_path = dst_path
        self.fig_size = (12.8 *2 /3, 9.2*2 /3)
        self.fontsize = 18
        self.gird_bins = 100
        self.maxpar_num = 10**4
    def run(self, show_, fig=None, save_path=None):
        t00 = time.time()
        warmup()
        t01 = time.time()
        print("warmup时间：", t01- t00)
        t0 = time.time()
        res = read_dst_fast(self.dst_path)
        t1 = time.time()
        print("读文件时间", t1-t0)

        partran_dist = np.array(res['partran_dist'])
        E_mean = res["kneticenergy"]
        # 限制最大点数以提高效率
        # if len(partran_dist) >= self.maxpar_num:
        #     indices = np.random.choice(len(partran_dist),  self.maxpar_num, replace=False)
        #     partran_dist = partran_dist[indices]
        t0_v1 = time.time()

        # x = partran_dist[:, 0]
        # x1 = partran_dist[:, 1]
        # y = partran_dist[:, 2]
        # y1 = partran_dist[:, 3]
        # phi = partran_dist[:, 4]
        # E = partran_dist[:, 5]


        x = partran_dist[:, 0] * 10
        x1 = partran_dist[:, 1] * 1000
        y = partran_dist[:, 2] * 10
        y1 = partran_dist[:, 3] * 1000
        phi = partran_dist[:, 4] * 180 / global_varible.Pi
        E = partran_dist[:, 5] - E_mean

        t1_v1 = time.time()
        print("计算时间", t1_v1-t0_v1)
        if not fig:
            fig = plt.figure(figsize=self.fig_size)

        # plt.scatter(x,x1)
        # plt.show()
        # import sys
        # sys.exit()

        font1 = {'family': 'Times New Roman', 'weight': 'bold', 'size': self.fontsize}

        # 绘制子图
        self._plot_density(fig, 221, x, x1, "x", "x'", font1)
        self._plot_density(fig, 222, y, y1, "y", "y'", font1)
        self._plot_density(fig, 223, phi, E, "φ", "Energy", font1)
        self._plot_density(fig, 224, x, y, "x", "y", font1)

        plt.tight_layout()
        if show_:

            plt.show()
            t2 =time.time()

            return None
        else:
            t4 = time.time()
            if save_path:  # 如果指定了保存路径，就保存图像
                fig.savefig(save_path)
            t5 = time.time()
            print("保存图片的时间", t5 - t4)
            plt.close(fig)  # 释放资源，防止内存堆积
            return fig  # 返回 fig 方便外部进一步处理（可选）


    def _plot_density(self, fig, position, x, y, xlabel, ylabel, font):

        ax = fig.add_subplot(position)

        colors = [(1, 1, 1), *plt.cm.jet(np.linspace(0, 1, 256))]  # 第一个颜色为白色，其余为 'jet'
        custom_cmap = LinearSegmentedColormap.from_list('custom_jet', colors)

        tracewin_like_jet = make_tracewin_like_jet()

        xmin, xmax = float(x.min()), float(x.max())
        ymin, ymax = float(y.min()), float(y.max())

        W, H = 400, 300


        t0 = time.time()
        density_img = pixel_scatter(x, y,  xmin, xmax, ymin, ymax, W, H, 0.0)
        t1 = time.time()
        print("生成img的时间", t1-t0)

        # density_img = gaussian_filter(density_img, sigma=0.2)
        # print(density_img)
        max_density = density_img.max()

        if max_density > 0:
            scalar_img = density_img / max_density
            vmin, vmax = 0.0, 1.0
        else:
            scalar_img = density_img
            vmin, vmax = 0.0, 1.0
        # print(scalar_img)
        t2 = time.time()


        im = ax.imshow(scalar_img, extent=[xmin, xmax, ymin, ymax],
                       origin='lower', aspect='auto',
                       cmap= tracewin_like_jet, vmin=vmin, vmax=vmax)

        ratio = 0.4
        ax.set_xlim([xmin - abs(xmin) * ratio, xmax + abs(xmax) * ratio])
        ax.set_ylim([ymin - abs(ymin) * ratio, ymax + abs(ymax) * ratio])
        norm = mpl.colors.Normalize(vmin=0.0, vmax=1.0)
        sm = mpl.cm.ScalarMappable(norm=norm, cmap=tracewin_like_jet)
        sm.set_array([])  # 必须调用，否则警告
        fig.colorbar(sm, ax=ax)
        t3 = time.time()
        print("imshow的时间", t3 - t2)
        _updating = False

        def _redraw(ax_):
            nonlocal _updating
            if _updating:
                return
            _updating = True
            try:
                cur_xmin, cur_xmax = ax_.get_xlim()
                cur_ymin, cur_ymax = ax_.get_ylim()

                new_img = pixel_scatter(
                    x, y,
                    float(cur_xmin), float(cur_xmax),
                    float(cur_ymin), float(cur_ymax),
                    W, H, 0.0
                )

                # new_img = gaussian_filter(new_img, sigma=1.5)
                max_density = new_img.max()
                # print(max_density)
                if max_density > 0:
                    new_img = new_img / max_density  # 保持 0~1 归一化
                im.set_data(new_img)
                im.set_extent([cur_xmin, cur_xmax, cur_ymin, cur_ymax])
                fig.canvas.draw_idle()
            finally:
                _updating = False

        ax.callbacks.connect("xlim_changed", _redraw)
        ax.callbacks.connect("ylim_changed", _redraw)



        ax.tick_params(axis='x', labelsize=14)  # x 轴刻度字体大小
        ax.tick_params(axis='y', labelsize=14)

        ax.grid(linestyle="--")
        ax.set_xlabel(xlabel, fontdict=font)
        ax.set_ylabel(ylabel, fontdict=font)

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
    t0 = time.time()
    # dst_path = r"F:\save\python_code\scatter\cpu_scatter_demo2\cafe1000.dst"
    # dst_path =r"C:\Users\shliu\Desktop\boun\part_dtl1.dst"
    dst_path = r"C:\Users\wangh\Desktop\part_rfq_1e6.dst"
    plot_phase = PlotPhase(dst_path)

    # plot_phase.run(show_=False, save_path = "test1.png")
    plot_phase.run(show_=True)

    t1 =time.time()
    print(t1- t0)