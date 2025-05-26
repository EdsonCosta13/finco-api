import os
import subprocess
from app import create_app, db

def init_database():
    """Initialize the database with all tables from models."""
    app = create_app()
    with app.app_context():
        # Drop all tables to reset everything
        db.drop_all()
        
        # Check if migrations directory already exists
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        if not os.path.exists(migrations_dir):
            print("Initializing migrations directory...")
            subprocess.run(["flask", "db", "init"], check=True)
        else:
            print("Migrations directory already exists, skipping initialization.")
        
        print("Creating migration...")
        subprocess.run(["flask", "db", "migrate", "-m", "Initial migration"], check=True)
        
        print("Applying migration...")
        subprocess.run(["flask", "db", "upgrade"], check=True)
        
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
