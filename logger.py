import datetime
import os
from discord import Webhook, RequestsWebhookAdapter
from dotenv import load_dotenv
import pytz
load_dotenv()

logfilepath = os.getenv('logfilepath')
webhook_logs = os.getenv('discord_logs')

logs_webhook = Webhook.from_url(webhook_logs, adapter=RequestsWebhookAdapter())

def get_time_old():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_time():
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    return now.strftime("%y-%m-%d %H:%M:%S")

def logit(message):
    logs_webhook.send(message)
    # if os.path.exists(logfile):
    #     with open(logfile, 'a') as f:
    #         f.write(f"{get_time()} - {message}\n".format())
    #         f.close()
        
    # else:
    #     with open(logfile, 'w') as f:
    #         f.write(f"{get_time()} - {message}\n".format())
    #         f.close()