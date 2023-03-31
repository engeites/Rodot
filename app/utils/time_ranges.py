from datetime import datetime

def get_hours_passed_today():
    now = datetime.now()

    # Get the midnight time for today
    today = datetime(now.year, now.month, now.day)

    # Calculate the number of hours passed since midnight
    return (now - today).total_seconds() // 3600
