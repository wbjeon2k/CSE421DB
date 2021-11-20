from flask import Flask, render_template
from flask import Blueprint, redirect, url_for

import psycopg2 as pg2
from models import TestModel, PartyModel
from app import connection
from jinja2 import Template
import json

bp = Blueprint('party', __name__, url_prefix='/party')

@bp.route('/')
def party_main():
    all_party_sql = """
        SELECT * FROM Party ORDER BY partyID
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    
    cur.execute(all_party_sql)
    all_party = cur.fetchall()
    all_party_list = PartyModel.serialize_party_list(all_party)
    #all_party_json_list = json.dumps(all_party_list)
    return render_template('party_list.html', party_list=all_party_list)

@bp.route('/detail/<int:partyId>')
def party_details(partyId):
    party_finder_sql_format = """
        SELECT * FROM Party WHERE partyID = %s    
    """
    conn = connection.get_connect()
    cur = conn.cursor()
    cur.execute(party_finder_sql_format, partyId)
    party = cur.fetchall()
    return party.serialize()