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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

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
        entry_date = datetime.strptime(data['entry_date'], '%d/%m/%Y').date()
        exit_date = datetime.strptime(data['exit_date'], '%d/%m/%Y').date() if data.get('exit_date') else None
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
        stock.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Stock updated'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
