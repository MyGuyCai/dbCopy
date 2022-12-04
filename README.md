# dbCopy
Automatically transfer mySQL select queries with foreign key restraints


TODO:
create the queries from the data

### Installation

    - `pip install -r requirements`

### Use

    - `python main.py`

### testing

    - Prerequisites:
        - install docker
        - installer liquibase

    - Running:
        - `docker compose up -d`
        - `liquibase --defaults-file=./testing/liquibaseSource.properties update`
        - `liquibase --defaults-file=./testing/liquibaseDestination.properties update`
        - `python ./testing/dummyData.py`
        - `python dbCopy.py`
        - enter the credentials for source
            - host: localhost
            - port: 3306
            - user: user
            - pass: pass
            - db: db
        - connect to source
        - enter the credentials for destination
            - host: localhost
            - port: 3307
            - user: user
            - pass: pass
            - db: db
        - connect to destination
        - enter a valid query
            - `SELECT * FROM parent AS p
               LEFT JOIN child as c
                   ON c.parent = p.id`



