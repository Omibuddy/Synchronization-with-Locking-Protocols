import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Create a new database connection using environment variables."""
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Connected to the database")
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise


def setup_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Create transaction test table
            cur.execute(
                """
                DROP TABLE IF EXISTS transaction_test CASCADE;
                CREATE TABLE transaction_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    value INTEGER
                );
            """
            )

            # Insert initial test data
            cur.execute(
                """
                INSERT INTO transaction_test (name, value) VALUES
                ('Item A', 100),
                ('Item B', 200),
                ('Item C', 300);
            """
            )

            conn.commit()
            print("Database initialized successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error setting up database: {e}")
        raise
    finally:
        conn.close()
