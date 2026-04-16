import struct
import sys

import numpy as np
import os

class Exdata():
    def __init__(self, path):
        self.path = path
        pass

    def get_grid_num(self):
        with open(self.path, 'rb') as f:
            tdata = struct.unpack("<c", f.read(1))

            index = struct.unpack("<i", f.read(4))

            grid_num = struct.unpack("<i", f.read(4))

            grid_num = int(grid_num[0])
            return grid_num
    def get_param(self):
        grid_num = self.get_grid_num()

        with open(self.path, 'rb') as f:

            byte_onestep = 1 + 4 + 4 + (grid_num * 4) * 4 + 8 * 12
            file_size = os.path.getsize(self.path)

            self.step = int((file_size) / byte_onestep)
            dtype = np.dtype([
                ('char', '<c'),
                ('index', '<i4'),
                ('grid_num', '<i4'),
                # ('f', '<i4', (4* grid_num)),  # 一口气读 1200 个 int32
                ('dx', '<i4', grid_num),
                ('dy', '<i4', grid_num),
                ('dr', '<i4', grid_num),
                ('dz', '<i4', grid_num),
                ('i', '<f8', 12),  # 一口气读   12 个 float64
            ])


            buf = f.read(byte_onestep * self.step)

            data = np.frombuffer(buf, dtype=dtype)

            # print(len(data))
            # print(data[-1])
            ex_list = []
            for i in range(len(data)):
            # for i in range():
            #     tab = np.array(data[i][3])

                # parts = np.array_split(tab, grid_num)
                # tab_x, tab_y, tab_r, tab_z = map(list, zip(*parts))
                tab_x = data[i][3]
                tab_y = data[i][4]
                tab_r = data[i][5]
                tab_z = data[i][6]

            # tab_x = [j[0] for j in parts]
                # tab_y = [j[1] for j in parts]
                # tab_r = [j[2] for j in parts]
                # tab_z = [j[3] for j in parts]
                # print(np.sum(tab_x), np.sum(tab_y), np.sum(tab_r), np.sum(tab_z))
                ex_list.append({
                    "index": data[i][1],
                    "grid_num": data[i][2],
                    "tab_x": tab_x,
                    "tab_y": tab_y,
                    "tab_r": tab_r,
                    "tab_z": tab_z,
                    "x_min": data[i][7][0],
                    "x_max": data[i][7][1],
                    "x_ave": data[i][7][2],
                    "y_min": data[i][7][3],
                    "y_max": data[i][7][4],
                    "y_ave": data[i][7][5],
                    "r_min": data[i][7][6],
                    "r_max": data[i][7][7],
                    "r_ave": data[i][7][8],
                    "z_min": data[i][7][9],
                    "z_max": data[i][7][10],
                    "z_ave": data[i][7][11],
                    })
        return ex_list
if __name__ == '__main__':
    index = -100
    cpu_path = r"C:\Users\anxin\Desktop\duibi\PCHistogram_cpu.dat"
    obj_cpu = Exdata(cpu_path)
    res = obj_cpu.get_param()
    c0 = res[index]["tab_x"]
    c0 = res[index]["x_min"]
    print(c0)


    gpu_path = r"C:\Users\anxin\Desktop\duibi\PCHistogram_gpu.dat"
    obj_gpu = Exdata(gpu_path)
    res = obj_gpu.get_param()
    g0 = res[index]["tab_x"]
    g0 = res[index]["x_min"]
    print(g0)
    # deta = c0 -g0
    # print(deta)