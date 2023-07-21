"""Module for formatting/filtering all SNMP data."""

import json
import os

def var_table(vartable):
    """This takes the output SNMP table for each
    switch and checks for Inlet Sensors. If one
    or more is found, it is sent to stage_1, where
    it is discarded if it belongs to Slot 2 or higher.
    Data is returned to be JSON'd.
    """

    snmp_info = {}
    sequence = 0
    try:
        for varbinds in vartable:

            for oid, val in varbinds:

                oid_old = oid.prettyPrint()
                val_old = val.prettyPrint()

                if ("nlet" in val_old) and (sequence == 0):
                    a_side, b_side  = stage_1(
                                            val_old,
                                            oid_old,
                                            )

                    if a_side != 0:
                        snmp_info[a_side] = b_side
                        sequence = sequence + 1

        return snmp_info, True

    except TypeError:
        print("TypeError")
        return "", False



def stage_1(val_old, oid_old):
    """Splits output and retains the index number.
    Filters out any inlet sensors belonging to Slots
    2 or higher.
    """

    a_side = oid_old.split("1.3.6.1.4.1.9.9.13.1.3.1.2.")[-1]
    b_side = val_old.split("STRING: ")[0]

    int_ignore = ["Slot 2", "Slot 3", "Slot 4", "Slot 5", "Slot 6", "Slot 7"]
    int_discard = [i for i in int_ignore if i in val_old]

    if int_discard:
        pass

    else:
        return a_side, b_side

    return 0, " "



def rx_json(rx_report, config):
    """Takes final temp report list and dumps it into a JSON
    file for uploading to a database later. Checks to see if
    "temp_levels.json" exists, and deletes it if so.
    """

    path_name = config["temp_path"]
    path_state = os.path.exists(path_name)

    if path_state:
        os.remove(path_name)

    json_obj = json.dumps(rx_report, indent=4)

    with open(config["temp_path"], 'a', encoding="UTF-8") as draft:

        print(json_obj, file=draft)
