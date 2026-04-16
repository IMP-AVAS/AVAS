import struct

class DensityParameter():
    def __init__(self, density_path):
        self.density_path = density_path
    def  get_parameter(self, ):
        data = {}


        with open(self.density_path, "rb") as f:
            # 读取 zg_lis 的长度 (第一个整数)
            run_step = struct.unpack('i', f.read(4))[0]
            self.grid_num = struct.unpack('i', f.read(4))[0]
            # print(run_step, grid_num)
            # 初始化结果数据结构
            data["zg_lis"] = []
            data["emit_lis"] = []
            data["rms_size_lis"] = []
            data["nownumofp_lis"] = []
            data["lost_lis"] = []
            data["maxlost_lis"] = []
            data["minlost_lis"] = []
            data["moy_lis"] = []
            data["maxb_lis"] = []
            data["minb_lis"] = []
            data["maxr_lis"] = []
            data["minr_lis"] = []
            data["tab_lis"] = []

            for _ in range(run_step):
                # 依次读取数据
                zg = struct.unpack('f', f.read(4))[0]  # 读取 1 个 float
                data["zg_lis"].append(zg)

                emit = struct.unpack('f' * 3, f.read(3 * 4))  # 读取 3 个 float
                data["emit_lis"].append(list(emit))

                rms_size = struct.unpack('f' * 3, f.read(3 * 4))  # 读取 3 个 float
                data["rms_size_lis"].append(list(rms_size))

                nownumofp = struct.unpack('i', f.read(4))[0]  # 读取 1 个 int
                data["nownumofp_lis"].append(nownumofp)

                lost = struct.unpack('i', f.read(4))[0]  # 读取 1 个 int
                data["lost_lis"].append(lost)

                maxlost = struct.unpack('i', f.read(4))[0]  # 读取 1 个 int
                data["maxlost_lis"].append(maxlost)

                minlost = struct.unpack('i', f.read(4))[0]  # 读取 1 个 int
                data["minlost_lis"].append(minlost)

                moy = struct.unpack('f' * 4, f.read(4 * 4))  # 读取 4 个 float
                data["moy_lis"].append(list(moy))

                maxb = struct.unpack('f' * 4, f.read(4 * 4))  # 读取 4 个 float
                data["maxb_lis"].append(list(maxb))

                minb = struct.unpack('f' * 4, f.read(4 * 4))  # 读取 4 个 float
                data["minb_lis"].append(list(minb))

                maxr = struct.unpack('f' * 4, f.read(4 * 4))  # 读取 4 个 float
                data["maxr_lis"].append(list(maxr))

                minr = struct.unpack('f' * 4, f.read(4 * 4))  # 读取 4 个 float
                data["minr_lis"].append(list(minr))

                # 动态处理 self.bins 数量的数据
                tab = []
                for _ in range(4):
                    tab_part = struct.unpack('i' * self.grid_num, f.read(self.grid_num * 4))  # 读取 bins 个 float
                    tab.append(list(tab_part))
                data["tab_lis"].append(tab)

        return data

if __name__ == "__main__":
    path = r"C:\Users\shliu\Desktop\test_yiman3\AVAS1\OutputFile\density_tot_par_1.dat"
    obj = DensityParameter(path)
    data = obj.get_parameter()
    print(len(data["zg_lis"]))
    print(len(data["tab_lis"]))