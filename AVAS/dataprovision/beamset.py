#单束文件的beamset
import numpy as np
import struct
import os
# 二进制文件，数据格式
# Char + Char + dumpPeriodicity(int) + Np(int) + Ib[mA](double) + freq[MHz](double) + mc2[MeV](double)
# + Nx * [Char + tpye(int) + Index(int) + time[s](double) + location[m](double) +
# Np * [x(d) + px(d) +  y(double) + py(double) + z(double) + pz(double) + lossFlag(int)]]
# Np * [x(double) + px(double) +  y(double) + py(double) + t(double) + pz(double) + recordFlag(double)]]


class BeamsetParameter():
    def __init__(self, beamset_path):
        self.beamset_path = beamset_path


    def get_step(self):
        with open(self.beamset_path, 'rb') as f:

            tdata = struct.unpack("<c", f.read(1))
            char1 = str(tdata[0])
            tdata = struct.unpack("<c", f.read(1))
            char2 = str(tdata[0])

            tdata = struct.unpack("<i", f.read(4))
            # self.dumpPeriodicity = int(tdata[0])
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

            #一步的字节数
        byte_onestep = 1 + 4 + 4 + 8 + 8 + (48 + 8) * self.numofp
        byte_head = 1 + 1 + 4*2 + 8*3

        file_size = os.path.getsize(self.beamset_path)
        step = (file_size - byte_head) / byte_onestep

        self.byte_onestep = byte_onestep   #一步的总比特
        self.step_byte_head = 1 + 4 + 4 + 8 + 8   #一步的开头比特
        self.step_particle_block_bytes = (48 + 8) * self.numofp  #一步的粒子比特

        self.byte_head = byte_head     #总的开头比特


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
            f.seek(self.byte_head, 1)

            #跳过多少步
            f.seek(num * self.byte_onestep, 1)

            self.one_step_dict = {}
            self.one_step_list = []

            header_struct = struct.Struct("<c i i d d")
            buf = f.read(self.step_byte_head)

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
            data = np.frombuffer(f.read((48 + 8) * self.numofp), dtype=np.dtype([
                ('x', '<f8'), ('xp', '<f8'), ('y', '<f8'), ('yp', '<f8'), ('z', '<f8'), ('zp', '<f8'),
                ('id', '<i4'), ('status', '<i4')
            ]))

            self.one_step_list = data

            # while True:
            #     try:
            #         tdata = struct.unpack("<c", f.read(1))
            #         # print(tdata)
            #     except struct.error:
            #         print("所选步数超过了总步数")
            #         break
            #
            #     else:
            #
            #         tpye = struct.unpack("<i", f.read(4))
            #         self.one_step_dict["tpye"] = int(tpye[0])
            #         # print("tpye", tpye)
            #
            #         Index = struct.unpack("<i", f.read(4))
            #         self.one_step_dict["index"] = int(Index[0])
            #         # print("index", Index)
            #
            #         time = struct.unpack("<d", f.read(8))
            #         self.one_step_dict["time"] = float(time[0])
            #         # print(time)
            #
            #         location = struct.unpack("<d", f.read(8))
            #         self.one_step_dict["location"] = float(location[0])
            #         # print("location", location)
            #         # for i in range(self.numofp):
            #         #     vdata1 = struct.unpack("<dddddd", f.read(48))
            #         #     vdata2 = struct.unpack("<ii", f.read(8))
            #         #
            #         #     vdata = list(vdata1) + list(vdata2)
            #         #     self.one_step_list.append(vdata)
            #         data = np.frombuffer(f.read((48 + 8) * self.numofp), dtype=np.dtype([
            #             ('x', '<f8'), ('xp', '<f8'), ('y', '<f8'), ('yp', '<f8'), ('z', '<f8'), ('zp', '<f8'),
            #             ('id', '<i4'), ('status', '<i4')
            #         ]))
            #         list2d = [list(item) for item in data.tolist()]
            #         print(list2d[0])
            #         self.one_step_list.append(list2d)
            #     break

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
    import os
    import numpy as np
    beamset_pasth = r"C:\Users\wangh\Desktop\test_xiao\OutputFile\BeamSet.plt"
    obj = BeamsetParameter(beamset_pasth)

    step = obj.get_step()
    print(step)
    # for i in step:
    v1 , v2 = obj.get_one_parameter(270)
    print(v1)

    x = np.array([i[0] for i in v2])
    z = np.asarray([i[4] for i in v2])
    z = np.array(z) + v1["location"]

    from matplotlib import pyplot as plt
    plt.scatter(z, x)
    plt.show()


    # res =obj.get_all_dict()
    # print(res)
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