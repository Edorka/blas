import sys
from core import Server
from core import Handler
from core import Log
import core

VERSION = "0.1"
OPTION = {}

class TelnetServer(Server):
	def __init__(self,args=""):
		self.id = "PyTelnet v."+VERSION
		self.ip = "" #valores por defecto
		self.port = 23000 #valores por defecto
		self.loglevel = 1
		Server.__init__(self,args)
		

class TelnetHandler(Handler):
 	def __init__(self,socket,parent=None,verbosity=1,logs={}):
		Handler.__init__(self,socket)
		self.log = logs
		self.parent = parent
		self.secuence  = ['login','check_login','command','end']
		self.report("connected")

	def step_login(self):
		"""trying to log in"""
		self.user = None
		self.send("login:")
		login = self.receive( "(?P<login>(([a-zA-Z0-9])*))")
		self.send("password:")
		password = self.receive( "(?P<passwd>(([a-zA-Z0-9])*))")
		self.login = (login,password)
		self.next_step()

	def step_check_login(self):
		"""checking user identity"""
		user_input = self.login[0]
		pass_input = self.login[1]	
		if user_input:
			user = user_input['login']
		if pass_input:
			passwd = pass_input['passwd']
		self.user = (user,passwd)
		self.report(str(self.user),3)
		self.next_step()

	def step_greeting(self):
		"""sending host info"""
		self.send("PyTelnet Server")
		self.next_step()

	def step_command(self):
		"""submits command"""
		self.send(" >:")
		command = self.receive( r"(?P<command>(.*))(\r)")
		if command['command'] == "exit": self.next_step()
		else: self.send(" TODO:RUN SHELL \n")	

	def step_end(self):
		"""ends session"""

if __name__ == '__main__':
	LOGLEVEL = 1
	print "init."
	server = TelnetServer(sys.argv)
	server.mainloop(TelnetHandler,limit=100) #) #,23000,"",1 )
