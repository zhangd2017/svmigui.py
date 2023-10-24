import win32com.client
import readfile as rf


def scope_initialize():
	scope=win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")  #creates instance of the ActiveDSO control
	connection=scope.MakeConnection("IP:%s"%scope_ip) #Connects to the oscilloscope.
	if(connection==False):
		#~ print('Unable to connect to the oscilloscope!')
		return (False,'Unable to connect to the oscilloscope!')

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
	response=scope.WriteString(chstr+"TRLV %f"%(trig_level),1)
	response=scope.WriteString(chstr+"TRSL %s"%(trig_slope),1)

	response=scope.WriteString("TRSE %s,SR,C%i"%(trig_type,trig_source),1)
	response=scope.WriteString("TDIV %f"%(timebase),1)
	response=scope.WriteString("TRDL %f;MSIZ %d;"%(timeoffset,max_sample),1)
	response=scope.WriteString("BWL C%i, %s;"%(chno,bandwidth),1)
	response=scope.WriteString(chstr+"TRA %s"%(tracemode),1)

	scope.Disconnect() #Disconnects from the oscilloscope
	#~ print('Oscilloscope successfully initialized!')
	return (True,'Oscilloscope successfully initialized!')



if __name__ == '__main__':
	
	filename='HyT-input.dat' # i know you wanna hyt it
	names,values=rf.readpars(filename)

	for i in range (len(names)):
		try:
			exec(names[i]+"=%s"%(values[i]))
		except (NameError, SyntaxError):
			exec(names[i]+"='%s'"%(values[i]))
	resp=scope_initialize()
	print(resp)
