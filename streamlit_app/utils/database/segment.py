from .session import Session
from .models import Segment, SegmentUser


def create_segment(name, description):
    session = Session()
    try:
        segment = Segment(name=name, description=description)
        session.add(segment)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_segments():
    session = Session()
    try:
        return session.query(Segment).all()
    finally:
        session.close()


def update_segment(segment_id, new_name, new_description):
    session = Session()
    try:
        segment = session.query(Segment).filter_by(id=segment_id).first()
        if segment:
            segment.name = new_name
            segment.description = new_description
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_segment(segment_id):
    session = Session()
    try:
        segment = session.query(Segment).filter_by(id=segment_id).first()
        if segment:
            session.delete(segment)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def add_user_to_segment(segment_id, user_id, username, first_name, last_name, phone):
    session = Session()
    try:
        segment_user = SegmentUser(
            segment_id=segment_id,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        session.add(segment_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def add_users_to_segment(segment_id, user_data_list):
    session = Session()
    try:
        for user_data in user_data_list:
            segment_user = SegmentUser(
                segment_id=segment_id,
                user_id=user_data["id"],
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone=user_data["phone"],
            )
            session.add(segment_user)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_segment_users(segment_id):
    session = Session()
    try:
        return session.query(SegmentUser).filter_by(segment_id=segment_id).all()
    finally:
        session.close()


def remove_user_from_segment(segment_id, user_id):
    session = Session()
    try:
        user = (
            session.query(SegmentUser)
            .filter_by(segment_id=segment_id, user_id=user_id)
            .first()
        )
        if user:
            session.delete(user)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_segment_user_count(segment_id):
    session = Session()
    try:
        return session.query(SegmentUser).filter_by(segment_id=segment_id).count()
    finally:
        session.close()
