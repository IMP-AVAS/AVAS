import sys
# sys.path.append(r'C:\Users\anxin\Desktop\AVAS_control')

from dataprovision.datasetparameter import DatasetParameter
from utils.treat_directory import list_files_in_directory, copy_directory, delete_directory

from utils.readfile import read_txt
from utils.treatlist import flatten_list, list_one_two, get_dimension

from utils.tool import write_to_txt,calculate_mean, calculate_rms, add_to_txt
from utils.treatfile import copy_file, split_file
import os
from utils.tolattice import write_mulp_to_lattice_only_sim

from core.MultiParticle import MultiParticle

import multiprocessing

import global_varible
import copy


class EA():
    """
    工程分析
    """

    def __init__(self, project_path):
        self.project_path = project_path

        self.lattice_mulp_path = os.path.join(self.project_path, 'InputFile', 'lattice_mulp.txt')
        self.lattice_path = os.path.join(self.project_path, 'InputFile', 'lattice.txt')

        self.input_path = os.path.join(self.project_path, 'InputFile')
        self.output_path = os.path.join(self.project_path, 'OutputFile')

        self.error_middle_path = os.path.join(self.project_path, 'OutputFile', 'error_middle')
        self.error_middle_output0_path = os.path.join(self.project_path, 'OutputFile', 'error_middle', 'output_0')
        self.error_output_path = os.path.join(self.project_path, 'OutputFile', 'error_output')
        self.normal_out_path = os.path.join(self.error_output_path, 'output_-1')
        self.ea_errors_par_tot_path = os.path.join(self.output_path, "EA_errors_par_tot.txt")

        self.loss = []
        self.opti_res = []
        self.error_elemment_command = global_varible.error_elemment_command
        self.error_elemment_stat = global_varible.error_elemment_command_stat
        self.error_elemment_dyn = global_varible.error_elemment_command_dyn

        self.error_beam_command = global_varible.error_beam_command
        self.error_beam_stat = global_varible.error_beam_stat
        self.error_beam_dyn = global_varible.error_beam_dyn

        self.all_group = 1
        self.all_time = 1
        self.lattice_mulp_list = []

        self.normal_data = []


        max_err_quad_tran = 5
        max_err_quad_rot = 5
        max_err_quad_k = 5

        self.err_quad_dx = max_err_quad_rot
        self.err_quad_dy = max_err_quad_rot
        self.err_quad_dz = max_err_quad_rot

        self.err_quad_dphix = max_err_quad_tran
        self.err_quad_dphiy = max_err_quad_tran
        self.err_quad_dphiz = max_err_quad_tran
        self.err_quad_dk = max_err_quad_k
        self.err_quad_max_value_lis = [self.err_quad_dx, self.err_quad_dy, self.err_quad_dphix, self.err_quad_dphiy,self.err_quad_dphiz, self.err_quad_dk, self.err_quad_dz]

        max_err_cav_tran = 5
        max_err_cav_rot = 5
        max_err_cav_k = 5
        max_err_cav_phis = 2
        
        
        self.err_cav_dx = max_err_cav_tran
        self.err_cav_dy = max_err_cav_tran
        self.err_cav_dz = max_err_cav_tran

        self.err_cav_dphix = max_err_cav_rot
        self.err_cav_dphiy = max_err_cav_rot
        self.err_cav_dk = max_err_cav_k
        self.err_cav_dphis = max_err_cav_phis

        self.err_cav_max_value_lis = [self.err_cav_dx, self.err_cav_dy, self.err_cav_dphix, self.err_cav_dphiy, self.err_cav_dk, self.err_cav_dphis, self.err_cav_dz]

        self.err_beam_parameter_num = 13
        self.err_quad_parameter_num = 7
        self.err_cav_parameter_num = 7




        self.decimal = 5  # 小数点保留多少位

        self.result_queue = multiprocessing.Queue()
        # if os.path.exists(self.error_middle_path):
        #     delete_directory(self.error_middle_path)
        # os.makedirs(self.error_middle_path)

        # if os.path.exists(self.error_output_path):
        #     delete_directory(self.error_output_path)
        # os.makedirs(self.error_output_path)

    def generate_basic_lattice(self):
        lines = read_txt(self.lattice_mulp_path, out='list')
        lines = [i for i in lines if i[0] in global_varible.mulp_basic_command]

        #为每一个场元件添加误差
        for i in range(len(lines)):
            if lines[i][0] == 'field' and lines[i][4] == '3':
                t_lis = ["err_quad_ncpl_dyn", 1, 0] + [0] * 8

                lines[i].append(t_lis)

            # 在叠加场添加高频腔原件误差
            elif lines[i][0] == 'field' and lines[i][4] == '1':
                t_lis = ["err_cav_ncpl_dyn", 1, 0] + [0] * 8
                lines[i].append(t_lis)

        new_lines = []
        for i in lines:
            if get_dimension(i) == 2:
                i_copy = copy.deepcopy(i)
                new_lines.append(i[-1])
                i_copy.pop()
                new_lines.append(i_copy)
            else:
                new_lines.append(i)
        #为每个误差添加编号
        new_lines = self.add_index(new_lines)

        #添加on命令
        new_lines = self.add_element_on_command(new_lines)
        #添加beam命令
        new_lines = self.add_beam_err_command(new_lines)

        new_lines.insert(1, ['step', 1 , 1])
        # for i in new_lines:
        #     print(i)

        return new_lines





    #为误差增加编号
    def add_index(self, lattice):
        lattice = copy.deepcopy(lattice)
        num = 0
        for i in lattice:
            if i[0] == "err_quad_ncpl_dyn":
                i.append(f"quad_{num}")
                num += 1

        num = 0
        for i in lattice:
            if i[0] == "err_cav_ncpl_dyn":
                i.append(f"cav_{num}")
                num +=1
        return lattice

    #增加开关
    def add_element_on_command(self,  lattice):
        lattice = copy.deepcopy(lattice)
        if lattice[0][0] != "start":
            print("No start command")

        quad_dyn_on = ["err_quad_dyn_on"] +[1] * 7
        cav_dyn_on = ["err_cav_dyn_on"] +[1] * 7

        lattice.insert(1, quad_dyn_on)
        lattice.insert(1, cav_dyn_on)
        return lattice

    def add_beam_err_command(sel,lattice):
        err_beam_dyn_on = ["err_beam_dyn_on"] +[1] *13
        err_beam_dyn = ["err_beam_dyn", 0] + [0] *13

        lattice= copy.deepcopy(lattice)

        lattice.insert(1, err_beam_dyn)
        lattice.insert(1, err_beam_dyn_on)

        return lattice

    def set_err(self, lattice, err):
        """
        为lattice增加误差
        err:二维列表，元素为err_type, element_index, err_choose, err_value
        """
        print(err)
        lattice = copy.deepcopy(lattice)

        for i in lattice:
            for j in err:
                if i[0] == "err_beam_dyn":
                    if i[0] == j[0]:
                        i[j[2] + 2] = j[3]

                elif i[0] == f"err_{j[0]}_ncpl_dyn" and int(i[-1].split("_")[-1]) == j[1]:
                    i[j[2] + 3] = j[3]


        return lattice




    def get_err_element_num(self, lattice):
        #得到所有的磁场元件和腔体元件
        quad_num = 0
        cav_num = 0
        for i in lattice:
            if i[0] == "err_quad_ncpl_dyn":
                quad_num += 1
            elif i[0] == "err_cav_ncpl_dyn":
                cav_num += 1
        return quad_num, cav_num

    def generate_max_element_err(self, quad_num, cav_num):
        #该功能为产生所有原件的最大误差命令列表
        #元素为 腔体误差或者磁场元件误差, element_index, err_choose, err_value
        lis = []
        #此处只产生元件误差
        for i in range(quad_num):
            for j in range(self.err_quad_parameter_num):
                v_lis = ["quad", i, j, self.err_quad_max_value_lis[j]]
                lis.append(v_lis)

        for i in range(cav_num):
            for j in range(self.err_cav_parameter_num):
                v_lis = ["cav", i, j, self.err_cav_max_value_lis[j]]
                lis.append(v_lis)
        return lis



    def write_to_lattice(self, lattice):
        #带误差的
        lattice = copy.deepcopy(lattice)
        #去掉编号
        for i in lattice:
            if i[0] == "err_quad_ncpl_dyn" or i[0] =="err_cav_ncpl_dyn":
                i.pop()

        for i in lattice:
            if i[0] in global_varible.error_elemment_command_dyn:
                if set(i[3:]) == {0}: 
                    i.append(False)

        lattice = [i for i in lattice if i[-1] is not False]


        with open(self.lattice_path, 'w') as f:
            for i in lattice:
                f.write(' '.join(map(str, i)) + '\n')


    def basic_simulate(self, project_path, out_putfile):
        multiparticle_obj = MultiParticle(project_path)
        res = multiparticle_obj.run(output_file=out_putfile)
        print("模拟结束")

    def simulate(self, lattice, time):
        self.write_to_lattice(lattice)
        # self.error_output_path
        process = multiprocessing.Process(target=self.basic_simulate,
                                          args=(self.project_path, 'outputfile\error_middle'))

        process.start()  # 启动子进程
        process.join()  # 等待子进程运行结束

        # suffix = self.get_max_file_suffix(self.error_output_path) + 1
        new_name = f"output_{time}"

        copy_file(self.lattice_path, self.error_middle_output0_path)

        copy_directory(self.error_middle_output0_path, self.error_output_path, new_name)
        delete_directory(self.error_middle_output0_path)

    def get_max_file_suffix(self, directory):
        #得到该文件夹的最大后缀
        """
        查找一个文件夹下面的所有文件
        :param directory:
        :return:【】

        """

        suffix = []


        res = list_files_in_directory(directory)
        for i in res:
            suffix.append(int(i.split("_")[-1]))

        if len(suffix) == 0:
            max_suffix = -1
        else:
            max_suffix = max(suffix)
        print(max_suffix)
        return max_suffix

    def write_ea_err_datas(self, time):

        err_datas_path = os.path.join(self.output_path, f"EA_Error_Datas_{time}.txt")
        lattice_path = self.lattice_path
        input = read_txt(lattice_path, out = "list")
        # 为每个元件加编号
        index = 0
        for i in input:
            if i[0] in global_varible.long_element:
                add_name = f'element_{index}'
                i.append(add_name)
                index += 1

        res = []
        for i in range(len(input)):
            if input[i][0] == global_varible.error_elemment_command_dyn[1]:
                #quad
                index = input[i+1][-1].split('_')[-1]
                err_name = f"CAV_ERROR[{index}]"
                
                t_lis = [err_name] + input[i][3:]
                res.append(t_lis)
            elif input[i][0] == global_varible.error_elemment_command_dyn[0]:
                # quad
                index = input[i + 1][-1].split('_')[-1]
                err_name = f"QUAD_ERROR[{index}]"
                t_lis = [err_name] + input[i][3:]
                res.append(t_lis)
        
        # res = [i for i in res  if set(i[1:]) != {"0"} ]

        write_to_txt(err_datas_path, res)


    def write_ea_err_par(self):
        #误差模拟完毕后对文件进行后处理
        #1.解析dataset文件

        print(self.error_output_path)
        errr_out_file_list = list_files_in_directory(self.error_output_path)

        print(errr_out_file_list)
        errors_par_tot_list = [[
        "step_err",     #组 0
        "ratio_loss", #束流损失率，1- 存在粒子/总粒子 or 损失粒子 / 总粒子
        "emit_x_increase", #,x, y z方向发射度增长， x/x0 - 1
        "emit_y_increase",
        "emit_z_increase",
        "x_center(m)", #中心位置 5
        "y_center(m)",
        "x_'(rad)",
        "y_'(rad)",
        "rms_x(m)",
        "rms_y(m)",
        "rms_x'(rad)",   #11
        "rms_y'(rad)",   #12
        "delat_energy", #能量变化  13
        # "delat_phase",  #14
        ]
        ]

        #正常模拟数据，无误差
        normal_data=[]
        for i in errr_out_file_list:
            step_err = split_file(i)[-1].split("output_")[-1]

            dataset_path = os.path.join(i ,"DataSet.txt")
            print(dataset_path)
            dataset_obj = DatasetParameter(dataset_path, self.project_path)
            dataset_obj.get_parameter()

            if int(step_err) == -1:

                normal_data = [ 0,
                dataset_obj.num_of_particle,  #总粒子数
                dataset_obj.emit_x[0],  #m, rad
                dataset_obj.emit_y[0],  #m, rad
                dataset_obj.emit_z[0],  #m, rad
                dataset_obj.x[-1],  #m
                dataset_obj.y[-1],  #m
                dataset_obj.x_1[-1],
                dataset_obj.y_1[-1],
                dataset_obj.rms_x[-1],
                dataset_obj.rms_y[-1],
                dataset_obj.rms_x1[-1],
                dataset_obj.rms_y1[-1],
                dataset_obj.ek[-1],  #MeV
                dataset_obj.phi[-1], #deg

                ]

            if True:
                t_lis = [
                step_err,
                dataset_obj.loss[-1] / normal_data[1],
                dataset_obj.emit_x[-1]/normal_data[2] - 1,
                dataset_obj.emit_y[-1]/normal_data[3] - 1,
                dataset_obj.emit_z[-1]/normal_data[4] - 1,
                dataset_obj.x[-1],  # m
                dataset_obj.y[-1],  # m
                dataset_obj.x_1[-1],
                dataset_obj.y_1[-1],
                dataset_obj.rms_x[-1],
                dataset_obj.rms_y[-1],
                dataset_obj.rms_x1[-1],
                dataset_obj.rms_y1[-1],
                dataset_obj.ek[-1] - normal_data[13],  # MeV
                # dataset_obj.phi[-1] - normal_data[14],  # deg
                ]
                errors_par_tot_list.append(t_lis)


        for i in range(1, len(errors_par_tot_list)):
            for j in range(1, len(errors_par_tot_list[0])):
                errors_par_tot_list[i][j] = "{:.5e}".format(errors_par_tot_list[i][j])

        errors_par_tot_path = os.path.join(self.output_path, "EA_errors_par_tot.txt")
        write_to_txt(errors_par_tot_path, errors_par_tot_list)

        return 0

    def get_normal_data(self):
        path = self.normal_out_path
        dataset_path = os.path.join(path, "DataSet.txt")
        print(dataset_path)
        dataset_obj = DatasetParameter(dataset_path, self.project_path)
        dataset_obj.get_parameter()

        normal_data = [0,
                       dataset_obj.num_of_particle,  # 总粒子数
                       dataset_obj.emit_x[0],  # m, rad
                       dataset_obj.emit_y[0],  # m, rad
                       dataset_obj.emit_z[0],  # m, rad
                       dataset_obj.x[-1],  # m
                       dataset_obj.y[-1],  # m
                       dataset_obj.x_1[-1],
                       dataset_obj.y_1[-1],
                       dataset_obj.rms_x[-1],
                       dataset_obj.rms_y[-1],
                       dataset_obj.rms_x1[-1],
                       dataset_obj.rms_y1[-1],
                       dataset_obj.ek[-1],  # MeV
                       dataset_obj.phi[-1],  # deg

                       ]
        self.normal_data = normal_data
        return normal_data

    def write_ea_err_par_title(self):
        errors_par_tot_title = [[
        "step_err",     #组 0
        "ratio_loss", #束流损失率，1- 存在粒子/总粒子 or 损失粒子 / 总粒子
        "emit_x_increase", #,x, y z方向发射度增长， x/x0 - 1 #2
        "emit_y_increase",
        "emit_z_increase",
        "x_center(m)", #中心位置 5
        "y_center(m)",
        "x_'(rad)",
        "y_'(rad)",
        "rms_x(m)",
        "rms_y(m)",
        "rms_x'(rad)",   #11
        "rms_y'(rad)",   #12
        "delat_energy(MeV)", #能量变化  13
        # "delat_phase",  #14
        ]]
        write_to_txt(self.ea_errors_par_tot_path, errors_par_tot_title)

    def write_ea_err_par_every_time(self, time):
        #误差模拟完毕后对文件进行后处理
        #1.解析dataset文件

        output = os.path.join(self.error_output_path, f"Output_{time}")

        if time == -1:
            self.write_ea_err_par_title()

        #解析正常的情况
        if True:
            dataset_path = os.path.join(self.normal_out_path, "DataSet.txt")

            dataset_obj = DatasetParameter(dataset_path, self.project_path)
            dataset_obj.get_parameter()

            normal_ek = dataset_obj.ek[-1]

        dataset_path = os.path.join(output, "DataSet.txt")
        dataset_obj = DatasetParameter(dataset_path, self.project_path)
        dataset_obj.get_parameter()


        t_lis = [
        time,
        dataset_obj.loss[-1] / dataset_obj.num_of_particle,  #0
        dataset_obj.emit_x[-1]/dataset_obj.emit_x[0] - 1,
        dataset_obj.emit_y[-1]/dataset_obj.emit_y[0] - 1,
        dataset_obj.emit_z[-1]/dataset_obj.emit_z[0] - 1,
        dataset_obj.x[-1],  # m
        dataset_obj.y[-1],  # m
        dataset_obj.x_1[-1],
        dataset_obj.y_1[-1],
        dataset_obj.rms_x[-1],
        dataset_obj.rms_y[-1],
        dataset_obj.rms_x1[-1],
        dataset_obj.rms_y1[-1],
        dataset_obj.ek[-1] - normal_ek,  # MeV
        # dataset_obj.phi[-1] - normal_data[14],  # deg
        ]


        for i in range(1, len(t_lis)):
            t_lis[i] = "{:.5e}".format(t_lis[i])

        add_to_txt(self.ea_errors_par_tot_path, [t_lis])

        return 0
    def run_normal(self):
        if os.path.exists(self.normal_out_path):
            delete_directory(self.normal_out_path)
        else:
            os.makedirs(self.normal_out_path)

        #模拟没有误差的情况
        write_mulp_to_lattice_only_sim(self.lattice_mulp_path, self.lattice_path)


        process = multiprocessing.Process(target=self.basic_simulate,
                                          args=(self.project_path, 'outputfile\error_output\output_-1'))

        process.start()  # 启动子进程
        process.join()  # 等待子进程运行结束

        copy_file(self.lattice_path, self.normal_out_path)


    def set_max_err_run(self):
        # 为每个原件设置最大误差，并且进行模拟
        lattice = self.generate_basic_lattice()

        quad_num, cav_num = self.get_err_element_num(lattice)

        #产生最大误差的命令
        com_lis = self.generate_max_element_err(quad_num, cav_num)
        self.run_normal()
        self.write_ea_err_par_every_time(-1)
        for i in range(0, len(com_lis)):

            new_lattice = self.set_err(lattice, [com_lis[i]])

            self.simulate(new_lattice, i)
            self.write_ea_err_datas(i)
            try:
                self.write_ea_err_par_every_time(i)
            except Exception as e:
                pass
    def test(self):
        # lattice = self.generate_basic_lattice()

        # lis = [["err_beam_dyn", 0, 0, 5],
        #     ["err_quad_ncpl_dyn", 0, 0, 5],
        #        ["err_quad_ncpl_dyn", 1, 0, 5]
        #        ]
        # lattice = self.add_err(lattice, lis)
        # for i in lattice:
        #     print(i)
        self.set_max_err_run()
        # self.get_normal_data()

        # self.write_ea_err_par_every_time(1)


if __name__ == "__main__":
    obj = EA(r"C:\Users\anxin\Desktop\test_mulp")
    # obj.test1()
    obj.set_max_err_run()