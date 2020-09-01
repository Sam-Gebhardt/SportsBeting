"""
Program to help keep track of sports betting.
Items to keep track of: Bet, Odds, Amount, Payout, Outcome
"""

import sqlite3

conn = sqlite3.connect('bets.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS open_bets (type text, bet_on text, bet_against text, odds text, 
            wager int, to_win int, outcome text, change int, date text)""")
    
c.execute("""CREATE TABLE IF NOT EXISTS closed_bets (type text, bet_on text, bet_against text, odds text, 
            wager int, to_win int, outcome text, change int, date text)""")
"""
Table contents

type: spread, ml, prop, custom
bet_on: winning outcome
bet_againts: losing outcome 
bet_info: the specific spread/prop/ML
odds: American
wager: Amount put on bet
to_win: Amount won if bet hits
outcome: Did the bet win or lose?
change: change in money
date: when it was placed

ex:
Say for Seahawks vs Falcons I bet $5 on the Seahawks ML(-125), then the table entry would be:

ml, Seahawks, Falcons, -125, -125, 5, 4, W, 9

If I bet on the spread:

spread, Seahawks, Falcons, -1.0, -115, 5, 4.35, L, 0
"""

def new_bet():
    """Get info for new bets"""

    print("What did you bet on? \n1: ML \n2: Spread \n3: Prop \n4: Other")
    bet_type = input("")
    bet_on = input("What did you bet on?")
    bet_aginst = input("Bet against?")


new_bet()