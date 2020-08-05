import sys
from lib.ServerTcp import ServerTcp
# from lib.ServerManager import ServerManager

gameServer = ServerTcp('127.0.0.1', 3001)
gameServer.start()

# gameServer = ServerManager('127.0.0.1', 3001)
# gameServer.start()