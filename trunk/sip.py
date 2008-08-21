import sys
from core import Server
from core import UDPHandler
from core import Log
import core

import time 

VERSION = "0.1"
OPTION = {}

class SIPServer(Server):
	def __init__(self,args=""):
		self.id = "PySIPServer v."+VERSION
		self.ip = "" #valores por defecto
		self.port = 5060 #valores por defecto
		self.loglevel = 1
		Server.__init__(self,args)
		self.family = core.UDP

class SIPHandler(UDPHandler):
 	def __init__(self,data,origin,parent=None,verbosity=1,logs={}):
		UDPHandler.__init__(self,data,origin)
		self.log = logs
		self.parent = parent
		self.secuence  = ['request','headers','run',"run_register","run_subscribe",'end']
		self.report("connected")

	def step_request(self):
		"""receiving command"""
		self.report("connected:"+str(self.incoming))
		pattern = "(?P<command>(REGISTER|SUBSCRIBE)) "
		pattern +="(?P<user>(\S*)) "
		pattern +="(?P<protocol>((\S)*))"
		pattern +="(\r\n)?"
		self.request = self.receive(pattern)
		if type(self.request) is core.Error:
			print self.request
			self.next_step("end")
		else:
			self.request["params"]= {}
			self.next_step()

	def step_headers(self):
		"""receiving param"""
		param_pattern = "(?P<name>(([a-zA-Z0-9\W])*)): "
		param_pattern += "(?P<value>((\S)*))"
		param_pattern += "(\r)?"
		pattern = "((\r\n)|"+param_pattern+")"
		param = self.receive(pattern)
		if type(param) is not dict:
			self.next_step("end")
		elif not param["name"]:
			self.next_step()
		else:
			self.request["params"][param["name"]]= param["value"]

	def step_run(self):
		"""state switch by command"""
		if self.request["command"] == "REGISTER": 
			self.next_step("run_register")
		elif self.request["command"] == "SUBSCRIBE": #,"subscribe"]:
			self.next_step("run_subscribe")
		#elif self.request["command"] == "INVITE": #SUBSCRIBE": #,"subscribe"]:
		#	self.next_step("run_invite")
		else:
			self.next_step("end")

	def size(self,file):
		oldpos = file.tell()
		file.seek(0,2)
		l = file.tell()
		file.seek(oldpos)
		return l

	def step_run_register(self):
		"""efectuando el registo del usuario"""
		msg = "SIP/2.0 200 OK\n"
		msg +="Allow: INVITE, ACK, CANCEL, OPTIONS, BYE\n"
		msg +="\n"
		self.send(msg) 
		self.next_step("end")

	def step_run_subscribe(self):
		"""efectuando la subscripcion del usuario"""
		msg = "SIP/2.0 200 OK\n"
		msg +="Via: SIP/2.0/TCP subB.example.com;branch=q4i9ufr4ui3;"
		msg +="received=192.168.1.11\n"
		msg +="\n"
		self.send(msg) 
		self.next_step("end")
				
	def step_run_invite(self):
		"""realizando invitacion"""
		#self.send("SIP(2.0 603 Decline\n\n")
		self.next_step("end")
				
	def step_run_get(self):
		filename = ROOT +  self.request["file"]
		if filename[-1] == "/":
			filename = filename + "index.html"
		try:
			file = open(filename)	
		except Exception, e:
			self.send("HTTP/1.0 400 Not Found\n")
			self.next_step("end")
		else:
			self.file = file
			self.send("HTTP/1.0 200 OK\n")
			self.send("Date: "+time.ctime()+"\n")
			self.send("Content-Type: text/html\n")
			self.send("Content-Length: "+str(self.size(file))+"\n")
			self.send("\n")
			for data in file.read():
				self.socket.send(data)
			self.next_step("end")

	def step_end(self):
		"""ends session"""

if __name__ == '__main__':
	LOGLEVEL = 1
	print "init."
	server = SIPServer(sys.argv)
	server.mainloop(SIPHandler,limit=100) #) #,23000,"",1 )