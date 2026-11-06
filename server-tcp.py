import socket

class Usuario:
    def __init__(self, nome, conn):
        self.nome = nome
        self.conn = conn

class ListaDeConexoes:
    def __init__(self):
        self.usuarios = {}
    
    def adicionar(self, usuario):
        if usuario.nome in self.usuarios:
            raise Exception("usuario já cadastrado")
        self.usuarios[usuario.nome] = usuario

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 5000))
s.listen()

def obter_nome(conn):
    conn.sendall("Qual é o seu nome? ".encode())
    data = conn.recv(1024)
    return data.decode().strip()

conexoes = ListaDeConexoes()

conn, addr = s.accept()
nome = obter_nome(conn)
usuario = Usuario(nome, conn)
conexoes.adicionar(usuario)

print("Conectado:", addr, nome)

while data := conn.recv(1024):
    print(data.decode())
conn.close()