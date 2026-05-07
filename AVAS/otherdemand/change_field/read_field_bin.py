import struct
import numpy as np
np.set_printoptions(threshold=np.inf)

def read_field_1d(filename):
    with open(filename, "rb") as f:

        # --- 读头 ---
        nz = struct.unpack("i", f.read(4))[0]
        zmax = struct.unpack("d", f.read(8))[0]

        nx = struct.unpack("i", f.read(4))[0]
        xmin = struct.unpack("d", f.read(8))[0]
        xmax = struct.unpack("d", f.read(8))[0]

        ny = struct.unpack("i", f.read(4))[0]
        ymin = struct.unpack("d", f.read(8))[0]
        ymax = struct.unpack("d", f.read(8))[0]

        # print("nz,nx,ny =", nz, nx, ny)
        # print("zmax,xmin,xmax,ymin,ymax,norm =", zmax, xmin, xmax, ymin, ymax)
        norm = struct.unpack("d", f.read(8))[0]

        total = (nz + 1) * (ny + 1) * (nx + 1)

        # 👉 直接读成一维
        data = np.fromfile(f, dtype=np.float32, count=total)

    header = dict(
        nz=nz, zmax=zmax,
        nx=nx, xmin=xmin, xmax=xmax,
        ny=ny, ymin=ymin, ymax=ymax,
        norm=norm
    )

    return header, data


def write_field_1d(filename, header, data):
    with open(filename, "wb") as f:
        f.write(struct.pack(
            "<ididdiddd",
            header["nz"], header["zmax"],
            header["nx"], header["xmin"], header["xmax"],
            header["ny"], header["ymin"], header["ymax"],
            header["norm"]
        ))

        data.astype(np.float32).tofile(f)


def add_one_to_field(infile, outfile):
    header, data = read_field_1d(infile)

    # 👉 一维数组直接加
    data += 1.0

    write_field_1d(outfile, header, data)


def save_field_to_txt(txtfile, header, data):
    with open(txtfile, "w", encoding="utf-8") as f:
        # 头部
        f.write(f"{header['nz']:12d}{header['zmax']:24.15E}\n")
        f.write(f"{header['nx']:12d}{header['xmin']:24.15E}{header['xmax']:24.15E}\n")
        f.write(f"{header['ny']:12d}{header['ymin']:24.15E}{header['ymax']:24.15E}\n")
        f.write(f"{header['norm']:12.0f}\n")

        # 数据区：每行一个值
        for v in data:
            f.write(f"{v:16.8f}\n")

def read_field_from_txt(txtfile):
    with open(txtfile, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 5:
        raise ValueError("txt 文件内容太少，至少需要 4 行头信息 + 数据。")

    # ---- 解析头部 ----
    line1 = lines[0].split()
    line2 = lines[1].split()
    line3 = lines[2].split()
    line4 = lines[3].split()

    if len(line1) != 2:
        raise ValueError(f"第1行头信息格式不对: {lines[0]}")
    if len(line2) != 3:
        raise ValueError(f"第2行头信息格式不对: {lines[1]}")
    if len(line3) != 3:
        raise ValueError(f"第3行头信息格式不对: {lines[2]}")
    if len(line4) != 1:
        raise ValueError(f"第4行头信息格式不对: {lines[3]}")

    header = {
        "nz": int(line1[0]),
        "zmax": float(line1[1]),

        "nx": int(line2[0]),
        "xmin": float(line2[1]),
        "xmax": float(line2[2]),

        "ny": int(line3[0]),
        "ymin": float(line3[1]),
        "ymax": float(line3[2]),

        "norm": float(line4[0]),
    }
    print(header)
    # ---- 解析数据区 ----
    data_list = []
    for i, line in enumerate(lines[4:], start=5):
        s = line.strip()
        if not s:
            continue
        try:
            data_list.append(float(s))
        except ValueError:
            raise ValueError(f"第{i}行不是合法浮点数: {line}")

    data = np.array(data_list, dtype=np.float32)

    # ---- 长度检查 ----
    expected = (header["nz"] + 1) * (header["ny"] + 1) * (header["nx"] + 1)
    if len(data) != expected:
        raise ValueError(
            f"数据长度不对: 读到 {len(data)} 个，"
            f"但根据头信息应为 {expected} 个 "
            f"= ({header['nz']}+1)*({header['ny']}+1)*({header['nx']}+1)"
        )

    return header, data


def txt_to_field_bin(txtfile, binfile):
    header, data = read_field_from_txt(txtfile)
    write_field_1d(binfile, header, data)
    print("txt 转二进制完成：", binfile)

if __name__ == "__main__":
    eader, data = read_field_from_txt(r"C:\Users\wangh\Desktop\test_2b\multipole4_1_3D.bsx")
    print(eader, data)
    # for i in range(1, 7):
    #     path1 = fr"C:\Users\shliu\Desktop\yanshou\error_b\InputFile\multipole4_{i}_3D.bsz"
    #     path2 = fr"C:\Users\shliu\Desktop\yanshou\error_b\InputFile\multipole4_{i}_3Db.bsz"
    #     txt_to_field_bin(path1, path2)
    #
    #     header, data = read_field_1d(path2)
    #     np.set_printoptions(threshold=np.inf)
    #
    #     # print(150, header )
    #     # print(151, data[:10] )


