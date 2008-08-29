import sys
from core import Server
from core import UDPHandler
from core import Log
import core

import time 
import md5

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
		self.secuence  = ['request','headers','run',"run_register","run_invite","run_subscribe",'end']
		self.report("connected")

	def step_request(self):
		"""receiving command"""
		self.report("connected:"+str(self.incoming))
		pattern = "(?P<command>(REGISTER|SUBSCRIBE|INVITE)) "
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
		param_pattern += "(?P<value>((\S| )*))"
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
		elif self.request["command"] == "INVITE": #SUBSCRIBE": #,"subscribe"]:
			self.next_step("run_invite")
		else:
			self.next_step("end")

	def step_run_invite(self):
		"""realizando invitacion"""
		print self.request

	def step_run_register(self):
		"""efectuando el registo del usuario"""
		#print self.request
		params = self.request["params"]
		if self.digest("REGISTER") == True:
			msg = "SIP/2.0 200 OK\n"
			print params["Authorization"]
		else:
			self.report("fallo en la autentificacion, solicitando.")
			msg = "SIP/2.0 401 Unathorized\n"
			nonce = md5.new(time.ctime()).digest().encode('hex')
			params["nonce"] = nonce
			msg += 'WWW-Authenticate: Digest realm="192.168.1.100", nonce="'+nonce+'", qop="auth"\n'
		print params
		#print self.digest()
		params["To"]= params["From"]
		fields = ['CSeq','Via','From','Call-ID','To','Contact','Server','Content-Length']
		msg += self.compose_headers(params,fields)
		print msg
		self.send(msg) 
		self.next_step("end")

	def compose_headers(self,params={},fields=[]):
		msg = ""
		for field in fields:
			if params.has_key(field):
				if field == 'Via':
					msg+=field+": "+params[field]+"="+str(self.incoming[1])+"\n"
				else: msg+=field+": "+params[field]+"\n"
		msg += "Server: PythonSIP prototype\n"		
		msg +="\n"
		return msg

	def step_run_subscribe(self):
		"""efectuando la subscripcion del usuario"""
		msg = "SIP/2.0 200 OK\n"
		msg +="received=192.168.1.11\n"
		msg +="\n"
		self.send(msg) 
		self.next_step("end")
				
	def step_run_invite(self):
		"""realizando invitacion"""
		#self.send("SIP(2.0 603 Decline\n\n")
		self.next_step("end")

	def digest(self,method=""):
		"""RFC1321 - The MD5 Message-Digest Algorithm"""
		params = self.request["params"]
		if not params.has_key("Authorization"): return False
		auth = params["Authorization"]
		if not auth.startswith("Digest"): return False
		auth=auth.replace("Digest ","")
		data = {}
		for line in auth.split(","):
			#print line
			reg = line.split("=")
			reg[0] = reg[0].strip(" ")
			data[reg[0]] = reg[1].strip('"')
		a1 =  data["username"]+":"+data["realm"]+":prueba"
		a2 =  method+":"+data["uri"]
		s1 = md5.new() ; s1.update(a1)
		s2 = md5.new() ; s2.update(a2)
		a = s1.digest().encode('hex')
		a += ":"+data["nonce"]+":"+data["nc"]+":"+data["cnonce"]+":"+data["qop"]
		a += ":"+s2.digest().encode('hex')
		#print "A:",a
		sum = md5.new() #time.ctime()).digest().encode('hex')
		sum.update(a)
		#print "DIGEST:",data["response"],"==",sum.digest().encode('hex')
		return data["response"]==sum.digest().encode('hex')

	def step_end(self):
		"""ends session"""

if __name__ == '__main__':
	LOGLEVEL = 1
	print "init."
	server = SIPServer(sys.argv)
	server.mainloop(SIPHandler,limit=100) #) #,23000,"",1 )
