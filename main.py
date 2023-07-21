#!/home/netmaschal/python/bin/python3
"""This program is designed to collect inlet temperature levels
for storage and querying for closets aproaching alert levels.
It references a list with one sensor for each switch, updated every
30 days. All data gets exported to a database for later retrieval."""

import configparser
import datetime
import mysql.connector
from jns_cisco_devices import cisco_devices
from snmp_scan import snmp_command
from snmp_scan import index_report
from sql_temperature import temp_table
from sql_temperature import index_table
from sql_temperature import final_table



def main():
    """Main logic."""

    config = configparser.ConfigParser()
    config.read("/home/netmaschal/python/snmp_temp_project/info.ini")
    config_v = {
        "log_path"      : str(config["file_path"]["log_path"]),
        "temp_path"     : str(config["file_path"]["temp_path"]),
        "index_path"    : str(config["file_path"]["index_path"]),
        "last_ran_path" : str(config["file_path"]["last_ran_path"]),
        "server_passwd" : str(config["sql_user"]["pass"]),
        "server_user"   : str(config["sql_user"]["name"]),
        "server_IP"     : str(config["sql_user"]["server"]),
        "server_port"   : str(config["sql_user"]["port"]),
        "server_db"     : str(config["sql_user"]["db_name"]),
        "oid_sen_val"   : str(config["oid"]["sensor_value"]),
        "oid_sen_inv"   : str(config["oid"]["sensor_inv"]),
        "comm_string"   : str(config["oid"]["c_string"]),
        }

    index_report.index(cisco_devices.interface_buildings(), config_v)

    print("Index check complete. Gathering data...")
    err_text = snmp_command.snmp_init(config_v)

    print("Data gathering complete. Beginning database export...")

    try:

        cnx = mysql.connector.connect(
            user        = config_v["server_user"],
            password    = config_v["server_passwd"],
            host        = config_v["server_IP"],
            database    = config_v["server_db"],
            port        = config_v["server_port"]
            )

        please = cnx.cursor()

        print("Verifying/Creating index tables....")
        index_table.json_load(config_v["index_path"], please)

        print("Creating/Filling temp tables....")
        temp_table.json_load(config_v["temp_path"], please)

        print("Creating/Compiling final table....")
        final_table.json_load(config_v["index_path"], please)

        cnx.commit()
        cnx.close()

        date = datetime.datetime.now()

        with open(f"{config_v['log_path']}", 'w', encoding="UTF-8") as log:

            with open(f"{config_v['last_ran_path']}", 'r', encoding="UTF-8") as ini:

                print(f"{date} - TEMPERATURE - "
                        "DATABASE CONNECTION SUCCESS \n Index Report:\n", file=log)
                print(ini.read(), file=log)

                try:
                    print(err_text, file=log)

                except NameError:
                    #Needed for development
                    pass


    except mysql.connector.Error as err:
        err_num = err.errno

        try:
            err_check(err_num,
                      config_v['log_path'],
                      config_v['last_ran_path'],
                      err_text)

        except NameError:
            #Needed for development
            err_none = " "
            err_check(err_num,
                      config_v['log_path'],
                      config_v['last_ran_path'],
                      err_none)

    print("Complete!")



def err_check(err, log_path, ini_path, err_text):
    """Checks error message number against list of
    known database connection error numbers. If it
    matches, the connection failure is logged. If it
    is not a connection issue, the error message is
    printed to console output."""

    conn_err_list = [1045, 1049, 2003, 2005]
    err_list = [i for i in conn_err_list if i == err]

    if err_list:
        date = datetime.datetime.now()

        with open(f"{log_path}", 'w', encoding="UTF-8") as log:

            with open(f"{ini_path}", 'r', encoding="UTF-8") as ini:

                print(f"{date} - TEMPERATURE - "
                    "DATABASE CONNECTION FAILURE", file=log)
                print(err, file=log)
                print(ini.read(), file=log)
                print(err_text, file=log)



def date_check(config, config_v):
    """Checks to see when the last index report
    was ran. If it was within 30 days, a report
    is not run."""

    config.read("/home/netmaschal/python/snmp_temp_project/"
                "index_names/last_ran.ini")

    try:
        date = {
            'last_ran' : config["run_date"]["date"]
            }

        date_report = index_report.file_check(date, config_v)

    except KeyError:
        date_report = True

    return date_report



if __name__ == "__main__":
    main()
