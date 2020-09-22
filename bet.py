"""
Program to help keep track of sports betting.
Items to keep track of: Bet, Odds, Amount, Payout, Outcome
"""

import sqlite3
from datetime import date


def initialize(bank: float):

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

    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", (date.today(), bank))
    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Master", bank))
    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Starting", 0))

    conn.commit()
    conn.close()


"""
Table contents

sport: sport
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

    conn.commit()
    conn.close()

    bankroll_history(bank)


def calc_odds(odds: int, wager: float) -> float:
    """Turn American odds into $$"""

    if odds >= 100:
        to_win = wager * (odds / 100)
    else:
        to_win = (wager / abs(odds)) * 100

    to_win = round(to_win, 2)
    return to_win


def implied_prob(odds: int) -> float:
    """Turn odds into the applied probability of the event occurring"""

    if odds < 0:
        odds = abs(odds)
        prob = (odds / (odds + 100)) * 100
    else:
        prob = (100 / (odds + 100)) * 100

    return round(prob, 2)


def covert_decimal(odds: int) -> float:
    """Covert american odds to decimal """

    if odds > 0:
        decimal = odds / 100
    else:
        decimal = 100 / abs(odds)

    return decimal


def new_bet(data: dict):
    """Get info for new bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    to_win = calc_odds(data["Odds"], data["Wager"])
    when = date.today()

    c.execute("""SELECT amount FROM bankroll WHERE date = ?""", ("Master", ))
    bankroll = c.fetchall()[0][0]

    if (bankroll - data["Wager"]) < 0:
        conn.close()
        return False

    c.execute("""UPDATE bankroll SET amount = amount - ? WHERE date = ?""", (data["Wager"], "Master", ))

    c.execute("""INSERT INTO open_bets (sport, type, matchup, bet_on, odds, wager, to_win, date) VALUES
    (?, ?, ?, ?, ?, ?, ?, ?) """, (data["Sport"], data["Type"], data["Matchup"], data["Bet"], data["Odds"],
                                   data["Wager"], to_win, when))

    conn.commit()
    conn.close()


def view_open_bets() -> list:
    """Look at open bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM open_bets""")
    open_bets = c.fetchall()

    c.execute("""SELECT * FROM open_parley""")
    open_parleys = c.fetchall()

    for bet in open_parleys:
        bet = list(bet)
        while "NULL" in bet:
            bet.remove("NULL")

        open_bets.append(bet)
    conn.close()

    return open_bets


def view_closed_bets() -> list:  # todo combine this/view_open_bets()
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM closed_bets""")
    closed_bets = c.fetchall()

    c.execute("""SELECT * FROM closed_parley""")
    closed_p = c.fetchall()

    for bet in closed_p:
        bet = list(bet)
        while "NULL" in bet:
            bet.remove("NULL")

        closed_bets.append(bet)

    conn.close()

    return closed_bets


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
            outcome = outcome.lower()
            if outcome == "w" or outcome == "l":
                break

        amount = open_bets[j][4] * -1
        # lost on the bet == wager
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


def open_parley(data: dict):
    """Open a parley bet"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    for i in range(1, 11):
        bet_str = f"bet{i}"
        data.setdefault(bet_str, "NULL")

    to_win = calc_odds(int(data["Odds"]), float(data["Wager"]))

    c.execute("""INSERT INTO open_parley (sport, bet1, bet2, bet3, bet4, bet5, bet6, bet7, bet8, bet9, bet10, 
               wager, odds, to_win, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (data["Sport"], data["bet1"], data["bet2"], data["bet3"], data["bet4"], data["bet5"], data["bet6"],
               data["bet7"], data["bet8"], data["bet9"], data["bet10"], data["Wager"], data["Odds"],
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


def custom_search(data: dict) -> list:
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    query = f"""SELECT * FROM open_bets WHERE sport LIKE '%{data["Sport"]}%' AND type LIKE '%{data["Type"]}%'
    matchup LIKE '%{data["Matchup"]}%' AND bet_on LIKE '%{data["Bet"]}%' AND odds LIKE '%{data["Odds"]}%' AND
    wager LIKE '%{data["Wager"]}%' AND to_win LIKE '%{data["to_win"]}%' AND date LIKE '%{data["Date"]}%')"""
    # Match any similar results and if the category is left blank it matches everything

    c.execute(query)
    results = c.fetchall()

    conn.close()
    return results
