"""Module for creating and filling the temp table.
Loads the temp_level JSON file and creates a temp
table for each switch.
"""

import json
from mysql.connector import errors


def json_load(file, please):
    """Loads the JSON file and deletes/creates the temp table
    for each switch if already created. It then iterates
    over each switch's inlet sensor, adding it to the table.
    """

    with open(f"{file}", 'r', encoding="UTF-8") as draft:

        interfaces = json.load(draft)

        for switch in interfaces:

            switch_name = switch["Switch"]

            if "-" in switch_name:
                switch_name = switch_name.replace("-", "_")

            temp_table_init(switch_name, please)

            for index, data in switch.items():

                if index.isnumeric():

                    temp_table_fill(
                            please,
                            switch_name,
                            index,
                            data
                            )



def temp_table_init(switch, please):
    """SQL command executor for creating the temp
    table for each switch. Deletes table first if it already
    exists. Date column is auto-generated on insert.
    """

    del_statement = f"""
    DROP TABLE IF EXISTS temp_{switch};"""

    statement = f"""
    CREATE TABLE temp_{switch}
    (id SERIAL,
    int_index int,
    switch varchar(80),
    temperature numeric,
    date date,
    PRIMARY KEY (id),
    CONSTRAINT temp_{switch}_fk
        FOREIGN KEY (int_index)
        REFERENCES index_{switch}(int_index)
        ON DELETE CASCADE)"""

    try:
        please.execute(del_statement)
        please.execute(statement)

    except errors.ProgrammingError:
        print("Something went wrong during temp table creation")



def temp_table_fill(please, switch, index, data):
    """SQL command executor for filling in the temp_level
    table with each switch's interface.
    """

    statement = f"""
    INSERT INTO temp_{switch} (int_index, switch, temperature, date)
    VALUES ({index}, '{switch}', {data}, CURDATE())"""

    try:
        please.execute(statement)

    except errors.ProgrammingError:
        print("Something went wrong during temp table filling.")
