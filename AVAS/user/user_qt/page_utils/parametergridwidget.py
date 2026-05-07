import os

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QDoubleSpinBox,
    QComboBox,
    QRadioButton,
    QMessageBox,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
)

class ParameterGridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(8)

        self.grid.setColumnStretch(0, 0)
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(2, 0)

        self.row_count = 0

    def add_row(self, title, edit, unit=""):
        lab = QLabel(title)
        lab.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.grid.addWidget(lab, self.row_count, 0)
        self.grid.addWidget(edit, self.row_count, 1)

        unit_label = QLabel(unit)
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.grid.addWidget(unit_label, self.row_count, 2)

        self.row_count += 1

    def add_rows(self, rows):
        """
        rows 格式：
        [
            ("Charge", self.text_charge, "e"),
            ("Mass", self.text_mass, "MeV"),
        ]
        """
        for row in rows:
            if len(row) == 2:
                title, edit = row
                unit = ""
            elif len(row) == 3:
                title, edit, unit = row
            else:
                raise ValueError("Each row must be (title, edit) or (title, edit, unit).")

            self.add_row(title, edit, unit)