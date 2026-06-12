from hpc.avasx_initializer import Avasx

if __name__ == "__main__":
    # 配置文件路径
    runtime_path = "/root/AVASX/Bend/A5/input.txt"
    beam_path = "/root/AVASX/Bend/A5/beam.txt"
    lattice_path = "/root/AVASX/Bend/A5/lattice_mulp.txt"
    #boundary_path = "/root/AVASX/Bend/A5/boundary.txt"

    # 运行
    avasx = Avasx(runtime_path, beam_path, lattice_path)
    avasx.run()
    avasx.release()