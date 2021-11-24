from flask import Flask, render_template
from flask import Blueprint, redirect, url_for

import psycopg2 as pg2
from models import TestModel, PartyModel
from app import connection
from jinja2 import Template
import json

# /party/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('games', __name__, url_prefix='/game')

# /party 첫 페이지.
# 모든 파티들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def party_main():
    all_game_sql = """
        SELECT * FROM Game
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    
    #cur.execute(all_game_sql)
    cur.execute("SELECT * FROM Game")
    all_game = cur.fetchall()
    all_game_list = PartyModel.serialize_party_list(all_game)
    #all_party_json_list = json.dumps(all_party_list)
    return render_template('party_list.html', party_list=all_game_list)

# game 에 달린 review 들 return.
# 현재는 serialize 된 json 그대로 return.
@bp.route('/game/detail/<int:gameId>')
def party_details(gameId):
    game_review_sql_format = """
        SELECT * FROM Party WHERE partyID = %s    
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    cur.execute(game_review_sql_format, gameId)
    party = cur.fetchall()
    return party.serialize()
