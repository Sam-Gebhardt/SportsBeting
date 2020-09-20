import tkinter as tk

# todo: make functions for testing, but cut them out and
#  alter functions in bet.py to take a dict as an arg


def out():
    print("Testing")


# def reset_data(data:dict):


def confirm(data: dict):
    """Store given data in the db"""
    for i in data:
        data[i] = data[i].get()
        print(data[i])

    try:
        int(data["Wager"])
        int(data["Odds"])

    except ValueError:
        print("no")
        # return False
    # data.clear()


def confirm_parley(data: dict):

    for i in data:
        if i == "Matchup":
            separated = data.get(i).get().split(";")
            for j in separated:
                j = j.strip()
                if j:
                    print(j)
        else:
            print(data.get(i).get())


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

        # self.logo()
        self.menu()
        self.start_page()
        # self.input_box()

    def start_page(self):
        btn = tk.Button(self.master, text='Exit', bd='5', command=self.master.destroy, bg="red")
        btn.grid(row=3, column=2, pady=10)

    def menu(self):
        menu_bar = tk.Menu(self.master)

        _open = tk.Menu(menu_bar, tearoff=0)
        _open.add_command(label="Bet", command=self.open_bet_menu)
        _open.add_command(label="Parley", command=self.open_parley_menu)
        menu_bar.add_cascade(label="Open", menu=_open)

        _close = tk.Menu(menu_bar, tearoff=0)
        _close.add_command(label="Bet")
        _close.add_command(label="Parley")
        menu_bar.add_cascade(label="Close", menu=_close)

        view = tk.Menu(menu_bar, tearoff=0)
        view.add_command(label="Open", command=out)
        view.add_command(label="Closed")
        view.add_command(label="All")
        view.add_command(label="Search")
        menu_bar.add_cascade(label="View", menu=view)

        bank = tk.Menu(menu_bar, tearoff=0)
        bank.add_command(label="History")
        menu_bar.add_cascade(label="Bank", menu=bank)

        self.master.config(menu=menu_bar)

    def logo(self):

        canvas = tk.Canvas(self.master, width=300, height=300, bg="green")

        img = tk.PhotoImage(file="m1.png")
        label = tk.Label(image=img)
        label.image = img  # must keep a reference of the image
        label.grid()
        canvas.create_image(20, 20, anchor="nw", image=img)

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

        self.sport_input.grid(row=1, column=2)
        self.label_sport.grid(row=2, column=2)

        self._type_input.grid(row=1, column=3)
        self.label_type.grid(row=2, column=3)

        self.match_input.grid(row=1, column=4)
        self.label_matchup.grid(row=2, column=4)

        self.bet_on_input.grid(row=1, column=5, pady=30)
        self.label_bet_on.grid(row=2, column=5)

        self.odds_input.grid(row=1, column=6)
        self.label_odds.grid(row=2, column=6)

        self.wager_input.grid(row=1, column=7)
        self.label_wager.grid(row=2, column=7)

        button = tk.Button(self.master, text="Confirm", command=lambda: confirm(self.data), bd='5', bg="green")
        button.grid(row=3, column=4, pady=3)

    def open_parley_menu(self):
        self.label_sport = tk.Label(self.master, text="Sport")
        self.label_matchup = tk.Label(self.master, text="Matchup(s) separated by a ';'")
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

        self.odds_input.grid(row=1, column=6)
        self.label_odds.grid(row=2, column=6)

        self.wager_input.grid(row=1, column=7)
        self.label_wager.grid(row=2, column=7)

        button = tk.Button(self.master, text="Confirm", command=lambda: confirm_parley(self.data), bd='5', bg="green")
        button.grid(row=3, column=4, pady=3)

    def confirm(self):
        """"""


if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    root.title("Bet Tracker")
    root.geometry("1000x500")
    app.mainloop()
