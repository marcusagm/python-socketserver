import sys
from lib.Server import Server
# from lib.ServerManager import ServerManager

gameServer = Server('127.0.0.1', 3001)
gameServer.start()

# gameServer = ServerManager('127.0.0.1', 3001)
# gameServer.start()