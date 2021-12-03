import json

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from flask import session, request
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
    all_party_sql_default = """
        SELECT * FROM party ORDER BY playStartDatetime ASC
    """
    # ASC desc 합치기
    # sort key 있을때 ASC order sort
    all_party_sql_sort = """
        SELECT * FROM party ORDER BY %s %s;
    """
    
    # ServiceUser_Party table 에서 serviceUserID 일치하는 모든 party.
    my_parties_sql = """
        SELECT * FROM Party WHERE Party.partyID IN
        (SELECT ServiceUser_Party.partyID FROM ServiceUser_Party
            WHERE ServiceUser_Party.serviceUserID = %d);
    """
    conn = Connection.get_connect()
    cur = conn.cursor()

    #TODO: session['user_id'] 처리?
    #session 이 global 인지, local 인지 확인 필요.
    #TODO: user_id 로 조회 하는게 맞는건지 확인 필요.
    service_user_id = session['user'].get('serviceUserID')
    
    my_parties_list = []
    #TODO: null 아니라 none
    if(service_user_id != None):
        cur.execute(my_parties_sql, (service_user_id,))
        my_parties_list = cur.fetchall()
    else:
        my_parties_list = []
    #JSON serialize
    my_parties = PartyModel.serialize_party_list(my_parties_list)
        
    sort_key_name = request.args.get('sort')
    if(sort_key_name == None):
        cur.execute(all_party_sql_default)
    else:
        order_key_name = request.args.get('order')
        if(order_key_name != None):
            cur.execute(all_party_sql_sort,(sort_key_name,order_key_name))
        else:
            cur.execute(all_party_sql_default)
    
    all_parties_list = cur.fetchall()
    parties = PartyModel.serialize_party_list(all_parties_list)
    
    return render_template('parties.html', parties = parties, my_parties = my_parties)

@bp.route('/parties/detail/<int:partyid>/')
def party_detail_method():
    conn = Connection.get_connect()
    cur = conn.cursor()
    
    return render_template('partyDetail.html')

# 새로운 파티 생성 get method
@bp.route('/parties/new/', methods = ['GET', 'POST'])
def new_party_get_method():
    if session.method == 'GET':
        if 'user' in session:
            all_game_sql = """
                SELECT * FROM Game ORDER BY Game.name ASC;
            """
            
            cur.execute(all_game_sql)
            game_list = cur.fetchall()
            all_game_list = GameModel.serialize_game_list(game_list)
            return render_template('newParty.html', games = all_game_list)
        else:
            return redirect(url_for('/parties/'))
    
    elif session.method == 'POST':
        if 'user' in session:
            gameid = session.get('gameid')
            name = request.form.get('name')
            datetime_from_front_string = request.form.get('playStartDatetime')
            #TODO: format 
            #https://dateutil.readthedocs.io/en/stable/
            playStartDatetime = dateutil.parse(datetime_from_front_string)
            joinLink = request.form.get('joinLink')
            leaderID = session['user_id']
            
            try:
                cur.execute(
                sql.SQL("INSERT INTO {} VALUES ( DEFAULT , %s, %s, %s, %s, %s) RETURNING partyID").format(sql.identifier('Party'))
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
        
@bp.route('/parties/<int:partyid>/join/')
def party_join_method(partyid):
    conn = Connection.get_connect()
    cur = conn.cursor()
    is_my_party = False
    if 'user' in session:
        # serviceUserID, partyID 모두 같은 ServiceUser_Party row count.
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
    
@bp.route('/parties/<int:partyid>/secession/')
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