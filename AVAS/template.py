import os.path


from utils.change_win_to_linux import change_end_crlf
if __name__ == '__main__':
    path = r"C:\Users\shliu\Desktop\yun3\cafe_avas"
    beam_path = os.path.join(path, "InputFile", "beam.txt")
    input_path = os.path.join(path, "InputFile", "input.txt")
    change_end_crlf(beam_path)
    change_end_crlf(input_path)

    # basic_mulp(path)
    #
    # # project_path = r'C:\Users\shliu\Desktop\test812\CAFE'
    # #
    #
    # import multiprocessing
    # process = multiprocessing.Process(target=basic_mulp,
    #                                   args=(project_path,))
    #
    # process.start()  # 启动子进程
    # process.join()  # 等待子进程运行结束
