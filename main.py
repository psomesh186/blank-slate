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
            self.cards = [line.strip() for line in f.readlines()]

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
        self.controller.switch_frame(HostGame)

    def join_game(self):
        '''Switch to join game frame'''
        self.controller.switch_frame(JoinGame)

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
        self.lobby_label = ttk.Label(self.lobby_frame, text=f"<Host Name>'s Lobby")
        self.lobby_label.pack()
        for i in range(4):
            player = ttk.Label(self.lobby_frame, text=f"Player {i}")
            player.pack()
        self.lobby_frame.pack(padx=20, pady=10, expand=tk.YES, fill=tk.BOTH)
        
        # Control buttons frame
        button_frame = tk.Frame(self)
        start_button = ttk.Button(button_frame, text="Start Game", command=self.start_game)
        start_button.pack(side=tk.LEFT, padx=20)
        home_button = ttk.Button(button_frame, text="Home Page", command=self.go_to_home)
        home_button.pack(side=tk.LEFT, padx=20)
        button_frame.pack(pady=10)

    def host_game(self):
        pass

    def start_game(self):
        pass

    def go_to_home(self):
        self.controller.switch_frame(HomePage)

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
        participant_frame.pack()

        # Display Available lobbies to join
        self.lobby_frame = tk.Frame(self, highlightbackground="blue", highlightthickness=2)
        for i in range(4):
            lobby = ttk.Button(self.lobby_frame, text=f"Player {i}")
            lobby.pack()
        self.lobby_frame.pack(padx=20, pady=10, expand=tk.YES, fill=tk.BOTH)
        
        # Control buttons frame
        button_frame = tk.Frame(self)
        home_button = ttk.Button(button_frame, text="Home Page", command=self.go_to_home)
        home_button.pack()
        button_frame.pack(pady=10)

    def go_to_home(self):
        self.controller.switch_frame(HomePage)

if __name__ == '__main__':
    app = BlankSlate()
    app.mainloop()