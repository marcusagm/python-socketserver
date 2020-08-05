import time
import queue
import errno
import socket
import select
import threading

class ServerTcp:

    def __init__(self, address = '127.0.0.1', port = 3000, bufferSize = 8192, timeout = 300):
        self.address = address
        self.port = int(port)
        self.bufferSize = bufferSize
        self.timeout = timeout
        self.clients = []
        self.lastPings = {}
        self.receivedPackets = queue.Queue()
        self.lastTimeoutCheck = time.time()
        self.timeoutTimer = None
        self.context = None
        self.listener = None
        self.isListening = True
        self.isShutDown = threading.Event()

    def start(self):
        try:
            # self.context = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.context = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.context.bind((self.address, self.port))
            self.context.listen(5)
            
            # self.context.setblocking(False)
            # self.context.settimeout(self.timeout)
            self.log('Servidor iniciado!')

            self.initTimeoutChecker()
            
            self.isShutDown.clear()
            while self.isListening == True:
                selecteds = select.select([self.context], [], [])
                if self.context in selecteds[0]:
                    self.processRequest()
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as error:
            print(error)
        finally:
            self.stop()
            self.isShutDown.set()

    def shutdown(self):
        self.stop()
        self.isShutDown.wait()

    def stop(self):
        self.isListening = False
        self.context.close()

    def processRequest(self):
        listener = threading.Thread(target=self.receiveData)
        listener.start()

    def receiveData(self):
        # data, client = self.context.recvfrom(self.bufferSize)
        # if data != '':
        #     self.registerClient(client)
        #     self.parseData(data, client)
        conn, addr = self.context.accept()
        while True:
            msg = conn.recv(1024)
            if not msg: break
            if msg:
                self.registerClient(conn, addr)
                self.parseData(msg, conn)

    def parseData(self, data, client):
        response = data.decode('utf-8')
        if response != '':
            self.log('Data:', response)

            if response == '::ping':
                self.registerPing(client)
            else:
                self.receivedPackets.put((data,client))
                self.sendToAll()

    def sendToAll(self):
        while not self.receivedPackets.empty():
            data, client = self.receivedPackets.get()
            for clientAddr in self.clients:
                if clientAddr != client:
                    clientAddr.send( data )

    def registerClient(self, client, addr):
        if client not in self.clients:
            self.clients.append(client)
            self.lastPings[str(client)] = time.time()
            self.log('Endereço:', str(addr), '- Conectou.')

    def removeClient(self, client):
        if client in self.clients:
            self.clients.remove(client)
            del self.lastPings[str(client)]
            self.log('Endereço:', str(client), '- Conexão finalizada.')

    def initTimeoutChecker(self):
        if self.timeoutTimer == None:
            self.timeoutTimer = threading.Timer(self.timeout, self.checkForTimeouts)
            self.timeoutTimer.start()

    def checkForTimeouts(self):
        now = time.time()
        self.timeoutTimer = None
        if now - self.lastTimeoutCheck > self.timeout:
            self.lastTimeoutCheck = time.time()

            for client, pingTime in list(self.lastPings.items()):
                if now - pingTime > self.timeout:
                    self.log('Endereço:', client, '- Timeout')
                    self.removeClient(eval(client))
        self.initTimeoutChecker()

    def registerPing(self, client):
        self.context.sendto('::pong'.encode('utf-8'), client)
        self.lastPings[str(client)] = time.time()

    def now(self):
        return time.ctime(time.time())

    def log(self, *message):
        print( self.now(), '-', ' '.join(message))
        