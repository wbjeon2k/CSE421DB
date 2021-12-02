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
bp = Blueprint('register', __name__, url_prefix='/register')

@bp.route('/', methods=['GET'])
def register_main_get():
    if 'user' in session:
        return redirect(url_for('/'))
    else:
        return render_template('register_template.html')
    
@bp.route('/', methods=['POST'])
def register_main_post():
    if 'user' in session:
        return redirect(url_for('/'))
    else:
        register_email = request.form.get('email')
        register_nickname = request.form.get('nickname')
        find_duplicate_sql = """
            SELECT COUNT(*) FROM SerivceUser
            WHERE email = %s OR nickname = %s;
        """
        conn = Connection.get_connect()
        cur = conn.cursor()
        cur.execute(find_duplicate_sql,(register_email,register_nickname))
        duplicate_cnt = cur.fetchone()[0]
        if(duplicate_cnt != 0):
            return render_template('register_template.html', error = "User with the email or the nickname exists")
        elif(duplicate_cnt == 0):
            raw_pw = request.form['rawPassword']
            hash_pw = hashlib.pbkdf2_hmac('sha256', raw_pw, b'saltkeywordrandom', 150000)
            enc_pw = hash_pw.hex()
            insert_user_sql = """
                INSERT INTO SerivceUser VALUES (%s,%s,%s,DEFAULT,NULL);
            """
            
            #TODO: session 과 연결을 해야하는가? 자동 로그인 하는걸로 
            try:
                cur.execute(insert_user_sql,(register_email, enc_pw, register_nickname))
                conn.commit()
            except Exception as e:
                return render_template('register_template.html', error = "User register failed. Try again.")
            #session 을 하면 main page로 redirect
            return redirect(url_for('/login'))
        else:
            return render_template('register_template.html', error = "Unknown register error. Try again.")