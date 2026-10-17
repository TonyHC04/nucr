import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-segura'
    DATABASE = 'database.db'
    CRYPTO_CURRENCY_NAME = "CryptoCoin"
    CRYPTO_SYMBOL = "CC"
    INITIAL_CRYPTO_PRICE = 100.0  # Valor inicial de la criptomoneda en USD