import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Operaciones de usuario
def create_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)',
            (username, email, generate_password_hash(password), datetime.now().isoformat())
        )
        user_id = cursor.lastrowid
        
        # Crear billetera para el usuario con saldo inicial de 10 CC
        cursor.execute(
            'INSERT INTO wallets (user_id, balance) VALUES (?, ?)',
            (user_id, 10.0)
        )
        
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def verify_user(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

# Operaciones de billetera
def get_wallet(user_id):
    conn = get_db_connection()
    wallet = conn.execute('SELECT * FROM wallets WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return wallet

def update_wallet_balance(user_id, new_balance):
    conn = get_db_connection()
    conn.execute('UPDATE wallets SET balance = ? WHERE user_id = ?', (new_balance, user_id))
    conn.commit()
    conn.close()

# Operaciones de transacciones
def create_transaction(sender_id, receiver_id, amount, description=""):
    conn = get_db_connection()
    
    # Obtener el precio actual de la criptomoneda
    crypto_price = get_current_crypto_price()
    
    try:
        # Registrar la transacción
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO transactions 
            (sender_id, receiver_id, amount, crypto_price, transaction_date, description) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            (sender_id, receiver_id, amount, crypto_price, datetime.now().isoformat(), description)
        )
        
        # Actualizar saldos
        sender_wallet = get_wallet(sender_id)
        receiver_wallet = get_wallet(receiver_id)
        
        update_wallet_balance(sender_id, sender_wallet['balance'] - amount)
        update_wallet_balance(receiver_id, receiver_wallet['balance'] + amount)
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_user_transactions(user_id):
    conn = get_db_connection()
    transactions = conn.execute('''
        SELECT t.*, 
               sender.username as sender_username,
               receiver.username as receiver_username
        FROM transactions t
        JOIN users sender ON t.sender_id = sender.id
        JOIN users receiver ON t.receiver_id = receiver.id
        WHERE t.sender_id = ? OR t.receiver_id = ?
        ORDER BY t.transaction_date DESC
    ''', (user_id, user_id)).fetchall()
    conn.close()
    return transactions

# Operaciones de criptomoneda
def get_current_crypto_price():
    conn = get_db_connection()
    price = conn.execute('SELECT price FROM crypto_prices ORDER BY date DESC LIMIT 1').fetchone()
    conn.close()
    return price['price'] if price else Config.INITIAL_CRYPTO_PRICE

def get_crypto_price_history(days=7):
    conn = get_db_connection()
    prices = conn.execute('''
        SELECT price, date 
        FROM crypto_prices 
        WHERE date >= date('now', ?) 
        ORDER BY date
    ''', (f'-{days} days',)).fetchall()
    conn.close()
    return prices

def update_crypto_price(new_price):
    conn = get_db_connection()
    conn.execute('INSERT INTO crypto_prices (price, date) VALUES (?, ?)', 
                 (new_price, datetime.now().isoformat()))
    conn.commit()
    conn.close()