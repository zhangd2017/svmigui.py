import spinapi as sp
import time
import signal
import sys
import pandas as pd
import numpy as np
import plotsequence as plotseq
from math import gcd
import pulseblaster as pb
import readfile as rf


def lcm(a):
	'''
			find lowest common multiple of items in a list
	'''
	lcm = a[0]
	for i in a[1:]:
		# 2.03.06.27 I made modifications in the following line such that the error
		# TypeError: 'float' object cannot be interpreted as an integer
		# is eliminated!!
		lcm = int(lcm * int(i) / gcd(int(lcm), int(i)))
		# lcm = lcm*i/gcd(lcm, i)
		# print(gcd(lcm,i))
	return lcm

# this return a list
def indexlist(lists, element):
	'''
	creates a list of indices with a certain value from given list
	'''
	indices= [i for i, x in enumerate(lists) if x == element]
	return indices
        
def pulses(units1, chno1, time1, units2, chno2, time2, freqs, pulsenature, checkboxvals, posnegvals, scanchannel, relchannel, scantime, t2jumpfile):
	
	lastindex=17
	units={'ns':1e-9, 'μs':1e-6, 'ms':1e-3, 's':1}
	
	#~ read all channels and times from gui
			
	freqmin=min(freqs)
	freqmax=max(freqs)

	#~ create one sequence from the channels and times
	#look for T0
	channels=0
	events=0
	tottime=0
	chno=18
	ch_done=[]
	ch_list=[i for i in range(lastindex+1)]

	durations={}
	events={}
	
	#~ sequence starts relative to channel T0 : find channel related to T0
	''' 
			To change: XXX find indexlist and get the events for all indexes with same channel
	'''
	starttag='T0'
	indexes=indexlist(chno1,starttag)
	# print(indexes)
	reptime=1/lcm(freqs)
	pulsetime=1/freqmin
	# print(indexes)
	# print(reptime)
	# print(pulsetime)
	
	
	''' 
			Do first pulse, starting at T0
	'''
	n=0
	

	score = 0
	for i in range(len(time1)):
		score+=int(time1[i]>1/freqs[i])+int(time2[i]>1/freqs[i])
	# print(score)
	#~ print(score)	
	if score>0:
		msg = 0
		return ['nothing'], msg
		
	while tottime<pulsetime:

		index=indexes[0]
		if checkboxvals[index]==True:
			if pulsenature[index]=='normal pulse':
				n+=1
				events['%ib%03i'%(index+1,n)]=time1[index]+(n-1)*1/freqs[index]
				events['%ie%03i'%(index+1,n)]=events['%ib%03i'%(index+1,n)]+time2[index]
				durations['%id%03i'%(index+1,n)]=time2[index]
				tottime+=1/freqs[index]
			channels+=1
			ch_done.append(index)
		else:
			#~ print('T0 not checked')
			return 'T0 not checked'
	# print(events,durations,tottime,ch_done,channels,index)

	nextindex=index
	'''
			Do all connected pulses
	'''
	while channels<chno:

		try:
			nextindex=indexlist(chno1,'%ib'%(nextindex+1))[0]
		except IndexError:
			#~ print('Index Error channel flags: %i'%nextindex)
			break
			
		ch_done.append(nextindex)
		tottime=0
		m=0
		
		while tottime<pulsetime:			
			try:
				if checkboxvals[nextindex]==True:
					done=0
					if scanchannel in '%ib'%(nextindex+1):
						
						print('scanchannel %s'%scanchannel)
						m+=1
						events['%ib%03i'%(nextindex+1,m)]=events['%s%03i'%(relchannel,1)]+scantime+(m-1)*1/freqs[nextindex]
						events['%ie%03i'%(nextindex+1,m)]=events['%ib%03i'%(nextindex+1,m)]+time2[nextindex]
						durations['%id%03i'%(nextindex+1,m)]=events['%ie%03i'%(nextindex+1,m)]-events['%ib%03i'%(nextindex+1,m)]
						#~ tottime+=1/freqs[nextindex]
						#~ print(events['%ib%03i'%(nextindex+1,m)])
						#~ print(events['%ie%03i'%(nextindex+1,m)])
						#~ print(durations['%id%03i'%(nextindex+1,m)])
						done=1
						tottime+=1/freqs[nextindex]
					
					if (pulsenature[nextindex]=='normal pulse' and done==0):
						m+=1
						events['%ib%03i'%(nextindex+1,m)]=events['%s%03i'%(chno1[nextindex],1)]+time1[nextindex]+(m-1)*1/freqs[nextindex]
						events['%ie%03i'%(nextindex+1,m)]=events['%ib%03i'%(nextindex+1,m)]+time2[nextindex]
						durations['%id%03i'%(nextindex+1,m)]=events['%ie%03i'%(nextindex+1,m)]-events['%ib%03i'%(nextindex+1,m)]
						tottime+=1/freqs[nextindex]
						
					if (pulsenature[nextindex]=='burst unit decelerator (+)' and done==0):
						#~ print('bursting around +')
						dectime,decdur=rf.readdecfile(t2jumpfile,'V')
						m+=1
						n=m
					
						for i in range (dectime.shape[0]):
							events['%ib%03i'%(nextindex+1,n)]=events['%s%03i'%(chno1[nextindex],1)]+time1[nextindex]+(m-1)*1/freqs[nextindex]+dectime[i]
							events['%ie%03i'%(nextindex+1,n)]=events['%ib%03i'%(nextindex+1,n)]+decdur[i]
							durations['%id%03i'%(nextindex+1,n)]=decdur[i]
							n+=1
							
						tottime+=1/freqs[nextindex]
						#~ break
						
					if pulsenature[nextindex]=='burst unit decelerator (-)':
						#~ print('bursting around -')
						dectime,decdur=rf.readdecfile(t2jumpfile,'H')
						#~ print(decdur)
						m+=1
						n=m
						
						for i in range (dectime.shape[0]):
							events['%ib%03i'%(nextindex+1,n)]=events['%s%03i'%(chno1[nextindex],1)]+time1[nextindex]+(m-1)*1/freqs[nextindex]+dectime[i]
							events['%ie%03i'%(nextindex+1,n)]=events['%ib%03i'%(nextindex+1,n)]+decdur[i]
							durations['%id%03i'%(nextindex+1,n)]=decdur[i]
							n+=1
							
						tottime+=1/freqs[nextindex]
					

				else:
					break
			except KeyError:
				print('keyerror: connected =%i'%m)
				break
		channels+=1
	# print(events)
	# upto here, only timings for 4 channels are calculated (1-4)
	'''
			Do all the pulses which were not done so far
	'''
	ch_todo=list(set(ch_list)-set(ch_done))
	
	for nextindex in ch_todo:
		tottime=0
		m=0
		while tottime<pulsetime:
			try:
				if checkboxvals[nextindex]==True:
					if pulsenature[nextindex]=='normal pulse':
						m+=1
						events['%ib%03i'%(nextindex+1,m)]=events['%s%03i'%(chno1[nextindex],1)]+time1[nextindex]+(m-1)*1/freqs[nextindex]
						events['%ie%03i'%(nextindex+1,m)]=events['%ib%03i'%(nextindex+1,m)]+time2[nextindex]
						durations['%id%03i'%(nextindex+1,m)]=events['%ie%03i'%(nextindex+1,m)]-events['%ib%03i'%(nextindex+1,m)]
						tottime+=1/freqs[nextindex]
						
					if pulsenature[nextindex]=='burst unit decelerator (+)':
						#~ print('bursting around +')
						dectime,decdur=rf.readdecfile(t2jumpfile,'V')
						m+=1
						n=(m-1)*dectime.shape[0]
						# n=m
					
						for i in range (dectime.shape[0]):
							events['%ib%03i'%(nextindex+1,n+i)]=events['%s%03i'%(chno1[nextindex],1)]+time1[nextindex]+(m-1)*1/freqs[nextindex]+dectime[i]
							events['%ie%03i'%(nextindex+1,n+i)]=events['%ib%03i'%(nextindex+1,n+i)]+decdur[i]
							durations['%id%03i'%(nextindex+1,n+i)]=decdur[i]
							# add the following line 2023.06.27
							# it doesn't work so comment it
							# n+=1
		
							
						tottime+=1/freqs[nextindex]
						
					if pulsenature[nextindex]=='burst unit decelerator (-)':
						#~ print('bursting around -')
						dectime,decdur=rf.readdecfile(t2jumpfile,'H')
						m+=1
						# n = (m - 1) * dectime.shape[0]
						n=m
						
						for i in range (dectime.shape[0]):
							events['%ib%03i'%(nextindex+1,n)]=events['%s%03i'%(chno1[nextindex],1)]+time1[nextindex]+(m-1)*1/freqs[nextindex]+dectime[i]
							events['%ie%03i'%(nextindex+1,n)]=events['%ib%03i'%(nextindex+1,n)]+decdur[i]
							durations['%id%03i'%(nextindex+1,n)]=decdur[i]
							n+=1
							
						tottime+=1/freqs[nextindex]
				else:
					break

			except KeyError:
				#~ print('keyerror: %i'%nextindex)
				break
				
			except IndexError:
				#~ print('indexerror: %i'%nextindex)
				break

		channels+=1
	# print(events)
	'''
			seems to work so far
	'''
		
	
	#~ print(events)
	#~ sort times in increasing order and then sort the keys by the same order
	times=sorted(events.values())
	keyindexes=[list(events.values()).index(time) for time in times] #indexes in order
	keys=[list(events.keys())[index] for index in keyindexes] # keys of these ordered indexes
	#~ print(keys)
	# print(events)
	# print(keys)
	# print(times)
	#~ create the pulses for all channels
	'''extract int from string:
		[int(s) for s in str.split() if s.isdigit()]'''
		
	resultion=1e-10
	activechannels=[]
	activeflags=[]
	output=[]



	
	for i in range(len(keys)-1):
		lastdig=4

		try:
			duration = times[i+1]-times[i]
			channelb=int(keys[i][:-lastdig])
			flagb=keys[i][-lastdig]
			mb=keys[i][-lastdig+1:]
		except ValueError:
			lastdig = 5
			duration = times[i+1]-times[i]
			channelb=int(keys[i][:-lastdig])
			flagb=keys[i][-lastdig]
			mb=keys[i][-lastdig+1:]
			
		lastdig=4

			
		try:		
			channele=int(keys[i+1][:-lastdig])
			flage=keys[i+1][-lastdig]
			me=keys[i+1][-lastdig+1:]
		except ValueError:
			lastdig=5
			channele=int(keys[i+1][:-lastdig])
			flage=keys[i+1][-lastdig]
			me=keys[i+1][-lastdig+1:]

		lastdig=4

		
		for channel in activeflags:
			try:                    
				if durations[channel]<=resultion:
					#~ print('remove %s'%(channel))

					activechannels.remove(int(channel[:-lastdig])) 
					activeflags.remove(channel)
			except KeyError:
				pass
				
			except ValueError:
				lastdig=5
				if durations[channel]<=resultion:
					#~ print('remove %s'%(channel))

					activechannels.remove(int(channel[:-lastdig])) 
					activeflags.remove(channel)
				
						
		if flagb=='b':
			activechannels.append(channelb)
			activeflags.append('%id%s'%(channelb,mb))

			#~ print('add %i%s'%(channelb,mb))

		for channel in activeflags:
			try:
				durations[channel]-=duration
				if durations[channel]<resultion:
					durations[channel]=0
			except KeyError:
				pass
				
		
				
		

		chflag=pb.channelflag(activechannels)
		for chno in range(len(posnegvals)):
			if posnegvals[chno]=='Negative':
				ch=list(chflag)
				if chflag[chno]=='1':
					ch[chno]='0'
				else: 
					ch[chno]='1'
				
				chflag="".join(ch)
					
		output.append([chflag,float(duration)])
		#~ print(chflag)
		#~ print(duration)

		
	#
	'''
		finish whole sequence and fill with waittime
	'''
	chflag=pb.channelflag([])
	for chno in range(len(posnegvals)):
		if posnegvals[chno]=='Negative':
			if posnegvals[chno]=='Negative':
				ch=list(chflag)
				if chflag[chno]=='1':
					ch[chno]='0'
				else: 
					ch[chno]='1'
				
				chflag="".join(ch)
					
	output.append([chflag,float(duration)])
	duration = 1/freqmin-max(times)
	output.append([chflag,duration])
	output=np.array(output).T
	
	
	#~ plotseq.plotsequence(output)
	#~ self.tof_scan()
		
	# print(output)
	msg = 1
	return output,msg
