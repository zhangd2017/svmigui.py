import socket    # used for TCP/IP communication

def pulsare_wavelength(TCP_IP,TCP_PORT,wavelength):
	BUFFER_SIZE = 4096
	#connect
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as msg:
        s = None
        continue
        
  	try:
        s.connect((TCP_IP, TCP_PORT))
    except socket.error as msg:
        s.close()
        s = None
        continue
    
	if s is None:  
		#~ print 'Could not connecto to Pulsare!'
		return (False,'Could not connecto to Pulsare!')
		
	msg=b"RemoteConnect\r\n"
	s.sendall(msg)
	resp=(s.recv(BUFFER_SIZE))
	wn_to_nm=10000000.00
	wlval=1/(wavelength*100)*1e9 #cm^-1 to nm
	msg=b'SetWavelength %.8f\r\n'%wlval
	s.sendall(msg)
	resp=s.recv(BUFFER_SIZE))
	s.close()
	
if __name__ == '__main__':
	TCP_IP='131.152.105.89'
	TCP_PORT=65510
	wavelength=17734.9	# fundamental in cm^-1
	resp=pulsare_wavelength(TCP_IP,TCP_PORT,wavelength)
	print(resp)
