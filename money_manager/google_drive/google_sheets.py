import flask
from flask import session
import googleapiclient.discovery
from money_manager.google_drive.google_auth import build_credentials, get_user_info
from money_manager.google_drive.objects import Statement, YearlyReport

app = flask.Blueprint('google_drive', __name__)


def build_drive_api_v3():
    credentials = build_credentials()
    return googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)


def get_yearly_report():
    sheet_id = session['sheet_id']
    service = build_drive_api_v3()
    yearly_report = YearlyReport(service, sheet_id)
    return yearly_report


def get_monthly_statement(month):
    yearly_report = get_yearly_report()
    monthly_statement = Statement(month, yearly_report)
    return monthly_statement

