from scripts import connection
from random import randint


def dump_dummy_data():
    cnx = connection.create_connection({
        'host': 'localhost',
        'port': '3306',
        'user': 'root',
        'pass': 'root',
        'db': 'db',
    })

    if cnx['response']:
        cnx = cnx['payload']
        print('Connection made\nLoading dummy data into database')

        country_data = [(1, 'WALES'), (2, 'ENGLAND'), (3, 'SCOTLAND'), (4, 'NORTHERN IRELAND')]
        parent_data = []
        child_data = []
        grandparent_data = []

        for index in range(0, 10001):
            parent_data.append((index, f"first_name{index}", f"last_name{index}"))
            child_data.append((index, f"first_name{index}", f"last_name{index}", index))
            grandparent_data.append((index, f"first_name{index}", f"last_name{index}", index, randint(1, 4)))

        connection.insert_data(cnx, 'parent', parent_data)
        connection.insert_data(cnx, 'child', child_data)
        connection.insert_data(cnx, 'db2.country', country_data)
        connection.insert_data(cnx, 'db2.grandparent', grandparent_data)

        print('Dummy data successfully entered into database\nClosing connection')
        connection.close_connection(cnx)
    else:
        print(f"Connection failed, error: {cnx['payload']}")


if __name__ == '__main__':
    dump_dummy_data()
    # cnx = connection.create_connection({
    #     'host': 'localhost',
    #     'port': '3306',
    #     'user': 'user',
    #     'pass': 'pass',
    #     'db': 'db',
    # })
    # cnx = cnx['payload']
    # connection.get_tables(cnx)
