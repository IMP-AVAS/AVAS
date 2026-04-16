
import numpy as np
def grid_density(x, y, num_bins=100, norm=True):
    xmin, xmax = np.min(x), np.max(x)
    ymin, ymax = np.min(y), np.max(y)

    x_bins = np.linspace(xmin, xmax, num_bins + 1)
    y_bins = np.linspace(ymin, ymax, num_bins + 1)

    x_idx = np.digitize(x, x_bins) - 1
    y_idx = np.digitize(y, y_bins) - 1

    x_idx = np.clip(x_idx, 0, num_bins - 1)
    y_idx = np.clip(y_idx, 0, num_bins - 1)

    grid_counts = np.zeros((num_bins, num_bins), dtype=int)

    # 快速统计每个格子的计数
    np.add.at(grid_counts, (x_idx, y_idx), 1)

    # 每个粒子的密度 = 它所在格子的粒子数
    z = grid_counts[x_idx, y_idx]

    if norm and np.max(z) > 0:
        z = z / np.max(z)

    return z

if __name__ == "__main__":
    x = [1,2,3,4,5,6,7,8,9,10]
    x_bins = np.linspace(1, 10, 10)
    print(x_bins)
    x_idx = np.digitize(x, x_bins) - 1
    print(x_idx)