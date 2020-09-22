import tkinter as tk
import bet as db
from os import path


def type_safety(data: dict) -> bool:
    """Make sure each input is the correct type"""
    for i in data:
        data[i] = data[i].get()

    try:
        data["Wager"] = int(data["Wager"])
        data["Odds"] = int(data["Odds"])

    except ValueError:
        return False

    return True


def separate_parley(data: dict):

    bets = data["Matchup"].split(",")
    for i in range(len(bets)):
        bets[i] = bets[i].strip()
        key = f"bet{i + 1}"
        data[key] = bets[i]


class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.data = {}

        self.label_sport = None
        self.label_matchup = None
        self.label_odds = None
        self.label_wager = None
        self.label_type = None
        self.label_bet_on = None

        self.sport_input = None
        self.match_input = None
        self.odds_input = None
        self.wager_input = None
        self._type_input = None
        self.bet_on_input = None

        self.inputs = []
        self.labels = []

        self.canvas = None
        self.button = None
        self.img_label = None
        self.error_msg = None

        self.menu()
        self.exit_button()

        if not path.isfile("bets.db"):
            db.initialize(0)

        self.home_page()

    def exit_button(self):
        btn = tk.Button(self.master, text='Exit', bd='5', command=self.master.destroy, bg="red")
        btn.grid(row=3, column=1, pady=10)

    def menu(self):
        menu_bar = tk.Menu(self.master)

        _open = tk.Menu(menu_bar, tearoff=0)
        _open.add_command(label="Bet", command=lambda: [self.clear(), self.open_bet_menu()])
        _open.add_command(label="Parley", command=lambda: [self.clear(), self.open_parley_menu()])
        menu_bar.add_cascade(label="Open", menu=_open)

        _close = tk.Menu(menu_bar, tearoff=0)
        _close.add_command(label="Bet")
        _close.add_command(label="Parley")
        menu_bar.add_cascade(label="Close", menu=_close)

        view = tk.Menu(menu_bar, tearoff=0)
        view.add_command(label="Open", command=None)
        view.add_command(label="Closed")
        view.add_command(label="All")
        view.add_command(label="Search")
        menu_bar.add_cascade(label="View", menu=view)

        bank = tk.Menu(menu_bar, tearoff=0)
        bank.add_command(label="History")
        menu_bar.add_cascade(label="Bank", menu=bank)

        self.master.config(menu=menu_bar)

    def home_page(self):

        self.canvas = tk.Canvas(self.master, width=300, height=300, bg="green")
        img = tk.PhotoImage(file="m1.png")
        self.img_label = tk.Label(image=img)
        self.img_label.image = img  # must keep a reference of the image
        self.img_label.grid()
        self.canvas.create_image(20, 20, anchor="nw", image=img)

    def open_bet_menu(self):

        self.label_sport = tk.Label(self.master, text="Sport")
        self.label_type = tk.Label(self.master, text="Type")
        self.label_matchup = tk.Label(self.master, text="Matchup")
        self.label_bet_on = tk.Label(self.master, text="Bet")
        self.label_odds = tk.Label(self.master, text="Odds")
        self.label_wager = tk.Label(self.master, text="Wager")

        sport = tk.StringVar()
        _type = tk.StringVar()
        matchup = tk.StringVar()
        bet_on = tk.StringVar()
        odds = tk.StringVar()
        wager = tk.StringVar()

        self.sport_input = tk.Entry(self.master, width=7, textvariable=sport)
        self._type_input = tk.Entry(self.master, width=7, textvariable=_type)
        self.match_input = tk.Entry(self.master, width=20, textvariable=matchup)
        self.bet_on_input = tk.Entry(self.master, width=20, textvariable=bet_on)
        self.odds_input = tk.Entry(self.master, width=7, textvariable=odds)
        self.wager_input = tk.Entry(self.master, width=7, textvariable=wager)

        self.data["Sport"] = sport
        self.data["Type"] = _type
        self.data["Matchup"] = matchup
        self.data["Bet"] = bet_on
        self.data["Odds"] = odds
        self.data["Wager"] = wager

        self.sport_input.grid(row=1, column=1)
        self.label_sport.grid(row=2, column=1)

        self._type_input.grid(row=1, column=2)
        self.label_type.grid(row=2, column=2)

        self.match_input.grid(row=1, column=3)
        self.label_matchup.grid(row=2, column=3)

        self.bet_on_input.grid(row=1, column=4, pady=30)
        self.label_bet_on.grid(row=2, column=4)

        self.odds_input.grid(row=1, column=5)
        self.label_odds.grid(row=2, column=5)

        self.wager_input.grid(row=1, column=6)
        self.label_wager.grid(row=2, column=6)

        self.labels = [self.label_sport, self.label_matchup, self.label_odds,
                       self.label_wager, self.label_type, self.label_bet_on]

        self.inputs = [self.sport_input, self.match_input, self.odds_input,
                       self.wager_input, self._type_input, self.bet_on_input]

        self.button = tk.Button(self.master, text="Confirm",
                                command=lambda: [self.confirm(_type="bet"), self.home_page()], bd='5', bg="green")

        self.button.grid(row=3, column=4, pady=3)

    def open_parley_menu(self):
        self.label_sport = tk.Label(self.master, text="Sport")
        self.label_matchup = tk.Label(self.master, text="Matchup(s) separated by a ','")
        self.label_odds = tk.Label(self.master, text="Odds")
        self.label_wager = tk.Label(self.master, text="Wager")

        sport = tk.StringVar()
        matchup = tk.StringVar()
        odds = tk.StringVar()
        wager = tk.StringVar()

        self.sport_input = tk.Entry(self.master, width=7, textvariable=sport)
        self.match_input = tk.Entry(self.master, width=48, textvariable=matchup)
        self.odds_input = tk.Entry(self.master, width=7, textvariable=odds)
        self.wager_input = tk.Entry(self.master, width=7, textvariable=wager)

        self.data["Sport"] = sport
        self.data["Matchup"] = matchup
        self.data["Odds"] = odds
        self.data["Wager"] = wager

        self.sport_input.grid(row=1, column=2)
        self.label_sport.grid(row=2, column=2)

        self.match_input.grid(row=1, column=4)
        self.label_matchup.grid(row=2, column=4)

        self.odds_input.grid(row=1, column=6, pady=30)
        self.label_odds.grid(row=2, column=6)

        self.wager_input.grid(row=1, column=7)
        self.label_wager.grid(row=2, column=7)

        self.labels = [self.label_sport, self.label_matchup, self.label_odds, self.label_wager]
        self.inputs = [self.sport_input, self.match_input, self.odds_input, self.wager_input]

        self.button = tk.Button(self.master, text="Confirm", 
                                command=lambda: [self.confirm(_type="parley"), self.home_page()], bd='5', bg="green")
        
        self.button.grid(row=3, column=4, pady=3)

    def clear(self):
        """"Destroy old widgets and send data to database"""

        for label in self.labels:
            if label:
                label.destroy()

        for inputs in self.inputs:
            if inputs:
                inputs.destroy()

        if self.button:
            self.button.destroy()

        if self.canvas:
            self.img_label.config(image="")

        self.data.clear()

    def confirm(self, _type=None):

        if not type_safety(self.data):
            self.error_msg = tk.Label(self.master, text="Odds/Wager must be a number")
            self.error_msg.grid(row=2, column=2)
            self.clear()
            return

        if _type == "bet":
            db.new_bet(self.data)
        elif _type == "parley":
            separate_parley(self.data)
            db.open_parley(self.data)

        self.clear()

    def error_handling(self):
        """Handle the case where inputs """


if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    root.title("Bet Tracker")
    root.geometry("1000x500")
    app.mainloop()
