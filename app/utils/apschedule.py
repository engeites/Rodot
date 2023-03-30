from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time
import pytz

# create scheduler instance
scheduler = AsyncIOScheduler()

# define the time of day to run the job
job_time = time(hour=9, minute=0)

# set the timezone for the job time (change as needed)
job_timezone = pytz.timezone('US/Eastern')