from socket import socket, SOCK_DGRAM, SOCK_STREAM, AF_INET, SO_REUSEADDR, SOL_SOCKET, timeout
from threading import Thread
 
isConnected = False

def receiveData(context):
    while isConnected:
        try:
            data = context.recvfrom(2048)
            data = data[0]
            print( '->', data.decode('utf-8'))
        except timeout:
            continue
        except:
            pass

# Cria host e port number
host = '127.0.0.1'
port = 3001

# O servidor seré um par endereço e port
server = (host, port)

# Criamos o socket
context = socket(AF_INET, SOCK_DGRAM)
# context = socket(AF_INET, SOCK_STREAM)
context.connect(server)
isConnected = True
try:

    listener = Thread(target=receiveData,args=(context,))
    listener.start()

    print('Bem vindo!')
    context.send(''.encode('utf-8'))

    # Vamos mandar menssagem enquanto a menssagem for diferente de sair (s)
    msg = input()
    while msg != 's':
        # Mandamos a menssagem atravÃ©s da conexÃ£o
        context.send(msg.encode('utf-8')) 
        # Podemos mandar mais menssagens
        msg = input()

    # Fechamos a conexÃ£o
    context.close()
except (KeyboardInterrupt, SystemExit):
    pass
finally:
    isConnected = False
    context.close()