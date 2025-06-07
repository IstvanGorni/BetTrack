import csv
from models import Bet
import os

class DataManager:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.bets = self.load_bets()

    def load_bets(self):
        bets = []
        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bet = Bet(
                    event=row['event'],
                    date=row['date'],
                    odds=row['odds'],
                    stake=row['stake'],
                    bet_type=row['bet_type'],
                    outcome=row['outcome'],
                    sport=row['sport'],
                    league=row['league'],
                    result=row['result'],
                    notes=row['notes'],
                    confidence_scale=row['confidence_scale']
                )
                bets.append(bet)
        return bets

    def add_bet(self, bet):
        file_exists = os.path.isfile(self.csv_path)
        is_empty = os.stat(self.csv_path).st_size == 0

        with open(self.csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['event', 'date', 'odds', 'stake', 'bet_type', 'outcome',
                          'sport', 'league', 'result', 'notes', 'confidence_scale']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Csak ha üres a fájl, írjuk bele a fejlécet
            if is_empty:
                writer.writeheader()

            writer.writerow({
                'event': bet.event,
                'date': bet.date,
                'odds': bet.odds,
                'stake': bet.stake,
                'bet_type': bet.bet_type,
                'outcome': bet.outcome,
                'sport': bet.sport,
                'league': bet.league,
                'result': bet.result,
                'notes': bet.notes,
                'confidence_scale': bet.confidence_scale
            })

    def get_all_bets(self):
        return self.bets

    def get_bets_by_outcome(self, outcome):
        return [bet for bet in self.bets if bet.outcome == outcome]

def calculate_total_balance(bets):
    return round(sum(bet.balance for bet in bets), 2)

def calculate_total_stake(bets):
    return sum(bet.stake for bet in bets)

def calculate_avgodds(bets):
    odds_list = []

    for bet in bets:
        try:
            odds_list.append(float(bet.odds))
        except (ValueError, TypeError):
            continue

    if not odds_list:
        return 0  # vagy "N/A"

    return round(sum(odds_list) / len(odds_list), 2)

