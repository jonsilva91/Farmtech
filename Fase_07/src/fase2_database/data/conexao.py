from pathlib import Path
import sqlite3

# Base: .../fase2_database
BASE_DIR = Path(__file__).resolve().parent.parent

# Pasta config dentro de fase2_database
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Caminho completo para o banco
DB_PATH = CONFIG_DIR / "farmtech.db"


class SQLiteDB:
    def __init__(self):
        # Usa str(DB_PATH) para evitar qualquer problema com Path
        self.conn = sqlite3.connect(str(DB_PATH))
        # Para retornar linhas como dict-like (sqlite3.Row)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # Garantir integridade referencial
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.cursor.close()
            self.conn.close()

    def fechar(self):
        """Compatibilidade, caso algum código antigo chame .fechar()."""
        self.cursor.close()
        self.conn.close()
