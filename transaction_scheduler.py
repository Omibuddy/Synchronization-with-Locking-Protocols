import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED, ISOLATION_LEVEL_REPEATABLE_READ, ISOLATION_LEVEL_SERIALIZABLE
from db_config import get_db_connection
from threading import Thread, Event
from time import sleep

class TransactionScheduler:
    def __init__(self):
        self.conn1 = get_db_connection()
        self.conn2 = get_db_connection()
        self.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        self._setup_connections()

    def _setup_connections(self):
        """Configure initial connection settings."""
        self.conn1.autocommit = False
        self.conn2.autocommit = False

    def set_isolation_level(self, level):
        """Set isolation level for both connections."""
        self.conn1.set_isolation_level(level)
        self.conn2.set_isolation_level(level)
        self.is_serializable = (level == ISOLATION_LEVEL_SERIALIZABLE)

    def execute_schedule(self, schedule_type):
        """Execute a specific transaction schedule."""
        try:
            if schedule_type == 'S1':
                self._execute_s1()
            elif schedule_type == 'S2':
                self._execute_s2()
            elif schedule_type == 'S3':
                self._execute_s3()
            else:
                raise ValueError(f"Unknown schedule type: {schedule_type}")
        except psycopg2.Error as e:
            self._rollback()
            print(f"Error executing schedule {schedule_type}: {e}")
            raise

    def _execute_s1(self):
        """S1 = r1(x) w2(x) c2 w1(x) r1(x) c1"""
        self._read_value(1, 1)  # r1(x)
        self._write_value(2, 1, "Updated by T2")  # w2(x)
        self._commit(2)  # c2
        self._write_value(1, 1, "Updated by T1")  # w1(x)
        self._read_value(1, 1)  # r1(x)
        self._commit(1)  # c1

    def _execute_s2(self):
        """S2 = r1(x) w2(x) c2 r1(x) c1"""
        self._read_value(1, 1)  # r1(x)
        self._write_value(2, 1, "Updated by T2")  # w2(x)
        self._commit(2)  # c2
        self._read_value(1, 1)  # r1(x)
        self._commit(1)  # c1

    def _execute_s3(self):
        """S3 = r2(x) w1(x) w1(y) c1 r2(y) w2(x) w2(y) c2"""
        self._read_value(2, 1)  # r2(x)
        self._write_value(1, 1, "Updated X by T1")  # w1(x)
        self._write_value(1, 2, "Updated Y by T1")  # w1(y)
        self._commit(1)  # c1
        self._read_value(2, 2)  # r2(y)
        self._write_value(2, 1, "Updated X by T2")  # w2(x)
        self._write_value(2, 2, "Updated Y by T2")  # w2(y)
        self._commit(2)  # c2

    def _read_value(self, transaction, id):
        """Read a value from the database."""
        conn = self.conn1 if transaction == 1 else self.conn2
        with conn.cursor() as cur:
            if self.is_serializable:
                cur.execute("SELECT * FROM transaction_test WHERE id = %s FOR SHARE", (id,))
            cur.execute("SELECT name, value FROM transaction_test WHERE id = %s", (id,))
            result = cur.fetchone()
            if result:
                print(f"T{transaction} reads: name={result[0]}, value={result[1]}")

    def _write_value(self, transaction, id, value):
        """Write a value to the database."""
        conn = self.conn1 if transaction == 1 else self.conn2
        with conn.cursor() as cur:
            if self.is_serializable:
                cur.execute("SELECT * FROM transaction_test WHERE id = %s FOR UPDATE", (id,))
            cur.execute("UPDATE transaction_test SET name = %s WHERE id = %s", (value, id))
            print(f"T{transaction} writes: {value}")

    def _commit(self, transaction):
        """Commit a transaction."""
        conn = self.conn1 if transaction == 1 else self.conn2
        conn.commit()
        print(f"T{transaction} commits")

    def _rollback(self):
        """Rollback both transactions."""
        try:
            self.conn1.rollback()
            self.conn2.rollback()
            print("Transactions rolled back")
        except psycopg2.Error as e:
            print(f"Error during rollback: {e}")

    def close(self):
        """Close database connections."""
        try:
            self.conn1.close()
            self.conn2.close()
        except psycopg2.Error as e:
            print(f"Error closing connections: {e}")