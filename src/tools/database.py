import sqlite3
import pandas as pd
from datetime import datetime

class TradeMemory:
    def __init__(self, db_name="trade_history.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Initializes the database and creates the table if it doesn't exist."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Added full_report column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP,
                ticker TEXT,
                signal TEXT,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                risk_level TEXT,
                full_report TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_analysis(self, ticker, signal, entry, target, stop, risk, full_report):
        """Saves a new analysis record to the database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        timestamp = datetime.now()
        
        cursor.execute('''
            INSERT INTO analyses (date, ticker, signal, entry_price, target_price, stop_loss, risk_level, full_report)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, ticker, signal, entry, target, stop, risk, full_report))
        
        conn.commit()
        conn.close()

    def get_history(self):
        """Returns the entire trade history as a pandas DataFrame, sorted by date descending."""
        conn = sqlite3.connect(self.db_name)
        
        query = "SELECT * FROM analyses ORDER BY date DESC"
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df

if __name__ == "__main__":
    # Test Block
    db = TradeMemory()
    # db.save_analysis("TEST.IS", "BUY", 10.50, 15.00, 9.50, "High Risk", "# Test Report Content")
    print(db.get_history())
