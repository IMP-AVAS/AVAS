import numpy as np
import os

def read_dataset_dast_final(path):
    data = np.loadtxt(path)

    loss = -(data[:, 28][-1] - data[:, 28][0])/ data[:, 28][0]

    emitx = (data[:, 13][-1] - data[:, 13][0])/ data[:, 13][0]
    emity = (data[:, 14][-1] - data[:, 14][0])/ data[:, 14][0]
    emitz = (data[:, 15][-1] - data[:, 13][0])/ data[:, 15][0]


    data= {
        "loss": loss,
        "emitx": emitx,
        "emity": emity,
        "emitz": emitz,

    }
    return data

if __name__ == '__main__':
    base_path = r"C:\Users\wangh\Desktop\hiaf_v2\result\dxy\g2"

    res = []

    paths = [os.path.join(base_path, f"output_2_{i}", "DataSet.txt") for i in range(90, 98) ]

    res = {
        "loss": [],
        "emitx": [],
        "emity": [],
        "emitz": [],
    }
    for path in paths:
        data = read_dataset_dast_final(path)
        res["loss"].append(data["loss"])
        res["emitx"].append(data["emitx"])
        res["emity"].append(data["emity"])
        res["emitz"].append(data["emitz"])

    avg_loss = np.mean(res["loss"])
    avg_emitx = np.mean(res["emitx"])
    avg_emity = np.mean(res["emity"])
    avg_emitz = np.mean(res["emitz"])

    emit_loss = {
        "g1":
            {
        "loss": avg_loss,
        "emitx": avg_emitx,
        "emity": avg_emity,
        "emitz": avg_emitz,
            }
    }
    import pickle

    # 加载原有的pickle文件数据
    pickle_path = os.path.join(base_path, "emit_loss.pkl")
    try:
        with open(pickle_path, "rb") as f:
            old_data = pickle.load(f)
    except (FileNotFoundError, EOFError):
        old_data = {}

    # 更新数据
    old_data.update(emit_loss)

    # 保存新数据回pickle文件
    with open(pickle_path, "wb") as f:
        pickle.dump(old_data, f)



    print(emit_loss)