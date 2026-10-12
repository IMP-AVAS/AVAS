from utils.readfile import read_txt
import numpy as np


path= r"C:\Users\wangh\Desktop\1009\v1.txt"
data = read_txt(path, out="list")

data = [[float(j) for j in i[:2]] for i in data]

index_list = [0]
for index, i in enumerate(data):
    if data[index][1] - data[index - 1][1] > 0.002:
        index_list.append(index-1)
        index_list.append(index)

index_list.append(len(data)-1)
# 每两个索引组成一个列表
index_groups = [
    index_list[i:i+2]
    for i in range(0, len(index_list), 2)
]

# 计算每组电流平均值
mean_list = []

for start, end in index_groups:
    current = [row[1] for row in data[start:end+1]]
    print(current[0], current[-1], np.mean(current) * 60, len(current))
    mean_list.append(np.mean(current))


print("电流平均值:", np.array(mean_list))