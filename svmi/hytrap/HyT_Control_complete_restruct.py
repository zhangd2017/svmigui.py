#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import readfile as rf
import gui
import pulseblaster as pb
#~ import lcwr_scope as scope
import plotsequence as plotseq
import pulseseq as ps
import numpy as np
import time
from matplotlib import pyplot as plt

#start by reading the config file
version = r'0.1 α' 
devmode = 1 #if 1: developer mode which means no communication to other devices
filename = './input/HyT-input.dat'#config file
params, values=rf.readpars(filename)
#~ CA_DEBUG_TRANSACTIONS=1
#~ CA_ASSERT_MAIN_THREAD_TRANSACTIONS=1
'''
    17.05.2018: Started changing the structure towards MultiThread
    Need to run the calculations on work thread:
    
    
    in work thread define functions from gui thread as signals
    
        readboard = pyqtSignal()
        units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard.emit()

    when the workthread is started (in guithread!):
        self.workT = WorkThread()
        worker=self.workT
        worker.readboard.connect(self.readboard)
        
        
    24.05.2018: Scan function should work now.
        Write plotseq a bit smarter such that it chooses the timestep for evaluating the status of a channel automatically

'''

for i in range (len(params)):
	try:
		exec(params[i]+"=%s"%(values[i]))
	except (NameError, SyntaxError):
		exec(params[i]+"='%s'"%(values[i].strip()))



class TrigPlotThread(QThread):
    TrigLog = pyqtSignal(object)
    PlotSeq = pyqtSignal(object,object,object)

    def __init__(self,output,checkboxvals):
        QThread.__init__(self)
        self.output = output
        self.checkboxvals = checkboxvals
        self.plotsequence = plotseq.plotsequence

    def __del__(self):
        self.wait()
        
    def run(self):
        output = self.output
        checkboxvals = self.checkboxvals
        xvals,yvals,newlabels=self.plotsequence(output, checkboxvals)
        self.TrigLog.emit('Done')   
        self.PlotSeq.emit(xvals,yvals,newlabels)   
        self.terminate()          
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
        
    def PlotSeq(self,output,checkboxvals):
        print('in workt')
        plotseq.plotsequence(output,checkboxvals)
        return
                
    def tof_scan(self,units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile,
                    scanchannel,relchannel,times):
                        

        for timing in times:
            output = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals,scanchannel,relchannel,timing,t2jumpfile)
            plotseq.plotsequence(output,checkboxvals)
            print(' put in')
            input()
            
            print(output)
        return
        
    def TestF(self):
        self.TrigLog.emit('Tehehehehest')
        return
        
    def pulses(self,units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile):
        output=ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
        return output
        

    def continuousTrig(self,units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile):
        scantime = 'None'
        scanchannel = 'None'
        relchannel = 'None'
        output=ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
        if devmode==1:
            self.TrigLog.emit('Not starting pulseblaster: Running in dev mode.')
        else:
            self.TrigLog.emit('Starting Pulse Blaster!')
            status = pb.pulseblaster_program(output,pb_clock)
            time.sleep(0.1)
            pb.pulseblaster_start()
        return
            
            
            
        

		
		

class GuiThread(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    plotsequence = pyqtSignal(object,object)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.RunningStatusBox.setStyleSheet("QTextBrowser {background-color: rgb(255,0,0);}")

        # connect functions to signals (GUI)
        self.LoadBoardButton.clicked.connect(self.OnLoadBoard)
        self.SaveConfigButton.clicked.connect(self.OnSaveConfig)
        self.PlotSequenceButton.clicked.connect(self.OnPlotSeq)
        self.T2JumpButton.clicked.connect(self.OnT2Jump)
        self.ConfigButton.clicked.connect(self.OnConfig)
        self.StartTriggerButton.clicked.connect(self.OnStartTrigger)
        self.StopTriggerButton.clicked.connect(self.OnStopTrigger)
        self.ScanSingleStartButton.clicked.connect(self.OnSingleScan)
        self.ScanListStartButton.clicked.connect(self.OnListScan)


        # initialize the trigger control tabs as defined in config file 
        channels=18
        
        index=self.ch_combo_chno1.findText(ch1b)
        self.ch_combo_chno1.setCurrentIndex(index)
        
        index=self.ch_combo_chno2.findText(ch1e)
        self.ch_combo_chno2.setCurrentIndex(index)
        
        self.ch_time1_sbox.setValue(ch1t1)
        self.ch_time2_sbox.setValue(ch1t2)
        
        index=self.ch_time1_unitbox.findText(ch1u1)
        self.ch_time1_unitbox.setCurrentIndex(index)
        
        index=self.ch_time2_unitbox.findText(ch1u1)
        self.ch_time2_unitbox.setCurrentIndex(index)

        index=self.ch_pulsebox.findText(ch1pulse)
        self.ch_pulsebox.setCurrentIndex(index)
        
        self.ch_freqbox.setValue(ch1freq)
        
        index=self.ch_posneg.findText(ch1trig)
        self.ch_posneg.setCurrentIndex(index)
        
        self.ch_checkBox.setCheckState(ch1cb)

        for chno in range(2,channels+1):

            try:
                index=eval("self.ch_combo_chno1_%i.findText(ch%ib)"%(chno,chno))
                exec('self.ch_combo_chno1_%i.setCurrentIndex(%i)'%(chno,index))
                
                index=eval("self.ch_combo_chno2_%i.findText(ch%ie)"%(chno,chno))
                exec('self.ch_combo_chno2_%i.setCurrentIndex(%i)'%(chno,index))
                
                exec("self.ch_time1_sbox_%i.setValue(ch%it1)"%(chno,chno))
                exec("self.ch_time2_sbox_%i.setValue(ch%it2)"%(chno,chno))
                
                #~ print(ch1u1)
                index=eval("self.ch_time1_unitbox_%i.findText(ch%iu1)"%(chno,chno))
                #~ print(index)
                exec("self.ch_time1_unitbox_%i.setCurrentIndex(%i)"%(chno,index))
                index=eval("self.ch_time2_unitbox_%i.findText(ch%iu2)"%(chno,chno))
                exec("self.ch_time2_unitbox_%i.setCurrentIndex(%i)"%(chno,index))
                
                index=eval("self.ch_pulsebox_%i.findText(ch%ipulse)"%(chno,chno))
                exec("self.ch_pulsebox_%i.setCurrentIndex(%i)"%(chno,index))
                
                exec("self.ch_freqbox_%i.setValue(ch%ifreq)"%(chno,chno))

                index=eval("self.ch_posneg_%i.findText(ch%itrig)"%(chno,chno))
                exec("self.ch_posneg_%i.setCurrentIndex(%i)"%(chno,index))
                
                exec("self.ch_checkBox_%i.setCheckState(ch%icb)"%(chno,chno))

            except NameError:
                #~ print('NameError')
                msg = 0
                
           
        self.T2JumpLine.setText(T2jumpfile)
        
        self.configfile = './input/HyT-input.dat'
        self.ConfigLine.setText(self.configfile)
        
        self.units={'ns':1e-9, 'μs':1e-6, 'ms':1e-3, 's':1}

        
        self.start_working()
        
    def FailSafe(self):
        choice = QtGui.QMessageBox.question(self, 'Failsafe',
                                    'Are you sure?',
                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        return choice==QtGui.QMessageBox.Yes
     
    def TrigLog(self,msg):
        self.TriggerLog.append(msg)
        return
        
    def OnStartTrigger(self):
        self.TriggerLog.append('Starting trigger.')
        self.RunningStatusBox.setStyleSheet("QTextBrowser {background-color: rgb(0,255,0);}")
        units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()
        self.workT.continuousTrig(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile)
        return
        
    def OnListScan(self):
        string = self.ScanListBox.toPlainText()
        unit1=self.ScanListUnitBox.currentText()
        unit=self.units[unit1]
        try:
            scanlist = [int(s) for s in string.split(',')]
            self.ScanLog.append('Scanning custom list. First: %s %s, Last: %s %s'%(scanlist[0],unit1,scanlist[-1],unit1))

        except ValueError:
            self.ScanLog.append('No list given.')
            
        return
        
    def OnStopTrigger(self):
        if devmode==1:
            self.TriggerLog.append('No trigger running: devmode.')
        else:
            self.TriggerLog.append('Stopping trigger.')
            pb.pulseblaster_stop()
        self.RunningStatusBox.setStyleSheet("QTextBrowser {background-color: rgb(255,0,0);}")
        return
        
    def start_working(self):
        self.TriggerLog.append('Welcome! You are using HyT-Control v.%s.\r'\
                                'Have fun!'%version)
        if devmode == 1:
            self.TriggerLog.append('Running in developer mode: No communication to devices.')
            
        self.workT = WorkThread()
        worker=self.workT
        
        self.plotsequence.connect(worker.PlotSeq)
        worker.readboard.connect(self.readboard)
        worker.TrigLog.connect(self.TrigLog)
        worker.start()
        
        return
        
    def OnT2Jump(self):
        t2jumpfile = QtWidgets.QFileDialog.getOpenFileName(self,'Open file', './', 'Data files (*.dat *.txt *out)')[0]
        self.TriggerLog.append('T2Jump file set to: %s'%t2jumpfile)
        self.T2JumpLine.setText(t2jumpfile)
        return
        
    def OnConfig(self):
        configfile = QtWidgets.QFileDialog.getOpenFileName(self,'Open file', './', 'Data files (*.dat *.txt)')[0]
        self.TriggerLog.append('Config file set to: %s'%configfile)
        self.ConfigLine.setText(configfile)
        return
        
    def OnSingleScan(self):
        units={'ns':1e-9, 'μs':1e-6, 'ms':1e-3, 's':1}
        self.TriggerLog.append('Starting single Scan.')
        units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()

        unit1 = self.ScanUnitBox.currentText()
        unit = units[unit1]
        startval = float(self.ScanStartBox.value())*unit
        stopval = float(self.ScanStopBox.value())*unit
        step = float(self.ScanStepBox.value())*unit


        try:
            values = [startval+ i * step for i in range(0,int(np.ceil((stopval-startval)/step))+1)]
        except ZeroDivisionError:
            self.ScanLog.append('Stepsize should not be zero.')
            return 0
            
        self.ScanLog.append('Scan starts at %s %s and stops at %s %s.'%(startval/unit,unit1,stopval/unit,unit1))

                
        scanchannel = self.ScanChannelBox.currentText()
        relchannel = self.ScanRelChannelBox.currentText()
        print(scanchannel,relchannel)
        
        self.workT.tof_scan(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile,
                    scanchannel,relchannel,values)
        return 1
        

    def OnPlotSeq(self):
        self.TriggerLog.append('Plot pulse sequence.')
        units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()
        scanchannel = 'None'
        relchannel = 'None'
        scantime = 'None'
        self.TriggerLog.append('Calculating sequence...')
        #~ output=ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
        output=ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
        self.TriggerLog.append('Plotting...')
        
        self.PlotT = TrigPlotThread(output,checkboxvals)
        
        self.PlotT.TrigLog.connect(self.TrigLog)
        self.PlotT.PlotSeq.connect(self.PlotSeq)
        
        self.PlotT.start()
        return
        
    def OnLoadBoard(self):
        self.TriggerLog.append('Loading sequence to board.')
        units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile = self.readboard()
        scanchannel = 'None'
        relchannel = 'None'
        scantime = 'None'
        output = ps.pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile)
        print(output)
        if devmode == 0:
            ans = pulseblaster_program(output,pb_clock)
            self.TriggerLog.append('PB status: %s.'%ans)
        return
        
    def PlotSeq(self,xvals,yvals,newlabels):
        fig, ax = plt.subplots()
        ticks = [0.25+i for i in range(len(xvals))]
        ax.set_yticks(ticks)
        ax.set_yticklabels(newlabels)
        plt.ylabel('Channel no.')
        plt.xlabel('time [$\mu$s]')
        
        no=0
        for i in range(len(xvals)):
            plt.plot(np.array(xvals[i])*1e6,(np.array(yvals[i])/2)-(newlabels[i]-1)+i)
        plt.show()
        
        
    def readboard(self):
        ''' read values from channels board'''
        
        t2jumpfile = self.T2JumpLine.text()
        lastindex=17
        indexes=[['%ib'%i,'%ie'%i] for i in range(1,lastindex)]
        #~ print(indexes)
        
        units={'ns':1e-9, 'μs':1e-6, 'ms':1e-3, 's':1}
        
        #~ read all channels and times from gui
        units1=[]
        units1.append(self.ch_time1_unitbox.currentText())

        #~ time 1 units in board
        for i in range(2,lastindex+1):
            units1.append(eval('self.ch_time1_unitbox_'+str(i)+'.currentText()'))
        
        #~ channel number relative
        chno1=[]
        chno1.append(self.ch_combo_chno1.currentText())
        for i in range(2,lastindex+1):
            chno1.append(eval('self.ch_combo_chno1_'+str(i)+'.currentText()'))

        #~ time 1
        time1=[]
        time1.append(self.ch_time1_sbox.value()*units[units1[0]])
        for i in range(2,lastindex+1):
            time1.append(eval('self.ch_time1_sbox_'+str(i)+'.value()*units[units1['+str(i-1)+']]'))

        #~ time 2 units
        units2=[]
        units2.append(self.ch_time2_unitbox.currentText())
        for i in range(2,lastindex+1):
            units2.append(eval('self.ch_time2_unitbox_'+str(i)+'.currentText()'))
        
        #~ second relative channel
        chno2=[]
        chno2.append(self.ch_combo_chno2.currentText())
        for i in range(2,lastindex+1):
            chno2.append(eval('self.ch_combo_chno2_'+str(i)+'.currentText()'))
        
        #~ time 2
        time2=[]
        time2.append(self.ch_time2_sbox.value()*units[units2[0]])
        for i in range(2,lastindex+1):
            time2.append(eval('self.ch_time2_sbox_'+str(i)+'.value()*units[units2['+str(i-1)+']]'))
        
        #~ frequency of the pulse
        freqs=[]
        freqs.append(self.ch_freqbox.value())
        for i in range(2,lastindex+1):
            freqs.append(eval('self.ch_freqbox_'+str(i)+'.value()'))

        #~ which kind of pulse? decelerator sequence? normal pulse?
        pulsenature=[]
        pulsenature.append(self.ch_pulsebox.currentText())
        for i in range(2,lastindex+1):
            pulsenature.append(eval('self.ch_pulsebox_'+str(i)+'.currentText()'))
          
        #~ checkbox : active / inactive
        checkboxvals=[]
        checkboxvals.append(self.ch_checkBox.isChecked())
        for i in range(2,lastindex+1):
            checkboxvals.append(eval('self.ch_checkBox_'+str(i)+'.isChecked()'))
            
        posnegvals=[]
        posnegvals.append(self.ch_posneg.currentText())
        for i in range(2,lastindex+1):
            posnegvals.append(eval('self.ch_posneg_'+str(i)+'.currentText()'))

        return units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, t2jumpfile
      
    def OnSaveConfig(self):
        filename_in = './input/HyT-input.dat'
        dialog = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", "")
        #~ dialog = QtWidgets.QFileDialog.selectFile(self,'Open file', './', 'Data files (*.dat *.txt)')
        filename_out = dialog[0]
        try:
            self.saveconfig(filename_in,filename_out)
            msg = 'Output file: %s'%filename_out
        except FileNotFoundError:
            msg = 'File not found!'
        return msg
        
    def saveconfig(self, filename_in, filename_out):
        infile = open(filename_in, "r")
        outfile = open(filename_out, "w")
        
        #~ READ OUT ALL GUI VARIABLES ! (TO DO!)---------------------------------------------------
        
        #~ triggercontrol guiparams
        trigparams=[]
        chs=19
        for i in range(1,chs):
            trigparams.append('ch%ib'%i)
            trigparams.append('ch%ie'%i)
            trigparams.append('ch%ipulse'%i)
            trigparams.append('ch%ifreq'%i)
            trigparams.append('ch%itrig'%i)
            trigparams.append('ch%icb'%i)
            for j in range(1,3):
                trigparams.append('ch%it%i'%(i,j))
                trigparams.append('ch%iu%i'%(i,j))
                 
        chu1,chb,cht1,chu2,che,cht2,chfreq,chpulse,chcb,chtrig,t2jumpfile = self.readboard()
        units={'μs':1e6, 'ms':1e3, 'ns':1e9, 's': 1}
        for i in range(len(chu1)):
            cht1[i] = cht1[i]*units[chu1[i]]
            cht2[i] = cht2[i]*units[chu2[i]]
        
        # rest of the gui changeable params in dictionary saveparams
        savaparams={}
        saveparams['T2jumpfile']= self.T2JumpLine.text()
        
        while True:
            line=infile.readline()
            paramname=''
            value=''
            num=0
            
            if line[0] is not '#':
                for char in line:
                    if char == '=':
                        break
                    paramname+=char
                    num+=1
                
                paramname=paramname.strip()
                value = eval(paramname)
                if paramname in trigparams:
                    tstr=''.join(i for i in paramname if not i.isdigit())
                    if paramname[-1].isdigit():
                        tstr+=paramname[-1]
                        
                    tnum=[int(i) for i in paramname if i.isdigit()]
                    value = eval(tstr)[tnum[0]-1]
                    try:
                        float(value)
                        value = "%.3f"%value
                    except (TypeError,ValueError):
                        value = value
                        
                if paramname in saveparams:
                    value = saveparam[paramname]
                    
                    
                outfile.write('%s = %s\r\n'%(paramname,value))
                
            else:
                outfile.write(line)
                
            if 'this is the end' in line:
                break
        return 
        
        
    def OnBrowse(self):
        dialog = QtWidgets.QFileDialog.getOpenFileName(self,'Open file', './', 'Data files (*.dat *.txt)')
        return dialog
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    form = GuiThread()
    
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
