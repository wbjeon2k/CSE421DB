from datetime import time
import sys
import time

import psycopg2 as pg2
from dotenv import dotenv_values
from psycopg2 import OperationalError


db_connection_info = dotenv_values('../.env')

POSTGRES = {
    'user': 'postgres',
    'password': db_connection_info['POSTGRES_PASSWORD'],
    'database': db_connection_info['POSTGRES_DB'],
    'host': db_connection_info['POSTGRES_CONTAINER_NAME'],
    'port': '5432'
}

class Connection:  # Factory pattern, Only one connection object create per one server
    conn = None

    @classmethod
    def _make_connection(cls):
        #when running at docker container party_finder
        # If webserver container up before db container, webserver cannot connect to DB
        # Therefore, if fail to connection, sleep some times and retry connection
        MAX_RETRY_COUNT = 6  # retry max count, if db connection failed, retry connection
        for i in range(MAX_RETRY_COUNT):
            try:
                cls.conn = pg2.connect(**POSTGRES)  # Try to connect to DB
            except OperationalError:
                if i < MAX_RETRY_COUNT - 1:  # Last loop pass sleep even though fail to connect
                    sleep_time = (i + 1) * 2  # Sleep time is accumulated for each failure
                    print(f'PostgreSQL container not ready yet. Sleep {sleep_time} sec and try reconnection', file=sys.stderr)
                    # Flush stdout, stderr for printing to docker log
                    sys.stdout.flush()
                    sys.stderr.flush()
                    time.sleep(sleep_time)
                continue
            break
        else:  # If for is end without break -> Exceed max try count
            raise ConnectionError('Cannot connect to DB')

        sys.stdout.flush()
        sys.stderr.flush()

    @classmethod
    def get_connect(cls):
        if cls.conn is None:
            cls._make_connection()
        return cls.conn
