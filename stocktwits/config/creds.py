from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os

CREDS_FILE = 'google_creds.json'

def get_creds_path():
    
    current_dir = os.path.abspath(os.path.dirname(__file__))

    try:
        creds_file_path = os.path.abspath(os.path.join(current_dir, CREDS_FILE))
        if(os.path.exists(creds_file_path)):
            return creds_file_path
    except Exception as e:
        #TODO: logging here
        pass

def get_gsheets_client():

    creds_file_path = get_creds_path()
    
    scopes = [
        "https://spreadsheets.google.com/feeds",
        'https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
        ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_path, scopes)
    client = gspread.authorize(creds)
    return client


