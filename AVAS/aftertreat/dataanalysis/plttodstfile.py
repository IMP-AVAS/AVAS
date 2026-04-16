
from dataprovision.beamset import BeamsetParameter
import math
from global_varible import c_light, Pi

import struct
import os
import numpy
from dataprovision.latticeparameter import LatticeParameter
class Plttozcode():
    def __init__(self, pltpath, project_path = None):
        self.project_path = project_path
        self.plt_path = pltpath
        if project_path:
            self.latttice_mulp_path = os.path.join(project_path, 'InputFile', 'lattice_mulp.txt')
    def get_all_step(self):
        obj = BeamsetParameter(self.plt_path)
        all_step =obj.get_step()
        return all_step


    #将存在的例子转换为dst文件
    def to_z_form_onestep(self, num):
        obj = BeamsetParameter(self.plt_path)
        obj.get_one_parameter(num)

        self.np = obj.numofp
        self.Ib = obj.Ib
        self.freq = obj.freq *10**6 #变成Hz
        self.BaseMassInMeV = obj.BaseMassInMeV

        part_dict = obj.one_step_dict
        part_list = obj.one_step_list

        exist_part_dstform_one_step = []
        all_part_dstform_one_step = []

        if part_dict["tpye"] == 0:
            for particle in part_list:
                if particle[5] > 0 and (particle[6] ==0 or particle[6]==2):

                    p2 = particle[1]**2 + particle[3]**2 + particle[5]**2
                    beta = math.sqrt(p2/(1 + p2))
                    v = beta * c_light
                    gamma = 1/math.sqrt(1-beta**2)

                    beta_z = math.sqrt(particle[5]**2/(1 + particle[5]**2))
                    v_z = beta_z * c_light

                    v_x = (particle[1]/ particle[5]) * v_z
                    v_y = (particle[3]/ particle[5]) * v_z


                    t = -(particle[4] / v_z)

                    x = (particle[0] + v_x * t) * 100
                    xx = particle[1] / particle[5]
                    y = (particle[2] + v_y * t) * 100
                    yy = particle[3] / particle[5]
                    phi = t * 2 * Pi * self.freq
                    E = (gamma - 1) * self.BaseMassInMeV

                    tlist = [x, xx, y, yy, phi, E]

                    exist_part_dstform_one_step.append(tlist)
                    all_part_dstform_one_step.append(tlist)
                else:
                    all_part_dstform_one_step.append([])

        if part_dict["tpye"] == 1:
            print("tcode开始")
            t_average = numpy.mean(numpy.array([i[4] for i in part_list if i[6] == 1]))
            for particle in part_list:
                if particle[6] ==1:

                    p2 = particle[1]**2 + particle[3]**2 + particle[5]**2
                    beta = math.sqrt(p2/(1 + p2))
                    # v = beta * c_light
                    gamma = 1/math.sqrt(1-beta**2)

                    # beta_z = math.sqrt(particle[5]**2/(1 + particle[5]**2))
                    # v_z = beta_z * c_light

                    t = particle[4] - t_average

                    x = particle[0] * 100
                    xx = particle[1] / particle[5]
                    y = particle[2] * 100
                    yy = particle[3] / particle[5]

                    phi = t * 2 * Pi * self.freq
                    E = (gamma - 1) * self.BaseMassInMeV

                    tlist = [x, xx, y, yy, phi, E]

                    exist_part_dstform_one_step.append(tlist)
                    all_part_dstform_one_step.append(tlist)
                else:
                    all_part_dstform_one_step.append([])

        # for i in exist_part_dstform_one_step[:10]:
        #     print(i)
        return exist_part_dstform_one_step, all_part_dstform_one_step, part_dict
    def write_to_dst(self, num):
        exist_part_dstform_one_step, all_part_dstform_one_step, part_dict_one_step = self.to_z_form_onestep(num)

        outputfile = os.path.dirname(self.plt_path)
        dst_name = "plt_step_" + str(num) + ".dst"
        outputfile_one_step = os.path.join(outputfile, dst_name)

        with open(outputfile_one_step, 'wb') as data0utFile:
            try:
                data0utFile.write(struct.pack('c', b'\x7D'))  # skip1
                data0utFile.write(struct.pack('c', b'\x64'))  # skip2

                data0utFile.write(struct.pack('i', self.np))
                data0utFile.write(struct.pack('d', self.Ib))  # mA
                data0utFile.write(struct.pack('d', self.freq/10**6))  # MHz

                data0utFile.write(struct.pack('c', b'\x7D'))

                for i in range(len(exist_part_dstform_one_step)):
                    for j in range(6):
                        data0utFile.write(struct.pack('d', exist_part_dstform_one_step[i][j]))

                data0utFile.write(struct.pack('d', self.BaseMassInMeV))  # Mev

            except IOError:
                print("输出错误")


    def get_location_index(self):

        lattice_obj = LatticeParameter(self.latttice_mulp_path)
        lattice_length = lattice_obj.v_start[-1] + lattice_obj.v_len[-1]
        print(lattice_length)
        # obj.get_parameter()
        # res = obj.allstep_dict
        # print(res)
    def to_dst_variable_t(self, num):
        pass
if __name__ == "__main__":

    project_path = r"C:\Users\anxin\Desktop\test\cafe_avas"
    # project_path = r"C:\Users\anxin\Desktop\test_mulp"
    beamset_path = os.path.join(project_path, "OutputFile", "BeamSet.plt")

    obj = Plttozcode(beamset_path, project_path)
    all_step = obj.get_all_step()
    print(all_step)

    # obj.to_z_form_onestep(0)

    obj.write_to_dst(0)
    # print(obj.get_all_step())
    # for i in range(54):
    #     obj.to_dst_variable_z(i)
    # obj.write_to_dst(-1)

