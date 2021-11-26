import json

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template

from database import Connection
from models import *

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('game', __name__, url_prefix='/game')

# /party 첫 페이지.
# 모든 파티들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def pgame_main():
    all_game_sql = """
        SELECT * FROM game
    """
    conn = Connection.get_connect()
    cur = conn.cursor()

    #cur.execute(all_game_sql)
    cur.execute("SELECT * FROM game;")
    all_game = cur.fetchall()
    
    all_game_list = []
    for games in all_game:
        all_game_list.append(GameModel(games[0], games[1]).serialize())
    #all_party_json_list = json.dumps(all_party_list)
    print(all_game_list)
    return render_template('game_list.html', game_list=all_game_list)

# game 에 달린 review 들 return.
# 현재는 serialize 된 json 그대로 return.
@bp.route('/game/detail/<int:gameId>')
def party_details(gameId):
    game_review_sql_format = """
        SELECT * FROM game WHERE partyID = %s
    """
    conn = Connection.get_connect()
    cur = conn.cursor()
    cur.execute(game_review_sql_format, (gameID,))
    #fetchall 은 list, fetchone 은 tuple 형태. 주의!
    tup = cur.fetchone()
    print(tup)
    g = GameModel(tup[0], tup[1]).serialize()
    # game 이외 parameter 들 추가 하여 컨텐츠 추가 가능.
    return render_template('game_detail.html', game = g)
