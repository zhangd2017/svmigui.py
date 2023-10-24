"""
this is the code for controlling mainly the pulsebluster, the scope and the maybe latter the carema

to do:
2023.06.25
1. when i start the program i got some message: (solved)
  if line[0] is not '#':
 this should be addressed at sometime
 this is solved by the following changes:
 if line[0] != '#':
 at line 528
2. when i close the program i got message:
Exception ignored in: <function WorkThread.__del__ at 0x000001DCAA995BD0>
Traceback (most recent call last):
  File "C:/Users\dongd\Desktop\pychem\svmi\starkvmicontrol.py", line 75, in __del__
    self.wait()
RuntimeError: wrapped C/C++ object of type WorkThread has been deleted
which should be addressed at some point

3. when i try to plot the sequence i got error message: (solved)
Traceback (most recent call last):
  File "C:/Users\dongd\Desktop\pychem\svmi\starkvmicontrol.py", line 349, in OnPlotSeq
    output, msg = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals,
  File "C:/Users\dongd\Desktop\pychem\svmi\pulseseq.py", line 58, in pulses
    reptime=1/lcm(freqs)
  File "C:/Users\dongd\Desktop\pychem\svmi\pulseseq.py", line 19, in lcm
    lcm = lcm*i/gcd(lcm, i)
TypeError: 'float' object cannot be interpreted as an integer
===this bug is to be solved urgently===
i modified the line as:
lcm = int(lcm * int(i) / gcd(int(lcm), int(i)))
to eliminate the error

2023.06.27
1. the sequence is not correct for the decelerator
there are overlaps between two sequence which should not be the case.
2. got the following warnings: (solved)
FutureWarning: The error_bad_lines argument has been deprecated and will be removed in a future version. Use on_bad_lines in the future.
  data=pd.read_csv(filename,skiprows=rowsskip,delim_whitespace=True,header=None,error_bad_lines=False)
  i replace the error_bad_lines=False with on_bad_lines='skip'
  this warning is gone!!

2023.06.28
1. make modifications such that the parameters are read with one for loop
2023.06.29
1. modify the readfile.py file such that it can read dec timing file with different dec length
got stupid error:(solved)
IndentationError: unindent does not match any outer indentation level
I solve this problem by convert indent into space which can be done in pycharm
2023.07.03
1. i got a bunch of errors when ploting the sequence (solved)
i solve this problem by adding the following line in the line 75 in the readfile.py file
 data[0] = data[0].astype(int)
 the problem is all the elements of the data read with read_csv function are str
 which is not substractable!
2023.07.04
1. problem one: when i plot the sequence i only get the one for dec + not for dec -(solved)
this problem is sovled by replacing
keyindexes=[list(events.values()).index(time) for time in times] #indexes in order
byk
eyindexes = np.argsort(list(events.values()))
2. problem two: the sequence does not terminate before the detection, not sure this is the problem
when ploting the sequence or this happens to the pulsebluster
3. problem got from yesterday: convert the t2jump file to time and duration, the duration index is out of range of the
array (solved)
look into problem three...
this problem can be solved by remove only last three elements from the t2jump file
and keep the 0x0000 time after the last 0x0010 or 0x0020 time
this is reasonable since the last switch on time should have a corresponding switching off time

"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import readfile as rf
import svmigui
import pulseblaster as pb
#~ import lcwr_scope as scope
import plotsequence as plotseq
import pulseseq as ps
import numpy as np
import time
from matplotlib import pyplot as plt
import pyqtgraph as pg

'''
code inherited from Claudio:
plotsequence.py: used to plot sequence of the pulsebluster
pulseseq.py: generate the pulse sequence
readfile.py: read configuration file
gui.py: the gui user interface 
scope.py: lib for controlling the oscilloscope
'''


#start by reading the config file
version = r'0.1 α'
devmode = 0 	#if 1: developer mode which means no communication to other devices
filename = './input/HyT-input.dat'	#config file
params, values = rf.readpars(filename)
# print(params,values)
#~ CA_DEBUG_TRANSACTIONS=1
#~ CA_ASSERT_MAIN_THREAD_TRANSACTIONS=1

# print(params,values)
'''
2023.06.14
not sure why the following lines are here!!
'''
for i in range (len(params)):
	try:
		exec(params[i]+"=%s"%(values[i]))
	except (NameError, SyntaxError):
		exec(params[i]+"='%s'"%(values[i].strip()))

# print(params[0])
class TrigPlotThread(QThread):
	TrigLog = pyqtSignal(object)
	PlotSeq = pyqtSignal(object, object, object)

	def __init__(self, output, checkboxvals):
		QThread.__init__(self)
		self.output = output
		self.checkboxvals = checkboxvals
		self.plotsequence = plotseq.plotsequence

	def __del__(self):
		self.wait()

	def run(self):
		output = self.output
		checkboxvals = self.checkboxvals
		xvals, yvals, newlabels = self.plotsequence(output, checkboxvals)
		self.TrigLog.emit('Done')
		self.PlotSeq.emit(xvals, yvals, newlabels)
		# ~ self.terminate()
		return


class WorkThread(QThread):
	readboard = pyqtSignal(object)
	TrigLog = pyqtSignal(object)

	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		return

	def PlotSeq(self, output, checkboxvals):
		print('in workt')
		plotseq.plotsequence(output, checkboxvals)
		return

	def tof_scan(self, units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals,
				 t2jumpfile,
				 scanchannel, relchannel, times):

		for timing in times:
			output, msg = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals,
									posnegvals, scanchannel, relchannel, timing, t2jumpfile)
			plotseq.plotsequence(output, checkboxvals)
		return

	def TestF(self):
		self.TrigLog.emit('Tehehehehest')
		return

	def pulses(self, units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals,
			   scanchannel, relchannel, scantime, t2jumpfile):
		output, msg = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals,
								posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
		return output, msg

	def continuousTrig(self, units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals,
					   t2jumpfile):
		scantime = 'None'
		scanchannel = 'None'
		relchannel = 'None'
		output, msg = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals,
								posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
		if devmode == 1:
			self.TrigLog.emit('Not starting pulseblaster: Running in dev mode.')
		else:
			self.TrigLog.emit('Starting Pulse Blaster!')
			status = pb.pulseblaster_program(output, pb_clock)
			time.sleep(0.1)
			pb.pulseblaster_start()
		return


class GuiThread(QtWidgets.QMainWindow, svmigui.Ui_MainWindow):
	plotsequence = pyqtSignal(object, object)

	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self)

		self.textBrowser_2.setStyleSheet("QTextBrowser {background-color: rgb(255,0,0);}")

		# connect functions to signals (GUI)
		self.pushButton.clicked.connect(self.OnLoadBoard)
		self.pushButton_2.clicked.connect(self.OnSaveConfig)
		self.pushButton_3.clicked.connect(self.OnPlotSeq)
		self.t2jump_button.clicked.connect(self.OnT2Jump)
		self.t2jump_button_2.clicked.connect(self.OnConfig)
		self.pushButton_4.clicked.connect(self.OnStartTrigger)
		self.pushButton_5.clicked.connect(self.OnStopTrigger)
		# self.ScanSingleStartButton.clicked.connect(self.OnSingleScan)
		# self.ScanListStartButton.clicked.connect(self.OnListScan)

		# initialize the trigger control tabs as defined in config file
		channels = 18

		# index = self.ch_comboBox_chno1_1.findText(ch1b)
		# self.ch_comboBox_chno1_1.setCurrentIndex(index)
		#
		# index = self.ch_comboBox_chno2_1.findText(ch1e)
		# self.ch_comboBox_chno2_1.setCurrentIndex(index)
		#
		# self.ch_doubleSpinBox_t1_1.setValue(ch1t1)
		# self.ch_doubleSpinBox_t2_1.setValue(ch1t2)
		#
		# index = self.ch_comboBox_unit1_1.findText(ch1u1)
		# self.ch_comboBox_unit1_1.setCurrentIndex(index)
		#
		# index = self.ch_comboBox_unit2_1.findText(ch1u1)
		# self.ch_comboBox_unit2_1.setCurrentIndex(index)
		#
		# index = self.ch_comboBox_pulsetype_1.findText(ch1pulse)
		# self.ch_comboBox_pulsetype_1.setCurrentIndex(index)
		#
		# self.ch_doubleSpinBox_freq_1.setValue(ch1freq)
		#
		# index = self.ch_comboBox_posneg_1.findText(ch1trig)
		# self.ch_comboBox_posneg_1.setCurrentIndex(index)
		#
		# self.ch_checkBox_1.setCheckState(ch1cb)

		for chno in range(1, channels + 1):

			try:
				index = eval("self.ch_comboBox_chno1_%i.findText(ch%ib)" % (chno, chno))
				exec('self.ch_comboBox_chno1_%i.setCurrentIndex(%i)' % (chno, index))

				index = eval("self.ch_comboBox_chno2_%i.findText(ch%ie)" % (chno, chno))
				exec('self.ch_comboBox_chno2_%i.setCurrentIndex(%i)' % (chno, index))

				exec("self.ch_doubleSpinBox_t1_%i.setValue(ch%it1)" % (chno, chno))
				exec("self.ch_doubleSpinBox_t2_%i.setValue(ch%it2)" % (chno, chno))

				# ~ print(ch1u1)
				index = eval("self.ch_comboBox_unit1_%i.findText(ch%iu1)" % (chno, chno))
				# ~ print(index)
				exec("self.ch_comboBox_unit1_%i.setCurrentIndex(%i)" % (chno, index))
				index = eval("self.ch_comboBox_unit2_%i.findText(ch%iu2)" % (chno, chno))
				exec("self.ch_comboBox_unit2_%i.setCurrentIndex(%i)" % (chno, index))

				index = eval("self.ch_comboBox_pulsetype_%i.findText(ch%ipulse)" % (chno, chno))
				exec("self.ch_comboBox_pulsetype_%i.setCurrentIndex(%i)" % (chno, index))

				exec("self.ch_doubleSpinBox_freq_%i.setValue(ch%ifreq)" % (chno, chno))

				index = eval("self.ch_comboBox_posneg_%i.findText(ch%itrig)" % (chno, chno))
				exec("self.ch_comboBox_posneg_%i.setCurrentIndex(%i)" % (chno, index))

				exec("self.ch_checkBox_%i.setCheckState(ch%icb)" % (chno, chno))
				# add the followsing lines to set the tristate option off
				exec("self.ch_checkBox_%i.setTristate(False)" % chno)

			except NameError:
				# ~ print('NameError')
				msg = 0

		self.t2jumppath_lineEdit.setText(T2jumpfile)

		self.configfile = './input/HyT-input.dat'
		self.t2jumppath_lineEdit_2.setText(self.configfile)

		self.units = {'ns': 1e-9, 'us': 1e-6, 'ms': 1e-3, 's': 1}

		# self.scan_plot1 = pg.PlotWidget()
		# self.scan_plot1.setObjectName("scanplot1")
		# self.scan_plotframe1.addWidget(self.scan_plot1)
		#
		# self.scan_plot2 = pg.PlotWidget()
		# self.scan_plot2.setObjectName("scanplot2")
		# self.scan_plotframe2.addWidget(self.scan_plot2)
		#
		# self.scan_plot3 = pg.PlotWidget()
		# self.scan_plot3.setObjectName("scanplot3")
		# self.scan_plotframe3.addWidget(self.scan_plot3)

		self.start_working()

	def FailSafe(self):
		choice = QtGui.QMessageBox.question(self, 'Failsafe',
											'Are you sure?',
											QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		return choice == QtGui.QMessageBox.Yes

	def TrigLog(self, msg):
		self.textBrowser.append(msg)
		return

	def OnStartTrigger(self):
		self.textBrowser.append('Starting trigger.')
		self.textBrowser_2.setStyleSheet("QTextBrowser {background-color: rgb(0,255,0);}")
		units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()
		self.workT.continuousTrig(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals,
								  posnegvals, t2jumpfile)
		return

	def OnListScan(self):
		string = self.ScanListBox.toPlainText()
		unit1 = self.ScanListUnitBox.currentText()
		unit = self.units[unit1]
		try:
			scanlist = [int(s) for s in string.split(',')]
			self.ScanLog.append(
				'Scanning custom list. First: %s %s, Last: %s %s' % (scanlist[0], unit1, scanlist[-1], unit1))

		except ValueError:
			self.ScanLog.append('No list given.')

		return

	def OnStopTrigger(self):
		if devmode == 1:
			self.textBrowser.append('No trigger running: devmode.')
		else:
			self.textBrowser.append('Stopping trigger.')
			pb.pulseblaster_stop()
		self.textBrowser_2.setStyleSheet("QTextBrowser {background-color: rgb(255,0,0);}")
		return

	def start_working(self):
		self.textBrowser.append('Welcome! You are using Stark-VMI control v.%s.\r' \
							   'Have fun!' % version)
		if devmode == 1:
			self.textBrowser.append('Running in developer mode: No communication to devices.')

		self.workT = WorkThread()
		worker = self.workT

		self.plotsequence.connect(worker.PlotSeq)
		worker.readboard.connect(self.readboard)
		worker.TrigLog.connect(self.TrigLog)
		worker.start()

		return

	def OnT2Jump(self):
		t2jumpfile = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './', 'Data files (*.dat *.txt *out)')[0]
		self.textBrowser.append('T2Jump file set to: %s' % t2jumpfile)
		self.t2jumppath_lineEdit.setText(t2jumpfile)
		return

	def OnConfig(self):
		configfile = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './', 'Data files (*.dat *.txt)')[0]
		self.textBrowser.append('Config file set to: %s' % configfile)
		self.t2jumppath_lineEdit_2.setText(configfile)
		return

	def OnSingleScan(self):
		units = {'ns': 1e-9, 'μs': 1e-6, 'ms': 1e-3, 's': 1}
		self.textBrowser.append('Starting single Scan.')
		units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()

		unit1 = self.ScanUnitBox.currentText()
		unit = units[unit1]
		startval = float(self.ScanStartBox.value()) * unit
		stopval = float(self.ScanStopBox.value()) * unit
		step = float(self.ScanStepBox.value()) * unit

		try:
			values = [startval + i * step for i in range(0, int(np.ceil((stopval - startval) / step)) + 1)]
		except ZeroDivisionError:
			self.ScanLog.append('Stepsize should not be zero.')
			return 0

		self.ScanLog.append(
			'Scan starts at %s %s and stops at %s %s.' % (startval / unit, unit1, stopval / unit, unit1))

		scanchannel = self.ScanChannelBox.currentText()
		relchannel = self.ScanRelChannelBox.currentText()
		print(scanchannel, relchannel)

		self.workT.tof_scan(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals,
							t2jumpfile,
							scanchannel, relchannel, values)
		return 1

	def OnPlotSeq(self):
		self.textBrowser.append('Plot pulse sequence.')
		units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()
		# self.textBrowser.append(str(freqs))
		scanchannel = 'None'
		relchannel = 'None'
		scantime = 'None'
		self.textBrowser.append('Calculating sequence...')
		output, msg = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals,
								posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
		if msg == 1:
			self.textBrowser.append('Pulse sequence ok.')
		if msg == 0:
			self.textBrowser.append('Pulse sequence wrong. Probably a delay longer than 1/frequency.')
			return
		self.textBrowser.append('Plotting...')

		self.PlotT = TrigPlotThread(output, checkboxvals)

		self.PlotT.TrigLog.connect(self.TrigLog)
		self.PlotT.PlotSeq.connect(self.PlotSeq)

		self.PlotT.start()
		# print(freqs)
		return

	def OnLoadBoard(self):
		self.textBrowser.append('Loading sequence to board.')
		units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()
		scanchannel = 'None'
		relchannel = 'None'
		scantime = 'None'
		output = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals,
						   scanchannel, relchannel, scantime, t2jumpfile)
		# print(output)
		if devmode == 0:
			ans = pb.pulseblaster_program(output, pb_clock)
			self.textBrowser.append('PB status: %s.' % ans)
		return

	def PlotSeq(self, xvals, yvals, newlabels):
		# self.seqplot.setBackground('w')
		fig, ax = plt.subplots(figsize=(20,12))
		# self.seqplot(fig)
		ticks = [0.25 + i for i in range(len(xvals))]
		ax.tick_params(axis="x", labelsize=20)
		ax.set_yticks(ticks)
		ax.set_yticklabels(newlabels,fontsize = 20)
		plt.ylabel('Channel no.',fontsize = 24)
		plt.xlabel('time [$\mu$s]',fontsize = 24)

		no = 0
		for i in range(len(xvals)):
			plt.plot(np.array(xvals[i]) * 1e6, (np.array(yvals[i]) / 2) - (newlabels[i] - 1) + i)
		plt.show()

	def readboard(self):
		''' read values from channels board'''

		t2jumpfile = self.t2jumppath_lineEdit.text()
		lastindex = 18
		indexes = [['%ib' % i, '%ie' % i] for i in range(1, lastindex+1)]
		# print(indexes)

		units = {'ns': 1e-9, 'us': 1e-6, 'ms': 1e-3, 's': 1}

		# ~ read all channels and times from gui
		units1 = []
		# units1.append(self.ch_comboBox_unit1_1.currentText())

		# ~ time 1 units in board
		for i in range(1, lastindex + 1):
			units1.append(eval('self.ch_comboBox_unit1_' + str(i) + '.currentText()'))

		# ~ channel number relative
		chno1 = []
		# chno1.append(self.ch_comboBox_chno1_1.currentText())
		for i in range(1, lastindex + 1):
			chno1.append(eval('self.ch_comboBox_chno1_' + str(i) + '.currentText()'))

		# ~ time 1
		time1 = []
		# time1.append(self.ch_doubleSpinBox_t1_1.value() * units[units1[0]])
		for i in range(1, lastindex + 1):
			time1.append(eval('self.ch_doubleSpinBox_t1_' + str(i) + '.value()*units[units1[' + str(i - 1) + ']]'))

		# ~ time 2 units
		units2 = []
		# units2.append(self.ch_comboBox_unit2_1.currentText())
		for i in range(1, lastindex + 1):
			units2.append(eval('self.ch_comboBox_unit2_' + str(i) + '.currentText()'))

		# ~ second relative channel
		chno2 = []
		# chno2.append(self.ch_comboBox_chno2_1.currentText())
		for i in range(1, lastindex + 1):
			chno2.append(eval('self.ch_comboBox_chno2_' + str(i) + '.currentText()'))

		# ~ time 2
		time2 = []
		# time2.append(self.ch_doubleSpinBox_t2_1.value() * units[units2[0]])
		for i in range(1, lastindex + 1):
			time2.append(eval('self.ch_doubleSpinBox_t2_' + str(i) + '.value()*units[units2[' + str(i - 1) + ']]'))

		# ~ frequency of the pulse
		freqs = []
		# freqs.append(self.ch_doubleSpinBox_freq_1.value())
		for i in range(1, lastindex + 1):
			freqs.append(eval('self.ch_doubleSpinBox_freq_' + str(i) + '.value()'))

		# ~ which kind of pulse? decelerator sequence? normal pulse?
		pulsenature = []
		# pulsenature.append(self.ch_comboBox_pulsetype_1.currentText())
		for i in range(1, lastindex + 1):
			pulsenature.append(eval('self.ch_comboBox_pulsetype_' + str(i) + '.currentText()'))

		# ~ checkbox : active / inactive
		checkboxvals = []
		# checkboxvals.append(self.ch_checkBox_1.isChecked())
		for i in range(1, lastindex + 1):
			checkboxvals.append(eval('self.ch_checkBox_' + str(i) + '.isChecked()'))

		posnegvals = []
		# posnegvals.append(self.ch_comboBox_posneg_1.currentText())
		for i in range(1, lastindex + 1):
			posnegvals.append(eval('self.ch_comboBox_posneg_' + str(i) + '.currentText()'))

		# print(len(units1))
		return units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile

	def OnSaveConfig(self):
		filename_in = './input/HyT-input.dat'
		dialog = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", "")
		# ~ dialog = QtWidgets.QFileDialog.selectFile(self,'Open file', './', 'Data files (*.dat *.txt)')
		filename_out = dialog[0]
		try:
			self.saveconfig(filename_in, filename_out)
			msg = 'Output file: %s' % filename_out
		except FileNotFoundError:
			msg = 'File not found!'
		return msg

	def saveconfig(self, filename_in, filename_out):
		infile = open(filename_in, "r")
		outfile = open(filename_out, "w")

		# ~ READ OUT ALL GUI VARIABLES ! (TO DO!)---------------------------------------------------

		# ~ triggercontrol guiparams
		trigparams = []
		chs = 18
		for i in range(1, chs+1):
			trigparams.append('ch%ib' % i)
			trigparams.append('ch%ie' % i)
			trigparams.append('ch%ipulse' % i)
			trigparams.append('ch%ifreq' % i)
			trigparams.append('ch%itrig' % i)
			trigparams.append('ch%icb' % i)
			for j in range(1, 3):
				trigparams.append('ch%it%i' % (i, j))
				trigparams.append('ch%iu%i' % (i, j))

		chu1, chb, cht1, chu2, che, cht2, chfreq, chpulse, chcb, chtrig, t2jumpfile = self.readboard()
		units = {'us': 1e6, 'ms': 1e3, 'ns': 1e9, 's': 1}
		for i in range(len(chu1)):
			cht1[i] = cht1[i] * units[chu1[i]]
			cht2[i] = cht2[i] * units[chu2[i]]

		# rest of the gui changeable params in dictionary saveparams
		saveparams = {}
		saveparams['T2jumpfile'] = self.t2jumppath_lineEdit.text()

		while True:
			line = infile.readline()
			paramname = ''
			value = ''
			num = 0

			if line[0] != '#':
				for char in line:
					if char == '=':
						break
					paramname += char
					num += 1

				paramname = paramname.strip()
				value = eval(paramname)
				if paramname in trigparams:
					tstr = ''.join(i for i in paramname if not i.isdigit())
					if paramname[-1].isdigit():
						tstr += paramname[-1]

					tnum = [int(i) for i in paramname if i.isdigit()]
					value = eval(tstr)[tnum[0] - 1]
					try:
						float(value)
						value = "%.3f" % value
					except (TypeError, ValueError):
						value = value

				if paramname in saveparams:
					value = saveparams[paramname]

				outfile.write('%s = %s\r\n' % (paramname, value))

			else:
				outfile.write(line)

			if 'this is the end' in line:
				break
		return

	def OnBrowse(self):
		dialog = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', './', 'Data files (*.dat *.txt)')
		return dialog


def main():
	app = QtWidgets.QApplication(sys.argv)
	form = GuiThread()

	form.show()
	app.exec_()


if __name__ == '__main__':
	main()