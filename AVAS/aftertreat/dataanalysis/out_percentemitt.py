from aftertreat.dataanalysis.percentemitt import PercentEmit
import os
import copy
from conf.contants import dst_picture_title_dict, option_type_dict
def treat_directory(directory_path, ratio):
    file_names = os.listdir(directory_path)
    if os.path.exists('result.txt'):
        os.remove('result.txt')
    with open('result.txt', 'a') as file:
        j = 0
        for file_name in file_names:
            file.write(file_name + '\n')

            file_name_all = os.path.join(directory_path, file_name)
            res = cla_twiss_output_standard(file_name_all, ratio)

            for i in res:
                file.write(i + '\n')
            j += 1
            file.write('' + '\n')
            print(f'已完成第{j}个文件的计算')

#用来计算一个dst文件的twiss参数，根据picture_type来计算
def cla_twiss_output_standard(item):
    """
    此函数用来处理单个dst文件
    """
    # item = {
    #     "ratio": ,
    #     "picture_type": [["x","x1"], ["y", "y1"]],
    #     "dst_path": ,
    #     "dst_dict": ,
    #     "ratio": ,
    #
    # }
    all_picture_type = item["picture_type"]  # e.g. [["x","x1"], ["y","y1"], ...]
    ratio = item.get("ratio", 1.0)

    v = PercentEmit()

    # 用于显示标题：["x","x1"] -> "X-X'"
    type_title_dict = dst_picture_title_dict

    lines = []
    twiss_dict = {}

    for pic in all_picture_type:
        this_item = copy.deepcopy(item)
        this_item["picture_type"] = pic

        (
            alpha_percent, beta_percent, gamma_percent,
            norm_epsilon_percent, norm_epsilon_100,
            norm_all_epsilon_percent, norm_all_epsilon_100,
            no_norm_epsilon_percent, no_norm_epsilon_100,
            no_norm_all_epsilon_percent, no_norm_all_epsilon_100
        ) = v.get_percent_emit(this_item)


        # print(
        #     alpha_percent,
        #     beta_percent,
        #     gamma_percent,
        #     rms_epsilon_percent,  # 你原来写成 rms_epsilon_perent，这里统一成 percent
        #     rms_epsilon_100,
        #     all_epsilon_100,
        #     all_epsilon_percent,
        # )
        twiss_dict[tuple(pic)] = [
            alpha_percent, beta_percent, gamma_percent,
            norm_epsilon_percent, norm_epsilon_100,   #归一化发射度
            norm_all_epsilon_percent, norm_all_epsilon_100,  #归一化全发射度
            no_norm_epsilon_percent, no_norm_epsilon_100,   #非归一化发射度
            no_norm_all_epsilon_percent, no_norm_all_epsilon_100  #非归一化全发射度
        ]
        # 下面就是你“目标格式”的那一段：每个 picture_type 一块
        lines.extend([
            f"{type_title_dict[pic[0]]} - {type_title_dict[pic[1]]}",   #标题
            f"ε(rms)  = {norm_epsilon_100:.5f} π.mm.mrad [ Norm. ]",     #归一化发射度
            f"ε(rms)[{ratio * 100:.0f}%]  = {norm_epsilon_100:.5f} π.mm.mrad [ Norm. ]",  #百分比归一化发射度
            f"ε[{ratio * 100:.0f}%] = {norm_all_epsilon_percent:.5f} π.mm.mrad",  #百分比全发射度归一化
            f"β = {beta_percent:.5f}  mm/π.mrad",   #百分比alpha
            f"α = {alpha_percent:.5f}",        #百分比beta
            " ",  # 空行分隔
        ])

    twiss_text = "\n".join(lines)
    return twiss_dict, twiss_text


if __name__ == "__main__":
    # 计算某一个dst文件的参数
    dst_path = r"C:\Users\wangh\Desktop\phase_plot\10w.dst"

    item = {
        "ratio": 1,
        "picture_type": [["x", "x1"], ["y", "y1"], ["z", "z1"], ["phi", "w"]],
        "dst_path": dst_path,
        "dst_dict": None,
    }
    twiss_dict, twiss_text = cla_twiss_output_standard(item)
    print(twiss_dict)

    # directory_path = r'C:\Users\anxin\Desktop\te'
    # treat_directory(directory_path, 0.8)