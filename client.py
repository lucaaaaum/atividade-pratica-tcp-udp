import os, socket, sys, threading

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000

def receber(s):
    while data := s.recv(1024):
        print(data.decode(), end="", flush=True)
    print("\nServidor encerrou a conexão.")
    os._exit(0)

s = socket.create_connection((HOST, PORT))
print("Local:", s.getsockname(), "-> Servidor:", s.getpeername())
threading.Thread(target=receber, args=(s,), daemon=True).start()

for linha in sys.stdin:
    s.sendall(linha.encode())
s.close()