from utils.treatfile import delete_file
import os

def change_end_crlf(file):
    """
    Change the end of the file
    将Windows文件的回车换行符改变成Linux的换行符
    """
    with open(file, 'rb') as infile:  # 使用二进制模式读取文件
        content = infile.read()

    # 使用 bytes 类型的替换方法
    content = content.replace(b'\r\n', b'\n')

    with open(file, 'wb') as outfile:  # 使用二进制模式写入文件
        outfile.write(content)

def read(file):
    with open(file, 'rb') as infile:  # 使用二进制模式读取文件
        content = infile.read()
    print(repr(content))  # 使用 repr() 函数显示隐藏字符

if __name__ == '__main__':
    file1 = r"C:\Users\shliu\Desktop\jiqun\test_err_dyn\InputFile\lattice_mulp.txt"

    path = r"C:\Users\shliu\Desktop\yun3\cafe_avas"
    beam_path = os.path.join(path, "InputFile", "beam.txt")
    input_path = os.path.join(path, "InputFile", "input.txt")
    change_end_crlf(beam_path)
    change_end_crlf(input_path)


    # file1 = r"C:\Users\shliu\Desktop\jiqun\lattice_cuowu2.txt"
    # # change_end(file)
    # read(file1)
    #
    # file2 = r"C:\Users\shliu\Desktop\jiqun\lattice_biaozhun.txt"
    # # change_end(file)
    # read(file2)