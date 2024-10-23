# config.py
from datetime import timedelta

class Config:
    SECRET_KEY = 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pcp_game.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do Flask-Session
    SESSION_TYPE = 'sqlalchemy'  # Use SQLAlchemy para gerenciar sessões
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True  # Assina o cookie de sessão para mais segurança
    SESSION_SQLALCHEMY_TABLE = 'sessions'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)  # Define o tempo de inatividade