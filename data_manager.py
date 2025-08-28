import csv
import os
import uuid
from models import Bet


class DataManager:
    def __init__(self, csv_path, transactions_path="transactions.csv"):
        self.csv_path = csv_path
        self.transactions_path = transactions_path
        self.bets = self.load_bets()
        self.max_id = self._get_max_id()
        self.transactions = self.load_transactions()  # Tranzakciók betöltése

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
                        id=row.get('id') or str(uuid.uuid4()),
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

    def count_bets_by_outcome(self):
        outcome_counts = {"won": 0, "lost": 0}

        for bet in self.bets:
            outcome = bet.outcome.strip().lower()
            if outcome in ["won", "win"]:
                outcome_counts["won"] += 1
            elif outcome in ['lost', 'lose']:
                outcome_counts['lost'] += 1

        return outcome_counts

    def add_bet(self, bet):
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

    def update_bet(self, updated_bet):
        for i, bet in enumerate(self.bets):
            if str(bet.id) == str(updated_bet.id):
                self.bets[i] = updated_bet
                break
        self._rewrite_csv()

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

    # ---------------------------
    # TRASACTION KEZELÉS - JAVÍTOTT
    # ---------------------------
    def load_transactions(self):
        transactions = []
        if not os.path.exists(self.transactions_path):
            return transactions

        with open(self.transactions_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Ha van ID mező a fájlban, hagyjuk figyelmen kívül
                    # és csak a szükséges mezőket olvassuk
                    transaction = {
                        "date": row["date"],
                        "amount": float(row["amount"]),
                        "type": row["type"],
                        "note": row.get("note", "")
                    }
                    transactions.append(transaction)
                except Exception as e:
                    print(f"[HIBA] Tranzakció feldolgozási hiba: {row} — {e}")
                    continue
        return transactions

    def add_transaction(self, date, amount, type_, note):
        transaction = {
            "date": date,
            "amount": float(amount),
            "type": type_,
            "note": note
        }

        is_empty = not os.path.exists(self.transactions_path) or os.stat(self.transactions_path).st_size == 0

        with open(self.transactions_path, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["date", "amount", "type", "note"]  # ID nélkül
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if is_empty:
                writer.writeheader()

            writer.writerow(transaction)

        self.transactions.append(transaction)

    def add_transaction(self, date, amount, type_, note):
        transaction = {
            "id": str(uuid.uuid4()),  # Egyedi azonosító
            "date": date,
            "amount": float(amount),
            "type": type_,
            "note": note
        }

        is_empty = not os.path.exists(self.transactions_path) or os.stat(self.transactions_path).st_size == 0

        with open(self.transactions_path, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["id", "date", "amount", "type", "note"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if is_empty:
                writer.writeheader()

            writer.writerow(transaction)

        self.transactions.append(transaction)
        return transaction["id"]  # Visszaadjuk az új tranzakció ID-ját

    def get_all_transactions(self):
        return self.transactions

    def delete_transaction(self, transaction_id):
        # Tranzakció törlése ID alapján
        self.transactions = [t for t in self.transactions if t["id"] != transaction_id]

        # CSV fájl újraírása
        with open(self.transactions_path, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["id", "date", "amount", "type", "note"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for transaction in self.transactions:
                writer.writerow(transaction)


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