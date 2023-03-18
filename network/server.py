import socket
import threading
import json
import collections
import time

class Server:
    '''Creates the server to host the game and send control signals'''
    def __init__(self, host_name, controller):
        self.host_name = host_name
        self.controller = controller
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(None)
        self.STOP_BROADCAST = False
        self.bind_socket()
        threading.Thread(target=self.broadcast_lobby).start()
        self.s.listen()
        self.player_details = collections.defaultdict(dict)
        self.players = 0
        self.STOP_ACCEPT = False

    def broadcast_lobby(self):
        # Initializing broadcast socket
        print("Started Broadcast")
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Broadcast IP address and Username Continuously
        message = str.encode(json.dumps({"host": socket.gethostbyname(socket.gethostname()), "name":self.host_name, "port":5555}))
        while True:
            broadcast_socket.sendto(message, ('<broadcast>', 8888))
            time.sleep(1)
            if self.STOP_BROADCAST:
                broadcast_socket.close()
                print("Stopped Broadcast")
                return

    def bind_socket(self):
        server = socket.gethostname()
        port = 5555
        server_ip = socket.gethostbyname(server)
        while True:
            try:
                self.s.bind((server_ip, port))
                break
            except socket.error as e:
                print(str(e))

    def threaded_client(self, player_id):
        while True:
            try:
                data = self.player_details[player_id]["conn"].recv(1024)
                reply = json.loads(data.decode())
                if not data:
                    self.player_details[player_id]["conn"].send(json.dumps({"Signal": "Goodbye"}))
                    break
                else:
                    if reply["Signal"] == "name":
                        self.controller.frames["HostGame"].add_player(reply["name"], player_id)
                    elif reply["Signal"] == "Submission":
                        self.controller.frames["PlayGame"].receive_word(reply["Word"], player_id)
            except socket.error:
                break

        print("Connection closed")
        self.player_details[player_id]["conn"].close()

    def accept_players(self):
        while True:
            if self.STOP_ACCEPT:
                break
            conn, addr = self.s.accept()
            print("Connected to: ", addr)
            self.player_details[str(addr)] = {"conn": conn, "addr": addr}
            thread = threading.Thread(target=self.threaded_client, kwargs={"player_id": str(addr)})
            thread.start()

    def start_game(self, game_info):
        self.STOP_BROADCAST = True
        self.STOP_ACCEPT = True
        for player in self.player_details:
            self.player_details[player]["conn"].send(str.encode(json.dumps({
                "Signal": "Player info", 
                "Player info": game_info,
                "Player ID": player})))
    
    def send_card(self, card_idx):
        for player in self.player_details:
            self.player_details[player]["conn"].send(str.encode(json.dumps({
                "Signal": "Card",
                "Card Index": card_idx
            })))
    
    def update_submission(self, player_id):
        for player in self.player_details:
            self.player_details[player]["conn"].send(str.encode(json.dumps({
                "Signal": "Update Submission",
                "Player": player_id
            })))

    def send_results(self, result):
        for player in self.player_details:
            self.player_details[player]["conn"].send(str.encode(json.dumps({
                "Signal": "Results",
                "Result": result
            })))
