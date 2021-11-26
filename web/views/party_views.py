from flask import Flask, render_template
from flask import Blueprint, redirect, url_for

import psycopg2 as pg2
from models import TestModel, PartyModel
from app import connection
from jinja2 import Template
import json

# /party/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('party', __name__, url_prefix='/party')

# /party 첫 페이지.
# 모든 파티들을 1번 부터 n 번 순서대로 표시.
@bp.route('/')
def party_main():
    all_party_sql = """
        SELECT * FROM party ORDER BY partyID
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    
    cur.execute(all_party_sql)
    all_party = cur.fetchall()
    all_party_list = PartyModel.serialize_party_list(all_party)
    #all_party_json_list = json.dumps(all_party_list)
    return render_template('party_list.html', party_list=all_party_list)

# /party 에 표시되는 링크를 누르면 생기는 페이지.
# 현재는 serialize 된 json 그대로 return.
@bp.route('/party/detail/<int:partyId>/')
def party_details(partyId):
    party_finder_sql_format = """
        SELECT * FROM party WHERE partyID = %s    
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    cur.execute(party_finder_sql_format, partyId)
    p = cur.fetchone()
    party = PartyModel(p[0], p[1], p[2], p[3], p[4], p[5]).serialize()
    
    return render_template('party_detail.html', party = party)
