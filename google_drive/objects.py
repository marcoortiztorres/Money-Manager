import os

import pandas as pd

SAMPLE_SPREADSHEET_ID = os.environ.get('SHEET_ID', default=False)


class YearlyReport:
    months = [
        {'name': 'January', 'cell': 'B'},
        {'name': 'February', 'cell': 'C'}]

    def __init__(self, google_service):
        self.service = google_service
        self.sheet = google_service.spreadsheets()
        self.monthly_reports = []
        self.spending_projections = []
        self.budget = []
        self.set_budget()
        self.set_spending_projections()

    def set_monthly_reports(self):
        for month in self.months:
            month_cell = month['cell']
            data_range = "Transactions!{}2:{}16".format(month_cell, month_cell)
            result = self.sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=data_range).execute()
            month_column = result.get('values', [])
            self.monthly_reports.append(Balance(month['name'], month_column))

    def set_spending_projections(self):
        data_range = "Transactions!A21:D31"
        result = self.sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=data_range).execute()
        projections = result.get('values', [])
        for row in projections:
            self.spending_projections.append({'label': row[0] if str(row[0]) != '\\t' else '',
                                              'ideal_spending': row[1] if str(row[1]) != '\\t' else '',
                                              'spending_remaining': row[2] if str(row[2]) != '\\t' else '',
                                              'projected_spending': row[3] if str(row[3]) != '\\t' else ''})

    def set_budget(self):
        data_range = "Transactions!O6:P15"
        result = self.sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=data_range).execute()
        projections = result.get('values', [])
        for row in projections:
            self.budget.append({'label': row[0],
                                'max': row[1]})


class Balance:
    def __init__(self, month, yearly_report_list):
        self.month = month
        self.starting_bank_balance = '$' + yearly_report_list[5][0]
        self.final_bank_balance = '$' + yearly_report_list[14][0]
        self.savings_balance = '$' + yearly_report_list[3][0]
        self.savings_deposit = '$' + yearly_report_list[1][0]
        self.savings_withdraw = '$' + yearly_report_list[2][0]


class Statement:
    description = 'description'
    category = 'category'
    sub_category = 'sub category'
    store = 'store'
    cost = 'cost'
    payment_type = 'payment type'
    date = 'date'

    def __init__(self, month, google_service):
        self.month = month
        self.service = google_service
        self.raw_transactions = []
        self.transactions = []
        self.transactions_json = []
        self.summary = []
        self.get_raw_sheet_data()

    def get_raw_sheet_data(self):
        data_range = "{}!A2:G302".format(self.month)
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=data_range).execute()
        self.raw_transactions = result.get('values', [])

    def set_transactions_dict(self):
        for transaction in self.raw_transactions:
            self.transactions.append(Transaction(transaction))
        self.set_transactions_json()

    def set_transactions_json(self):
        transactions = []
        for transaction in self.transactions:
            transactions.append(
                {
                    self.category: transaction.category,
                    self.sub_category: transaction.sub_category,
                    self.description: transaction.description,
                    self.store: transaction.store,
                    self.cost: round(float(transaction.cost), 2),
                    self.payment_type: transaction.payment_type,
                    self.date: transaction.date,
                }
            )
        self.transactions_json = transactions

    def set_summary(self):
        total_key = 'total'
        transactions = self.transactions_json
        transactions = pd.DataFrame(transactions)
        unique_categories = transactions[self.category].unique().tolist()
        summary_table = []
        # categorical Sums
        for category in unique_categories:
            category_transactions = transactions[transactions[self.category] == category]
            category_total_cost = category_transactions[self.cost].sum(axis=0).tolist()
            total_cost_rounded = round(float(category_total_cost), 2)
            summary_table.append({self.category: category, total_key: "${}".format(total_cost_rounded)})
        # Total Sum
        total_cost = transactions[self.cost].sum(axis=0).tolist()
        total_cost_rounded = round(float(total_cost), 2)
        summary_table.append({self.category: 'TOTAL', total_key: "${}".format(total_cost_rounded)})

        self.summary = summary_table


class Transaction:
    def __init__(self, google_sheet_row):
        self.category = google_sheet_row[0]
        self.sub_category = google_sheet_row[1]
        self.description = google_sheet_row[2]
        self.store = google_sheet_row[3]
        self.cost = google_sheet_row[4]
        self.payment_type = google_sheet_row[5]
        self.date = google_sheet_row[6]
