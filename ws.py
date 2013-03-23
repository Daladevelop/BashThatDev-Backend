from twisted.internet import protocol, reactor
from twisted.web.server import Site
from twisted.web.static import File
from twisted.python import log
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

class BroadcastProtocol(WebSocketServerProtocol):
	def onOpen(self):
		self.factory.register(self)
	def onMessage(self,msg,binary):
		if not binary:
			self.factory.broadcast("'%s' from %s" % (msg, self.peerstr))
			
	def connectionLost(self,reason):
		WebSocketServerProtocol.connectionLost(self,reason)
		self.factory.unregister(self)


class BroadcastFactory(WebSocketServerFactory):
	def __init__(self, url, debug = True):
		WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debug)
		self.clients = []
	
		self.tc = 0

		self.tick()

	def tick(self):
		self.tc += 1
		self.broadcast("TICK")
		reactor.callLater(1, self.tick)
	def register(self, client):
		print "register"
		if not client in self.clients:
			print "registered: " + client.peerstr
		else:
			print "client client already..."

	def unregister(self, client):
		if client in self.clients:
			print "unregister:" + client.peerstr
			self.clients.remove(client)
		else:
			"print trying to remove client not in clients..."

	def broadcast(self,msg):
		print "broadcast '%s'" % msg
		for c in self.clients:
			c.sendMessage(msg)

	
if __name__ == "__main__":
	ServerFactory = BroadcastFactory
	factory = ServerFactory("ws://localhost:1337", debug = True)
	factory.protocol = BroadcastProtocol
	listenWS(factory)
	reactor.run()
