dst_picture_title_dict = {
    "x": "X(mm)",
    "y": "Y(mm)",
    "z": "Z(mm)",
    "x1": "X'(mrad)",
    "y1": "Y'(mrad)",
    "z1": "Z'(mrad)",
    "phi": "Φ(deg)",
    "w": "W(MeV)",
    "w_minus_mean": "W(MeV)",
    "dp_p_100": "dp/p(%)",
    "dp_p": "dp/p",
}

#为用户选择做转换
option_type_dict = {
    "X": "x",
    "Y": "y",
    "Z": "z",
    "X'": "x1",
    "Y'": "y1",
    "Z'": "z1",
    "Φ": "phi",
    "W": "w_minus_mean",
    "dp/p": "dp_p_100",
}

edst_option_type_dict = {
    "X": "x",
    "Y": "y",
    "Z": "z",
    "X'": "x1",
    "Y'": "y1",
    "Z'": "z1",
    "Φ": "phi",
    "W": "w",
    "dp/p": "dp_p_100",
}

#为edst文件准别
edst_picture_title_dict = {
    "x": "X(mm)",
    "y": "Y(mm)",
    "z": "Z(mm)",
    "x1": "X'(mrad)",
    "y1": "Y'(mrad)",
    "z1": "Z'(mrad)",
    "phi": "Φ(deg)",
    "w": "W(MeV)",
    "w_minus_mean": "W(MeV)",
    "dp_p_100": "dp/p(%)",
}
edst_picture_type_key_dict = {
    "x": ["b1_x", "b2_x"],
    "y": ["b1_y", "b2_y"],

    "x1": ["b1_x1", "b2_x1"],
    "y1": ["b1_y1", "b2_y1"],

    "phi": ["b1_phi_deg", "b2_phi_deg"],
    "w": ["b1_w", "b2_w"],

}