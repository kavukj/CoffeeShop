from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.environ.get("DATABASE")
DB_USER = os.environ.get("USERNAME")
DB_PASS = os.environ.get("PASSWORD")