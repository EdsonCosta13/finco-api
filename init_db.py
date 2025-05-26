import os
from app import create_app, db

def init_database():
    """Initialize the database with all tables from models."""
    app = create_app()
    with app.app_context():
        # Drop all tables to reset everything
        print("Dropping all existing tables...")
        db.drop_all()
        
        # Create all tables based on current models
        print("Creating all tables from models...")
        db.create_all()
        
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
