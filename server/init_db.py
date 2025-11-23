#!/usr/bin/env python3
"""
Database initialization script
Creates all tables defined in models
"""
import sys
from pathlib import Path

# Add the server directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.base import Base
from app.db.session import engine
from app.models.conversation import Conversation, Message
from app.models.notification import Notification

def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
