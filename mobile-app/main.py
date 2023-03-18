from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp

class HomePage(MDScreen):
    pass


class HostGame(MDScreen):
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