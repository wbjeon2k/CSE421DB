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

# /games 첫 페이지.
@bp.route('/')
def game_main():
    # 처음 /games 에 들어가면 보이는 table.
    game_default_sql = """
        SELECT gameID, name, (SELECT COUNT(*) FROM Party WHERE Party.gameID = Game.gameID) as population FROM Game;
    """
    # sort key 로 name/popular 들어왔을때 ASC order sort.
    game_order_by_asc_sql = """
        SELECT gameID, name, (SELECT COUNT(*) FROM Party WHERE Party.gameID = Game.gameID) as population FROM Game
        ORDER BY %s ASC;
    """
    # sort key 로 name/popular 들어왔을때 DESC order sort.
    game_order_by_desc_sql = """
        SELECT gameID, name, (SELECT COUNT(*) FROM Party WHERE Party.gameID = Game.gameID) as population FROM Game
        ORDER BY %s DESC;
    """
    conn = Connection.get_connect()
    cur = conn.cursor()

    sort_key_name = request.args.get('sort')
    order_key = request.args.get('order')
    
    if(sort_key_name == NULL):
        # ?sort 가 없는 상황.
        cur.execute(game_default_sql)
    elif(order_key == 'asc' and sort_key_name != NULL):
        cur.execute(game_order_by_asc_sql, (sort_key_name,))
    elif(order_key == 'desc' and sort_key_name != NULL):
        cur.execute(game_order_by_desc_sql, (sort_key_name,))
    else:
        # exception 을 던지지 않기 위한 예외처리.
        cur.execute(game_default_sql)
        
    all_game = cur.fetchall()
    
    #game table JSON serialize
    all_game_list = []
    for games in all_game:
        all_game_list.append(GameModel(games[0], games[1], games[2]).serialize())
    
    #TODO: template html 파일 이름, parameter 확인
    return render_template('game_list.html', game_list=all_game_list)

# TODO: game 에서 표시 할 컨텐츠 정하기
# 아래는 임시. 작동하는 코드 아님.
# game 순위, game 파티, game review, game tag
@bp.route('/game/detail/<int:gameid>/')
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
