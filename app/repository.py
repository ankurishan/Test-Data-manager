"""Excel-backed central repository for generated test data batches."""
import json
import os
import uuid
from datetime import datetime

import pandas as pd

from app.config import BATCH_COLUMNS, BATCH_SHEET_NAME, EXCEL_REPO_PATH


class RepositoryLockedError(Exception):
    """Raised when the Excel repository file cannot be written (open elsewhere)."""


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=BATCH_COLUMNS)


def load_batches() -> pd.DataFrame:
    """Load all batches from the shared Excel repository, creating it if absent."""
    if not os.path.exists(EXCEL_REPO_PATH):
        return _empty_frame()
    try:
        return pd.read_excel(EXCEL_REPO_PATH, sheet_name=BATCH_SHEET_NAME, dtype=str)
    except (ValueError, FileNotFoundError):
        # File exists but sheet is missing/unreadable yet.
        return _empty_frame()


def _write_batches(df: pd.DataFrame) -> None:
    try:
        with pd.ExcelWriter(EXCEL_REPO_PATH, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, sheet_name=BATCH_SHEET_NAME, index=False)
    except PermissionError as exc:
        raise RepositoryLockedError(
            "Could not write to the repository file — it may be open in Excel "
            "or locked by sync. Close it and try again."
        ) from exc


def save_batch(created_by: str, records: list[dict], notes: str = "") -> str:
    """Append a new Available batch to the repository and return its batch_id."""
    df = load_batches()
    batch_id = str(uuid.uuid4())[:8]
    new_row = {
        "batch_id": batch_id,
        "created_by": created_by,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "record_count": len(records),
        "json_data": json.dumps(records),
        "status": "Available",
        "reserved_by": "",
        "reserved_at": "",
        "released_at": "",
        "notes": notes,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _write_batches(df)
    return batch_id


def reserve_batch(batch_id: str, user: str) -> None:
    """Mark a batch Reserved by `user`; raises if it is not currently Available."""
    df = load_batches()
    row = df.index[df["batch_id"] == batch_id]
    if row.empty:
        raise ValueError(f"Batch {batch_id} not found")
    if df.loc[row[0], "status"] != "Available":
        raise ValueError(f"Batch {batch_id} is not Available")
    df.loc[row[0], "status"] = "Reserved"
    df.loc[row[0], "reserved_by"] = user
    df.loc[row[0], "reserved_at"] = datetime.now().isoformat(timespec="seconds")
    df.loc[row[0], "released_at"] = ""
    _write_batches(df)


def release_batch(batch_id: str) -> None:
    """Mark a Reserved batch Available again, clearing reservation fields."""
    df = load_batches()
    row = df.index[df["batch_id"] == batch_id]
    if row.empty:
        raise ValueError(f"Batch {batch_id} not found")
    df.loc[row[0], "status"] = "Available"
    df.loc[row[0], "reserved_by"] = ""
    df.loc[row[0], "released_at"] = datetime.now().isoformat(timespec="seconds")
    _write_batches(df)
