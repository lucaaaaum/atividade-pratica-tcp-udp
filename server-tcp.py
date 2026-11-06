import socket
import threading


class Usuario:
    def __init__(self, nome, conn, addr):
        self.nome = nome
        self.conn = conn
        self.addr = addr


class ListaDeConexoes:
    def __init__(self):
        self.usuarios = {}
        self.lock = threading.Lock()

    def adicionar(self, usuario):
        with self.lock:
            if usuario.nome in self.usuarios:
                return False
            self.usuarios[usuario.nome] = usuario
            return True

    def remover(self, nome):
        with self.lock:
            self.usuarios.pop(nome, None)

    def nomes(self):
        with self.lock:
            return list(self.usuarios)


conexoes = ListaDeConexoes()


def obter_nome(conn):
    conn.sendall("Qual é o seu nome? ".encode())
    data = conn.recv(1024)
    if not data:
        return None  # cliente desconectou antes de responder
    return data.decode().strip()


def atender(conn, addr):
    usuario = None
    try:
        while usuario is None:
            nome = obter_nome(conn)
            if nome is None:
                return
            if not nome:
                continue
            candidato = Usuario(nome, conn, addr)
            if conexoes.adicionar(candidato):
                usuario = candidato
            else:
                conn.sendall("Nome já em uso.\n".encode())

        conn.sendall(f"Bem-vindo, {usuario.nome}!\n".encode())
        print("Conectado:", addr, usuario.nome)

        while data := conn.recv(1024):
            print(f"[{usuario.nome}] {data.decode().strip()}")
    except OSError:
        pass  # conexão resetada ou quebrada pelo cliente
    finally:
        if usuario:
            conexoes.remover(usuario.nome)
            print("Desconectado:", addr, usuario.nome)
        conn.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5000))
s.listen()
print("Servidor TCP escutando na porta 5000")

while True:
    conn, addr = s.accept()
    threading.Thread(target=atender, args=(conn, addr), daemon=True).start()