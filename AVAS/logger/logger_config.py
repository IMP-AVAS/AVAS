# logger_config.py
# import logging
#
# def setup_logger(level=logging.INFO):
#     logging.basicConfig(
#         level=level,
#         format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
#         datefmt="%Y-%m-%d %H:%M:%S"
#     )
#
# DEBUG    ❌（被过滤）
# INFO     ✅
# WARNING  ✅
# ERROR    ✅
# CRITICAL ✅
import time
import logging
import os
from conf.setting import if_logger


script_directory = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在文件夹的绝对路径
parent_directory = os.path.dirname(script_directory)  # 获取上级目录的路径
logger_save_file = os.path.join(parent_directory, "logger", "logger_history")

timestamp = time.strftime("%Y%m%d")
log_filename = os.path.join(logger_save_file, timestamp + ".log")


def setup_logger(
    level=logging.INFO,
):
    if if_logger == 0:
        logging.disable(logging.CRITICAL)   # 禁用所有日志
        return

    # 1️⃣ 获取 root logger
    root = logging.getLogger()
    root.setLevel(level)

    # 2️⃣ 防止重复添加 handler（非常重要）
    if root.handlers:
        return

    # 3️⃣ 日志格式
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s |  %(filename)s:%(lineno)d  | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 4️⃣ 终端 handler（INFO 及以上）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # 5️⃣ 文件 handler（DEBUG 全量）
    file_handler = logging.FileHandler(
        log_filename,
        mode="a",
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # 6️⃣ 加到 root logger
    root.addHandler(console_handler)
    root.addHandler(file_handler)



# setup_logger(
#     level=logging.INFO,
#     log_file="app.log",
# )

# import logging
# from logger_config import setup_logger
#
# setup_logger(level=logging.INFO, log_file="run.log", if_logger=0)
#
# logger = logging.getLogger(__name__)
#
# logger.info("Program started")





# import logging
# from logger.logger_config import setup_logger
# logger = logging.getLogger(__name__)
