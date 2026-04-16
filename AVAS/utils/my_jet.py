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

        tw = (1-t) * 7/10
        tt = 1- tw
        rgb = tw * white  + tt * target_rgb
        new_low[i, :3] = rgb
        new_low[i, 3] = 1.0  # alpha 固定为 1

    # 拷贝 jet 颜色，并用 new_low 覆盖前 k 个
    new_colors = jet.copy()
    new_low[0, :] = [1.0, 1.0, 1.0, 1.0]
    new_colors[:k, :] = new_low

    # new_colors[0, :] = [1.0, 1.0, 1.0, 1.0]

    # 构造新的 colormap
    return LinearSegmentedColormap.from_list("tracewin_like_jet", new_colors)