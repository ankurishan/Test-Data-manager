"""Static configuration for the Test Data Manager app."""
import os

GENDERS = ["Random", "Male", "Female", "Other"]

CITIES = [
    "Random", "New York", "London", "Mumbai", "Bengaluru", "Toronto",
    "Sydney", "Singapore", "Dubai", "Berlin", "Tokyo",
]

COUNTRIES = [
    "Random", "United States", "United Kingdom", "India", "Canada",
    "Australia", "Singapore", "United Arab Emirates", "Germany", "Japan",
]

# Path to the shared Excel repository. Point this at a SharePoint-synced local
# folder so multiple users see the same file; override via env var when needed.
EXCEL_REPO_PATH = os.environ.get(
    "TDM_EXCEL_REPO_PATH",
    os.path.join(os.path.expanduser("~"), "test_data_repository.xlsx"),
)

BATCH_SHEET_NAME = "Batches"

BATCH_COLUMNS = [
    "batch_id", "created_by", "created_at", "record_count", "json_data",
    "status", "reserved_by", "reserved_at", "released_at", "notes",
]
