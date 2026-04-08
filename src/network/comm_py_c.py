import socket
import select
import json_utils as j

C_HOST = "127.0.0.1"
C_PORT = 1040

PY_PORT = 1030

def connect_sock_send():
    python_c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    python_c_socket.connect((C_HOST, C_PORT))
    print(f"Connected at {C_HOST}:{C_PORT}")
    return python_c_socket

def connect_sock_recv():
    python_c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    python_c_socket.bind((C_HOST, PY_PORT))
    print(f"Listen at {C_HOST}:{PY_PORT}")
    return python_c_socket

def send_data(data, sock):
    sock.send(data.encode())
    sock.close()

def receive_data(sock):
    ready, _, _ = select.select([sock], [], [], 0)  # 0 = non bloquant

    if ready:
        response = sock.recv(1024)
        msg = response.decode()
        print("Réponse du serveur :", msg)
        return msg
    
    return None


# sock = connect_sock_send()

# data = j.create_json(0, 100, 10, 10)
# send_data(data, sock)

sock = connect_sock_recv()

while True:
    msg = receive_data(sock)

    if msg:
        data = j.load_json(msg)
        print(data)
        print(data["uid"])


