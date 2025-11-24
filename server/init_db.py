#!/usr/bin/env python3
"""
Database initialization script
Creates the database and containers if they don't exist
"""
import sys
from pathlib import Path

# Add the server directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import init_cosmos, get_database

def init_db():
    """Initialize database and containers"""
    print("Creating database and containers...")
    init_cosmos()
    db = get_database()
    if db is not None:
        try:
            db_id = getattr(db, "id", str(db))
        except Exception:
            db_id = str(db)
        print(f"Database '{db_id}' and containers created or already exist.")
    else:
        print("Cosmos DB not configured. Nothing to create.")

if __name__ == "__main__":
    init_db()