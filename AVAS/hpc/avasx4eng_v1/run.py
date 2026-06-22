from avasx4eng_initializer import Avasx4Eng

if __name__ == "__main__":
    # 配置文件路径
    runtime_path = "/root/AVASX4ENG/Bend/A5/input.txt"
    beam_path = "/root/AVASX4ENG/Bend/A5/beam.txt"
    lattice_path = "/root/AVASX4ENG/Bend/A5/lattice"
    #boundary_path = "config/boundary.txt"

    # 运行
    avasx = Avasx4Eng(runtime_path, beam_path, lattice_path)
    avasx.run()
    #avasx.release()
