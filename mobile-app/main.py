import collections
import threading
from network import server, client
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRaisedButton
from kivy.clock import mainthread
from kivymd.app import MDApp
import time
from functools import partial
import random

class HomePage(MDScreen):
    pass


class HostGame(MDScreen):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.player_details = collections.defaultdict(dict)

    def host_game(self):
        self.host_name = self.ids.host_name.text
        self.ids.lobby_name.text = self.host_name + "'s Lobby"
        self.ids.host_button.disabled = True
        BlankSlateApp.lobby = server.Server(self.host_name, self.manager)
        self.player_details["Host"]["name"] = self.host_name
        self.player_details["Host"]["score"] = 0
        threading.Thread(target=BlankSlateApp.lobby.accept_players).start()
        self.ids.start_button.disabled = False

    def start_game(self):
        self.add_players(self.player_details, "Host")
        BlankSlateApp.lobby.start_game(self.player_details)
        time.sleep(0.1)
        # self.manager.get_screen("PlayGame").choose_card(None)
    
    def add_players(self, player_details, player_id):
        BlankSlateApp.players = player_details
        BlankSlateApp.id = player_id
    
    @mainthread
    def add_player(self, player_name, player_id):
        label = MDLabel(text=f"{player_name}", size_hint_y=None, height=50, halign="center")
        self.ids.lobby.add_widget(label, index=1)
        self.player_details[player_id]["name"] = player_name
        self.player_details[player_id]["score"] = 0


class JoinGame(MDScreen):
    
    def join_game(self):
        self.participant_name = self.ids.participant_name.text
        self.ids.join_button.disabled = True
        BlankSlateApp.lobby = client.Client(self.participant_name, self.manager)
        threading.Thread(target=BlankSlateApp.lobby.get_hosts).start()

    @mainthread
    def add_lobby(self, lobby_name, host):
        button = MDRaisedButton(text=f"{lobby_name}'s Lobby", size_hint_x=0.8, pos_hint={'center_x': 0.5}, on_release=partial(self.start_game, host))
        self.ids.lobby.add_widget(button, index=1)
    
    def start_game(self, host, _):
        BlankSlateApp.lobby.join_lobby(host)
        self.manager.current = "WaitScreen"
        self.manager.transition.direction = "left"
    
    @mainthread
    def add_players(self, player_details, player_id):
        BlankSlateApp.players = player_details
        BlankSlateApp.id = player_id
        self.manager.current = "PlayGame"
        self.manager.transition.direction = "left"


class WaitScreen(MDScreen):
    pass


class PlayGame(MDScreen):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Loading cards
        with open('cards.txt') as f:
            self.cards = [line.strip() for line in f.readlines()]
        self.card_idx = list(range(len(self.cards)))
        random.shuffle(self.card_idx)
        self.current_idx = 0
        self.answers = {}

    def on_pre_enter(self):
        self.create_score_table(BlankSlateApp.players)
        self.add_buttons()
        if BlankSlateApp.id == "Host":
            self.choose_card(None)
    
    def create_score_table(self, players):
        self.ids.grid.cols = 3
        self.ids.grid.rows = len(players)

        for idx, player in enumerate(players):
            label = MDLabel(text=f"{players[player]['name']}: {players[player]['score']}")
            if player == BlankSlateApp.id:
                label.color = (1, 0, 0, 1)
            self.ids[f"{idx}_label"] = label
            self.ids.grid.add_widget(label)
            icon = MDIcon(icon='check', theme_text_color='Custom', text_color=(0, 1, 0, 1))
            icon.opacity = 0
            self.ids[f"{idx}_icon"] = icon
            self.ids.grid.add_widget(icon)
            # self.ids.grid.add_widget(Button(size_hint_x=0.1)) # use this instead of icon to visualize cell size
            answer = MDLabel(text='', theme_text_color='Custom')
            self.ids[f"{idx}_answer"] = answer
            self.ids.grid.add_widget(answer)

    def add_buttons(self):
        if BlankSlateApp.id == "Host":
            submit_button = MDRaisedButton(text="Submit", size_hint=(0.4, None), on_release=self.submit_word)
            next_round_button = MDRaisedButton(text="Next Round", size_hint=(0.4, None), on_release=self.choose_card)
            self.ids.buttons.add_widget(submit_button)
            self.ids.buttons.add_widget(next_round_button)
        else:
            submit_button = MDRaisedButton(text="Submit", size_hint=(1, None), on_release=self.submit_word)
            self.ids.buttons.add_widget(submit_button)
        self.ids["submit_button"] = submit_button
    
    def submit_word(self, _):
        self.ids["submit_button"].disabled = True
        if BlankSlateApp.id == "Host":
            self.receive_word(self.ids.answer.text, "Host")
        else:
            BlankSlateApp.lobby.send_word(self.ids.answer.text)

    def receive_word(self, word, player):
        self.answers[player] = word
        BlankSlateApp.lobby.update_submission(player)
        self.update_submission(player)
        if len(self.answers) == len(BlankSlateApp.players):
            self.process_results()
            return

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
                color = (0, 0, 1, 1)
                reward = 1
            elif len(players) == 2:
                color = (0, 1, 0, 1)
                reward = 3
            else:
                color = (1, 1, 1, 1)
                reward = 0
            for player in players:
                BlankSlateApp.players[player]["score"] += reward
                result[player] = [word, color, BlankSlateApp.players[player]["score"]]
        self.show_results(result)
        BlankSlateApp.lobby.send_results(result)

    @mainthread
    def show_results(self, result):
        for idx, player in enumerate(BlankSlateApp.players):
            self.ids[f"{idx}_label"].text = f"{BlankSlateApp.players[player]['name']}: {result[player][2]}"
            self.ids[f"{idx}_answer"].text = result[player][0]
            self.ids[f"{idx}_answer"].text_color = result[player][1]
            BlankSlateApp.players[player]["score"] = result[player][2]
        
        # Checking player scores for win threshold
        winners = []
        for player in BlankSlateApp.players:
            if BlankSlateApp.players[player]["score"] >= BlankSlateApp.win_threshold:
                winners.append(BlankSlateApp.players[player]["name"])
        if len(winners) > 0:
            if BlankSlateApp.id == "Host":
                self.ids["next_round_button"].disabled = True
            self.ids.current_card.text = f"{', '.join(winners)} WON!!!"

    @mainthread
    def update_submission(self, player):
        idx = list(BlankSlateApp.players).index(player)
        self.ids[f"{idx}_icon"].opacity = 1

    def choose_card(self, _):
        card_idx = self.card_idx[self.current_idx]
        self.current_idx += 1
        BlankSlateApp.lobby.send_card(card_idx)
        self.set_card(card_idx)
    
    def reset_round(self):
        for idx, player in enumerate(BlankSlateApp.players):
            self.ids[f"{idx}_icon"].opacity = 0
            self.ids[f"{idx}_answer"].text = ""
            self.ids[f"{idx}_label"].text_color = (1, 1, 1, 1)
        self.ids["submit_button"].disabled = False
        self.ids.answer.text = ""
        self.answers = {}

    @mainthread
    def set_card(self, card_idx):
        self.reset_round()
        self.ids.current_card.text = self.cards[card_idx]


class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        Window.size = (350, 650)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        '''Maps Screens to return to on back press'''

        if key == 27:  # the esc key
            if self.current_screen.name == "HomePage":
                return False  # exit the app from this page
            elif self.current_screen.name == "HostGame":
                self.current = "HomePage"
                self.transition.direction = "right"
                return True  # do not exit the app
            elif self.current_screen.name == "JoinGame":
                self.current = "HomePage"
                self.transition.direction = "right"
                return True  # do not exit the app


class BlankSlateApp(MDApp):

    win_threshold = 25

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return None

if __name__ == "__main__":
    BlankSlateApp().run()