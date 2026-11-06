import socket
import threading
from datetime import datetime


class MensagemDoChatBot:
    def __init__(self, conteudo, opcoes=None):
        self.conteudo = conteudo  # texto fixo ou função(usuario) -> texto
        self.opcoes = opcoes or []

    def adicionar_opcao(self, opcao):
        self.opcoes.append(opcao)

    def formatar(self, usuario):
        if callable(self.conteudo):
            texto = self.conteudo(usuario)
        else:
            texto = self.conteudo
        texto += "\n"
        if self.opcoes:
            texto += "opções: " + ", ".join(self.opcoes) + "\n"
        return texto


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


class ChatBot:
    def __init__(self, conexoes):
        self.conexoes = conexoes
        self.mensagens = {
            "help": MensagemDoChatBot(self.ajuda),
            "ping": MensagemDoChatBot("pong!", ["ping", "help"]),
            "usuarios": MensagemDoChatBot(self.listar_usuarios, ["help"]),
            "hora": MensagemDoChatBot(self.hora, ["help"]),
            "eu": MensagemDoChatBot(self.quem_sou_eu, ["usuarios", "help"]),
            "sair": MensagemDoChatBot("até mais!"),
        }

    def ajuda(self, usuario):
        return "olá, eu sou um chatbot em TCP! os comandos são: " + ", ".join(self.mensagens)

    def listar_usuarios(self, usuario):
        return "conectados: " + ", ".join(self.conexoes.nomes())

    def hora(self, usuario):
        return "agora são " + datetime.now().strftime("%H:%M:%S") + " (UTC)"

    def quem_sou_eu(self, usuario):
        ip, porta = usuario.addr
        return f"você é {usuario.nome}, conectado de {ip}:{porta}"

    def responder(self, comando, usuario):
        msg = self.mensagens.get(comando)
        if msg is None:
            return "comando desconhecido. digite help.\n"
        return msg.formatar(usuario)


conexoes = ListaDeConexoes()
chatbot = ChatBot(conexoes)


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

        conn.sendall(f"Bem-vindo, {usuario.nome}! Digite help para ver os comandos.\n".encode())
        print("Conectado:", addr, usuario.nome)

        while data := conn.recv(1024):
            comando = data.decode().strip().lower()
            if not comando:
                continue
            print(f"[{usuario.nome}] {comando}")
            conn.sendall(chatbot.responder(comando, usuario).encode())
            if comando == "sair":
                break
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