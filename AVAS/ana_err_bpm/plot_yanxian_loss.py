
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    path = "./loss/dE_loss_g5.xlsx"
    df = pd.read_excel(path)

    z = df["z"].values

    fig, ax = plt.subplots(figsize=(14, 8))

    # ax.plot(z, df["loss_max"], label="max")
    ax.plot(z, df["loss_min"], label="min")
    ax.plot(z, df["loss_mean"], label="mean")

    ax.set_xlabel("z [cm]")      # ← 根据你实际单位改成 m / cm
    ax.set_ylabel("Loss")
    # ax.set_title("Loss Envelope Along Beamline")
    ax.legend()
    # ax.grid(True)



    df_bpm = pd.read_excel("bpm_v2.xlsx")
    name_bpm = df_bpm["name_bpm"].values
    bpm_posi = df_bpm["bpm_posi"].values   # 单位必须和 z 一致（cm）

    ymin, ymax = ax.get_ylim()

    for name, pos in zip(name_bpm, bpm_posi):
        # 画竖线
        ax.axvline(
            x=pos,
            color="gray",
            linestyle="--",
            linewidth=0.8,
            alpha=0.6
        )

        # 标注 BPM 名字（顶部，竖着写）
        ax.text(
            pos,
            ymax,
            name,
            rotation=90,
            va="bottom",
            ha="center",
            fontsize=10,
            alpha=0.8
        )


    plt.tight_layout()
    plt.show()