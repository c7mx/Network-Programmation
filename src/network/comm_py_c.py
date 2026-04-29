import socket
import select
import network.json_utils as j

C_HOST = "127.0.0.1"
C_PORT = 1040

PY_PORT = 1030

def connect_sock_send():
    python_c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    python_c_socket.connect((C_HOST, C_PORT))
    return python_c_socket

def connect_sock_recv():
    python_c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    python_c_socket.bind((C_HOST, PY_PORT))
    return python_c_socket

def send_data(sock, uid, hp, x, y, type=None):
    data = j.create_json(uid, hp, x, y, type)
    sock.send(data.encode())

def send_Property(sock , Req, uid, etat, Post_local):
    data = j.create_jsonbis(Req, uid, etat, Post_local)
    sock.send(data.encode())

def ask_property(sock, Ask, uid, Post_local):
    etat = None
    data = j.create_jsonbisbis(Ask, uid, etat, Post_local)
    sock.send(data.encode())


def receive_data(sock):
    ready, _, _ = select.select([sock], [], [], 0)  # 0 = non bloquant

    if ready:
        response = sock.recv(1024)
        msg = response.decode()
        return msg
    
    return None
