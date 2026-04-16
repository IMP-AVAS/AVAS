from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton,
                             QCheckBox, QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox)
from PyQt5.QtGui import QTextDocument, QTextCharFormat, QColor, QTextCursor

from PyQt5.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QTextEdit,
                             QHBoxLayout, QFrame, QApplication,
                             QCompleter, QInputDialog)
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QSyntaxHighlighter, QTextCharFormat, QFont, QTextDocument, QTextCursor
from PyQt5.QtCore import Qt, QRect, QRegExp, QSize, QPoint
import sys
from PyQt5.QtWidgets import QPushButton, QDialog, QLineEdit, QVBoxLayout

from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import QRegExp
import time
from PyQt5.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor
)
from PyQt5.QtCore import QRegExp

class FindReplaceDialog(QDialog):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setWindowTitle("Replace")
        self.setFixedSize(400, 200)

        # 查找框
        self.find_label = QLabel("Find(N):")
        self.find_input = QLineEdit()

        # 替换框
        self.replace_label = QLabel("Replace(P):")
        self.replace_input = QLineEdit()

        # 复选框选项
        self.case_sensitive = QCheckBox("CaseSensitive(C)")
        self.loop_search = QCheckBox("Circulation(R)")
        self.loop_search.setChecked(True)  # 默认开启循环搜索

        # 按钮
        self.find_next_button = QPushButton("Next(F)")
        self.replace_button = QPushButton("Replace(R)")
        self.replace_all_button = QPushButton("Replace all(A)")
        self.cancel_button = QPushButton("Cancel")

        # 连接信号
        self.find_next_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace_current)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.cancel_button.clicked.connect(self.close)

        # 布局
        layout = QVBoxLayout()
        find_layout = QHBoxLayout()
        find_layout.addWidget(self.find_label)
        find_layout.addWidget(self.find_input)

        replace_layout = QHBoxLayout()
        replace_layout.addWidget(self.replace_label)
        replace_layout.addWidget(self.replace_input)

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.loop_search)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.find_next_button)
        button_layout.addWidget(self.replace_button)
        button_layout.addWidget(self.replace_all_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(find_layout)
        layout.addLayout(replace_layout)
        layout.addLayout(options_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)


    def show_error_message(self, message):
        """ 显示错误信息的弹窗 """
        QMessageBox.warning(self, "error", message)

    def find_next(self):
        """ 查找下一个匹配项，并高亮显示 """
        find_text = self.find_input.text()
        if not find_text:  # 查找内容为空时，弹出提示
            self.show_error_message("Please enter what to find")
            return

        # 获取大小写匹配标志
        flags = QTextDocument.FindFlags()
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindCaseSensitively

        doc = self.editor.document()
        cursor = self.editor.textCursor()
        pos = cursor.position()

        # 查找匹配项
        match_cursor = doc.find(find_text, pos, flags)

        if match_cursor.isNull():  # 如果找不到
            if self.loop_search.isChecked():
                match_cursor = doc.find(find_text, 0, flags)  # 从头查找

                if match_cursor.isNull():
                    self.show_error_message("No match was found")
                    return
            else:
                self.show_error_message("No match was found")  # 未找到时显示提示
                return

        if not match_cursor.isNull():
            self.editor.setTextCursor(match_cursor)  # 选中匹配内容
            # self.highlight_selection(match_cursor)  # 调用高亮方法

    # def highlight_selection(self, cursor):
    #     """ 高亮当前选中的文本 """
    #     selection = QTextEdit.ExtraSelection()
    #
    #     # 创建文本格式
    #     fmt = QTextCharFormat()
    #     fmt.setBackground(QColor("#0078D7"))  # 设置背景为蓝色
    #     fmt.setForeground(QColor("red"))  # 设置前景色（字体颜色）为红色
    #
    #     selection.format = fmt  # 应用格式
    #     selection.cursor = cursor  # 应用到当前匹配的 cursor
    #
    #     self.editor.setExtraSelections([selection])  # 应用样式

    def replace_current(self):
        """ 替换当前选中的匹配项 """
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()

        # 检查查找内容是否为空
        if not find_text:
            self.show_error_message("Please enter what to find")
            return

        # 检查替换内容是否为空
        if not replace_text:
            self.show_error_message("Please enter a replacement")
            return

        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(replace_text)
        else:
            self.show_error_message("Search for a match and then replace it")

    def replace_all(self):
        """ 替换文档中所有匹配项 """
        find_text = self.find_input.text()
        if not find_text:  # 如果查找框为空，不执行替换
            self.show_error_message("Please enter what to find")
            return

        replace_text = self.replace_input.text()
        if not replace_text:  # 如果替换框为空，不执行替换
            self.show_error_message("Please enter a replacement")
            return

        # 获取大小写匹配标志
        flags = QTextDocument.FindFlags()
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindCaseSensitively  # 添加大小写匹配选项

        doc = self.editor.document()
        cursor = doc.find(find_text, 0, flags)
        count = 0

        while not cursor.isNull():
            cursor.insertText(replace_text)
            count += 1
            cursor = doc.find(find_text, cursor.position(), flags)  # 继续查找下一个匹配项

        print(f"替换了 {count} 处匹配项")
        if count == 0:
            self.show_error_message("No match was found")


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = parent
        self.setWindowTitle("Find")

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText(" ")
        self.search_input.returnPressed.connect(self.find_text)

        self.search_button = QPushButton("Find", self)
        self.search_button.clicked.connect(self.find_text)

        layout = QVBoxLayout()
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_button)
        self.setLayout(layout)

    def find_text(self):
        search_text = self.search_input.text()
        if search_text:
            self.editor.find(search_text, QTextDocument.FindCaseSensitively)

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        # 定义不同命令的颜色
        self.command_formats = {
            'drift': QColor("black"),

            'field': QColor("green"),

            "steerer": QColor("blue"),
            "quad": QColor("blue"),
            "edge": QColor("blue"),
            "solenoid": QColor("blue"),
            "bend": QColor("blue"),

            "start": QColor("red"),
            "end": QColor("red"),
        }

        for command, color in self.command_formats.items():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            # 让匹配到的整行变色
            # 注意这里是 ^command.*$，即以 command 开头的一整行都着色
            self.rules.append((QRegExp(f"^{command}.*$"), fmt))

        # end 之后的颜色（灰色）
        self.gray_format = QTextCharFormat()
        self.gray_format.setForeground(QColor("gray"))

        # 约定：blockState=1 表示已经遇到过 "end"
        #      blockState=0 表示还没遇到 "end"

    def highlightBlock(self, text: str):
        """
        highlightBlock 会被每一行（block）调用一次。
        可以通过 previousBlockState() 获取上一行的状态，
        通过 setCurrentBlockState() 设置当前行的状态。
        """

        # 如果上一行已经是 "end" 状态，则整行置灰
        if self.previousBlockState() == 1:
            # print(self.previousBlockState())
            self.setFormat(0, len(text), self.gray_format)
            # 当前行依然保持 "end" 之后的状态
            self.setCurrentBlockState(1)
            return
        else:
            # 否则，先默认将当前行设置为“正常状态”
            self.setCurrentBlockState(0)

        # 先做你已有的关键字匹配
        for pattern, fmt in self.rules:
            match_index = pattern.indexIn(text)
            if match_index >= 0:
                self.setFormat(match_index, pattern.matchedLength(), fmt)

        # 检测当前行是否是 end
        if text.strip().lower() == "end":
            # 如果是，则本行后面的所有行都应该变灰
            self.setCurrentBlockState(1)
