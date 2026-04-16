from PyQt5.QtWidgets import (QPlainTextEdit, QWidget, QVBoxLayout, QTextEdit,
                             QHBoxLayout, QFrame, QApplication,
                             QCompleter, QInputDialog)
from PyQt5.QtGui import QPainter, QColor, QTextFormat, QSyntaxHighlighter, QTextCharFormat, QFont, QTextDocument, QTextCursor, QIcon
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
from user.user_qt.lattice_file. latticeideuseclass import FindReplaceDialog, SearchDialog, SyntaxHighlighter
import global_varible

from PyQt5.QtGui import QFont, QFontDatabase

class LineNumberArea(QWidget):
    """行号区域，支持折叠功能"""
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

    def mousePressEvent(self, event):
        """检测是否点击了折叠符号，并触发折叠"""
        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top()

        while block.isValid():
            text = block.text().strip()
            if text.startswith("section"):  # 检测折叠标记
                symbol_rect = QRect(5, int(top), self.width() - 10, self.code_editor.fontMetrics().height())
                if symbol_rect.contains(event.pos()):  # 仅在折叠符号区域点击
                    self.code_editor.toggle_fold(block)
                    return

            block = block.next()
            block_number += 1
            top += self.code_editor.blockBoundingRect(block).height()

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        # font = QFont("Courier")
        # self.setFont(font)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)  # 系统默认等宽 TrueType
        font.setPointSize(12)
        font.setStyleHint(QFont.Monospace) #需要的是等宽字体（monospace），优先找等宽字体来匹配
        font.setFixedPitch(True) #每个字符宽度必须一致
        self.document().setDefaultFont(font)  # 关键：文档默认字体也要同步



        ##############################################
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.line_number_map = {}                # ✅ 提前
        self.max_logical_number = 1              # ✅ 可选：给宽度计算一个默认值
        self.last_index = -1


        self.line_number_area = LineNumberArea(self)

        self.highlighter = SyntaxHighlighter(self.document())
        self.folded_blocks = {}  # 存储折叠区域 { 起始block_number: [隐藏的block_number列表] }

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width()

        # self.line_number_map = {}
        # self.last_index = -1

        # self.keywords = [
        #     "drift", "drift2", "drift3",
        #     "field1", "field2", "field3",
        #     "soppose1", "soppose2", "soppose3"
        # ]

        self.keywords = [
            "drift length radius",
            "field length radius 0 fieldType frequency phase ke kb fieldMap",
            'quad length radius 0 gradient',
            'solenoid length radius 0 gradient',
            "bend length radius plc radius gradient direction",
            "steer length radius plc bx\ex by\ey type max_value",
            'edge 0 radius 0 angle radius gap k1 k2 direction'

        ]

        # 初始化 QCompleter
        self.completer = QCompleter(self.keywords, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)  # 大小写不敏感
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)  # 设置补全弹窗
        # self.completer.setFilterMode(Qt.MatchContains)  # 支持匹配中间部分
        self.completer.activated.connect(self.insert_completion)  # 选中项时插入

        self.textChanged.connect(self.on_text_changed)
        self.on_text_changed()

        self.index_v1 = 0

    # def set_font_size(self, size):
    #     """ 修改 CodeEditor 的字体大小 """
    #     font = self.font()  # 获取当前字体
    #     print("before:", font.pointSize(), font.pixelSize(), "-> request:", size)
    #     font.setPointSize(size)  # 设置新的字体大小
    #     self.setFont(font)  # 应用新的字体大小
    #     self.line_number_area.setFont(font)

    def zoom_editor(self, delta_steps: int):
        """delta_steps >0 放大，<0 缩小"""
        if delta_steps > 0:
            self.zoomIn(delta_steps)
        elif delta_steps < 0:
            self.zoomOut(-delta_steps)

        # 关键：同步行号区字体（用 editor 当前 font）
        self.line_number_area.setFont(self.font())

        # 关键：如果你行号栏宽度是动态的，字体变了要重算宽度
        self.update_line_number_area_width()
        # self.line_number_area.update()

    def line_number_area_width(self) -> int:
        """根据最大行号位数动态计算行号栏宽度（像素）"""
        # 这里用“可见的逻辑行号”或 blockCount 都行
        # 你如果想按 blockCount 来算：
        # max_num = max(1, self.blockCount())

        # 你现在的逻辑行号是 logical_number（元素计数），那就用它更贴合

        if self.line_number_map:
            max_num = max(1, max(self.line_number_map.keys()))  # 或者用你自己的最大 logical_number
        else:
            max_num = "12345"
        digits = len(str(max_num))
        # print(151, max_num, digits)


        fm = self.fontMetrics()
        # '9' 通常最宽，用它估计位数宽度
        text_width = fm.horizontalAdvance('9' * digits)

        padding = 12   # 左右留白（你还画了折叠符号，适当大点）
        fold_icon_space = 14  # 给 "▶" 留点空间（如果你要显示）
        return text_width + padding + fold_icon_space

    def update_line_number_area_width(self):
        w = self.line_number_area_width()
        if getattr(self, "_lnw", None) == w:
            return

        self._lnw = w
        # print(155, self._lnw)
        self.setViewportMargins(self._lnw, 0, 0, 0)
        self.line_number_area.setFixedWidth(w)


    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        # else:
        #     print(149, "光标触发")
        #     self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())


    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.contentsRect()
        #设置line_number_area的左上角和宽度
        self.line_number_area.setGeometry(QRect(rect.left(), rect.top(), 50, rect.height()))
        # print(157, "结束")
        # print("<<" * 30)
        # w = self.line_number_area_width()
        # self.line_number_area.setGeometry(QRect(rect.left(), rect.top(), w, rect.height()))

    def on_text_changed(self):
        # print(176, "文本变化")
        #只有文本变化，才重新计算
        self.update_line_numbers()  # ✅ 只在文本变化时重算
        # self.line_number_area.update()  # ✅ 让行号区重绘一次
        self.update_line_number_area_width()  # 如果你做动态宽度，可以在这里更新


    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(50, 50, 50, 50))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    #计算数字区域的号码
    def update_line_numbers(self):
        """扫描整个文档，重新计算行号"""
        self.line_number_map.clear()
        logical_number = -1  # 全局递增编号

        block = self.document().firstBlock()  # 获取文档的第一行
        while block.isValid():
            text = block.text().strip()
            # print(text)
            # if text.startswith("drift") or text.startswith("field"):
            # if any(text.startswith(prefix) for prefix in global_varible.all_element):

            text_lower = text.lower()
            if ":" in text_lower:
                text_lower = text_lower.split(":", 1)[1]

            if not text.startswith("!") and text_lower.split():
                first_word = text_lower.split()[0]
                if first_word in global_varible.all_element:
                    logical_number += 1  # 递增编号
                    self.line_number_map[block.blockNumber()] = logical_number

            elif text.startswith("end"):
                break
            block = block.next()  # 移动到下一个 block
        # print("line_number_map", self.line_number_map)



    def line_number_area_paint_event(self, event):
        """绘制行号（按 `drift` 或 `field` 递增）"""
        self.index_v1 += 1
        # print(224, "绘制区域", self.index_v1)
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)

        block = self.firstVisibleBlock()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            block_number = block.blockNumber()
            text = block.text().strip()

            # 绘制折叠标记
            if text.startswith("section"):
                painter.setPen(Qt.red)
                painter.drawText(5, int(top), self.line_number_area.width() - 10,
                                 int(self.fontMetrics().height()), Qt.AlignmentFlag.AlignLeft, "▶")

            # 获取正确的行号
            logical_number = self.line_number_map.get(block_number, -1)

            # 绘制行号
            if block.isVisible() and logical_number != -1:
                painter.setPen(Qt.black)
                painter.drawText(0, int(top), self.line_number_area.width() - 5,
                                 int(self.fontMetrics().height()), Qt.AlignmentFlag.AlignRight, str(logical_number))

            # 继续遍历下一个 block
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
        # print(241, "绘制区域结束")
        # print("<<" * 60)
    def insert_completion(self, completion=None):
        """ 插入补全文本（回车/鼠标选择） """
        if completion is None:
            completion = self.completer.currentCompletion()  # 获取当前高亮的选项
            if not completion:
                return  # 防止无效插入

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(self.completer.completionPrefix()))
        cursor.insertText(completion)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        """ 监听键盘输入，控制补全行为 """
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                selected_index = self.completer.popup().currentIndex()  # 获取当前选中的索引
                if selected_index.isValid():
                    completion = self.completer.completionModel().data(selected_index)  # 获取选中项
                    self.insert_completion(completion)  # 插入正确的补全项
                self.completer.popup().hide()
                return  # 阻止回车事件传递给 QPlainTextEdit
            elif event.key() in (Qt.Key_Escape, Qt.Key_Backspace):
                self.completer.popup().hide()
                return
            elif event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right):
                super().keyPressEvent(event)  # 让方向键正常移动光标
                return  # 阻止触发补全

        # 默认行为
        super().keyPressEvent(event)

        # 只允许字母 `A-Z` / `a-z` 触发补全
        if not event.text().isalpha():  # 非字母时，不触发补全
            self.completer.popup().hide()
            return

        # 获取当前光标所在单词
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        prefix = cursor.selectedText()


        if not prefix:
            self.completer.popup().hide()
            return

        self.completer.setCompletionPrefix(prefix)
        self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        rect = self.cursorRect()
        rect.setWidth(
            self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(rect)



    def toggle_fold(self, start_block):
        """折叠或展开 fold{ } 代码块"""
        block_number = start_block.blockNumber()
        cursor = self.textCursor()

        if block_number in self.folded_blocks:
            # 取消折叠，恢复可见
            for line in self.folded_blocks[block_number]:
                block = self.document().findBlockByNumber(line)
                block.setVisible(True)
            del self.folded_blocks[block_number]

            cursor.beginEditBlock()
            cursor.setPosition(start_block.position())
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            original_text = cursor.selectedText()
            if original_text.endswith("..."):  # 防止重复添加
                cursor.insertText(original_text[:-3])
            cursor.endEditBlock()
        else:
            # 计算折叠范围, 进行折叠
            lines = []
            block = start_block.next()
            while block.isValid():
                text = block.text().strip()
                if text.startswith("}"):  # 结束折叠
                    break
                lines.append(block.blockNumber())
                block.setVisible(False)
                block = block.next()

            if lines:
                self.folded_blocks[block_number] = lines
            if not lines:
                return 0

            cursor.beginEditBlock()
            cursor.setPosition(start_block.position())
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            original_text = cursor.selectedText()
            if not original_text.endswith("..."):  # 防止重复添加
                cursor.insertText(original_text + "...")
            cursor.endEditBlock()

        self.updateGeometry()
        self.viewport().update()
        self.line_number_area.update()

    def remove_comment(self):
        """在选中的每一行前，如果有 '! ' 则删除"""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return

        doc = cursor.document()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        start_block = doc.findBlock(start)  # 获取选区起始行
        end_block = doc.findBlock(end)  # 获取选区结束行

        cursor.beginEditBlock()  # 开始批量编辑

        block = start_block
        while block.isValid():
            block_text = block.text()

            if block_text.startswith("!"):  # 只有当行首是 "! " 时才移除
                block_cursor = QTextCursor(block)
                block_cursor.movePosition(QTextCursor.StartOfBlock)  # 移动到行首
                block_cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 1)  # 选中 "!"
                block_cursor.removeSelectedText()  # 删除 "! "

            if block == end_block:
                break  # 处理完最后一行后退出循环

            block = block.next()  # 移动到下一行

        cursor.endEditBlock()  # 结束批量编辑
    def add_comment(self):
        """在选中的每一行前添加 !"""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return

        doc = cursor.document()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        start_block = doc.findBlock(start)  # 选区的起始行
        end_block = doc.findBlock(end)  # 选区的结束行

        cursor.beginEditBlock()  # 开始批量编辑，支持撤销

        block = start_block
        while block.isValid():
            block_cursor = QTextCursor(block)
            block_cursor.movePosition(QTextCursor.StartOfBlock)
            block_cursor.insertText("!")  # 插入 `! `

            if block == end_block:
                break  # 处理完最后一行后退出

            block = block.next()  # 移动到下一行

        cursor.endEditBlock()  # 结束批量编辑



class CodeEditorWithLineNumbers(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()  # 竖直布局

        # 搜索按钮
        self.search_button = QPushButton("find", self)
        self.search_button.clicked.connect(self.open_search_dialog)
        # self.search_button.setFixedSize(50, 25)

        # 添加注释按钮
        self.comment_button = QPushButton("!", self)
        self.comment_button.clicked.connect(self.add_comment)
        # self.comment_button.setFixedSize(25, 25)

        # 取消注释按钮
        self.uncomment_button = QPushButton("x!", self)
        self.uncomment_button.clicked.connect(self.remove_comment)
        # self.uncomment_button.setFixedSize(25, 25)

        # **新增字体放大按钮**
        self.increase_font_button = QPushButton("A+", self)
        self.increase_font_button.clicked.connect(self.increase_font_size)
        # self.increase_font_button.setFixedSize(25, 25)

        # **新增字体缩小按钮**
        self.decrease_font_button = QPushButton("A-", self)
        self.decrease_font_button.clicked.connect(self.decrease_font_size)
        # self.decrease_font_button.setFixedSize(25, 25)

        self.replace_button = QPushButton("replace", self)
        self.replace_button.clicked.connect(self.open_replace_dialog)
        # self.replace_button.setFixedSize(50, 25)

        self.editor = CodeEditor()

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.replace_button)

        button_layout.addWidget(self.comment_button)
        button_layout.addWidget(self.uncomment_button)
        button_layout.addWidget(self.increase_font_button)  # 添加放大按钮
        button_layout.addWidget(self.decrease_font_button)  # 添加缩小按钮
        button_layout.addStretch(1)

        layout.addLayout(button_layout)
        layout.addWidget(self.editor)
        self.setLayout(layout)

        self.current_font_size = 12  # 记录当前字体大小

    def open_replace_dialog(self):
        """ 打开替换对话框 """
        dialog = FindReplaceDialog(self.editor)
        dialog.exec_()  # 以模态方式运行

    def increase_font_size(self):
        self.editor.zoom_editor(1)

    def decrease_font_size(self):
        self.editor.zoom_editor(-1)

    # def increase_font_size(self):
    #     """ 增加字体大小 """
    #     self.editor.zoomIn(3)
    #     self.editor.update_line_number_area_width()
    #     # self.current_font_size += 3
    #     # self.editor.set_font_size(self.current_font_size)
    #     #
    #     # # if self.current_font_size < 18:  # 设置最小字体大小
    #     # #     self.current_font_size += 3
    #     # #     self.editor.set_font_size(self.current_font_size)
    #     # print("增加后的大小", self.current_font_size)
    # def decrease_font_size(self):
    #     self.editor.zoomOut(3)
    #     self.editor.update_line_number_area_width()
    #     """ 减小字体大小 """
    #     # self.current_font_size -= 3
    #     # self.editor.set_font_size(self.current_font_size)
    #     #
    #     # # if self.current_font_size > 9:  # 设置最小字体大小
    #     # #     self.current_font_size -= 3
    #     # #     self.editor.set_font_size(self.current_font_size)
    #     # print("缩小后的大小", self.current_font_size)

    def open_search_dialog(self):
        dialog = SearchDialog(self.editor)
        dialog.exec_()

    def add_comment(self):
        """调用 CodeEditor 里的添加注释方法"""
        self.editor.add_comment()

    def remove_comment(self):
        """调用 CodeEditor 里的取消注释方法"""
        self.editor.remove_comment()
    def setPlainText(self, text):
        self.editor.setPlainText(text)
    def toPlainText(self):
        return self.editor.toPlainText()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = CodeEditorWithLineNumbers()
    print(530, ">>" * 60)
    editor.setPlainText(
        "drift      0.08513  0.02   0 \n"
        "field      0.35	   0.02     0   3   0   0   1    0.620137  sol_yuan \n"
        "field      0.21	   0.02     0   1   162.5e6   -31   1.68    -1.68   hwR010 \n"
        "drift      0.08513  0.02   0 \n"
        "field      0.35	   0.02     0   3   0   0   1    0.620137  sol_yuan \n"
        "field      0.21	   0.02     0   1   162.5e6   -31   1.68    -1.68   hwR010 \n"
        "drift      0.08513  0.02   0 \n"                                                                                                                                                                                      
        "field      0.35	   0.02     0   3   0   0   1    0.620137  sol_yuan \n"
        "field      0.21	   0.02     0   1   162.5e6   -31   1.68    -1.68   hwR010 \n"
        "drift      0.08513  0.02   0 \n"
        "field      0.35	   0.02     0   3   0   0   1    0.620137  sol_yuan \n"
        "field      0.21	   0.02     0   1   162.5e6   -31   1.68    -1.68   hwR010 \n"
        "drift      0.08513  0.02   0 \n"
        "section { \n"
        "field      0.35	   0.02     0   3   0   0   1    0.620137  sol_yuan \n"
        "field      0.21	   0.02     0   1   162.5e6   -31   1.68    -1.68   hwR010 \n"
        "drift      0.08513  0.02   0 \n"
        "}"
        "field      0.35	   0.02     0   3   0   0   1    0.620137  sol_yuan \n"
        "field      0.21	   0.02     0   1   162.5e6   -31   1.68    -1.68   hwR010 \n"
    )
    editor.show()
    sys.exit(app.exec_())
