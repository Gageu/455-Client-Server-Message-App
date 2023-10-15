import socket
import threading

# Global list to store all connected clients
clients = []
clients_lock = threading.Lock()

def client_thread(client_socket, addr):
    try:
        while True:
            # Receiving the header first (5 bytes long)
            header = client_socket.recv(5).decode('utf-8')
            
            # Receiving the data size
            data_size = int(client_socket.recv(10).decode('utf-8'))
            
            # Receiving the data
            data = client_socket.recv(data_size)
            
            if not data:
                break

            # Print to the console
            if header == "EXIT_":
                print(f"Client {addr} has disconnected.")
            elif header == "TEXT_":
                print(f"Received text message from {addr} and relaying to other clients.")
            elif header == "FILE_":
                print(f"Received file from {addr} and relaying to other clients.")

            # Relay to all other clients
            with clients_lock:
                for client in clients:
                    if client != client_socket:
                        try:
                            client.sendall(header.encode('utf-8'))  # Send header first
                            client.sendall(str(data_size).zfill(10).encode('utf-8'))  # Send size next
                            client.sendall(data)
                        except:
                            pass
    except:
        pass
    finally:
        # Remove the client from the clients list and close the connection
        with clients_lock:
            clients.remove(client_socket)
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen(5)
    print("Server listening on port 12345...")

    while True:
        client_socket, addr = server.accept()
        with clients_lock:
            clients.append(client_socket)
        print(f"Accepted connection from {addr}")
        threading.Thread(target=client_thread, args=(client_socket, addr)).start()

if __name__ == "__main__":
    start_server()
