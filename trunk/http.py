import sys
from core import Server
from core import TCPHandler
from core import Log
import core


import time 

VERSION = "0.1"
ROOT = "./www"
OPTION = {}

class HTTPServer(Server):
	def __init__(self,args=""):
		self.id = "PyHTTPServer v."+VERSION
		self.ip = "" #valores por defecto
		Server.__init__(self)
		self.config["verbosity"] = 1
		self.config["port"] = 8000 #valores por defecto
		self.config["configfile"] = "http.cfg" 
		self.configure(args)	

	def config_rootdir(self,value):
		"""r:<dir> sets document root directory"""
		if value:
			try: open(value)
			except IOError, e:
				if e.errno == 21:
					self.config["rootdir"] = value
			else:
				self.log(value+" is not a directory.",0)
		else:
			print self.usage()

class HTTPHandler(TCPHandler):
 	def __init__(self,socket,parent=None,verbosity=1,logs={}):
		TCPHandler.__init__(self,socket)
		self.parent = parent
		self.log = self.parent.log
		self.next = 'request'
		self.secuence  = ['request','headers','run',"run_get",'end']
		self.log("connected")

	def step_request(self):
		"""receiving command"""
		#self.send("login:")
		pattern = "(?P<command>(GET)) "
		pattern +="(?P<file>(([a-zA-Z0-9\._/])*)) "
		pattern +="(?P<protocol>(([a-zA-Z0-9\._/ ])*))"
		pattern +="(\r\n)?"
		self.request = self.receive(pattern)
		self.request["params"]= {}
		self.next_step('headers')

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
			self.next_step('run')
		else:
			self.request["params"][param["name"]]= param["value"]

	def step_run(self):
		"""state switch by command"""
		if self.request["command"] == "GET":
			self.next_step("run_get")
		else:
			self.next_step("end")

	def size(self,file):
		oldpos = file.tell()
		file.seek(0,2)
		l = file.tell()
		file.seek(oldpos)
		return l

	def step_run_get(self):
		address = self.address() 
		self.log("received GET from "+address,0)
		root = self.parent.config["rootdir"]
		filename = root +  self.request["file"]
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


if __name__ == '__main__':
	LOGLEVEL = 1
	print "init."
	server = HTTPServer(sys.argv)
	server.mainloop(HTTPHandler,limit=100) #) #,23000,"",1 )
