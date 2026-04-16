from core.LinacOPTEngine import LinacOPTEngine

import ctypes as C
import os
from apps.matchtwiss import mismatch
from utils.myoptimize import gradient_descent_minimize

class CircleMatch():
    """
    周期匹配（linacopt）
    """
    def __init__(self, project_path):
        self.project_path = project_path
        # self.lattice_test = os.path.join(self.self.project_path, lattice_test)
        self.LinacOPT_engine = LinacOPTEngine()

        self.mismatch =mismatch

    def circle_match_file(self, filename):
        # 单组匹配功能,输入文件处理
        lattice_file_name = f"match_no_command.txt"
        lattice_file_name = os.path.join(self.project_path, 'InputFile', lattice_file_name)
        fo_in = open(filename, "r")
        fname_out = open(lattice_file_name, "w+")
        fo_out = open(lattice_file_name, "w+")
        Team_number = 0  # 组别数
        Circle_Number = 0  # 周期短有多少个周期
        Cell_Number = 0  # 每个周期有多少个元件
        Cell_end = 0  # 结束标识符
        Cell_match_number = 0  # 该组周期段需要匹配几个周期
        com_number = 0  # 已经写了多少个元件
        com_list = ['DIPOLE', 'DRIFT', 'QUAD', 'SOLENOID', 'RF_GAP', 'RF_MAP'];  # 元件列表
        N3 = -1  # 功能标识符，0代表横向匹配，1代表纵向匹配
        for line in fo_in.readlines():
            linelist = line.split()
            if linelist[0] == 'LATTICE':
                Team_number = linelist[1]
                Circle_Number = int(linelist[2])
                Cell_Number = int(linelist[3])
            # 周期开始，结构重写
            elif linelist[0] == 'LATTICE_END':
                Cell_end = 1  # 结束标识符
            elif linelist[0] == 'CIRCLE_MATCH':
                Cell_match_number = int(linelist[2])  # 需要多少个周期参与匹配
                N3 = int(linelist[3])
            # 周期段开始
            elif Circle_Number != 0:
                if com_number < Cell_match_number * Cell_Number:
                    if linelist[0] in com_list:
                        fo_out.writelines(line)
                        com_number += 1
        fo_out.close()
        return N3

    def circle_match_goal(self, N3):
        def goal(x):
            out = (C.c_double * 6)()

            f1 = r'InputFile\input.txt'
            f2 = r'InputFile\match_no_command.txt'
            f3 = r'InputFile\beam.txt'

            f1 = bytes(os.path.join(self.project_path, f1), encoding='utf-8')
            f2 = bytes(os.path.join(self.project_path, f2), encoding='utf-8')
            f3 = bytes(os.path.join(self.project_path, f3), encoding='utf-8')

            str1 = C.c_char_p()
            str1.value = f1
            str2 = C.c_char_p()
            str2.value = f2
            str3 = C.c_char_p()
            str3.value = f3
            out = (C.c_double * 6)()
            change_line = (C.c_double * 6)(*x)
            self.LinacOPT_engine.Trace_win_beam_change(str1, str2, str3, change_line, out)
            # print(out[0:6])
            if N3 == 0:
                M1 = mismatch(x[0:2], out[0:2])
                M2 = mismatch(x[2:4], out[2:4])
                M = M1 + M2
            else:
                M = mismatch(x[4:6], out[4:6])
            return M

        return goal

    def write_input_twiss(self, res):
        path = os.path.join(self.project_path, 'OutputFile', 'env_input_twiss.txt')
        with open(path, 'w') as file:
            for i in range(0, len(res), 2):
                file.write(str(round(res[i], 5)))
                file.write("   ")
                file.write(str(round(res[i+1], 5)))
                file.write("\n")

    def circle_match(self, filename):
        filename = os.path.join(self.project_path, 'InputFile', filename)

        N3 = self.circle_match_file(filename)  # 标识符
        goal = self.circle_match_goal(N3)  # 目标函数
        # 上下界如何指定？

        m_ub = [10, 10, 10, 10, 1, 1]
        m_lb = [-10, 0, -10, 0, -1, 0]

        # ga = GA(func=goal, n_dim=len(m_lb), size_pop=20, lb=m_lb, ub=m_ub, max_iter=50)
        # best_x, best_y = ga.run()
        # # print(pso.gbest_x)
        # if best_y < 0.5:
        #     print("已完成匹配,目标位置与目标Twiss的失配度为:")
        # else:
        #     print("未完成匹配,目标位置与目标Twiss的失配度为:")
        # # print(pso.gbest_y)
        # print(best_y)
        # print("入口Twiss参数为：")
        # print(best_x)

        options = {'maxiter': 100}
        result = gradient_descent_minimize(goal, m_lb, m_ub, None, options)
        # print(pso.gbest_x)
        if result.fun < 0.5:
            print("已完成匹配,目标位置与目标Twiss的失配度为:")
        else:
            print("未完成匹配,目标位置与目标Twiss的失配度为:")
        print(result.fun)
        print("入口Twiss参数为：")
        print(result.x)
        self.write_input_twiss(result.x)

if __name__ == "__main__":
    # os.chdir(r'C:\Users\anxin\Desktop\circle_match')
    v = CircleMatch(r'C:\Users\shliu\Desktop\AVAS914\test')
    v.circle_match('lattice_env.txt')
