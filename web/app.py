import json
import os
import sys
import time
from datetime import datetime

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, session, url_for
from psycopg2.errors import DuplicateTable, UniqueViolation
from secret_key import secret_key

from database import Connection
from models import *

app = Flask(__name__)
# db = SQLAlchemy()


# test main page for connection test
@app.route('/')
def main():
    conn = Connection.get_connect()
    cur = conn.cursor()
    # Get top 20 popular parties, popular means how may user were joined
    popular_parties_query = (
        'SELECT party_id, name, playstart_datetime, leader_id, joinLink, game_id, '
        '(SELECT COUNT(*) FROM service_user_party WHERE party_id=party.party_id) as popular '
        'FROM party ORDER BY popular DESC LIMIT 20'
    )
    # Get top 20 popular clans, popular means how may user were joined
    popular_clans_query = (
        'SELECT clan_id, name, leader_id, '
        '(SELECT COUNT(*) FROM service_user WHERE clan_id=clan.clan_id) as popular '
        'FROM clan ORDER BY popular DESC LIMIT 20'
    )
    cur.execute(popular_parties_query)
    popular_parties_fetch = cur.fetchall()
    popular_parties = PartyModel.serialize_party_list(popular_parties_fetch)
    
    cur.execute(popular_clans_query)
    popular_fetch = cur.fetchall()
    popular_clan_objs = [ClanModel(*each, related_fetch=True) for each in popular_fetch]
    popular_clans = ClanModel.serialize_clan_list(popular_clan_objs)

    return render_template('base.html', popular_parties=popular_parties, popular_clans=popular_clans)


# generate sample_db table for test/chk
@app.route('/gen', methods=['GET', 'POST'])
def test_table_gen():
    conn = Connection.get_connect()
    cur = conn.cursor()

    try:
        cur.execute('DROP TABLE IF EXISTS sample_db;')
        conn.commit()
    except Exception as e:
        print('ERROR at drop table :', e)

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
    msg_format = 'message'
    content_format = 'content number %i'
    for i in range(300):
        cur.execute(
            'INSERT INTO sample_db (id, msg, content) VALUES (%s, %s, %s)',
            (i, msg_format, (content_format % i)),
        )
        # conn.commit()
    conn.commit()
    cur.close()

    ret = 'successfully added sample_db'
    return ret


### list 전체 fetchall, serialize, template 에 rendering.
@app.route('/chk')
def test_table_chk():
    conn = Connection.get_connect()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sample_db')
    select_all = cur.fetchall()
    ret = []
    for t in select_all:
        ret.append(TestModel(t[0], t[1], t[2]).serialize())
    # to_json = json.dumps(ret)
    print(ret)
    return render_template('test_list.html', test_list=ret)
    # return to_json


### ID가 같은 객체 1개 fetchone, serialize 하여 template 에 rendering.
@app.route('/detail/<int:id>/')
def detail(id):
    conn = Connection.get_connect()
    cur = conn.cursor()
    # https://dololak.tistory.com/533
    cur.execute('SELECT * FROM sample_db WHERE id = %s', (id,))
    get_one = cur.fetchone()
    serialzed = TestModel(get_one[0], get_one[1], get_one[2]).serialize()
    return render_template('test_detail.html', test=serialzed)


### Load initial data
@app.route('/initialize/data/')
@app.before_first_request
def initialize_data():
    conn = Connection.get_connect()
    cur = conn.cursor()

    session.clear()

    sql_file = open('../DB_SQL.sql', 'r').read()
    print(sql_file)
    try:
        cur.execute(sql_file)
        conn.commit()
        # print("load successful")
    except pg2.errors.DuplicateTable as d:
        conn.rollback()
        conn.commit()
        # return "table already exist; pass table creating"

    try:
        with open('../data/datasets/tags.json') as f:
            tags = json.load(f)
        for tag in tags:
            cur.execute(
                'INSERT INTO tag (tag_id, name) VALUES (%s, %s)', (tag['id'], tag['name'])
            )
        conn.commit()

        with open('../data/datasets/game_rank_list.json', encoding='utf-8') as f:
            games = json.load(f)
        for game in games:
            cur.execute(
                'INSERT INTO game (game_id, name) VALUES (%s, %s)', (game['id'], game['name'])
            )
        conn.commit()

        with open('../data/datasets/game_tag_list.json') as f:
            game_tags = json.load(f)
        for game_tag in game_tags:
            for tag_id in game_tag['tags']:
                cur.execute(
                    'INSERT INTO game_tag (game_id, tag_id) VALUES (%s, %s)',
                    (game_tag['id'], tag_id),
                )
        # Make free board (자유게시판)
        cur.execute('INSERT INTO board (board_id, clan_id) VALUES (DEFAULT, NULL)')
    except Exception as u:  # already inserted data -> Violate unique key constraint in PK
        conn.rollback()  # rollback all queries; not reflected to real db
        # return 'Faild; Already inserted data'

    conn.commit()
    return 'Success; Insert initial data'


if __name__ == '__main__':
    conn = Connection.get_connect()
    cur = conn.cursor()

    # main_blueprint = Blueprint('main', __name__, url_prefix='/main')
    # app.register_blueprint(main_blueprint)
    conn.commit()

    import views.game_views as game_views
    import views.login_view as login_views
    import views.logout_views as logout_views
    import views.party_views as party_views
    import views.register_view as register_views
    import views.clan_views as clan_views
    import views.user_views as user_views
    import views.board_views as board_views

    app.register_blueprint(party_views.bp)
    app.register_blueprint(game_views.bp)
    app.register_blueprint(register_views.bp)
    app.register_blueprint(login_views.bp)
    app.register_blueprint(logout_views.bp)
    app.register_blueprint(clan_views.bp)
    app.register_blueprint(user_views.bp)
    app.register_blueprint(board_views.bp)

    app.secret_key = secret_key.from_file('/tmp/secret_key')
    app.run(host='0.0.0.0', port=8088)
