import socket
import struct

PORT_C = 1040
PORT_PYTHON = 1030

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", PORT_PYTHON))

# envoyer "PING" + entier 42
msg = "PING".encode()
num = 42
data = struct.pack("!I", num) + msg  # !I = entier 4 octets big endian
sock.sendto(data, ("127.0.0.1", PORT_C))

# recevoir réponse
resp, addr = sock.recvfrom(1024)
resp_num = struct.unpack("!I", resp[:4])[0]
resp_msg = resp[4:].decode()

print(f"Reçu de C: '{resp_msg}' avec entier: {resp_num}")
