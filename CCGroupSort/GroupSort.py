# -*- coding: gbk -*-

import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QVBoxLayout, QDesktopWidget, QMessageBox, QFileDialog,
    QApplication, QCheckBox)
from PyQt5.QtGui import QIcon
import DataProcess
import NetworkFlow


class MyExample(QWidget):

    def __init__(self):
        """Initialize class"""

        # Set Default
        super().__init__()
        self._default_path = "./Result.xlsx"

        # Create Input part: Label & LineEdit
        input_label = QLabel('Input File')
        output_label = QLabel('Output File')
        self._input_edit = QLineEdit()
        self._input_edit.setText('')
        self._output_edit = QLineEdit()
        self._output_edit.setText(self._default_path)
        input_button = QPushButton('Open...', self)
        output_button = QPushButton('Open...', self)

        # Create CheckBox for algorithm
        self._diff_sheets = QCheckBox('Save group data in diffrent sheets')
        self._diff_sheets.setCheckable(True)
        self._diff_sheets.setChecked(True)
        self._ignore_member = QCheckBox('Divided into groups anyway')
        self._ignore_member.setCheckable(True)
        self._ignore_member.setChecked(True)

        # Create buttons for running
        self._status_label = QLabel('(Waiting)', self)
        run_button = QPushButton('Run', self)
        quit_button = QPushButton('Quit', self)

        # Connect signals and slots
        input_button.clicked.connect(self._get_input_file_name)
        output_button.clicked.connect(self._get_output_file_name)
        run_button.clicked.connect(self._slot_run)
        quit_button.clicked.connect(self._slot_close)

        # Box Layout
        input_box = QHBoxLayout()
        input_box.addWidget(input_label)
        input_box.addWidget(self._input_edit)
        input_box.addWidget(input_button)
        output_box = QHBoxLayout()
        output_box.addWidget(output_label)
        output_box.addWidget(self._output_edit)
        output_box.addWidget(output_button)
        check_box = QHBoxLayout()
        check_box.addWidget(self._diff_sheets)
        check_box.addWidget(self._ignore_member)
        check_box.addStretch(10)
        button_box = QHBoxLayout()
        button_box.addWidget(self._status_label)
        button_box.addStretch(10)
        button_box.addWidget(run_button)
        button_box.addWidget(quit_button)
        main_box = QVBoxLayout()
        main_box.addLayout(input_box)
        main_box.addLayout(output_box)
        main_box.addLayout(check_box)
        main_box.addStretch(10)
        main_box.addLayout(button_box)
        self.setLayout(main_box)

        # Create Window
        self.resize(480, 80)
        self._move_center()
        self.setWindowTitle('Group Sort')
        self.setWindowIcon(QIcon('icon.ico'))

        return

    def _move_center(self):
        """Move window into the center of desktop"""
        qr = self.frameGeometry()
        point_center = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(point_center)
        self.move(qr.topLeft())

    def _slot_run(self):
        """Running the algorithm"""

        confirm_string = 'Are you sure to begin grouping?\n'
        self._status_label.setText('(Processing...)')
        reply = QMessageBox.question(self,
                                     'Confirm',
                                     confirm_string,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            # input
            (raw_data, key_data) = DataProcess.read_data(self._input_edit.text())
            # network flow
            pro_data = NetworkFlow.main_loop(key_data)
            # ignore_member
            if self._ignore_member.isChecked():
                res_data = DataProcess.ignore_sort(pro_data)
            else:
                res_data = pro_data
            # add other information
            final_data = DataProcess.add_other_data(raw_data, res_data)
            # write data
            DataProcess.write_data(self._output_edit.text(),
                                   final_data,
                                   self._diff_sheets.isChecked())
            QMessageBox.information(self,
                                    "Information",
                                    "Grouping has been finished.",
                                    QMessageBox.Yes)
            self._status_label.setText('(Waiting)')
        else:
            self._status_label.setText('(Waiting)')
        return

    def _slot_close(self):
        """Close the window"""
        reply = QMessageBox.question(self,
                                     'Confirm',
                                     "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
        return

    def _get_input_file_name(self):
        """Get input file name by QFileDialog"""
        file_path = QFileDialog.getOpenFileName(parent=self)
        if file_path[0] != '':
            self._input_edit.setText(file_path[0])
            self._output_edit.setText(self._default_path)
        return

    def _get_output_file_name(self):
        """Get output file name by QFileDialog"""
        file_path = QFileDialog.getOpenFileName(parent=self)
        if file_path[0] != "":
            self._output_edit.setText(file_path[0])
        return


def main():
    app = QApplication(sys.argv)

    ex = MyExample()
    ex.show()

    sys.exit(app.exec_())
    return

if __name__ == '__main__':
    main()
