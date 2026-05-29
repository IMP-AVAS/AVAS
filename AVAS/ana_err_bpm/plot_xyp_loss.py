#沿线的质心和相位
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import re
if __name__ == '__main__':
    df_bpm = pd.read_excel("bpm_v2.xlsx")
    name_bpm = df_bpm["name_bpm"].values
    bpm_posi = df_bpm["bpm_posi"].values   # 单位必须和 z 一致（cm）



    path = r"./loss/dphi_loss_g4.xlsx"
    df = pd.read_excel(path)

    loss_mean =  df["loss_mean"]/10**5 *100

    x = df["z"]


    if 1:
        fig, axs = plt.subplots(2, 2, figsize=(14, 8), sharex=True)

        # ================= 子图 1：cx + loss =================
        ax = axs[0, 0]
        ax.plot(x, df["cx_max"] * 1000, label="cx max")
        ax.plot(x, df["cx_min"] * 1000, label="cx min")
        ax.fill_between(x, df["cx_min"] * 1000, df["cx_max"] * 1000, alpha=0.3)
        ax.set_ylabel("x [mm]")

        ax2 = ax.twinx()
        ax2.plot(x, loss_mean, "k--", label="loss mean(%)")
        ax2.set_ylabel("Loss(%)")

        ax.legend(loc="upper left")
        ax2.legend(loc="upper right")
        if 1 :
            ymin, ymax = ax.get_ylim()

            for i, (name, pos) in enumerate(zip(name_bpm, bpm_posi)):


                ax.axvline(
                    x=pos,
                    color="gray",
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.6
                )
                index = int(re.search(r'\d+', name).group())
                if index <=6:
                    if i % 5 == 0:  # 每隔一个 BPM 标一次
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue
                elif index >6:
                    if i % 2 != 0:
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue


        # ================= 子图 2：cy + loss =================
        ax = axs[0, 1]
        ax.plot(x, df["cy_max"] * 1000, label="cy max")
        ax.plot(x, df["cy_min"] * 1000, label="cy min")
        ax.fill_between(x, df["cy_min"] * 1000, df["cy_max"] * 1000, alpha=0.3)
        ax.set_ylabel("y [mm]")

        ax2 = ax.twinx()
        ax2.plot(x, loss_mean, "k--", label="loss mean(%)")
        ax2.set_ylabel("Los(%)")

        ax.legend(loc="upper left")
        ax2.legend(loc="upper right")

        if 1:
            ymin, ymax = ax.get_ylim()

            for i, (name, pos) in enumerate(zip(name_bpm, bpm_posi)):

                ax.axvline(
                    x=pos,
                    color="gray",
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.6
                )
                index = int(re.search(r'\d+', name).group())
                if index <= 6:
                    if i % 5 == 0:  # 每隔一个 BPM 标一次
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue
                elif index > 6:
                    if i % 2 != 0:
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue
        # ================= 子图 3：phase + loss =================
        ax = axs[1, 0]
        ax.plot(x, df["phase_max"], label="phase max")
        ax.plot(x, df["phase_min"], label="phase min")
        ax.fill_between(x, df["phase_min"], df["phase_max"], alpha=0.3)
        ax.set_ylabel("phase [deg]")

        ax2 = ax.twinx()
        ax2.plot(x, loss_mean, "k--", label="loss mean(%)")
        ax2.set_ylabel("Loss(%)")

        ax.legend(loc="upper left")
        ax2.legend(loc="upper right")

        if 1:
            ymin, ymax = ax.get_ylim()

            for i, (name, pos) in enumerate(zip(name_bpm, bpm_posi)):

                ax.axvline(
                    x=pos,
                    color="gray",
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.6
                )
                index = int(re.search(r'\d+', name).group())
                print(51, index)
                if index <= 6:
                    if i % 5 == 0:  # 每隔一个 BPM 标一次
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue
                elif index > 6:
                    if i % 2 != 0:
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue

        # ================= 子图 4：Δphase(BPM) + loss =================
        ax = axs[1, 1]

        phase_max = df["phase_max"].values
        phase_min = df["phase_min"].values
        phase_normal = df["phase_normal"].values

        dphase_max_curve = phase_max - phase_normal
        dphase_min_curve = phase_min - phase_normal

        # 一阶线性插值到 BPM
        dphase_max_bpm = np.interp(bpm_posi, x, dphase_max_curve)
        dphase_min_bpm = np.interp(bpm_posi, x, dphase_min_curve)

        ax.plot(bpm_posi, dphase_max_bpm, label="Δphase max")
        ax.plot(bpm_posi, dphase_min_bpm, label="Δphase min")
        ax.fill_between(bpm_posi, dphase_min_bpm, dphase_max_bpm, alpha=0.3)

        ax.axhline(0, color="k", lw=1, ls="--", alpha=0.7)
        ax.set_ylabel("Δ phase [deg]")
        ax.set_xlabel("z")

        ax2 = ax.twinx()
        ax2.plot(x, loss_mean, "k--", alpha=0.7, label="loss mean(%)")
        ax2.set_ylabel("Loss(%)")

        ax.legend(loc="upper left")
        ax2.legend(loc="upper right")

        if 1:
            ymin, ymax = ax.get_ylim()

            for i, (name, pos) in enumerate(zip(name_bpm, bpm_posi)):

                ax.axvline(
                    x=pos,
                    color="gray",
                    linestyle="--",
                    linewidth=0.8,
                    alpha=0.6
                )
                index = int(re.search(r'\d+', name).group())
                print(51, index)
                if index <= 6:
                    if i % 5 == 0:  # 每隔一个 BPM 标一次
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue
                elif index > 6:
                    if i % 2 != 0:
                        ax.text(
                            pos,
                            ymax * 1.05,
                            name[3:],
                            rotation=90,
                            va="bottom",
                            ha="center",
                            fontsize=10,
                            alpha=0.8
                        )
                    else:
                        continue

        plt.tight_layout()
        plt.show()


