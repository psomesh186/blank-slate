import socket
import json
import threading


class Client:
    '''Enables players to join a host's lobby'''
    def __init__(self, client_name, manager):
        self.client_name = client_name
        self.manager = manager
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.hosts = {}
        self.host = {}
        self.STOP_FIND = False

    def get_hosts(self):
        broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcastSocket.settimeout(3)
        broadcastSocket.bind(('', 8888))
        while True:
            if self.STOP_FIND:
                break
            try:
                data = broadcastSocket.recv(1024)
                msg = json.loads(data.decode())
                if msg["host"] in self.hosts:
                    continue
                self.hosts[msg["host"]] = msg
                self.manager.get_screen("JoinGame").add_lobby(msg["name"], msg["host"])
            except socket.timeout:
                pass
        broadcastSocket.close()

    def listen_to_host(self):
        while True:
            try:
                data = self.s.recv(1024)
                if not data:
                    break
                reply = json.loads(data.decode())
                if reply["Signal"] == "Player info":
                    self.manager.get_screen("JoinGame").add_players(reply["Player info"], reply["Player ID"])
                elif reply["Signal"] == "Card":
                    self.manager.get_screen("PlayGame").set_card(reply["Card Index"])
                elif reply["Signal"] == "Update Submission":
                    self.manager.get_screen("PlayGame").update_submission(reply["Player"])
                elif reply["Signal"] == "Results":
                    self.manager.get_screen("PlayGame").show_results(reply["Result"])
            except socket.error:
                break

    def join_lobby(self, host):
        self.STOP_FIND = True
        self.host = self.hosts[host]
        self.s.connect((self.host["host"], self.host["port"]))
        msg = str.encode(json.dumps({"Signal": "name", "name": self.client_name}))
        self.s.send(msg)
        threading.Thread(target=self.listen_to_host).start()

    def send_word(self, word):
        msg = str.encode(json.dumps({"Signal": "Submission", "Word": word}))
        self.s.send(msg)