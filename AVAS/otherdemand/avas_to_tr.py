['FIELD_MAP', '7700', '330', '-20', '20', '-3', '3', '0', '0', 'hwr015', '0']

#这是一个用于将AVAS转换成tracewin的转换脚本，

# def field_tmp_to_stat(tmp):
#     """
#     将 tmp 反向解析为 FIELD_MAP stat
#     """
#     assert tmp[0] == "field", "Not a field tmp"
#
#     z_start = tmp[1] * 1000
#     R   = tmp[2] * 1000
#     field_type = tmp[4]
#
#     # 默认占位，按需补
#     stat = ["FIELD_MAP", None, None, None, None, None, None, None, None, None]
#
#     # ===== 静电场 =====
#     if field_type == 2:
#         # 对应 stat[1] == 7
#         stat[1] = "7"
#         stat[2] = str(z_start)
#         stat[4] = str(R)
#         stat[6] = tmp[7]
#         stat[9] = tmp[9]
#
#     # ===== 特定磁/电场 =====
#     elif field_type == 3:
#         # 对应 stat[1] == 70
#         stat[1] = "70"
#         stat[2] = str(z_start)
#         stat[4] = str(R)
#         stat[5] = tmp[8]
#         stat[9] = tmp[9]
#
#     # ===== RF 场 =====
#     elif field_type == 1:
#         # 对应 stat[1] == 7700
#         stat[1] = "7700"
#         stat[2] = str(z_start)
#         stat[4] = str(R)
#         stat[3] = str(tmp[6])     # phase
#         stat[5] = tmp[8]
#         stat[6] = tmp[7]
#         stat[9] = tmp[9]
#
#     else:
#         raise ValueError(f"Unknown field_type: {field_type}")
#
#     return stat
import sys

def read_avas(avas_path):

    with open(avas_path, encoding='utf-8') as file_object:
        lines = file_object.readlines()

    avas_list = []

    for line in lines:
        lst = line.split()
        avas_list.append(lst)
    return avas_list

def tran_avas_tracewin_list(avas_list):
    trace_win_list = []

    for index, stat in enumerate(avas_list):
        if len(stat) == 0:
            trace_win_list.append([])
        elif stat[0][0] == "!":
            stat[0] = ";" + stat[0][1:]
            trace_win_list.append(stat)

        elif stat[0].lower() == "drift":
            print(stat)
            tmp = [stat[0].lower(), float(stat[1])*1000, float(stat[2])*1000, 0, 0]
            trace_win_list.append(tmp)


        elif stat[0].lower() == "field":
            if int(stat[4]) == 1:
            #高频电磁场
                tmp =["field_map", 7700, float(stat[1]) *1000, float(stat[6]),
                      float(stat[2]) * 1000, float(stat[8]), float(stat[7]),
                      0, 0, stat[9], 0
                      ]
                if int(stat[3]) == 0:
                    trace_win_list.append(["SET_SYNC_PHASE"])

            #静磁场
            elif int(stat[4]) == 3:
                tmp = ["field_map", 70, float(stat[1]) *1000, 0,
                      float(stat[2]) * 1000, float(stat[8]), 0,
                      0, 0, stat[9], 0
                      ]
            elif int(stat[4]) == 2:
            #静电场
                tmp = ["field_map", 7, float(stat[1]) *1000, 0,
                      float(stat[2]) * 1000, 0, float(stat[7]),
                      0, 0, stat[9], 0
                      ]
            trace_win_list.append(tmp)

        elif stat[0].lower() == "quad":
            tmp = ["quad", float(stat[1])*1000, float(stat[4]), float(stat[2]) * 1000,  0, 0, 0, 0, 0, 0]
            trace_win_list.append(tmp)

        elif stat[0].lower() == "solenoid":
            tmp = ["Solenoid", float(stat[1])*1000, float(stat[4]), float(stat[2])*1000 ]
            trace_win_list.append(tmp)

        elif stat[0].lower() == "bend":
            tmp = ["bend", float(stat[3]), float(stat[5]), float(stat[7]), float(stat[2])*1000, int(stat[7]) ]
            trace_win_list.append(tmp)

        elif stat[0].lower() == "edge":
            tmp = ["EDGE", float(stat[4]), float(stat[5]), float(stat[6]) * 1000, float(stat[7]), float(stat[8]),
                   float(stat[2]) * 1000, int(stat[9])
                   ]
            trace_win_list.append(tmp)

        elif stat[0].lower() == "steer":
            tmp = ["THIN_STEERING", float(stat[4]), float(stat[5]), float(stat[2]) * 1000, int(stat[6]),
            ]
            trace_win_list.append(tmp)

        elif stat[0].lower() == "superpose":
            # tmp = ["SUPERPOSE_MAP", float(stat[1])*1000, float(stat[2])*1000, float(stat[3])*1000, float(stat[4]) , float(stat[5]),
            #        float(stat[6]),
            #        ]
            tmp = ["SUPERPOSE_MAP", float(stat[1])*1000
                   ]
            trace_win_list.append(tmp)
    return trace_win_list


def write_to_tracewin_lattice(new_trlattice, avas_lattice_path):
    with open(avas_lattice_path, 'w', encoding='UTF-8' ) as file_object:
        for i in new_trlattice:
            tmp_s = " ".join(map(str, i))
            file_object.write(tmp_s+"\n")






if __name__ == '__main__':
    # fiels = [ "5.74228", "0.0055", "1", "1", "750e6", "180, "1.4", "1.4", "hwr"  ]

    avas_path = r"C:\Users\wangh\Desktop\proton_fix\lattice.txt"
    tracewin_lattice_path = r"C:\Users\wangh\Desktop\proton_fix\lattice_mulp.dat"

    avas_lattice = read_avas(avas_path)


    trace_win_list = tran_avas_tracewin_list(avas_lattice)
    print(trace_win_list)
    write_to_tracewin_lattice(trace_win_list, tracewin_lattice_path)

