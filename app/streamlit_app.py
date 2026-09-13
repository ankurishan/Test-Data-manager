"""Streamlit UI: generate fake REST API test data and manage a shared repository."""
import json

import streamlit as st

from app.config import CITIES, COUNTRIES, GENDERS
from app.generator import generate_records
from app.repository import RepositoryLockedError, load_batches, release_batch, reserve_batch, save_batch

st.set_page_config(page_title="Test Data Manager", layout="wide")
st.title("Test Data Manager")

generate_tab, repo_tab = st.tabs(["Generate Test Data", "Repository"])

with generate_tab:
    st.subheader("Generate fake user records")
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name (optional fixed override)")
        last_name = st.text_input("Last Name (optional fixed override)")
        username_pattern = st.text_input(
            "Username pattern (optional, e.g. {first}.{last}{n})"
        )
        password = st.text_input("Password (optional fixed override)")
    with col2:
        gender = st.selectbox("Gender", GENDERS)
        city = st.selectbox("City", CITIES)
        country = st.selectbox("Country", COUNTRIES)
        num_records = st.number_input("Number of Records", min_value=1, max_value=1000, value=5)

    if st.button("Generate", type="primary"):
        st.session_state["generated_records"] = generate_records(
            count=int(num_records),
            first_name=first_name or None,
            last_name=last_name or None,
            username_pattern=username_pattern or None,
            password=password or None,
            gender=gender,
            city=city,
            country=country,
        )

    records = st.session_state.get("generated_records")
    if records:
        json_text = json.dumps(records, indent=2)
        st.code(json_text, language="json")
        st.download_button("Download JSON", json_text, file_name="test_data.json", mime="application/json")

        st.markdown("---")
        st.subheader("Save to Repository")
        created_by = st.text_input("Your name (created_by)", key="created_by_input")
        notes = st.text_input("Notes (optional)", key="notes_input")
        if st.button("Save to Repository"):
            if not created_by:
                st.error("Please enter your name before saving.")
            else:
                try:
                    batch_id = save_batch(created_by, records, notes)
                    st.success(f"Saved batch {batch_id} to the repository.")
                except RepositoryLockedError as exc:
                    st.error(str(exc))

with repo_tab:
    st.subheader("Shared batch repository")
    if st.button("Refresh"):
        st.rerun()

    batches = load_batches()
    if batches.empty:
        st.info("No batches saved yet.")
    else:
        display_cols = [
            "batch_id", "status", "record_count", "created_by",
            "created_at", "reserved_by", "reserved_at", "released_at", "notes",
        ]
        st.dataframe(batches[display_cols], use_container_width=True)

        selected_id = st.selectbox("Select a batch", batches["batch_id"])
        selected_row = batches[batches["batch_id"] == selected_id].iloc[0]

        with st.expander("View JSON"):
            st.code(json.dumps(json.loads(selected_row["json_data"]), indent=2), language="json")

        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            reserve_user = st.text_input("Reserve as (name)", key="reserve_user_input")
        with action_col2:
            if st.button("Reserve"):
                if not reserve_user:
                    st.error("Enter your name to reserve.")
                else:
                    try:
                        reserve_batch(selected_id, reserve_user)
                        st.success(f"Batch {selected_id} reserved by {reserve_user}.")
                        st.rerun()
                    except (ValueError, RepositoryLockedError) as exc:
                        st.error(str(exc))
        with action_col3:
            if st.button("Release"):
                try:
                    release_batch(selected_id)
                    st.success(f"Batch {selected_id} released.")
                    st.rerun()
                except (ValueError, RepositoryLockedError) as exc:
                    st.error(str(exc))
