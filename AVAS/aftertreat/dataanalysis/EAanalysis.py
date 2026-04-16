from utils.readfile import read_txt
import os
import matplotlib.pyplot as plt

class EaAnalysis():
    def __init__(self, project_path):
        self.project_path = project_path
        self.input_path = os.path.join(self.project_path, 'InputFile')
        self.output_path = os.path.join(self.project_path, 'OutputFile')

        self.EA_errors_par_tot_path = os.path.join( self.output_path, "EA_errors_par_tot.txt")


    def get_para(self):
        errors_par_tot = read_txt(self.EA_errors_par_tot_path)
        v = errors_par_tot.pop("step_err")


        errors_par_tot = {int(k): [float(i) for i in v] for k, v in errors_par_tot.items()}
        # print(errors_par_tot)
        # print(errors_par_tot[-1])

        v1 = {} #index, 可能为None
        all_loss = []

        start = 5 #0: x  1: y 2: phix 3: phiy 4:phiz   5:场幅
        delta = 7 - start

        for i in range(start, 126, 7):
            v = errors_par_tot.get(i)
            if v:
                v1[i] = v
            else:
                all_loss.append(i)
                v1[i] = None

        x = [(k+delta)/7 for k, v in v1.items() ]
        print(x)
        #束损
        # y = [v[0] * 100 if v else 100 for k,v in v1.items() ]

        #发射度x
        # y = [v[1] * 100 for k, v in v1.items() if v ]
        #质心x
        y = [v[4] * 1000 for k,v in v1.items() if v]


        loss_index = [(i+delta)/7 for i in all_loss]

        print(loss_index)
        plt.plot(x, y, marker='o')

        #
        #
        # v3 = [i for i in range(len(v1))]
        # v4 = [i for i in v3 if i not in v1]
        # print(v1)
        # print(v4)
        #
        plt.show()


if __name__ == "__main__":
    path =r"C:\Users\anxin\Desktop\test_mulp"
    obj = EaAnalysis(path)
    obj.get_para()
