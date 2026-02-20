"""Application configuration and constants."""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "expense_tracker.db")
FONTS_DIR = os.path.join(BASE_DIR, "resources", "fonts")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

APP_NAME = "Expense Tracker"
APP_VERSION = "1.0.0"
