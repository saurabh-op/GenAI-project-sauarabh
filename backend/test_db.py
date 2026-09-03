import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

print("Connecting...")

connection = psycopg.connect(
    os.getenv("DATABASE_URL"),
    connect_timeout=10
)

print("Database connection successful!")

connection.close()