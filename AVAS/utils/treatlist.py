import copy

#将一个列表变成1维度
def flatten_list(lst):
    flat_list = []
    for item in lst:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

#将一个1维列表变成另一个二维列表的形状，这两个列表的数据量要一样

def list_one_two(x, y):
    x = copy.deepcopy(x)
    y = copy.deepcopy(y)
    """
    x: 要改变形状的列表
    y: 目标形状列表
    """
    for i in range(len(y)):
        for j in range(len(y[i])):
            if x:
                y[int(i)][int(j)] = x.pop(0)
    return y

#得到一个列表的维度
def get_dimension(lst):
    if not isinstance(lst, list):
        return 0  # 不是列表，维度为 0
    else:
        return 1 + max(get_dimension(item) for item in lst)