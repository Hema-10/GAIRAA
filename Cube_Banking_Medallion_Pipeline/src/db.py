from contextlib import contextmanager
import mysql.connector
from src.config import MYSQL_CONFIG

@contextmanager
def connection():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
