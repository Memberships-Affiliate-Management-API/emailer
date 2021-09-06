"""
    **scheduler**
        used to dynamically add jobs on a separate thread to complete tasks that should not interfere
        with requests, or requests that takes a long time to complete
"""
__developer__ = "mobius-crypt"
__email__ = "mobiusndou@gmail.com"
__twitter__ = "@blueitserver"
__github_repo__ = "https://github.com/freelancing-solutions/memberships-and-affiliate-api"
__github_profile__ = "https://github.com/freelancing-solutions/"

from typing import Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from src.utils.utils import create_id as create_unique_id

task_scheduler = BackgroundScheduler({'apscheduler.timezone': 'Africa/Johannesburg'})
cron_scheduler = BackgroundScheduler({'apscheduler.timezone': 'Africa/Johannesburg'})
