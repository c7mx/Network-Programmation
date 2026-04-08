    import socket
    import json_utils as j

    HOST = "127.0.0.1"
    C_PORT = 1040
    PY_PORT = 1030

    def connect_sock_send():
        python_c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        python_c_socket.connect((HOST, C_PORT))
        print(f"Connected at {HOST}:{C_PORT}")
        return python_c_socket

    def connect_sock_recv():
        python_c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        python_c_socket.bind((HOST, PY_PORT))
        print(f"Listen at {HOST}:{PY_PORT}")
        return python_c_socket

    def send_data(data, sock):
        sock.send(data.encode())
        sock.close()

    def receive_data(sock):
        response = sock.recv(1024)
        print("Réponse du serveur :", response.decode())
        return response.decode()
        sock.close()

    sock = connect_sock_send()

    data = j.create_json(0, 100, 10, 10)
    send_data(data, sock)


    sock = connect_sock_recv()
    msg = receive_data(sock)
    data = j.load_json(msg)
    print(data)
    print(data["uid"])

