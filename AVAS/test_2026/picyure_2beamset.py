from dataprovision.beamset_2beam import BeamsetParameter2b
import numpy as np
import matplotlib.pyplot as plt
if __name__ == "__main__":
    c_light = 299792458
    mass_sn32 = 122957.208
    mass_sn33 = 122957.208
    str_p1 = "sn32"
    str_p2 = "sn33"

    beamset_pasth = r"C:\Users\wangh\Desktop\132Sn33\132Sn33\OutputFile\BeamSet.plt"
    obj = BeamsetParameter2b(beamset_pasth)
    step = obj.get_step()



    dic_0, lis_0 = obj.get_one_parameter(0)
    zp_0 = [i for i in lis_0 if  i[8] == 32 ]
    fp_0 = [i for i in lis_0 if  i[8] == 33 ]


    if 1:
        p_loss_lis = []
        fp_loss_lis = []
        z_lis = []

        rms_x_p_lis = []
        rms_x_fp_lis = []

        rms_y_p_lis = []
        rms_y_fp_lis = []

        energy_p_lis = []
        energy_fp_lis = []

        for i in range(0, step):
            print(i)
            dic, lis = obj.get_one_parameter(i)

            zp = [i for i in lis if i[6] == 1 and i[8] == 32]
            fp = [i for i in lis if i[6] == 1 and i[8] == 33]

            #
            p_loss = (len(zp_0) - len(zp))/100
            fp_loss = (len(fp_0) - len(fp))/100
            p_loss_lis.append(p_loss)
            fp_loss_lis.append(fp_loss)

            z_lis.append(dic['location'])

            #计算rms_x 和rms_y
            x_p = np.array([i[0] for i in zp]) *1000
            x_fp = np.array([i[0] for i in fp]) *1000

            y_p = np.array([i[2] for i in zp]) *1000
            y_fp = np.array([i[2] for i in fp]) *1000
            # print(253, y_p)
            # print(254, y_p)

            rms_x_p = float(np.sqrt(np.mean((x_p - np.mean(x_p)) ** 2)))
            rms_x_fp = float(np.sqrt(np.mean((x_fp - np.mean(x_fp)) ** 2)))
            rms_y_p = float(np.sqrt(np.mean((y_p - np.mean(y_p)) ** 2)))
            rms_y_fp = float(np.sqrt(np.mean((y_fp - np.mean(y_fp)) ** 2)))
            # print(259, rms_y_p, rms_x_fp)

            rms_x_p_lis.append(rms_x_p)
            rms_x_fp_lis.append(rms_x_fp)
            rms_y_p_lis.append(rms_y_p)
            rms_y_fp_lis.append(rms_y_fp)
            #############################

            #计算能量

            pz_p = np.array([i[5] for i in zp])
            pz_fp = np.array([i[5] for i in fp])

            pz2_p = pz_p ** 2
            pz2_fp = pz_fp ** 2

            beta_p = np.sqrt(pz2_p / (1 + pz2_p))
            beta_fp = np.sqrt(pz2_fp / (1 + pz2_fp))

            gamma_p = 1 / np.sqrt(1 - beta_p ** 2)
            gamma_fp = 1 / np.sqrt(1 - beta_fp ** 2)
            # print(gamma_p[:10])
            energy_p = (gamma_p - 1) * mass_sn32
            energy_fp = (gamma_fp - 1) * mass_sn33

            energy_p_lis.append(float(np.mean(energy_p)))
            energy_fp_lis.append(float(np.mean(energy_fp)))
    ####################################################

        fig, axes = plt.subplots(3, 2, figsize=(14, 12))

        # =====================================================
        # 1. Loss
        # =====================================================
        axes[0, 0].plot(z_lis, p_loss_lis,
                        color='r',
                        label= str_p1)

        axes[0, 0].plot(z_lis, fp_loss_lis,
                        color='b',
                        label= str_p2)

        axes[0, 0].set_xlabel('z(m)', fontsize=14)
        axes[0, 0].set_ylabel('Loss (%)', fontsize=14)
        axes[0, 0].set_title("Beam Loss", fontsize=16)

        axes[0, 0].legend()
        axes[0, 0].grid()

        # =====================================================
        # 2. Sn32 RMS
        # =====================================================
        axes[0, 1].plot(z_lis,
                        rms_x_p_lis,
                        color='r',
                        label='X')

        axes[0, 1].plot(z_lis,
                        [-1 * i for i in rms_x_p_lis],
                        color='r')

        axes[0, 1].plot(z_lis,
                        rms_y_p_lis,
                        color='b',
                        label='Y')

        axes[0, 1].plot(z_lis,
                        [-1 * i for i in rms_y_p_lis],
                        color='b')

        axes[0, 1].set_xlabel('z(m)', fontsize=14)
        axes[0, 1].set_ylabel('RMS X/Y (mm)', fontsize=14)
        axes[0, 1].set_title(str_p1, fontsize=16)
        axes[0, 1].legend()
        axes[0, 1].grid()

        # =====================================================
        # 3. Sn33 RMS
        # =====================================================
        axes[1, 0].plot(z_lis, rms_x_fp_lis, color='r', label='X')

        axes[1, 0].plot(z_lis,
                        [-1 * i for i in rms_x_fp_lis],
                        color='r')

        axes[1, 0].plot(z_lis,
                        rms_y_fp_lis,
                        color='b',
                        label='Y')

        axes[1, 0].plot(z_lis,
                        [-1 * i for i in rms_y_fp_lis],
                        color='b')

        axes[1, 0].set_xlabel('z(m)', fontsize=14)
        axes[1, 0].set_ylabel('RMS X/Y (mm)', fontsize=14)
        axes[1, 0].set_title(str_p2, fontsize=16)

        axes[1, 0].legend()
        axes[1, 0].grid()

        # =====================================================
        # 4. Energy
        # =====================================================
        axes[1, 1].plot(z_lis,
                        energy_p_lis,
                        color='r',
                        label='Sn32')

        axes[1, 1].plot(z_lis,
                        energy_fp_lis,
                        color='b',
                        label='Sn33')

        axes[1, 1].set_xlabel('z(m)', fontsize=14)
        axes[1, 1].set_ylabel('Energy (MeV)', fontsize=14)

        axes[1, 1].legend()
        axes[1, 1].grid()

        # =====================================================
        # 5. Delta Energy
        # =====================================================
        delta_energy = np.array(energy_p_lis) - np.array(energy_fp_lis)

        axes[2, 0].plot(z_lis,
                        delta_energy,
                        color='b')

        axes[2, 0].set_xlabel('z(m)', fontsize=14)
        axes[2, 0].set_ylabel('Delta Energy (MeV)', fontsize=14)

        axes[2, 0].grid()

        # =====================================================
        # 删除空白子图
        # =====================================================
        fig.delaxes(axes[2, 1])

        # 自动调整布局
        plt.tight_layout()

        # 保存图片（可选）
        # plt.savefig("beam_analysis.png",
        #             dpi=300,
        #             bbox_inches='tight')

        plt.show()

    if 1:
        for i in range(0, step):
            dic, lis = obj.get_one_parameter(i)
            fontsize = 12
            tick_size = 10

            fig, axs = plt.subplots(2, 2, figsize=(7, 7))  # 4行3列的子图布局
            plt.subplots_adjust(wspace=0.1, hspace=0.3)

            zp = [i for i in lis if i[6] == 1 and i[8] > 0]
            fp = [i for i in lis if i[6] == 1 and i[8] < 0]

        #第一张图 x_x1
            if 1:
                zp_x = np.array([i[0] for i in zp]) *1000
                zp_x1 = np.array([i[1] for i in zp]) *1000
                axs[0, 0].scatter(zp_x, zp_x1, s=0.1, color='r')

                fp_x = np.array([i[0] for i in fp]) *1000
                fp_x1 = np.array([i[1] for i in fp]) *1000
                axs[0, 0].scatter(fp_x, fp_x1, s=0.1, color='b')

                axs[0, 0].set_xlabel("x")
                axs[0, 0].set_ylabel("x'")

            # 第一张图 x_x1
            if 2:
                zp_y = np.array([i[2] for i in zp]) * 1000
                zp_y1 = np.array([i[3] for i in zp]) * 1000
                axs[0, 1].scatter(zp_y, zp_y1, s=0.1, color='r')

                fp_y = np.array([i[2] for i in fp]) * 1000
                fp_y1 = np.array([i[3] for i in fp]) * 1000
                axs[0, 1].scatter(fp_y, fp_y1, s=0.1, color='b')

                axs[0, 1].set_xlabel("y")
                axs[0, 1].set_ylabel("y'")

            # 第一张图 xy_y1
            if 2:
                zp_y = np.array([i[2] for i in zp]) * 1000
                zp_y1 = np.array([i[3] for i in zp]) * 1000
                axs[0, 1].scatter(zp_y, zp_y1, s=0.1, color='r')

                fp_y = np.array([i[2] for i in fp]) * 1000
                fp_y1 = np.array([i[3] for i in fp]) * 1000
                axs[0, 1].scatter(fp_y, fp_y1, s=0.1, color='b')

                axs[0, 1].set_xlabel("y")
                axs[0, 1].set_ylabel("y'")

            # 第3张图 z-y
            if 3:
                zp_z = np.array([i[4] for i in zp]) * 1000 - dic["location"] * 1000
                zp_y = np.array([i[2] for i in zp]) * 1000- dic["location"]
                axs[1, 0].scatter(zp_z, zp_y, s=0.1, color='r')

                fp_z = np.array([i[4] for i in fp]) * 1000- dic["location"] * 1000
                fp_y = np.array([i[2] for i in fp]) * 1000- dic["location"]
                axs[1, 0].scatter(fp_z, fp_y, s=0.1, color='b')

                axs[1, 0].set_xlabel("z")
                axs[1, 0].set_ylabel("y")

            if 4:
                p_loss = len(zp_0) - len(zp)
                fp_loss = len(fp_0) - len(fp)

                axs[1, 1].text(
                    0.05, 0.95,  # 坐标 (相对轴域, 0~1)
                    f"p_loss {p_loss}",  # 显示的字母
                    fontsize=10,
                    fontweight='bold',
                    va='top', ha='left'  # 上对齐、左对齐
                )

                axs[1, 1].text(
                    0.05, 0.85,  # 坐标 (相对轴域, 0~1)
                    f"fp_loss {fp_loss}",  # 显示的字母
                    fontsize=10,
                    fontweight='bold',
                    va='top', ha='left'  # 上对齐、左对齐
                )


                axs[1, 1].text(
                    0.05, 0.75,  # 坐标 (相对轴域, 0~1)
                    f"p red ",  # 显示的字母
                    fontsize=10,
                    fontweight='bold',
                    va='top', ha='left'  # 上对齐、左对齐
                )
                axs[1, 1].text(
                    0.05, 0.65,  # 坐标 (相对轴域, 0~1)
                    f"fp blue ",  # 显示的字母
                    fontsize=10,
                    fontweight='bold',
                    va='top', ha='left'  # 上对齐、左对齐
                )

                axs[1, 1].text(
                    0.05, 0.55,  # 坐标 (相对轴域, 0~1)
                    f"distance {dic['location']}",  # 显示的字母
                    fontsize=10,
                    fontweight='bold',
                    va='top', ha='left'  # 上对齐、左对齐
                )
                picture_path = fr"C:\Users\wangh\Desktop\field_ciads\picture\{dic['location']}.png"
                plt.savefig(picture_path, bbox_inches='tight')

