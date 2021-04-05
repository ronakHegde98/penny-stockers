from datetime import datetime
from pytz import timezone

def get_current_datetime() -> str:
  format = '%m-%d-%Y %I:%M %p'
  central_tz = timezone('US/Central')
  current_time = datetime.now(tz = central_tz)
  return datetime.strftime(current_time, format) 

def is_int(input_str: str) -> int:
    if(input_str):
        if(',' in input_str):
            input_str = input_str.replace(',', '')
        try:
            int(input_str)
            return True
        except ValueError as e:
            return False
    return False





