import threading
import time
import socket
import json

class Server:
    def __init__(self, port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.clients = []
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        print(f"Servidor iniciado na porta {self.port}")
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(5)
        self.running = True
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        print("Aguardando conexões...")
        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexão recebido de {addr}")
            with self.lock:
                self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def stop(self):
        self.running = False

        with self.lock:
            for client in self.clients:
                client.close()
            self.clients.clear()

        self.server_socket.close()
        print("Servidor parado")

    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                print(f"{time.strftime("%H:%M:%S", time.localtime())} - {message['sender']}: {message['message']}")  # Log only the message content
                self.broadcast(message, sender_socket=client_socket)  # Pass the sender socket
            except (json.JSONDecodeError, ConnectionResetError):
                break

        with self.lock:
            self.clients.remove(client_socket)
        client_socket.close()
        print("Conexão fechada")

    def broadcast(self, message, sender_socket=None):
        with self.lock:
            for client in self.clients:
                try:
                    if client != sender_socket:
                        client.send(json.dumps(message).encode())
                except (BrokenPipeError, ConnectionResetError):
                    pass

if __name__ == "__main__":
    server = Server(port=8080)
    try:
        server.start()
        while True:
            cmd = input("Digite 'sair' para parar o servidor: ")
            if cmd.lower() == 'sair':
                server.stop()
                break
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Interrompendo o servidor...")
        server.stop()