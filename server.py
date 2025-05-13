import threading
import time
import socket
import json
import uuid  # Add this import for generating unique IDs

class Server:
    def __init__(self, port):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.clients = {}  # Change to a dictionary to store client sockets with their IDs
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

            data = client_socket.recv(1024)
            if not data:
                client_socket.close()
                continue

            try:
                client_info = json.loads(data.decode())
                client_name = client_info['client_name']
            except (json.JSONDecodeError, KeyError):
                client_socket.close()
                continue

            with self.lock:
                self.clients[client_name] = client_socket

            threading.Thread(target=self.handle_client, args=(client_socket, client_name)).start()

    def stop(self):
        self.running = False

        with self.lock:
            for client in self.clients.values():
                client.close()
            self.clients.clear()

        self.server_socket.close()
        print("Servidor parado")

    def handle_client(self, client_socket, client_name):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                print(f"{time.strftime('%H:%M:%S', time.localtime())} - {client_name} to {message['recipient']}: {message['message']}")
                self.broadcast(message, sender_socket=client_socket, recipient=message.get('recipient'))
            except (json.JSONDecodeError, ConnectionResetError):
                break

        with self.lock:
            del self.clients[client_id]
        client_socket.close()
        print(f"Conexão fechada para o cliente {client_id}")

    def broadcast(self, message, sender_socket=None, recipient=None):
        with self.lock:
            message['sender'] = list(self.clients.keys())[list(self.clients.values()).index(sender_socket)]

            if recipient and recipient in self.clients:
                try:
                    self.clients[recipient].send(json.dumps(message).encode())
                except (BrokenPipeError, ConnectionResetError):
                    pass
            else:
                for client_id, client in self.clients.items():
                    if client != sender_socket:
                        try:
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