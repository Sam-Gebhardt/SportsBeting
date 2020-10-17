"""
Program to help keep track of sports betting.
Items to keep track of: Bet, Odds, Amount, Payout, Outcome
"""

import sqlite3
from datetime import date

from typing import List


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
                 to_win real, outcome text, change real, date text)""")
    # only supports 10 team parley

    c.execute("""CREATE TABLE IF NOT EXISTS bankroll (date char, amount real)""")

    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", (date.today(), bank))
    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Master", bank))
    c.execute("""INSERT INTO bankroll (date, amount) VALUES (?, ?)""", ("Winnings", 0))

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


def bankroll_amount() -> tuple:
    """Return the amount of money in bankroll"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT (amount) FROM bankroll WHERE date = ? """, ("Master",))
    current = c.fetchall()[0][0]

    c.execute("""SELECT (amount) FROM bankroll WHERE date = ? """, ("Winnings",))
    change = c.fetchall()[0][0]

    conn.close()
    current = round(current, 2)
    change = round(change, 2)

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


def bankroll_add(amount: float) -> None:
    """Add money to the bank"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""UPDATE bankroll SET amount = amount + ? WHERE date = ?""", (amount, "Master"))

    conn.commit()
    conn.close()


def view_bank() -> list:
    """Return bankroll history as a list"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM bankroll WHERE date != ? AND date != ?""", ("Master", "Winnings", ))
    bank = c.fetchall()
    conn.close()

    return bank


def new_bet(data: dict) -> bool:
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
    bankroll_history(bankroll - data["Wager"])
    return True


def close_bet(to_close: list):
    """Move an open bet to closed_bet table"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    outcome = to_close.pop()
    for bet in to_close:
        amount = bet[5] * -1
        # lost on the bet == wager
        if outcome == "W":
            amount = float(bet[5]) + float(bet[6])
            amount = round(amount, 2)
            # amount = wager + to_win
        elif outcome == "P":
            amount = bet[5]

        c.execute("""INSERT INTO closed_bets (sport, type, matchup, bet_on, odds, wager, 
                  to_win, outcome, change, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (bet[0], bet[1], bet[2], bet[3], bet[4], bet[5], bet[6], outcome, amount, bet[7],))

        c.execute("""DELETE FROM open_bets WHERE sport = ? AND type = ? AND matchup = ? AND bet_on = ?
                  AND odds = ? AND wager = ? AND to_win = ?""",
                  (bet[0], bet[1], bet[2], bet[3], bet[4], bet[5], bet[6]))

        c.execute("""UPDATE bankroll SET amount = amount + ? WHERE date = ?""", (amount, "Master"))
        conn.commit()

        c.execute("""SELECT amount FROM bankroll WHERE date = ?""", ("Master",))
        total = c.fetchall()[0][0]
        bankroll_history(total)

    conn.close()


def view_open_bets() -> list:
    """Look at open bets"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM open_bets""")
    open_bets = c.fetchall()

    c.execute("""SELECT * FROM open_parley""")
    open_parleys = c.fetchall()
    conn.close()

    for bet in open_parleys:
        bet = list(bet)
        while "NULL" in bet:
            bet.remove("NULL")

        open_bets.append(bet)

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


def view_open_parley() -> list:
    """View open parleys. Returns a string version to display and a list version for interfacing with the db"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM open_parley""")
    open_parleys = c.fetchall()

    return open_parleys


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


def close_parley(to_close: list) -> None:
    """Close a parley bet"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    outcome = to_close.pop()
    for bet in to_close:
        amount = bet[11] * -1
        # lost on the bet == wager
        if outcome == "W":
            amount = float(bet[11]) + float(bet[12])
            amount = round(amount, 2)
            # amount = wager + to_win
        elif outcome == "P":
            amount = bet[11]

        c.execute("""INSERT INTO closed_parley (sport, bet1, bet2, bet3, bet4, bet5, bet6, bet7, bet8, bet9, bet10, 
                     wager, odds, to_win, outcome, change, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?)""",
                  (bet[0], bet[1], bet[2], bet[3], bet[4], bet[5], bet[6], bet[7], bet[8], bet[9], bet[10],
                   bet[11], bet[12], bet[13], outcome, amount, bet[14]))

        c.execute("""DELETE FROM open_parley WHERE sport = ? AND bet1 = ? AND, bet2 = ? AND, bet3 = ? 
                     AND bet4 = ? AND bet5 = ? AND bet6 = ? AND bet7 = ? AND bet8 = ? AND bet9 = ? 
                     AND bet10 = ? AND wager = ? AND odds = ? AND to_win = ?""",
                  (bet[0], bet[1], bet[2], bet[3], bet[4], bet[5], bet[6], bet[7], bet[8], bet[9], bet[10],
                   bet[11], bet[12], bet[13]))

        c.execute("""UPDATE bankroll SET amount = amount + ? WHERE date = ?""", (amount, "Master"))
        conn.commit()

        c.execute("""SELECT amount FROM bankroll WHERE date = ?""", ("Master",))
        total = c.fetchall()[0][0]
        bankroll_history(total)

    conn.commit()
    conn.close()


def delete_bet(remove) -> None:
    """Delete a bet"""

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    if type(remove) == tuple:  # in the case only 1 bet is deleted
        remove = [remove]

    for entry in remove:
        for i in entry:
            if len(entry) == 8:
                c.execute(f"""DELETE FROM closed_bets WHERE sport = ? AND type = ? AND matchup = ? AND bet_on = ? AND 
                              odds = ? AND wager = ? AND to_win = ? AND date = ?""",
                          (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]))
            else:
                c.execute("""DELETE FROM closed_bets WHERE sport = ? AND type = ? AND matchup = ? AND bet_on = ? AND 
                             odds = ? AND wager = ? AND to_win = ? AND outcome = ? AND change = ? date = ?""",
                          (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9]))

    conn.commit()
    conn.close()


def custom_search(data: dict) -> list:
    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    query = f"""SELECT * FROM open_bets WHERE sport LIKE '%{data["Sport"]}%' AND type LIKE '%{data["Type"]}%' AND
    matchup LIKE '%{data["Matchup"]}%' AND bet_on LIKE '%{data["Bet"]}%' AND odds LIKE '%{data["Odds"]}%' AND
    wager LIKE '%{data["Wager"]}%'"""
    # Match any similar results and if the category is left blank it matches everything

    c.execute(query)
    results = c.fetchall()

    query2 = f"""SELECT * FROM closed_bets WHERE sport LIKE '%{data["Sport"]}%' AND type LIKE '%{data["Type"]}%' AND
    matchup LIKE '%{data["Matchup"]}%' AND bet_on LIKE '%{data["Bet"]}%' AND odds LIKE '%{data["Odds"]}%' AND
    wager LIKE '%{data["Wager"]}%'"""

    c.execute(query2)
    results2 = c.fetchall()
    conn.close()

    results += results2
    return results


def record() -> str:

    conn = sqlite3.connect('bets.db')
    c = conn.cursor()

    c.execute("""SELECT * FROM closed_bets""")
    data = c.fetchall()

    win, loss, push = 0, 0, 0
    for bet in data:
        if bet[7] == "W":
            win += 1
        elif bet[7] == "L":
            loss += 1
        elif bet[7] == "P":
            push += 1

    record_str = f"{win}-{loss}-{push}"
    return record_str


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


def stringify(results: List[tuple]) -> List[str]:

    str_results = []
    for i in range(len(results)):
        str_version = ""
        for j in results[i]:
            if type(j) == float:
                j = round(j, 2)

            if j == "NULL":
                continue

            str_version = str_version + " " + str(j)
        str_results.append(str_version)

    return str_results


# todo:
#  * general cleanup
