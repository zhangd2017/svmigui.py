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
from guistarkvmi import Ui_MainWindow
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

        for channel in range(1,4):
            exec('self.graph%i.setBackground(str(white))'%channel)
            exec('self.x%i = list(range(1)'%channel)  # 100 time points
            exec('self.y%i = list(range(1)'%channel) # 100 data points')
        # self.graph2.setBackground('white')
        # self.graph3.setBackground('white')


        # creating a timer object

        # adding action to timer
        # self.timer.timeout.connect(self.showTime)


        # update the timer every second

        self.connect.clicked.connect(self.OnCOM)
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

        for channel in range(1,4):
            exec('self.data_line%i = self.graph%i.plot(self.x%i, self.y%i, pen=str(red),\
                                         symbol=str(x), symbolPen=str(b), symbolBrush=0.2, \
                                         name=str(pressure))'%(channel,channel,channel,channel))
            exec('self.graph%i.setLabel(str(left), str(pressure), units=str(mbar), fontsize = str(28))'%channel)
            exec('self.graph%i.setLabel(str(bottom), str(Time), units=str(ms), fontsize = str(28))'%channel)

        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()
        self.informationtext.setPlainText('action time is displayed above\nrelative time always start from 0, initial pressure is set to 0')
    def ClearGraphs(self):
        for channel in range(1, 4):
            exec('self.graph%i.clear()'%channel)
            exec('self.x%i = list(range(1))'%channel) # 100 time points
            exec('self.y%i = list(range(1))'%channel)  # 100 data points
        self.timer.stop()
        self.informationtext.setPlainText('action time is displayed above\nclear plot')

    def update_plot_data(self):
        self.x.append(self.x[-1] + self.interval)  # Add a new value 1 higher than the last.

        self.y.append( self.gauge.get_pressure(display_units=True))  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.
    def OnCOM(self):
        self.comboBox.clear()
        self.ports = serial_ports()
        i=0
        for port in self.ports:
            self.comboBox.addItem("")
            self.comboBox.setItemText(i, port)
            i+=1
        self.informationtext.setPlainText('set the COM port for reading the pressure')
        # print(self.comboBoxportname.currentText())
        self.gauge = Leybold.ITR90(str(self.comboBox.currentText()))
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