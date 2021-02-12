import flask
import googleapiclient.discovery
from google_drive.google_auth import build_credentials, get_user_info
from google_drive.objects import Statement, YearlyReport

from plotlydash.plotter import create_plot, create_average_description_pie

app = flask.Blueprint('google_drive', __name__)


def build_drive_api_v3():
    credentials = build_credentials()
    return googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)


def get_yearly_report():
    service = build_drive_api_v3()
    yearly_report = YearlyReport(service)
    yearly_report.set_monthly_reports()
    return yearly_report


def get_monthly_statement(month):
    service = build_drive_api_v3()
    monthly_statement = Statement(month, service)
    monthly_statement.set_transactions_dict()
    monthly_statement.set_summary()
    return monthly_statement


@app.route('/statements/view/<month>', methods=['GET'])
def view_file(month):
    statement = get_monthly_statement(month)
    pie_total = create_plot(statement.transactions_json, 'Food')
    return flask.render_template(
        'transactions.html',
        month=month,
        transactions=statement.transactions,
        summary=statement.summary,
        pie_total=pie_total,
        user_info=get_user_info())
