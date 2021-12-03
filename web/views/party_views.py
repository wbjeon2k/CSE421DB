import json
import sys
import dateutil

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from flask import session, request, Response
from psycopg2 import sql
from psycopg2.sql import SQL
from database import Connection
from models import *
from datetime import *
from dateutil import *

# /party/... url 들을 포워딩 해주는 blueprint
bp = Blueprint("parties", __name__, url_prefix='/parties')

# /party 첫 페이지.
# 모든 파티들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def party_main():
    #parties 처음 들어왔을때 보여지는 table
    all_party_sql_default = "SELECT * FROM party ORDER BY playstart_datetime ASC"
    # sort_key, asc\desc
    all_party_sql_sort = "SELECT * FROM party ORDER BY {} {};"
    
    # service_user_party table 에서 service_user_id  일치하는 모든 party.
    my_parties_sql = "\
        SELECT * FROM party WHERE party.party_id IN \
        (SELECT service_user_party.party_id FROM service_user_party \
            WHERE service_user_party.service_user_id  = {});\
    "
    conn = Connection.get_connect()
    cur = conn.cursor()

    
    service_user_id = None
    if 'user' in session:
        service_user_id = session['user'].get('service_user_id')
    
    my_parties_list = []
    #TODO: null 아니라 none
    #if session.get('user') and session['user'].get('clanID') != None
    if(service_user_id != None):
        cur.execute(my_parties_sql.format(service_user_id))
        my_parties_list = cur.fetchall()
    else:
        my_parties_list = []
    #JSON serialize
    my_parties = partyModel.serialize_party_list(my_parties_list)
        
    sort_key_name = request.args.get('sort')
    if(sort_key_name == None):
        cur.execute(all_party_sql_default)
    else:
        order_key_name = request.args.get('order')
        if(order_key_name != None):
            cur.execute(all_party_sql_sort.format(sort_key_name,order_key_name))
        else:
            cur.execute(all_party_sql_default)
    
    all_parties_list = cur.fetchall()
    parties = partyModel.serialize_party_list(all_parties_list)
    
    return render_template('parties.html', parties = parties, my_parties = my_parties)

@bp.route('/<int:partyid>/')
def party_detail_method(partyid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    
    get_party_sql_base = "SELECT * FROM party WHERE (party_id = {})"
    get_party_sql = get_party_sql_base.format(partyid)
    
    cur.execute(get_party_sql)
    tmp = cur.fetchone()
    print(str(tmp))
    if(tmp == None):
        return "error: no such party. frontend error support needed"
    
    fetched_party = partyModel(tmp[0],tmp[1],tmp[2],tmp[3],tmp[4],tmp[5]).serialize()
    
    return render_template('partyDetail.html', party = fetched_party)
    #return "have to return partiies/partyid"

# 새로운 파티 생성 get method
@bp.route('/new/', methods = ['GET', 'POST'])
def new_party_method():
    conn = Connection.get_connect()
    cur = conn.cursor()
    
    if request.method == 'GET':
        if 'user' in session:
            all_game_sql = "SELECT * FROM game ORDER BY game.name ASC;"
            
            cur.execute(all_game_sql)
            game_list = cur.fetchall()
            all_game_list = partyModel.serialize_game_list(game_list)
            return render_template('newParty.html', games = all_game_list)
        else:
            return redirect(url_for('parties.party_main'))
    
    elif request.method == 'POST':
        if 'user' in session:
            gameid = request.form.get('gameID')
            
            name = request.form.get('name')
            name = add_single_quote(name)
            
            datetime_from_front_string = request.form.get('playStartDateTime')
            #TODO: format 
            #https://dateutil.readthedocs.io/en/stable/
            playstart_datetime = dateutil.parser.parse(datetime_from_front_string)
            playstart_datetime = add_single_quote(str(playstart_datetime))
            
            joinLink = request.form.get('joinLink')
            joinLink = add_single_quote(joinLink)

            sys.stdout.write(str(session['user']))
            sys.stdout.flush()
            
            leaderID = session['user'].get('service_user_id')
            
            if(gameid == None or name == None or datetime_from_front_string == None or joinLink == None):
                return "Missing information from front end!"
            
            try:
                #RETURNING party_id 통해 insert 후 party_id 가져오기.
                insert_new_party_sql_base = "INSERT INTO party VALUES ( DEFAULT , {}, TIMESTAMP {}, {}, {}, {}) RETURNING party_id"
                insert_new_party_sql = insert_new_party_sql_base.format(name, playstart_datetime,leaderID,joinLink,gameid)
                cur.execute(insert_new_party_sql)
            except Exception as error:
                conn.rollback()
                return "error"
            
            new_party_id = cur.fetchone()[0]
            conn.commit()

            return redirect(url_for('parties.party_detail_method', partyid = new_party_id ), code = 302)
            #return "OK"
        else:
            redirect(url_for('parties.party_main'))
        
@bp.route('/<int:partyid>/join/')
def party_join_method(partyid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    is_my_party = False
    if 'user' in session:
        # service_user_id , party_id 모두 같은 service_user_party row count.
        search_party_sql = """
            SELECT COUNT(*) FROM service_user_party
            WHERE service_user_id  = {} AND party_id = {};
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
                sql.SQL("INSERT INTO {} service_user_party ({}, {})").format(sql.identifier('party'))
                        ,[service_user_id, party_id]
                        )
            except Exception as error:
                return error
            redirect(url_for('parties/%d/' % partyid))    
        else:
            redirect(url_for('parties/%d/' % partyid))       
    else:
        redirect(url_for('parties/%d/' % partyid))    
    
@bp.route('/parties/<int:partyid>/secession/')
def party_secession_method(partyid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    if 'user' in session:
        search_party_sql = """
            SELECT COUNT(*) FROM service_user_party
            WHERE service_user_id  = {} AND party_id = {};
        """
        user_id = session['user_id']
        cur.execute(search_party_sql, (user_id, partyid,))
        search_cnt = cur.fetchone()[0]
        if(search_cnt != 0):
            redirect(url_for('parties/%d/' % partyid))
        elif(search_cnt == 0):
            party_exit_sql = """
                DELETE FROM service_user_party
                WHERE service_user_id  = {} AND party_id = {};
            """
            cur.execute(party_exit_sql, (user_id, partyid))
            conn.commit()
            redirect(url_for('parties/%d/' % partyid))    
        else:
            redirect(url_for('parties/%d/' % partyid))       
    else:
        redirect(url_for('parties/%d/' % partyid)) 