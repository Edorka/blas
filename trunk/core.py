import socket
import re
import sys
import time
from threading import Thread


letters = r"[a-z,A-Z]"
numbers = r"[0-9]"
decimal_point = r"\."

TCP = 0
UDP = 1

def join_or(*arg):
	s = ""
	for a in arg:
		if s: s+="|"
		s+=a
	return s

def join_and(*arg):
	s = ""
	for a in arg:
		if s: s+="|"
		s+=a
	return s

def under(name,content):
	pre = "(?P<"+name+">"
	port = ")"
	return pre+content+post

class Log:
	def __init__(self,minlevel=0):
		self.minlevel = minlevel

	def set(self,minlevel):
		self.minlevel = minlevel
		
	def put(self,msg,level=1):
		if  level > self.minlevel: return
		s = time.ctime()+":"
		s += msg#.encode('string_escape')
		print s

	def __call__(self,msg,level=1):
		self.put(msg,level)

class FileLog(Log):
	def __init__(self,filename=None,minlevel=0):
		Log.__init__(self,minlevel)
		self.file = None
		if filename:
			try:
				self.file = open(filename,'a')
			except IOError:
				msg =  "Warning: unable to open filename:"
				msg += filename + "."
				print msg

	def put(self,msg,level=1):
		if not level > self.minlevel: return
		s = time.ctime()+":"
		s += msg.encode('string_escape')
                if self.file:
			self.file.write(s+"\n")
	                self.file.flush()
		else:
			print s

class Error(Exception):
	def __init__(self,msg):
		self.msg = msg
	def __str__(self):
		return "Error: "+str(self.msg)

def parse_params(args):
	r = {}
	value = []; param = None
	while args:
		arg = args.pop(0)
		if arg.startswith("-"):
			if param: r[ param ] = " ".join(r[ param ])
			param = arg.replace("-","")
			r[ param ] = []
			value = r[ param ]
		else:
			value += [arg] 
	if param: r[ param ] = " ".join(r[ param ])
	return r

def parse_config(data):
	r = {}
	for line in data:
		if "=" in line:
			if line.endswith("\n"): line = line[:-1]
			param,value = line.split("=")
			r[param] = value
	return r

def get_arg(args, param):
	if not args.has_key(param): return None
	return " ".join( args[param] )

class Server:

	def __init__(self,args=""):
		self.log = Log() #self.config["verbosity"] ) #temporal log
		self.config = {}

	def configure(self,args):
		#self.config["configfile"] = "telnet.cfg"
		#self.config["verbosity"] = 1
		self.family = TCP
		config_methods = self.get_config_methods()
		prev_params = []
		if args:
			params = parse_params(args)
			#test if there is config
			param_of = self.get_prefixes()
			for prefix,value in params.items():
				if param_of.has_key(prefix):
					param = param_of[prefix]	
					self.run_config(param,value,config_methods)
					prev_params.append(param)		
					print prev_params
				else: 
					print "unknown parameter: ",prefix
					print self.usage()
					exit(-1)
		filename = self.config["configfile"] 
		try:
			fd = open(filename)
		except Exception,e:
			self.log("no config file found."+self.config["configfile"])
		else:
			fileparams = parse_config(fd.readlines())
			for param,value in fileparams.items():
				if not param in prev_params:
					self.run_config(param,value,config_methods)
			#self.args = self.load_args(parsed)
		
	#@def report(self,msg,level=2):
	#	c = str(self.id)+":"
	#	self.log.put(msg,level)
		#msg = c + msg
		#if self.log.has_key('output'):
		#	self.log["output"].put(msg,level)
		#else:
		#	print msg		


	def run_config(self,param,value,config_methods):
		#print "trying:",param,value
		if config_methods.has_key(param):
			config_methods[param](value)
		else:
			msg = "Fail to load parameter:"+param+"\n"
			msg += self.usage()
			self.log.put(msg)	
			exit

	def get_config_methods(self):
		param_func = {}
		for m in dir(self):
			if m.startswith("config_"):
				param = m.replace("config_","")
				function = eval("self."+m)
				doc = function.__doc__
				id = doc.split(":")[0]
				param_func[param] = function
		return param_func

	def get_prefixes(self):
		r = {}
		for m in dir(self):
			if m.startswith("config_"):
				param = m.replace("config_","")
				function = eval("self."+m)
				doc = function.__doc__
				id = doc.split(":")[0]
				r[id] = param
		return r

	def config_configfile(self,value):
		"""c:<file> specifies config file to load"""
		if value:
			self.config["configfile"] = value
		else:
			print self.usage()

	def config_logfile(self,value):
		"""l:<file> specifies file where to log, stdout for console."""
		if value:
			if value == 'stdout':
				self.log = Log(self.config["verbosity"])
				self.log("logging to console")
			else:
				self.log("saving log to file: "+value)
				self.log = FileLog(value,self.config["verbosity"])
		else:
			print self.usage()
	
	def config_listenport(self,value):
		"""p:[1-65535] specifies TCP port to listen"""
		if value:
			self.config["port"] = int(value)
		else:
			print self.usage()

	def config_verbosity(self,value):
		"""v:[0-4] specifies verbosity level"""
		if value:
			self.config["verbosity"] = int(value)
			self.log.set(self.config["verbosity"])
		else:
			print self.usage()

	
	def usage(self):
		msg = ""
		for m in dir(self):
			if m.startswith("config_"):
				param = m.replace("config_","")
				function = eval("self."+m)
				doc = function.__doc__
				param  = "-"+doc.split(":")[0]
				line = doc.split(":")[1]
				msg += param + ":" + line + "\n" 
		return msg
	
	def mainloop(self,handler=None,limit=1000):
		port = self.config["port"]
		self.clients = []
		r = "listening on port "+str(port)
		#if self.ip: r += " for incoming connections from "+self.ip
		#r += "\n"
		self.log(r,0)
		#if not self.family: self.family = TCP
		if self.family is TCP:
			s = socket.socket();
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((self.ip,port))
			s.listen( limit )
		else:
			s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM);
			s.bind((self.ip,port))
		self.socket = s
		running = True
#		try:
		while running:
			if self.family is TCP: 
				(c, address) = s.accept()
				h = handler(c,self)
			else:
				data,addr = s.recvfrom(1500)
				h = handler(data,addr,self)
			self.clients.append(h)
			h.log = self.log
			h.start()
		self.close()
#		except(KeyboardInterrupt, SystemExit):
#			self.close()

	def close(self,msg="closing server"):
		self.log(msg)
		self.socket.close()
		if self.clients:
			self.log("recovering client threads")
			for c in self.clients : 
				if c.isAlive(): c.join(2) #close()


class Handler(Thread):

	#def report(self,msg,level=2):
	#	c = str(self.id)+":"
	#	msg = c + msg
	#	if self.log.has_key('output'):
	#		self.log["output"].put(msg,level)
	#	else:
	#		print msg		

	def error(self,msg,level=2):
		if self.log.has_key('error'):
			self.log["error"].put(msg,level)
		else:
			print "ERROR:"+msg		

	def __init__(self):
		self.done = []
		self.next = None ; self.current = None
		Thread.__init__(self)

	def run(self):
		if not self.next:
			self.next = self.secuence.pop(0)
		#self.current=self.secuence.pop(0)
#		try:
		while self.next:
			self.current=self.next
			self.log_step()
			exec("self.step_"+self.current+"()")
			if self.current == "end" : break		
#		except(KeyboardInterrupt, SystemExit):
#			self.close()

	def receive_line(self,pattern):
		return self.receive(pattern+"(?\r)")

	def log_step(self,state=None):
		if not state: state = self.current
		if not self.current: self.log("nothing left.")
		else:
			s = eval("self.step_"+state)
			if s.__doc__:
				self.log("current state:"+s.__doc__,2)
			else:
				self.log("current state:"+state,2)

	def next_step(self,state=None):
		if state:
			self.next = state
			if state in self.secuence:
				position = self.secuence.index(state)
				self.done += self.secuence[:position]
				self.secuence = self.secuence[position+1:]
		else:
			self.done += [self.current]
			if self.secuence:
				self.next = self.secuence.pop(0)
			else: self.next=None

	def back_step(self,name):
		self.secuence = [self.current] + self.secuence
		self.current = name
		self.log_step()

	

class TCPHandler(Handler):

	def __init__(self,socket):
		self.socket = socket
		self.socket.settimeout(60)
		incoming = socket.getpeername()
		self.id = str(incoming[0])+":"+str(incoming[1])
		Handler.__init__(self)

	def send(self,data):
		s = self.socket
		if not data: return None
		try: 
			s.send(data) #+platform.protocol.EOL)
		except socket.error, msg:
			self.error(10,msg+"sending:"+data+".")

	def step_end(self):
		"""ending and closing connection."""
		self.socket.close()

	def address(self):
		reg = self.socket.getpeername()#dir(self.socket))
		m = reg[0]+":"+str(reg[1])
		return m
	
	def receive(self,pattern=".*"):
		s = self.socket
		s.settimeout(15000)
		c = ""; input = ""; send = None
		resultado = {}
		while c is not  None:
			try:
				c = s.recv(1)
			except socket.error, msg:
				c = None
			if c:
				input += c
			else:
				self.error("timed out");
				#send = Error(2,"timed out")
				break;
			if input == "" and c =="\r":  continue
			if c == '\n': 
				resultado = re.match(pattern,input)
				if resultado == None:
					# ERROR : linea incorrecta
					send = Error("fallo en la recepcion de :"+pattern+"\nse recibio:"+input)
					break;
				else: 
					# tenemos cadena
					send = resultado.groupdict()
					break;
		if send == None : send = Error(1)
		return send



class UDPHandler(Handler):

	def __init__(self,data,origin):
		self.data = data
		self.incoming = origin
		self.id = str(origin[0])+":"+str(origin[1])
		Handler.__init__(self)

	def send(self,data,ip=None,port=None):
		destiny = (self.incoming[0],self.incoming[1])
		if ip: destiny[0] = ip
		if port: destiny[1] = port
		#print "enviando udp:"+str(destiny[0])+":"+str(destiny[1])
		#self.log("ORIGIN:"+self.incoming)
		#if not data: return None
		try: 
			s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
			s.sendto(data,destiny) #+platform.protocol.EOL)
		except socket.error, msg:
			self.error(10,msg+"sending:"+data+".")

	def address(self):
		reg =(self.incoming[0],self.incoming[1])
		m = reg[0]+":"+str(reg[1])
		return m
	
	def receive(self,pattern=".*"):
		c = ""; input = ""; send = None
		resultado = {}
		while c is not None:
			c = self.data[0] ; self.data= self.data[1:]
			if c:
				input += c
			if input == "" and c =="\r":  continue
			if c == '\n': 
				resultado = re.match(pattern,input)
				if resultado == None:
					# ERROR : linea incorrecta
					send = Error("fallo en la recepcion de :"+pattern+"\nse recibio:"+input)
					break;
				else: 
					# tenemos cadena
					send = resultado.groupdict()
					break;
		if send == None : send = Error("fallo en recepcion, retorno nulo")
		return send

	def step_end(self):
		self.log("end of process.")
