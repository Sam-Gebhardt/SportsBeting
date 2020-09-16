"""
Program to help keep track of sports betting.
Items to keep track of: Bet, Odds, Amount, Payout, Outcome
"""

import sqlite3
from datetime import date
from os import path


def initialize():
    if not path.isfile("bets.db"):
        """Check if db exists, creates it if not"""

        conn = sqlite3.connect('bets.db')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS open_bets (sport text, type text, matchup text, bet_on text, odds text, 
                    wager real, to_win real, date text)""")

        c.execute("""CREATE TABLE IF NOT EXISTS closed_bets (sport text, type text, matchup text, bet_on text, 
                    odds text, wager real, to_win real, outcome text, change real, date text)""")

        c.execute("""CREATE TABLE IF NOT EXISTS open_parley (sport text, bet1 text, bet2 text, bet3 text, bet4 text, 
                    bet5 text, bet6 text, bet7 text, bet8 text, bet9 text, bet10 text, wager real, odds text,
                     to_win real, date text)""")

        c.execute("""CREATE TABLE IF NOT EXISTS closed_parley (sport text, bet1 text, bet2 text, bet3 text, bet4 text, 
                bet5 text, bet6 text, bet7 text, bet8 text, bet9 text, bet10 text, wager real, odds text,
                    to_win real, change real, date text)""")
        # only supports 10 team parley

        c.execute("""CREATE TABLE IF NOT EXISTS bankroll (date char, amount real)""")

        bank = input("Enter starting bankroll: ")
        c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", (date.today(), bank))
        c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Master", bank))
        c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Starting", 0))

        conn.commit()
        conn.close()


"""
Table contents

type: spread, ml, prop, custom
matchup: Teams playing
bet_on: winning outcome
odds: American
wager: Amount put on bet
to_win: Amount won if bet hits
*outcome: Did the bet win or lose?
*change: change in money
date: when it was placed
* = closed only

ex:
Say for Seahawks vs Falcons I bet $5 on the Seahawks ML(-125), then the table entry would be:

ML, Seahawks vs Falcons, Seahawks ML, -125, 5, 4, W, 9

If I bet on the spread:

spread, Seahawks vs Falcons, Seahawks -1.0, -115, 5, 4.35, L, 0
"""


def bankroll_amount():
    """Return the amount of money in bankroll"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT (amount) FROM bankroll WHERE date = ? """, ("Master",))
    current = c.fetchall()[0][0]

    c.execute("""SELECT (amount) FROM bankroll WHERE date = ? """, ("Starting",))
    change = c.fetchall()[0][0]

    # c.execute("""SELECT SUM(wager) FROM open_bets""")
    # open_sum = c.fetchall()[0][0]
    # if open_sum:
        # change += open_sum

    conn.close()

    return current, change


def bankroll_history(master_amount: int):
    """Keeps track of the changes in bankroll over time"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM bankroll WHERE date = ?""", (date.today(),))
    bank = c.fetchall()

    if len(bank) == 0:
        c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", (date.today(), master_amount))
    else:
        c.execute("""UPDATE bankroll SET amount = ? WHERE date = ?""", (master_amount, date.today()))

    c.execute("""UPDATE bankroll SET amount = ? WHERE date = ?""", (master_amount, "Master"))

    conn.commit()
    conn.close()


def bankroll_update(change: float, wager=0, add=False):
    """Add or subtract from bankroll"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM bankroll WHERE date = ?""", ("Master",))
    bank = c.fetchall()[0][1]

    if not add:
        c.execute("""UPDATE bankroll SET amount = amount - ? WHERE date = ?""", (change, "Starting"))

    else:
        bank += change + wager
        c.execute("""UPDATE bankroll SET amount = amount + ? WHERE date = ?""", (change, "Starting"))

    conn.commit()  # todo add orignal wager, money won as args
    conn.close()

    bankroll_history(bank)


def calc_odds(odds: int, wager: float):
    """Turn American odds into $$"""

    if odds >= 100:
        to_win = wager * (odds / 100)
    else:
        to_win = (wager / abs(odds)) * 100

    to_win = round(to_win, 2)
    return to_win


def new_bet():
    """Get info for new bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    sport = input("Which sport: ")
    matchup = input("Which teams are playing: ")
    type_ = input("What type of bet is it: ")
    bet_on = input("What did you bet on: ")
    wager = input("Wager: ")
    odds = input("Odds: ")

    odds = int(odds)
    wager = float(wager)

    to_win = calc_odds(odds, wager)
    when = date.today()

    c.execute("""SELECT amount FROM bankroll WHERE date = ?""", ("Master", ))
    bankroll = c.fetchall()[0][0]

    if (bankroll - wager) < 0:
        print("The bet is more than the bankroll. Aborting")
        return

    c.execute("""UPDATE bankroll SET amount = amount - ? WHERE date = ?""", (wager, "Master", ))

    c.execute("""INSERT INTO open_bets (sport, type, matchup, bet_on, odds, wager, to_win, date) VALUES
    (?, ?, ?, ?, ?, ?, ?, ?) """, (sport, type_, matchup, bet_on, odds, wager, to_win, when))

    conn.commit()
    conn.close()


def view_open_bets():
    """Look at open bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM open_bets""")
    open_bets = c.fetchall()

    for i in open_bets:
        print(i)

    c.execute("""SELECT * FROM open_parley""")
    open_p = c.fetchall()

    for i in open_p:
        print(i)

    conn.close()


def view_closed_bets():
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM closed_bets""")
    closed_bets = c.fetchall()

    for i in closed_bets:
        print(i)

    c.execute("""SELECT * FROM closed_parley""")
    closed_p = c.fetchall()

    for i in closed_p:
        print(i)

    conn.close()


def close_bet():
    """Move an open bet to closed_bet table"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM open_bets""")
    open_bets = c.fetchall()

    for i, bet in enumerate(open_bets):
        print(f"{i}: {bet}")

    close = input("To close: ")

    for j in close:
        try:
            j = int(j)
        except ValueError:
            continue

        while True:

            outcome = input(f"W/L bet #{j}: ")
            outcome.lower()
            if outcome == "w" or outcome == "l":
                break

        amount = 0
        # default is 0 because wager is already removed from bank roll
        if outcome == "w":
            amount = float(open_bets[j][4]) + float(open_bets[j][5])
            amount = round(amount, 2)
            # amount = wager + to_win

        c.execute("""INSERT INTO closed_bets (sport, type, matchup, bet_on, odds, wager, 
        to_win, outcome, change, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (open_bets[j][0], open_bets[j][1], open_bets[j][2], open_bets[j][3], open_bets[j][4],
                   open_bets[j][5], open_bets[j][6], outcome, amount, open_bets[j][7],))

        c.execute("""DELETE FROM open_bets WHERE sport = ? AND matchup = ? AND bet_on = ?""",
                  (open_bets[j][0], open_bets[j][2], open_bets[j][3]))

        conn.commit()
        if outcome == "w":  # if won, then add to_win else subtract wager
            bankroll_update(open_bets[j][6], wager=open_bets[j][5], add=True)
        else:
            bankroll_update(open_bets[j][5])

        print(f"Bet #{j} closed")

    conn.close()


def open_parley():
    """Open a parley bet"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    n = input("How many bets in the parley: ")
    bets = []
    for i in range(1, int(n) + 1):
        bets.append(input(f"Bet #{i}: "))

    for i in range(10):
        if i + 1 > len(bets):
            bets.append("NULL")

    sport = input("Sport: ")
    odds = input("Odds: ")
    wager = input("Wager: ")

    to_win = calc_odds(int(odds), float(wager))

    c.execute("""INSERT INTO open_parley (sport, bet1, bet2, bet3, bet4, bet5, bet6, bet7, bet8, bet9, bet10, 
    wager, odds, to_win, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (sport, bets[0], bets[1],
                                                                                         bets[2], bets[3], bets[4],
                                                                                         bets[5], bets[6], bets[7],
                                                                                         bets[8], bets[9], wager, odds,
                                                                                         to_win, date.today(),))

    conn.commit()
    conn.close()


def close_parley():
    """Close a parley bet"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM open_parley""")
    par = c.fetchall()

    cleansed = []
    for bet in par:
        new = []
        for item in bet:
            if item != "NULL":
                new.append(item)
        cleansed.append(new)

    conn.commit()
    conn.close()


def delete_bet():
    """Delete a bet"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    remove = input("Remove open or closed bet: ")
    query = f"""SELECT * FROM {remove}_bets"""
    c.execute(query)
    bets = c.fetchall()

    for i, j in enumerate(bets):
        print(f"{i}: {j}")

    to_close = input("Enter bets to delete: ")
    nums = to_close.split(",")
    for i in nums:
        i = int(i.strip())
        c.execute(f"""DELETE FROM {remove}_bets WHERE date = ? AND matchup = ? AND odds = ?""",
                  (bets[i][6], bets[i][1], bets[i][3]))

    print(f"Removed: {to_close}")

    conn.commit()
    conn.close()


def custom_search():
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    search = input("Search by and value: ")
    search = search.split(",")

    for i in range(len(search)):
        search[i] = search[i].strip()

    query = f"""SELECT * FROM open_bets WHERE ({search[0]} = ?)"""  # Use for loop to make multi-var custom search
    c.execute(query, (search[1],))
    results = c.fetchall()

    for bet in results:
        print(bet)

    conn.close()


def main():

    todo = input("Todo: ")
    if todo == "open":
        new_bet()

    elif todo == "close":
        close_bet()

    elif todo == "view":
        open_close = input("open or closed: ")
        if open_close == "open":
            view_open_bets()
        else:
            view_closed_bets()

    elif todo == "search":
        custom_search()

    elif todo == "delete":
        delete_bet()

    elif todo == "bank":
        choice = input("Add or view: ")
        if choice == "view":
            print(f"Current: {bankroll_amount()[0]}\nChange: {bankroll_amount()[1]}")
        else:
            n = int(input("Amount: "))
            bankroll_update(n, add=True)
            print(f"New Bankroll: {bankroll_amount()[0]}")

    elif todo == "q":
        return

    elif todo == "parley":
        open_parley()

    print("")
    main()


if __name__ == "__main__":
    initialize()
    main()


# todo close/w: bank is correct, but change stays the same
# todo close/l: bank stays the same, but change decrease by the wager * 2
