#readfile
import pandas as pd
import numpy as np

def readpars(filename):
    with open(filename) as f:
        lines = f.readlines()
    # print(lines)
    params=[]
    values=[]

    for i in range (len(lines)-1):    
        param=''
        value=''
        j=0
        val=0
        while True:
            try:
                char=lines[i][j]
            except IndexError:
                break
           
            if (char != '=')&val==0:
                param+=char
        
            if val==1:
                value+=char
             
            if char=='=':
                val=1
                        
            if char=='#':
                break       
        
            j+=1
        
        param = param.rstrip('=')
        value = value.rstrip('\n')
        param = param.strip()
        value.replace(" ","")
        param.replace(" ","")
        if param != '#':
            params.append(param)
            values.append(value)
    
    return params, values
    
        
        
if __name__ == '__main__':
    filename = './input/HyT-input.dat'
    params, values = readpars(filename)
    # print(params)
    
    
def readdecfile(filename,sign):
    '''
            Reads T2jump.out files from deceleration simulation
            required for creating decelerator burst sequences!
    '''

    rowsskip= (0,1,2,3,4) #skip unnecessary rows, s.t. files can be read in easily, the first 4 lines are not used
    data=pd.read_csv(filename,skiprows=rowsskip,delim_whitespace=True,header=None,on_bad_lines='skip')
    data = data.iloc[:-3]
    data=np.array(data)
    data=np.insert(data,0,[1010,'0x0010','!',0],axis=0)
    # print(data)
    ''' 
        since this line (first of decelerator sequence) is always the same and it does not have
        the same shape as the rest, it is skipped when reading the file and then added.
    '''

    duration=[]
    data=pd.DataFrame(data)
    data[0] = data[0].astype(int)
    ns=1e-9
    unit=ns
    if sign=='V':
        time=(data[data[1]=='0x0010'][0]-data[0][0])
        duration=np.array([(data[0][2*i+1]-data[0][2*i]) for i in range(time.shape[0])])
        time=np.array(time)*unit
        duration=np.array(duration)*unit

    if sign=='H':
        time=(data[data[1]=='0x0020'][0]-data[0][0])
        duration=np.array([data[0][2*i+2]-data[0][2*i+1] for i in range(time.shape[0])])
        time=np.array(time)*unit
        duration=np.array(duration)*unit

    return time, duration

#~ for i in range (len(params)):
    #~ try:
        #~ exec(params[i]+"=%s"%(values[i]))
    #~ except (NameError, SyntaxError):
        #~ exec(params[i]+"='%s'"%(values[i]))

#~ print(scan_step)
    

    
    
    
