

import os
from past_file.MultiParticleEngine import PartranSimCpuEngine, EnvSimCpuEngine

from utils.readfile import read_txt
from utils.tool import write_to_txt


def MultiParticle(item):
    device = item.get("device") or "cpu"
    env_par_mode = item.get("env_par_mode") or "mulp"

    # print(13, device, env_par_mode )

    if device == "gpu":
        print(16)
        return PartranSimGpu(item)

    elif device == "cpu":
        if env_par_mode == "mulp":
            print(21)
            return PartranSimCpu(item)

        elif env_par_mode == "env":
            print(25)
            return EnvSimCpu(item)


class PartranSimCpu():
    def __init__(self, item):
        self.project_path = item["project_path"]
        self.input_file = item.get("input_file")
        self.output_file = item.get("output_file")
        self.field_path = item.get("field_path")
        # self.errorlog_path = item.get("errorlog_path")
        self.multiparticle_engine = item.get("mulp_engine")
        self.device = item.get("device")
        self.if_error = item.get("if_error", 0)
        self.env_par_mode = item.get("env_par_mode", "par")


        if self.input_file is None:
            self.input_file = os.path.join(self.project_path, "InputFile")
        if self.output_file is None:
            self.output_file = os.path.join(self.project_path, "OutputFile")

        if self.field_path == None:
            self.field_path = self.input_file

        if self.if_error == 0:
            self.errorlog_path = os.path.join(self.output_file, "ErrorLog.txt")
        elif self.if_error == 1:
            self.errorlog_path = os.path.join(self.output_file, "output_0", "ErrorLog.txt")

        if self.multiparticle_engine is None:
            self.multiparticle_engine = PartranSimCpuEngine(item)

    def run(self):
        if os.path.exists(self.errorlog_path):
            os.remove(self.errorlog_path)

        res_tmp = self.multiparticle_engine.get_path(self.input_file, self.output_file, self.field_path)

        res = self.multiparticle_engine.main_agent(1)

        # 检查报错
        if res == 1:
            # raise Exception(f'模拟错误，请查询OutputFile中的ErrorLog.txt')

            error = self.check_error_file(self.errorlog_path)
            raise Exception(f'{error}')
        elif res == 2:
            # raise Exception(f'模拟错误，请查询OutputFile中的ErrorLog.txt')
            error = self.check_error_file(self.errorlog_path)
            raise Exception(f'{error}')


class EnvSimCpu():
    def __init__(self, item):
        self.project_path = item["project_path"]
        self.input_file = item.get("input_file")
        self.output_file = item.get("output_file")
        self.field_path = item.get("field_path")
        # self.errorlog_path = item.get("errorlog_path")
        self.multiparticle_engine = item.get("mulp_engine")
        self.device = item.get("device")
        self.if_error = item.get("if_error", 0)
        self.env_par_mode = item.get("env_par_mode", "par")

        if self.input_file is None:
            self.input_file = os.path.join(self.project_path, "InputFile")
        if self.output_file is None:
            self.output_file = os.path.join(self.project_path, "OutputFile")

        if self.field_path == None:
            self.field_path = self.input_file

        if self.if_error == 0:
            self.errorlog_path = os.path.join(self.output_file, "ErrorLog.txt")
        elif self.if_error == 1:
            self.errorlog_path = os.path.join(self.output_file, "output_0", "ErrorLog.txt")

        if self.multiparticle_engine is None:
            self.multiparticle_engine = EnvSimCpuEngine(item)

    def run(self):
        if os.path.exists(self.errorlog_path):
            os.remove(self.errorlog_path)

        res_tmp = self.multiparticle_engine.get_path(self.input_file, self.output_file, self.field_path)

        res = self.multiparticle_engine.main_agent(1)

        # 检查报错
        if res == 1:
            # raise Exception(f'模拟错误，请查询OutputFile中的ErrorLog.txt')

            error = self.check_error_file(self.errorlog_path)
            raise Exception(f'{error}')
        elif res == 2:
            # raise Exception(f'模拟错误，请查询OutputFile中的ErrorLog.txt')
            error = self.check_error_file(self.errorlog_path)
            raise Exception(f'{error}')

class PartranSimGpu():
    """
    使用gpu进行模拟
    """
    def __init__(self, item):
        self.project_path = item["project_path"]
        self.input_file = item.get("input_file")
        self.output_file = item.get("output_file")
        self.field_path = item.get("field_path")
        # self.errorlog_path = item.get("errorlog_path")
        self.multiparticle_engine = item.get("mulp_engine")
        self.device = item.get("device")
        self.if_error = item.get("if_error", 0)
        self.env_par_mode = item.get("env_par_mode", "par")


        if self.input_file is None:
            self.input_file = os.path.join(self.project_path, "InputFile")
        if self.output_file is None:
            self.output_file = os.path.join(self.project_path, "OutputFile")

        if self.field_path == None:
            self.field_path = self.input_file

        if self.if_error == 0:
            self.errorlog_path = os.path.join(self.output_file, "ErrorLog.txt")
        elif self.if_error == 1:
            self.errorlog_path = os.path.join(self.output_file, "output_0", "ErrorLog.txt")

        if self.multiparticle_engine is None:
            self.multiparticle_engine = PartranSimCpuEngine(item)

        self.boundary_path = os.path.join(self.project_path, "InputFile", "boundary.txt")



    def generate_input_gpu(self, input_file, output_file, field_path):
        input_txt = os.path.join(input_file, "input.txt")
        ori_input_res = read_txt(input_txt, out="list", case_sensitive=True)

        ori_input_res_keys = [i[0].lower() for i in ori_input_res]

        if "numofgrid" not in ori_input_res_keys:
            ori_input_res.append(["numofgrid", 24, 24, 24])
        if "meshrms" not in ori_input_res_keys:
            ori_input_res.append(["meshrms", 4, 4, 4])

        ori_input_res.append(["statoutputinterval", 1])


        ori_input_res.append(["beampath", input_file]) #dst文件在哪个位置，
        ori_input_res.append(["outputpath", output_file]) #输出文件地址
        ori_input_res.append(["fieldpath", field_path]) #长文件地址


        input_txt_gpu = os.path.join(input_file, "input_gpu.txt")
        write_to_txt(input_txt_gpu, ori_input_res)

        self.if_boundary = 0
        for i in ori_input_res:
            if i[0] == "boundary":
                if int(i[1]) == 0:
                    self.if_boundary = 0
                elif int(i[1]) == 1:
                    self.if_boundary = 1

    def generate_beam_gpu(self, input_file, output_file, field_path):
        beam_txt = os.path.join(input_file, "beam.txt")
        ori_beam_res = read_txt(beam_txt, out="list", case_sensitive=True)

        for i in ori_beam_res:
            if i[0].lower() == "kneticenergy":
                i.append(0)

        beam_txt_gpu = os.path.join(input_file, "beam_gpu.txt")
        write_to_txt(beam_txt_gpu, ori_beam_res)


    def run(self):
        from hpc.avasx_initializer import Avasx

        if os.path.exists(self.errorlog_path):
            os.remove(self.errorlog_path)

        self.generate_input_gpu(self.input_file, self.output_file, self.field_path)
        self.generate_beam_gpu(self.input_file, self.output_file, self.field_path)

        input_txt_gpu_path = os.path.join(self.input_file, "input_gpu.txt")
        beam_txt_gpu_path = os.path.join(self.input_file, "beam_gpu.txt")
        lattice_txt_gpu_path = os.path.join(self.input_file, "lattice.txt")
        boundary_path = None
        if self.if_boundary == 1:
            boundary_path = self.boundary_path

        # 运行
        avasx = Avasx(input_txt_gpu_path, beam_txt_gpu_path, lattice_txt_gpu_path, boundary_path)
        avasx.run()
        # avasx.release()

def basic_mulp(project_path):
    obj = MultiParticle(project_path)
    res = obj.run()

if __name__ == "__main__":
    import os

    path = r"C:\Users\shliu\Desktop\cafe2\AVAS"
    item = {'project_path': path,
            "device":"cpu",
            "env_par_mode": "mulp",
            }
    obj = MultiParticle(item)
    obj.run()
    # print(">" * 30)
    # print("exe =", sys.executable)
    # print("cwd =", os.getcwd())
    # print("__file__ =", __file__)
    # print("platform =", platform.platform())
    # print("PATH(head) =", os.environ.get("PATH", "")[:300])
    # print("PATH(has dllfile) =", "dllfile" in os.environ.get("PATH", ""))
    # print("sys.path(head) =", sys.path[:5])
    # print(">" * 30)

    # obj.run()



