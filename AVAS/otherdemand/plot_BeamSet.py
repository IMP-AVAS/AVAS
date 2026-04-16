import math

import numpy as np
import matplotlib.pyplot as plt
import random
import struct
from scipy.stats import gaussian_kde

inFileName = r"C:\Users\wangh\Desktop\AVAS_Linux\OutputFile\BeamSet.plt"
index = 1
typec = 1
boundary = 0.05
figName0 = r"NH_N_"
figName1 = r"NH_P_"
figNames = r"NH_S_"

Nx = []
Nx_ = []
Ny = []
Ny_ = []
Nz = []
NE = []

Px = []
Px_ = []
Py = []
Py_ = []
Pz = []
PE = []

location = 0
#restmassMev = 938.271875
with open(inFileName, 'rb') as f:
    tdata = struct.unpack("<c", f.read(1))
    char1 = str(tdata[0])
    tdata = struct.unpack("<c", f.read(1))
    char2 = str(tdata[0])

    tdata = struct.unpack("<i", f.read(4))
    dumpPeriodicity = int(tdata[0])
    # print("输出间隔为{aa}".format(aa=self.dumpPeriodicity))

    tdata = struct.unpack("<i", f.read(4))
    numofp = int(tdata[0])
    # print("粒子数为：{aa}".format(aa=self.numofp))

    tdata = struct.unpack("<d", f.read(8))
    Ib = float(tdata[0])
    # print("流强为：{aa}mA".format(aa=self.Ib))

    tdata = struct.unpack("<d", f.read(8))
    freq = float(tdata[0])
    # print("频率为：{aa}MHz".format(aa=self.freq))

    tdata = struct.unpack("<d", f.read(8))
    BaseMassInMeV = float(tdata[0])
    # print("粒子静止质量为：{aa}MeV".format(aa=self.BaseMassInMeV))

    # 一步的字节数
    byte_onestep = 1 + 4 + 4 + 8 + 8 + (48 + 8) * numofp
    f.seek(index * byte_onestep, 1)

    tdata = struct.unpack("<c", f.read(1))

    tpyecc = struct.unpack("<i", f.read(4))
    tp = int(tpyecc[0])
    # print("tpye", tpye)

    Indexcc = struct.unpack("<i", f.read(4))
    tmp_index = int(Indexcc[0])
    # print("index", Index)

    timecc = struct.unpack("<d", f.read(8))
    time = float(timecc[0])
    # print(time)

    locationcc = struct.unpack("<d", f.read(8))
    location = float(locationcc[0])

    # print("location", location)
    # for i in range(self.numofp):
    #     vdata1 = struct.unpack("<dddddd", f.read(48))
    #     vdata2 = struct.unpack("<ii", f.read(8))
    #
    #     vdata = list(vdata1) + list(vdata2)
    #     self.one_step_list.append(vdata)
    data = np.frombuffer(f.read((48 + 8) * numofp), dtype=np.dtype([
        ('x', '<f8'), ('xp', '<f8'), ('y', '<f8'), ('yp', '<f8'), ('z', '<f8'), ('zp', '<f8'),
        ('id', '<i4'), ('status', '<i4')
    ]))
    data = [list(row) for row in data]

    for particle in data:
        x, xp, y, yp, z, zp, idx, lossf = particle[0:8]
        Ek = (math.sqrt(1 + pow(xp, 2) + pow(yp, 2) + pow(zp, 2)) - 1) * BaseMassInMeV
        if abs(z) <= 0.05:
            if idx > 0.5:
                Px.append(x * 1000)
                Px_.append(xp/zp * 1000)
                Py.append(y * 1000)
                Py_.append(yp/zp * 1000)
                Pz.append(z)
                PE.append(Ek)
        else:
            if idx > 0.5:
                Nx.append(x * 1000)
                Nx_.append(xp / zp * 1000)
                Ny.append(y * 1000)
                Ny_.append(yp / zp * 1000)
                Nz.append(z)
                NE.append(Ek)

print("N_Num: ", len(Nx))
print("P_Num: ", len(Px))
if typec == 0:
    # -------------------------------------N x-x'-----------------------
    x = np.array(Nx)
    y = np.array(Nx_)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]
    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    font1 = {'family': 'Times New Roman',
             'weight': 'bold',
             'size': 24}
    plt.figure(num = 1, figsize=(20, 12))
    plt.subplot(221)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("x(mm)", font1)
    plt.ylabel("x'(mrad)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-5, 5])
    # plt.ylim([-0.7, 0.7])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-0.6, -0.3, 0, 0.3, 0.6], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------N y-y'-----------------------
    x = np.array(Ny)
    y = np.array(Ny_)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    plt.subplot(222)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("y(mm)", font1)
    plt.ylabel("y'(mrad)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-6, 6])
    # plt.ylim([-0.9, 0.9])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-0.6, -0.3, 0, 0.3, 0.6], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------N z-E-----------------------
    x = np.array(Nz)
    y = np.array(NE)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    plt.subplot(223)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("z(m)", font1)
    plt.ylabel("Energy(MeV)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-70, 70])
    # plt.ylim([619.75, 622.25])
    # plt.xticks([-0.01, -0.005, 0, 0.005, 0.01], fontsize=16,family='Times New Roman',weight = 'bold')
    # plt.yticks([620, 620.50, 621, 621.50, 622], fontsize=16,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------N x-y-----------------------
    x = np.array(Nx)
    y = np.array(Ny)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    plt.subplot(224)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("x(mm)", font1)
    plt.ylabel("y(mm)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-70, 70])
    # plt.ylim([-70, 70])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.savefig(figName0 + str(location) + ".png", dpi=400, bbox_inches='tight')
    plt.show()

    # -------------------------------------P x-x'-----------------------
    x = np.array(Px)
    y = np.array(Px_)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]
    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    font1 = {'family': 'Times New Roman',
             'weight': 'bold',
             'size': 24}
    plt.figure(num = 2, figsize=(20, 12))
    plt.subplot(221)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("x(mm)", font1)
    plt.ylabel("x'(mrad)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-5, 5])
    # plt.ylim([-0.7, 0.7])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-0.6, -0.3, 0, 0.3, 0.6], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------P y-y'-----------------------
    x = np.array(Py)
    y = np.array(Py_)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    plt.subplot(222)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("y(mm)", font1)
    plt.ylabel("y'(mrad)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-6, 6])
    # plt.ylim([-0.9, 0.9])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-0.6, -0.3, 0, 0.3, 0.6], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------P z-E-----------------------
    x = np.array(Pz)
    y = np.array(PE)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    plt.subplot(223)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("z(m)", font1)
    plt.ylabel("Energy(MeV)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-70, 70])
    # plt.ylim([619.75, 622.25])
    # plt.xticks([-0.01, -0.005, 0, 0.005, 0.01], fontsize=16,family='Times New Roman',weight = 'bold')
    # plt.yticks([620, 620.50, 621, 621.50, 622], fontsize=16,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------P x-y-----------------------
    x = np.array(Px)
    y = np.array(Py)

    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]

    maxcoloebar = 0
    for i in range(len(z)):
        if z[i] > maxcoloebar:
            maxcoloebar = z[i]

    for i in range(len(z)):
        z[i] = z[i] / maxcoloebar

    plt.subplot(224)
    plt.scatter(x, y, c=z, s=4.0, cmap='Spectral_r', vmin=0, vmax=1.0)
    plt.colorbar()
    plt.xlabel("x(mm)", font1)
    plt.ylabel("y(mm)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-70, 70])
    # plt.ylim([-70, 70])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.savefig(figName1 + str(location) + ".png", dpi=400, bbox_inches='tight')
    plt.show()

else:

    font1 = {'family': 'Times New Roman',
             'weight': 'bold',
             'size': 24}
    plt.figure(num = 1, figsize=(10, 6))
    plt.subplot(221)
    plt.scatter(Nx, Nx_, s=4.0, c="steelblue")
    plt.scatter(Px, Px_, s=4.0, c="darkred")
    plt.xlabel("x(mm)", font1)
    plt.ylabel("x'(mrad)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-5, 5])
    # plt.ylim([-0.7, 0.7])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-0.6, -0.3, 0, 0.3, 0.6], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------y-y'-----------------------
    plt.subplot(222)
    plt.scatter(Ny, Ny_, s=4.0, c="steelblue")
    plt.scatter(Py, Py_, s=4.0, c="darkred")
    plt.xlabel("y(mm)", font1)
    plt.ylabel("y'(mrad)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-6, 6])
    # plt.ylim([-0.9, 0.9])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-0.6, -0.3, 0, 0.3, 0.6], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------Phi-E-----------------------
    plt.subplot(223)
    plt.scatter(Nz, NE, s=4.0, c="steelblue")
    plt.scatter(Pz, PE, s=4.0, c="darkred")
    plt.xlabel("z(m)", font1)
    plt.ylabel("Energy(MeV)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-70, 70])
    # plt.ylim([619.75, 622.25])
    # plt.xticks([-0.01, -0.005, 0, 0.005, 0.01], fontsize=16,family='Times New Roman',weight = 'bold')
    # plt.yticks([620, 620.50, 621, 621.50, 622], fontsize=16,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    # -------------------------------------Phi-E-----------------------
    plt.subplot(224)
    plt.scatter(Nx, Ny, s=4.0, c="steelblue")
    plt.scatter(Px, Py, s=4.0, c="darkred")
    plt.xlabel("x(mm)", font1)
    plt.ylabel("y(mm)", font1)
    plt.grid(linestyle="--")
    # plt.xlim([-70, 70])
    # plt.ylim([-70, 70])
    # plt.xticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    # plt.yticks([-4.0, -2.0, 0, 2.0, 4.0], fontsize=20,family='Times New Roman',weight = 'bold')
    plt.xticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.yticks(fontsize=20, family='Times New Roman', weight='bold')
    plt.tight_layout()
    plt.savefig(figNames + str(location) + ".png", dpi=400, bbox_inches='tight')
    plt.show()

