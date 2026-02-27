from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

def get_engine():
    load_dotenv()

    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    database = os.getenv('DB_NAME')
    port = os.getenv('DB_PORT')

    try:
        # From sqlalchemy docs: database url = dialect+driver://username:password@host:port/database
        engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {e}")
        
    return engine