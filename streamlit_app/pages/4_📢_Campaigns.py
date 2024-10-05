import streamlit as st
import pandas as pd
from streamlit_app.utils.database.telegram_config import get_all_telegram_configs
from streamlit_app.utils.database.segment import get_all_segments
from streamlit_app.utils.database.assistant import get_all_assistants
from streamlit_app.utils.database.campaigns import (
    create_campaign,
    get_all_campaigns,
    delete_campaign,
    get_campaign_recipients,
    update_recipient_status,
    delete_campaign_recipient,
    get_campaign_summary,
    update_campaign,
)
from streamlit_app.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

st.set_page_config(page_title="Manage Campaigns", page_icon="📢")

st.markdown("# Manage Campaigns")

tab1, tab2, tab3 = st.tabs(["Create Campaign", "View Campaigns", "Edit Campaign"])

with tab1:
    st.header("Create New Campaign")

    # Select Telegram account
    telegram_configs = get_all_telegram_configs()
    selected_phone = st.selectbox(
        "Select Telegram Account",
        [config.phone_number for config in telegram_configs],
        key="create_telegram_account",
    )

    # Select segment
    segments = get_all_segments()
    selected_segment = st.selectbox(
        "Select Segment", [segment.name for segment in segments], key="create_segment"
    )

    # Select assistant
    assistants = get_all_assistants()
    selected_assistant = st.selectbox(
        "Select Assistant",
        [assistant.name for assistant in assistants],
        key="create_assistant",
    )

    # Message template
    message_template = st.text_area("Message Template", key="create_message_template")

    # Make every message unique
    make_unique = st.checkbox("Make every message unique", key="create_make_unique")

    # Throttle
    throttle = st.number_input(
        "Throttle (seconds)", min_value=0.0, value=1.0, step=0.1, key="create_throttle"
    )

    if st.button("Create Campaign", key="create_campaign_button"):
        try:
            campaign_id = create_campaign(
                telegram_config_id=next(
                    config.id
                    for config in telegram_configs
                    if config.phone_number == selected_phone
                ),
                segment_id=next(
                    segment.id
                    for segment in segments
                    if segment.name == selected_segment
                ),
                assistant_id=next(
                    assistant.id
                    for assistant in assistants
                    if assistant.name == selected_assistant
                ),
                message_template=message_template,
                make_unique=make_unique,
                throttle=throttle,
            )
            st.success(f"Campaign created successfully with ID: {campaign_id}")
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

with tab2:
    st.header("View Campaigns")

    campaigns = get_all_campaigns()
    if not campaigns:
        st.info(
            "No campaigns found. Create a new campaign in the 'Create Campaign' tab."
        )
    else:
        campaign_data = []
        for campaign in campaigns:
            summary = get_campaign_summary(campaign.id)
            campaign_data.append(
                {
                    "ID": campaign.id,
                    "Telegram Account": campaign.telegram_config.phone_number,
                    "Segment": campaign.segment.name,
                    "Assistant": campaign.assistant.name,
                    "Total Recipients": summary["total_recipients"],
                    "Pending": summary["pending_count"],
                    "Sent": summary["sent_count"],
                    "Failed": summary["failed_count"],
                    "Last Sent": summary["last_sent_at"] or "N/A",
                }
            )

        df = pd.DataFrame(campaign_data)
        st.dataframe(df)

        # Add delete button for each campaign
        for campaign in campaigns:
            if st.button(
                f"Delete Campaign {campaign.id}", key=f"delete_campaign_{campaign.id}"
            ):
                delete_campaign(campaign.id)
                st.success(f"Campaign {campaign.id} deleted successfully")
                st.rerun()

with tab3:
    st.header("Edit Campaign")

    campaigns = get_all_campaigns()
    if not campaigns:
        st.info(
            "No campaigns found. Create a new campaign in the 'Create Campaign' tab."
        )
    else:
        selected_campaign_id = st.selectbox(
            "Select Campaign to Edit",
            [campaign.id for campaign in campaigns],
            format_func=lambda x: f"Campaign {x}",
            key="edit_campaign_select",
        )

        selected_campaign = next(
            (c for c in campaigns if c.id == selected_campaign_id), None
        )

        if selected_campaign:
            st.subheader(f"Editing Campaign {selected_campaign.id}")

            # Telegram account (read-only)
            st.text(
                f"Telegram Account: {selected_campaign.telegram_config.phone_number}"
            )

            # Segment
            segments = get_all_segments()
            selected_segment = st.selectbox(
                "Select Segment",
                [segment.name for segment in segments],
                index=[segment.id for segment in segments].index(
                    selected_campaign.segment_id
                ),
                key="edit_segment",
            )

            # Assistant
            assistants = get_all_assistants()
            selected_assistant = st.selectbox(
                "Select Assistant",
                [assistant.name for assistant in assistants],
                index=[assistant.id for assistant in assistants].index(
                    selected_campaign.assistant_id
                ),
                key="edit_assistant",
            )

            # Message template
            message_template = st.text_area(
                "Message Template",
                value=selected_campaign.message_template,
                key="edit_message_template",
            )

            # Make every message unique
            make_unique = st.checkbox(
                "Make every message unique",
                value=selected_campaign.make_unique,
                key="edit_make_unique",
            )

            # Throttle
            throttle = st.number_input(
                "Throttle (seconds)",
                min_value=0.0,
                value=selected_campaign.throttle,
                step=0.1,
                key="edit_throttle",
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Campaign", key="update_campaign_button"):
                    try:
                        update_campaign(
                            campaign_id=selected_campaign.id,
                            segment_id=next(
                                segment.id
                                for segment in segments
                                if segment.name == selected_segment
                            ),
                            assistant_id=next(
                                assistant.id
                                for assistant in assistants
                                if assistant.name == selected_assistant
                            ),
                            message_template=message_template,
                            make_unique=make_unique,
                            throttle=throttle,
                        )
                        st.success(
                            f"Campaign {selected_campaign.id} updated successfully"
                        )
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error updating campaign: {str(e)}")
                        st.error(f"An error occurred: {str(e)}")

            with col2:
                if st.button("Delete Campaign", key="delete_campaign_button"):
                    try:
                        delete_campaign(selected_campaign.id)
                        logger.info(
                            f"Campaign {selected_campaign.id} deleted successfully"
                        )
                        st.success(
                            f"Campaign {selected_campaign.id} deleted successfully"
                        )
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error deleting campaign: {str(e)}")
                        st.error(f"An error occurred: {str(e)}")

            # Display campaign recipients
            st.subheader("Campaign Recipients")
            recipients = get_campaign_recipients(selected_campaign.id)
            if recipients:
                recipient_data = []
                for recipient in recipients:
                    recipient_data.append(
                        {
                            "User ID": recipient.user_id,
                            "Username": recipient.username,
                            "Status": recipient.status,
                            "Sent At": recipient.sent_at,
                        }
                    )
                st.dataframe(pd.DataFrame(recipient_data))

                # Allow updating recipient status
                col1, col2, col3 = st.columns(3)
                with col1:
                    selected_recipient = st.selectbox(
                        "Select recipient to update",
                        [r.user_id for r in recipients],
                        key=f"select_recipient_{selected_campaign.id}",
                    )
                with col2:
                    new_status = st.selectbox(
                        "New status",
                        ["Pending", "Sent", "Failed"],
                        key=f"new_status_{selected_campaign.id}",
                    )
                with col3:
                    if st.button(
                        "Update Status", key=f"update_status_{selected_campaign.id}"
                    ):
                        update_recipient_status(
                            selected_campaign.id, selected_recipient, new_status
                        )
                        st.success(f"Status updated for recipient {selected_recipient}")
                        st.rerun()

                # Allow deleting recipients
                recipient_to_delete = st.selectbox(
                    "Select recipient to delete",
                    [r.user_id for r in recipients],
                    key=f"delete_recipient_{selected_campaign.id}",
                )
                if st.button(
                    "Delete Recipient",
                    key=f"delete_recipient_button_{selected_campaign.id}",
                ):
                    delete_campaign_recipient(selected_campaign.id, recipient_to_delete)
                    st.success(
                        f"Recipient {recipient_to_delete} deleted from campaign {selected_campaign.id}"
                    )
                    st.rerun()
            else:
                st.info("No recipients for this campaign.")
