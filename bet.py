"""
Program to help keep track of sports betting.
Items to keep track of: Bet, Odds, Amount, Payout, Outcome
"""

import sqlite3
from datetime import date
from os import path


if not path.isfile("bets.db"):
    """Check if db exsists, creates it if not"""
    
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS open_bets (type text, matchup text, bet_on text, odds text, 
                wager int, to_win int, date text)""")
        
    c.execute("""CREATE TABLE IF NOT EXISTS closed_bets (type text, matchup text, bet_on text, odds text, 
                wager int, to_win int, outcome text, change int, date text)""")

    c.execute("""CREATE TABLE IF NOT EXISTS bankroll (date char, amount int)""")

    bank = input("Enter starting bankroll: ")
    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", (date.today(), bank))
    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Master", bank))

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

    c.execute("""SELECT (amount) FROM bankroll WHERE date = ? """, ("Master", ))
    bank = c.fetchall()[0][0]

    conn.commit()
    conn.close()

    return bank

def bankroll_history(master_amount: int, c, conn):
    """Keeps track of the changes in bankroll over time"""


    c.execute("""SELECT * FROM bankroll WHERE date = ?""", (date.today(), ))
    bank = c.fetchall()

    if len(bank) == 0:
        c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", (date.today(), master_amount))
        return
    
    c.execute("""UPDATE bankroll set amount = ? WHERE date = ?""", (master_amount, "Master"))



def bankroll_remove(amount: int):
    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM bankroll WHERE date = ?""", ("Master", ))
    bank = c.fetchall()[0][1]

    bank -= amount
    if bank < 0:
        print("Your bet is more than bankroll. Aborting")
        return False

    bankroll_history(bank, c, conn)
    # c.execute("""UPDATE bankroll SET amount = ? WHERE date = ? """, (bank, "Master"))
    
    conn.commit()
    conn.close()

    return True

def bankroll_add(amount: int):
    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM bankroll""")
    bank = c.fetchall()[0][1]

    bank += amount
    bankroll_history(bank, c, conn)
    # c.execute("""UPDATE bankroll SET amount = ? WHERE date = ?""", (bank, "Master" ))
    
    conn.commit()
    conn.close()

    return bank


def new_bet():
    """Get info for new bets"""
    
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()   

    matchup = input("Which teams are playing: ")
    type_ = input("What type of bet is it: ")
    bet_on = input("What did you bet on: ")
    odds = input("Odds: ")
    wager = input("Wager: ")

    odds = int(odds)
    wager = int(wager)

    if odds >= 100:
        to_win = wager * (odds / 100)
    else:
        to_win = (wager / abs(odds)) * 100

    to_win = round(to_win, 2)
    when = date.today()
    if bankroll_remove(wager):

        c.execute("""INSERT INTO open_bets (type, matchup, bet_on, odds, wager, to_win, date) VALUES
        (?, ?, ?, ?, ?, ?, ?) """, (type_, matchup, bet_on, odds, wager, to_win, when))
    
    conn.commit()
    conn.close()

    print("")
    main()


def view_open_bets():
    """Look at open bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM open_bets""")
    open_bets = c.fetchall()

    for i in open_bets:
        print(i)

    conn.commit()
    conn.close()


def view_closed_bets():

    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM closed_bets""")
    open_bets = c.fetchall()

    for i in open_bets:
        print(i)

    conn.commit()
    conn.close()

    print("")
    main()


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

        while(True):

            outcome = input(f"W/L bet #{j}: ")
            outcome.lower()
            if outcome == "w" or outcome == "l":
                break
        
        change = 0
        # default is 0 because wager is already removed from bank roll
        if outcome == "w":
            change = open_bets[j][4] + open_bets[j][5]
            # change = wager + to_win
        
        c.execute("""INSERT INTO closed_bets (type, matchup, bet_on, odds, wager, 
        to_win, outcome, change, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""" ,
        (open_bets[j][0], open_bets[j][1], open_bets[j][2], open_bets[j][3], 
        open_bets[j][4], open_bets[j][5], outcome, change, open_bets[j][6]))

        # c.execute("""DELETE)

        print(f"Bet #{j} closed")
       
    conn.commit()
    conn.close()

    print("")
    main()


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
        i = i.strip()
        c.execute(f"""DELETE FROM {remove}_bets WHERE date = ? AND matchup = ? AND odds = ?""", 
        (bets[0][6], bets[0][1], bets[0][3]))
    
    print(f"Removed: {to_close}")

    conn.commit()
    conn.close()

    print("")
    main()

def custom_search():

    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    search = input("Search by and value: ")
    search = search.split(",")

    for i in range(len(search)):
        search[i] = search[i].strip()

    query = f"""SELECT * FROM open_bets WHERE ({search[0]} = ?)""" # Use for loop to make mulit-var custom search
    c.execute(query, (search[1], ))
    results = c.fetchall()

    for bet in results:
        print(bet)
    
    conn.commit()
    conn.close()

    print("")
    main()


# custom_search()

def main():

    todo = input("Todo: ")
    if todo == "open":
        new_bet();

    elif todo ==  "close":
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
            print(bankroll_amount())
        else:
            total = bankroll_add(int(input("Amount: ")))
            print(f"New Bankroll: {total}")

        print("")

        main()

    elif todo == "q":
        return

    else:  # not an option, try again
        main()


if __name__ == "__main__":
    main()
# main
