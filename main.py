import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
        self.add_frame(HomePage)
        self.add_frame(HostGame)
        self.add_frame(JoinGame)

        # Loading cards
        with open('cards.txt') as f:
            cards = [line.strip() for line in f.readlines()]
            self.white_cards = cards[:250]
            self.black_cards = cards[250:]

        # Displaying homepage
        self.switch_frame(HomePage)

    def add_frame(self, frame_name):
        frame = frame_name(self.container, self)
        self.frames[frame_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def switch_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()


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
        host_button = ttk.Button(controls, text="Host Game", command = self.host_game)
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
        self.controller.switch_frame(HostGame)

    def join_game(self):
        '''Switch to join game frame'''
        self.controller.switch_frame(JoinGame)

class HostGame(tk.Frame):
    '''Creates the frame with game hosting controls'''
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Host a Game")
        label.pack()


class JoinGame(tk.Frame):
    '''Creates the frame with game joining controls'''
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Join a Game")
        label.pack()


if __name__ == '__main__':
    app = BlankSlate()
    app.mainloop()