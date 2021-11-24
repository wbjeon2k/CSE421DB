import json
import os
import sys
import time
from datetime import datetime

import psycopg2 as pg2
from dotenv import dotenv_values
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from psycopg2 import Error, OperationalError

from models import TestModel

app = Flask(__name__)
#db = SQLAlchemy()

db_connection_info = dotenv_values()

POSTGRES = {
    'user': 'postgres',
    'password': db_connection_info['POSTGRES_PASSWORD'],
    'database': db_connection_info['POSTGRES_DB'],
    'host': db_connection_info['POSTGRES_CONTAINER_NAME'],
    'port': '5432'
}

FROMLOCAL = {
    'user': 'postgres',
    'pw': 'postgres',
    'db': 'party_finder',
    'host': 'localhost',
    'port': '55432'
}

'''
!!!실제 제출할때는 connect 정보 바꿔야 한다!!!
'''
def get_connect():
        #when running at docker container party_finder
        # If webserver container up before db container, webserver cannot connect to DB
        # Therefore, if fail to connection, sleep some times and retry connection
        conn = None
        MAX_RETRY_COUNT = 6  # retry max count, if db connection failed, retry connection
        for i in range(MAX_RETRY_COUNT):
            try:
                conn = pg2.connect(**POSTGRES)  # Try to connect to DB
            except OperationalError:
                if i < MAX_RETRY_COUNT - 1:  # Last loop pass sleep even though fail to connect
                    sleep_time = i * 2  # Sleep time is accumulated for each failure
                    print(f'PostgreSQL container not ready yet. Sleep {sleep_time} sec and try reconnection', file=sys.stderr)
                    # Flush stdout, stderr for printing to docker log
                    sys.stdout.flush()
                    sys.stderr.flush()
                    time.sleep(sleep_time)
                    continue
            break
        else:  # If for is end without break -> Exceed max try count
            raise ConnectionError('Cannot connect to DB')

        print('DB Connection success', file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()

        #when running at local
        # conn = pg2.connect(database="party_finder",user="postgres",password="ideal-entropy-fanfold-synopsis-grazier",host="localhost",port="55432")
        return conn

class connection:
    def __init__(self):
        self.connect_info = pg2.connect(database="party_finder",user="postgres",password="ideal-entropy-fanfold-synopsis-grazier",host="localhost",port="55432")

    def get_connect():
        #when running at docker container party_finder
        #conn=pg2.connect(database="party_finder",user="postgres",password="ideal-entropy-fanfold-synopsis-grazier",host="party_finder_postgres",port="5432")

        #when running at local
        conn = pg2.connect(database="party_finder",user="postgres",password="ideal-entropy-fanfold-synopsis-grazier",host="localhost",port="55432")
        return conn

#test main page for connection test
@app.route("/")
def main():
    return 'This is main page'

#test page for Jinja2 template html rendering test
@app.route("/test/base")
def page_jinja2_base():
    return render_template("base.html")

#generate sample_db table for test/chk
@app.route("/test/gen", methods=["GET", "POST"])
def test_table_gen():
    conn = get_connect()
    cur = conn.cursor()

    try:
        cur.execute("DROP TABLE IF EXISTS sample_db;")
        conn.commit()
    except Exception as e:
        print("ERROR at drop table :", e)

    create_tc_table = '''
        CREATE TABLE sample_db (
        id INTEGER NOT NULL PRIMARY KEY,
        msg VARCHAR(50) NOT NULL,
        content VARCHAR(50) NOT NULL
        );
    '''
    cur.execute(create_tc_table)
    conn.commit()

    insert_tc_format = '''
        INSERT INTO sample_db VALUES (%i, %s)
    '''
    msg_format = "message"
    content_format = "content number %i"
    for i in range(300):
        cur.execute('INSERT INTO sample_db (id, msg, content) VALUES (%s, %s, %s)', (i,msg_format, (content_format % i)))
        #conn.commit()
    conn.commit()
    cur.close()

    ret = 'successfully added sample_db'
    return ret


### list 전체 fetchall, serialize, template 에 rendering.
@app.route("/test/chk")
def test_table_chk():
    conn = get_connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sample_db")
    select_all = cur.fetchall()
    ret = []
    for t in select_all:
        ret.append(TestModel(t[0], t[1], t[2]).serialize())
    #to_json = json.dumps(ret)
    print(ret)
    return render_template('test_list.html', test_list=ret)
    #return to_json


### ID가 같은 객체 1개 fetchone, serialize 하여 template 에 rendering.
@app.route('/test/detail/<int:id>/')
def detail(id):
    conn = get_connect()
    cur = conn.cursor()
    #https://dololak.tistory.com/533
    cur.execute("SELECT * FROM sample_db WHERE id = %s", (id,))
    get_one = cur.fetchone()
    serialzed = TestModel(get_one[0], get_one[1], get_one[2]).serialize()
    return render_template('test_detail.html', test=serialzed)


if __name__ == '__main__':
    get_connect()

    #main_blueprint = Blueprint('main', __name__, url_prefix='/main')
    #app.register_blueprint(main_blueprint)

    sql_file = open('./DB_SQL.sql','r').read()
    print(sql_file)
    cursor = get_connect().cursor()
    cursor.execute(sql_file)
    #cdir = os.path.dirname(os.path.abspath())
    #TODO: link with loader
    print("load successful")

    import views.party_views as party_views
    app.register_blueprint(party_views.bp)

    import views.game_views as game_views
    app.register_blueprint(game_views.bp)

    app.run()
