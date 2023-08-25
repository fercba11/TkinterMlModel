import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = 'localhost'
puerto = 9999
mensaje = b'Hola desde el cliente UDP'
clientsocket.sendto(mensaje, (host, puerto))
clientsocket.close()
print("Mensaje enviado al servidor")