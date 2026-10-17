import sqlite3
from datetime import datetime
from config import Config

def init_db():
    with sqlite3.connect(Config.DATABASE) as conn:
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Tabla de billeteras
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            balance REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Tabla de transacciones
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            crypto_price REAL NOT NULL,
            transaction_date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
        ''')
        
        # Tabla de precios históricos de la criptomoneda
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS crypto_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price REAL NOT NULL,
            date TEXT NOT NULL
        )
        ''')
        
        # Insertar precio inicial si no existe
        cursor.execute('SELECT COUNT(*) FROM crypto_prices')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO crypto_prices (price, date) VALUES (?, ?)', 
                           (Config.INITIAL_CRYPTO_PRICE, datetime.now().isoformat()))
        
        conn.commit()
