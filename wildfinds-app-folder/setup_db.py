import pymysql
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from projects import db, create_app

# Database configuration
user = 'root'
password = 'iamroot33'
host = 'localhost'
database_name = 'wildfinds_db'

# Create an app instance
app = create_app()

def create_database_if_not_exists():
    # Connect to MySQL server without a specific database
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password
    )
    cursor = connection.cursor()

    try:
        # Check if the database exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"Database '{database_name}' created or already exists.")
    except ProgrammingError as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()
        connection.close()

def setup_database():
    # Run the create database function
    create_database_if_not_exists()

    # Configure SQLAlchemy URI to connect to the new/existing database
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{user}:{password}@{host}/{database_name}'
    )

    # Initialize the database
    with app.app_context():
        db.create_all()
        print("All tables created successfully.")

if __name__ == "__main__":
    setup_database()

