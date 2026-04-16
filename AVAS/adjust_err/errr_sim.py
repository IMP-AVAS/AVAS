
from apps.error import ErrorDyn
from adjust_err.conv2 import import_adjust, tran_tracewin_avas, add_err, write_to_avas_lattice
import os
class NewError(ErrorDyn):
    def __init__(self, project_path, seed, if_normal):
        super().__init__(project_path, seed, if_normal)

    def run(self):
        self.write_err_par_title()
        self.write_err_par_tot_title()

        if self.if_normal == 1:
            self.run_normal()
            self.write_err_par_every_time(0,0)


        self.all_group = 3
        self.all_time = 100

        for i in range(1, self.all_group + 1):
            for j in range(1, self.all_time + 1):
                print(i, j)
                v = (i-1) * self.all_time + j -1
                self.tran_trace2avas(v)
                lattice_mulp_list = self.generate_lattice_mulp_list(i)
                self.run_one_time(i, j, lattice_mulp_list)
                self.write_err_datas(i, j)
                self.write_err_par_every_time(i, j)


    def tran_trace2avas(self, index, ):
        tracewin_lattice_path = os.path.join(self.project_path, "InputFile", "end to end-design.dat")
        avas_lattice_path = os.path.join(self.project_path, "InputFile", "lattice_mulp.txt")

        adjust_file = os.path.join(self.project_path, "adjust_err", f"Adjusted_Values.txt_{index}")
        error_file = os.path.join(self.project_path, "adjust_err", f"Error_Datas.txt_{index}")

        # 根据adjust，修改后的lattice
        adjust_tracewin_lattice = import_adjust(tracewin_lattice_path, adjust_file)

        #不修改，直接读取tracewin的lattice
        # adjust_tracewin_lattice = read_tracewin(adjust_tracewin_lattice)

        # 将lattice转换成avas
        avas_lattice = tran_tracewin_avas(adjust_tracewin_lattice)

        new_avaslattice = add_err(avas_lattice, error_file, self.all_group, self.all_time)
        write_to_avas_lattice(new_avaslattice, avas_lattice_path)


def read_tracewin(in_put):

    with open(in_put, encoding='utf-8') as file_object:
        lines = file_object.readlines()

    tracewin_list = []

    for line in lines:
        lst = line.split()
        tracewin_list.append(lst)

    # tracewin_list = [[word.lower() for word in line] for line in tracewin_list]

    return tracewin_list
def write_trace_to_avas1(tracewin_lattiace_path, avas_lattice_path):
    tracewin_list = read_tracewin(tracewin_lattiace_path)

    avas_list2 = tran_tracewin_avas(tracewin_list)
    # print(avas_list)
    with open(avas_lattice_path, 'w', encoding='UTF-8') as file_object:
        for i in avas_list2:
            tmp_s = " ".join(map(str, i))
            file_object.write(tmp_s + "\n")


if __name__ == '__main__':
    project_path = r"C:\Users\shliu\Desktop\test_yiman3\AVAS1"
    # project_path = r"C:\Users\shliu\Desktop\chaodao"
    tracewin_lattiace_path = r"C:\Users\shliu\Desktop\新建文件夹 (2)\MEBT_template.dat"
    avas_lattice_path = r"C:\Users\shliu\Desktop\新建文件夹 (2)\latticae_mulp.txt"


    write_trace_to_avas1(tracewin_lattiace_path, avas_lattice_path)

    obj = NewError(project_path, 1, True)

    obj.run()

    # project_path = r"C:\Users\shliu\Desktop\field_ciads"
    #
    # tracewin_lattiace_path = os.path.join(project_path, "InputFile", "Lattice.dat")
    # avas_lattice_path = os.path.join(project_path, "InputFile", "lattice.txt")
    #
    #
    # write_trace_to_avas1(tracewin_lattiace_path, avas_lattice_path)
