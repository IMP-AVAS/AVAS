import math
from global_varible import c_light, Pi
import numpy

def plt2dstdata(bunch_info, part_list):
    np = bunch_info["numofp"]
    Ib = bunch_info["Ib"]
    freq = bunch_info["freq"]  # 变成Hz
    BaseMassInMeV = bunch_info["BaseMassInMeV"]
    bunch_tpye = bunch_info["bunch_tpye"]
    exist_part_dstform_one_step = []
    all_part_dstform_one_step = []
    # print(part_list)
    if bunch_tpye == 0:
        for particle in part_list:
            if particle[5] > 0 and (particle[6] == 1):

                p2 = particle[1] ** 2 + particle[3] ** 2 + particle[5] ** 2
                beta = math.sqrt(p2 / (1 + p2))
                v = beta * c_light
                gamma = 1 / math.sqrt(1 - beta ** 2)

                beta_z = math.sqrt(particle[5] ** 2 / (1 + particle[5] ** 2))
                v_z = beta_z * c_light

                v_x = (particle[1] / particle[5]) * v_z
                v_y = (particle[3] / particle[5]) * v_z

                t = -(particle[4] / v_z)

                x = particle[0]
                xx = particle[1] / particle[5]

                y = particle[2]
                yy = particle[3] / particle[5]

                phi = t * 2 * Pi * freq
                E = (gamma - 1) * BaseMassInMeV
                z = particle[4]
                tlist = [x, xx, y, yy, phi, E, z]

                exist_part_dstform_one_step.append(tlist)
                all_part_dstform_one_step.append(tlist)
            else:
                all_part_dstform_one_step.append([])

    if bunch_tpye == 1:
        print("tcode开始")
        t_average = numpy.mean(numpy.array([i[4] for i in part_list if i[6] == 1]))
        for particle in part_list:
            if particle[6] == 1:

                p2 = particle[1] ** 2 + particle[3] ** 2 + particle[5] ** 2
                beta = math.sqrt(p2 / (1 + p2))
                # v = beta * c_light
                gamma = 1 / math.sqrt(1 - beta ** 2)

                # beta_z = math.sqrt(particle[5]**2/(1 + particle[5]**2))
                # v_z = beta_z * c_light

                t = particle[4] - t_average

                x = particle[0] * 100
                xx = particle[1] / particle[5]
                y = particle[2] * 100
                yy = particle[3] / particle[5]

                phi = t * 2 * Pi * freq
                E = (gamma - 1) * BaseMassInMeV

                tlist = [x, xx, y, yy, phi, E]

                exist_part_dstform_one_step.append(tlist)
                all_part_dstform_one_step.append(tlist)
            else:
                all_part_dstform_one_step.append([])


    return exist_part_dstform_one_step