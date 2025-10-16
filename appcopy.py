# app.py (updated)
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.Date, nullable=False)
    stock_name = db.Column(db.String(50), nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    target = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=False)
    exit_date = db.Column(db.Date, nullable=True)
    points = db.Column(db.Float, nullable=True)
    profit_money = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'entry_date': self.entry_date.strftime('%d/%m/%Y') if self.entry_date else None,
            'stock_name': self.stock_name,
            'entry_price': self.entry_price,
            'target': self.target,
            'stop_loss': self.stop_loss,
            'exit_date': self.exit_date.strftime('%d/%m/%Y') if self.exit_date else None,
            'points': self.points,
            'profit_money': self.profit_money,
            'status': self.status
        }

with app.app_context():
    db.create_all()

# Mock data for stock screener
MOCK_STOCKS = [
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'ABBV', 'price': 162.22, 'change_pct': -1.27, 'high': 162.85, 'low': 162.32},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'BIO', 'price': 306.77, 'change_pct': 0.28, 'high': 310.69, 'low': 306.10},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'BIIB', 'price': 197.40, 'change_pct': 0.0, 'high': 197.40, 'low': 197.40},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'CHE', 'price': 546.29, 'change_pct': -0.19, 'high': 549.62, 'low': 543.29},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'CI', 'price': 324.57, 'change_pct': -2.5, 'high': 330.17, 'low': 324.08},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'COR', 'price': 319.61, 'change_pct': 0.59, 'high': 320.37, 'low': 318.26},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'DHR', 'price': 206.10, 'change_pct': -0.29, 'high': 209.52, 'low': 204.44},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'ELV', 'price': 394.49, 'change_pct': -0.20, 'high': 398.28, 'low': 392.73},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'HCA', 'price': 420.25, 'change_pct': 0.40, 'high': 424.41, 'low': 419.49},
    {'exchange': 'NYSE', 'sector': 'Healthcare', 'symbol': 'HUM', 'price': 502.17, 'change_pct': 0.21, 'high': 506.51, 'low': 502.69},
    # Add more for other sectors/exchanges for completeness
    {'exchange': 'NASDAQ', 'sector': 'Technology', 'symbol': 'AAPL', 'price': 150.25, 'change_pct': 1.20, 'high': 152.00, 'low': 149.50},
    {'exchange': 'NASDAQ', 'sector': 'Financial', 'symbol': 'JPM', 'price': 210.75, 'change_pct': -0.50, 'high': 212.00, 'low': 210.00},
    {'exchange': 'NYSE', 'sector': 'Financial', 'symbol': 'BAC', 'price': 45.30, 'change_pct': 0.80, 'high': 46.00, 'low': 44.90},
    # ... can add more as needed
]

def filter_stocks_by_price(price, price_range):
    if price_range == '$0.00-$49.99':
        return 0 <= price < 50
    elif price_range == '$50.00-$99.99':
        return 50 <= price < 100
    elif price_range == '$100.00-$199.99':
        return 100 <= price < 200
    elif price_range == '$200.00-$499.99':
        return 200 <= price < 500
    elif price_range == '$500.00-$999.99':
        return 500 <= price < 1000
    elif price_range == '$1000.00-Above':
        return price >= 1000
    return True  # No filter

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/opensignal')
def opensignal():
    active_stocks = Stock.query.filter_by(status='Active').order_by(Stock.entry_date.desc()).all()
    return render_template('opensignal.html', stocks=[stock.to_dict() for stock in active_stocks])

@app.route('/performance')
def performance():
    # Demo sample data for successful closed signals
    sample_signals = [
        {'stock': 'FSLR', 'bought': 233.37, 'sold': 240.37, 'gain': 3.0, 'sent': '10-15-2025', 'closed': '10-15-2025', 'sector': 'Financial Banks'},
        {'stock': 'TPR', 'bought': 114.28, 'sold': 117.71, 'gain': 3.0, 'sent': '10-06-2025', 'closed': '10-15-2025', 'sector': 'Consumer Non-Durables'},
        {'stock': 'SO', 'bought': 95.89, 'sold': 98.77, 'gain': 3.0, 'sent': '10-08-2025', 'closed': '10-14-2025', 'sector': 'Public Utilities'},
        {'stock': 'MLM', 'bought': 623.23, 'sold': 641.93, 'gain': 3.0, 'sent': '09-30-2025', 'closed': '10-13-2025', 'sector': 'Non-Energy Minerals'},
        {'stock': 'GEV', 'bought': 362.50, 'sold': 373.21, 'gain': 3.0, 'sent': '10-05-2025', 'closed': '10-15-2025', 'sector': 'Producer Manufacturing'},
        {'stock': 'ORCL', 'bought': 198.78, 'sold': 204.74, 'gain': 3.0, 'sent': '10-09-2025', 'closed': '10-13-2025', 'sector': 'Technology Services'},
        {'stock': 'EL', 'bought': 93.22, 'sold': 96.02, 'gain': 3.0, 'sent': '10-28-2025', 'closed': '10-08-2025', 'sector': 'Consumer Non-Durables'},
        {'stock': 'SO', 'bought': 95.36, 'sold': 98.37, 'gain': 3.0, 'sent': '10-24-2025', 'closed': '10-07-2025', 'sector': 'Consumer Services'},
        {'stock': 'PPL', 'bought': 36.38, 'sold': 37.47, 'gain': 3.0, 'sent': '04-29-2025', 'closed': '10-07-2025', 'sector': 'Utilities'},
        {'stock': 'AEP', 'bought': 114.40, 'sold': 117.83, 'gain': 3.0, 'sent': '08-22-2025', 'closed': '10-07-2025', 'sector': 'Utilities'},
    ]
    market_report = "Market Close Report: NASDAQ Composite Index 22,670.08 +148.38 (+0.66%) | Total Shares Traded: over 4.56 billion | Declining stocks led advancers by 1.32 to 1 ratio. There were 1,886 advancers and 2,547 decliners for the day. After hours most active for Oct 16, 2025: NVDA, OXY, CSX, GRA."
    return render_template('performance.html', signals=sample_signals, market_report=market_report)

@app.route('/screener', methods=['GET', 'POST'])
def screener():
    if request.method == 'GET':
        return render_template('screener_form.html')
    else:
        exchange = request.form.get('exchange')
        sector = request.form.get('sector')
        price_range = request.form.get('price_range')

        filtered_stocks = MOCK_STOCKS
        if exchange:
            filtered_stocks = [s for s in filtered_stocks if s['exchange'] == exchange]
        if sector:
            filtered_stocks = [s for s in filtered_stocks if s['sector'] == sector]
        if price_range:
            filtered_stocks = [s for s in filtered_stocks if filter_stocks_by_price(s['price'], price_range)]

        # For demo, limit to first 10
        filtered_stocks = filtered_stocks[:10]

        title = f"{exchange or 'All'} / {sector or 'All'} Results"
        return render_template('screener_results.html', stocks=filtered_stocks, title=title, exchange=exchange, sector=sector)

@app.route('/stocks', methods=['GET'])
def get_stocks():
    stocks = Stock.query.order_by(Stock.entry_date.desc()).all()
    return jsonify([stock.to_dict() for stock in stocks])

@app.route('/admin/stock/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    stock = Stock.query.get(stock_id)
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404

    db.session.delete(stock)
    db.session.commit()
    return jsonify({'message': 'Stock deleted successfully'}), 200


@app.route('/admin/stock', methods=['POST', 'PUT'])
def admin_update_stock():
    data = request.json
    required = ['entry_date', 'stock_name', 'entry_price', 'target', 'stop_loss', 'status']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    try:
        entry_date = datetime.datetime.strptime(data['entry_date'], '%d/%m/%Y').date()
        exit_date = datetime.datetime.strptime(data['exit_date'], '%d/%m/%Y').date() if data.get('exit_date') else None
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    if request.method == 'POST':
        stock = Stock(
            entry_date=entry_date,
            stock_name=data['stock_name'],
            entry_price=float(data['entry_price']),
            target=float(data['target']),
            stop_loss=float(data['stop_loss']),
            exit_date=exit_date,
            points=float(data['points']) if data.get('points') else None,
            profit_money=float(data['profit_money']) if data.get('profit_money') else None,
            status=data['status']
        )
        db.session.add(stock)
        db.session.commit()
        return jsonify({'message': 'Stock added'}), 201
    else:
        if 'id' not in data:
            return jsonify({'error': 'ID required'}), 400
        stock = Stock.query.get(data['id'])
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        stock.entry_date = entry_date
        stock.stock_name = data['stock_name']
        stock.entry_price = float(data['entry_price'])
        stock.target = float(data['target'])
        stock.stop_loss = float(data['stop_loss'])
        stock.exit_date = exit_date
        stock.points = float(data['points']) if data.get('points') else None
        stock.profit_money = float(data['profit_money']) if data.get('profit_money') else None
        stock.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Stock updated'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)