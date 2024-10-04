import streamlit as st
import pandas as pd
from streamlit_app.utils.logging_utils import setup_logger
from streamlit_app.utils.database import (
    create_segment,
    get_all_segments,
    add_users_to_segment,
    get_segment_user_count,
    update_segment,
    delete_segment,
    get_segment_users,
    remove_user_from_segment,
    add_user_to_segment,
)

logger = setup_logger(__name__)

st.set_page_config(page_title="Manage Segments", page_icon="👥")

st.markdown("# Manage User Segments")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Create Segment", "View Segments", "Edit Segment", "Add Users", "Import Users"]
)

# Tab 1: Create Segment
with tab1:
    st.header("Create New Segment")
    segment_name = st.text_input("Segment Name")
    segment_description = st.text_area("Segment Description")

    if st.button("Create Segment"):
        try:
            create_segment(segment_name, segment_description)
            logger.info(f"Segment '{segment_name}' created successfully!")
            st.success(f"Segment '{segment_name}' created successfully!")
        except Exception as e:
            logger.error(f"Error creating segment: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

# Tab 2: View Segments
with tab2:
    st.header("Existing Segments")
    segments = get_all_segments()

    if segments:
        segment_data = []
        for segment in segments:
            user_count = get_segment_user_count(segment.id)
            segment_data.append(
                {
                    "ID": segment.id,
                    "Name": segment.name,
                    "Description": segment.description,
                    "User Count": user_count,
                }
            )

        df = pd.DataFrame(segment_data)
        st.dataframe(df)
    else:
        st.info("No segments created yet.")

# Tab 3: Edit Segment
with tab3:
    st.header("Edit Segment")
    segments = get_all_segments()
    segment_names = [segment.name for segment in segments]
    selected_segment = st.selectbox("Select Segment to Edit", segment_names)

    if selected_segment:
        segment = next(
            segment for segment in segments if segment.name == selected_segment
        )
        new_name = st.text_input("New Segment Name", value=segment.name)
        new_description = st.text_area(
            "New Segment Description", value=segment.description
        )

        if st.button("Update Segment"):
            try:
                update_segment(segment.id, new_name, new_description)
                logger.info(f"Segment '{segment.name}' updated successfully!")
                st.success(f"Segment '{segment.name}' updated successfully!")
            except Exception as e:
                logger.error(f"Error updating segment: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

        if st.button("Delete Segment"):
            try:
                delete_segment(segment.id)
                logger.info(f"Segment '{segment.name}' deleted successfully!")
                st.success(f"Segment '{segment.name}' deleted successfully!")
                st.rerun()
            except Exception as e:
                logger.error(f"Error deleting segment: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

        st.subheader("Segment Users")
        users = get_segment_users(segment.id)
        if users:
            user_data = [
                {
                    "ID": user.id,
                    "Username": user.username,
                    "First Name": user.first_name,
                    "Last Name": user.last_name,
                }
                for user in users
            ]
            df = pd.DataFrame(user_data)
            st.dataframe(df)

            user_to_remove = st.selectbox(
                "Select User to Remove",
                [f"{user.username or user.id}" for user in users],
            )
            if st.button("Remove User"):
                user = next(
                    user
                    for user in users
                    if user.username == user_to_remove or str(user.id) == user_to_remove
                )
                try:
                    remove_user_from_segment(segment.id, user.id)
                    logger.info(
                        f"User '{user_to_remove}' removed from segment '{segment.name}' successfully!"
                    )
                    st.success(
                        f"User '{user_to_remove}' removed from segment '{segment.name}' successfully!"
                    )
                    st.rerun()
                except Exception as e:
                    logger.error(f"Error removing user from segment: {str(e)}")
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.info("No users in this segment.")

# New Tab 4: Add Users
with tab4:
    st.header("Add Users to Segment")
    segments = get_all_segments()
    segment_names = [segment.name for segment in segments]
    selected_segment = st.selectbox(
        "Select Segment", segment_names, key="add_users_segment"
    )

    if selected_segment:
        segment = next(
            segment for segment in segments if segment.name == selected_segment
        )

        st.subheader("Add New User")
        user_id = st.text_input("User ID")
        username = st.text_input("Username")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        phone = st.text_input("Phone")

        if st.button("Add User"):
            try:
                add_user_to_segment(
                    segment.id, user_id, username, first_name, last_name, phone
                )
                logger.info(f"User added to segment '{segment.name}' successfully!")
                st.success(f"User added to segment '{segment.name}' successfully!")
                st.rerun()
            except Exception as e:
                logger.error(f"Error adding user to segment: {str(e)}")
                st.error(f"An error occurred: {str(e)}")

        st.subheader("Current Users in Segment")
        users = get_segment_users(segment.id)
        if users:
            user_data = [
                {
                    "ID": user.id,
                    "User ID": user.user_id,
                    "Username": user.username,
                    "First Name": user.first_name,
                    "Last Name": user.last_name,
                    "Phone": user.phone,
                }
                for user in users
            ]
            df = pd.DataFrame(user_data)
            st.dataframe(df)
        else:
            st.info("No users in this segment.")

# Tab 5: Import Users
with tab5:
    st.header("Import Users to Segment")

    segments = get_all_segments()
    segment_names = [segment.name for segment in segments]
    selected_segment = st.selectbox("Select Segment", segment_names)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            # Define expected columns
            expected_columns = ["id", "username", "first_name", "last_name", "phone"]

            # Check if all expected columns are present
            missing_columns = set(expected_columns) - set(df.columns)
            if missing_columns:
                st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
            else:
                # Validate data types
                df["id"] = pd.to_numeric(df["id"], errors="coerce")
                df["username"] = df["username"].astype(str)
                df["first_name"] = df["first_name"].astype(str)
                df["last_name"] = df["last_name"].astype(str)
                df["phone"] = df["phone"].astype(str)

                # Check for any null values after type conversion
                null_counts = df[expected_columns].isnull().sum()
                if null_counts.sum() > 0:
                    st.warning("Some rows contain invalid data:")
                    st.write(null_counts[null_counts > 0])

                # Display preview of valid data
                st.write("Preview of valid data:")
                st.write(df[expected_columns].head())

                if st.button("Import Users"):
                    try:
                        selected_segment_id = next(
                            segment.id
                            for segment in segments
                            if segment.name == selected_segment
                        )
                        # Filter out rows with null values
                        valid_df = df.dropna(subset=expected_columns)
                        user_data = valid_df[expected_columns].to_dict("records")
                        add_users_to_segment(selected_segment_id, user_data)
                        logger.info(
                            f"Users imported to segment '{selected_segment}' successfully!"
                        )
                        st.success(
                            f"Imported {len(user_data)} valid users to segment '{selected_segment}' successfully!"
                        )
                        if len(user_data) < len(df):
                            st.warning(
                                f"Skipped {len(df) - len(user_data)} invalid rows."
                            )
                    except Exception as e:
                        logger.error(f"Error importing users: {str(e)}")
                        st.error(f"An error occurred: {str(e)}")
        except pd.errors.EmptyDataError:
            st.error("The uploaded file is empty.")
        except pd.errors.ParserError:
            st.error("Unable to parse the CSV file. Please check the file format.")
