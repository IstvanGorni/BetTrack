class Bet:
    def __init__(self, event, date, odds, stake, bet_type, outcome, sport, league, result, notes, confidence_scale):
        self.event = event
        self.date = date
        self.odds = float(odds)
        self.stake = float(stake)
        self.bet_type = bet_type
        self.outcome = outcome
        self.sport = sport
        self.league = league
        self.result = result
        self.notes = notes
        self.confidence_scale = int(confidence_scale)
        self.balance = self.calculate_balance()

    def calculate_balance(self):
        outcome = self.outcome.strip().lower()
        if outcome == "lost" or outcome == "lose":
            return -self.stake
        elif outcome == "won" or outcome == "win":
            return round(self.stake * (self.odds - 1), 2)
        else:
            return 0

    def __repr__(self):
        return f"<Bet {self.event} ({self.date})>"