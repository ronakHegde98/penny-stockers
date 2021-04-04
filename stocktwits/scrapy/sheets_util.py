from gspread import exceptions as gspread_exceptions
from util import get_current_datetime 
import time

import logging

 

def fill_column(col_index, sheet, data: list, start_row_index = 0) -> None:
    time.sleep(2)

    row_index = start_row_index

    for index, value in enumerate(data):
        if(index%50 == 0):
            time.sleep(10)
        try:
            sheet.update_cell(row_index, col_index, value)
            row_index+=1
            print(index)
            time.sleep(1)
        except APIError as e:
            logging.critical("There was an error with Google API requests", exc_info)
        
def get_sheet(spreadsheet, sheet_name):

    try:
        sheet = spreadsheet.worksheet(sheet_name)
        return sheet
    except gspread_exceptions.WorksheetNotFound as e:
        logging.criticial(f'The sheet {sheet_name} was not found in {spreadsheet.title}')

def get_new_col_index(sheet):
       return len(sheet.row_values(1)) + 1

def append_column(sheet):
    sheet.add_cols(1)

def insert_timestamp_header(sheet, col_index):
    try:
        sheet.update_cell(1,col_index, get_current_datetime())
    except gspread_exceptions.IncorrectCellLabel:
        print((f'There was an issue inserting a timestamp at position: (1, {col_index}) for sheet: {sheet.title}'))

def setup_column(sheet, append_new_column = True, new_col_index = None):
    if(not new_col_index):
        new_col_index = get_new_col_index(sheet)

    if(append_new_column):
        append_column(sheet)
        
    insert_timestamp_header(sheet, col_index = new_col_index)

def get_column_values(sheet, col_index: int, starting_row_index: int = 1):
    return sheet.col_values(col_index)[starting_row_index:]


