from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from database.db_operations import (
    create_user, verify_user, get_user_by_username, get_wallet, 
    get_user_transactions, create_transaction, get_current_crypto_price,
    get_crypto_price_history,update_crypto_price
)
from datetime import datetime, timedelta
import random
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return User(user_data) if user_data else None

# Simular fluctuaciones de precio
def simulate_price_change():
    current_price = get_current_crypto_price()
    change_percent = random.uniform(-5, 5)  # Cambio entre -5% y +5%
    new_price = current_price * (1 + change_percent/100)
    update_crypto_price(new_price)
    return new_price

# Rutas de autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if create_user(username, email, password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'danger')
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = verify_user(username, password)
        if user_data:
            user = User(user_data)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas principales
@app.route('/')
@login_required
def dashboard():
    # Simular cambio de precio (solo para demostración)
    current_price = simulate_price_change()
    
    wallet = get_wallet(current_user.id)
    transactions = get_user_transactions(current_user.id)[:5]  # Últimas 5 transacciones
    
    # Datos para gráficos
    price_history = get_crypto_price_history(7)
    dates = [datetime.fromisoformat(price['date']).strftime('%Y-%m-%d') for price in price_history]
    prices = [price['price'] for price in price_history]
    
    # Calcular valor total en USD
    total_value = wallet['balance'] * current_price if wallet else 0
    
    return render_template('dashboard.html', 
                         wallet=wallet,
                         transactions=transactions,
                         current_price=current_price,
                         total_value=total_value,
                         price_history=price_history,
                         dates=dates,
                         prices=prices,
                         crypto_name=Config.CRYPTO_CURRENCY_NAME,
                         cryptoSymbol=Config.CRYPTO_SYMBOL)

@app.route('/transactions')
@login_required
def transactions():
    wallet = get_wallet(current_user.id)
    all_transactions = get_user_transactions(current_user.id)
    return render_template('transactions.html', 
                         wallet=wallet,
                         transactions=all_transactions,
                         crypto_name=Config.CRYPTO_CURRENCY_NAME,
                         cryptoSymbol=Config.CRYPTO_SYMBOL)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    wallet = get_wallet(current_user.id)
    
    if request.method == 'POST':
        recipient = request.form['recipient']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')
        
        recipient_user = get_user_by_username(recipient)
        
        if not recipient_user:
            flash('Recipient not found.', 'danger')
        elif recipient_user['id'] == current_user.id:
            flash('You cannot send money to yourself.', 'danger')
        elif amount <= 0:
            flash('Amount must be positive.', 'danger')
        elif wallet['balance'] < amount:
            flash('Insufficient funds.', 'danger')
        else:
            if create_transaction(current_user.id, recipient_user['id'], amount, description):
                flash('Transfer successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Transfer failed. Please try again.', 'danger')
    
    return render_template('transfer.html', 
                         wallet=wallet,
                         crypto_name=Config.CRYPTO_CURRENCY_NAME,
                         cryptoSymbol=Config.CRYPTO_SYMBOL)

if __name__ == '__main__':
    app.run(debug=True)