import math
import numpy
import struct

inFileName = r"C:\Users\wangh\Desktop\test_mu\mu_all_avas\OutputFile\outData_16.718114.txt"
outFileName = r"C:\Users\wangh\Desktop\test_mu\mu_all_avas\OutputFile\outData_2026.dst"

freq = 162.5e6
particleRestMass = 105.65837450
#particleRestMass = 938.271875
radius = 0.25
#radius = 0.06
Ib = 0
#--------------------------------------------------------------------------------------
data = numpy.loadtxt(inFileName, dtype=float)
number = len(data)

centertime = 0
countNum = 0
for i in range(number):
    if (math.sqrt(data[i][1] * data[i][1] + data[i][3] * data[i][3]) <= radius):
        centertime += data[i][5]
        countNum += 1
centertime = centertime / countNum

print(countNum)

validdata = []
for i in range(number):
    if(math.sqrt(data[i][1] * data[i][1] + data[i][3] * data[i][3]) <= radius):
        gamma = math.sqrt(1 + pow(data[i][2], 2) + pow(data[i][4], 2) + pow(data[i][6], 2))
        tmp = []
        tmp.append(data[i][1] * 100)
        tmp.append(data[i][2] / data[i][6])
        tmp.append(data[i][3] * 100)
        tmp.append(data[i][4] / data[i][6])
        tmp.append((data[i][5] - centertime) * math.pi * 2 * freq)
        tmp.append((gamma - 1) * particleRestMass)
        validdata.append(tmp)

f = open(outFileName, 'wb')
data = struct.pack('<B', 125)
f.write(data)
data = struct.pack('<B', 100)
f.write(data)
data = struct.pack('<i', countNum)
f.write(data)
data = struct.pack('<d', Ib)
f.write(data)
data = struct.pack('<d', freq/(1.0e6))
f.write(data)
data = struct.pack('<B', 125)
f.write(data)

for i in range(len(validdata)):
    data = struct.pack('<dddddd', validdata[i][0], validdata[i][1], validdata[i][2], validdata[i][3], validdata[i][4], validdata[i][5])
    f.write(data)
data = struct.pack('<d', particleRestMass)
f.write(data)
f.close()