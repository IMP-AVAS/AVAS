#这个类的作用为使用linacopt进行基础的一次模拟
import os
import sys

from core.LinacOPTEngine import LinacOPTEngine
import shutil

class BasicEnvSim():
    """
    基础的包络模拟（linacopt）
    """
    def __init__(self, project_path, lattice):
        self.project_path = project_path
        # self.lattice_test = os.path.join(self.self.project_path, lattice_test)
        self.LinacOPT_engine = LinacOPTEngine()
        self.lattice = lattice


    def run(self):
        f1 = r'InputFile\input.txt'
        f2 = self.lattice
        f3 = r'InputFile\beam.txt'
        f4 = r"OutputFile\env_output.txt"

        f1 = bytes(os.path.join(self.project_path, f1), encoding='utf-8')
        f2 = bytes(os.path.join(self.project_path, f2), encoding='utf-8')
        f3 = bytes(os.path.join(self.project_path, f3), encoding='utf-8')
        f4 = bytes(os.path.join(self.project_path, f4), encoding='utf-8')

        print(196)
        self.LinacOPT_engine.Trace_win_file(f1, f2, f3, f4)

        father_dir = sys.path[0]
        # father_dir = os.path.dirname(os.path.abspath(__file__))
        source_beam_out = os.path.join(father_dir, 'beam_out.txt')
        destination_beam_out = os.path.join(self.project_path, 'OutputFile', 'env_beam_out.txt')
        shutil.copyfile(source_beam_out, destination_beam_out)

        source_trm = os.path.join(father_dir, 'Tr_M.txt')
        destination_trm = os.path.join(self.project_path, 'OutputFile', 'Tr_M.txt')
        shutil.copyfile(source_trm, destination_trm)

        os.remove(source_beam_out)
        # os.remove(source_trm)

if __name__ == '__main__':
    project_path = r'C:\Users\anxin\Desktop\test_env'
    lattice_env = os.path.join(project_path, 'InputFile', 'match_no_command.txt')
    obj = BasicEnvSim(project_path, lattice_env)
    obj.run()