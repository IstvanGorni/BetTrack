import csv
import os
import uuid
from models import Bet


class DataManager:
    def __init__(self, csv_path, transactions_path="transactions.csv"):
        self.csv_path = csv_path
        self.transactions_path = transactions_path
        self.bets = self.load_bets()
        self.transactions = self.load_transactions()
        self.max_id = self._get_max_id()

    def _get_max_id(self):
        max_id = 0
        for bet in self.bets:
            try:
                max_id = max(max_id, int(bet.id))
            except:
                continue
        return max_id

    # -------------------
    # BETS
    # -------------------
    def load_bets(self):
        bets = []
        if not os.path.exists(self.csv_path):
            return bets

        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    bets.append(
                        Bet(
                            id=row.get("id"),
                            event=row["event"],
                            date=row["date"],
                            odds=row["odds"],
                            stake=row["stake"],
                            bet_type=row["bet_type"],
                            outcome=row["outcome"],
                            sport=row["sport"],
                            league=row["league"],
                            result=row.get("result", ""),
                            notes=row.get("notes", ""),
                            confidence_scale=row.get("confidence_scale") or 8,
                            total_bets=row.get("total_bets") or 1
                        )
                    )
                except Exception as e:
                    print("[HIBA] Bet load:", e)
        return bets

    def add_bet(self, bet):
        self.max_id += 1
        bet.id = str(self.max_id)

        is_empty = not os.path.exists(self.csv_path) or os.stat(self.csv_path).st_size == 0

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            fieldnames = bet.to_dict().keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if is_empty:
                writer.writeheader()
            writer.writerow(bet.to_dict())

        self.bets.append(bet)

    def update_bet(self, updated_bet):
        """
        Meglévő fogadás frissítése ID alapján
        """
        for i, bet in enumerate(self.bets):
            if str(bet.id) == str(updated_bet.id):
                self.bets[i] = updated_bet
                break

        self._rewrite_bets()

    def get_all_bets(self):
        return self.bets

    def delete_bet(self, bet_id):
        self.bets = [b for b in self.bets if b.id != bet_id]
        self._rewrite_bets()

    def _rewrite_bets(self):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = self.bets[0].to_dict().keys() if self.bets else []
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if fieldnames:
                writer.writeheader()
                for bet in self.bets:
                    writer.writerow(bet.to_dict())

    # -------------------
    # TRANSACTIONS
    # -------------------
    def load_transactions(self):
        transactions = []
        if not os.path.exists(self.transactions_path):
            return transactions

        with open(self.transactions_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                transactions.append({
                    "id": row["id"],
                    "date": row["date"],
                    "amount": float(row["amount"]),
                    "type": row["type"],
                    "note": row.get("note", "")
                })
        return transactions

    def add_transaction(self, date, amount, type_, note):
        transaction = {
            "id": str(uuid.uuid4()),
            "date": date,
            "amount": float(amount),
            "type": type_,
            "note": note
        }

        is_empty = not os.path.exists(self.transactions_path) or os.stat(self.transactions_path).st_size == 0

        with open(self.transactions_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=transaction.keys())
            if is_empty:
                writer.writeheader()
            writer.writerow(transaction)

        self.transactions.append(transaction)

    def get_all_transactions(self):
        return self.transactions

    def delete_transaction(self, transaction_id):
        self.transactions = [t for t in self.transactions if t["id"] != transaction_id]
        with open(self.transactions_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "amount", "type", "note"])
            writer.writeheader()
            for t in self.transactions:
                writer.writerow(t)


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