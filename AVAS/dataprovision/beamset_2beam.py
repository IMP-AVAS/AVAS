import numpy as np
import struct
import os

#双束文件的的beamset
# 二进制文件，数据格式
# Char + Char + dumpPeriodicity(int) + Np(int) + Ib[mA](double) + freq[MHz](double) + mc2[MeV](double)
# + Nx * [Char + tpye(int) + Index(int) + time[s](double) + location[m](double) +
# Np * [x(d) + px(d) +  y(double) + py(double) + z(double) + pz(double) + lossFlag(int)]]
# Np * [x(double) + px(double) +  y(double) + py(double) + t(double) + pz(double) + recordFlag(double)]]


class BeamsetParameter2b():
    def __init__(self, beamset_path):
        self.beamset_path = beamset_path


    def get_step(self):
        with open(self.beamset_path, 'rb') as f:

            tdata = struct.unpack("<B", f.read(1))
            plt_type = int(tdata[0])


            tdata = struct.unpack("<c", f.read(1))
            char2 = str(tdata[0])

            tdata = struct.unpack("<i", f.read(4))
            self.dumpPeriodicity = int(tdata[0])
            # print("输出间隔为{aa}".format(aa=self.dumpPeriodicity))

            tdata = struct.unpack("<i", f.read(4))
            self.numofp = int(tdata[0])
            # print("粒子数为：{aa}".format(aa=numofp))

            tdata = struct.unpack("<d", f.read(8))
            self.Ib = float(tdata[0])
            # print("流强为：{aa}mA".format(aa=self.Ib))

            tdata = struct.unpack("<d", f.read(8))
            self.freq = float(tdata[0])
            # print("频率为：{aa}MHz".format(aa=self.freq))

            tdata = struct.unpack("<d", f.read(8))
            self.BaseMassInMeV = float(tdata[0])
            # print("粒子静止质量为：{aa}MeV".format(aa=self.BaseMassInMeV))

            #一步的字节

        self.total_head_byte = 1 + 1 + 4*2 + 8*3  #文件的总开头

        self.one_step_head_byte = 1 + 4 + 4 + 8 + 8  # 一步的开头比特
        self.one_step_particle_block_bytes = 8 * 6 + 4 * 3 + 8 * 2
        self.one_step_byte = self.one_step_head_byte + self.one_step_particle_block_bytes * (self.numofp + 1)


        file_size = os.path.getsize(self.beamset_path)
        step = (file_size -  self.total_head_byte) / self.one_step_byte

        return int(step)

    def get_one_parameter(self, num):
        step_num = self.get_step()
        step_list = [i for i in range(step_num)]
        # print(step_list)
        if num < 0:
            num = step_list[num]
        elif num >= step_num or num < step_num*-1:
            print(f"There are {step_num - 1} step in this file, it's beyond that",)
            return 0

        with open(self.beamset_path, 'rb') as f:

            #跳过开头
            f.seek(self.total_head_byte, 1)

            #跳过多少步
            f.seek(num * self.one_step_byte, 1)

            self.one_step_dict = {}
            self.one_step_list = []

            header_struct = struct.Struct("<c i i d d")
            buf = f.read(self.one_step_head_byte)

            _, tpye, index, time, location = header_struct.unpack(buf)

            self.one_step_dict = {
                "type": tpye,
                "index": index,
                "time": time,
                "location": location,
            }

            # print("location", location)
            # for i in range(self.numofp):
            #     vdata1 = struct.unpack("<dddddd", f.read(48))
            #     vdata2 = struct.unpack("<ii", f.read(8))
            #
            #     vdata = list(vdata1) + list(vdata2)
            #     self.one_step_list.append(vdata)
            data = np.frombuffer(f.read(self.one_step_particle_block_bytes * (self.numofp+1)), dtype=np.dtype([
                ('x', '<f8'), ('xp', '<f8'), ('y', '<f8'), ('yp', '<f8'), ('z', '<f8'), ('zp', '<f8'),
                ('status', '<i4'), ('id', '<i4'), ('charge', '<i4'),
                ('mass', '<f8'), ('weight', '<f8'),
            ]))

            data_array = np.column_stack([
                data['x'],
                data['xp'],
                data['y'],
                data['yp'],
                data['z'],
                data['zp'],
                data['status'],
                data['id'],
                data['charge'],
                data['mass'],
                data['weight'],
            ])

            #给所有的粒子加上同步粒子的信息

            syn_x = data_array[-1][0]
            syn_y = data_array[-1][2]

            syn_z = location

            data_array[:, 0] = data_array[:, 0] + syn_x
            data_array[:, 2] = data_array[:, 2] + syn_y
            data_array[:, 4] = data_array[:, 4] + syn_z

            self.one_step_list = data_array


        return self.one_step_dict, self.one_step_list


    def get_parameter(self):
        with open(self.beamset_path, 'rb') as f:
            # 跳过开头
            f.seek(self.byte_head, 1)

            # 跳过多少步

            self.allstep_list = []
            self.allstep_dict = []

            while True:
                header_struct = struct.Struct("<c i i d d")
                buf = f.read(self.step_byte_head)
                if len(buf) == 0:
                    break

                _, tpye, index, time, location = header_struct.unpack(buf)

                every_step_dict = {
                    "type": tpye,
                    "index": index,
                    "time": time,
                    "location": location,
                }

                vadata = np.frombuffer(f.read((48 + 8) * self.numofp), dtype=np.dtype([
                    ('x', '<f8'), ('xp', '<f8'), ('y', '<f8'), ('yp', '<f8'), ('z', '<f8'), ('zp', '<f8'),
                    ('id', '<i4'), ('status', '<i4')
                ]))



                self.allstep_dict.append(every_step_dict)
                self.allstep_list.append(vadata)

        return self.allstep_dict, self.allstep_list


    def get_all_dict(self, ):

        all_step_dict = []
        header_struct = struct.Struct("<c i i d d")

        with open(self.beamset_path, "rb") as f:
            f.seek(self.byte_head, 1)

            while True:
                # 直接从文件开头偏移到 byte_head
                buf = f.read(self.step_byte_head)
                if len(buf) < self.step_byte_head:
                    break

                _, tpye, index, time, location = header_struct.unpack(buf)

                all_step_dict.append({
                    "tpye": tpye,
                    "index": index,
                    "time": time,
                    "location": location,
                })

                f.seek(self.step_particle_block_bytes, 1)

            return all_step_dict


if __name__ == "__main__":

    beamset_pasth = r"C:\Users\wangh\Desktop\test_xiao\OutputFile\BeamSet.plt"
    obj = BeamsetParameter2b(beamset_pasth)

    step = obj.get_step()
    print(step)
    # for i in range(390):
    #     dic ,lis = obj.get_one_parameter(i)
    #     print(dic["location"])


    dic ,lis = obj.get_one_parameter(265)
    print(dic["location"])

    print(lis[-1])
    import matplotlib.pyplot as plt

    z_p = [i[4] for i in lis if int(i[8]) == 1 and int(i[6])==1]
    y_p = [i[2] for i in lis if int(i[8]) == 1 and int(i[6])==1]
    z_ap = [i[4] for i in lis if int(i[8]) == -1 and int(i[6])==1]
    y_ap = [i[2] for i in lis if int(i[8]) == -1 and int(i[6])==1]
    # # print(d1, l1[0])
    #
    # res =obj.get_all_dict()
    #
    plt.scatter(z_p, y_p,s=4.0)
    plt.scatter(z_ap, y_ap,s=4.0)
    plt.show()


    # # print(res)
    # x = np.array([i[0] for i in v2])
    # x1 = np.array([i[1]/i[5] for i in v2])
    #
    # z = np.asarray([i[4] for i in v2])
    #
    # from matplotlib import pyplot as plt
    # plt.scatter(x,x1)
    # plt.show()


    # res = obj.get_all_dict()
    # print(res)

    # v1, v2 = obj.get_one_parameter(49)
    # print(v1)
    # # print(v1, v2)


    # print(x)
    # print(x1)
    # from utils.tool import cal_twiss
    #
    # item ={
    #     "x": x,
    #     "x1": x1,
    #     "coefficient": 1,
    #     "gamma": 1.000042631556908,
    #     "beta": 0.029190516,
    # }
    # res = cal_twiss(item)
    # print(res)
    #
    # from matplotlib import pyplot as plt
    # print(len(x), len(x1))
    # plt.scatter(x, x1)
    # plt.show()

    # res = obj.get_parameter()
    # res = obj.allstep_dict[0]
    # print(res)

    # for i in range(697):
    #     v1, v2 =obj.get_one_parameter(i)
    #     print(v1)
    # print(v1)
    # import matplotlib.pyplot as plt
    # # x = [i[0] * 1000 for i in v2]
    # # y = [i[2] * 1000for i in v2]
    #
    # x = [i[4] * 1000 for i in v2]
    # y = np.array([i[5] * 1000for i in v2])
    # y = [(i -np.mean(y))/np.mean(y) *1000 for i in y]
    #
    # plt.scatter(x, y, s = 0.8)
    # plt.show()