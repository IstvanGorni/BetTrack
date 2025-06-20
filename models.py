import uuid

class Bet:
    def __init__(self, id, event, date, odds, stake, bet_type, outcome, sport, league, result, notes, confidence_scale):
        self.id = id  # ÚJ
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
        if outcome in ["lost", "lose"]:
            return -self.stake
        elif outcome in ["won", "win"]:
            return round(self.stake * (self.odds - 1), 2)
        else:
            return 0

    def to_dict(self):
        return {
            'id': self.id,
            'event': self.event,
            'date': self.date,
            'odds': self.odds,
            'stake': self.stake,
            'bet_type': self.bet_type,
            'outcome': self.outcome,
            'sport': self.sport,
            'league': self.league,
            'result': self.result,
            'notes': self.notes,
            'confidence_scale': self.confidence_scale
        }

    def __repr__(self):
        return f"<Bet {self.event} ({self.date})>"
