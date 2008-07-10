import socket
import re
import sys
import time
from threading import Thread


letters = r"[a-z,A-Z]"
numbers = r"[0-9]"
decimal_point = r"\."

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
	def __init__(self,filename=None,minlevel=0):
		self.minlevel = minlevel
		self.file = None
		if filename:
			if type(filename) == file:
				self.file = filename 
			else: 
				try:
					self.file = open(filename,'a')
				except IOError:
					msg =  "Warning: unable to open filename:"
					msg += filename + "."
					print msg
					self.file = None

	def put(self,msg,level=2):
		#print ">"+str((msg,level))
		if level < self.minlevel: return
		#if self.id : p = str(self.id)+":"
		#else: p = self.ip
		s = time.ctime()+":"
		#s += p+":"
		s += msg.encode('string_escape')
                if self.file:
			self.file.write(s+"\n")
	                self.file.flush()
		else:
			print s

class Out(Log):
	None	


def parse_args(args):
	r = {}
	value = []; param = None
	while args:
		arg = args.pop(0)
		if arg.startswith("-"):
			param = arg.replace("-","")
			r[ param ] = []
			value = r[ param ]
		else:
			value +=[ arg ]
	return r
	
def get_arg(args, param):
	if not args.has_key(param): return None
	return " ".join( args[param] )

class Server:
	def __init__(self,args):
		#print "based on GAS"
		self.log = {}
		self.config = {}
		if args:
			parsed = parse_args(args)
			self.args = self.load_args(parsed)

	def report(self,msg,level=2):
		c = str(self.id)+":"
		msg = c + msg
		if self.log.has_key('output'):
			self.log["output"].put(msg,level)
		else:
			print msg		

	def error(self,msg,level=2):
		if self.log.has_key('error'):
			self.log["error"].put(msg,level)
		else:
			print "ERROR:"+msg	

	def load_config(self):
		params = {}
		for m in dir(self):
			if m.startswith("config_"):
				param = m.replace("config_","")
				function = eval("self."+m)
				doc = function.__doc__
				id = doc.split(":")[0]
				params[id] = param
				methods[param] = function			
			

	def load_args(self,arg):
		output_file = get_arg(arg,"l")	
		self.log["output"] = Log(output_file) 
		error_file = get_arg(arg,"e")
		self.log["error"]= Log(error_file)
		port_arg = get_arg(arg,"p")
		if port_arg: self.port = int(port_arg) 
		loglevel_arg = get_arg(arg,"v")
		if loglevel_arg: self.loglevel = int(loglevel_arg)

	def config_configfile(self,value):
		"""c:specifies config file to load"""
		if value:
			self.configfile = value
		else:
			self.usage()
	
	def config_listenport(self,value):
		"""p:<file> specifies TCP port to listen"""
		if value:
			self.config["port"] = int(value)
		else:
			self.usage()



	def usage(self):
		msg = ""
		for m in dir(self):
			if m.startswith("config_"):
				param = m.replace("config_","")
				function = eval("self."+m)
				doc = function.__doc__
				param  = "-"+doc.split(":")[0]
				line = doc.split(":")[1]
				msg += param + ":" + usage + "/n" 
		return msg
#		return """\
#-l <file> : specifies standard log output\n
#-e <file> : specifies error log output\n
#-p <port> : TCP port to listen\n
#-v <1-10> : verbosity\n
#"""
	def mainloop(self,handler=None,limit=1000):
		r = "listening on port "+str(self.port)
		if self.ip: r += " for incoming connections from "+self.ip
		r += "\n"
		self.report(r,3)
		s = socket.socket();
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((self.ip,self.port))
		s.listen( limit )
		while 1 :
			(c, address) = s.accept()
			h = handler(c,address,self)
			h.log = self.log
			h.start()

class Handler(Thread):

	def report(self,msg,level=2):
		c = str(self.id)+":"
		msg = c + msg
		if self.log.has_key('output'):
			self.log["output"].put(msg,level)
		else:
			print msg		

	def error(self,msg,level=2):
		if self.log.has_key('error'):
			self.log["error"].put(msg,level)
		else:
			print "ERROR:"+msg		

	def __init__(self,socket):
		self.socket = socket
		self.socket.settimeout(60)
		incoming = socket.getpeername()
		self.id = str(incoming[0])+":"+str(incoming[1])
		self.done = []
		Thread.__init__(self)

	def run(self):
		self.current=self.secuence.pop(0)
		while self.secuence:
			exec("self.step_"+self.current+"()")
			if self.current == 'end': break
		self.socket.close()

	def send(self,data):
		s = self.socket
		if not data: return None
		try: 
			s.send(data) #+platform.protocol.EOL)
		except socket.error, msg:
			self.error(10,msg+"sending:"+data+".")

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
					send = Error(2,pattern+input)
					break;
				else: 
					# tenemos cadena
					send = resultado.groupdict()
					break;
		if send == None : send = Error(1)
		return send

	def receive(self,pattern="(?P<input>(.*))"):
		s = self.socket
		data = s.recv(1000)
		m = re.match(pattern,data)
		if m: return m.groupdict()
		else: return None

	def log_step(self,state=None):
		if not state: state = self.current
		s = eval("self.step_"+state)
		if s.__doc__:
			self.report("current state:"+s.__doc__,12)
		else:
			self.report("current state:"+state,12)

	def next_step(self,state=None):
		if state:
			position = self.secuence.index(state)
			self.current = state
			self.done += self.secuence[:position]
			self.secuence = self.secuence[position+1:]
		else:
			self.done += [self.current]
			self.current = self.secuence.pop(0)
		self.log_step()

	def back_step(self,nam):
		self.secuence = [self.current] + self.secuence
		self.current = name
		self.log_step()

	def step_end(self):
		self.report("end of process.")
	

