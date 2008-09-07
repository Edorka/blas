import sys
from core import Server
from core import TCPHandler
from core import Log
import core

VERSION = "0.1"
OPTION = {}

class TelnetServer(Server):
	def __init__(self,args=""):
		Server.__init__(self)
		self.id = "PyTelnet v."+VERSION
		self.config["configfile"] = "telnet.log"
		self.config["port"] = 23000 #valores por defecto
		self.config["verbosity"] = 1
		self.ip = "" 
		self.configure(args)	
#	def close(self):
#		self.log("TelnetServer ending.")
 #		Server.close(self)

class TelnetHandler(TCPHandler):
 	def __init__(self,socket,parent=None,verbosity=1,logs={}):
		TCPHandler.__init__(self,socket)
		self.log = parent.log
		self.parent = parent
		self.next = 'login'
		self.secuence  = ['login','check_login','command','end']
		self.log("connected")

	def step_login(self):
		"""trying to log in"""
		self.user = None
		self.send("login:")
		login = self.receive( "(?P<login>(([a-zA-Z0-9])*))")
		self.send("password:")
		password = self.receive( "(?P<passwd>(([a-zA-Z0-9])*))")
		self.login = (login,password)
		self.next_step('check_login')

	def step_check_login(self):
		"""checking user identity"""
		user_input = self.login[0]
		pass_input = self.login[1]	
		if user_input:
			user = user_input['login']
		if pass_input:
			passwd = pass_input['passwd']
		self.user = (user,passwd)
		self.log(str(self.user),3)
		self.next_step('command')

	def step_greeting(self):
		"""sending host info"""
		self.send("PyTelnet Server")
		self.next_step()

	def step_command(self):
		"""submits command"""
		self.send(" >:")
		command = self.receive( r"(?P<command>(.*))(\r)")
		if command['command'] == "exit": 
			#self.socket.close()
			self.next_step('end')
		else: self.send(" TODO:RUN SHELL \n")	

if __name__ == '__main__':
	print "init."
	server = TelnetServer(sys.argv)
	server.mainloop(TelnetHandler,limit=100) #) #,23000,"",1 )
