from db_config import setup_database
from transaction_scheduler import TransactionScheduler
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_REPEATABLE_READ, ISOLATION_LEVEL_SERIALIZABLE
import psycopg2

def run_transaction_test(isolation_level, level_name):
    """Run transaction tests with specified isolation level."""
    print(f"\n=== Testing with {level_name} ===\n")
    scheduler = TransactionScheduler()
    try:
        scheduler.set_isolation_level(isolation_level)
        
        print("\nExecuting Schedule S1:")
        try:
            scheduler.execute_schedule('S1')
        except psycopg2.errors.QueryCanceled as e:
            print(f"Schedule S1 timed out: {e}")
        setup_database()  # Reset database state
        
        print("\nExecuting Schedule S2:")
        try:
            scheduler.execute_schedule('S2')
        except psycopg2.errors.QueryCanceled as e:
            print(f"Schedule S2 timed out: {e}")
        setup_database()  # Reset database state
        
        print("\nExecuting Schedule S3:")
        try:
            scheduler.execute_schedule('S3')
        except psycopg2.errors.QueryCanceled as e:
            print(f"Schedule S3 timed out: {e}")
        setup_database()  # Reset database state
        
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        scheduler.close()

def main():
    try:
        # Initial database setup
        setup_database()
        
        # Test with different isolation levels
        run_transaction_test(
            ISOLATION_LEVEL_READ_COMMITTED,
            "READ COMMITTED (Default)"
        )
        
        run_transaction_test(
            ISOLATION_LEVEL_REPEATABLE_READ,
            "REPEATABLE READ"
        )
        
        run_transaction_test(
            ISOLATION_LEVEL_SERIALIZABLE,
            "SERIALIZABLE"
        )
        
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == '__main__':
    main()