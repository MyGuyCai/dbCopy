import mysql.connector
from mysql.connector import errorcode


def create_connection(credentials: dict) -> dict:
    """
    :param credentials: dictionary of required credentials
    :return: { response: boolean, payload: error or connection }
    """
    try:
        cnx = mysql.connector.connect(
            host=credentials['host'],
            port=credentials['port'],
            user=credentials['user'],
            password=credentials['pass'],
            database=credentials['db'],
        )
        cnx.autocommit = True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return {
                'response': False,
                'payload': "Something is wrong with your user name or password"
            }
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return {
                'response': False,
                'payload': "Database does not exist"
            }
        else:
            return {
                'response': False,
                'payload': err
            }
    else:
        return {
            'response': True,
            'payload': cnx
        }


def close_connection(database: mysql.connector):
    """
    :param database: Database connection
    """
    database.close()


def insert_data(database: mysql.connector, table_name: str, values: list[tuple], columns: list[str] = None):
    """
    :param database: Database connection
    :param table_name: Table to insert into
    :param values: List of tuples of values
    :param columns: Optional list of column names
    :return:
    """
    if columns is None:
        columns = []
    cursor = database.cursor()
    column_query_string = ''
    if columns is not None:
        column_query_string = f"({','.join(columns)})"
    query = f"INSERT INTO {table_name}{column_query_string} VALUES " + \
            ",".join(f"({''.join('%s,' for _ in values[0])[:-1]})" for _ in values)
    flattened_values = [item for sublist in values for item in sublist]
    cursor.execute(query, flattened_values)
    database.commit()


def get_database_structure(database: mysql.connector):
    cursor = database.cursor()
    cursor.execute(f"select * from information_schema.KEY_COLUMN_USAGE")
    database_structure = {
        'schema_tables': {},
        'foreign_keys': {}
    }
    for fk in cursor.fetchall():
        if fk[1] not in ['mysql', 'sys']:
            if fk[2] == 'PRIMARY':
                try:
                    database_structure['schema_tables'][fk[4]].append(fk[5])
                except KeyError:
                    database_structure['schema_tables'][fk[4]] = [fk[5]]
            else:
                database_structure['foreign_keys'][fk[2]] = {
                    'schema': fk[1],
                    'table': fk[5],
                    'column': fk[6],
                    'foreign_schema': fk[9],
                    'foreign_table': fk[10],
                    'foreign_column': fk[11],
                    'position_in_unique_restraint': fk[8]
                }

    return database_structure
