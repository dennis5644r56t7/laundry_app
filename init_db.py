from app import app, db
import os

def init_db():
    # Create application context
    with app.app_context():
        # Remove existing database if it exists
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'laundry.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Removed existing database")

        # Create all tables
        db.create_all()
        print("Created new database with all tables")

if __name__ == '__main__':
    init_db()
