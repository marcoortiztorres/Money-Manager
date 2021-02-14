import os
import pandas as pd
import numpy as np
from datetime import datetime

SAMPLE_SPREADSHEET_ID = os.environ.get('SHEET_ID', default=False)

ROW_LIMIT = 500

# SUMMARY SHEET
MONTH_KEY = 'Month'
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
STORE_KEY = 'Store'
PAYMENT_KEY = 'Payment Method'
DATE_KEY = 'Date'


def get_current_month():
    current_date = datetime.now()
    return current_date.strftime("%B")


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
        return pd.DataFrame(data_list[1:], columns=data_list[0])

    def set_monthly_reports(self):
        data_range = "Balances!A1:F"
        balance_summary_df = self.get_sheet_df(data_range)

        self.balances_df = balance_summary_df
        self.monthly_reports = balance_summary_df.to_dict('records')

    def set_summary_df(self):
        data_range = "Summary!A1:F"
        spending_summary_df = self.get_sheet_df(data_range)

        self.summary_df = spending_summary_df
        self.summaries = spending_summary_df.to_dict('records')
        self.set_current_projection()

    def set_current_projection(self):
        current_month = get_current_month()

        grouped_spending_df = self.summary_df.groupby(MONTH_KEY)
        current_projections = grouped_spending_df.get_group(current_month)
        self.current_projections_df = current_projections.set_index(CATEGORY_KEY)

    def update_summary_sheet(self):
        current_month = get_current_month()
        current_day = float(datetime.today().day)
        monthly_statement = Statement(current_month, self)

        current_projection = self.current_projections_df
        monthly_statement_summary = monthly_statement.summary_df[[COST_KEY]]

        for index, row in monthly_statement_summary.iterrows():
            spent = round(float(row[COST_KEY]), 2)
            monthly_statement_summary.loc[index, SPENDING_TOTAL_KEY] = spent
            try:
                budget = float(current_projection.loc[index, BUDGET_KEY])
                monthly_statement_summary.loc[index, BUDGET_KEY] = round(budget, 2)
                monthly_statement_summary.loc[index, BUDGET_REMAINDER] = round(budget - spent, 2)
            except Exception as e:
                monthly_statement_summary.loc[index, BUDGET_KEY] = np.nan
                monthly_statement_summary.loc[index, BUDGET_REMAINDER] = np.nan
            monthly_statement_summary.loc[index, PROJECTED_SPENDING] = round((spent * 30) / current_day, 2)

        re_indexed_projection_df = monthly_statement_summary.reset_index(drop=False)
        re_indexed_budget_df = current_projection[[BUDGET_KEY]].reset_index(drop=False)

        self.budget = re_indexed_budget_df.to_dict('records')
        self.current_projection = re_indexed_projection_df.to_dict('records')


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
        data_range = "{}!A1:H".format(self.month)
        transactions_df = self.yearly_report.get_sheet_df(data_range)
        transactions_df.loc[:, COST_KEY] = transactions_df[COST_KEY].astype('float64')

        self.transactions_df = transactions_df
        self.transactions_json = transactions_df.to_dict('records')

        totals_df = transactions_df.groupby(CATEGORY_KEY).agg({COST_KEY: "sum"})
        totals_df = totals_df.sort_values(by=COST_KEY, ascending=False, na_position='last')
        summary_df = transactions_df.groupby(CATEGORY_KEY).describe()[COST_KEY]
        df_merged = pd.merge(totals_df, summary_df, left_index=True, right_index=True, how='inner')
        df_merged_subset = df_merged[[COST_KEY, 'count', 'mean']].round(2)
        self.summary_df = df_merged_subset
        self.summary_json = df_merged_subset.reset_index(drop=False).to_dict('records')
