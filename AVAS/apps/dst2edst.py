
#将两个dst文件合并成一个，且可以不是同一种束流
import struct
import numpy as np

from utils.readfile import read_dst_fast
import global_varible

def generate_extra_particle_dc(partran, number, phase_min, phase_max, phase_center):
    right_partran = []  # 右边的粒子
    left_partran = []  # 左边的粒子

    #生成右边的粒子
    right_phase = phase_max - global_varible.Pi
    right_ratio = right_phase/(2 *global_varible.Pi)
    righr_particle_num = int(right_ratio * number)

    idx = np.random.choice(number, size=righr_particle_num, )
    sample_particles_right = partran[idx]

    right_phase = [global_varible.Pi, phase_max]
    sample_particles_right[:, 4] = np.random.uniform(
        low=right_phase[0],
        high=right_phase[1],
        size=sample_particles_right.shape[0]
    )
    right_partran = sample_particles_right

    #生成左边的粒子
    left_phase = -1 * global_varible.Pi - phase_min
    left_ratio = left_phase / (2 *global_varible.Pi)
    righr_particle_num = int(left_ratio * number)

    idx = np.random.choice(number, size=righr_particle_num, )
    sample_particles_left = partran[idx]

    left_phase = [phase_min, - global_varible.Pi]
    sample_particles_left[:, 4] = np.random.uniform(
        low=left_phase[0],
        high=left_phase[1],
        size=sample_particles_left.shape[0]
    )
    left_partran = sample_particles_left

    all_partran = np.vstack([
        partran,
        right_partran,
        left_partran
    ])
    all_partran[:, 4] = all_partran[:, 4] + phase_center
    return all_partran

def generate_extra_particle_pulse(partran, number, phase_min, phase_max, phase_center):
    right_partran = []  # 右边的粒子
    left_partran = []  # 左边的粒子

    #将束流归于中心
    phi_mean =  float(partran[:, 4].mean())
    partran[:, 4] = partran[:, 4] - phi_mean


    all_partran_list = []

    # 根据 phase_min 和 phase_max 决定复制范围
    k_min = int(np.floor(phase_min / (2 * global_varible.Pi))) #向下取整 np.floor(2.3)  2 np.floor(-2.3)  # -3
    k_max = int(np.ceil(phase_max / (2 * global_varible.Pi))) #向上取整np.ceil(2.3) 3 np.ceil(-2.3)   # -2

    for k in range(k_min, k_max + 1):
        temp = partran.copy()

        # 每 360 度复制一次
        temp[:, 4] = temp[:, 4] + (k * 2 * global_varible.Pi)

        # 只保留目标范围内的粒子
        mask = (temp[:, 4] >= phase_min) & (temp[:, 4] <= phase_max)
        temp = temp[mask]

        if temp.shape[0] > 0:
            all_partran_list.append(temp)

    if len(all_partran_list) == 0:
        return np.empty((0, partran.shape[1]))

    all_partran = np.vstack(all_partran_list)
    all_partran[:, 4] = all_partran[:, 4] + phase_center

    return all_partran



class Dst2edst():
    def __init__(self, item):

        self.b1_phase_min = item.get("b1_phase_min") * global_varible.Pi/180
        self.b1_phase_max = item.get("b1_phase_max") * global_varible.Pi/180

        self.b2_phase_min = item.get("b2_phase_min") * global_varible.Pi/180
        self.b2_phase_max = item.get("b2_phase_max") * global_varible.Pi/180

        self.b1_phase_center = item.get("b1_phase_center") * global_varible.Pi/180
        self.b2_phase_center = item.get("b2_phase_center") * global_varible.Pi/180

        self.syn_p_charge = item.get("syn_p_charge")
        self.syn_p_mass = item.get("syn_p_mass")
        self.syn_p_phi = item.get("syn_p_phi") * global_varible.Pi/180
        self.syn_p_energy = item.get("syn_p_energy")

        self.b1_charge = item.get("b1_charge")
        self.b2_charge = item.get("b2_charge")

        self.b1_path = item.get("b1_path")
        self.b2_path = item.get("b2_path")

        self.two_beam_mode = item.get("2beam_mode")
        self.edst_path = item.get("edst_path")
        #dc定义为1, pulse定义为0

    def run(self):
        BaseCharge = 1.60217653e-19
        C_light = 299792458

#对束流1进行处理
        ###########################################################################
        data_1 = read_dst_fast(self.b1_path)
        number_1 = data_1["number"]
        ib_1 = data_1["ib"]
        freq_1 = data_1["freq"] 
        partran_1 = data_1["partran_dist"]


        BaseMassInMeV_1 = data_1["basemassinmev"]
        aveEnergy_1 = data_1["kneticenergy"]


        macroNumber = 1
        if ib_1 != 0:
            macroNumber_1 = abs(ib_1 / 1000 / (freq_1) / number_1 / BaseCharge / self.b1_charge)

# 对束流2进行处理
        ###############################################################
        data_2 = read_dst_fast(self.b2_path)
        number_2 = data_2["number"]
        ib_2 = data_2["ib"]
        freq_2 = data_2["freq"]
        partran_2 = data_2["partran_dist"]

        BaseMassInMeV_2 = data_2["basemassinmev"]
        aveEnergy_2 = data_2["kneticenergy"]

        macroNumber = 1
        if ib_2 != 0:
            macroNumber_2 = abs(ib_2 / 1000 / (freq_2) / number_2 / BaseCharge / self.b2_charge)

#########################################################################################################

        validdata = []
        #生成正负数据
        #Cr52 48373.58942976 #Cr53 49305.21580433
        print(BaseMassInMeV_1, BaseMassInMeV_2)

        new_data_1 = []
        new_data_2 = []
        #生成正数据

        if 1:
            # 将dc定义为1，puslse定义为0
            #束流1的生成
            if self.two_beam_mode[0] == 1:
                new_data_1 = generate_extra_particle_pulse(partran_1, number_1, self.b1_phase_min, self.b1_phase_max, self.b1_phase_center)
            elif self.two_beam_mode[0] == 0:
                new_data_1 = generate_extra_particle_pulse(partran_1, number_1, self.b1_phase_min, self.b1_phase_max, self.b1_phase_center)

            n = new_data_1.shape[0]

            # 新建一个 (N, 9) 的数组
            new_data_1_ext = np.zeros((n, 9), dtype=new_data_1.dtype)

            # 前 6 列复制原来的粒子数据
            new_data_1_ext[:, :6] = new_data_1

            # 后 3 列写入 charge, mass, macroNumber
            new_data_1_ext[:, 6] = self.b1_charge
            new_data_1_ext[:, 7] = BaseMassInMeV_1
            new_data_1_ext[:, 8] = macroNumber_1

            # 替换回 new_data_1
            new_data_1 = new_data_1_ext

            # theta = np.deg2rad(30)
            #
            # x = new_data_1[:, 0].copy()
            # y = new_data_1[:, 1].copy()
            #
            # new_data_1[:, 0] = x * np.cos(theta) + y * np.sin(theta)
            # new_data_1[:, 1] = -x * np.sin(theta) + y * np.cos(theta)


            #束流2的生成
            if self.two_beam_mode[0] == 1:
                new_data_2 = generate_extra_particle_pulse(partran_2, number_2, self.b2_phase_min, self.b2_phase_max, self.b2_phase_center)
            elif self.two_beam_mode[0] == 0:
                new_data_2 = generate_extra_particle_pulse(partran_2, number_2, self.b2_phase_min, self.b2_phase_max, self.b2_phase_center)


            n = new_data_2.shape[0]

            # 新建一个 (N, 9) 的数组
            new_data_2_ext = np.zeros((n, 9), dtype=new_data_2.dtype)

            # 前 6 列复制原来的粒子数据
            new_data_2_ext[:, :6] = new_data_2

            # 后 3 列写入 charge, mass, macroNumber
            new_data_2_ext[:, 6] = self.b2_charge
            new_data_2_ext[:, 7] = BaseMassInMeV_2
            new_data_2_ext[:, 8] = macroNumber_2

            # 替换回 new_data_2
            new_data_2 = new_data_2_ext


        validdata = np.vstack([new_data_1, new_data_2])

        print(validdata[0])
        # --------------------------------------------------
        number = len(validdata)
        # --------------------------------------------------

        # --------------------------------------------------

        f = open(self.edst_path, 'wb')
        data = struct.pack('<B', 125)
        f.write(data)
        data = struct.pack('<B', 100)
        f.write(data)
        data = struct.pack('<i', number)
        f.write(data)
        data = struct.pack('<d', ib_1)  #流强没意义，所以用束流1的流强占用位置
        f.write(data)
        data = struct.pack('<d', freq_1/(10**6))   #要求所有束流的频率一致，所以用束流1的频率，单位是HZ
        f.write(data)
        data = struct.pack('<B', 125)
        f.write(data)

        for i in range(len(validdata)):
            data = struct.pack('<ddddddddd', validdata[i][0], validdata[i][1], validdata[i][2], validdata[i][3],
                               validdata[i][4], validdata[i][5], validdata[i][6], validdata[i][7], validdata[i][8])
            f.write(data)

        data = struct.pack('<ddddddddd', 0, 0, 0, 0, self.syn_p_phi, self.syn_p_energy,
                           self.syn_p_charge, self.syn_p_mass, 1)

        f.write(data)
        data = struct.pack('<d', BaseMassInMeV_1)  #质量也是没有意义的，所以用束流1的质量占位置
        f.write(data)
        f.close()


if __name__ == "__main__":
    item = {'b1_phase_min': -720.0,   #束流1最小相位
            'b1_phase_max': 720.0,    #束流1最大相位

            'b2_phase_min': -720.0,    #束流1的中心
            'b2_phase_max': 720.0,     #束流2的中心

            'b1_phase_center': 0,
            'b2_phase_center': 0,

            'syn_p_charge': 1,
            'syn_p_mass': 938.27209,
            'syn_p_phi': 0,
            'syn_p_energy': 1,   #同步粒子的能量

            'b1_charge': 1,
            'b2_charge': -1,

            'b1_path': r"C:\Users\wangh\Desktop\test_page_2b\Outputfile\generate_2beam\part_rfq1.dst",
            'b2_path': r"C:\Users\wangh\Desktop\test_page_2b\Outputfile\generate_2beam\part_rfq2.dst",
            '2beam_mode': (1, 1),
            'edst_path': 'C:\\Users\\wangh\\Desktop\\test_page_2b\\OutputFile\\generate_2beam\\2beam2.edst'}

    obj = Dst2edst(item)
    obj.run()