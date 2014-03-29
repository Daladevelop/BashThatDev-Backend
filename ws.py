#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:et

from twisted.internet import protocol, reactor
from twisted.web.server import Site
from twisted.web.static import File
from twisted.python import log
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS

from gameserver import *
import json
import base64
import log, logging

gameserver = GameEngine()
PORT = 1338
TICKTIME = .02


#data = {'msg': 'hello'}
#pix = {}
#pix['dood'] = ("data:image/png;base64,%s" % base64.b64encode(open('sprite.png').read()))
#data['msg'] = 'hello'
#data['pix'] = pix

sprites = []
sound_effects = []
music_tracks = []

sprites.append({ 'name': 'player',
                 'data': 'data:image/png;base64,%s' %
                 base64.b64encode(open('sprite.png').read()) })
sound_effects.append({ 'name': 'jump',
                       'url': 'audio/jump.mp3'})
sound_effects.append({ 'name': 'moose_scream',
                       'url': 'audio/oops.mp3'})

data = {}
data['sprites'] = sprites
data['music_tracks'] = []
data['sound_effects'] = sound_effects

hellomsg = json.dumps(data)

logger = logging.getLogger(__name__)

class BroadcastProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.factory.register(self)

    def onMessage(self,msg,binary):
        #if not binary:
        #   self.factory.broadcast("%s from %s" % (msg, self.peerstr))
        json_data = None

        try:
            json_data = json.loads(msg)
        except ValueError:
            pass

        if json_data is not None:
            gameserver.handle(json_data, str(self.peer))

    def connectionLost(self,reason):
        logger.info("Connection lost %s" % reason)
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

class BroadcastFactory(WebSocketServerFactory):
    
    def __init__(self, url, debug = True):
        WebSocketServerFactory.__init__( self, url, debug = debug,
                debugCodePaths = debug)
        self.clients = []
    
        self.tc = 0

        self.tick()

    def tick(self):
        self.tc += 1
#       self.broadcast("TICK")
        gameserver.update()
        self.broadcast(json.dumps(gameserver.get_state()))
        reactor.callLater(TICKTIME, self.tick)

    def register(self, client):
        logger.debug("Handling client registration")
        if not client in self.clients:
            logger.debug("Registering: %s" % client.peer)
            self.clients.append(client)
            gameserver.add_client(str(client.peer))
            client.sendMessage(hellomsg)
        else:
            logger.debug("Client already registered")

    def unregister(self, client):
        logger.debug("Handling client unregistration")
        if client in self.clients:
            logger.debug("Unregistering: %s" % str(client.peer))
            gameserver.remove_client(str(client.peer))
            self.clients.remove(client)
        else:
            logger.debug("Cannot unregister client, client not registered: %s" % client.peer)

    def broadcast(self, msg):
        #logger.debug('Broadcasting "%s" to %d clients' % (msg, len(self.clients)))
        for c in self.clients:
            c.sendMessage(msg)

if __name__ == "__main__":
    log.initialize_logging(debug=True)
    logger.info("Server is starting on port %d", PORT)

    ServerFactory = BroadcastFactory
    factory = ServerFactory("ws://localhost:{}".format(PORT), debug=True)
    factory.protocol = BroadcastProtocol
    listenWS(factory)

    reactor.run()
