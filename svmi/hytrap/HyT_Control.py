#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import time
import numpy as np
#~ import mainwindow as gui
import gui
from fractions import gcd


class LaserThread(QThread):
    replot = pyqtSignal(np.ndarray)
    global upreq
    
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        return

class GuiThread(QtWidgets.QMainWindow, gui.Ui_MainWindow):

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.boomButton.clicked.connect(self.pulses)
        self.ch_combo_chno1.setCurrentIndex(0)
        self.ch_combo_chno1_2.setCurrentIndex(5)
        self.ch_combo_chno1_3.setCurrentIndex(7)
        self.ch_combo_chno1_4.setCurrentIndex(1)
        
        self.ch_combo_chno2.setCurrentIndex(1)
        self.ch_combo_chno2_2.setCurrentIndex(3)
        self.ch_combo_chno2_3.setCurrentIndex(5)
        self.ch_combo_chno2_4.setCurrentIndex(7)
        
    def indexlist(self, lists, element):
        '''
        creates a list of indices with a certain value from given list
        '''
        indices= [i for i, x in enumerate(lists) if x == element]
        return indices
        
    
    def channelflag(self, numbers):
        '''
            takes a list of channelnumbers as input. Creates a string of 24 zeroes 
            (1 for each available channel on pulseblaster) and then sets the string of each channel
            number from the input to 1. Required for Spinapi instruction functions.
            Example:
                use for channels [1,3]
                output will be
                '101000000000000000000000'
        '''
        maxno=24
        flags=list('0'*maxno)
        output=''
        for num in numbers:
            flags[num-1]='1'
        
        for flag in flags:
            output+=flag
            
        if numbers==[0]:
            output='0'*maxno
        return output
        
    def decpulses():
        return
        
    def readdecfile(directory,filename):
        '''
                Reads T2jump.out files from deceleration simulation
                required for creating decelerator burst sequences!
        '''
        
        rowsskip= (0,1,2,3,4,129,130,131) #skip unnecessary rows, s.t. files can be read in easily
        data=pd.read_csv(directory+filename,skiprows=rowsskip,delim_whitespace=True,header=None,error_bad_lines=False)
        data=np.array(data)
        data=np.insert(data,0,[1010,'0x0010','!',0],axis=0) 
        ''' 
            since this line (first of decelerator sequence) is alwasy the same and it does not have
            the same shape as the rest, it is skipped when reading the file and added later.
        '''
        return data.T
        
    def lcm(self,a):
        lcm = a[0]
        for i in a[1:]:
          lcm = lcm*i/gcd(lcm, i)
        return lcm
        
    def pulses(self):
        lastindex=17
        indexes=[['%ib'%i,'%ie'%i] for i in range(1,lastindex)]
        #~ print(indexes)
        
        units={'ns':1e-9, 'μs':1e-6, 'ms':1e-3, 's':1}
        
        #~ read all channels and times from gui
        units1=[]
        units1.append(self.ch_time1_unitbox.currentText())
        units1.append(self.ch_time1_unitbox_2.currentText())
        units1.append(self.ch_time1_unitbox_3.currentText())
        units1.append(self.ch_time1_unitbox_4.currentText())
        
        chno1=[]
        chno1.append(self.ch_combo_chno1.currentText())
        chno1.append(self.ch_combo_chno1_2.currentText())
        chno1.append(self.ch_combo_chno1_3.currentText())
        chno1.append(self.ch_combo_chno1_4.currentText())
        
        time1=[]
        time1.append(self.ch_time1_sbox.value()*units[units1[0]])
        time1.append(self.ch_time1_sbox_2.value()*units[units1[1]])
        time1.append(self.ch_time1_sbox_3.value()*units[units1[2]])
        time1.append(self.ch_time1_sbox_4.value()*units[units1[3]])
        
        units2=[]
        units2.append(self.ch_time2_unitbox.currentText())
        units2.append(self.ch_time2_unitbox_2.currentText())
        units2.append(self.ch_time2_unitbox_3.currentText())
        units2.append(self.ch_time2_unitbox_4.currentText())
        
        chno2=[]
        chno2.append(self.ch_combo_chno2.currentText())
        chno2.append(self.ch_combo_chno2_2.currentText())
        chno2.append(self.ch_combo_chno2_3.currentText())
        chno2.append(self.ch_combo_chno2_4.currentText())
        
        time2=[]
        time2.append(self.ch_time2_sbox.value()*units[units2[0]])
        time2.append(self.ch_time2_sbox_2.value()*units[units2[1]])
        time2.append(self.ch_time2_sbox_3.value()*units[units2[2]])
        time2.append(self.ch_time2_sbox_4.value()*units[units2[3]])
        
        freqs=[]
        freqs.append(self.ch_freqbox.value())
        freqs.append(self.ch_freqbox_2.value())
        freqs.append(self.ch_freqbox_3.value())
        freqs.append(self.ch_freqbox_4.value())
        
        pulsenature=[]
        pulsenature.append(self.ch_pulsebox.currentText())
        pulsenature.append(self.ch_pulsebox_2.currentText())
        pulsenature.append(self.ch_pulsebox_3.currentText())
        pulsenature.append(self.ch_pulsebox_4.currentText())
                
        checkboxvals=[]
        checkboxvals.append(self.ch_checkBox.isChecked())
        checkboxvals.append(self.ch_checkBox_2.isChecked())
        checkboxvals.append(self.ch_checkBox_3.isChecked())
        checkboxvals.append(self.ch_checkBox_4.isChecked())
        
        print(checkboxvals)
        freqmin=min(freqs)
        freqmax=max(freqs)

        #~ create one sequence from the channels and times
        #look for T0
        channels=0
        events=0
        tottime=0
        chno=4
        ch_done=[]
        ch_list=[i for i in range(lastindex+1)]
        print(ch_list)
    
        durations={}
        events={}
        
        #~ sequence starts relative to channel T0 : find channel related to T0
        ''' 
        To change: XXX find indexlist and get the events for all indexes with same channel
        '''
        starttag='T0'
        indexes=self.indexlist(chno1,starttag)
        reptime=1/self.lcm(freqs)
        pulsetime=1/freqmin
        
        print(pulsetime)
        
        ''' 
        Do first pulse, starting at T0
        '''
        n=0
        while tottime<pulsetime:
            index=indexes[0]
            if checkboxvals[index]==True:
                if pulsenature[index]=='normal pulse':
                    n+=1
                    events['%ib%i'%(index+1,n)]=time1[index]+(n-1)*1/freqs[index]
                    events['%ie%i'%(index+1,n)]=events['%ib%i'%(index+1,n)]+time2[index]
                    durations['%id%i'%(index+1,n)]=time2[index]
                    tottime+=1/freqs[index]
                    print(tottime)
                channels+=1
                ch_done.append(index)
            else:
                print('T0 not checked')
                return 'T0 not checked'
        #~ print(events)

        nextindex=index
        '''
        Do all connected pulses
        '''
        
        while channels<chno:
            try:
                nextindex=self.indexlist(chno1,'%ib'%(nextindex+1))[0]
            except IndexError:
                print('Index Error channel flags: %i'%nextindex)
                break
                
            ch_done.append(nextindex)
            tottime=0
            m=0
            while tottime<pulsetime:
                
                try:
                    #~ if pulsenature[nextindex]=='normal pulse':
                        #~ print('normal pulse')
                    m+=1
                    events['%ib%i'%(nextindex+1,m)]=events['%s%i'%(chno1[nextindex],m)]+time1[nextindex]+(m-1)*1/freqs[index]
                    events['%ie%i'%(nextindex+1,m)]=events['%ib%i'%(nextindex+1,m)]+time2[nextindex]
                    durations['%id%i'%(nextindex+1,m)]=events['%ie%i'%(nextindex+1,m)]-events['%ib%i'%(nextindex+1,m)]
                    tottime+=1/freqs[nextindex]
                    ch_done.append(nextindex)
                    #~ if 'dec' in pulsenature[nextindex]:
                        #~ print('dec, index: %i'%nextindex)
                    #~ if freqs[nextindex]
                except KeyError:
                    print('keyerror: m=%i'%m)
                    m=lastindex+2
            channels+=1
        
        '''
        Do all the pulses which were not done so far
        '''
        ch_todo=list(set(ch_list)-set(ch_done))
        print(ch_todo)
        
        for nextindex in ch_todo:
            tottime=0
            m=0
            while tottime<pulsetime:
                
                try:
                    #~ if pulsenature[nextindex]=='normal pulse':
                        #~ print('normal pulse')
                    m+=1
                    events['%ib%i'%(nextindex+1,m)]=events['%s%i'%(chno1[nextindex],m)]+time1[nextindex]+(m-1)*1/freqs[index]
                    events['%ie%i'%(nextindex+1,m)]=events['%ib%i'%(nextindex+1,m)]+time2[nextindex]
                    durations['%id%i'%(nextindex+1,m)]=events['%ie%i'%(nextindex+1,m)]-events['%ib%i'%(nextindex+1,m)]
                    tottime+=1/freqs[nextindex]
                    ch_done.append(nextindex)
                    #~ if 'dec' in pulsenature[nextindex]:
                        #~ print('dec, index: %i'%nextindex)
                    #~ if freqs[nextindex]
                except KeyError:
                    print('keyerror: %i'%nextindex)
                    tottime=2*pulsetime
                    
                except IndexError:
                    print('indexerror: %i'%nextindex)
                    tottime=2*pulsetime

            channels+=1
            

        
        print(events)
        #~ sort times in increasing order and then sort the keys by the same order
        times=sorted(events.values())
        keyindexes=[list(events.values()).index(time) for time in times] #indexes in order
        keys=[list(events.keys())[index] for index in keyindexes] # keys of these ordered indexes
        
        #~ print(events)
        
        #~ create the pulses for all channels
        '''extract int from string:
            [int(s) for s in str.split() if s.isdigit()]'''
            
        resultion=1e-10
        activechannels=[]
        for i in range(len(keys)-1):
            duration = times[i+1]-times[i]
            
            channelb=int(keys[i][:-2])
            flagb=keys[i][-2]
            mb=int(keys[i][-1])
            
            channele=int(keys[i+1][:-2])
            flage=keys[i+1][-2]
            me=int(keys[i+1][-1])
            
            for channel in activechannels:
                if durations['%id%i'%(channel,mb)]<=resultion:
                    activechannels.remove(channel) 
                            
            if flagb=='b':
                activechannels.append(channelb)
                
            for channel in activechannels:
                durations['%id%i'%(channel,mb)]-=duration
                if durations['%id%i'%(channel,mb)]<resultion:
                    durations['%id%i'%(channel,mb)]=0

            #~ print(durations)
                
            chflag=self.channelflag(activechannels)
            
            #~ print(chflag)
            #~ print(duration)
            
        
        #~ print(keys[0][:-2])
        return chno1, time1, chno2, time2
        
    def OnBOOM(self):
        self.pulses()
        
   
		
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    form = GuiThread()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
