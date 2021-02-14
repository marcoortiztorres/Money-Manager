import pandas as pd
import numpy as np
from datetime import datetime
from money_manager.google_drive.google_sheets import build_drive_api_v3
from money_manager.google_drive.objects import *


def create_new_sheet():
    month = get_this_month()
    day = int(datetime.today().day)
    data = [
        {
            "title": 'Balances',
            "df": pd.DataFrame([
                {MONTH_KEY: month, STARTING_BANK_BALANCE_KEY: 0, FINAL_BANK_BALANCE_KEY: 0,
                 SAVINGS_BALANCE_KEY: 0, SAVINGS_DEPOSIT_KEY: 0, SAVINGS_WITHDRAW_KEY: 0}
            ])
        },
        {
            "title": "Summary",
            "df": pd.DataFrame([
                {MONTH_KEY: month, CATEGORY_KEY: f'=UNIQUE({month}!C2:C)',
                 SPENDING_TOTAL_KEY: f'=SUMIF({month}!C2:C,"*"&B2&"*",{month}!B2:B)', BUDGET_KEY: 200,
                 BUDGET_REMAINDER: f'=D2-C2', PROJECTED_SPENDING: f'=(C2*30)/{day}'}
            ])
        },
        get_new_monthly_sheet(month, template=True)

    ]
    service = build_drive_api_v3()
    sheets = service.spreadsheets()
    create_body = {"properties": {"title": "Money Management Sheet"},
                   "sheets": list(map(lambda d: {"properties": {"title": d.get("title")}}, data))}

    spreadsheet = sheets.create(body=create_body, fields='spreadsheetId').execute()
    spreadsheet_id = spreadsheet.get("spreadsheetId")

    update_body = {
        "valueInputOption": "USER_ENTERED",
        "data": list(map(lambda d: {"range": d.get("title"), "values": df_to_sheet(d.get("df"))}, data))
    }

    sheets.values().batchUpdate(spreadsheetId=spreadsheet_id, body=update_body).execute()

    print('Spreadsheet ID: {0}'.format(spreadsheet_id))
    return spreadsheet_id


def df_to_sheet(df):
    df_columns = [np.array(df.columns)]
    df_values = df.values.tolist()
    df_to_sheet = np.concatenate((df_columns, df_values)).tolist()
    return df_to_sheet


def get_this_month():
    current_date = datetime.now()
    month = current_date.strftime("%B")
    print("month:", month)
    return month

def get_current_month():
    current_date = datetime.now()
    return current_date.strftime("%B")


def get_new_monthly_sheet(month, template=False):
    if template:
        return {
            "title": month,
            "df": pd.DataFrame([{ITEM_KEY: 'Burrito', COST_KEY: 8.99, CATEGORY_KEY: 'Food',
                                 SUB_CATEGORY_KEY: 'Fast Food', DESCRIPTION_KEY: '', STORE_KEY: 'Chipotle',
                                 PAYMENT_KEY: 'Credit Card', DATE_KEY: datetime.now().strftime("%d/%m/%Y")}])
        }
    else:
        return {
            "title": month,
            "df": pd.DataFrame([{ITEM_KEY: '', COST_KEY: '', CATEGORY_KEY: '',
                                 SUB_CATEGORY_KEY: '', DESCRIPTION_KEY: '', STORE_KEY: '',
                                 PAYMENT_KEY: '', DATE_KEY: ''}])
        }
