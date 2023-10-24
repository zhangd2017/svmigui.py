import win32com.client
import readfile as rf
import time


'''
    Some important settings
    
    # verticalcoupling 0: A1M, 1: D1M, 2: D50, 3: GND, 4: DC, 5: AC
    # samplemode 0: RealTime, 1: RIS, 2: Sequence, 3: Roll, 4: WaveStream
    # bandwidth 0: Fulll, 1: 20 MHZ, 2: 25 MHZ, 3: 200 MHZ, 4: 250 MHZ, 5: 1 GHZ
    # vertical range VDIV: v/div in V
    # vertical offset OFST: offset in V
    # Probe Attenuation ATTN: Selects the vertical attenuation factor of the probe. Values up to 10000.
    # Interpolation InterpolateType: 0: Linear, 1: Sinx/x
    # Noise Filter EnhanceResType: 0: None, 1: +0.5 bits, 2: +1.0 bits ,... 6: + 3bits
    # Trigger Source SR: 0: Channel 1, 1: Channel 2, 2: Channel 3, 3: Channel 4, 4: Ext, 
        5: Ext10, 6: Line, 7: Pattern
    # Qualifier Source QL
    # Trigger Qualifier (Do we need this?)

        When the trigger qualifier is on, the test set samples the input signal when 
        a trigger is received. It then determines if the input signal was valid by looking 
        at its power level. If the power level during sampling did not meet the requirements 
        of a valid signal, the state returns to wait for trigger without processing the samples. 
        Trigger qualifier is available for GSM/GPRS TX Power and Phase Frequency Error measurements only.
'''

# measuring page 86 ff

def scope_initialize():
    scope=win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")  #creates instance of the ActiveDSO control
    connection=scope.MakeConnection("IP:%s"%scope_ip) #Connects to the oscilloscope.
    if(connection==False):
        #~ print('Unable to connect to the oscilloscope!')
        return (connection,'Unable to connect to the oscilloscope!')

    try:
        response = scope.WriteString("*IDN?",1)
        scope_id = scope.ReadString(80)
        response=scope.WriteString("VBS 'app.Acquisition.Horizontal.SampleMode=%s'"%(samplemode),1)
        response=scope.WriteString("VBS 'app.Acquisition.Horizontal.NumSegments=%d'"%(numberofsegments ),1)
    
        chno=1
        acquisition="VBS 'app.acquisition.C%i."%chno
        response=scope.WriteString(acquisition+"AverageSweeps=%i'"%(sweeps),1)
        response=scope.WriteString(acquisition+"InterpolateType=%i'"%(interpolatetype),1)
        response=scope.WriteString(acquisition+"EnhanceResType=%i'"%(enhancerestype),1)
        response=scope.WriteString(acquisition+"Invert=%s'"%(eval('ch%i_invert'%(chno))),1)
    
    
        chstr="C%i:"%chno
        response=scope.WriteString(chstr+"ATTN %s"%(probeattenuation),1)  
        response=scope.WriteString(chstr+"VDIV %f"%(eval('ch%i_scale'%(chno))),1)
        response=scope.WriteString(chstr+"OFST %f"%(eval('ch%i_verticaloffset'%(chno))),1)
        response=scope.WriteString(chstr+"CPL %s"%(eval('ch%i_verticalcoupling'%(chno))),1)
    
    
        # Trigger
        response=scope.WriteString("TRSE %s,SR,C%i"%(trig_type,trig_source),1)
        
        response=scope.WriteString("TRDL %s"%(str(timeoffset)),1)   # time delay (offset)
        response=scope.WriteString("TDIV %s"%(str(timebase)),1)     # time division (time base)
        response=scope.WriteString("MSIZ %s"%(5000000),1)     # Maximum sample size
    
    
        response=scope.WriteString("C%i:TRLV %f"%(trig_source,trig_level),1)
        response=scope.WriteString("C%i:TRSL %s"%(trig_source,trig_slope),1)
    
        response=scope.WriteString("BWL OFF",1)
        response=scope.WriteString(chstr+"TRA %s"%(tracemode),1)
        
        #acquire data
    #    scope.WriteString("*CLS;ARM;FRTR",1) #clear registers
        scope.WriteString("WFSU SP,0,NP,0,FP,0,SN,0",1) # waveform setup
        scope.WriteString("CFMT DEF9,WORD,BIN",1) # BYTE <> WORD
        scope.WriteString("C1:WF? DESC",1)
        desc = scope.ReadString(1024)
        print(desc)
    
    #    scope.WriteString("VBS app.ClearSweeps",1)
        response = scope.WriteString("C%i:WF? DAT1"%(1),1)
#        time.sleep(1e-2)
        data = scope.ReadString(100000)
    #
        print(data)
        data_s = data.strip('DAT1,#9')[9:]
#        print(data_s)
        
        print(data_s.encode('utf-8'))
        scope.Disconnect()

    except:
        scope.Disconnect() #Disconnects from the oscilloscope
    return (True,'%s successfully initialized!'%scope_id)


if __name__ == '__main__':
    
    filename='./input/HyT-input.dat' # i know you wanna hyt that
    names,values=rf.readpars(filename)

    for i in range (len(names)):
        try:
            exec(names[i]+"=%s"%(values[i]))
        except (NameError, SyntaxError):
            try:
                exec(names[i]+"='%s'"%(values[i]))
            except:
                print('problem after %s = %s'%(names[i-1],values[i-1]))
    resp=scope_initialize()
    print(resp)
