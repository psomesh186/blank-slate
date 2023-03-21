import collections
import threading
from network import server, client
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
import time

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
        self.manager.get_screen("PlayGame").choose_card()
    
    def add_players(self, player_details, player_id):
        BlankSlateApp.players = player_details
        BlankSlateApp.id = player_id
    
    def add_player(self, player_name, player_id):
        label = MDLabel(text=f"{player_name}", size_hint_y=None, height=50, halign="center")
        self.ids.lobby.add_widget(label, index=1)
        self.player_details[player_id]["name"] = player_name
        self.player_details[player_id]["score"] = 0


class JoinGame(MDScreen):
    
    def join_game(self):
        self.participant_name = self.ids.participant_name.text
        print(self.participant_name)
        self.ids.join_button.disabled = True
        BlankSlateApp.lobby = client.Client(self.participant_name, self.manager)
        threading.Thread(target=BlankSlateApp.lobby.get_hosts).start()

    def add_lobby(self, lobby_name, host):
        button = MDRaisedButton(text=f"{lobby_name}", size_hint_x=0.8, pos_hint={'center_x': 0.5}, on_release=lambda: self.start_game(host))
        self.ids.lobby.add_widget(button, index=1)
    
    def start_game(self, host):
        BlankSlateApp.lobby.join_lobby(host)
        self.manager.current = "WaitScreen"
        self.manager.transition.direction = "left"
    
    def add_players(self, player_details, player_id):
        BlankSlateApp.players = player_details
        BlankSlateApp.id = player_id


class WaitScreen(MDScreen):
    pass


class PlayGame(MDScreen):
    
    def choose_card(self):
        pass


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

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return None

if __name__ == "__main__":
    threading.Thread(target=BlankSlateApp().run())