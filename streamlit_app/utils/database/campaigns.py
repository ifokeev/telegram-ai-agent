from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from .models import Campaign, CampaignRecipient, SegmentUser
from .session import Session


def create_campaign(
    segment_id,
    assistant_id,
    message_template,
    make_unique,
    throttle,
):
    session = Session()
    try:
        campaign = Campaign(
            segment_id=segment_id,
            assistant_id=assistant_id,
            message_template=message_template,
            make_unique=make_unique,
            throttle=throttle,
        )
        session.add(campaign)
        session.commit()

        # Add recipients from the segment
        segment_users = (
            session.query(SegmentUser).filter_by(segment_id=segment_id).all()
        )
        for user in segment_users:
            recipient = CampaignRecipient(
                campaign_id=campaign.id, user_id=user.user_id, username=user.username
            )
            session.add(recipient)
        session.commit()

        return campaign.id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_campaigns():
    session = Session()
    try:
        return (
            session.query(Campaign)
            .options(
                joinedload(Campaign.telegram_config),
                joinedload(Campaign.segment),
                joinedload(Campaign.assistant),
            )
            .all()
        )
    finally:
        session.close()


def delete_campaign(campaign_id):
    session = Session()
    try:
        campaign = session.query(Campaign).filter_by(id=campaign_id).first()
        if campaign:
            session.delete(campaign)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_campaign_recipients(campaign_id):
    session = Session()
    try:
        return session.query(CampaignRecipient).filter_by(campaign_id=campaign_id).all()
    finally:
        session.close()


def update_recipient_status(campaign_id, user_id, status):
    session = Session()
    try:
        recipient = (
            session.query(CampaignRecipient)
            .filter_by(campaign_id=campaign_id, user_id=user_id)
            .first()
        )
        if recipient:
            recipient.status = status
            if status == "Sent":
                recipient.sent_at = datetime.utcnow()
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_campaign_recipient(campaign_id, user_id):
    session = Session()
    try:
        recipient = (
            session.query(CampaignRecipient)
            .filter_by(campaign_id=campaign_id, user_id=user_id)
            .first()
        )
        if recipient:
            session.delete(recipient)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_campaign_summary(campaign_id):
    session = Session()
    try:
        total_recipients = (
            session.query(func.count(CampaignRecipient.id))
            .filter_by(campaign_id=campaign_id)
            .scalar()
        )
        pending_count = (
            session.query(func.count(CampaignRecipient.id))
            .filter_by(campaign_id=campaign_id, status="Pending")
            .scalar()
        )
        sent_count = (
            session.query(func.count(CampaignRecipient.id))
            .filter_by(campaign_id=campaign_id, status="Sent")
            .scalar()
        )
        failed_count = (
            session.query(func.count(CampaignRecipient.id))
            .filter_by(campaign_id=campaign_id, status="Failed")
            .scalar()
        )
        last_sent = (
            session.query(func.max(CampaignRecipient.sent_at))
            .filter_by(campaign_id=campaign_id, status="Sent")
            .scalar()
        )

        return {
            "total_recipients": total_recipients,
            "pending_count": pending_count,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "last_sent_at": last_sent,
        }
    finally:
        session.close()


def update_campaign(
    campaign_id, segment_id, assistant_id, message_template, make_unique, throttle
):
    session = Session()
    try:
        campaign = session.query(Campaign).filter_by(id=campaign_id).first()
        if campaign:
            campaign.segment_id = segment_id
            campaign.assistant_id = assistant_id
            campaign.message_template = message_template
            campaign.make_unique = make_unique
            campaign.throttle = throttle
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
