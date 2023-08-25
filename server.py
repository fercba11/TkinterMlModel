import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = 'localhost'
puerto = 9999
serversocket.bind((host, puerto))

print(f"Servidor UDP escuchando en {host}:{puerto}")

try:
    while True:
        print("servidor hace prueba while correcta")
        mensaje, address = serversocket.recvfrom(1024)
        print(f"Recibido desde: {address[0]} - Mensaje: {mensaje.decode('ascii')}")

        # Guardar el mensaje recibido en un archivo .txt
        with open('datos_socket.txt', 'a') as archivo:
            archivo.write(f"Recibido desde: {address[0]} - Mensaje: {mensaje.decode('ascii')}\n")
            
except KeyboardInterrupt:
    print("Servidor cerrado")
    serversocket.close()