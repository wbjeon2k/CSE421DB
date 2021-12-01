import json

import psycopg2 as pg2
from psycopg2.sql import Identifier, SQL
from flask import Blueprint, Flask, redirect, render_template, url_for, request
from jinja2 import Template

from database import Connection
from models import *

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('games', __name__, url_prefix='/games')

#URI requirements
#https://superclass.notion.site/Service-URIs-6339514566164062998c57f690cbcc4c
#https://stackoverflow.com/questions/24892035/how-can-i-get-the-named-parameters-from-a-url-using-flask
#https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query

# /party 첫 페이지.
# 모든 파티들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def game_main():
    game_default_sql = """
        SELECT gameID, name, (SELECT COUNT(*) FROM Party WHERE Party.gameID = Game.gameID) as population FROM Game;
    """
    game_order_by_asc_sql = """
        SELECT gameID, name, (SELECT COUNT(*) FROM Party WHERE Party.gameID = Game.gameID) as population FROM Game
        ORDER BY %s ASC;
    """
    game_order_by_desc_sql = """
        SELECT gameID, name, (SELECT COUNT(*) FROM Party WHERE Party.gameID = Game.gameID) as population FROM Game
        ORDER BY %s DESC;
    """
    conn = Connection.get_connect()
    cur = conn.cursor()

    sort_key_name = request.args.get('sort')
    order_key = request.args.get('order')
    
    if(sort_key_name == NULL):
        cur.execute(game_default_sql)
    elif(order_key == 'asc' and sort_key_name != NULL):
        cur.execute(game_order_by_asc_sql, (sort_key_name,))
    elif(order_key == 'desc' and sort_key_name != NULL):
        cur.execute(game_order_by_desc_sql, (sort_key_name,))
    else:
        cur.execute(game_default_sql)
        
    all_game = cur.fetchall()
    
    all_game_list = []
    for games in all_game:
        all_game_list.append(GameModel(games[0], games[1], games[2]).serialize())
    #all_party_json_list = json.dumps(all_party_list)
    print(all_game_list)
    return render_template('game_list.html', game_list=all_game_list)

# game 에 속한 party 들 return.
@bp.route('/game/detail/<int:gameid>')
def party_details(gameid):
    game_review_sql_format = """
        SELECT * FROM Party WHERE gameID = %s
    """
    conn = Connection.get_connect()
    cur = conn.cursor()
    cur.execute(game_review_sql_format, (gameid,))
    #fetchall 은 list, fetchone 은 tuple 형태. 주의!
    tup = cur.fetchall()
    print(tup)
    g = PartyModel(tup[0], tup[1]).serialize()
    # game 이외 parameter 들 추가 하여 컨텐츠 추가 가능.
    return render_template('game_detail.html', game = g)
