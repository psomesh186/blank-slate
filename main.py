from doctest import Example
from email.policy import strict
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from network import server, client
import threading
import collections
import time


class BlankSlate(tk.Tk):
    '''Creates main application frame and provides frame switching'''
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Blank Slate")

        # Creating application container
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Storing different frames
        self.frames = {}
        self.add_frame(HomePage, "HomePage")
        self.add_frame(HostGame, "HostGame")
        self.add_frame(JoinGame, "JoinGame")
        self.add_frame(WaitFrame, "WaitFrame")

        # Displaying homepage
        self.switch_frame("HomePage")

        self.lobby = None
        self.players = collections.defaultdict(dict)
        self.id = None
        self.win_threshold = 25

    def add_frame(self, frame_class, frame_name):
        frame = frame_class(self.container, self)
        self.frames[frame_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def switch_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

    def add_players(self, player_details, player_id):
        self.players = player_details
        self.id = player_id
        self.add_frame(PlayGame, "PlayGame")

class HomePage(tk.Frame):
    '''Creates the homepage of the game'''

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        cover_frame = tk.Frame(self)
        # Loading cover image
        self.cover_image = None
        self.load_cover()
        cover = ttk.Label(cover_frame, image=self.cover_image)
        cover.pack(fill="both", expand=True)
        cover_frame.pack(expand=True)

        controls = tk.Frame(self)
        # Creating host button
        host_button = ttk.Button(controls, text="Host Game", command=self.host_game)
        host_button.pack(side=tk.LEFT, padx=20)

        # Creating join button
        join_button = ttk.Button(controls, text="Join Game", command=self.join_game)
        join_button.pack(side=tk.LEFT, padx=20)

        controls.pack()


    def load_cover(self):
        '''Loads game cover image'''
        image = Image.open(f"images/blank-slate.png")
        self.cover_image = ImageTk.PhotoImage(image)

    def host_game(self):
        '''Switch to host game frame'''
        self.controller.switch_frame("HostGame")

    def join_game(self):
        '''Switch to join game frame'''
        self.controller.switch_frame("JoinGame")


class HostGame(tk.Frame):
    '''Creates the frame with game hosting controls'''
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Get host name and host a lobby
        host_frame = tk.Frame(self)
        label = ttk.Label(host_frame, text="Enter Username:")
        label.pack(side=tk.LEFT, padx=20)
        self.host_name = ttk.Entry(host_frame)
        self.host_name.pack(side=tk.LEFT, padx=20)
        self.host_button = ttk.Button(host_frame, text="Host Game", command=self.host_game)
        self.host_button.pack(side=tk.LEFT, padx=20)
        host_frame.pack()

        # Lobby details
        self.lobby_frame = tk.Frame(self, highlightbackground="blue", highlightthickness=2)
        self.lobby_frame.pack(padx=20, pady=10, expand=tk.YES, fill=tk.BOTH)
        
        # Control buttons frame
        button_frame = tk.Frame(self)
        self.start_button = ttk.Button(button_frame, text="Start Game", command=self.start_game, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=20)
        home_button = ttk.Button(button_frame, text="Home Page", command=self.go_to_home)
        home_button.pack(side=tk.LEFT, padx=20)
        button_frame.pack(pady=10)
        self.player_details = collections.defaultdict(dict)

    def host_game(self):
        self.controller.lobby = server.Server(self.host_name.get(), self.controller)
        self.host_button.config({"state": tk.DISABLED})
        self.lobby_label = ttk.Label(self.lobby_frame, text=f"{self.host_name.get()}'s Lobby")
        self.lobby_label.pack()
        self.player_details["Host"]["name"] = self.host_name.get()
        self.player_details["Host"]["score"] = 0
        threading.Thread(target=self.controller.lobby.accept_players).start()
        self.start_button.config(state=tk.NORMAL)

    def add_player(self, player_name, player_id):
        self.lobby_label = ttk.Label(self.lobby_frame, text=f"{player_name}")
        self.lobby_label.pack()
        self.player_details[player_id]["name"] = player_name
        self.player_details[player_id]["score"] = 0
    
    def start_game(self):
        self.controller.add_players(self.player_details, "Host")
        self.controller.lobby.start_game(self.player_details)
        time.sleep(0.1)
        self.controller.frames["PlayGame"].choose_card()
        self.controller.switch_frame("PlayGame")

    def go_to_home(self):
        self.controller.switch_frame("HomePage")


class JoinGame(tk.Frame):
    '''Creates the frame with game joining controls'''
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Get participant name and join a lobby
        participant_frame = tk.Frame(self)
        label = ttk.Label(participant_frame, text="Enter Username:")
        label.pack(side=tk.LEFT, padx=20)
        self.participant_name = ttk.Entry(participant_frame)
        self.participant_name.pack(side=tk.LEFT, padx=20)
        self.join_button = ttk.Button(participant_frame, text="Join Game", command=self.join_game)
        self.join_button.pack(side=tk.LEFT, padx=20)
        participant_frame.pack()

        # Display Available lobbies to join
        self.lobby_frame = tk.Frame(self, highlightbackground="blue", highlightthickness=2)
        self.lobby_frame.pack(padx=20, pady=10, expand=tk.YES, fill=tk.BOTH)
        
        # Control buttons frame
        button_frame = tk.Frame(self)
        home_button = ttk.Button(button_frame, text="Home Page", command=self.go_to_home)
        home_button.pack()
        button_frame.pack(pady=10)

    def go_to_home(self):
        self.controller.switch_frame("HomePage")

    def join_game(self):
        self.join_button.config({"state": tk.DISABLED})
        self.controller.lobby = client.Client(self.participant_name.get(), self.controller)
        threading.Thread(target=self.controller.lobby.get_hosts).start()

    def add_lobby(self, lobby_name, host):
        lobby = ttk.Button(master=self.lobby_frame, text=f"{lobby_name}", command=lambda host=host: self.start_game(host))
        lobby.pack()
        self.lobby_frame.pack()

    def start_game(self, host):
        self.controller.lobby.join_lobby(host)
        self.controller.switch_frame("WaitFrame")


class WaitFrame(tk.Frame):
    '''Waiting screen till host starts the game'''
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text=f"Waiting for host to start the game...", font=("Helvetica", 45, "bold"))
        label.pack()


class PlayGame(tk.Frame):
    '''Creates the frame where the game is played'''
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Loading cards
        with open('cards.txt') as f:
            self.cards = [line.strip() for line in f.readlines()]
        self.card_idx = list(range(len(self.cards)))
        random.shuffle(self.card_idx)
        self.current_idx = 0

        score_frame = tk.Frame(self)
        self.score_labels = {}
        label = ttk.Label(score_frame, text=f"Player Scores")
        label.pack()
        for player in self.controller.players:
            player_frame = tk.Frame(score_frame)
            player_name = ttk.Label(player_frame, text=f"{self.controller.players[player]['name']}: ")
            if player == self.controller.id:
                player_name.config(foreground="red")
            self.score_labels[player] = ttk.Label(player_frame, text=f"{self.controller.players[player]['score']}")
            player_name.pack(side=tk.LEFT)
            self.score_labels[player].pack(side=tk.LEFT)
            player_frame.pack()
        
        score_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=10)

        self.game_frame = tk.Frame(self, highlightbackground="blue", highlightthickness=2)
        self.current_card = ttk.Label(self.game_frame, text=f"", font=("Helvetica", 30, "bold"))
        self.current_card.pack(pady=20)
        self.answer = ttk.Entry(self.game_frame, font=("Helvetica", 30, "bold"))
        self.answer.pack(pady=20)
        self.submit_button = ttk.Button(self.game_frame, text="Submit", command=self.submit_word)
        self.submit_button.pack(pady=20)

        self.player_frame = tk.Frame(self.game_frame)
        self.submission_labels = {}
        for player in self.controller.players:
            self.submission_labels[player] = ttk.Label(self.player_frame, text=f"{self.controller.players[player]['name']}")
            self.submission_labels[player].pack(side=tk.LEFT)
        self.player_frame.pack(padx=20, pady=10)
        self.game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.result_frame = tk.Frame(self, highlightbackground="blue", highlightthickness=2)
        self.result_labels = {}
        for player in self.controller.players:
            result_label_frame = tk.Frame(self.result_frame)
            name = ttk.Label(result_label_frame, text=f"{self.controller.players[player]['name']}: ", font=("Helvetica", 30, "bold"))
            self.result_labels[player] = ttk.Label(result_label_frame, font=("Helvetica", 30, "italic"))
            name.pack(side=tk.LEFT)
            self.result_labels[player].pack(side=tk.LEFT)
            result_label_frame.pack()
        if self.controller.id == "Host":
            self.next_round_button = ttk.Button(self.result_frame, text="Next Round", command=self.choose_card)
            self.next_round_button.pack(side=tk.BOTTOM, pady=20)
        self.answers = {}
        self.color_map = {"w": "white", "b": "blue", "g": "green"}

    def choose_card(self):
        card_idx = self.card_idx[self.current_idx]
        self.current_idx += 1
        self.controller.lobby.send_card(card_idx)
        self.set_card(card_idx)

    def set_card(self, card_idx):
        self.result_frame.pack_forget()
        self.answer.delete(0, tk.END)
        self.submit_button.configure(state=tk.NORMAL)
        self.answers = {}
        for player in self.controller.players:
            self.submission_labels[player].config(foreground="white")
        self.game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.current_card.config(text=f"{self.cards[card_idx]}")

    def update_submission(self, player):
        self.submission_labels[player].configure(foreground="green")

    def receive_word(self, word, player):
        self.answers[player] = word
        if len(self.answers) == len(self.controller.players):
            self.process_results()
            return
        self.controller.lobby.update_submission(player)
        self.update_submission(player)

    def submit_word(self):
        self.submit_button.configure(state=tk.DISABLED)
        if self.controller.id == "Host":
            self.receive_word(self.answer.get(), "Host")
        else:
            self.controller.lobby.send_word(self.answer.get())

    def process_results(self):
        words = {}
        result = {}
        for player, word in self.answers.items():
            word = word.lower()
            if word in words:
                words[word].append(player)
            else:
                words[word] = [player]
        for word, players in words.items():
            if len(players) > 2:
                color = 'b'
                reward = 1
            elif len(players) == 2:
                color = 'g'
                reward = 3
            else:
                color = 'w'
                reward = 0
            for player in players:
                self.controller.players[player]["score"] += reward
                result[player] = [word, color, self.controller.players[player]["score"]]
        self.show_results(result)
        self.controller.lobby.send_results(result)

    def show_results(self, result):
        self.game_frame.pack_forget()
        
        for player in self.controller.players:
            self.result_labels[player].configure(text=f"{result[player][0]}", foreground=self.color_map[result[player][1]])
            self.score_labels[player].configure(text=f"{result[player][2]}")
            self.controller.players[player]["score"] = result[player][2]
        
        # Checking player scores for win threshold
        winners = []
        for player in self.controller.players:
            if self.controller.players[player]["score"] >= self.controller.win_threshold:
                winners.append(self.controller.players[player]["name"])
        if len(winners) > 0:
            if self.controller.id == "Host":
                self.next_round_button.pack_forget()
            winner_label = ttk.Label(self.result_frame, text=f"{', '.join(winners)} WON!!!", font=("Helvetica", 45, "bold"))
            winner_label.pack(pady=20)
        self.result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
            


if __name__ == '__main__':
    app = BlankSlate()
    app.mainloop()