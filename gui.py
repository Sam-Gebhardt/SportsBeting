import tkinter as tk
import bet as db
from os import path


def type_safety(data: dict) -> bool:
    """Make sure each input is the correct type"""

    for i in data:
        data[i] = data[i].get()

    try:
        data["Wager"] = float(data["Wager"])
        data["Odds"] = int(data["Odds"])

    except ValueError:
        return False

    return True


def separate_parley(data: dict):
    """Take user input and correctly separate it into a dict"""

    bets = data["Matchup"].split(",")
    for i in range(len(bets)):
        bets[i] = bets[i].strip()
        key = f"bet{i + 1}"
        data[key] = bets[i]


def turn_to_str(data: dict) -> dict:
    """Turn tk string object to a python str"""

    for i in data:
        data[i] = data[i].get()

    return data


def make_db():
    """Check if a db exists, call the apportion function if needed"""

    if not path.isfile("bets.db"):
        db.initialize(0)


class App(tk.Frame):
    """Main window for the app"""

    def __init__(self, master=None):
        super().__init__(master)

        self.master = master
        self.data = {}

        self.label_sport = None  # Labels for entries when opening bets
        self.label_matchup = self.label_odds = self.label_wager = self.label_type = self.label_bet_on = None

        self.sport_input = None  # text entry boxes when opening bets
        self.match_input = self.odds_input = self.wager_input = self._type_input = self.bet_on_input = None

        self.inputs = []  # list of input boxes
        self.labels = []  # list of labels

        self.canvas = None  # home image
        self.img_label = None

        self.button = None  # Confirm button
        self.close_button = None  # exit the app

        self.error_msg = None  # Error if wager/odds != int
        self.view_labels = []  # labels for viewing bets
        self.menu_bar = None  # menu bar
        self.selections = None  # list box selections to close bets

        self.listbox = None  # widgets for closing bets
        self.won_button = self.loss_button = None

        self.menu()
        self.home_page()

    def exit_button(self, col=99):
        """Makes a button that kills the app window"""

        self.close_button = tk.Button(self.master, text='Exit', bd='5', command=self.master.destroy, bg="red")
        self.close_button.grid(row=99, column=col, sticky="SE")

    def menu(self):
        """Creates a menu bar with the options: open, close, view, bank and wallet balance"""

        self.menu_bar = tk.Menu(self.master)

        _open = tk.Menu(self.menu_bar, tearoff=0)
        _open.add_command(label="Bet", command=lambda: [self.clear(), self.open_bet_menu(), self.exit_button(col=5)])
        _open.add_command(label="Parley", command=lambda:
                          [self.clear(), self.open_parley_menu(), self.exit_button(col=3)])

        self.menu_bar.add_cascade(label="Open", menu=_open)

        _close = tk.Menu(self.menu_bar, tearoff=0)
        _close.add_command(label="Bet", command=lambda: [self.clear(), self.close_bet(), self.exit_button()])
        _close.add_command(label="Parley", command=lambda: [self.clear(), self.close_parley(), self.exit_button()])
        self.menu_bar.add_cascade(label="Close", menu=_close)

        view = tk.Menu(self.menu_bar, tearoff=0)
        view.add_command(label="Open", command=lambda: [self.clear(), self.view_open(), self.exit_button()])
        view.add_command(label="Closed", command=lambda: [self.clear(), self.view_closed(), self.exit_button()])
        view.add_command(label="All", command=lambda:
                         [self.clear(), self.view_open(), self.view_closed(), self.exit_button()])

        view.add_command(label="Search", command=lambda: [self.clear(), self.search(), self.exit_button(col=5)])
        self.menu_bar.add_cascade(label="View", menu=view)

        bank = tk.Menu(self.menu_bar, tearoff=0)
        bank.add_command(label="History", command=lambda: [self.clear(), self.bank_history(), self.exit_button()])
        bank.add_command(label="Add", command=lambda: [self.clear(), self.bank_add(), self.exit_button()])
        self.menu_bar.add_cascade(label="Bank", menu=bank)

        current_bankroll = db.bankroll_amount()[0]
        label_str = " " * 10 + f"Wallet: {current_bankroll}"
        self.menu_bar.add_cascade(label=label_str)
        self.master.config(menu=self.menu_bar)

    def update_bank(self):
        """Update the bank balance that's displayed in the menu"""

        bank = db.bankroll_amount()[0]
        label_str = " " * 10 + f"Wallet: {bank}"
        self.menu_bar.entryconfig(5, label=label_str)

    def home_page(self):
        """The homepage that displays the logo"""

        self.canvas = tk.Canvas(self.master, width=300, height=300, bg="green")
        img = tk.PhotoImage(file="m1.png")
        self.img_label = tk.Label(image=img)
        self.img_label.image = img  # must keep a reference of the image
        self.img_label.grid()
        self.canvas.create_image(20, 20, anchor="nw", image=img)
        self.exit_button()

    def open_bet_menu(self):
        """Create entries/labels for making a bet"""

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

        self.sport_input.grid(row=1, column=0)
        self.label_sport.grid(row=2, column=0)

        self._type_input.grid(row=1, column=1)
        self.label_type.grid(row=2, column=1)

        self.match_input.grid(row=1, column=2)
        self.label_matchup.grid(row=2, column=2)

        self.bet_on_input.grid(row=1, column=3, pady=30)
        self.label_bet_on.grid(row=2, column=3)

        self.odds_input.grid(row=1, column=4)
        self.label_odds.grid(row=2, column=4)

        self.wager_input.grid(row=1, column=5)
        self.label_wager.grid(row=2, column=5)

        self.labels = [self.label_sport, self.label_matchup, self.label_odds,
                       self.label_wager, self.label_type, self.label_bet_on]

        self.inputs = [self.sport_input, self.match_input, self.odds_input,
                       self.wager_input, self._type_input, self.bet_on_input]

        self.button = tk.Button(self.master, text="Confirm", command=lambda:
                                [self.confirm(_type="bet"), self.home_page(),
                                 self.update_bank()], bd='5', bg="green")

        self.button.grid(row=3, column=2, pady=3)

    def open_parley_menu(self):
        """Create entries/labels for making a parley bet"""

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

        self.sport_input.grid(row=1, column=0)
        self.label_sport.grid(row=2, column=0)

        self.match_input.grid(row=1, column=1)
        self.label_matchup.grid(row=2, column=1)

        self.odds_input.grid(row=1, column=2, pady=30)
        self.label_odds.grid(row=2, column=2)

        self.wager_input.grid(row=1, column=3)
        self.label_wager.grid(row=2, column=3)

        self.labels = [self.label_sport, self.label_matchup, self.label_odds, self.label_wager]
        self.inputs = [self.sport_input, self.match_input, self.odds_input, self.wager_input]

        self.button = tk.Button(self.master, text="Confirm",
                                command=lambda: [self.confirm(_type="parley"), self.home_page()], bd='5', bg="green")

        self.button.grid(row=3, column=1, pady=3)

    def close_bet(self, func=db.close_bet, bets_func=db.view_open_bets):
        """Close a bet"""

        self.listbox = tk.Listbox(self.master, selectmode="multiple")
        self.listbox.config(width=0, height=0)
        bets = bets_func()

        for i in bets:
            self.listbox.insert("end", i)

        self.listbox.grid(row=0, column=0)
        self.won_button = tk.Button(self.master, text="Won Bets", bg="green", bd=5,
                                    command=lambda: [self.get_selections(), func(self.selections),
                                                     self.clear(), self.update_bank(), self.home_page()])
        self.loss_button = tk.Button(self.master, text="Lost Bets", bg="red", bd=5,
                                     command=lambda: [self.get_selections(loss=True), func(self.selections),
                                                      self.clear(), self.update_bank(), self.home_page()])

        self.won_button.grid(row=1, column=1, padx=25)
        self.loss_button.grid(row=1, column=0)

    def close_parley(self):
        """Close a parley"""
        self.close_bet(func=db.close_parley, bets_func=db.view_open_parley)

    def get_selections(self, loss=False):
        """Get selections from listbox"""

        self.selections = [self.listbox.get(i) for i in self.listbox.curselection()]
        if loss:
            self.selections.append("L")
        else:
            self.selections.append("W")

    def view_open(self):
        """View open bets"""

        open_bets = db.view_open_bets()
        open_bets = db.stringify(open_bets)
        for i in range(len(open_bets)):
            self.view_labels.append(tk.Label(self.master, text=f"{open_bets[i]}"))
            self.view_labels[i].grid(row=i, column=0, sticky="w")

    def view_closed(self):
        """View closed bets"""

        closed_bets = db.view_closed_bets()
        closed_bets = db.stringify(closed_bets)
        for i in range(len(closed_bets)):
            self.view_labels.append(tk.Label(self.master, text=f"{closed_bets[i]}"))
            self.view_labels[i].grid(row=i, column=0, sticky="w")

    def view_data(self):
        """View data for a custom search"""

        results = db.custom_search(turn_to_str(self.data))
        results = db.stringify(results)
        self.clear()
        for i in range(len(results)):
            self.view_labels.append(tk.Label(self.master, text=f"{results[i]}"))
            self.view_labels[i].grid(row=i, column=0, sticky="w")

    def search(self):
        """Search db for a specific bet"""

        self.open_bet_menu()
        self.button.destroy()
        self.button = tk.Button(self.master, text="Search", command=lambda: [self.view_data()], bg="green", bd=5)
        self.button.grid(row=3, column=3)

    def bank_history(self):
        """See bankroll history"""

        results = db.view_bank()
        for i in range(len(results)):
            self.view_labels.append(tk.Label(self.master, text=f"{results[i]}"))
            self.view_labels[i].grid(row=i, column=0, sticky="w")

    def bank_add(self):
        """Add money to the bank"""

        self.label_wager = tk.Label(self.master, text="Amount: ")
        wager = tk.StringVar()
        self.wager_input = tk.Entry(self.master, width=7, textvariable=wager)
        self.data["Wager"] = wager

        self.wager_input.grid(row=1, column=1)
        self.label_wager.grid(row=1, column=0)

        self.labels = [self.label_wager]
        self.inputs = [self.wager_input]

        self.button = tk.Button(self.master, text="Add", command=lambda:
                                [db.bankroll_add(self.data["Wager"].get()),  # send change to db
                                 self.update_bank(), self.clear(), self.home_page()], bd='5', bg="green")

        self.button.grid(row=1, column=2, padx=13)

    def clear(self):
        """"Destroy old widgets and clear dict"""

        for label in self.labels:
            if label:
                label.destroy()

        for inputs in self.inputs:
            if inputs:
                inputs.destroy()

        for bet in self.view_labels:
            bet.destroy()
        self.view_labels = []

        if self.canvas:
            self.img_label.config(image="")

        widgets = [self.button, self.close_button, self.listbox, self.won_button, self.loss_button]
        for i in widgets:
            if i:
                i.destroy()

        self.data.clear()
        self.selections = None

    def confirm(self, _type=None):
        """Confirms that the inputted data conforms to the expected type"""

        if not type_safety(self.data):
            ErrorWindow("Wager/Odds must be a number")
            self.clear()
            return

        if _type == "bet":
            if not db.new_bet(self.data):
                ErrorWindow("Wager can't be more than Bankroll")
                self.clear()
                return

        elif _type == "parley":
            separate_parley(self.data)
            db.open_parley(self.data)

        self.clear()


class ErrorWindow:
    """Display a custom error message in a new window. Main window is locked until the error is closed."""

    def __init__(self, message):

        win = tk.Toplevel()
        win.title("Error")
        label = tk.Label(win, text=message, bg="red")
        button = tk.Button(win, text="Okay", command=lambda: [win.grab_release(), win.destroy()], bg="green", bd='5')
        label.pack()
        button.pack()
        win.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    make_db()
    app = App(master=root)
    root.title("Bet Tracker")
    root.geometry("1000x500")
    app.mainloop()

# todo:
#  * close bet/close parley
#  * Math tab w/ imp prob, covert, to_make
#  * exit button --Refractor so it doesn't have to be called everytime
#  * logo (remove or make?)
#  * Add a delete option
#  * Add a push
#  * Win-loss-push + total money up
