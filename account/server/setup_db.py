from configuration import Config
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from getpass import getpass

def get_superuser_credentials():
    """Get PostgreSQL superuser credentials from user input."""
    print("\nDatabase superuser credentials needed to create database and user.")
    print("These credentials will only be used for setup and won't be stored.\n")
    
    username = input("PostgreSQL superuser username (default 'postgres'): ").strip() or 'postgres'
    password = getpass("PostgreSQL superuser password: ").strip()
    
    return username, password

def setup_database(config: Config):
    """Set up the database using configuration settings."""
    superuser, password = get_superuser_credentials()
    
    # Connect to default database as superuser
    super_conn = None
    conn = None
    try:
        # Initial superuser connection to postgres database
        super_conn = psycopg2.connect(
            host=config.database.host,
            port=config.database.port,
            database='postgres',
            user=superuser,
            password=password
        )
        super_conn.autocommit = True
        super_cur = super_conn.cursor()
        
        # Create user if doesn't exist
        print(f"\nCreating database user '{config.database.user}'...")
        super_cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (config.database.user,))
        if not super_cur.fetchone():
            super_cur.execute(
                f"CREATE USER {config.database.user} WITH PASSWORD %s",
                (config.database.password,)
            )
            print("User created successfully!")
        else:
            print("User already exists.")
        
        # Create database if doesn't exist
        print(f"\nCreating database '{config.database.database}'...")
        super_cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config.database.database,))
        if not super_cur.fetchone():
            super_cur.execute(f"CREATE DATABASE {config.database.database}")
            print("Database created successfully!")
        else:
            print("Database already exists.")
        
        # Grant privileges
        super_cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {config.database.database} TO {config.database.user}")
        
        # Close superuser connection
        super_cur.close()
        super_conn.close()
        
        # Connect as the application user to set up tables
        print("\nSetting up database tables...")
        conn = psycopg2.connect(config.database.url)
        cur = conn.cursor()
        
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                revoked_at TIMESTAMP,
                issuer_ip TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
            CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);
        """)
        
        conn.commit()
        print("Database tables created successfully!")
        print("\nDatabase setup completed! You can now run the OAuth server.")
        
    except psycopg2.Error as e:
        print(f"\nError during database setup: {e}")
        if 'password authentication failed' in str(e):
            print("\nTip: Check that you entered the correct superuser password.")
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
        if super_conn and not super_conn.closed:
            super_conn.close()

if __name__ == '__main__':
    try:
        config = Config(env_file='.env', config_file='config.yml')
        setup_database(config)
    except Exception as e:
        print(f"\nConfiguration error: {e}")
        sys.exit(1)