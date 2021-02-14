import os

from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy

from money_manager.google_drive import google_sheets, google_auth
from money_manager.plotlydash import plotter

app = Flask(__name__)

# Database Setup
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Google Auth Setup
app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)
app.register_blueprint(google_auth.app)
app.register_blueprint(google_sheets.app)

from money_manager.database_query import get_user_sheet


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        session['user_info'] = user_info
        get_user_sheet(user_info['id'])

        yearly_report = google_sheets.get_yearly_report()

        return render_template(
            'dashboard.html',
            projections=yearly_report.current_projection,
            budgets=yearly_report.budget,
            user_info=user_info)

    return render_template('login.html')


@app.route('/statements', methods=['GET', 'POST', 'OPTIONS'])
def statements():
    if google_auth.is_logged_in():
        yearly_report = google_sheets.get_yearly_report()
        return render_template(
            'statements.html',
            monthly_reports=yearly_report.monthly_reports)

    return render_template('login.html')


@app.route('/statements/view/<month>', methods=['GET'])
def view_file(month):
    statement = google_sheets.get_monthly_statement(month)
    pie_total = plotter.create_plot(statement.transactions_json, 'Food')
    return render_template(
        'transactions.html',
        month=month,
        transactions=statement.transactions_json,
        summary=statement.summary_json,
        pie_total=pie_total)


if __name__ == '__main__':
    app.run()
