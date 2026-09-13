---
name: test-data-manager
description: Use when maintaining or extending the Test Data Manager Streamlit app in this repo (app/) — generating fake REST API user test data, editing dropdown lists, changing the JSON schema, or working with the shared Excel repository's reserve/release lifecycle.
---

# Test Data Manager Skill

This repo contains a local Streamlit app (`app/streamlit_app.py`) that generates
fake user records for testing a REST-based user-creation API, and a shared Excel
file acting as a central repository so multiple people can reserve/release
generated batches without collisions.

## Files
- `app/config.py` — static dropdown lists (`GENDERS`, `CITIES`, `COUNTRIES`) and
  `EXCEL_REPO_PATH` (override via `TDM_EXCEL_REPO_PATH` env var; point it at a
  SharePoint-synced local folder to share with a team).
- `app/generator.py` — `generate_records(...)` builds fake records with Faker.
- `app/repository.py` — Excel-backed CRUD: `load_batches`, `save_batch`,
  `reserve_batch`, `release_batch`.
- `app/streamlit_app.py` — UI with "Generate Test Data" and "Repository" tabs.

## Conventions to preserve
- **JSON record schema** is a flat object with camelCase keys: `firstName,
  lastName, userName, password, gender, city, country`. Any new field must be
  added consistently in `generator.py`'s output dict, not nested.
- **Dropdown values** (gender/city/country) live only in `app/config.py`. Add or
  remove entries there — never hardcode lists elsewhere. Keep `"Random"` as the
  first option in each list so the generator's random-fallback logic keeps
  working.
- **Optional override fields** (first name, last name, username pattern,
  password): when the user leaves a text box blank, the generator must fall back
  to Faker/random per record; when filled in, the value applies to *all* records
  in that batch. Preserve this behavior when adding new overridable fields.
- **Repository status lifecycle** is strictly `Available -> Reserved ->
  Available`. `reserve_batch` must reject reserving a batch that isn't
  `Available`; `release_batch` always clears `reserved_by` and sets
  `released_at`. Do not add extra statuses without updating both repository
  functions and the UI's Reserve/Release buttons.
- **Excel writes** must go through `repository._write_batches`, which wraps
  `PermissionError` (file open elsewhere / sync lock) into
  `RepositoryLockedError` — a clear, user-facing message. Never write the Excel
  file directly from the UI layer.

## Running the app
```
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```
Opens at `http://localhost:8501`.

## Known limitations (do not silently "fix" without discussion)
- Concurrent writes from multiple users editing the Excel file at the same
  moment are only handled via a locked-file error message, not true row-level
  locking. A move to SharePoint Lists/Graph API would be needed for that.
- Faker-generated passwords are plain text and may not satisfy every target
  API's password complexity rules.
