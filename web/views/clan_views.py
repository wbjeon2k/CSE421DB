# members 를 list로 넘겨준다.
import json
import sys
import dateutil

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for, session
from jinja2 import Template
from flask import session, request, Response
from psycopg2 import sql
from psycopg2.sql import SQL
from database import Connection
from models import *
from datetime import *
from dateutil import *

# /party/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('clans', __name__, url_prefix='/clans')

# /clans 첫 페이지.
# 모든 클랜들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def clan_main():
    # clans 처음 들어왔을때 보여지는 table
    all_clan_sql_default = (
        'SELECT clan_id, name, leader_id, '
        '(SELECT COUNT(*) FROM service_user WHERE clan_id=clan.clan_id) as popular '
        'FROM clan'
    )
    # sort_key, asc\desc
    all_clan_sql_sort = (
        'SELECT clan_id, name, leader_id, '
        '(SELECT COUNT(*) FROM service_user WHERE clan_id=clan.clan_id) as popular '
        'FROM clan ORDER BY {} {};'
    )

    # service_user_party table 에서 service_user_id  일치하는  clan.
    my_clan_sql = (
        'SELECT clan_id, name, leader_id, '
        '(SELECT COUNT(*) FROM service_user WHERE clan_id=clan.clan_id) as popular '
        'FROM clan '
        'WHERE clan.clan_id='
        '(SELECT clan_id FROM service_user '
        'WHERE service_user.service_user_id=%s);'
    )
    conn = Connection.get_connect()
    cur = conn.cursor()

    service_user_id = None
    if 'user' in session:
        service_user_id = session['user'].get('service_user_id')

    my_clan = None

    if service_user_id != None:
        cur.execute(my_clan_sql, (service_user_id,))
        my_clan_item = cur.fetchone()
        if my_clan_item is not None:
            # JSON serialize
            my_clan = ClanModel(*my_clan_item, related_fetch=True).serialize()
    else:
        my_clan = None

    sort_key_name = request.args.get('sort')
    if sort_key_name == None:
        cur.execute(all_clan_sql_default)
    else:
        order_key_name = request.args.get('order')
        if order_key_name != None:
            cur.execute(all_clan_sql_sort.format(sort_key_name, order_key_name))
        else:
            cur.execute(all_clan_sql_default)

    all_clans_fetch = cur.fetchall()
    all_clans_objs = [ClanModel(*each, related_fetch=True) for each in all_clans_fetch]
    clans = ClanModel.serialize_clan_list(all_clans_objs)

    return render_template('clans.html', clans=clans, my_clan=my_clan)


@bp.route('/<int:clanid>/')
def clan_detail_method(clanid):
    conn = Connection.get_connect()
    cur = conn.cursor()

    # 주어진 clanid 로 파티 찾기.
    get_clan_sql = (
        'SELECT clan_id, name, leader_id, '
        '(SELECT COUNT(*) FROM service_user WHERE clan_id=clan.clan_id) as popular '
        'FROM clan '
        'WHERE (clan_id=%s)'
    )

    cur.execute(get_clan_sql, (clanid,))
    clan_info = cur.fetchone()
    if clan_info == None:
        return 'error: no such party. frontend error support needed'

    # PartyModel 객체에 게임 이름 추가.
    fetched_clan = ClanModel(*clan_info, related_fetch=True)

    retrieve_members_query = (
        'SELECT service_user_id, email, nickname, isAdmin, clan_id '
        'FROM service_user WHERE clan_id=%s'
    )
    cur.execute(retrieve_members_query, (clanid,))
    members_tuple = cur.fetchall()
    members_objs = [ServiceUserModel(*each) for each in members_tuple]
    members = ServiceUserModel.serialize_service_user_list(members_objs)

    return render_template('clanDetail.html', clan=fetched_clan, members=members)


# 새로운 클랜 생성 get method
@bp.route('/new/', methods=['GET', 'POST'])
def new_clan_method():
    conn = Connection.get_connect()
    cur = conn.cursor()

    if request.method == 'GET':
        if 'user' in session:
            return render_template('newClan.html')
        else:
            return redirect(url_for('login.login_main'))

    elif request.method == 'POST':
        if 'user' not in session:
            return redirect(url_for('parties.party_main'))
            
        name = request.form.get('name')
        leader_id = session['user'].get('service_user_id')

        try:
            # RETURNING clan_id 통해 insert 후 clan_id 가져오기.
            insert_new_clan_sql_base = 'INSERT INTO clan VALUES ( DEFAULT, %s, %s) RETURNING clan_id'
            cur.execute(insert_new_clan_sql_base, (name, leader_id))
        except Exception as error:
            conn.rollback()
            return 'error'

        new_clan_id = cur.fetchone()[0]

        # Update logged in user clan id to new clan id
        user_clan_id_update_query = 'UPDATE service_user SET clan_id=%s WHERE service_user_id=%s'
        cur.execute(user_clan_id_update_query, (new_clan_id, leader_id))

        # Make board for this clan
        create_clan_board_query = 'INSERT INTO board VALUES (DEFAULT, %s)'
        cur.execute(create_clan_board_query, (new_clan_id,))

        conn.commit()

        # update session valuel; must using .update() method
        session_user = session.get('user')
        session_user['clanID'] = new_clan_id
        session.update(user=session_user)

        return redirect(
            url_for('clans.clan_detail_method', clanid=new_clan_id), code=302
        )


@bp.route('/<int:clanid>/join/')
def clan_join_method(clanid):
    conn = Connection.get_connect()
    cur = conn.cursor()

    if 'user' not in session:
        return redirect(url_for('login'), code=302)
        
    if session['user']['clanID'] is not None:  # already joined clan
        return redirect(url_for('clans.clan_detail_method', clanid=clanid), code=302)

    # Update now logged in user's clan id
    update_clan_id_query = 'UPDATE service_user SET clan_id=%s WHERE service_user_id=%s;'
    user_id = session['user'].get('service_user_id')
    cur.execute(update_clan_id_query, (clanid, user_id))
    conn.commit()

    # update session valuel; must using .update() method
    session_user = session.get('user')
    session_user['clanID'] = clanid
    session.update(user=session_user)

    return redirect(url_for('clans.clan_detail_method', clanid=clanid), code=302)


@bp.route('/<int:clanid>/secession/')
def clan_secession_method(clanid):
    conn = Connection.get_connect()
    cur = conn.cursor()

    if 'user' not in session:
        return redirect(url_for('login'), code=302)
        
    if session['user']['clanID'] is None:  # already joined clan
        return redirect(url_for('clans.clan_detail_method', clanid=clanid), code=302)
    elif session['user']['clanID'] != clanid:  # not member of this clan
        return redirect(url_for('clans.clan_detail_method', clanid=clanid), code=302)

    user_id = session['user']['service_user_id']
    # Check for logged in user is leader of clan -> if logged in user is leader of clan, user cannot leave this clan
    retrieve_clan_leader_count_query = 'SELECT count(*) FROM clan WHERE leader_id=%s'
    cur.execute(retrieve_clan_leader_count_query, (user_id,))
    if cur.fetchone()[0] > 0:  # user is leader of this clan
        return redirect(url_for('clans.clan_detail_method', clanid=clanid), code=302)

    user_secession_query = 'UPDATE service_user SET clan_id=NULL where service_user_id=%s'
    cur.execute(user_secession_query, (user_id,))
    conn.commit()

    # update session valuel; must using .update() method
    session_user = session.get('user')
    session_user['clanID'] = None
    session.update(user=session_user)

    return redirect(url_for('clans.clan_detail_method', clanid=clanid), code=302)
