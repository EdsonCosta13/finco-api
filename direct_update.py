from app import create_app, db

def update_invitation_tables():
    app = create_app()
    with app.app_context():
        connection = db.engine.connect()
        
        try:
            # Try to add status column to company_invitations
            print("Adding status column to company_invitations table...")
            connection.execute("""
            ALTER TABLE company_invitations 
            ADD COLUMN status VARCHAR(20) DEFAULT 'pending'
            """)
        except Exception as e:
            print(f"Note: {str(e)}")
            
        try:
            # Try to add status column to employee_invitations
            print("Adding status column to employee_invitations table...")
            connection.execute("""
            ALTER TABLE employee_invitations 
            ADD COLUMN status VARCHAR(20) DEFAULT 'pending'
            """)
        except Exception as e:
            print(f"Note: {str(e)}")
        
        # Update existing records
        print("Updating existing records...")
        connection.execute("""
        UPDATE company_invitations 
        SET status = CASE WHEN is_used = 1 THEN 'used' ELSE 'pending' END
        """)
        
        connection.execute("""
        UPDATE employee_invitations 
        SET status = CASE WHEN is_used = 1 THEN 'used' ELSE 'pending' END
        """)
        
        print("Update completed!")

if __name__ == "__main__":
    update_invitation_tables()
