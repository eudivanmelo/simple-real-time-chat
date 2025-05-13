import socket
import json
import threading

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print(f"Conectado ao servidor {self.host}:{self.port}")
        self.running = True
        self.listen_thread = threading.Thread(target=self.listen_for_messages)
        self.listen_thread.start()

    def listen_for_messages(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = json.loads(data.decode())
                print(f"{message['sender']}: {message['message']}")
            except (json.JSONDecodeError, ConnectionResetError):
                break

        self.client_socket.close()
        print("Conexão fechada")

    def send_message(self, message):
        try:
            data = json.dumps(message).encode()
            self.client_socket.sendall(data)
        except (BrokenPipeError, ConnectionResetError):
            print("Erro ao enviar mensagem. O servidor pode estar desconectado.")

    def close(self):
        self.client_socket.close()
        print("Conexão fechada")

if __name__ == "__main__":
    client_name = input("Digite seu nome: ")
    client = Client(host='localhost', port=8080)
    client.send_message({"message": f"{client_name} entrou no chat", "sender": "Sistema"})
    print("Digite uma mensagem para enviar (ou 'sair' para sair)")

    try:
        while True:
            message = input()
            if message.lower() == 'sair':
                break
            client.send_message({"message": message, "sender": client_name})
    except KeyboardInterrupt:
        print("Interrompendo o cliente...")
    finally:
        client.close()