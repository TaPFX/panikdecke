
from PanikDeckeServer import PanikDeckeServer
import os

import socket

def get_ip_address():
 ip_address = '';
 s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 while True:
  try:
   if s.connect(("8.8.8.8",80)) == None:
    ip_address = s.getsockname()[0]
    s.close()
    break
  except:
   print("try again")
  finally:
   s.close()
     
 return ip_address

serverInst = PanikDeckeServer(ip=get_ip_address())
