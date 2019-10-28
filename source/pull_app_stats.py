
from biokbase.service.Client import Client as ServiceClient
import os
import datetime
import json
import client as c

token = os.environ['USER_TOKEN']
service_wizard_url = os.environ['SERVICE_WIZARD_URL']

def get_app_stats(start_date, end_date):

    client = ServiceClient(service_wizard_url, use_url_lookup=True, token=token)

    if type(start_date) == str:
        # Format date strings to datetime objects
        start_date = datetime.datetime.strptime(start_date, '%m-%d-%Y')
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date = datetime.datetime.strptime(end_date, '%m-%d-%Y')
        end_date = datetime.datetime.combine(end_date, datetime.datetime.max.time())

        # datetime to epoch. Epoch format needed for elastic query
        epoch_start = int(start_date.strftime('%s')) * 1000
        epoch_end = int(end_date.strftime('%s')) * 1000
    else:
        # datetime to epoch. Epoch format needed for elastic query
        epoch_start = int(start_date.strftime('%s')) * 1000
        epoch_end = int(end_date.strftime('%s')) * 1000

    metrics = client.sync_call('kb_Metrics.get_app_metrics', [{'epoch_range': [epoch_start, epoch_end]}])
    job_states = metrics[0]['job_states']

    error_logs = []
    #error_list = []
    for log in job_states:
        # Convert timestamps from milliseconds to seconds.
        millisec_crtime = log["creation_time"]/1000.0
        creation_time_iso = datetime.datetime.utcfromtimestamp(millisec_crtime).isoformat()
        if log.get('error'):
            if "app_id" in log:
                if log.get('status') == '':
                    errlog_dictionary = {"user" : log["user"], "error_msg": "_NULL_", "app_id" : log["app_id"], "type": "errorlogs",
                                 "job_id": log["job_id"], 'timestamp': creation_time_iso}
                    #print(errlog_dictionary)
                else:
                    errlog_dictionary = {"user" : log["user"], "error_msg": log.get('status'), "app_id" : log["app_id"], "type": "errorlogs",
                                 "job_id": log["job_id"], 'timestamp': creation_time_iso}
            
            
            else:
                errlog_dictionary = {"user" : log["user"], "error_msg": log.get('status'), "app_id" : "None", "type": "errorlogs",
                                 "job_id": log["job_id"], 'timestamp': creation_time_iso}
                print(errlog_dictionary)
            
        c.to_logstashJson(errlog_dictionary)
            
            
    print("Error logs added to Logstash for date range: {} to {}".format(start_date, end_date))
















































