import copy
import os.path

from utils.readfile import read_txt
import numpy as np
from core.MultiParticle import MultiParticle
import random
import shutil
if __name__ == "__main__":
    project_path = r"E:\using\hu\saomiao_mebt"
    lattice_mulp_path = os.path.join(project_path, "InputFile", "lattice_mulp.txt")
    lattice_path = os.path.join(project_path, "InputFile", "lattice.txt")

    lattice_mulp_lis = read_txt(lattice_mulp_path, out='list', readdall=True)
    # print(lattice_mulp_lis)

    orig_data = np.array([289.543, -276.219, 209.933, -147.316, 209.068, -156.973])
    orig_data_min = orig_data - [50, 50, 50, 50, 50, 50]
    orig_data_max = orig_data + [50, 50, 50, 50, 50, 50]

    # orig_data_min1 = orig_data - [40, 40, 40, 40, 40, 40]
    # orig_data_max1 = orig_data - [30, 30, 30, 30, 30, 30]
    #
    # orig_data_min2 = orig_data + [30, 30, 30, 30, 30, 30]
    # orig_data_max2 = orig_data + [40, 40, 40, 40, 40, 40]

    for i in range(499, 10000):
        new_lis = []
        # random_num1 = [round(np.random.uniform(orig_data_min1[i], orig_data_max1[i]), 5) for i in range(6)]
        # random_num2 = [round(np.random.uniform(orig_data_min2[i], orig_data_max2[i]), 5) for i in range(6)]
        #
        # random_num = random.choice([random_num1, random_num2])

        random_num = [round(np.random.uniform(orig_data_min[i], orig_data_max[i]), 5) for i in range(6)]

        # print(26, random_num1)
        new_lis = []

        index = 0
        for j in lattice_mulp_lis:
            if len(j)> 0 and j[0] == "fieldx":
                v = copy.deepcopy(j)
                v[0] = 'field'
                v[-2] = random_num[index]
                new_lis.append(v)
                index += 1

            else:
                new_lis.append(j)

        with open(lattice_path, 'w') as f:
            for k in new_lis:
                f.write(' '.join(map(str, k)) + '\n')

        suiji = os.path.join(project_path, "suiji.txt")

        random_num.insert(0, i)
        with open(suiji, 'a') as f:
            f.write(' '.join(map(str, random_num)) + '\n')

        obj = MultiParticle(project_path)
        obj.run()
        print("                     ")
        print("         模拟结束            ")

        orig_dataset = os.path.join(project_path, "OutputFile", "DataSet.txt")
        destination_folder = os.path.join(project_path, "data",  f"dataset_{i}.txt")

        shutil.copy(orig_dataset, destination_folder)
