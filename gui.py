import tkinter as tk


def out():
    print("Testing")


class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.logo()
        # self.master.after(3000, self.start_page())
        self.menu()
        self.start_page()

    def start_page(self):
        btn = tk.Button(root, text='Click me !', bd='5', command=self.master.destroy)
        btn.pack()

    def menu(self):
        menu_bar = tk.Menu(self.master)

        _open = tk.Menu(menu_bar, tearoff=0)
        _open.add_command(label="Bet", command=None)
        _open.add_command(label="Parley")
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
        label.pack()
        canvas.create_image(20, 20, anchor="nw", image=img)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    root.title("Bet Tracker")
    app.mainloop()
