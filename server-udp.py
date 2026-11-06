import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 5001))

while True:
    data, addr = s.recvfrom(1024)
    print(addr, data.decode())