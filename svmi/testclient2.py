import time
from xmlrpc.client import ServerProxy
import numpy as np
import unidaq as ud



class LaserLock():
    def __init__(self):
        self.kp = 1
        self.ki = 1
        self.setwl = 397
        self.piezovoltage = 0
        self.integral_window = 100
        self.ud_channel = 0
        self.ud_boardno = 0
        self.sleeptime = 0.2
        self.server_ip = "131.152.105.174"
        self.server_port = 8000
        self.piezo_max = 0.5
        print('Super Duper Ultra Wave Length Client 3000')
        print('ip', self.server_ip)
        print('port', self.server_port)
    
    
    def connect(self):
        link = 'http://' + self.server_ip + ':' + str(self.server_port)
        self.server = ServerProxy(link)
        ts, wl = self.server.get_wavelength()
        print(ts)
        print(wl)
        return
        
    def set_piezovoltage(self, voltage):
        udaq = ud.UniDaq()
        udaq.initalize()
        udaq.GetCardInfo(self.ud_boardno)
        udaq.ConfigAO(self.ud_boardno,self.ud_channel,3)
        udaq.WriteAOVoltage(self.ud_boardno,self.ud_channel,voltage)
        udaq.close()
        return
        
    def lock(self):
        integral_list = np.zeros(self.integral_window)
        while True:
            ts, wavelength = self.server.get_wavelength()
            dwl = wavelength - self.setwl
            
            tmp = np.insert(integral_list, 0, dwl)
            integral_list = np.delete(tmp,-1)
            integral_value = np.sum(integral_list)
            
            dv = self.kp * dwl + self.ki * integral_value
            self.piezovoltage = self.piezovoltage + dv
            
            if np.abs(self.piezovoltage) < self.piezo_max:
                self.set_piezovoltage(self.piezovoltage)
            else:
                print('Voltage not within boundaries')
            print(wavelength)
            print(dwl)
            print(self.piezovoltage)
            
            time.sleep(self.sleeptime)
            
if __name__ == '__main__':
    Locken = LaserLock()
    Locken.setwl = 396.956486463458
    Locken.kp = 1e-6
    Locken.ki = 1e-6
    
    Locken.connect()
    Locken.lock()