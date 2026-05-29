#沿线的rmsxy和束损
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    path = "d_e_5.xlsx"
    df = pd.read_excel(path)


    if 1:
        bpm_name = df["bpm_name"].tolist()

        x = np.arange(len(bpm_name))

        fig, axs = plt.subplots(2, 2, figsize=(14, 8), sharex=True)

        # ---------- 子图 1：BPM X ----------
        ax = axs[0, 0]
        ax.plot(x, df["bpm_rmsx_max"])
        ax.plot(x, df["bpm_rmsx_min"])
        ax.fill_between(x, df["bpm_rmsx_min"], df["bpm_rmsx_max"], alpha=0.3)
        ax.set_ylabel("x [mm]")
        ax.set_title("BPM X envelope")
        ax.grid(True)

        # 👇 上面一行也设置横坐标
        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)
        ax.tick_params(axis="x", labelbottom=True)

        # ---------- 子图 2：BPM Y ----------
        ax = axs[0, 1]
        ax.plot(x, df["bpm_rmsy_max"])
        ax.plot(x, df["bpm_rmsy_min"])
        ax.fill_between(x, df["bpm_rmsy_min"], df["bpm_rmsy_max"], alpha=0.3)
        ax.set_ylabel("y [mm]")
        ax.set_title("BPM Y envelope")
        ax.grid(True)

        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)
        ax.tick_params(axis="x", labelbottom=True)

        # ---------- 子图 3：Phase ----------
        # ax = axs[1, 0]
        # ax.plot(x, df["bpmphase_max"])
        # ax.plot(x, df["bpmphase_min"])
        # ax.fill_between(x, df["bpmphase_min"], df["bpmphase_max"], alpha=0.3)
        # ax.set_ylabel("phase [deg]")
        # ax.set_title("BPM Phase envelope")
        # ax.grid(True)
        #
        # ax.set_xticks(x)
        # ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)

        # ax = axs[1, 0]

        # energy_normal = df["energy_normal"]

        # denergy_max = df["energy_max"] - energy_normal
        # denergy_min = df["energy_min"] - energy_normal

        # ax.plot(x, denergy_max, label="energy max - normal")
        # ax.plot(x, denergy_min, label="energy min - normal")

        # ax.fill_between(x, denergy_min, denergy_max, alpha=0.3)

        # # 关键参考线
        # ax.axhline(0, color="k", lw=1, ls="--", alpha=0.7)

        # ax.set_ylabel("Δ energy [MeV]")
        # ax.set_title("BPM energy envelope (relative to nominal)")
        # ax.grid(True)
        # ax.legend()

        # ax.set_xticks(x)
        # ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)

        ax = axs[1, 0]

        loss_max = df["loss_max"]
        loss_min = df["loss_min"]
        import re
        def parse_loss_mean(x):
            # 如果本来已经是 list 或 ndarray
            if isinstance(x, (list, np.ndarray)):
                return np.mean(x)

            # 如果是字符串，例如 "[np.float64(0.0), np.float64(12.0)]"
            if isinstance(x, str):
                nums = re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", x)
                nums = [float(v) for v in nums]
                return np.mean(nums) if len(nums) > 0 else np.nan

            return np.nan

        df["loss_mean"] = df["loss"].apply(parse_loss_mean)
        loss_mean = df["loss_mean"].to_numpy()


        ax.plot(x, loss_max, label="loss_max")
        ax.plot(x, loss_min, label="loss_min")
        ax.plot(x, loss_mean, label="loss_mean")

        ax.fill_between(x, loss_min, loss_max, alpha=0.3)

        # 关键参考线
        ax.axhline(0, color="k", lw=1, ls="--", alpha=0.7)

        ax.set_ylabel("")
        ax.set_title("particle loss")
        ax.grid(True)
        ax.legend()

        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)

        # ---------- 子图 4 ----------

        ax = axs[1, 1]


        def parse_number(x):
            if isinstance(x, (list, np.ndarray)):
                return np.array(x, dtype=float)

            if isinstance(x, str):
                # 优先匹配 np.float64(...) 里面的数字，避免把 float64 里的 64 也提取出来
                nums = re.findall(r"np\.float64\(([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\)", x)

                # 如果不是 np.float64(...) 形式，再按普通数字提取
                if len(nums) == 0:
                    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", x)

                return np.array([float(v) for v in nums], dtype=float)

            return np.array([], dtype=float)


        df["bpm_number"] = df["bpm_number"].apply(parse_number)



        diff_lis = []

        for i in range(len(df)):
            if i == 0:
                diff = np.zeros_like(df["bpm_number"].iloc[i])
            else:
                diff = df["bpm_number"].iloc[i - 1]- df["bpm_number"].iloc[i]

            diff_lis.append(diff)

        df["bpm_number_diff"] = diff_lis


        df["bpm_number_diff_mean"] = df["bpm_number_diff"].apply(np.mean)
        df["bpm_number_diff_max"] = df["bpm_number_diff"].apply(np.max)
        df["bpm_number_diff_min"] = df["bpm_number_diff"].apply(np.min)


        ax.plot(x, df["bpm_number_diff_max"], label="loss_max")
        ax.plot(x,  df["bpm_number_diff_min"], label="loss_min")
        ax.plot(x, df["bpm_number_diff_mean"], label="loss_mean")
        ax.fill_between(x, df["bpm_number_diff_min"], df["bpm_number_diff_max"], alpha=0.3)

        # 关键参考线
        ax.axhline(0, color="k", lw=1, ls="--", alpha=0.7)

        ax.set_ylabel("")
        ax.set_title("particle loss")
        ax.grid(True)
        ax.legend()

        ax.set_xticks(x)
        ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)



        # bpmphase_normal = df["bpmphase_normal"]
        # # print(bpmphase_normal)
        # dphase_max = df["bpmphase_max"] - bpmphase_normal
        # dphase_min = df["bpmphase_min"] - bpmphase_normal

        # ax.plot(x, dphase_max, label="phase max - normal")
        # ax.plot(x, dphase_min, label="phase min - normal")

        # ax.fill_between(x, dphase_min, dphase_max, alpha=0.3)

        # # 关键参考线
        # ax.axhline(0, color="k", lw=1, ls="--", alpha=0.7)

        # ax.set_ylabel("Δ phase [deg]")
        # ax.set_title("BPM Phase envelope (relative to nominal)")
        # ax.grid(True)
        # ax.legend()

        # ax.set_xticks(x)
        # ax.set_xticklabels(bpm_name, rotation=90, fontsize=7)




    plt.tight_layout()
    plt.show()