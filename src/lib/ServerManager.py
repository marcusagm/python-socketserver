import time
import queue
import socket
import threading
import socketserver 

class ServerHandler:
    
    def __init__(self):
        self.clients = []
        self.last_pings = {}
        self.timer = time.time()
        self.receivedPackets = queue.Queue()
        self.socket = None

    def now(self):
        return time.ctime(time.time())

    def log(self, *message):
        print( self.now(), '-', ' '.join(message))

    def registerClient(self, client):
        if client not in self.clients:
            self.clients.append(client)
            self.log(str(client), 'Conexão estabelecida.')

    def removeClient(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.log(str(client), 'Conexão finalizada.')

    def parseData(self, data):
        return data

    def addToQueue(self, client, socket, data):
        self.timer = time.time()
        self.socket = socket
        self.registerClient(client)
        self.receivedPackets.put((data, client))
        self.sendToAll()

    def sendToAll(self):
        if not self.receivedPackets.empty():
            data, addr = self.receivedPackets.get()
            response = self.parseData(data)

            for clientAddr in self.clients:
                if clientAddr != addr:
                    self.socket.sendto( response, clientAddr)

class ServerListener(socketserver.BaseRequestHandler):

    serverHandler = ServerHandler()

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        client = self.client_address
        self.serverHandler.addToQueue(client, socket, data)

class ServerThreaded(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

class ServerManager():
    
    def __init__(self, address = '127.0.0.1', port = 3000, timeout = 5):
        self.address = address
        self.port = int(port)
        self.timeout = timeout
        self.server = None
        self.serverThread = None

    def start(self):
        print('Iniciando...')
        self.server = ServerThreaded((self.address, self.port), ServerListener)
        ip, port = self.server.server_address

        self.serverThread = threading.Thread(target=self.server.serve_forever)
        self.serverThread.daemon = True
        self.serverThread.start()

        print("Server loop running in thread:", self.serverThread.name)
        print('IP:', str(ip), 'Port:', str(port))

        while self.serverThread.is_alive():
            cmd = input('exit to close:')
            if cmd == 'exit':
                self.stop()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def now(self):
        return time.ctime(time.time())

    def log(self, *message):
        print( self.now(), '-', ' '.join(message))