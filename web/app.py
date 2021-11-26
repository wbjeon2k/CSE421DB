import json
import os
import sys
import time
from datetime import datetime

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for

from database import Connection
from models import TestModel

app = Flask(__name__)
#db = SQLAlchemy()


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
    conn = Connection.get_connect()
    cur = conn.cursor()

    try:
        cur.execute("DROP TABLE IF EXISTS sample_db;")
        conn.commit()
    except Exception as e:
        print("ERROR at drop table :", e)

    create_tc_table = """
        CREATE TABLE sample_db (
        id INTEGER NOT NULL PRIMARY KEY,
        msg VARCHAR(50) NOT NULL,
        content VARCHAR(50) NOT NULL
        );
    """
    cur.execute(create_tc_table)
    conn.commit()

    insert_tc_format = """
        INSERT INTO sample_db VALUES (%i, %s)
    """
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
    conn = Connection.get_connect()
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
    conn = Connection.get_connect()
    cur = conn.cursor()
    #https://dololak.tistory.com/533
    cur.execute("SELECT * FROM sample_db WHERE id = %s", (id,))
    get_one = cur.fetchone()
    serialzed = TestModel(get_one[0], get_one[1], get_one[2]).serialize()
    return render_template('test_detail.html', test=serialzed)


if __name__ == '__main__':
    conn = Connection.get_connect()
    cur = conn.cursor()

    #main_blueprint = Blueprint('main', __name__, url_prefix='/main')
    #app.register_blueprint(main_blueprint)

    sql_file = open('./DB_SQL.sql','r').read()
    print(sql_file)
    cur.execute(sql_file)

    conn.commit()
    #cdir = os.path.dirname(os.path.abspath())
    #TODO: link with loader
    print("load successful")

    import views.party_views as party_views
    app.register_blueprint(party_views.bp)

    import views.game_views as game_views
    app.register_blueprint(game_views.bp)

    app.run(host='0.0.0.0', port=8088)
