"""Module for reading index report and gathering RX levels
for each interface."""

import json
from jns_snmp_connect import snmp_connect
from snmp_scan import dict_create


def snmp_init(config):
    """The index report is loaded and each switch
    inlet sensor is sent to stage 1, for temperature
    data collection. This is then combined and sent
    to be output to a JSON file.
    """

    with open(config["index_path"], 'r', encoding="UTF-8") as draft:

        index_dict = json.load(draft)
        temp_report = []
        err_report = ["Description report errors:"]

        for switch_set in index_dict:

            switch_key = switch_set.keys()
            switch = switch_set["Switch"]
            temp_dict = {"Switch" : switch}

            for index in switch_key:

                if index.isnumeric():

                    oid = config["oid_sen_val"] + index

                    temp_level_c = stage_1(
                                            config,
                                            switch,
                                            err_report,
                                            oid
                                            )

                    if isinstance(temp_level_c, float):

                        #Converts from Celcius to Fahrenheit
                        temp_level_f = ((temp_level_c * 9/5) + 32)

                        updict = {index : temp_level_f}

                        temp_dict.update(updict)

            temp_report.append(temp_dict)

        dict_create.rx_json(temp_report, config)

    return err_report



def stage_1(config, switch, err_report, oid):
    """The inlet sensor temperature for each switch
    is gathered via SNMP, then returned."""

    temp_level, status_1 = snmp_connect.snmp_binds(
                                            switch,
                                            config,
                                            oid
                                            )

    if status_1 and len(temp_level) > 0:

        for unused_oid, val in temp_level:
            val_old = val.prettyPrint()

        return float(val_old)

    log_text = f"{switch} - Bad SNMP connection"
    err_report.append(log_text)

    return " "
