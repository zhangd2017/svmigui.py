"""
this piece of python is used to read and display the pressure in real time
the pressure is read from a Leybold ITR90 pressure gauge via rs232 serial port
the gui is written in Qtdesigner, a ui file is saved and then convert to a py file
with the following command pyuic5 -x name.ui -o name.py
the gui.py (from the ui file) is then called in the main python program
graph update interval is adjustable with the variable interval

created by: Prof. Dr. Dongdong Zhang
date : 2023.03.10

todo:
1. add save function to save the starting time and pressure data into a file
2.
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime, pyqtSignal
from pyqtgraph import PlotWidget
import serial
import time
import glob
from gui import Ui_MainWindow
import sys
from datetime import datetime
from random import randint
import pyqtgraph as pg
from pylablib.devices import Leybold


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

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)

        self.graph.setBackground('white')
        self.x = list(range(1))  # 100 time points
        self.y = list(range(1)) # 100 data points

        # creating a timer object

        # adding action to timer
        # self.timer.timeout.connect(self.showTime)


        # update the timer every second

        self.connectport.clicked.connect(self.OnCOM)
        self.startplot.clicked.connect(self.plotgraph)
        self.clearplot.clicked.connect(self.ClearGraphs)


    def plotgraph(self):
        current_time = QDateTime.currentDateTime()
        # converting QTime object to string
        label_time = current_time.toString("dd.MM.yyyy, hh:mm:ss")
        # showing it to the label
        self.starttimetext.setPlainText(label_time)
        self.timer = QTimer(self)
        self.interval = 50
        self.timer.setInterval(self.interval)
        self.data_line = self.graph.plot(self.x, self.y, pen='red',\
                                         symbol='x', symbolPen='b', symbolBrush=0.2, name='pressure')
        self.graph.setLabel('left', 'pressure', units='mbar', fontsize = '28')
        self.graph.setLabel('bottom', 'Time', units='ms', fontsize = '28')
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.informationtext.setPlainText('action time is displayed above\nrelative time always start from 0, initial pressure is set to 0')
    def ClearGraphs(self):
        self.graph.clear()
        self.timer.stop()
        self.x = list(range(1))  # 100 time points
        self.y = list(range(1))  # 100 data points
        self.informationtext.setPlainText('action time is displayed above\nclear plot')
    def update_plot_data(self):
        self.x.append(self.x[-1] + self.interval)  # Add a new value 1 higher than the last.

        self.y.append( self.gauge.get_pressure(display_units=True))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.
    def OnCOM(self):
        self.comboBoxportname.clear()
        self.ports = serial_ports()
        i=0
        for port in self.ports:
            self.comboBoxportname.addItem("")
            self.comboBoxportname.setItemText(i, port)
            i+=1
        self.informationtext.setPlainText('set the COM port for reading the pressure')
        # print(self.comboBoxportname.currentText())
        self.gauge = Leybold.ITR90(str(self.comboBoxportname.currentText()))
        return

    # def showTime(self):
    #     # getting current time
    #     current_time = QDateTime.currentDateTime()
    #     # converting QTime object to string
    #     label_time = current_time.toString("dd.MM.yyyy, hh:mm:ss")
    #     # showing it to the label
    #     self.time.setPlainText(label_time)

        # self.time.setPlainText(str(datetime.now()))


if __name__ == "__main__":

    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())