import json

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template

from app import connection
from models import PartyModel, TestModel

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
@bp.route('/party/detail/<int:partyId>')
def party_details(partyId):
    party_finder_sql_format = """
        SELECT * FROM party WHERE partyID = %s
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    cur.execute(party_finder_sql_format, partyId)
    party = cur.fetchall()
    return party.serialize()
