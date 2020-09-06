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

    c.execute("""CREATE TABLE IF NOT EXISTS bankroll (amount int)""")

    bank = input("Enter starting bankroll: ")
    c.execute("""INSERT INTO bankroll (amount, ) VALUES (?, )""", (bank, ))

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


def bankroll_remove(amount: int):
    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM bankroll""")
    bank = c.fetchall()[0][0]

    bank -= amount
    if bank < 0:
        print("Your bet is more than bankroll. Aborting")
        return False

    c.execute("""UPDATE bankroll SET amount = ? """, (bank, ))
    
    conn.commit()
    conn.close()

    return True

def bankroll_add(amount: int):
    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM bankroll""")
    bank = c.fetchall()[0][0]

    bank += amount
    c.execute("""UPDATE bankroll SET amount = ? """, (bank, ))
    
    conn.commit()
    conn.close()


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


def close_bet():
    """Move an open bet to closed_bet table"""

    # make custom search

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

        print(f"Bet #{j} closed")
       
    conn.commit()
    conn.close()


def main():

    return


if __name__ == "__main__":
    main()
