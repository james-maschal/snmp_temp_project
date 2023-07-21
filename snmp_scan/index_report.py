"""Module for Creating/Verifying the index report.
This report contains temperature sensor to be polled,
and Switch name.
"""

import os
import datetime
import configparser
import json
from jns_snmp_connect import snmp_connect
from snmp_scan import dict_create


def file_check(date, config):
    """Checks the difference between recorded date of last runtime.
    If it's been over 30 days, another index report will be initiated.
    """

    path_name = config["index_path"]
    path_state = os.path.exists(path_name)

    if not path_state:
        return True

    now = datetime.datetime.now()
    then = datetime.datetime.strptime(date["last_ran"], '%Y-%m-%d %H:%M:%S.%f')
    delta = now - then

    if delta > datetime.timedelta(days=30):
        return True

    return None



def index(buildings, config):
    """Initiates stage 1 to begin SNMP polling for
    each switch. If it makes it through, it gets added
    to the list 'index_report'. The list gets sent to
    the json file function, and records the current
    date/time into a config file named 'last_ran.ini'"""

    index_report = []
    log_text = ["Index report issues:"]

    for i in buildings:

        for switch in i:

            index_dict = stage_1(switch, config, log_text)

            if len(index_dict) > 0:

                updict = {"Switch" : switch}

                updict.update(index_dict)

                index_report.append(updict)

    index_json(index_report, config, log_text)

    return True



def stage_1(switch, config, log_text):
    """Polls each switch for its sensor inventory
    table using SNMP. It then passes this to
    the dictionary creator for processing."""

    vartable, status_1 = snmp_connect.snmp_table(
                                            switch,
                                            config,
                                            config["oid_sen_inv"]
                                            )

    if status_1 and len(vartable) > 0:
        index_dict, status_2 = dict_create.var_table(vartable)

        if status_2:

            return index_dict

        log_text.append(f"{switch} - Bad SNMP data (inventory).")
        return {}

    log_text.append(f"{switch} - Bad SNMP connection (inventory).")
    return {}



def index_json(index_report, config, log_text):
    """Prints out results from index report into
    a JSON file, to be read for temperature polling,
    and later uploading to database.
    """

    json_obj = json.dumps(index_report, indent=4)

    with open(config["index_path"], 'w', encoding="UTF-8") as draft:
        print(json_obj, file=draft)

    config_run = configparser.ConfigParser()
    config_run["run_date"] = {'date' : datetime.datetime.now()}
    config_run["log_text"] = {'log' : log_text}

    with open(config["last_ran_path"], 'w', encoding="UTF-8") as configfile:
        config_run.write(configfile)
