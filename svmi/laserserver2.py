# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 12:19:48 2020

@author: Claudantus
"""

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import datetime
from pytz import reference
# import wlmdriver as wm

print('Ultra XXL mega laser server')
# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Create server
localip="131.152.105.218"
localport=8000

# localip="127.0.0.1"
# localport=50080
server = SimpleXMLRPCServer((localip, localport),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


  
def get_wavelength():
    # wm.EnableInterferogram()
    # inter1, inter2 = wm.Interferogram()
    # wavelength = wm.GetWavelength()

    localtime = reference.LocalTimezone()
    now = datetime.datetime.now()
    ts = str(now.strftime("%Y-%m-%d %H:%M:%S" + localtime.tzname(now))).strip('W. Europe Daylight Time') 
    wavelength = 1337
    # ts = 1
    return ts, wavelength
server.register_function(get_wavelength, 'get_wavelength')



server.serve_forever()
