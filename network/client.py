import socket
import json
import collections
import threading
import tkinter as tk
from tkinter import ttk


class Client:
    '''Enables players to join a host's lobby'''
    def __init__(self, client_name, controller):
        self.client_name = client_name
        self.controller = controller
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
                self.controller.frames["JoinGame"].add_lobby(msg["name"], msg["host"])
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
                    self.controller.add_players(reply["Player info"], reply["Player ID"])
                    self.controller.switch_frame("PlayGame")
                elif reply["Signal"] == "Card":
                    self.controller.frames["PlayGame"].set_card(reply["Card Index"])
                elif reply["Signal"] == "Update Submission":
                    self.controller.frames["PlayGame"].update_submission(reply["Player"])
                elif reply["Signal"] == "Results":
                    self.controller.frames["PlayGame"].show_results(reply["Result"])
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