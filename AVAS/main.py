import sys

from PyQt5.QtWidgets import QApplication, QMessageBox
from user.user_qt.user_pyqt import MainWindow
import multiprocessing
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    multiprocessing.freeze_support()

    def exception_handler(type, value, traceback):
        # 显示错误信息
        QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred:\n{value}")
        # 输出到控制台（调试用）
        sys.__excepthook__(type, value, traceback)


    # 将全局异常处理器设置为自定义的函数
    sys.excepthook = exception_handler


    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())

