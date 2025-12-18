from datetime import datetime
import re
import string
def check_time():
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
    return f"The current time is {current_time}."

def check_date():
    today = datetime.now()
    current_date = today.strftime("%A, %B %d, %Y")  # e.g., "Monday, December 02, 2025"
    return f"Today's date is {current_date}."

def is_time_or_date_query(text: str) -> bool:
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))

    if any(keyword in text for keyword in ["what date is it", "current date", "check date", "today's date", "what time is it", "current time", "check the time"]):
        return True
    return False

# print(is_time_or_date_query("What time is it now?"))