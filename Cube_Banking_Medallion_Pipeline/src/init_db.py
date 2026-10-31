from src.config import ROOT, MYSQL_CONFIG
from src.db import connection
from src.logging_config import get_logger
import mysql.connector

def main():
    # Connect without selecting a DB so schema.sql can create it if needed.
    server_config = dict(MYSQL_CONFIG)
    server_config.pop("database", None)
    conn = mysql.connector.connect(**server_config)
    try:
        cursor = conn.cursor()
        sql = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
        # Execute statements one by one because Connector/Python versions differ in multi-statement support.
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    get_logger(__name__).info("MySQL database and tables created/verified.")

if __name__ == "__main__":
    main()
