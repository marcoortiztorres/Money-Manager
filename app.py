import os
import json

from flask import Flask, render_template, session, request
from google_drive import google_auth, google_sheets

app = Flask(__name__)
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)
app.register_blueprint(google_auth.app)
app.register_blueprint(google_sheets.app)

SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'February!A2:E'


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def index():
    if google_auth.is_logged_in():
        yearly_report = google_sheets.get_yearly_report()

        monthly_reports = yearly_report.monthly_reports
        return render_template(
            'dashboard.html',
            monthly_reports=monthly_reports,
            projections=yearly_report.spending_projections,
            budget=yearly_report.budget,
            user_info=google_auth.get_user_info())

    return render_template('login.html')


@app.route('/statements', methods=['GET', 'POST', 'OPTIONS'])
def statements():
    if google_auth.is_logged_in():
        yearly_report = google_sheets.get_yearly_report()
        monthly_reports = yearly_report.monthly_reports
        return render_template(
            'statements.html',
            monthly_reports=monthly_reports,
            user_info=google_auth.get_user_info())

    return render_template('login.html')


if __name__ == '__main__':
    app.run()
