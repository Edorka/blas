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
		self.loglevel = 1
		Server.__init__(self)
		self.family = core.UDP
		self.config["verbosity"] = 1
		self.config["port"] = 5060 #valores por defecto
		self.config["configfile"] = "sip.cfg" 
		self.password = {}
		self.password['user1']='password'
		self.password['user2']='password'
		self.password['user3']='password'
		self.configure(args)

	def config_domain(self,value):
		"""d:<domain name> sets domain name."""
		if value:
			self.config["domain"] = value
		else:
			print self.usage()



class SIPHandler(UDPHandler):
 	def __init__(self,data,origin,parent=None,verbosity=1,logs={}):
		UDPHandler.__init__(self,data,origin)
		self.parent = parent
		self.log=parent.log
		self.secuence  = ['request','headers','run',"run_register","run_invite","run_subscribe",'end']
		self.next = "request"
		self.log("connected")

	def step_request(self):
		"""receiving command"""
		self.log("connected:"+str(self.incoming))
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
			self.next_step('headers')

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
			self.next_step('run')
		else:
			self.request["params"][param["name"]]= param["value"]

	def step_run(self):
		"""state switch by command"""
		command = self.request["command"]
		params = self.request["params"]
		self.log("parametros recibidos para metodo "+command+":\n"+ self.str_params(params),4)
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

	def str_params(self,params=None):
		if not params: params=self.request["params"]
		s = ""
		for param,value in params.items():
			s+= param+": "+value+"\n"
		return s

	def step_run_register(self):
		"""efectuando el registo del usuario"""
		#print self.request
		params = self.request["params"]
		domain = self.parent.config["domain"]
		if self.digest("REGISTER") == True:
			msg = "SIP/2.0 200 OK\n"
			#self.log("cadena de autorizacion:"+str_param(params["Authorization"]),4)
		else:
			self.log("fallo en la autentificacion, solicitando.",0)
			msg = "SIP/2.0 401 Unathorized\n"
			nonce = md5.new(time.ctime()).digest().encode('hex')
			params["nonce"] = nonce
			msg += 'WWW-Authenticate: Digest realm="'+domain+'", nonce="'+nonce+'", qop="auth"\n'
		#self.log(str(params),4)
		#print self.digest()
		params["To"]= params["From"]
		fields = ['CSeq','Via','From','Call-ID','To','Contact','Server','Content-Length']
		msg += self.compose_headers(params,fields)
		self.log("respondiendo:\n"+msg,4)
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



if __name__ == '__main__':
	LOGLEVEL = 1
	print "init."
	server = SIPServer(sys.argv)
	server.mainloop(SIPHandler,limit=100) #) #,23000,"",1 )
