import socket
import json
import threading

class Client:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        self.client_socket.sendall(json.dumps({"client_name": name}).encode())

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

    def send_message(self, message, recipient="all"):
        try:
            data = json.dumps({"message": message, "recipient": recipient}).encode()
            self.client_socket.sendall(data)
        except (BrokenPipeError, ConnectionResetError):
            print("Erro ao enviar mensagem. O servidor pode estar desconectado.")

    def close(self):
        self.client_socket.close()
        print("Conexão fechada")

if __name__ == "__main__":
    client_name = input("Digite seu nome: ")

    client = Client(host='localhost', port=8080, name=client_name)
    client.send_message(f"{client_name} entrou no chat")

    print("Digite uma mensagem para enviar (ou 'sair' para sair)")

    try:
        while True:
            message = input("Digite sua mensagem: ")
            if message.lower() == 'sair':
                break

            if message.startswith("/"):
                parts = message.split(" ", 1)
                recipient = parts[0][1:]
                message = parts[1] if len(parts) > 1 else ""
            else:
                recipient = "all"

            client.send_message(message, recipient)
    except KeyboardInterrupt:
        print("Interrompendo o cliente...")
    finally:
        client.close()