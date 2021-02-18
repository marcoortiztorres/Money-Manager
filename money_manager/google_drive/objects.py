import os
import pandas as pd
import numpy as np
from datetime import datetime

SAMPLE_SPREADSHEET_ID = os.environ.get('SHEET_ID', default=False)

ROW_LIMIT = 500

# SUMMARY SHEET
MONTH_KEY = 'Month'
SUMMARY_KEY = 'Summary'
TOTAL_KEY = 'Total'
STARTING_BANK_BALANCE_KEY = 'Starting Bank Balance'
FINAL_BANK_BALANCE_KEY = 'Final Bank Balance'
SAVINGS_BALANCE_KEY = 'Savings Balance'
SAVINGS_DEPOSIT_KEY = 'Savings Deposit'
SAVINGS_WITHDRAW_KEY = 'Savings Withdraw'

# SUMMARY SHEET
SPENDING_TOTAL_KEY = 'Spending Total'
BUDGET_KEY = 'Budget'
BUDGET_REMAINDER = 'Budget Remaining'
PROJECTED_SPENDING = 'Projected Spending'

# MONTHLY SHEETS
ITEM_KEY = 'Item'
COST_KEY = 'Cost'
CATEGORY_KEY = 'Category'
SUB_CATEGORY_KEY = 'Sub Category'
DESCRIPTION_KEY = 'Description'
STORE_KEY = 'Company'
PAYMENT_KEY = 'Payment Method'
DATE_KEY = 'Date'


def get_current_month():
    current_date = datetime.now()
    return current_date.strftime("%B")


def clean_finances(df, column_name):
    df[column_name] = df[column_name].str.replace('(', '-', regex=True)
    df[column_name] = df[column_name].str.replace(',', '', regex=True)
    df[column_name] = df[column_name].str.replace(')', '', regex=True)
    df[column_name] = df[column_name].astype('float64')
    return df[column_name]


class YearlyReport:

    def __init__(self, google_service, sheet_id):
        self.service = google_service
        self.sheet_id = sheet_id
        self.sheet = google_service.spreadsheets()

        self.balances_df = pd.DataFrame()
        self.monthly_reports = []

        self.summary_df = pd.DataFrame()
        self.summaries = []
        self.budget = []

        self.current_projections_df = pd.DataFrame()
        self.current_projection = []

        self.set_monthly_reports()
        self.set_summary_df()

    def get_sheet_df(self, data_range):
        result = self.sheet.values().get(spreadsheetId=self.sheet_id, range=data_range).execute()
        data_list = result.get('values', [])
        df = pd.DataFrame(data_list[1:], columns=data_list[0])
        return df.replace('', np.nan)

    def set_monthly_reports(self):
        data_range = "Balances!A1:H"
        balance_summary_df = self.get_sheet_df(data_range)

        self.balances_df = balance_summary_df
        self.monthly_reports = balance_summary_df.to_dict('records')

    def set_summary_df(self):
        data_range = "Summary!A1:J"
        spending_summary_df = self.get_sheet_df(data_range)

        self.summary_df = spending_summary_df
        self.summaries = spending_summary_df.to_dict('records')
        self.set_current_projection()

    def set_current_projection(self):
        current_month = get_current_month()

        summary_df = self.summary_df.ffill()
        grouped_spending_df = summary_df.groupby(MONTH_KEY)
        current_projections = grouped_spending_df.get_group(current_month)
        indexed_projections = current_projections.drop([MONTH_KEY], axis=1).set_index(SUMMARY_KEY)
        transposed_projections = indexed_projections.transpose()
        re_indexed_projections = transposed_projections.reset_index(drop=False).rename(columns={'index': CATEGORY_KEY})

        self.current_projections_df = re_indexed_projections
        self.current_projection = re_indexed_projections.to_dict('records')
        self.budget = re_indexed_projections[[CATEGORY_KEY, BUDGET_KEY]].to_dict('records')

    def set_projection(self):
        return 0


class Statement:

    def __init__(self, month, yearly_report):
        self.month = month
        self.yearly_report = yearly_report

        self.transactions_df = pd.DataFrame
        self.transactions_json = []
        self.summary_df = pd.DataFrame
        self.summary_json = []

        self.get_sheet_data()

    def get_sheet_data(self):
        data_range = "Transactions!A1:I"
        transactions_df = self.yearly_report.get_sheet_df(data_range)
        transactions_df[COST_KEY] = clean_finances(transactions_df, COST_KEY)

        month_transactions = transactions_df[transactions_df[MONTH_KEY] == self.month]
        clean_string_df = month_transactions.fillna('')

        self.transactions_df = clean_string_df
        self.transactions_json = clean_string_df.to_dict('records')

        totals_df = clean_string_df.groupby(CATEGORY_KEY).agg({COST_KEY: "sum"})
        totals_df = totals_df.sort_values(by=COST_KEY, ascending=False, na_position='last')
        summary_df = transactions_df.groupby(CATEGORY_KEY).describe()[COST_KEY]
        df_merged = pd.merge(totals_df, summary_df, left_index=True, right_index=True, how='inner')
        df_merged_subset = df_merged[[COST_KEY, 'count', 'mean']].round(2)
        self.summary_df = df_merged_subset
        self.summary_json = df_merged_subset.reset_index(drop=False).to_dict('records')
