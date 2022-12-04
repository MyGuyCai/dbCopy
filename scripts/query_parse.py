from scripts import connection
import re


def parse_query_tables(query: str, default_schema: str):
    def recursion_joins(recur_query):
        join_selects = "^(left\s|inner\s)?join\s(\w.*?)\sas\s(\w.*?)\son\s(\w.*?)=\s(\w.*?)\s(and\s(\w.*?))?((left\s|inner\s)?join.*)"
        grouped_query = re.search(join_selects, recur_query)
        try:
            recursion_joins(grouped_query.group(8))
            join_table = grouped_query.group(2)
            join_table_selector = grouped_query.group(3)
        except AttributeError:
            join_final_select = "^(left\s|inner\s)?join\s(\w.*?)\sas\s(\w.*?)\son\s.*$"
            last_grouped_query = re.search(join_final_select, recur_query)
            join_table = last_grouped_query.group(2)
            join_table_selector = last_grouped_query.group(3)
        add_table_to_dict(join_table, join_table_selector)

    def add_table_to_dict(join_table: str, join_table_selector: str):
        if '.' not in join_table:
            join_table = f"{default_schema}.{join_table}"
        tables_dict[join_table] = join_table_selector

    tables_dict = {}
    transfer_queries = []
    initial_select = "^select\s(\w.*|[*])\sfrom\s(\w.*?)\sas\s(\w.*?)\s(\w.*?)where(?!.*where).*"

    # format the query and create groups
    reduced_query = re.search(initial_select, query)

    # get the initial table and the join tables
    initial_table = reduced_query.group(2)
    initial_table_identifier = reduced_query.group(3)
    join_query = reduced_query.group(4)

    # add all tables in query to dict
    add_table_to_dict(initial_table, initial_table_identifier)
    recursion_joins(join_query)

    return tables_dict


def parse_required_tables(query_tables: dict, structure: dict):
    def get_constrained_tables(table_to_check, base_table=None):
        if base_table is None:
            base_table = table_to_check
            required_tables[base_table] = []

        for fk_restraint in structure['foreign_keys']:
            fk_table = f"{structure['foreign_keys'][fk_restraint]['schema']}" \
                       f".{structure['foreign_keys'][fk_restraint]['table']}"
            new_fk_table = f"{structure['foreign_keys'][fk_restraint]['foreign_schema']}" \
                           f".{structure['foreign_keys'][fk_restraint]['foreign_table']}"
            if fk_table == table_to_check:
                required_tables[base_table].append(new_fk_table)
            if new_fk_table not in required_tables:
                get_constrained_tables(new_fk_table)

    tables_to_check = [x for x in query_tables]
    required_tables = {}

    for table in tables_to_check:
        get_constrained_tables(table)
    return required_tables


def parse_transfer_queries(query, required_tables, default_schema, structure):
    def fix_table_name(table_name):
        if '.' not in table_name:
            table_name = f"{default_schema}.{table_name}"
        return table_name

    def parse_additional_queries(query_string):
        find_inners = "(left\s|inner\s)?join\s(\w.*?)\sas\s(\w.*?)\son\s(\w.*?)=\s(\w.*?)\s(and\s(\w.*?))?((left\s|inner\s)?join.*)"
        final_inners = "^(left\s|inner\s)?join\s(\w.*?)\sas\s(\w.*?)\son\s.*$"

        try:
            additional_query = re.search(find_inners, query_string)
            table = fix_table_name(additional_query.group(2))
        except AttributeError:
            additional_query = re.search(final_inners, query_string)
            table = fix_table_name(additional_query.group(2))

        for req_table in required_tables[table]:
            if req_table not in tables_transferred:
                print(req_table)
                print(create_query_middle(req_table))

        try:
            parse_additional_queries(additional_query.group(8))
        except IndexError:
            pass

    def create_query_middle(table_name):
        schema = table_name.split(".")[0]
        table = table_name.split(".")[1]
        for entry in structure['foreign_keys']:
            if structure['foreign_keys'][entry]['schema'] == schema and structure['foreign_keys'][entry]['table'] == table:
                column = structure['foreign_keys'][entry]['column']
                fk_table = f"{structure['foreign_keys'][entry]['foreign_schema']}.{structure['foreign_keys'][entry]['foreign_column']}"
                print(column, fk_table)
                print("hi")
        return f"{query_start}LEFT JOIN {table_name} as c2 ON c2.{column} = p.{fk_table}"

    def create_query_start(table_name, identifier):
        return f"SELECT {identifier}.* FROM {table_name} AS {identifier} "

    initial_select = "^select\s(\w.*|[*])\sfrom\s(\w.*?)\sas\s(\w.*?)\s(\w.*?)where(?!.*where)(.*)"
    reduced_query = re.search(initial_select, query)

    query_start = create_query_start(fix_table_name(reduced_query.group(2)), reduced_query.group(3))
    query_end = f"WHERE{reduced_query.group(5)}"

    transfer_queries = [f"{query_start}{query_end}"]
    tables_transferred = [fix_table_name(reduced_query.group(2))]

    parse_additional_queries(reduced_query.group(4))

    print(tables_transferred)
    print(transfer_queries)
    return transfer_queries


def get_required_queries(database, default_schema, query):
    # format the original query
    query_formatted_lower = query.lower().replace("\n", "").strip()
    query_formatted = re.sub(' +', ' ', query_formatted_lower)
    # get database schema structure
    structure = connection.get_database_structure(database)
    # get tables from query
    result = parse_query_tables(query_formatted, default_schema)
    # get all required tables
    required_tables = parse_required_tables(result, structure)
    # get the transfer queries in order
    parse_transfer_queries(query_formatted, required_tables, default_schema, structure)

    return required_tables


if __name__ == '__main__':
    cnx = connection.create_connection({
        'host': 'localhost',
        'port': '3306',
        'user': 'root',
        'pass': 'root',
        'db': 'db',
    })
    cnx = cnx['payload']

    db_query = """ SELECT * FROM parent AS p
                LEFT JOIN child as c
                    ON c.parent = p.id
                LEFT JOIN db2.grandparent as g
                    ON g.grand_child = c.id
                WHERE p.firstname = 'first_name1576'"""

    req = get_required_queries(cnx, "db", db_query)
    print(req)
