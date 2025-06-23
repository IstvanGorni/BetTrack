import csv
import os
import uuid
from models import Bet

class DataManager:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.bets = self.load_bets()
        self.max_id = self._get_max_id()  # Legnagyobb eddigi ID-t betöltjük

    def _get_max_id(self):
        """Visszaadja az eddigi legnagyobb numerikus ID-t, ha van, különben 0"""
        max_id = 0
        for bet in self.bets:
            try:
                max_id = max(max_id, int(bet.id))
            except (ValueError, TypeError):
                continue
        return max_id

    def load_bets(self):
        bets = []
        if not os.path.exists(self.csv_path):
            return bets

        with open(self.csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    bet = Bet(
                        id=row.get('id') or str(uuid.uuid4()),  # ha nincs id, generálunk egy UUID-t
                        event=row['event'],
                        date=row['date'],
                        odds=row['odds'],
                        stake=row['stake'],
                        bet_type=row['bet_type'],
                        outcome=row['outcome'],
                        sport=row['sport'],
                        league=row['league'],
                        result=row.get('result', ''),
                        notes=row.get('notes', ''),
                        confidence_scale=row.get('confidence_scale', '')
                    )
                    bets.append(bet)
                except Exception as e:
                    print(f"[HIBA] Sor kihagyva: {row} — {e}")
        return bets

    def add_bet(self, bet):
        # Automatikus numerikus ID generálása
        self.max_id += 1
        bet.id = str(self.max_id)

        is_empty = not os.path.exists(self.csv_path) or os.stat(self.csv_path).st_size == 0

        with open(self.csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'event', 'date', 'odds', 'stake', 'bet_type', 'outcome',
                          'sport', 'league', 'result', 'notes', 'confidence_scale']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if is_empty:
                writer.writeheader()

            writer.writerow(bet.to_dict())
        self.bets.append(bet)

    def get_all_bets(self):
        return self.bets

    def get_bets_by_outcome(self, outcome):
        return [bet for bet in self.bets if bet.outcome == outcome]

    def delete_bet(self, bet_id):
        self.bets = [bet for bet in self.bets if bet.id != bet_id]
        self._rewrite_csv()

    def _rewrite_csv(self):
        with open(self.csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'event', 'date', 'odds', 'stake', 'bet_type', 'outcome',
                          'sport', 'league', 'result', 'notes', 'confidence_scale']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for bet in self.bets:
                writer.writerow(bet.to_dict())

# Kiegészítő számítások

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
        return 0

    return round(sum(odds_list) / len(odds_list), 2)
