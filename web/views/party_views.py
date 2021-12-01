import json

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from flask import session, request
from psycopg2 import sql
from psycopg2.sql import SQL
from database import Connection
from models import *
from datetime import datetime, timezone

# /party/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('parties', __name__, url_prefix='/parties')

# /party 첫 페이지.
# 모든 파티들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def party_main():
    all_party_sql_default = """
        SELECT * FROM party ORDER BY playStartDatetime ASC
    """
    all_party_sql_sort_asc = """
        SELECT * FROM party ORDER BY %s ASC;
    """
    all_party_sql_sort_desc = """
        SELECT * FROM party ORDER BY %s DESC;
    """
    my_parties_sql = """
        SELECT * FROM Party WHERE Party.partyID IN
        (SELECT ServiceUser_Party.partyID FROM ServiceUser_Party
            WHERE ServiceUser_Party.serviceUserID = %d);
    """
    conn = Connection.get_connect()
    cur = conn.cursor()

    service_user_id = session['user_id']
    my_parties_list = []
    if(service_user_id != NULL):
        cur.execute(my_parties_sql, (service_user_id,))
        my_parties_list = cur.fetchall()
    else:
        my_parties_list = []
    my_parties = PartyModel.serialize_party_list(my_parties_list)
        
    sort_key_name = request.args.get('sort')
    if(sort_key_name == NULL):
        cur.execute(all_party_sql_default)
    else:
        order_key_name = request.args.get('order')
        if(order_key_name == 'asc'):
            cur.execute(all_party_sql_sort_asc, (sort_key_name,))
        elif(order_key_name == 'desc'):
            cur.execute(all_party_sql_sort_desc,(sort_key_name,))
        else:
            cur.execute(all_party_sql_default)
    
    all_parties_list = cur.fetchall()
    parties = PartyModel.serialize_party_list(all_parties_list)
    #all_party_json_list = json.dumps(all_party_list)
    return render_template('party_list.html', parties = parties, my_parties = my_parties)

# 새로운 파티 생성 get method
@bp.route('/parties/new/', method = 'GET')
def new_party_get_method():
    if 'user' in session:
        all_game_sql = """
            SELECT * FROM Game ORDER BY Game.name ASC;
        """
        
        cur.execute(all_game_sql)
        game_list = cur.fetchall()
        all_game_list = GameModel.serialize_game_list(game_list)
        return render_template('new_party_template.html', games = all_game_list)
    else:
        return redirect(url_for('/parties/'))
    
@bp.route('/parties/new/', method = 'POST')
def new_party_post_method():
    conn = Connection.get_connect()
    cur = conn.cursor()
    if 'user' in session:
        gameid = session.get('gameid')
        name = request.form.get('name')
        datetime_from_front = request.form.get('playStartDatetime')
        playStartDatetime = datetime.strftime(datetime_from_front)
        joinLink = request.form.get('joinLink')
        leaderID = session['user_id']
        
        try:
            cur.execute(
            sql.SQL("INSERT INTO {} VALUES (%s, %s, %s, %s, %s, %s) RETURNING partyID").format(sql.identifier('Party'))
                    ,[name, playStartDatetime,leaderID,joinLink,gameid]
                    )
        except Exception as error:
            return error
        
        conn.commit()
        
        new_party_id = cur.fetchone()[0]
        new_party_url = 'parties/%s' % new_party_id
        return redirect(url_for(new_party_url))
    else:
        redirect(url_for('parties/'))
        
@bp.route('/parties/<int:partyid>/join/', method = 'GET')
def party_detail_method(partyid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    is_my_party = False
    if 'user' in session:
        search_party_sql = """
            SELECT COUNT(*) FROM ServiceUser_Party
            WHERE serviceUserID = %s AND partyID = %s;
        """
        user_id = session['user_id']
        cur.execute(search_party_sql, (user_id, partyid,))
        search_cnt = cur.fetchone()[0]
        if(search_cnt != 0):
            redirect(url_for('parties/%d/' % partyid))
        elif(search_cnt == 0):
            try:
                service_user_id = user_id
                party_id = partyid
                cur.execute(
                sql.SQL("INSERT INTO {} ServiceUser_Party (%s, %s)").format(sql.identifier('Party'))
                        ,[service_user_id, party_id]
                        )
            except Exception as error:
                return error
            redirect(url_for('parties/%d/' % partyid))    
        else:
            redirect(url_for('parties/%d/' % partyid))       
    else:
        redirect(url_for('parties/%d/' % partyid))    
    
@bp.route('/parties/<int:partyid>/join/', method = 'GET')
def party_secession_method(partyid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    if 'user' in session:
        search_party_sql = """
            SELECT COUNT(*) FROM ServiceUser_Party
            WHERE serviceUserID = %s AND partyID = %s;
        """
        user_id = session['user_id']
        cur.execute(search_party_sql, (user_id, partyid,))
        search_cnt = cur.fetchone()[0]
        if(search_cnt != 0):
            redirect(url_for('parties/%d/' % partyid))
        elif(search_cnt == 0):
            party_exit_sql = """
                DELETE FROM ServiceUser_Party
                WHERE serviceUserID = %s AND partyID = %s;
            """
            cur.execute(party_exit_sql, (user_id, partyid))
            conn.commit()
            redirect(url_for('parties/%d/' % partyid))    
        else:
            redirect(url_for('parties/%d/' % partyid))       
    else:
        redirect(url_for('parties/%d/' % partyid)) 