from numba import njit, prange
import numpy as np

# @njit(parallel=True)
# def pixel_scatter(x, y, xmin, xmax, ymin, ymax, W, H, fill_value):
#
#     img = np.full((H, W), fill_value, dtype=np.float32)
#
#
#     dx = xmax - xmin
#     dy = ymax - ymin
#
#     for k in prange(len(x)):
#         X = x[k]
#         Y = y[k]
#
#         if X < xmin or X > xmax or Y < ymin or Y > ymax:
#             continue
#
#         i = int((X - xmin) / dx * (W - 1))
#         j = int((1 - (Y - ymin) / dy) * (H - 1))
#         # print(i, j)
#         if 0 <= i < W and 0 <= j < H:
#             img[j, i] += 1
#
#     return img

# import numpy as np
#
# def pixel_scatter(x, y, xmin, xmax, ymin, ymax, W, H, fill_value=0.0):
#     img = np.full((H, W), fill_value, dtype=np.float32)
#
#     dx = xmax - xmin
#     dy = ymax - ymin
#
#     for k in range(len(x)):
#         X, Y = x[k], y[k]
#         if not (xmin <= X <= xmax and ymin <= Y <= ymax):
#             continue
#         i = int((X - xmin) / dx * (W - 1))
#         j = int((1 - (Y - ymin) / dy) * (H - 1))
#         if 0 <= i < W and 0 <= j < H:
#             img[j, i] += 1
#
#     return img
#
#
# def block_density(n1, block_h, block_w):
#     H, W = n1.shape
#     # 计算块的数量
#     h_blocks = H // block_h + (1 if H % block_h else 0)
#     w_blocks = W // block_w + (1 if W % block_w else 0)
#
#     # 用于存储块统计
#     n2_small = np.zeros((h_blocks, w_blocks), dtype=np.float32)
#
#     for bh in range(h_blocks):
#         for bw in range(w_blocks):
#             # 计算该块的实际像素范围
#             j1 = bh * block_h
#             j2 = min((bh + 1) * block_h, H)
#             i1 = bw * block_w
#             i2 = min((bw + 1) * block_w, W)
#
#             n2_small[bh, bw] = np.sum(n1[j1:j2, i1:i2])
#
#     # 将块数据 broadcast 到 n1 形状，形成对应大小的 n2
#     n2 = np.zeros_like(n1)
#     for bh in range(h_blocks):
#         for bw in range(w_blocks):
#             j1 = bh * block_h
#             j2 = min((bh + 1) * block_h, H)
#             i1 = bw * block_w
#             i2 = min((bw + 1) * block_w, W)
#             n2[j1:j2, i1:i2] = n2_small[bh, bw]
#
#     return n2
#
#
# def replace_nonzero_with_block(n1, n2):
#     result = n1.copy()
#     mask = (n1 > 0)
#     result[mask] = n2[mask]
#     return result

# import numpy as np
# from numba import njit, prange
#


@njit(parallel=True, cache=True)
def pixel_scatter(x, y,
                  xmin, xmax, ymin, ymax,
                  W, H,  block_num,
                  fill_value):

    # 1. 像素级统计
    n1 = np.full((H, W), fill_value, dtype=np.float32)

    dx = xmax - xmin
    dy = ymax - ymin

    N = x.shape[0]

    # 块大小（可以根据需要改）

    block_h = block_num
    block_w = block_num

    # 块的数量
    h_blocks = H // block_h
    if H % block_h != 0:
        h_blocks += 1

    w_blocks = W // block_w
    if W % block_w != 0:
        w_blocks += 1

    # 每个块的粒子总数
    n2_small = np.zeros((h_blocks, w_blocks), dtype=np.float32)

    # ========= 1 + 2：在同一轮循环里统计 n1 和 n2_small =========

    # n1：每个像素格里有多少点
    # n2：每个大块block里有多少点，然后把这个块值铺回这个块覆盖的所有像素
    for k in prange(N):
        X = x[k]
        Y = y[k]

        if X < xmin or X > xmax or Y < ymin or Y > ymax:
            continue

        i = int((X - xmin) / dx * (W - 1))  #求出像素位置
        j = int(((Y - ymin) / dy) * (H - 1))  #求出像素位置

        if 0 <= i < W and 0 <= j < H:
            n1[j, i] += 1.0   #每个像素点代表多少粒子

            # 关键：直接算出所在块
            bh = j // block_h   #像素位置÷ 每块像素的大小 = 像素位于哪个格子里
            bw = i // block_w
            if bh < h_blocks and bw < w_blocks:
                n2_small[bh, bw] += 1.0        #每个block块里有多少个粒子

    # ========= 3. 把块值铺回到每个像素 -> n2 =========
    n2 = np.zeros_like(n1)

    for bh in prange(h_blocks):
        j1 = bh * block_h
        j2 = H if (bh + 1) * block_h > H else (bh + 1) * block_h  #这个快覆盖的起始像素和终点像素

        for bw in range(w_blocks):
            i1 = bw * block_w
            i2 = W if (bw + 1) * block_w > W else (bw + 1) * block_w   # 对应的w像素

            v = n2_small[bh, bw]
            for jj in range(j1, j2):
                for ii in range(i1, i2):
                    n2[jj, ii] = v   #为每个像素赋值

    # ========= 4. 用块总数替换 n1 中非零像素 =========
    for j in prange(H):
        for i in range(W):
            if n1[j, i] > 0.0:
                n1[j, i] = n2[j, i]

    return n1

def warmup():
    # 用小数据触发一次编译
    x_dummy = np.linspace(0, 1, 1000, dtype=np.float64)
    y_dummy = np.linspace(0, 1, 1000, dtype=np.float64)

    x_dummy = np.ascontiguousarray(x_dummy)
    y_dummy = np.ascontiguousarray(y_dummy)

    _ = pixel_scatter(x_dummy, y_dummy,
                      0.0, 1.0, 0.0, 1.0,
                      100, 75, 4,0.0)