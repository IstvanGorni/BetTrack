from email.policy import default

from flask import Flask, render_template, request, redirect, url_for  # url_for hozzáadva
from data_manager import DataManager, calculate_total_balance, calculate_total_stake, calculate_avgodds
from models import Bet
from datetime import datetime

app = Flask(__name__)
data_manager = DataManager('data.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        raw_date = request.form['date']
        formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%Y.%m.%d')

        bet = Bet(
            id=None,
            event=request.form['event'],
            date=formatted_date,
            odds=request.form['odds'],
            stake=request.form['stake'],
            bet_type=request.form['bet_type'],
            outcome=request.form['outcome'],
            sport=request.form['sport'],
            league=request.form['league'],
            result=request.form['result'],
            notes=request.form['notes'],
            confidence_scale=request.form['confidence_scale'],
            total_bets=request.form['total_bets']

        )

        data_manager.add_bet(bet)
        return redirect('/')

    return render_template('index.html')

@app.route('/bet')
def show_bets():
    page = int(request.args.get('page', 1))
    per_page = 10
    date_filter = request.args.get('date_filter')

    data_manager.bets = data_manager.load_bets()
    all_bets = data_manager.get_all_bets()

    if date_filter:
        try:
            converted_filter = datetime.strptime(date_filter, "%Y-%m-%d").strftime("%Y.%m.%d")
            all_bets = [bet for bet in all_bets if bet.date == converted_filter]
        except ValueError:
            pass

    total_pages = (len(all_bets) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_bets = all_bets[start:end]

    return render_template(
        'bets.html',
        bets=paginated_bets,
        page=page,
        total_pages=total_pages,
        date_filter=date_filter
    )

@app.route('/edit/<bet_id>', methods=['GET', 'POST'])
def edit_bet(bet_id):
    bets = data_manager.get_all_bets()
    bet = next((b for b in bets if b.id == bet_id), None)

    if not bet:
        return "Bet not found", 404

    if request.method == 'POST':
        raw_date = request.form['date']
        formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%Y.%m.%d')

        updated_bet = Bet(
            id=bet.id,
            event=request.form['event'],
            date=formatted_date,
            odds=request.form['odds'],
            stake=request.form['stake'],
            bet_type=request.form.get('bet_type', bet.bet_type),
            outcome=request.form['outcome'],
            sport=request.form['sport'],
            league=request.form['league'],
            result=request.form['result'],
            notes=request.form['notes'],
            confidence_scale=request.form['confidence_scale'],
            total_bets=request.form['total_bets']
        )

        data_manager.update_bet(updated_bet)
        return redirect('/bet')

    bet.date_html = datetime.strptime(bet.date, '%Y.%m.%d').strftime('%Y-%m-%d')
    return render_template('edit_bet.html', bet=bet)

@app.route('/totalbalance', methods=['GET'])
def totalbalance():
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')

    bets = data_manager.get_all_bets()

    if year and month and day:
        filter_str = f"{year}.{month.zfill(2)}.{day.zfill(2)}"
        filtered_bets = [bet for bet in bets if bet.date == filter_str]
    elif year and month:
        filter_str = f"{year}.{month.zfill(2)}"
        filtered_bets = [bet for bet in bets if bet.date.startswith(filter_str)]
    elif year:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.")]
    else:
        filtered_bets = bets

    total = calculate_total_balance(filtered_bets)
    return render_template('total_balance.html', total_balance=total, year=year, month=month, day=day)

@app.route('/totalstake')
def totalstake():
    year = request.args.get('year')
    month = request.args.get('month')

    bets = data_manager.get_all_bets()

    if year and month:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.{month.zfill(2)}")]
    elif year:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.")]
    else:
        filtered_bets = bets

    total = calculate_total_stake(filtered_bets)
    return render_template('total_stake.html', total_stake=total, year=year, month=month)

@app.route('/avgodds')
def avgodds():
    year = request.args.get('year')
    month = request.args.get('month')

    bets = data_manager.get_all_bets()

    if year and month:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.{month.zfill(2)}")]
    elif year:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.")]
    else:
        filtered_bets = bets

    total = calculate_avgodds(filtered_bets)
    return render_template('avgodds.html', avg_odds=total, year=year, month=month)

@app.route('/betcount')
def betcount():
    year = request.args.get('year')
    month = request.args.get('month')
    week = request.args.get('week')

    bets = data_manager.get_all_bets()

    def parse_date(date_str):
        return datetime.strptime(date_str, "%Y.%m.%d")

    filtered_bets = bets

    if year:
        filtered_bets = [
            bet for bet in filtered_bets
            if parse_date(bet.date).year == int(year)
        ]

    if month:
        filtered_bets = [
            bet for bet in filtered_bets
            if f"{parse_date(bet.date).month:02d}" == month
        ]

    if week:
        filtered_bets = [
            bet for bet in filtered_bets
            if parse_date(bet.date).isocalendar()[1] == int(week)
        ]

    count = len(filtered_bets)

    return render_template(
        'betcount.html',
        bet_count=count,
        year=year,
        month=month,
        week=week
    )

@app.route('/delete/<bet_id>', methods=['POST'])
def delete_bet(bet_id):
    data_manager.delete_bet(bet_id)
    return redirect('/bet')

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])
        type_ = request.form['type']  # Deposit vagy Withdrawal
        note = request.form.get('note', '')

        # mentés
        data_manager.add_transaction(date, amount, type_, note)

        return redirect(url_for('transactions'))

    transactions = data_manager.get_all_transactions()
    # MÓDOSÍTOTT: Deposit = negatív, Withdrawal = pozitív
    balance = sum(-t['amount'] if t['type'] == 'Deposit' else t['amount'] for t in transactions)

    return render_template('transactions.html', transactions=transactions, balance=balance)

if __name__ == '__main__':
    app.run(debug=True)