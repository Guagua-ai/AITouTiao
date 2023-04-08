import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database_if_not_exists(db_name):
    # Connect to the PostgreSQL server
    # Remove the database name from the connection string
    dsn = os.getenv('INIT_DATABASE_URL')[:-len(db_name)]
    conn = psycopg2.connect(dsn=dsn)

    # Set the isolation level for this connection
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Create a new cursor
    cursor = conn.cursor()

    # Check if the database exists
    cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), (db_name,))

    # If the database doesn't exist, create it
    if not cursor.fetchone():
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
        print(f"Database '{db_name}' created.")

    # Close the cursor and connection
    cursor.close()
    conn.close()