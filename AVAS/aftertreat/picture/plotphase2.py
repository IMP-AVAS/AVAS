"""此文件为画相图"""
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

import time

import matplotlib as mpl
from scipy.ndimage import gaussian_filter
from utils.my_jet import make_tracewin_like_jet

from dataprovision.beamparameter import DstParameter

from utils.pixel_scatter import pixel_scatter, warmup
import logging
from logger.logger_config import setup_logger
from conf.contants import dst_picture_title_dict
import sys
logger = logging.getLogger(__name__)

def plot_dst_density(ax, x, y, xlabel, ylabel, font, this_twiss):
    tick_font = 12
    # 1) 保留原始散点数据，别让后面被覆盖

    x_data = np.asarray(x)
    y_data = np.asarray(y)
    tracewin_like_jet = make_tracewin_like_jet(low_frac=0.1, N=256)

    xmin, xmax = float(x_data.min()), float(x_data.max())
    ymin, ymax = float(y_data.min()), float(y_data.max())
    extent =[xmin,  xmax, ymin,ymax]

    W, H = 400, 300
    block_num = 4



    pn = len(x_data)
    if pn <= 10 * 10:
        this_sigma = 1
    elif pn <= 10 * 10 ** 4:
        this_sigma = 0.7
    elif pn <= 100 * 10 ** 4:
        this_sigma = 0.5
    elif pn <= 1000 * 10 ** 4:
        this_sigma = 0.3
    else:
        this_sigma = 0.1


    density_img = pixel_scatter(x_data, y_data, xmin, xmax, ymin, ymax, W, H, block_num, 0.0)
    density_img = gaussian_filter(density_img, sigma=this_sigma)
    max_density = density_img.max()
    scalar_img = density_img / max_density if max_density > 0 else density_img
    np.set_printoptions(threshold=np.inf)


    im = ax.imshow(
        scalar_img,
        extent=extent,
        origin='lower',
        aspect='auto',
        cmap=tracewin_like_jet,
        vmin=0.0, vmax=1.0,
        interpolation="nearest",  # 可选：防止imshow插值导致“糊/怪”
    )

    # 颜色条建议直接绑 im（更直观）
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    if this_twiss:
    # 2) 画相椭圆：千万别再用 x 这个变量名

        alpha = this_twiss[0]
        beta = this_twiss[1]
        emit = this_twiss[9]
        if beta != 0:
            theta = np.linspace(0, 2 * np.pi, 800)
            xe = np.sqrt(emit * beta) * np.cos(theta)
            xpe = -np.sqrt(emit / beta) * (alpha * np.cos(theta) + np.sin(theta))
            ax.plot(xe, xpe, 'r')
        else:
            print("error beta = 0")
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
                x_data, y_data,  # 3) 这里必须用原始散点
                float(cur_xmin), float(cur_xmax),
                float(cur_ymin), float(cur_ymax),
                W, H, block_num, 0.0
            )

            x_span = abs(cur_xmax - cur_xmin)

            full_x_span = float(x_data.max() - x_data.min())
            zoom_ratio = x_span / full_x_span

            pn2 = zoom_ratio * pn

            if pn2 <= 10 * 10:
                this_sigma2 = 1
            elif pn2 <= 10 * 10 ** 4:
                this_sigma2 = 0.7
            elif pn2 <= 100 * 10 ** 4:
                this_sigma2 = 0.5
            elif pn2 <= 1000 * 10 ** 4:
                this_sigma2 = 0.3
            else:
                this_sigma2 = 0.1

            new_img = gaussian_filter(new_img, sigma=this_sigma2)
            m = new_img.max()
            if m > 0:
                new_img = new_img / m

            im.set_data(new_img)


            im.set_extent([cur_xmin, cur_xmax, cur_ymin, cur_ymax])
            ax_.figure.canvas.draw_idle()
        finally:
            _updating = False

    ax.callbacks.connect("xlim_changed", _redraw)
    ax.callbacks.connect("ylim_changed", _redraw)

    increase_ratio = 1.2
    decrease_ratio = 0.8

    def adjust_lower_bound(val, increase_ratio, decrease_ratio):
        if val > 0:
            return val * decrease_ratio
        elif val < 0:
            return val * increase_ratio
        return val

    def adjust_upper_bound(val, increase_ratio, decrease_ratio):
        if val > 0:
            return val * increase_ratio
        elif val < 0:
            return val * decrease_ratio
        return val

    new_xmin = adjust_lower_bound(xmin, increase_ratio, decrease_ratio)
    new_xmax = adjust_upper_bound(xmax, increase_ratio, decrease_ratio)
    new_ymin = adjust_lower_bound(ymin, increase_ratio, decrease_ratio)
    new_ymax = adjust_upper_bound(ymax, increase_ratio, decrease_ratio)

    ax.set_xlim(new_xmin, new_xmax)
    ax.set_ylim(new_ymin, new_ymax)

    ax.tick_params(axis='x', labelsize=tick_font)
    ax.tick_params(axis='y', labelsize=tick_font)
    ax.grid(linestyle="--")
    ax.set_title(f"{xlabel} - {ylabel}", fontdict=font)



class PlotPhase2:
    def __init__(self, ):
        self.fig_size = (12.8 *2 /3, 9.2*2 /3)
        self.fig_size = (6.4, 6)
        self.fontsize = 12
        self.gird_bins = 100
        self.maxpar_num = 10**4

        self.dst_picture_title_dict = dst_picture_title_dict

    def run(self, item):

        # item = {
        #     "show_": show_,
        #     "fig":,
        #     "save_path":save_path,
        #     "picture_type": ,
        #      "dst_path": ,
        #      "dst_dict": ,
        # }
        show_ = item.get("show_")
        fig =  item.get("fig")
        save_path = item.get("save_path")
        picture_type = item.get("picture_type")
        dst_path = item.get("dst_path")
        dst_dict = item.get("dst_dict")
        twiss_dict = item.get("twiss_dict")

        if dst_path:
            dst_obj = DstParameter(dst_path)
            dst_dict = dst_obj.get_parameter()

        energy = dst_dict["energy"]

        t0 = time.time()
        warmup()
        t1 = time.time()
        # print("warmup时间：", t1- t0)

        particle_number = len(dst_dict["x"])
        self.particle_number = particle_number

        if not picture_type:
            picture_type = [
                ["x", "x1"],
                ["y", "y1"],
                ["phi", "w"],
                ["z", "z1"],
            ]
        else:
            picture_type = picture_type
        # logger.info(f"picture_type: {picture_type}")
        #创建标题
        picture_title = []

        for i in picture_type:
            v1 = []
            v1.append(self.dst_picture_title_dict[i[0]])
            v1.append(self.dst_picture_title_dict[i[1]])
            picture_title.append(v1)
        # print(picture_title)
        # logger.info(f"picture_title: {picture_title}")

        t2 = time.time()
        # print("计算时间", t2-t1)
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
            if twiss_dict:
                this_twiss = twiss_dict.get(tuple(i))
            else:
                this_twiss = None


            plot_dst_density(
            picture_axs_dict[index]
            , dst_dict[picture_type[index][0]], dst_dict[picture_type[index][1]],
                picture_title[index][0], picture_title[index][1], font1, this_twiss)




        fig.text(0.01, 0.95, f'Particle Number  {particle_number},       Energy {energy:.2f} MeV',
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





if __name__ == "__main__":
    setup_logger(
        level=logging.INFO,
    )

    logger.info('hello world')
    t0 = time.time()
    # dst_path = r"F:\save\python_code\scatter\cpu_scatter_demo2\cafe1000.dst"
    # dst_path =r"C:\Users\shliu\Desktop\boun\part_dtl1.dst"
    dst_path = r"C:\Users\wangh\Desktop\324\v1\OutputFile\inData.dst"

    plot_phase = PlotPhase2()

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
        "picture_type":  [["x", "x1"], ["y", "y1"],
                          ["phi", "w_minus_mean"], ["z", "dp_p"]],
        "dst_path": dst_path,
        "dst_dict": None,
        "twiss_dict": twiss_dict
        }




    # alpha_percent,
    # beta_percent,
    # gamma_percent,
    # rms_epsilon_percent,  # 你原来写成 rms_epsilon_perent，这里统一成 percent
    # rms_epsilon_100,
    # all_epsilon_100,
    # all_epsilon_percent
    plot_phase.run(item)

    t1 =time.time()
    print(t1- t0)