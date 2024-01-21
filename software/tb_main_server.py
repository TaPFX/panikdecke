
from PanikDeckeServer import PanikDeckeServer
import os

if(os != 'nt'):
    serverInst = PanikDeckeServer(ip='Panikdecke')
else:
    serverInst = PanikDeckeServer() #run on localhost
