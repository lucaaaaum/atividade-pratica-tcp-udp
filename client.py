import os, socket, sys, threading

UDP_PORT = 5001
BROADCAST = "255.255.255.255"

def descobrir(timeout=2):
    u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    u.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    u.settimeout(timeout)
    u.sendto(b"DISCOVER", (BROADCAST, UDP_PORT))
 
    servidores = []
    try:
        while True:
            data, (ip, _) = u.recvfrom(1024)
            partes = data.decode().split()
            if len(partes) == 2 and partes[0] == "CHATBOT":
                servidor = (ip, int(partes[1]))
                if servidor not in servidores:
                    servidores.append(servidor)
    except socket.timeout:
        pass
    u.close()
    return servidores

def escolher_servidor():
    print("Procurando servidores na rede...")
    servidores = descobrir()
    if not servidores:
        print("Nenhum servidor encontrado.")
        sys.exit(1)
    if len(servidores) == 1:
        return servidores[0]
    for i, (ip, porta) in enumerate(servidores, 1):
        print(f"{i}) {ip}:{porta}")
    return servidores[int(input("Escolha: ")) - 1]


def receber(tcp):
    while data := tcp.recv(1024):
        print(data.decode(), end="", flush=True)
    print("\nServidor encerrou a conexão.")
    os._exit(0)

host, tcp_port = escolher_servidor()
try:
    tcp = socket.create_connection((host, tcp_port), timeout=5)
    tcp.settimeout(None)
except ConnectionRefusedError:
    print(f"O servidor {host}:{tcp_port} recusou a conexão. O servidor TCP está rodando?")
    sys.exit(1)
except OSError as e:
    print(f"Não foi possível conectar a {host}:{tcp_port}: {e}")
    sys.exit(1)
print("Local:", tcp.getsockname(), "-> Servidor:", tcp.getpeername())
threading.Thread(target=receber, args=(tcp,), daemon=True).start()

for linha in sys.stdin:
    tcp.sendall(linha.encode())
tcp.close()