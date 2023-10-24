"""
this python is used to read and plot pressure values got
from Leybold pressure gauge ITR90 via a serial port in real time
we warp the gui with QyQt5 and plot the graphs with pyqtgraph
pressure values are read via pylablib.devices leybold

the gui is created with qtdesigner and then convert to a python file
pyuic5 -x filename.ui -o filename.py

creater: Prof. Dr. Dongdong Zhang
date: 2023.03.08
"""

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from pylablib.devices import Leybold
import serial
import gui
from gui3 import Ui_Form
import sys
import glob
import time
import numpy as np
import pyqtgraph as pg
from datetime import datetime
from random import randint

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class MainWindow(QMainWindow,Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.time = ''
        self.clearGraphs_gui = pyqtSignal()

        # self.pushButton.clicked.connect(self.the_button_was_clicked)
        self.pushButton.clicked.connect(self.OnCOM)
        self.pushButton_2.clicked.connect(self.startploting)
        self.pushButton_3.clicked.connect(self.ClearGraphs)
        self.x = list(range(1))  # 100 time points
        self.y = [randint(0,100)]  # 100 data points
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.widget.plot(self.x, self.y, pen=pen)

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def OnCOM(self):
        self.comboBox.clear()
        self.ports = serial_ports()
        i=0
        for port in self.ports:
            self.comboBox.addItem("")
            self.comboBox.setItemText(i, port)
            i+=1
        return
    def update_plot_data(self):
        # self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        # self.y = self.y[1:]  # Remove the first
        self.y.append(randint(0,100))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.
    # def the_button_was_clicked(self):
    #     self.time = str(datetime.now())
    #     self.textBrowser.setPlainText(self.time)
    def startploting(self):

        return
    def ClearGraphs(self):
        self.widget.clear()
        return


if __name__ == "__main__":

    app = QApplication(sys.argv)
    Form = MainWindow()
    # ui = gui3.Ui_Form()
    # ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())