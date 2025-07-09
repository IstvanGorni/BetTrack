from flask import Flask, render_template, request, redirect
from data_manager import DataManager, calculate_total_balance, calculate_total_stake, calculate_avgodds
from models import Bet
from datetime import datetime

app = Flask(__name__)
data_manager = DataManager('data.csv')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Konvertáljuk a dátumot a kívánt formátumra
        raw_date = request.form['date']
        formatted_date = datetime.strptime(raw_date, '%Y-%m-%d').strftime('%Y.%m.%d')

        bet = Bet(
            id=None,
            event=request.form['event'],
            date=formatted_date,  # <-- itt már formázva mentjük
            odds=request.form['odds'],
            stake=request.form['stake'],
            bet_type=request.form['bet_type'],
            outcome=request.form['outcome'],
            sport=request.form['sport'],
            league=request.form['league'],
            result=request.form['result'],
            notes=request.form['notes'],
            confidence_scale=request.form['confidence_scale']
        )

        data_manager.add_bet(bet)
        return redirect('/')

    return render_template('index.html')


@app.route('/bet')
def show_bets():
    page = int(request.args.get('page', 1))
    per_page = 10

    data_manager.bets = data_manager.load_bets()
    all_bets = data_manager.get_all_bets()

    total_pages = (len(all_bets) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_bets = all_bets[start:end]

    return render_template(
        'bets.html',
        bets=paginated_bets,
        page=page,
        total_pages=total_pages
    )


@app.route('/totalbalance', methods=['GET'])
def totalbalance():
    year = request.args.get('year')
    month = request.args.get('month')

    bets = data_manager.get_all_bets()

    # Szűrés, ha meg van adva év vagy hónap
    if year and month:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.{month.zfill(2)}")]
    elif year:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.")]
    else:
        filtered_bets = bets

    total = calculate_total_balance(filtered_bets)
    return render_template('total_balance.html', total_balance=total, year=year, month=month)


@app.route('/totalstake')
def totalstake():
    year = request.args.get('year')
    month = request.args.get('month')

    bets = data_manager.get_all_bets()

    # Szűrés évre és hónapra, ha meg van adva
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

    bets = data_manager.get_all_bets()

    # Szűrés dátum alapján
    if year and month:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.{month.zfill(2)}")]
    elif year:
        filtered_bets = [bet for bet in bets if bet.date.startswith(f"{year}.")]
    else:
        filtered_bets = bets

    count = len(filtered_bets)
    return render_template('betcount.html', bet_count=count, year=year, month=month)

@app.route('/delete/<bet_id>', methods=['POST'])
def delete_bet(bet_id):
    data_manager.delete_bet(bet_id)
    return redirect('/bet')

counts = data_manager.count_bets_by_outcome()
print(f"Nyertes szelvények száma: {counts['won']}")
print(f"Vesztes szelvények száma: {counts['lost']}")


if __name__ == '__main__':
    app.run(debug=True)
