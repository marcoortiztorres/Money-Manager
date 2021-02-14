from flask import session
from money_manager.models import User, db
from money_manager.google_drive.sheet_template import create_new_sheet
GOOGLE_ID_KEY = 'id'
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'


def get_user_sheet(google_id):
    results = query_google_id(google_id)
    print(results)
    if results is None:
        session['sheet_id'] = get_new_user_sheet(google_id)
    else:
        user = User.query.get_or_404(results)
        session['sheet_id'] = user.sheet_id
    return session.get('sheet_id')


def query_google_id(google_id):
    return db.session.query(User.id).filter_by(google_id=google_id).scalar()


def get_new_user_sheet(google_id):
    new_sheet_id = create_new_sheet()
    response = add_user(google_id, new_sheet_id)
    session['new_user'] = True
    print("new user:", response)
    return new_sheet_id


def add_user(google_id, sheet_id):
    try:
        user = User(
            google_id=google_id,
            sheet_id=sheet_id
        )
        db.session.add(user)
        db.session.commit()
        return "User added. user id={}".format(user.id)
    except Exception as e:
        return str(e)
