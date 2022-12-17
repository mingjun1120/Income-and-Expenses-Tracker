from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv
import os

# Load the environment variables
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(project_key=DETA_KEY)

# This is how to create/connect a database
db = deta.Base(name="monthly_reports")


def insert_period(period, incomes, expenses, comment):
    """Returns the report on a successful creation, otherwise raises an error"""
    return db.put({"key": period, "incomes": incomes, "expenses": expenses, "comment": comment})


def fetch_all_periods():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items


def get_period(period):
    """Return a dictionary. If not found, the function will return None"""
    return db.get(period)


# --- DATABASE INTERFACE ---
def get_all_periods():
    items = fetch_all_periods()
    periods = [item["key"] for item in items]
    return periods
