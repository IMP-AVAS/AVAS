"""此文件为计算twiss参数"""
import numpy
import math
import struct

class CalTwiss(object):

    def __init__(self, inFileName):
        self.__C_light = 299792458

        self.number = -1
        self.Ib = -1
        self.freq = -1
        self.particleData = []
        self.BaseMassInMeV = -1
        self.energy = -1
        self.phase = -1
        self.beta = -1
        self.gamma = -1
        self.RMSE = -1
        self.inFileName = inFileName
        self.emitxx = []
        self.emityy = []
        self.emitzz = []

    def get_data(self):
        inFileName = self.inFileName

        f = open(inFileName, 'rb')
        f.read(2)
        tdata = struct.unpack("<i", f.read(4))
        self.number = int(tdata[0])

        tdata = struct.unpack("<d", f.read(8))
        self.Ib = float(tdata[0])

        tdata = struct.unpack("<d", f.read(8))
        self.freq = float(tdata[0])

        # print(self.number)
        # print(self.Ib)
        # print(self.freq)
        f.read(1)

        xdata = numpy.arange(6 * self.number, dtype='float64').reshape(self.number, 6)

        for i in range(self.number):
            tdata = f.read(48)
            tdata = struct.unpack("<dddddd", tdata)
            xdata[i, 0] = tdata[0]
            xdata[i, 1] = tdata[1]
            xdata[i, 2] = tdata[2]
            xdata[i, 3] = tdata[3]
            xdata[i, 4] = tdata[4]
            xdata[i, 5] = tdata[5]

        tdata = struct.unpack("<d", f.read(8))
        self.BaseMassInMeV = tdata[0]
        f.close()
        #print(self.BaseMassInMeV)
        for i in range(self.number):
            row = []
            row.append(xdata[i, 0])
            row.append(xdata[i, 1])
            row.append(xdata[i, 2])
            row.append(xdata[i, 3])
            row.append(xdata[i, 4])
            row.append(xdata[i, 5])
            self.particleData.append(row)

        self.energy = 0
        self.phase = 0
        for row in self.particleData:
            self.energy += row[5]    #总能量
            self.phase += row[4] / math.pi * 180

        self.energy = self.energy / self.number        #平均能量
        self.phase = self.phase / self.number          #

        eSizeRms = 0
        for row in self.particleData:
            eSizeRms += math.pow((row[5] - self.energy), 2)
        eSizeRms = math.sqrt(eSizeRms / self.number)
        self.RMSE = eSizeRms / self.energy

        self.gamma = 1 + self.energy / self.BaseMassInMeV
        self.beta = math.sqrt(1 - 1.0 / self.gamma / self.gamma)

        self.EEenergy()
        self. EenergyRMS()
        self.PaNumber()
        self.emitxx_()
        self.emityy_()
        self.emitzz_()
        # print(self.BaseMassInMeV)
        #print(self.gamma)
        #print(self.beta)
        #print(eSizeRms)

    def EEenergy(self):
        return self.energy

    def EenergyRMS(self):
        return self.RMSE

    def PaNumber(self):
        return self.number

    def emitxx_(self):
        sumx = 0
        sumx_ = 0
        maxx = 0
        for row in self.particleData:
            if(maxx < abs(row[0] * 10)):
                maxx = abs(row[0] * 10)
            sumx += row[0] * 10
            sumx_ += row[1] * 1000
        averageX = sumx / self.number
        averageX_ = sumx_ / self.number

        f1 = 0
        f2 = 0
        f3 = 0
        for row in self.particleData:
            f1 += math.pow((row[0] * 10 - averageX), 2)
            f2 += math.pow((row[1] * 1000 - averageX_), 2)
            f3 += (row[0] * 10 - averageX) * (row[1] * 1000 - averageX_)

        alpha = -1 * (f3/self.number)
        f1 = f1/self.number
        f2 = f2/self.number
        beta = f1
        f3 = (f3/self.number)**2

        RmsX = math.sqrt(f1)
        emit = math.sqrt(f1 * f2 - f3)
        parameter = []
        alpha = alpha / emit
        beta = beta / emit
        gam = (1 + alpha ** 2) / beta

        parameter.append(alpha)
        parameter.append(beta)
        #parameter.append(math.sqrt(beta * emit))
        #parameter.append(math.sqrt(gam * emit))
        parameter.append(emit * self.beta * self.gamma)
        parameter.append(RmsX)
        parameter.append(averageX)
        parameter.append(maxx)
        self.emitxx = parameter
        return self.emitxx

    def emityy_(self):
        sumy = 0
        sumy_ = 0
        maxy = 0
        for row in self.particleData:
            if (maxy < abs(row[2] * 10)):
                maxy = abs(row[2] * 10)
            sumy += row[2] * 10
            sumy_ += row[3] * 1000
        averagey = sumy / self.number
        averagey_ = sumy_ / self.number

        f1 = 0
        f2 = 0
        f3 = 0
        for row in self.particleData:
            f1 += math.pow((row[2] * 10 - averagey), 2)
            f2 += math.pow((row[3] * 1000 - averagey_), 2)
            f3 += (row[2] * 10 - averagey) * (row[3] * 1000 - averagey_)

        alpha = -1 * (f3 / self.number)
        f1 = f1 / self.number
        f2 = f2 / self.number
        beta = f1
        f3 = (f3 / self.number) ** 2

        RmsY = math.sqrt(f1)
        emit = math.sqrt(f1 * f2 - f3)
        parameter = []
        alpha = alpha / emit
        beta = beta / emit
        gam = (1 + alpha ** 2) / beta

        parameter.append(alpha)
        parameter.append(beta)
        #parameter.append(math.sqrt(beta * emit))
        #parameter.append(math.sqrt(gam * emit))
        parameter.append(emit * self.beta * self.gamma)
        parameter.append(RmsY)
        parameter.append(averagey)
        parameter.append(maxy)
        self.emityy = parameter
        return self.emityy

    def emitzz_(self):
        z = []
        z_ = []
        for row in self.particleData:
            tmp_gamma = 1.0 + row[5] / self.BaseMassInMeV
            tmp_beta = math.sqrt(1 - 1.0 / tmp_gamma / tmp_gamma)
            tmp_speed = tmp_beta * self.__C_light
            speedz = math.sqrt(pow(tmp_speed, 2) / (pow(row[1], 2) + pow(row[3], 2) + 1))
            tmp_t0 = row[4] / (2 * math.pi * self.freq * 1000000)

            z.append(-1 * tmp_t0 * speedz * 1000)
            z_.append(speedz)

        sumz = 0
        sumz_ = 0
        maxz = 0
        for i in range(len(z)):
            if (maxz < abs(z[i])):
                maxz = abs(z[i])
            sumz += z[i]
            sumz_ += z_[i]
        averagez = sumz / self.number
        averagez_ = sumz_ / self.number

        for i in range(len(z_)):
            z_[i] = (z_[i] - averagez_) / z_[i] * 1000#self.beta/self.__C_light * 1000

        sumz_ = 0
        for i in range(len(z)):
            sumz_ += z_[i]
        averagez_ = sumz_ / self.number

        ySize = 0
        for i in range(len(z)):
            if abs(z[i] - averagez) > ySize:
                ySize = (z[i] - averagez)

        ySizeRms = 0
        for i in range(len(z)):
            ySizeRms += math.pow((z[i] - averagez), 2)
        ySizeRms = math.sqrt(ySizeRms / self.number)



        x_Size = 0
        for i in range(len(z_)):
            if abs(z_[i] - averagez_) > x_Size:
                x_Size = (z_[i] - averagez_)

        x_SizeRms = 0
        for i in range(len(z_)):
            x_SizeRms += math.pow((z_[i] - averagez_), 2)
        x_SizeRms = math.sqrt(x_SizeRms / self.number)



        f1 = 0
        f2 = 0
        f3 = 0
        for i in range(len(z)):
            f1 += math.pow((z[i] - averagez), 2)
            f2 += math.pow((z_[i] - averagez_), 2)
            f3 += (z[i] - averagez) * (z_[i] - averagez_)

        alpha = -1 * (f3 / self.number)
        f1 = f1 / self.number
        f2 = f2 / self.number
        beta = f1
        f3 = (f3 / self.number) ** 2

        RmsZ = math.sqrt(f1)
        emit = math.sqrt(f1 * f2 - f3)
        parameter = []
        alpha = alpha / emit
        beta = beta / emit
        gam = (1 + alpha ** 2) / beta

        parameter.append(alpha)
        parameter.append(beta)
        #parameter.append(math.sqrt(beta * emit))
        #parameter.append(math.sqrt(gam * emit))
        parameter.append(emit * self.beta * self.gamma)
        parameter.append(RmsZ)
        parameter.append(averagez_)
        parameter.append(maxz)
        self.emitzz = parameter
        return self.emitzz

    def get_emit_xyz(self):
        self.get_data()
        self.emitxx_()
        self.emityy_()
        self.emitzz_()
        return [self.emitxx, self.emityy, self.emitzz]


if __name__ == "__main__":
    a = CalTwiss(r"C:\Users\shliu\Desktop\2brfq\inputFile\part_input.dst")
#     # a.input(r"C:\Users\anxin\Desktop\cafe_avas\InputFile\part_rfq.dst")
    print(a.get_emit_xyz())













