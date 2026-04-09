import network.comm_py_c as NetPy
import network.json_utils as j

full_data = []
while True:
    sock = NetPy.connect_sock_recv()
    msg = NetPy.receive_data(sock)

    if msg:
        data = j.load_json(msg)
        full_data.append(data)
        print(full_data)
