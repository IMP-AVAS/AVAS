
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    path = "dE_g5.xlsx"
    df = pd.read_excel(path)


    if 1:
        bpm_name = df["bpm_name"].tolist()

        x = np.arange(len(bpm_name))

        fig, axs = plt.subplots(2, 2, figsize=(14, 8), sharex=True)

        # ---------- 子图 1：BPM X ----------
        ax = axs[0, 0]
        ax.plot(x, df["bpmx_max"])
        ax.plot(x, df["bpmx_min"])
        ax.fill_between(x, df["bpmx_min"], df["bpmx_max"], alpha=0.3)
        ax.set_ylabel("x [m]")
        ax.set_title("BPM X envelope")
        ax.grid(True)

        # 👇 上面一行也设置横坐标
        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)
        ax.tick_params(axis="x", labelbottom=True)

        # ---------- 子图 2：BPM Y ----------
        ax = axs[0, 1]
        ax.plot(x, df["bpmy_max"])
        ax.plot(x, df["bpmy_min"])
        ax.fill_between(x, df["bpmy_min"], df["bpmy_max"], alpha=0.3)
        ax.set_ylabel("y [m]")
        ax.set_title("BPM Y envelope")
        ax.grid(True)

        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)
        ax.tick_params(axis="x", labelbottom=True)

        # ---------- 子图 3：Phase ----------
        ax = axs[1, 0]
        ax.plot(x, df["bpmphase_max"])
        ax.plot(x, df["bpmphase_min"])
        ax.fill_between(x, df["bpmphase_min"], df["bpmphase_max"], alpha=0.3)
        ax.set_ylabel("phase [deg]")
        ax.set_title("BPM Phase envelope")
        ax.grid(True)

        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)

        # ---------- 子图 4 ----------

        ax = axs[1, 1]

        bpmphase_normal = df["bpmphase_normal"]
        print(bpmphase_normal)
        dphase_max = df["bpmphase_max"] - bpmphase_normal
        dphase_min = df["bpmphase_min"] - bpmphase_normal

        ax.plot(x, dphase_max, label="phase max - normal")
        ax.plot(x, dphase_min, label="phase min - normal")

        ax.fill_between(x, dphase_min, dphase_max, alpha=0.3)

        # 关键参考线
        ax.axhline(0, color="k", lw=1, ls="--", alpha=0.7)

        ax.set_ylabel("Δ phase [deg]")
        ax.set_title("BPM Phase envelope (relative to nominal)")
        ax.grid(True)
        ax.legend()

        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)




    plt.tight_layout()
    plt.show()