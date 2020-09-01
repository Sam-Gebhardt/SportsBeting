"""
Program to help keep track of sports betting.
Items to keep track of: Bet, Odds, Amount, Payout, Outcome
"""

import sqlite3
from datetime import date

conn = sqlite3.connect('bets.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS open_bets (type text, matchup text, bet_on text, odds text, 
            wager int, to_win int, date text)""")
    
c.execute("""CREATE TABLE IF NOT EXISTS closed_bets (type text, matchup text, bet_on text, odds text, 
            wager int, to_win int, outcome text, change int, date text)""")
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

    c.execute("""INSERT INTO open_bets (type, matchup, bet_on, odds, wager, to_win, date) VALUES
    (?, ?, ?, ?, ?, ?, ?) """, (type_, matchup, bet_on, odds, wager, to_win, when))

    conn.commit()
    conn.close()


def view_open_bets():
    """Look at open bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM open_bets""")
    open = c.fetchall()

    for i in open:
        print(i)

    conn.commit()
    conn.close()


def view_closed_bets():

    conn = sqlite3.connect('bets.db')
    c = conn.cursor() 

    c.execute("""SELECT * FROM closed_bets""")
    open = c.fetchall()

    for i in open:
        print(i)

    conn.commit()
    conn.close()

# new_bet()
view_open_bets()


def main():

    return


if __name__ == "__main__":
    main()
    