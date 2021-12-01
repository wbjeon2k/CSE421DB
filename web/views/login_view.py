import json

import psycopg2 as pg2
from flask import Blueprint, Flask, redirect, render_template, url_for
from jinja2 import Template
from flask import session, request
from psycopg2 import sql
from psycopg2.sql import SQL
from database import Connection
from models import *
from datetime import datetime, timezone
from database import Connection
from models import *
import hashlib

# /game/... url 들을 포워딩 해주는 blueprint
bp = Blueprint('login', __name__, url_prefix='/login')

@bp.route('/', methods=['GET'])
def register_main_get():
    if 'user' in session:
        return redirect(url_for('/'))
    else:
        return render_template('login_template.html')
    
    
@bp.route('/', methods=['POST'])
def register_main_get():
    if 'user' in session:
        return redirect(url_for('/'))
    else:
        find_user_sql = """
            SELECT COUNT(*) FROM SerivceUser WHERE email = %s;
        """
        conn = Connection.get_connect()
        cur = conn.cursor()
        login_email = request.form.get('email')
        cur.execute(find_user_sql, (login_email,))
        user_count = cur.fetchone()[0]
        if(user_count != 0):
            request_pw = request.form.get('rawPassword')
            hashed_pw = hashlib.pbkdf2_hmac('sha256', request_pw, b'saltkeywordrandom', 150000)
            fetch_user_pw_sql = """
                SELECT encryptedPassword FROM SerivceUser WHERE email = %s;
            """
            cur.execute(fetch_user_pw_sql,(login_email,))
            fetched_hash_pw = cur.fetchone()[0]
            if(fetched_hash_pw == hashed_pw):
                #https://pythonise.com/series/learning-flask/flask-session-object
                user_dict = 
                session['user']=user_dict
        elif(user_count == 0):
            return render_template('login_template.html', error='Wrong email or password')
        else:
            return render_template('login_template.html', error='Wrong email or password')