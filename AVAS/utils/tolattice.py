import global_varible
from utils.readfile import read_txt, read_lattice_mulp, read_lattice_mulp_with_name
def write_mulp_to_lattice_only_sim(lattice_mulp_path, lattice_path):
    """
    :param lattice_mulp_path:
    :param lattice_path:
    :return: None
    该函数的作用是将lattice_mulp中的内容写的入到lattice, 处理的情况为只进行多粒子模拟，不包含误差，矫正等
    """
    lattice_mulp = read_lattice_mulp(lattice_mulp_path)
    lattice_mulp = [i for i in lattice_mulp if i[0] in global_varible.mulp_basic_command]
    with open(lattice_path, 'w', encoding='utf-8') as f:
        for i in lattice_mulp:
            f.write(' '.join(map(str, i)) + '\n')

def write_mulp_to_lattice_only_sim2(lattice_mulp_path, lattice_path):
    """
    :param lattice_mulp_path:
    :param lattice_path:
    :return: None
    该函数的作用是将lattice_mulp中的内容写的入到lattice, 处理的情况为只进行多粒子模拟，不包含误差，矫正等
    """
    lattice_mulp_list, lattice_mulp_name = read_lattice_mulp_with_name(lattice_mulp_path)
    lattice_mulp = [i for i in lattice_mulp_list if i[0] in global_varible.mulp_basic_command]
    with open(lattice_path, 'w', encoding='utf-8') as f:
        for i in lattice_mulp:
            f.write(' '.join(map(str, i)) + '\n')



if __name__ == '__main__':
    lattice_mulp_path = r"C:\Users\shliu\Desktop\test_lattice\lattice_mulp.txt"
    lattice_path = r"C:\Users\shliu\Desktop\test_lattice\lattice.txt"
    write_mulp_to_lattice_only_sim2(lattice_mulp_path, lattice_path)