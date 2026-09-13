import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "app.db"

# Guarda cada uma das 3 coleções de dados do app (peças/PN, registros de CS1,
# fotos dos analistas) como um blob JSON por chave — o mesmo formato que já
# era salvo no localStorage do navegador, só que agora centralizado no
# servidor e compartilhado entre todos os computadores que acessam o app.
SCHEMA = """
CREATE TABLE IF NOT EXISTS kv_store (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
"""

# Únicas chaves que a API aceita ler/gravar (ver app.py) — evita que a rota
# genérica /api/store/<key> vire um jeito de gravar chave arbitrária.
CHAVES_VALIDAS = {"pecas", "cs1_records", "analyst_photos"}


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
