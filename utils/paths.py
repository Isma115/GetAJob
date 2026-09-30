import os

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(APP_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
GENERATED_DIR = os.path.join(DATA_DIR, "generated")
DATA_DB_PATH = os.path.join(DATA_DIR, "job_assistant.db")


def ensure_data_dirs():
    for path in (DATA_DIR, EXPORTS_DIR, GENERATED_DIR):
        os.makedirs(path, exist_ok=True)


def data_path(*parts):
    ensure_data_dirs()
    return os.path.join(DATA_DIR, *parts)

