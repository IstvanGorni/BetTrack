from datetime import datetime
import uuid


class Bet:
    def __init__(
        self,
        event,
        date,
        odds,
        stake,
        bet_type,
        outcome,
        sport,
        league,
        result="",
        notes="",
        confidence_scale=8,
        total_bets=1,
        created_at=None,
        id=None
    ):
        self.id = id if id is not None else str(uuid.uuid4())
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
        self.total_bets = int(total_bets)

        # timestamp
        self.created_at = created_at or datetime.now().isoformat()

        # ✅ DEFAULT confidence_scale = 8
        try:
            self.confidence_scale = int(confidence_scale)
        except (ValueError, TypeError):
            self.confidence_scale = 8

        # ✅ DEFAULT total_bets = 1
        try:
            self.total_bets = int(total_bets)
        except (ValueError, TypeError):
            self.total_bets = 1

        self.balance = self.calculate_balance()

    def calculate_balance(self):
        outcome = self.outcome.strip().lower()
        if outcome in ["lost", "lose"]:
            return -self.stake
        elif outcome in ["won", "win"]:
            return round(self.stake * (self.odds - 1), 2)
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "event": self.event,
            "date": self.date,
            "odds": self.odds,
            "stake": self.stake,
            "bet_type": self.bet_type,
            "outcome": self.outcome,
            "sport": self.sport,
            "league": self.league,
            "result": self.result,
            "notes": self.notes,
            "confidence_scale": self.confidence_scale,
            "total_bets": self.total_bets,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<Bet {self.event} ({self.date})>"
