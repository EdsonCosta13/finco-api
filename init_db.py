import os
import subprocess
from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

def init_database():
    """Initialize the database with all tables from models."""
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from app.models.company import Company
        from app.models.employee import Employee
        from app.models.credit_request import CreditRequest
        from app.models.investment import Investment
        from app.models.invitation import CompanyInvitation, EmployeeInvitation
        
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
