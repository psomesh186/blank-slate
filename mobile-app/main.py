import collections
import threading
from network import server, client
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp

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
        pass


class JoinGame(MDScreen):
    pass


class PlayGame(MDScreen):
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
    BlankSlateApp().run()